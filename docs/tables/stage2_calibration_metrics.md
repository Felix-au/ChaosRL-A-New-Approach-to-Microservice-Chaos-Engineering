<!-- Table: stage2_calibration_metrics -->

| Fault Type | Metric | Fit Cases (OB) | Held-Out Cases (SS) | Empirical Mean | Simulated Mean | Wasserstein Distance (Fit) | Wasserstein Distance (Held-Out) | KS Test Stat | KS p-value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CPU | CPU Delta (%) | 25 | 25 | 75.2728 | 75.2133 | 0.9570 | 75.2133 | 1.0000 | 0.0000 |
| DELAY | Latency Ratio (x) | 25 | 25 | 68.2732 | 68.7145 | 7.1678 | 67.7145 | 1.0000 | 0.0000 |
| LOSS | Latency Ratio (x) | 25 | 25 | 8.0856 | 5.7901 | 4.5960 | **4.9520** | 0.8000 | 0.0000 |
| MEM | Latency Ratio (x) | 25 | 25 | 23.2148 | 23.4068 | 11.6618 | 22.4552 | 0.9380 | 0.0000 |
| DISK | Latency Ratio (x) | 25 | 25 | 6.7564 | 7.3982 | 2.2568 | 6.4105 | 0.9780 | 0.0000 |
