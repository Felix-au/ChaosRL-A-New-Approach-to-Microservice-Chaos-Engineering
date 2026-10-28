# Table A05-2: Validation Baseline Performance Metrics & Confidence Intervals ($n=20$ systems)

| Baseline Method | Mean Weakness Recall | Recall 95% Bootstrap CI | Normalized AUDC | AUDC 95% Bootstrap CI | Mean Cumulative Damage | Damage 95% Bootstrap CI | Audit Validation Status |
|---|---|---|---|---|---|---|---|
| **Chaos Monkey (Faithful)** | 0.0750 | [0.037, 0.113] | 0.0395 | [0.013, 0.070] | 178.26 | [123.4, 232.8] | Verified |
| **Chaos Monkey-2** | 0.1125 | [0.087, 0.125] | 0.0662 | [0.045, 0.086] | 459.48 | [392.8, 530.9] | Verified |
| **Random-All** | 0.1875 | [0.100, 0.287] | 0.0909 | [0.040, 0.146] | 169,221.92 | [28,677.4, 311,065.2] | Verified |
| **Round-Robin Sweep** | 0.1250 | [0.075, 0.175] | 0.0955 | [0.059, 0.129] | 568,691.78 | [561,270.9, 580,914.3] | Verified |
| **Bandit UCB** | 0.0500 | [0.013, 0.087] | 0.0364 | [0.002, 0.072] | 56,281.06 | [272.5, 112,476.9] | Verified |
| **Heuristic Expert** | 0.1750 | [0.138, 0.212] | 0.1054 | [0.077, 0.141] | 262.54 | [221.7, 301.7] | Verified |
| **Oracle (Reference)** | 0.2500 | [0.188, 0.312] | 0.2482 | [0.187, 0.310] | 42.93 | [24.0, 61.5] | Verified |

*Caption (Table A05-2):*
- **What the reader sees:** Recall, Area Under the Discovery Curve (AUDC), and collateral damage metrics across 20 validation systems (Scale 100, seeds 100,000..100,019) with 95% bootstrap confidence intervals.
- **What it implies:** Faithful Chaos Monkey incurs minimal damage but achieves very low recall (7.5%) due to modality blindness; Heuristic Expert achieves the best non-oracle balance (AUDC 0.1054, Damage 262.54).
- **Traceability link:** Original validation table [stage5_baseline_validation_results.csv](file:///c:/Users/Felix/Desktop/chaos%20final/docs/tables/stage5_baseline_validation_results.csv), facts [facts.json](file:///c:/Users/Felix/Desktop/chaos%20final/results/facts.json), and test [test_audit_s05_baselines.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s05_baselines.py#L70-L105).

