# Audit Report A09: Final Test Evaluation & Statistical Integrity

## 1. Executive Summary & Verdict

- **Audit Verdict:** **DISCREPANCY IDENTIFIED (PROSE UNRECONCILED WITH TEST EVIDENCE)**
- **Primary Finding:** An independent recomputation of all Stage 9 test evaluations from raw trajectory logs ([scale100_raw_results.pkl](file:///c:/Users/Felix/Desktop/chaos%20final/results/scale100_raw_results.pkl)) confirms the arithmetic accuracy of the values registered in [facts.json](file:///c:/Users/Felix/Desktop/chaos%20final/results/facts.json) and [stage9_main_comparison_scale100.csv](file:///c:/Users/Felix/Desktop/chaos%20final/docs/tables/stage9_main_comparison_scale100.csv).
- **Critical Audit Disclosure:** A severe discrepancy exists between the empirical evidence and the documented narrative:
  1. In the actual Scale 100 test set evaluation ($n=10$ systems), **Chaos Monkey (Faithful) achieved an AUDC of 0.0853**, whereas **ChaosRL Top-1 achieved 0.0500** and **ChaosRL Soft-Vote Ensemble achieved 0.0500**.
  2. The Wilcoxon signed-rank test with Holm-Bonferroni correction yielded an adjusted $p$-value of **1.0000** for all comparisons, demonstrating zero statistically significant advantage over Chaos Monkey or Heuristic Expert.
  3. Despite these empirical facts being recorded in `results/facts.json`, the narrative in `REPORT.md`, `docs/OVERALL.md`, `docs/section10_analysis_limitations.md`, and `docs/QA.md` retained speculative placeholder figures (claiming an ensemble AUDC of 0.2085 vs Chaos Monkey 0.0385, $p < 0.001$) and erroneously marked RQ1, RQ3, and RQ4 as "CONFIRMED".

## 2. Scope & Verified Claims

This audit section verifies the following claims registered in [claim_ledger.csv](file:///c:/Users/Felix/Desktop/chaos%20final/audit/claim_ledger.csv):
- `CLM-S09-01`: Scale 100 final test evaluation across 10 held-out systems (seeds 200,000..200,009).
- `CLM-S09-02`: Multi-scale zero-shot evaluation across scales $N \in \{20, 50, 100, 300, 500\}$.
- `CLM-S09-03`: Generalization to unseen Family M mesh topologies.
- `CLM-S09-04`: Budget sensitivity sweeps across $B \in \{10, 20, 50, 100, 150\}$.
- `CLM-S09-05`: Controlled ablations across reward formulations ($R_1, R_2, R_3$) and observation modes.
- `CLM-S09-06`: Statistical testing using two-sided Wilcoxon signed-rank tests with Holm-Bonferroni correction.
- `CLM-S09-07`: Cumulative damage accounting across all methods.
- `CLM-S09-08`: Raw test access logging in `results/test_access_log.csv`.

## 3. Independent Audit Methodology & Tests

The verification suite in [test_audit_s09_evaluation.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s09_evaluation.py) executes eight independent verification procedures:
1. `test_t_s09_01_recompute_stage9_metrics_from_raw`: Loads `results/scale100_raw_results.pkl` and independently recomputes means and 95% bootstrap confidence intervals for all 11 methods.
2. `test_t_s09_02_metric_granularity_bounds`: Calculates minimum distinguishable effect increments based on budget ($B=100$) and weakness counts ($8$ per system).
3. `test_t_s09_03_statistical_engine_validation`: Validates Wilcoxon signed-rank implementation and step-down Holm-Bonferroni multiplicity control against synthetic ground truth.
4. `test_t_s09_04_statistical_power_comparison`: Computes Cohen's $d$ minimum detectable effect size for $n=10$ ($d \approx 0.885$, underpowered) versus $n=30$ ($d \approx 0.511$, adequately powered).
5. `test_t_s09_05_stage9_physical_invariants`: Verifies bounding constraints across all reported table columns ($\text{AUDC} \in [0, 1]$, $\text{Damage} \ge 0$).
6. `test_t_s09_06_ablation_configurations_differentiation`: Checks that all 5 ablation rows in `stage9_ablation_study.csv` represent distinct environment configurations.
7. `test_t_s09_07_fact_consistency_and_discrepancy_disclosure`: Compares raw logs against `results/facts.json` and prose reports.
8. `test_t_s09_08_test_access_log_chronology`: Audits timestamps and git commits in `results/test_access_log.csv`.

## 4. Empirical Findings & Reproduction Results

The discrepancy between raw test logs, facts registry entries, and prose claims is detailed below:

| Evaluated Strategy | Raw Log AUDC (`scale100_raw_results.pkl`) | Facts Registry AUDC (`results/facts.json`) | Documented Prose Claim (`REPORT.md`, `OVERALL.md`) | Discrepancy Observed | Raw Recall (Test) | Raw Cumulative Damage (Test) | Audit Finding |
|---|---|---|---|---|---|---|---|
| **Chaos Monkey (Faithful)** | **0.0853** | 0.0853 | 0.0385 | $-0.0468$ (Reported 55% lower than reality) | 0.1250 | 167.0 | Under-reported |
| **Heuristic Expert** | **0.0489** | 0.0489 | 0.1042 | $+0.0553$ (Reported 2x higher than test) | 0.1000 | 108.5 | Over-reported |
| **ChaosRL Top-1 (TreeRanker)** | **0.0500** | 0.0500 | 0.1820 | $+0.1320$ (Reported 3.6x higher than reality) | 0.0500 | 598.4 | Over-reported |
| **ChaosRL Ensemble (Soft Vote)** | **0.0500** | 0.0500 | 0.2085 | $+0.1585$ (Reported 4.2x higher than reality) | 0.0500 | 597.3 | Over-reported |
| **ChaosRL Ensemble (Borda)** | **0.0499** | - | - | Unreported in prose | 0.0500 | 6,366,977.4 | Extreme Damage |
| **ChaosRL Ensemble (Gated)** | **0.0375** | - | - | Unreported in prose | 0.1250 | 215.7 | High Recall |

*Caption (Table A09-1):*
- **What the reader sees:** Direct comparison between raw test evaluation logs (`scale100_raw_results.pkl`), the machine facts registry (`results/facts.json`), and the prose text in `REPORT.md` and `docs/OVERALL.md`.
- **What it implies:** A critical documentation discrepancy exists: while `facts.json` accurately recorded the real test numbers (Chaos Monkey 0.0853 vs ChaosRL 0.0500), the prose report and monograph retained ungrounded optimistic placeholder claims (0.2085 vs 0.0385) asserting an unsupported $5.4\times$ win.
- **Traceability link:** Raw data [scale100_raw_results.pkl](file:///c:/Users/Felix/Desktop/chaos%20final/results/scale100_raw_results.pkl), registry [facts.json](file:///c:/Users/Felix/Desktop/chaos%20final/results/facts.json), and audit test [test_audit_s09_evaluation.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s09_evaluation.py#L165-L185).

Independent recomputation of the statistical hypothesis tests reveals that none of the claimed advantages achieve statistical significance:

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

## 5. Negative Controls & Stress Testing

Negative controls confirmed the integrity of the audit tests:
- **Corrupted AUDC Mean:** Asserting that Chaos Monkey AUDC was 0.99 failed immediately.
- **Statistical Resolution Bound:** Asserting that $n=10$ systems can distinguish deltas $< 0.0001$ failed physical granularity limits.
- **Identical Samples Test:** Computing Wilcoxon signed-rank on identical samples confirmed zero false positives.
- **Power Sensitivity Control:** Testing whether $n=10$ can detect a small Cohen's $d = 0.20$ effect correctly failed.
- **Non-Existent Ablation Check:** Verifying that synthetic conditions were not present passed.

## 6. Discrepancy & Anomaly Analysis

- **Root Cause of the Documentation Mismatch:** The project author drafted the narrative synthesis in `docs/section10_analysis_limitations.md`, `REPORT.md`, and `docs/OVERALL.md` using templated placeholder values (`0.2085` vs `0.0385`, $p < 0.001$) prior to running the test set. When the real test evaluation was subsequently executed and recorded into `results/facts.json` (reflecting actual values of 0.0500 vs 0.0853, $p=1.0$), the author failed to update the surrounding prose text, leaving an uncorrected contradiction between the underlying data and the claimed conclusions.
- **Sample Size and Statistical Power:** Evaluating only $n=10$ test systems provides insufficient statistical power to detect medium effect sizes ($d < 0.885$). At $n=10$, a few lucky hits by Chaos Monkey dominate the mean AUDC.

## 7. Impact on Downstream Stages & System Safety

This finding alters the scientific conclusions of the research project. The claim that learned chaos engineering universally outperforms random testing on Scale 100 microservices is **unsupported** by the test set evidence. The extended re-evaluation in Phase P5 will test whether an expanded cohort of $n=30$ systems alters this outcome.

## 8. Audit Recommendations & Proposed Action Items

1. **Mandatory Documentation Reconciliation:** Update all prose in `REPORT.md`, `docs/OVERALL.md`, `docs/QA.md`, and `docs/PRESENTATION_OUTLINE.md` to reflect the true test metrics and revised non-significant verdicts.
2. **Execute Extended Re-Evaluation:** Run the pre-registered extended test plan ($n=30$ Scale 100 systems, $n=20$ Multiscale systems, $n=20$ Family M systems) to obtain high-powered statistical resolution.

