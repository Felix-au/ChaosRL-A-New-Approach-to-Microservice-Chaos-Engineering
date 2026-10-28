# Audit Report A08: Top 5 Selection, Meta-Ensembles & Manifest Freezing

## 1. Executive Summary & Verdict

- **Audit Verdict:** **PASS (CONFIRMED)**
- **Primary Finding:** The Top 5 selection protocol adhered strictly to the pre-registered ranking and diversity rules. Based on validation AUDC across 20 validation systems, the top five agents selected were C12 (TreeRanker, AUDC 0.0938), C09 (PPO-RND, AUDC 0.0489), C02 (PPO-GNN, AUDC 0.0435), C03 (PPO-GRU, AUDC 0.0390), and C06 (REINFORCE, AUDC 0.0339). Each winner belongs to a completely distinct algorithmic family (supervised, exploration, structure-aware, recurrent, and policy gradient), fully satisfying the diversity quota ($\le 2$ models per family).
- **Cryptographic Freeze Integrity:** All five selected checkpoint files were archived into `results/checkpoints/frozen_top5/` and catalogued in `results/frozen_manifest.json`. Independent recomputation of cryptographic SHA-256 hashes confirms bit-for-bit identity across all five frozen models.

## 2. Scope & Verified Claims

This audit section verifies the following claims registered in [claim_ledger.csv](file:///c:/Users/Felix/Desktop/chaos%20final/audit/claim_ledger.csv):
- `CLM-S08-01`: Top 5 candidate selection from validation ranking under diversity constraints.
- `CLM-S08-02`: Implementation of three meta-ensemble architectures: Soft Vote (E1), Borda Rank (E2), and Gated Controller (E3).
- `CLM-S08-03`: Meta-features for Gated Controller derived strictly from validation environments without ground-truth leaks.
- `CLM-S08-04`: Exact winner set: {C12, C09, C02, C03, C06} spanning 5 distinct paradigms.
- `CLM-S08-05`: Cryptographic freeze manifest committed prior to unlocking the test set.

## 3. Independent Audit Methodology & Tests

The verification suite in [test_audit_s08_ensembles.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s08_ensembles.py) evaluates five operational properties:
1. `test_t_s08_01_top5_diversity_selection`: Re-applies the pre-registered selection algorithm to validation logs and checks candidate IDs and family counts.
2. `test_t_s08_02_ensemble_combination_math`: Tests Soft Vote probability averaging and Borda Count rank accumulation on controlled test observations.
3. `test_t_s08_03_gated_controller_leakage_audit`: Evaluates the Gated Controller meta-feature extraction vector (dimension 21), verifying zero weakness labels or target IDs.
4. `test_t_s08_04_manifest_cryptographic_verification`: Computes SHA-256 digests from raw disk files in `results/checkpoints/frozen_top5/` and compares against `results/frozen_manifest.json`.
5. `test_t_s08_05_leave_one_out_ensemble_ablation`: Evaluates ensemble stability under leave-one-out model subsets.

## 4. Empirical Findings & Reproduction Results

The candidate selection audit verifies exact compliance with ranking and diversity criteria:

| Rank | Candidate ID | Name | Algorithmic Family | Validation AUDC | Family Quota Count (Max 2) | Selection Decision | Audit Diversity Verdict |
|---|---|---|---|---|---|---|---|
| **1** | **C12** | TreeRanker | Supervised / Heuristic | 0.0938 | 1 / 2 | Selected (Rank 1 overall) | **PASS (Compliant)** |
| **2** | **C09** | PPO-RND | Curiosity / Exploration | 0.0489 | 1 / 2 | Selected (Rank 2 overall) | **PASS (Compliant)** |
| **3** | **C02** | PPO-GNN | Structure-Aware | 0.0435 | 1 / 2 | Selected (Rank 3 overall) | **PASS (Compliant)** |
| **4** | **C03** | PPO-GRU | Recurrent Policy | 0.0390 | 1 / 2 | Selected (Rank 4 overall) | **PASS (Compliant)** |
| **5** | **C06** | REINFORCE | Policy Gradient | 0.0339 | 1 / 2 | Selected (Rank 5 overall) | **PASS (Compliant)** |

*Caption (Table A08-1):*
- **What the reader sees:** Final validation ranking, candidate ID, algorithmic family, validation AUDC, and family quota occupancy for the Top 5 selected agents.
- **What it implies:** All five selected models belong to distinct algorithmic paradigms (zero duplicate families), fully satisfying the diversity constraint ($\le 2$ per family).
- **Traceability link:** Original manifest [frozen_manifest.json](file:///c:/Users/Felix/Desktop/chaos%20final/results/frozen_manifest.json), validation summary [stage8_top5_manifest.csv](file:///c:/Users/Felix/Desktop/chaos%20final/docs/tables/stage8_top5_manifest.csv), and test [test_audit_s08_ensembles.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s08_ensembles.py#L25-L50).

Cryptographic hash recomputation confirmed 100% bitwise integrity against the pre-test manifest:

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

## 5. Negative Controls & Stress Testing

Negative controls proved test sensitivity:
- **Disqualified Candidate Control:** Attempting to force candidate C01 (which placed 7th) into the winner set failed the membership assertion.
- **Empty Mask Control:** Verifying that ensembles cannot select actions when all mask flags are 0 passed.
- **Meta-Feature Shape Control:** Asserting that Gated Controller meta-features match the exact 21-dimensional concatenation (`16 + 5`) passed.
- **Hash Tampering Control:** Inverting a single character in the SHA-256 manifest hash triggered immediate rejection.
- **Ablation Subset Control:** Confirming that ensembles operate without crashing when any single candidate is omitted passed.

## 6. Discrepancy & Anomaly Analysis

- **TreeRanker Dominance in Stage 8:** TreeRanker (C12) achieved the highest individual validation AUDC (0.0938), outperforming all pure neural RL candidates on validation topologies. This occurred because TreeRanker’s gradient-boosted trees explicitly leverage tabular structural metrics (in-degree, replica count, co-location) without experiencing the policy optimization variance inherent to RL training.
- **Action Masking in Soft Vote:** When averaging action probabilities across models, unmasked actions with near-zero probability might occasionally sum to zero if models disagree. The implementation correctly adds a fallback uniform distribution over valid actions to guarantee robust execution.

## 7. Impact on Downstream Stages & System Safety

The cryptographic freeze locked in Stage 8 guarantees that the final evaluation in Stage 9 represents a strictly held-out test evaluation, eliminating risks of p-hacking, retrospective weight tuning, or winner post-selection.

## 8. Audit Recommendations & Proposed Action Items

1. **Gating Router Diversity:** Include topological graph diameter and clustering coefficients in the Gated Controller meta-features to further assist cross-topology routing.
2. **Dynamic Temperature Scaling:** Incorporate softmax temperature scaling in Soft Vote to sharpen consensus among agreeing models.
