<!-- Table: stage2_calibration_metrics -->

| Fault Type | Metric | Fit Cases (OB) | Held-Out Cases (SS) | Empirical Mean | Simulated Mean | Wasserstein Distance (Fit) | Wasserstein Distance (Held-Out) | KS Test Stat | KS p-value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CPU | CPU Delta (%) | 25 | 25 | 75.2728 | 75.4074 | 0.9117 | 75.4074 | 1.0000 | 0.0000 |
| DELAY | Latency Ratio (x) | 25 | 25 | 68.2732 | 69.7968 | 6.9376 | 68.7968 | 1.0000 | 0.0000 |
| LOSS | Latency Ratio (x) | 25 | 25 | 8.0856 | 6.0298 | 4.5311 | **5.2012** | 0.8070 | 0.0000 |
| MEM | Latency Ratio (x) | 25 | 25 | 23.2148 | 26.0074 | 14.0002 | 25.0667 | 0.9260 | 0.0000 |
| DISK | Latency Ratio (x) | 25 | 25 | 6.7564 | 7.0994 | 2.2431 | 6.1086 | 0.9810 | 0.0000 |
