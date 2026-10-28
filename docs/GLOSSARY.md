# ChaosRL Technical Glossary

This glossary provides formal definitions for concepts in distributed microservice architectures, chaos engineering, reinforcement learning, and statistical testing.

---

### Distributed Systems & Microservices
- **Microservices:** An architectural pattern decomposing software applications into modular, loosely coupled network services communicating over remote procedure calls (RPC) or HTTP REST.
- **Dependency Call Graph:** A directed graph $G = (V, E)$ where vertices $V$ represent services and directed edges $e = (u, v) \in E$ represent upstream caller $u$ invoking downstream callee $v$.
- **Gateway Service:** The root ingress service receiving external end-user requests and routing traffic to downstream business services.
- **Service Level Objective (SLO):** A formal target for service reliability and performance. In ChaosRL, the system SLO is defined at the gateway: 99th percentile (p99) latency $\le 500\text{ ms}$ and request error rate $\le 2\%$.
- **Steady State:** A operational baseline regime wherein a system without injected faults meets its defined SLO in $100\%$ of evaluation seeds (within noise bounds).
- **Cascading Failure:** A failure mode where an outage or performance degradation in a downstream dependency spreads transitively upstream, collapsing caller services.
- **Retry Storm:** Pathological load amplification occurring when upstream services retry failing requests without backoff or jitter, exponentially magnifying traffic on an already saturated downstream service.
- **Circuit Breaker:** A protective architectural pattern that temporarily halts outbound calls to an unhealthy downstream service once error rates cross a defined threshold, preventing upstream thread exhaustion.

---

### Chaos Engineering
- **Chaos Engineering:** The discipline of experimenting on a distributed system to build confidence in the system's capability to withstand turbulent conditions in production.
- **Chaos Monkey:** Netflix's pioneering tool that randomly terminates virtual machine instances or containers in production without topological awareness or history.
- **Fault Injection:** Deliberate introduction of hardware, software, or network anomalies (e.g., container termination, artificial network latency, packet loss, or CPU exhaustion).
- **Planted Weakness:** A latent, ground-truth architectural defect intentionally embedded into a simulated topology (e.g., missing timeout on a critical path, single replica on a hub service).
- **Simple Weakness:** A defect triggered by a single specific fault injection on an individual target.
- **Compound Weakness:** A defect requiring two or more concurrent fault injections (e.g., simultaneous container kill and CPU exhaustion across replicas) to manifest an SLO violation.
- **Decoy:** A service with high connectivity (hub) or prominent structural position that is fortified with multiple replicas, circuit breakers, and aggressive caching, preventing naive degree-based heuristics from succeeding.
- **Damage (Safety Metric):** The cumulative severity-weighted duration during which the gateway SLO is violated during an experiment.

---

### Reinforcement Learning & Machine Learning
- **Agent:** The autonomous decision-maker that observes system states and chooses actions (faults) to maximize long-term reward.
- **Observation Space:** The numerical and topological feature vector representing per-service metrics (latency, error rate, CPU utilization), graph structure (degree, layer depth), and experiment history.
- **Action Mask:** A boolean vector that filters out invalid, exhausted, or redundant candidate actions prior to policy selection.
- **Reward Function ($R_1, R_2, R_3$):** Formulations translating experimental outcomes into scalar feedback:
  - $R_1$: Sparse binary reward (+1 for new weakness, 0 otherwise).
  - $R_2$: Dense regularized reward (+1 for new weakness minus damage penalty and redundancy cost).
  - $R_3$: $R_2$ plus shaping bonus for informative partial service degradation.
- **Area Under the Discovery Curve (AUDC):** The integral of the weakness discovery count plotted against the cumulative experiment budget, normalized by budget and total planted weaknesses.
- **GNN Scorer:** A Graph Neural Network that performs message passing across the microservice call graph to produce action candidate logits.
- **Ensemble Controller:** A meta-policy combining the predictions of multiple diverse models (Soft Voting, Borda Rank Voting, or Random Forest Gating).

