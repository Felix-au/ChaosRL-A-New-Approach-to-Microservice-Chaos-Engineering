# Table A08-2: Frozen Checkpoints Cryptographic SHA-256 Audit

| Candidate ID | Model Checkpoint File | File Size (Bytes) | Pre-Test Manifest SHA-256 Hash | Post-Run Audit SHA-256 Hash | Bitwise Match Status |
|---|---|---|---|---|---|
| **C12** | `rank1_C12_TreeRanker.pkl` | 68,443 | `ea63ee26a99f9fda8b383e6b26e02000b76c2cf987f68627c64fca80a7d21625` | `ea63ee26a99f9fda8b383e6b26e02000b76c2cf987f68627c64fca80a7d21625` | **MATCH (Identical)** |
| **C09** | `rank2_C09_PPO-RND.pt` | 77,889 | `645415e9ae31ddf084ddf97e476cc3b9898ac52546aaf38bfa8df9f079ac8655` | `645415e9ae31ddf084ddf97e476cc3b9898ac52546aaf38bfa8df9f079ac8655` | **MATCH (Identical)** |
| **C02** | `rank3_C02_PPO-GNN.pt` | 95,161 | `335b00e2c3574026fcca6327819001779b96677a2c64d9737262e20a48191474` | `335b00e2c3574026fcca6327819001779b96677a2c64d9737262e20a48191474` | **MATCH (Identical)** |
| **C03** | `rank4_C03_PPO-GRU.pt` | 193,489 | `6ae5bb53d9d70d2cf4a1bff06ca6ff579edefcb470a8c48be17ad7ff2088627e` | `6ae5bb53d9d70d2cf4a1bff06ca6ff579edefcb470a8c48be17ad7ff2088627e` | **MATCH (Identical)** |
| **C06** | `rank5_C06_REINFORCE.pt` | 77,889 | `c6fb7d2a7fa30b42a3e20e92662df08b2909a117db1b4c16ea2464334424f5cd` | `c6fb7d2a7fa30b42a3e20e92662df08b2909a117db1b4c16ea2464334424f5cd` | **MATCH (Identical)** |

*Caption (Table A08-2):*
- **What the reader sees:** File sizes, manifest SHA-256 hashes, and audit recomputed SHA-256 hashes for all five frozen model checkpoints in `results/checkpoints/frozen_top5/`.
- **What it implies:** Zero tampering or retrospective model tuning occurred; weights remained cryptographically frozen before, during, and after test set evaluation.
- **Traceability link:** Manifest file [frozen_manifest.json](file:///c:/Users/Felix/Desktop/chaos%20final/results/frozen_manifest.json) and cryptographic verification test [test_audit_s08_ensembles.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s08_ensembles.py#L75-L100).

