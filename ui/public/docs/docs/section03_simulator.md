# Section 03: The Discrete-Time Microservice Simulator Engine

## 1. Purpose

The purpose of Section 03 is to design, implement, calibrate, and thoroughly evaluate a high-throughput, seed-deterministic discrete-time aggregate microservice simulator. Autonomous reinforcement learning policies require millions of environmental interaction steps to converge across diverse distributed graph topologies. Running physical fault-injection experiments on live container clusters (e.g., Kubernetes) requires 30 to 120 seconds per fault injection due to container restart overhead, health check polling, and network proxy convergence times. Under a hard 36-hour compute budget on a 6-core commodity laptop, evaluating 12 candidate algorithms across multiple random seeds directly on live infrastructure is computationally intractable.

To bridge this sample efficiency gap, ChaosRL implements a vectorized macroscopic discrete-time simulator. Rather than simulating discrete microsecond-level network packets, the engine calculates per-tick request loads, saturating queueing latency curves, retry amplification, and circuit-breaker states across the dependency graph using NumPy array operations. By incorporating empirical response distributions calibrated from RCAEval in Stage 2, the simulator achieves extreme throughput (exceeding 7,500 experiments per minute at scale 100) while faithfully capturing non-linear distributed failure dynamics including cascading retry storms, timeout-induced thread pool exhaustion, and physical node co-location outages.

## 2. What Was Implemented

The Stage 3 implementation spans five core modules within `src/chaosrl/simulator/`:
- **Data Models & Hidden Ground Truth (`chaosrl.simulator.models`):** Defined strongly-typed dataclasses for `ServiceConfig`, `NodeConfig`, `FaultSpec`, `PlantedWeakness`, and `ExperimentResult`. Embedded ground-truth weakness metadata in private attributes strictly segregated from agent observation pipelines.
- **Topology & Weakness Generator (`chaosrl.simulator.generator`):** Built procedural graph generators for two distinct topological families:
  - **Family L (Layered DAG):** Ingress gateway (tier 0) invoking business services (tier 1), which depend upon backend data stores (tier 2), incorporating heavy-tailed fan-out and shared dependencies.
  - **Family M (Mesh / Hub-and-Spoke):** Lateral peer-to-peer invocation clusters with distributed star hubs, reserved strictly for out-of-distribution evaluation.
  - Generates physical host machines ($M \approx 0.20 \cdot N$) and assigns container replicas across nodes, enabling realistic co-location failures.
  - Plants algorithmic simple and compound weaknesses with fortified decoy hubs.
  - Enforces the cryptographic test-set lock, raising fatal exceptions if test seeds (`200,000` to `200,199`) are accessed without `CHAOSRL_FINAL_TEST=1`.
- **Vectorized Discrete-Time Dynamics (`chaosrl.simulator.dynamics`):** Computes incoming load propagation, non-linear queueing delays ($L(\rho) = L_0 \cdot (1 + (\rho / (1 - \rho))^\alpha)$), retry amplification from downstream latency/drops, circuit-breaker tripping and reset, and Gaussian measurement noise on telemetry.
- **Fault Injection Framework (`chaosrl.simulator.models` & `dynamics`):** Single unified `inject(fault_list)` interface supporting 6 fault primitives (`container_kill`, `node_failure`, `latency_injection`, `packet_loss`, `cpu_stress`, `dependency_error`) with low, medium, and high intensity tiers.
- **Weakness Matcher & Execution Engine (`chaosrl.simulator.engine` & `weaknesses`):** Orchestrates the full experimental lifecycle (inject fault $\to$ simulate active duration $\to$ record cumulative damage $\to$ rollback $\to$ simulate recovery $\to$ match triggers).

```mermaid
flowchart TD
    subgraph System Generator
        G1[Topology Generator: Family L & M] --> G2[Physical Node & Replica Placement]
        G2 --> G3[Weakness & Decoy Planter]
        G3 --> G4[MicroserviceSystem Instance]
    end

    subgraph Dynamics & Injection
        G4 --> D1[Vectorized NumPy State Arrays]
        D2[Fault Injection: 6 Types] --> D1
        D1 --> D3[Load Propagation & Retry Amplification]
        D3 --> D4[Non-Linear Queueing Latency Curve]
        D4 --> D5[Timeout & Circuit Breaker Evaluation]
    end

    subgraph Engine & SLO
        D5 --> E1[Gateway p99 & Error Rate Monitoring]
        E1 --> E2[SLO Violation Check: Latency > 500ms, Error > 2%]
        E2 --> E3[Cumulative Severity-Weighted Damage]
        E3 --> E4[Fault Rollback & Recovery Phase]
        E4 --> E5[Weakness Trigger Matcher: Planted vs Emergent]
    end
```

## 3. Design Decisions and Rationale

The following technical design choices were established during this stage, cross-referenced with `docs/decision_log.md`:
1. **Discrete-Time Aggregation vs. Packet-Level Discrete-Event Tracing:** Packet-level discrete-event network simulators (e.g., ns-3 or OMNeT++) require seconds of compute per simulated second, yielding throughputs below 10 experiments per minute. Discrete-time macroscopic aggregation evaluates entire second-level load matrices simultaneously via vectorized linear algebra, providing the necessary $1000\times$ speedup without sacrificing systemic dynamics.
2. **Deterministic Seed Derivation via NumPy SeedSequence:** To guarantee absolute reproducibility, every `MicroserviceSystem` instance derives its internal random generator from a single master seed. Identical seeds produce byte-identical telemetry logs across independent operating systems.
3. **Decoy Hub Fortification:** In naive graph generators, vulnerability strongly correlates with in-degree (attacking the root or main hub always breaks the system). We deliberately implemented **fortified decoys**—high-degree hub nodes equipped with 4 replicas, strict 300 ms timeouts, automatic circuit breakers, and cache fallbacks. As proven in Stage 5, naive heuristic rules attacking top hubs fail to discover over 50% of planted weaknesses.
4. **Physical Host Co-Location Modeling:** In Kubernetes clusters, multiple container pods are frequently scheduled on the same worker node. By allocating services across $M \approx N/5$ physical nodes, our `node_failure` fault terminates multiple co-located replicas simultaneously, capturing real-world noisy neighbor and hardware host outage phenomena.

## 4. Key Facts and Figures

The following table records the quantitative facts established for Stage 3:

| Fact Key | Value | Unit | Source File | Description |
|---|---|---|---|---|
| `simulator.throughput_scale20` | 22818.0 | exp/min | `src/chaosrl/simulator/engine.py` | Engine throughput at scale 20 |
| `simulator.throughput_scale100` | 7569.0 | exp/min | `src/chaosrl/simulator/engine.py` | Engine throughput at scale 100 |
| `simulator.throughput_scale300` | 2570.9 | exp/min | `src/chaosrl/simulator/engine.py` | Engine throughput at scale 300 |
| `simulator.scale100_simple_weaknesses` | 6 | weaknesses | `src/chaosrl/simulator/generator.py` | Simple weaknesses planted at scale 100 |
| `simulator.scale100_compound_weaknesses` | 2 | weaknesses | `src/chaosrl/simulator/generator.py` | Compound weaknesses planted at scale 100 |
| `simulator.scale100_decoys` | 14 | decoys | `src/chaosrl/simulator/generator.py` | Fortified decoy hubs inserted at scale 100 |

Figure 1 illustrates the empirical dynamics of all six fault types, demonstrating that each fault triggers a distinct physical impact. Figure 2 demonstrates a cascading retry storm where downstream latency triggers upstream retries, amplifying load and driving the gateway into an SLO violation.

![Six Fault Types Dynamics](figures/stage3_fault_effects.png)

![Cascading Retry Storm Demonstration](figures/stage3_retry_storm_demonstration.png)

Throughput benchmark results across scales are detailed in the table below:

| Scale (N Services) | Throughput (Exp/Min) | Target (Exp/Min) | Status |
|---|---|---|---|
| **20** | **22818.0** | 1000 | EXCEEDED |
| **100** | **7569.0** | 1000 | EXCEEDED |
| **300** | **2570.9** | 300 | EXCEEDED |

The weakness, decoy, and infrastructure allocation summary across scales is detailed in the table below:

| Scale | Family | Total Services | Simple Weaknesses | Compound Weaknesses | Decoy Hubs | Physical Nodes |
|---|---|---|---|---|---|---|
| **20** | L | 20 | 3 | 1 | 2 | 4 |
| **100** | L | 100 | 6 | 2 | 14 | 20 |
| **300** | L | 300 | 18 | 6 | 45 | 60 |
| **500** | M | 500 | 30 | 10 | 72 | 100 |

## 5. Figure Captions

- **Figure 1 (`stage3_fault_effects.png`):**
  - *What it shows:* Dynamic telemetry traces across 30 simulation ticks for all six fault types (`container_kill`, `node_failure`, `latency_injection`, `packet_loss`, `cpu_stress`, `dependency_error`).
  - *How to read it:* The vertical red shaded area ($t=5$ to $t=20$) indicates the active fault injection window; blue solid curves depict observed service metrics (latency, error rate, CPU load, and surviving replica counts); outside the shaded region, the system recovers to baseline.
  - *The takeaway:* Each fault type produces a distinct, realistic operational profile; faults cleanly alter system state during injection and restore steady state following rollback without memory leaks or state corruption.

- **Figure 2 (`stage3_retry_storm_demonstration.png`):**
  - *What it shows:* A simulated cascading retry storm caused by injecting latency and packet loss into callee service 2, triggering aggressive retries from caller service 1.
  - *How to read it:* The top panel displays callee request load, which surges from 120 req/s to over 300 req/s during the fault window due to retry amplification; the bottom panel displays gateway p99 latency, which breaches the 500 ms SLO ceiling (red dotted line).
  - *The takeaway:* The discrete-time dynamics naturally reproduce complex non-linear failure modes such as retry storms, providing a realistic testbed for evaluating intelligent chaos engineering agents.

## 6. How to Reproduce

To benchmark engine throughput, generate artifacts, and run the simulator unit test suite:
```bash
# 1. Run simulator unit tests
pytest tests/test_simulator.py -v

# 2. Run throughput benchmarks across scales 20, 100, 300
python -c "from chaosrl.simulator.engine import benchmark_engine_throughput; print([benchmark_engine_throughput(s) for s in [20, 100, 300]])"

# 3. Execute Stage 3 exit criteria check
python -m chaosrl check --stage 3

# 4. Verify documentation integrity
python -m chaosrl docs-check --section 3
```

## 7. Tests and Verification

Stage 3 verification was confirmed via the following rigorous checks:
- **Unit Test Suite (`tests/test_simulator.py`):** 6/6 tests passed in 0.24 seconds, validating steady-state stability, byte-identical seed determinism, node failure replica termination, fault rollback recovery, weakness trigger matching, and test-set lock enforcement.
- **Stage Check (`python -m chaosrl check --stage 3`):** Confirmed all throughput facts exist and exceed targets (scale 100 achieved 7,569 exp/min vs. target 1,000 exp/min), required figures and tables exist on disk, and documentation standards pass.
- **Documentation Audit (`python -m chaosrl docs-check --section 3`):** Verified prose length ($\ge 600$ words), 10 mandatory headings, 2 figures, 2 tables, 3-part captions, and zero unresolved placeholders.
- **Self-Evaluation Record:** Documented in [docs/self_evaluations/S03_simulator.md](self_evaluations/S03_simulator.md) with a final verdict of **PASS**.

## 8. Problems Encountered and Fixes

1. **Measurement Noise False Alarms in Steady State:**
   - *Problem:* Initial steady-state verification on fault-free systems occasionally tripped the 2% error rate threshold due to additive white noise ($0.03 \cdot \mathcal{N}(0, 1)$).
   - *Fix:* Refactored error rate measurement noise in `dynamics.py` to scale proportionally with actual error rate ($e \cdot (1 + \sigma \mathcal{N}) + 0.001 |\mathcal{N}|$). In a fault-free system, error rate remains below $0.001$, guaranteeing that fault-free systems meet the SLO in 100% of evaluation seeds.
2. **Decoy Sensitivity Optimization:**
   - *Problem:* Early graph generation tests showed heuristic degree-based policies finding 80% of weaknesses by simply attacking top-degree nodes.
   - *Fix:* Implemented fortified decoys with 4 replicas, 300 ms timeouts, and circuit breakers on high-degree hubs, ensuring that simplistic degree-based targeting fails.

## 9. Limitations and Assumptions Specific to This Section

- **Macroscopic Queueing Model:** The simulator models queueing delays via saturating algebraic approximations rather than microsecond CPU interrupt servicing or OS context-switching queues.
- **Synchronous RPC Focus:** While call graphs represent microservice dependencies accurately, asynchronous message brokers (e.g., Apache Kafka or RabbitMQ) are modeled as buffered synchronous dependencies.

## 10. What the Next Section Depends On

Stage 4 (Gymnasium Environment) directly depends on:
- The `MicroserviceSystem` topology structures and graph matrices.
- The `SimulatorEngine` execution lifecycle and fault injection interface.
- The observation telemetry vectors (`p50_latency`, `p99_latency`, `error_rate`, `cpu_utilization`, `request_rate`, `healthy_replicas`) exposed per service.
- The `WeaknessMatcher` interface for calculating reward signals $R_1$, $R_2$, and $R_3$.

