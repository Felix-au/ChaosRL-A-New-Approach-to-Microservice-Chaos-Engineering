# Table A06-2: Candidate Trainable Parameters & Compute Budget Audit

| Candidate Category | Model Implementations | Maximum Observed Parameters | Formal Hardware Ceiling | Budget Utilization (%) | Peak Training RAM (GB) | Machine Constraint Status |
|---|---|---|---|---|---|---|
| **Recurrent Policies** | C03 (PPO-GRU) | 47,123 | 1,000,000 | 4.71% | $< 1.2$ GB | **PASS ($\le 9.0$ GB)** |
| **GNN Architectures** | C02, C07 (PPO-GNN) | 22,611 | 1,000,000 | 2.26% | $< 0.8$ GB | **PASS ($\le 9.0$ GB)** |
| **Standard Policy Gradients** | C01, C04, C06, C08, C09 | 18,323 | 1,000,000 | 1.83% | $< 0.6$ GB | **PASS ($\le 9.0$ GB)** |
| **Supervised Ensembles** | C12 (TreeRanker) | 12,000 | 1,000,000 | 1.20% | $< 0.4$ GB | **PASS ($\le 9.0$ GB)** |
| **Value-Based Networks** | C05 (DQN-Dueling) | 7,634 | 1,000,000 | 0.76% | $< 0.5$ GB | **PASS ($\le 9.0$ GB)** |
| **Gradient-Free Policies** | C10 (ES-Policy) | 2,802 | 1,000,000 | 0.28% | $< 0.3$ GB | **PASS ($\le 9.0$ GB)** |
| **Contextual Bandits** | C11 (LinUCB) | 1,536 | 1,000,000 | 0.15% | $< 0.2$ GB | **PASS ($\le 9.0$ GB)** |
| **Overall Pool** | **All 12 Candidates** | **47,123** | **1,000,000** | **4.71%** | **$< 1.5$ GB** | **PASS (100% compliant)** |

*Caption (Table A06-2):*
- **What the reader sees:** Parameter counts grouped by architecture family compared against the 1,000,000 parameter budget ceiling and memory footprints.
- **What it implies:** Every model in the pool utilizes under 5% of the maximum allowed parameter budget, guaranteeing rapid CPU training and strict compliance with the 9 GB peak RAM constraint.
- **Traceability link:** Original metrics in [stage6_candidate_smoke_benchmarks.csv](file:///c:/Users/Felix/Desktop/chaos%20final/docs/tables/stage6_candidate_smoke_benchmarks.csv), registry [registry.py](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/agents/candidates/registry.py), and test [test_audit_s06_candidates.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s06_candidates.py#L75-L95).
