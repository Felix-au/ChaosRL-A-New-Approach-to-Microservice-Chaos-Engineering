<!-- Table: stage2_calibration_metrics -->

| Fault Type | Metric | Fit Cases (OB) | Held-Out Cases (SS) | Empirical Mean | Simulated Mean | Wasserstein Distance (Fit) | Wasserstein Distance (Held-Out) | KS Test Stat | KS p-value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CPU | CPU Delta (%) | 25 | 25 | 75.2728 | 75.3666 | 0.9343 | 75.3666 | 1.0000 | 0.0000 |
| DELAY | Latency Ratio (x) | 25 | 25 | 68.2732 | 68.3627 | 7.1956 | 67.3627 | 1.0000 | 0.0000 |
| LOSS | Latency Ratio (x) | 25 | 25 | 8.0856 | 6.1690 | 4.6286 | **5.3228** | 0.8220 | 0.0000 |
| MEM | Latency Ratio (x) | 25 | 25 | 23.2148 | 25.9706 | 11.2332 | 25.0215 | 0.9370 | 0.0000 |
| DISK | Latency Ratio (x) | 25 | 25 | 6.7564 | 7.3399 | 2.3033 | 6.3552 | 0.9710 | 0.0000 |
