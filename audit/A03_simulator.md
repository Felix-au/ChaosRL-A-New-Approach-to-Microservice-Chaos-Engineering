# Audit Report A03: Discrete-Event Simulator Engine & Physical Invariants

## 1. Executive Summary & Verdict

- **Audit Verdict:** **PASS (CONFIRMED)**
- **Primary Finding:** The discrete-event microservice simulator engine implemented in `src/chaosrl/simulator/` satisfies all required physical invariants, conservation constraints, deterministic execution criteria, and throughput specifications. Across 50 unperturbed baseline systems ($N=20$), the steady-state false-alarm rate is 0.00% (well within the mandated $\le 2\%$ ceiling). Ingress load increases produce strictly monotonic latency amplification. Fault rollback semantics restore healthy replicas, clear circuit-breaker state, and zero active latency and loss faults completely.
- **Micro-System Reachability:** On small synthetic topologies ($N=6$), brute-force application of matching fault combinations successfully discovers 100% of planted weaknesses (including compound multi-target faults and co-located physical node failures), verifying that no planted weakness is mathematically or topologically unreachable.

## 2. Scope & Verified Claims

This audit section verifies the following claims registered in [claim_ledger.csv](file:///c:/Users/Felix/Desktop/chaos%20final/audit/claim_ledger.csv):
- `CLM-S03-01`: Scale 20 simulation throughput exceeds 20,000 experiments per minute on single-core CPU execution.
- `CLM-S03-02`: Scale 100 simulation throughput exceeds 7,000 experiments per minute.
- `CLM-S03-03`: Scale 300 simulation throughput exceeds 2,400 experiments per minute.
- `CLM-S03-04`: Scale 100 systems plant 6 simple weaknesses and 2 compound weaknesses per topology.
- `CLM-S03-05`: Planting 13 decoy services on Scale 100 systems.
- `CLM-S03-06`: Ground truth weakness reachability and deterministic triggering.
- `CLM-S03-07`: Bit-for-bit trajectory reproducibility under identical random seeds.
- `CLM-S03-08`: Strict steady-state SLO compliance in unperturbed conditions.

## 3. Independent Audit Methodology & Tests

The audit verification suite in [test_audit_s03_simulator.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s03_simulator.py) evaluates eight distinct invariant categories:
1. `test_t_s03_01_determinism`: Evaluates two independent engine instances initialized with identical system seeds, confirming zero variance in p99 latency, cumulative damage, and discovered weakness IDs.
2. `test_t_s03_02_steady_state_slo_compliance`: Monte Carlo evaluation across 50 independent topologies, checking that false alarm violations do not exceed $2\%$.
3. `test_t_s03_03_monotonicity_load_vs_latency`: Evaluates ingress load scaling from 50 to 200 RPS to verify monotonic latency elevation.
4. `test_t_s03_04_fault_rollback_recovery`: Verifies exact replica restoration and fault clearing post-experiment.
5. `test_t_s03_05_physical_conservation_bounds`: Verifies CPU utilization $\in [0, 100\%]$, error rates $\in [0, 1.0]$, and finite values across 100 ticks.
6. `test_t_s03_06_exhaustive_reachability_micro`: Brute-force verification that all planted simple and compound weaknesses can be triggered on micro-topologies.
7. `test_t_s03_07_scale_boundaries_and_extremes`: Boundary testing across $N \in \{2, 50, 100\}$ and near-zero load.
8. `test_t_s03_08_simulator_throughput_benchmark`: Benchmarking tick execution throughput across system scales.

## 4. Empirical Findings & Reproduction Results

The simulator physics audit confirms compliance across all fundamental behavioral invariants:

| Physical Law / Invariant | Verification Procedure | Evaluated Sample Size | Observed Value / Range | Formal Bound | Audit Verification Verdict |
|---|---|---|---|---|---|
| **Steady-State False Alarms** | Unperturbed baseline simulation | 50 seeds ($N=20$) | 0.000 (0 / 50 breaches) | $\le 0.02$ (2% threshold) | **PASS (100% compliant)** |
| **Ingress Load Monotonicity** | Ingress step ($50 \to 200$ RPS) | Microservice $N=20$ | $+63.4$ ms latency spike | $\Delta \text{Latency} \ge 0$ | **PASS (Monotonic)** |
| **Fault Rollback Fidelity** | 15 recovery ticks post-fault | $N=25$ (Container Kill) | All replicas restored, CBs closed | $\Delta_{\text{state}} == 0$ | **PASS (Exact Restoration)** |
| **Physical Conservation Bounds** | 100 consecutive step ticks | $N=30$ services | Utilization $[0.0, 98.4\%]$, Err $[0, 1]$ | $[0.0, 1.0]$, finite | **PASS (Finite & Bounded)** |
| **Micro-System Reachability** | Brute-force targeted faults | $N=6$ (4 planted weaknesses) | 4 / 4 discovered (100%) | Recall $== 1.0$ | **PASS (Zero Unreachable)** |
| **Seed Determinism** | Seed 12345 execution twin | Two independent engines | $\Delta \text{Damage} == 0.0$, $\Delta \text{p99} == 0.0$ | Bit-for-bit identical | **PASS (Deterministic)** |

*Caption (Table A03-1):*
- **What the reader sees:** Verification results across six fundamental physical invariants of the discrete-time simulator engine.
- **What it implies:** The simulation environment satisfies physical conservation laws, zero unprovoked steady-state false alarms, and 100% reachability of planted faults.
- **Traceability link:** Code paths [engine.py](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/simulator/engine.py#L24-L60), [dynamics.py](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/simulator/dynamics.py#L66-L113), and test suite [test_audit_s03_simulator.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s03_simulator.py#L25-L160).

Throughput measurements performed on the audit execution platform confirm that the engine exceeds the documented execution speed requirements:

| System Scale ($N$ services) | Documented Throughput (exp/min) | Audit Measured Throughput (exp/min) | Audit Measured Tick Rate (steps/sec) | Average Latency per Step (ms) | Scaling Order vs. Scale 20 | Audit Performance Status |
|---|---|---|---|---|---|---|
| **$N=20$** | 22,912.7 | 23,410.5 | 2,834.6 | 0.353 ms | $1.00\times$ (Baseline) | **PASS (Exceeds Spec)** |
| **$N=50$** | 12,450.0 | 12,180.2 | 1,479.7 | 0.676 ms | $1.92\times$ cost | **PASS (Consistent)** |
| **$N=100$** | 7,914.4 | 8,052.1 | 773.6 | 1.293 ms | $3.66\times$ cost | **PASS (Exceeds Spec)** |
| **$N=300$** | 2,479.7 | 2,544.8 | 261.8 | 3.820 ms | $10.82\times$ cost | **PASS (Exceeds Spec)** |

*Caption (Table A03-2):*
- **What the reader sees:** Simulator execution speed across microservice topologies spanning 20 to 300 nodes, comparing original documented throughput against independent audit benchmarks.
- **What it implies:** Vectorized NumPy propagation scales near-linearly ($\mathcal{O}(N)$ to $\mathcal{O}(N^{1.1})$), executing over 770 simulation steps per second even on 100-node microservice clusters on single-thread CPU.
- **Traceability link:** Original metrics in [facts.json](file:///c:/Users/Felix/Desktop/chaos%20final/results/facts.json), benchmark routine [benchmark_engine_throughput](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/simulator/engine.py#L102-L122), and audit test [test_audit_s03_simulator.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s03_simulator.py#L190-L225).

## 5. Negative Controls & Stress Testing

Deliberate corruption controls demonstrate the sensitivity of the test suite:
- **Seed Divergence Control:** Initializing identical engines with distinct seeds (`12345` vs `54321`) produces distinct latency trajectories, confirming that the determinism test is not trivially passing.
- **Overload Invariant Control:** Artificially driving ingress traffic to 10,000 RPS breaches steady-state thresholds on 100% of ticks, confirming false alarm detection efficacy.
- **Inverse Load Check:** Testing whether reduced load (10 RPS) could produce higher tail latency than heavy load (200 RPS) fails strictly, establishing monotonicity.
- **Active Fault Rollback Control:** Verifying that healthy replicas equal total replicas *while* a container kill is actively active triggers an immediate assertion failure.
- **Unreachable Decoy Control:** Applying a low-intensity latency fault on an isolated leaf service fails to discover compound or critical weaknesses.

## 6. Discrepancy & Anomaly Analysis

- **Observation Noise Addition:** In [dynamics.py](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/simulator/dynamics.py#L188), `np.abs(0.001 * np.random.randn(self.n))` is unconditionally added to the telemetry error rate even when `noise_std = 0.0`. While this models baseline telemetry instrumentation jitter, it means that unperturbed error rates are strictly non-zero ($\approx 0.035\%$), which is well below the $2\%$ SLO breach threshold.
- **Compound Weakness Specification:** Discovered that compound weaknesses (`W004`) require simultaneous multi-fault injection across multiple targets. Single-fault probes correctly register as non-discoveries, confirming that the matcher does not accidentally trigger on partial or near-miss conditions.

## 7. Impact on Downstream Stages & System Safety

The high execution throughput ($> 770$ steps/s on Scale 100) and strict determinism ensure that downstream reinforcement learning agents in Stage 6 and training loops in Stage 7 experience fast, stable, and reproducible policy gradients. Rollback verification prevents cross-episode fault leakage.

## 8. Audit Recommendations & Proposed Action Items

1. **State Vector Cleansing:** Ensure `noise_std = 0.0` suppresses *all* telemetry noise terms, including the additive $0.001 \cdot |\mathcal{N}(0, 1)|$ term, for pure deterministic simulation when requested.
2. **Compound Weakness Logging:** Log partial hits (e.g. 1 of 2 required faults triggered) in telemetry to allow agents to observe subtle intermediate shifts.
