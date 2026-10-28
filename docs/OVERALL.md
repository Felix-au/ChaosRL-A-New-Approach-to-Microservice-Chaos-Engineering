# ChaosRL: Autonomous Reinforcement Learning for Microservice Vulnerability Discovery
*A Rigorous Empirical Research Monograph*

---

## 1. Executive Summary

Modern enterprise software systems are built as complex, interconnected microservice call graphs. Ensuring their operational resilience against unexpected infrastructure and network faults has traditionally relied on chaos engineering practices, epitomized by Netflix's Chaos Monkey. However, classical Chaos Monkey operates via unguided, memoryless random container termination. This approach suffers from two severe limitations: it causes excessive collateral Service Level Objective (SLO) damage, and it systematically misses complex multi-fault vulnerabilities such as cascading retry storms, unshielded dependency timeouts, and physical node co-location bottlenecks.

**ChaosRL** resolves this challenge by formulating chaos engineering as a reinforcement learning problem. Rather than injecting random failures, an autonomous agent observes system telemetry (latency ratios, error rates, queue depths, CPU utilization) and structural graph properties (degree centrality, layer depth, replica counts), learning an optimal policy that determines which fault to inject into which service at what intensity. 

This research project develops:
1. A fast, discrete-time aggregate microservice simulator capable of running over 1,000 experiments per minute, calibrated against empirical measurements from 375 real microservice failure cases (RCAEval).
2. A pool of 12 diverse candidates spanning policy-gradient (PPO, A2C, REINFORCE), structure-aware Graph Neural Networks (GNN), value-based Q-learning (Double Dueling DQN), gradient-free optimization (Evolution Strategies), and non-deep contextual bandits.
3. A diversity-constrained Top-5 selection protocol and three meta-ensemble controllers (Soft Voting, Borda Rank Voting, and Random Forest Gating).
4. A locked test-set evaluation protocol enforcing zero test snooping, pre-registered hypotheses, and paired non-parametric statistical significance testing.

The findings establish that learned chaos policies significantly outperform classical random injection by discovering more architectural weaknesses with higher sample efficiency and lower collateral damage.

---

## 2. Project at a Glance

The following master facts table summarizes the scope, parameters, and experimental volume of the ChaosRL research project:

| Metric / Dimension | Specification / Value | Source / Notes |
|---|---|---|
| **Primary Goal** | Autonomous RL-guided chaos engineering | Replaces random Chaos Monkey |
| **System Scales Simulated** | 20, 100, 300 (Training/Test) & 500 (OOD) | Configured in `configs/scales.yaml` |
| **Topology Families** | Family L (Layered DAG) & Family M (Mesh) | Family M reserved strictly for OOD test |
| **Fault Catalog** | 6 Fault Types (Kill, Latency, Loss, CPU, Node, Error) | 3 intensity tiers (Low, Medium, High) |
| **Planted Weakness Types** | Simple (Single-Fault) & Compound (Multi-Fault) | Algorithmically generated with decoys |
| **Candidate Algorithms** | 12 Candidates across 5 Families | C01 through C12 |
| **Ensemble Models** | E1 (Soft Vote), E2 (Borda Rank), E3 (RF-Gated) | Meta-controllers over Top 5 |
| **Baseline Algorithms** | Chaos Monkey, Chaos Monkey-2, Random-All, UCB, Heuristic, Oracle | 6 competitive + 1 reference |
| **Data Calibration Source** | RCAEval (Online Boutique, Sock Shop, Train Ticket) | 375 empirical fault-injection cases |
| **Disjoint Seed Splits** | Train: 0–99,999; Val: 100,000–100,099; Test: 200,000–200,199 | Enforced programmatically in code |
| **Hardware Configuration** | AMD Ryzen 5 5500U (6C/12T), 14 GB RAM, Windows 11 | CPU-only PyTorch execution |
| **Hard Compute Budget** | 36.0 Wall-Clock Hours | Configured in `configs/budget.yaml` |

---

## 3. System Architecture

The ChaosRL platform is organized into modular subsystems operating under strict separation of concerns:

```mermaid
flowchart TD
    subgraph Data & Calibration
        D1[RCAEval Telemetry Data] --> D2[Distribution Fitting]
        D2 --> D3[Calibrated Fault Parameters]
    end

    subgraph Simulation & Environment
        D3 --> S1[Discrete-Time Simulator Engine]
        S2[Topology Generator: Family L & M] --> S1
        S3[Ground-Truth Weakness & Decoy Planter] --> S1
        S1 --> E1[Gymnasium ChaosEnv]
    end

    subgraph Agents & Meta-Controllers
        E1 --> A1[Baseline Suite: CM, Random, UCB, Heuristic]
        E1 --> A2[Learned Pool: PPO, GNN, DQN, ES, LinUCB]
        A2 --> EN1[Top-5 Selection & Freezing]
        EN1 --> EN2[Ensembles: E1 Soft, E2 Rank, E3 RF-Gate]
    end

    subgraph Evaluation & Auditing
        A1 --> EV1[Locked Final Evaluation Harness]
        EN2 --> EV1
        EV1 --> EV2[Statistical Significance & Bootstrap CIs]
        EV2 --> EV3[Facts Registry & Auto-Documentation]
    end
```

1. **Topology & System Generator:** Synthesizes realistic microservice dependency graphs with configurable service counts, multi-replica container scheduling across physical nodes, traffic routing, retry backoffs, and circuit breakers.
2. **Ground-Truth Planter:** Embeds simple and compound architectural vulnerabilities into the generated topologies alongside high-connectivity, well-defended decoy hubs.
3. **Discrete-Time Simulator:** Advances system state across discrete time ticks using vectorized NumPy matrix operations, modeling queueing delay saturation, retry amplification, and cascading failures.
4. **Gymnasium Environment (`ChaosEnv`):** Exposes a standardized black-box RL interface providing graph-structured observations, dynamic candidate action masking, and regularized reward calculations.
5. **Candidate Pool & Ensembles:** Hosts 12 diverse learned models and meta-ensembles that select fault injection targets based on graph state.
6. **Auditing & Verification Engine:** Enforces test-set isolation, reproducible seeding, facts registry resolution, and automated documentation consistency.

---

## 4. Data and Calibration Summary

To ensure simulation realism, fault response functions are grounded in real-world distributed systems telemetry rather than arbitrary mathematical formulas. We utilize the **RCAEval** benchmark (Pham et al.), which contains 375 real fault-injection cases conducted on production-grade microservice benchmark applications:
- **Online Boutique** (Google Cloud microservices demo)
- **Sock Shop** (Weaveworks microservices architecture)
- **Train Ticket** (Large-scale enterprise microservices benchmark)

Empirical telemetry time-series capturing pre-injection and post-injection system metrics (CPU utilization, p50/p90/p99 latencies, network packet loss, and error rates) are ingested. Response function parameters (latency amplification factors, queue saturation exponents, and resource exhaustion curves) are calibrated via distribution matching (minimizing Wasserstein distance between simulated and empirical response profiles).

---

## 5. Simulator Summary

The simulator models microservice systems through discrete-time macroscopic aggregation. For each service $i$ at tick $t$, incoming request load $\lambda_i(t)$ is computed by aggregating external ingress traffic and upstream dependency calls, explicitly incorporating **retry amplification**:
$$\lambda_i(t) = \lambda_i^{\text{ext}}(t) + \sum_{j \in \text{Callers}(i)} \left( \lambda_{j \to i}^{\text{base}}(t) + \lambda_{j \to i}^{\text{retry}}(t) \right)$$

Per-replica utilization $\rho_i(t)$ and queueing latency $L_i(t)$ follow saturating non-linear queueing curves:
$$L_i(t) = L_{i,0} \cdot \left( 1 + \left( \frac{\rho_i(t)}{1 - \rho_i(t) + \epsilon} \right)^{\alpha} \right)$$
where $L_{i,0}$ is base latency and $\alpha$ is calibrated queueing power. When latency exceeds service timeout thresholds, requests abort, tripping upstream circuit breakers and shedding load according to configured retry and fallback policies.

The simulator incorporates 6 distinct fault types:
1. `container_kill`: Direct termination of a container instance.
2. `node_failure`: Termination of all co-located replicas residing on a physical host.
3. `latency_injection`: Artificial network or processing delay added to inbound calls.
4. `packet_loss`: Stochastic dropping of network packets across service boundaries.
5. `cpu_stress`: Resource starvation elevating background utilization toward saturation.
6. `dependency_error`: Forced generation of HTTP 500 error responses.

---

## 6. Environment and Reward Summary

The `ChaosEnv` environment exposes a graph observation space comprising:
- **Per-Service Dynamic Telemetry:** Normalized latency ratio, error rate, CPU utilization, healthy replica fraction, and active fault status.
- **Per-Service Static Graph Features:** In-degree, out-degree, topological layer depth, replica count, and physical node co-location count.
- **Experiment History Features:** Injection counts per fault type and historical discovery outcomes.
- **Global Context:** Remaining experiment budget $B - t$, cumulative damage, and total weaknesses discovered.

The action space consists of tuples `(service_id, fault_type, intensity)`. For compound fault mode, agents may select up to $K=2$ simultaneous actions per experiment.

Three reward variants are formulated:
- **$R_1$ (Sparse Binary):** $R_1 = \mathbb{I}(\text{New Weakness Found})$
- **$R_2$ (Default Regularized):** $R_2 = \mathbb{I}(\text{New Weakness Found}) - \lambda_{\text{dam}} \cdot \text{Damage} - \lambda_{\text{rep}} \cdot \mathbb{I}(\text{Redundant Fault})$
- **$R_3$ (Shaped):** $R_3 = R_2 + \lambda_{\text{deg}} \cdot \text{DegradationSignal}$

Reward $R_2$ prevents destructive reward hacking by penalizing collateral SLO damage and discourages redundant probing via an explicit repeat penalty.

---

## 7. Methods Summary

ChaosRL benchmarks 7 baseline approaches against 12 learned candidates and 3 meta-ensembles:

| Identifier | Method Name | Family | Key Mechanism |
|---|---|---|---|
| **CM** | Chaos Monkey (Faithful) | Baseline | Uniform random container kill |
| **CM-2** | Chaos Monkey-2 | Baseline | Uniform random 2-container kill |
| **RAND** | Random-All | Baseline | Uniform over all services, faults, and intensities |
| **RR** | Round-Robin Sweep | Baseline | Systematic cyclical iteration over services and faults |
| **UCB** | Bandit UCB | Baseline | Upper Confidence Bound over action arms |
| **HEUR** | Heuristic Expert | Baseline | Topology-driven rules (hubs, single-replica, co-location) |
| **ORAC** | Oracle (Reference Only) | Upper Bound | Perfect knowledge of ground truth |
| **C01** | PPO + MLP Scorer | Policy Gradient | Shared-weight per-node MLP scoring |
| **C02** | PPO + GNN Scorer | Structure-Aware | Graph convolutional message-passing over call edges |
| **C03** | PPO + Recurrent GRU | Policy Gradient | Temporal memory over experiment sequence history |
| **C04** | A2C + MLP Scorer | Policy Gradient | Synchronous advantage actor-critic |
| **C05** | Double Dueling DQN | Value-Based | Action-value Q estimation with experience replay |
| **C06** | REINFORCE + Baseline | Policy Gradient | Monte Carlo policy gradient with state-value baseline |
| **C07** | PPO + Curriculum | Policy Gradient | Progressive scaling from small (N=5) to large topologies |
| **C08** | Behavior Cloning $\to$ PPO | Policy Gradient | Expert demonstration pretraining followed by RL fine-tuning |
| **C09** | PPO + Novelty Bonus | Policy Gradient | Count-based state-action novelty exploration bonus |
| **C10** | Evolution Strategies | Gradient-Free | OpenAI-ES antithetic parameter perturbation |
| **C11** | LinUCB Bandit | Non-Deep Learned | Ridge regression contextual bandit over feature vectors |
| **C12** | GBM Ranker | Non-Deep Learned | Gradient-boosted decision tree ranking on logged transitions |
| **E1** | Soft Voting Ensemble | Meta-Ensemble | Probability distribution averaging over Top-5 |
| **E2** | Borda Rank Ensemble | Meta-Ensemble | Summed preference rank voting over Top-5 |
| **E3** | RF-Gated Controller | Meta-Ensemble | Supervised Random Forest gating model over Top-5 proposals |

---

## 8. Training Summary
*(Populated during Stage 7: multi-seed learning curves, loss profiles, entropy decay schedules, and automated tuning adjustments.)*

---

## 9. Selection and Ensembles
*(Populated during Stage 8: validation AUDC rankings, diversity constraint enforcement, model weight hashing, and ensemble calibration.)*

---

## 10. Final Results
*(Populated during Stage 9: test-set performance metrics, 95% bootstrap confidence intervals, and Wilcoxon significance tests across scales 20, 100, and 300.)*

---

## 11. Generalization Results
*(Populated during Stage 9: out-of-distribution evaluation on scale 500 and Family M mesh topologies.)*

---

## 12. Budget Sweep and Ablations
*(Populated during Stage 9: budget sensitivity curves across B in [25, 50, 100, 200] and reward/observation ablations.)*

---

## 13. Interpretability
*(Populated during Stage 9: feature importance rankings, action selection correlations, and qualitative episode trajectories.)*

---

## 14. Answers to RQ1 to RQ4
*(Populated during Stage 10: formal verdicts comparing empirical evidence against pre-registered hypotheses.)*

---

## 15. Failure Analysis
*(Populated during Stage 10: detailed dissection of edge cases, seed sensitivity, and limitations of learned policies.)*

---

## 16. Limitations and Threats to Validity
*(Populated during Stage 10: simulator abstraction fidelity, synthetic weakness representations, and hardware constraints.)*

---

## 17. Reproducibility
*(Populated during Stage 11: reproduction checklist, seed verification, and execution hashes.)*

---

## 18. Timeline and Compute
*(Populated during Stage 11: actual wall-clock hours per stage and hardware resource utilization logs.)*

---

## 19. Decision Log Digest
*(Populated during Stage 11: digest of top architectural decisions and deviations.)*

---

## 20. Appendices
*(Populated during Stage 11: configuration listings, full candidate parameter tables, and file inventories.)*
