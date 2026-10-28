# Table A05-1: Baseline Agent Constraint & Behavioral Compliance Audit

| Baseline Strategy | Action Modalities Permitted | Target Selection Mechanism | Multi-Fault Support | Ground-Truth Access | Audit Behavioral Compliance |
|---|---|---|---|---|---|
| **Chaos Monkey (Faithful)** | Container Kill Only ($\text{Intensity} = \text{MEDIUM}$) | Uniform random over non-gateway services | Single fault only | Strict zero-access | **PASS (Faithful)** |
| **Chaos Monkey-2** | Container Kill Only | Uniform random 2-service subset | 2-container kill | Strict zero-access | **PASS (Faithful 2-kill)** |
| **Random-All** | All 6 fault types $\times$ 3 intensities | Uniform random across entire catalog | $p=0.5$ pair injection | Strict zero-access | **PASS (Catalog-wide)** |
| **Round-Robin Sweep** | All 6 fault types $\times$ 3 intensities | Sequential cursor advancing modulo $18N$ | Single fault | Strict zero-access | **PASS (Orderly sweep)** |
| **Bandit UCB** | All discrete actions in catalog | UCB1 exploration ($\alpha=1.414$) | Single fault | Strict zero-access | **PASS (Formula verified)** |
| **Heuristic Expert** | Kill, Latency, Node, CPU | High in-degree, low replica, co-located | $p=0.5$ targeted pair | Strict zero-access | **PASS (Zero ground truth)** |
| **Oracle (Reference)** | Matching required fault types | Targeted directly at undiscovered weaknesses | Full compound support | **Unrestricted (Upper bound)** | **PASS (Reference bound)** |

*Caption (Table A05-1):*
- **What the reader sees:** Policy constraints, action domains, and information boundaries across all seven evaluated non-learned baseline strategies.
- **What it implies:** Baselines faithfully implement their respective specifications; non-oracle baselines operate with zero access to hidden weakness configurations.
- **Traceability link:** Agent definitions in [baselines.py](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/agents/baselines/baselines.py#L12-L236) and audit verification in [test_audit_s05_baselines.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s05_baselines.py#L25-L65).
