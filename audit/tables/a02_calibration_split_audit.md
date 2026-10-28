# Table A02-1: Empirical Calibration Dataset Inventory & Split Audit

| Fault Modality | Target Telemetry Metric | Fit Partition (Online Boutique) | Held-Out Partition (Sock Shop) | Total Parsed Cases | Raw CSV Source Files | Audit Verification Status |
|---|---|---|---|---|---|---|
| **CPU** | CPU Delta (%) | 25 | 25 | 50 | 75 | Verified (Exact Match) |
| **DELAY** | Latency Ratio ($\times$) | 25 | 25 | 50 | 75 | Verified (Exact Match) |
| **LOSS** | Latency Ratio ($\times$) | 25 | 25 | 50 | 75 | Verified (Exact Match) |
| **MEM** | Latency Ratio ($\times$) | 25 | 25 | 50 | 75 | Verified (Exact Match) |
| **DISK** | Latency Ratio ($\times$) | 25 | 25 | 50 | 75 | Verified (Exact Match) |
| **Total** | Multi-metric | 125 | 125 | 250 | 375 | **VERIFIED (100%)** |

*Caption (Table A02-1):*
- **What the reader sees:** Case counts and raw file counts per fault modality across the fit partition (`RE1-OB`) and held-out partition (`RE1-SS`), verified by independent directory parsing.
- **What it implies:** The empirical calibration dataset satisfies strict split disjointness across topologies and accounts for all 375 ingested raw telemetry files without uncalibrated gaps.
- **Traceability link:** Code paths [parse.py](file:///c:/Users/Felix/Desktop/chaos%20final/src/chaosrl/data/parse.py#L142-L180), [test_audit_s02_data.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s02_data.py#L25-L48), and [rcaeval_manifest.json](file:///c:/Users/Felix/Desktop/chaos%20final/data_raw/rcaeval_manifest.json).

