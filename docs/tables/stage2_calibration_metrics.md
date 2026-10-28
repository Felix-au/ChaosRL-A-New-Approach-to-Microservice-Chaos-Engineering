<!-- Table: stage2_calibration_metrics -->

| Fault Type | Metric | Fit Cases (OB) | Held-Out Cases (SS) | Empirical Mean | Simulated Mean | Wasserstein Distance (Fit) | Wasserstein Distance (Held-Out) | KS Test Stat | KS p-value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CPU | CPU Delta (%) | 25 | 25 | 75.2728 | 75.3286 | 0.9248 | 75.3286 | 1.0000 | 0.0000 |
| DELAY | Latency Ratio (x) | 25 | 25 | 68.2732 | 68.4398 | 6.8550 | 67.4398 | 1.0000 | 0.0000 |
| LOSS | Latency Ratio (x) | 25 | 25 | 8.0856 | 7.0690 | 4.7251 | 6.2298 | 0.8120 | 0.0000 |
| MEM | Latency Ratio (x) | 25 | 25 | 23.2148 | 23.1325 | 11.0839 | 22.1925 | 0.9290 | 0.0000 |
| DISK | Latency Ratio (x) | 25 | 25 | 6.7564 | 7.1857 | 2.3517 | **6.1969** | 0.9740 | 0.0000 |
