# Table A09-2: Statistical Hypothesis Testing Recomputation & Multiplicity Control

| Comparison Pair | Sample Size ($n$) | Mean Paired AUDC Delta ($\Delta$) | Wilcoxon Signed-Rank $W$ | Unadjusted $p$-value | Holm-Bonferroni Adjusted $p$-value | Documented Verdict | True Statistical Verdict |
|---|---|---|---|---|---|---|---|
| **ChaosRL Top-1 vs. Chaos Monkey** | 10 | $-0.0353$ | 16.0 | 0.8125 | **1.0000** | Proclaimed "CONFIRMED" | **NOT SIGNIFICANT (Loss)** |
| **ChaosRL Top-1 vs. Heuristic Expert** | 10 | $+0.0011$ | 24.0 | 0.5000 | **1.0000** | Proclaimed "CONFIRMED" | **NOT SIGNIFICANT (Tie)** |
| **ChaosRL Ensemble vs. Chaos Monkey** | 10 | $-0.0353$ | 16.0 | 0.8125 | **1.0000** | Proclaimed "CONFIRMED" | **NOT SIGNIFICANT (Loss)** |
| **ChaosRL Ensemble vs. ChaosRL Top-1** | 10 | $+0.0000$ | 0.0 | 1.0000 | **1.0000** | Proclaimed "CONFIRMED" | **NOT SIGNIFICANT (Tie)** |

*Caption (Table A09-2):*
- **What the reader sees:** Recomputed Wilcoxon signed-rank statistics, unadjusted $p$-values, and Holm-Bonferroni adjusted $p$-values for the four core statistical comparisons on Scale 100 ($n=10$ test systems).
- **What it implies:** Under rigorous statistical testing on the 10-system sample, ChaosRL demonstrates zero statistically significant advantage over Chaos Monkey ($p=1.0$) or Heuristic Expert ($p=1.0$), and the ensemble achieves zero gain over Top-1 ($\Delta = 0.0000, p=1.0$).
- **Traceability link:** Original statistical table [stage9_statistical_tests.csv](file:///c:/Users/Felix/Desktop/chaos%20final/docs/tables/stage9_statistical_tests.csv), facts [facts.json](file:///c:/Users/Felix/Desktop/chaos%20final/results/facts.json), and audit test [test_audit_s09_evaluation.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s09_evaluation.py#L65-L100).

