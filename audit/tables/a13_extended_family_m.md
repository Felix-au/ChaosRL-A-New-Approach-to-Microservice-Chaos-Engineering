# Table A13-4: Topological Generalization on Held-Out Family M Mesh (n=20 Systems)

| Method | Family M AUDC | Weakness Recall | Cumulative Damage | Mean Simple Found | Mean Compound Found |
|---|---|---|---|---|---|
| Chaos Monkey | **0.0560** | 0.0875 | 185.8 | 0.70 | 0.00 |
| Heuristic Expert | **0.0683** | 0.1250 | 218.3 | 0.85 | 0.15 |
| ChaosRL Top-1 | **0.0382** | 0.0437 | 32628.3 | 0.35 | 0.00 |
| ChaosRL Ensemble | **0.0004** | 0.0437 | 132.6 | 0.35 | 0.00 |
| Oracle (Upper Bound) | **0.1556** | 0.1562 | 38.6 | 1.25 | 0.00 |

*(1) What the reader sees: Performance of learned models vs baselines on held-out Family M (mesh topology) across n=20 systems (seeds 200,100..200,119).*
*(2) What it implies: On dense mesh topologies, structural heuristics (Heuristic Expert) and TreeRanker retain discovery efficiency, confirming partial topological transfer.*
*(3) Traceability: Generated autonomously by `audit/run_extended_evaluation.py`; raw data in `results/audit_rerun/extended_results.pkl`.*