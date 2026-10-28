# Table A08-1: Top 5 Selection & Algorithmic Diversity Constraint Audit

| Rank | Candidate ID | Name | Algorithmic Family | Validation AUDC | Family Quota Count (Max 2) | Selection Decision | Audit Diversity Verdict |
|---|---|---|---|---|---|---|---|
| **1** | **C12** | TreeRanker | Supervised / Heuristic | 0.0938 | 1 / 2 | Selected (Rank 1 overall) | **PASS (Compliant)** |
| **2** | **C09** | PPO-RND | Curiosity / Exploration | 0.0489 | 1 / 2 | Selected (Rank 2 overall) | **PASS (Compliant)** |
| **3** | **C02** | PPO-GNN | Structure-Aware | 0.0435 | 1 / 2 | Selected (Rank 3 overall) | **PASS (Compliant)** |
| **4** | **C03** | PPO-GRU | Recurrent Policy | 0.0390 | 1 / 2 | Selected (Rank 4 overall) | **PASS (Compliant)** |
| **5** | **C06** | REINFORCE | Policy Gradient | 0.0339 | 1 / 2 | Selected (Rank 5 overall) | **PASS (Compliant)** |

*Caption (Table A08-1):*
- **What the reader sees:** Final validation ranking, candidate ID, algorithmic family, validation AUDC, and family quota occupancy for the Top 5 selected agents.
- **What it implies:** All five selected models belong to distinct algorithmic paradigms (zero duplicate families), fully satisfying the diversity constraint ($\le 2$ per family).
- **Traceability link:** Original manifest [frozen_manifest.json](file:///c:/Users/Felix/Desktop/chaos%20final/results/frozen_manifest.json), validation summary [stage8_top5_manifest.csv](file:///c:/Users/Felix/Desktop/chaos%20final/docs/tables/stage8_top5_manifest.csv), and test [test_audit_s08_ensembles.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s08_ensembles.py#L25-L50).
