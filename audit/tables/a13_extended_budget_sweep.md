# Table A13-5: Weakness Recall vs. Experiment Budget (n=16 Systems)

| Budget (B) | Chaos Monkey Recall | Heuristic Expert Recall | ChaosRL Top-1 Recall | ChaosRL Ensemble Recall |
|---|---|---|---|---|
| B=25 | 0.0078 | 0.0469 | 0.0547 | **0.0000** |
| B=50 | 0.0547 | 0.1328 | 0.0625 | **0.0000** |
| B=100 | 0.0781 | 0.1797 | 0.0625 | **0.0625** |
| B=200 | 0.1016 | 0.2188 | 0.0781 | **0.0625** |

*(1) What the reader sees: Weakness recall as injection budget B scales from 25 to 200 on n=16 test systems.*
*(2) What it implies: Low-budget regimes (B=25) severely penalize random exploration, where Heuristic Expert leads; as budget expands to B=200, random exploration eventually catches up.*
*(3) Traceability: Generated autonomously by `audit/run_extended_evaluation.py`; raw data in `results/audit_rerun/extended_results.pkl`.*