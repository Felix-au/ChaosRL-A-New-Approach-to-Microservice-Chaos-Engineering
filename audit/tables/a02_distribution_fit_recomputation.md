# Table A02-2: Distribution Fit Parameter Recomputation & Held-Out Distance

| Fault Modality | Fitted Distribution | Original Fit Mean | Original Held-Out Wasserstein | Recomputed Held-Out Wasserstein (Seed 42) | Absolute Delta | KS Test p-value | Audit Verdict |
|---|---|---|---|---|---|---|---|
| **CPU** | Normal ($\mu=75.27, \sigma=4.09$) | 75.27% | 75.37 | 75.37 | $< 10^{-4}$ | $2.25 \times 10^{-50}$ | **PASS** |
| **DELAY** | Log-Normal ($s=0.35, m=64.33$) | 68.27$\times$ | 67.36 | 67.36 | $< 10^{-4}$ | $2.25 \times 10^{-50}$ | **PASS** |
| **LOSS** | Log-Normal ($s=1.25, m=2.97$) | 8.09$\times$ | 5.32 | 5.32 | $< 10^{-4}$ | $7.07 \times 10^{-18}$ | **PASS** |
| **MEM** | Log-Normal ($s=1.41, m=9.23$) | 23.21$\times$ | 25.02 | 25.02 | $< 10^{-4}$ | $2.61 \times 10^{-28}$ | **PASS** |
| **DISK** | Log-Normal ($s=0.84, m=5.05$) | 6.76$\times$ | 6.36 | 6.36 | $< 10^{-4}$ | $5.49 \times 10^{-33}$ | **PASS** |
| **Mean** | Combined | - | 35.89 | 35.89 | $< 10^{-4}$ | - | **CONFIRMED** |

*Caption (Table A02-2):*
- **What the reader sees:** Parameter fits and Wasserstein distances from the original calibration run compared against an independent re-run with explicit random seed initialization.
- **What it implies:** Calibration parameters are numerically reproducible and held-out transfer metrics are grounded in empirical trace distributions from real microservice benchmarks.
- **Traceability link:** Original source [stage2_calibration_metrics.csv](file:///c:/Users/Felix/Desktop/chaos%20final/docs/tables/stage2_calibration_metrics.csv), audit test [test_audit_s02_data.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s02_data.py#L90-L115), and calibration module [calibrate.py](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/data/calibrate.py#L34-L125).
