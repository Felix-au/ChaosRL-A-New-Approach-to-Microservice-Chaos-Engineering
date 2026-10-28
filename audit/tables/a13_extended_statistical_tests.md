# Table A13-2: Extended Statistical Significance and Power Analysis (n=10 vs n=30)

| Hypothesis / Comparison | Cohort | Mean AUDC Diff | Wilcoxon W | Cohen's d | Raw p-value | Adj p (Holm-Bonferroni) | Statistical Power |
|---|---|---|---|---|---|---|---|
| ChaosRL Top-1 vs Chaos Monkey | Original Slice (n=10) | +0.0323 | 27.0 | 0.543 | 0.1211 | **Not Significant** | 0.336 |
| ChaosRL Top-1 vs Heuristic Expert | Original Slice (n=10) | -0.0549 | 12.0 | -0.551 | 0.9473 | **Not Significant** | 0.345 |
| ChaosRL Ensemble vs Chaos Monkey | Original Slice (n=10) | +0.0314 | 26.0 | 0.522 | 0.1484 | **Not Significant** | 0.315 |
| ChaosRL Ensemble vs ChaosRL Top-1 | Original Slice (n=10) | -0.0009 | 1.0 | -0.271 | 1.0000 | **Not Significant** | 0.120 |
| ChaosRL Top-1 vs Chaos Monkey | Extended Slice (n=20) | +0.0502 | 133.0 | 0.770 | 0.0037 | **p = 0.0112** | 0.904 |
| ChaosRL Top-1 vs Heuristic Expert | Extended Slice (n=20) | -0.0300 | 68.0 | -0.324 | 0.9164 | **Not Significant** | 0.280 |
| ChaosRL Ensemble vs Chaos Monkey | Extended Slice (n=20) | +0.0565 | 150.0 | 0.791 | 0.0025 | **p = 0.0099** | 0.918 |
| ChaosRL Ensemble vs ChaosRL Top-1 | Extended Slice (n=20) | +0.0063 | 14.5 | 0.221 | 0.6219 | **Not Significant** | 0.156 |
| ChaosRL Top-1 vs Chaos Monkey | Combined Cohort (n=30) | +0.0442 | 275.0 | 0.703 | 0.0012 | **p = 0.0037** | 0.961 |
| ChaosRL Top-1 vs Heuristic Expert | Combined Cohort (n=30) | -0.0383 | 127.5 | -0.408 | 0.9846 | **Not Significant** | 0.579 |
| ChaosRL Ensemble vs Chaos Monkey | Combined Cohort (n=30) | +0.0481 | 298.0 | 0.709 | 0.0009 | **p = 0.0037** | 0.963 |
| ChaosRL Ensemble vs ChaosRL Top-1 | Combined Cohort (n=30) | +0.0039 | 25.5 | 0.167 | 0.8373 | **Not Significant** | 0.143 |

*(1) What the reader sees: Paired Wilcoxon signed-rank tests, Holm-Bonferroni adjusted p-values, Cohen's d effect sizes, and empirical power for n=10, n=20, and n=30 cohorts.*
*(2) What it implies: With n=10 systems, the test was severely underpowered (power 0.336) resulting in non-significance (p = 0.1211). When powered with n=30 systems (power 0.961), ChaosRL Top-1 and Soft-Vote Ensemble achieve statistically significant superiority over faithful Chaos Monkey (+0.0481 AUDC, p = 0.0037, Cohen's d = 0.709). However, ChaosRL fails to outperform Heuristic Expert (AUDC 0.1145, p = 0.9846) and incurs higher damage than Chaos Monkey.*
*(3) Traceability: Calculated via `scipy.stats.wilcoxon` in `audit/run_extended_evaluation.py`; parameters pre-registered in `audit/preregistered_plan.md`.*