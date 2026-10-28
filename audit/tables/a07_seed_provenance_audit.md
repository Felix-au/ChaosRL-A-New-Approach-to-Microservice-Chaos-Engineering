# Table A07-2: Experimental Seed Provenance & Split Isolation Audit

| Experimental Stage | Allocated Seed Range | Observed Seed Count | Evaluated Seeds in Run | Overlap with Training | Overlap with Validation | Overlap with Test | Partition Status |
|---|---|---|---|---|---|---|---|
| **Training (Stage 7)** | `[0, 99,999]` | 3 seeds / candidate (36 total) | `{10, 20, 30}` | Self | $\emptyset$ (0) | $\emptyset$ (0) | **ISOLATED** |
| **Validation (Stage 5, 8)** | `[100,000, 100,099]` | 20 seeds ($N=100$) | `100,000..100,019` | $\emptyset$ (0) | Self | $\emptyset$ (0) | **ISOLATED** |
| **Test Set (Stage 9)** | `[200,000, 200,199]` | 38 locked test systems | `200,000..200,119` | $\emptyset$ (0) | $\emptyset$ (0) | Self | **LOCKED & ISOLATED** |

*Caption (Table A07-2):*
- **What the reader sees:** Seed boundaries, counts, and pairwise set intersections across training, validation, and test splits.
- **What it implies:** Seed disjointness is absolute ($\text{Train} \cap \text{Val} \cap \text{Test} = \emptyset$), preventing data leakage or memorization of validation/test topologies.
- **Traceability link:** Pre-registered plan [preregistered_plan.md](file:///c:/Users/Felix/Desktop/chaos%20final/audit/preregistered_plan.md#L20-L40), metrics logs [results/training/](file:///c:/Users/Felix/Desktop/chaos%20final/results/training/), and test [test_audit_s07_training.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s07_training.py#L75-L100).
