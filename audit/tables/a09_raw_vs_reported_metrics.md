# Table A09-1: Scale 100 Test Metrics: Raw Logs vs. Documented Prose Discrepancy

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
