# ChaosRL Modeling Assumptions & Realism Boundaries

This document enumerates all fundamental modeling assumptions, fidelity boundaries, and structural constraints embedded within the ChaosRL discrete-time simulator.

---

## 1. Discrete-Time Aggregate Dynamics vs. Continuous Event Tracing
- **Assumption:** The simulator models system behavior across discrete time ticks (default $\Delta t = 1.0\text{ s}$ per tick) using aggregate load, queueing latency curves, and error rate propagation, rather than microsecond-level packet or discrete-event request traces.
- **Realism Limits:** While discrete-time aggregation enables massive throughput ($> 1,000$ experiments per minute) necessary for multi-seed RL training, it does not capture sub-millisecond OS thread scheduling jitter, TCP slow-start window dynamics, or kernel socket buffer overflows.
- **Justification:** For architectural weakness discovery (e.g., discovering missing circuit breakers, retry storms, and single points of failure), aggregate macroscopic dynamics over seconds provide sufficient fidelity while avoiding intractable computational overhead.

---

## 2. Linear and Heavy-Tailed Topology Generation
- **Assumption:** Microservice call graphs are generated according to two structural families:
  - **Family L (Layered DAG):** Distinct gateway, business, and storage tiers with preferential attachment for shared backend dependencies.
  - **Family M (Mesh / Hub-and-Spoke):** Lateral peer-to-peer invocation clusters with distributed hub nodes.
- **Realism Limits:** Real-world enterprise architectures often exhibit complex circular dependency patterns, event-driven message brokers (Kafka/RabbitMQ), and asynchronous worker pools that depart from pure directed acyclic structures.
- **Justification:** Clear family demarcation allows rigorous evaluation of out-of-distribution (OOD) structural generalization (RQ4) by training strictly on Family L and evaluating zero-shot on Family M.

---

## 3. Ground-Truth Weakness Planting & Decoys
- **Assumption:** Ground-truth weaknesses are algorithmically planted based on distributed systems antipatterns (unprotected single replicas, missing timeouts, retry storms, co-located critical replicas). Decoys are deliberately inserted to ensure naive heuristics fail.
- **Realism Limits:** In production systems, weaknesses may arise from application code logic bugs (e.g., memory leaks, database connection pool deadlocks, or bad SQL query plans) that are orthogonal to infrastructure topology.
- **Justification:** Algorithmic planting enables exact mathematical calculation of discovery recall, precision, and AUDC against a known ground truth, which is impossible in noisy production environments where the denominator of undiscovered bugs is unknown.

---

## 4. Empirical Calibration Scope
- **Assumption:** Fault effect distributions (latency elevation, CPU saturation, packet loss propagation) are fitted to empirical measurements from the public RCAEval microservice benchmark.
- **Realism Limits:** The calibration dataset grounds the *response functions* of individual faults in empirical measurements, but the planted weaknesses themselves remain synthetic. ChaosRL is therefore classified as a **data-calibrated simulator**, not a physical container cluster.

