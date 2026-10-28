<!-- Table: stage2_calibration_metrics -->

| Fault Type | Metric | Fit Cases (OB) | Held-Out Cases (SS) | Empirical Mean | Simulated Mean | Wasserstein Distance (Fit) | Wasserstein Distance (Held-Out) | KS Test Stat | KS p-value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CPU | CPU Delta (%) | 25 | 25 | 75.2728 | 75.3740 | 0.9030 | 75.3740 | 1.0000 | 0.0000 |
| DELAY | Latency Ratio (x) | 25 | 25 | 68.2732 | 69.2649 | 6.8915 | 68.2649 | 1.0000 | 0.0000 |
| LOSS | Latency Ratio (x) | 25 | 25 | 8.0856 | 6.2183 | 4.5126 | **5.3725** | 0.8130 | 0.0000 |
| MEM | Latency Ratio (x) | 25 | 25 | 23.2148 | 24.8680 | 10.6293 | 23.9229 | 0.9340 | 0.0000 |
| DISK | Latency Ratio (x) | 25 | 25 | 6.7564 | 7.0674 | 2.0183 | 6.0836 | 0.9740 | 0.0000 |
