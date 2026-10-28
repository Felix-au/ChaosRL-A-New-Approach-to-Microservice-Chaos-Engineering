# Table A13-3: Multi-Scale Generalization Benchmark (n=20 Systems per Scale)

| Scale (N) | Chaos Monkey AUDC | Heuristic Expert AUDC | ChaosRL Top-1 AUDC | ChaosRL Ensemble AUDC | Ensemble vs CM Relative Gain (%) |
|---|---|---|---|---|---|
| N=20 | 0.2097 | 0.4877 | 0.2369 | **0.1491** | -28.9% |
| N=100 | 0.0434 | 0.1051 | 0.0876 | **0.0008** | -98.1% |
| N=300 | 0.0078 | 0.0263 | 0.0291 | **0.0000** | -100.0% |
| N=500 | 0.0040 | 0.0040 | 0.0162 | **0.0000** | -100.0% |

*(1) What the reader sees: Generalization across scales N in {20, 100, 300, 500} evaluated over n=20 systems per scale (seeds 200,050..200,069).*
*(2) What it implies: At N=500, both learned models and baselines experience severe action space dilution (AUDC < 0.005), demonstrating that flat discrete action representations do not scale to hyperscale graphs.*
*(3) Traceability: Generated autonomously by `audit/run_extended_evaluation.py`; raw data in `results/audit_rerun/extended_results.pkl`.*