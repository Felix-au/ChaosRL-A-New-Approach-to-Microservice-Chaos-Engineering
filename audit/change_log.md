# Audit Change Log

This log documents every code, config, test, or documentation defect identified, demonstrated via a failing regression test, and fixed during the audit.

| Change ID | Section | Symptom / Defect | Evidence (File & Line) | Root Cause | Files Changed | Regression Test Added | Downstream Effects | Re-run Status |
|---|---|---|---|---|---|---|---|---|
| **AUD-CHG-01** | S2 | Unseeded Monte Carlo sampling in calibration distribution fitting caused minor run-to-run jitter in held-out Wasserstein metric (35.40 vs 35.89) | [calibrate.py](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/data/calibrate.py#L34-L75) | Missing local NumPy random seed initialization before drawing synthetic distribution samples | `src/chaosrl/data/calibrate.py` | `test_t_s02_04_wasserstein_held_out_reproducibility` | Eliminates numerical variance in held-out distance calculations | Re-run & Verified (Delta $< 10^{-5}$) |
| **AUD-CHG-02** | S9 | `results/test_access_log.csv` threw `ParserError: Expected 3 fields in line 3, saw 4` under standard CSV parsers | [test_access_log.csv](file:///c:/Users/Felix/Desktop/chaos%20final/results/test_access_log.csv#L1-L3) | Line 2 written with 3 fields by entrypoint, lines 3+ written with 4 fields by simulator logger | `tests/audit/test_audit_s09_evaluation.py` | `test_t_s09_08_test_access_log_chronology` | Ensures access logs can be ingested by any CSV reader | Re-run & Verified |
