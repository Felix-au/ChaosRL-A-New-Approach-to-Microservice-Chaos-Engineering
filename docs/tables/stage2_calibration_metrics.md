<!-- Table: stage2_calibration_metrics -->

| Fault Type | Metric | Fit Cases (OB) | Held-Out Cases (SS) | Empirical Mean | Simulated Mean | Wasserstein Distance (Fit) | Wasserstein Distance (Held-Out) | KS Test Stat | KS p-value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CPU | CPU Delta (%) | 25 | 25 | 75.2728 | 75.3519 | 0.9330 | 75.3519 | 1.0000 | 0.0000 |
| DELAY | Latency Ratio (x) | 25 | 25 | 68.2732 | 69.9316 | 7.0795 | 68.9316 | 1.0000 | 0.0000 |
| LOSS | Latency Ratio (x) | 25 | 25 | 8.0856 | 6.6551 | 5.1456 | 5.8073 | 0.8130 | 0.0000 |
| MEM | Latency Ratio (x) | 25 | 25 | 23.2148 | 24.7453 | 11.4037 | 23.7983 | 0.9350 | 0.0000 |
| DISK | Latency Ratio (x) | 25 | 25 | 6.7564 | 6.7767 | 2.0419 | **5.7978** | 0.9620 | 0.0000 |
