# Self-evaluation: Stage 08 Model Selection, Freeze, and Ensembles

- Date/time: 2026-10-28T20:15:00+05:30
- Git commit hash: `3e83be3`
- Config hash: `e4b17a82` (configs/training.yaml)

## Exit Criteria

| Criterion | Result | Evidence |
| :--- | :--- | :--- |
| Top 5 selected under diversity constraint ($\le 2$ per family) | PASS | `results/frozen_manifest.json` (5 models across 5 distinct families) |
| Cryptographic freeze manifest exists with valid SHA-256 hashes | PASS | `results/frozen_manifest.json` |
| Manifest and ensemble tables generated and formatted | PASS | `docs/tables/stage8_top5_frozen_manifest.md`, `docs/tables/stage8_ensemble_validation_results.md` |
| Diversity selection and ensemble comparison figures saved | PASS | `docs/figures/stage8_top5_diversity_selection.png`, `docs/figures/stage8_ensemble_vs_single_discovery.png` |
| Facts registered in registry | PASS | `ensemble.top1_single_audc`, `ensemble.best_ensemble_name`, `ensemble.best_ensemble_audc`, `ensemble.audc_gain` |
| Ensemble superiority holds on validation systems | PASS | E3: Gated Controller (AUDC: 0.0980) beats Top-1 Single (AUDC: 0.0750) with +0.0230 gain |
| Section documentation complete with 10 mandatory headings | PASS | `docs/section08_selection_ensembles.md` |
| Unit tests pass | PASS | `pytest tests/test_ensembles.py` (4/4 passed) |
| Programmatic checks pass | PASS | `python -m chaosrl check --stage 8` |

## Independent Recomputation

| Quantity | Primary Value | Recomputed Value | Match? |
| :--- | :--- | :--- | :--- |
| `ensemble.top1_single_audc` | 0.0750 | 0.0750 (recomputed from `stage8_ensemble_validation_results.csv`) | MATCH |
| `ensemble.best_ensemble_audc` | 0.0980 | 0.0980 (recomputed from `stage8_ensemble_validation_results.csv`) | MATCH |
| `ensemble.audc_gain` | 0.0230 | 0.0230 (0.0980 - 0.0750) | MATCH |
| `frozen_manifest.model_count` | 5 | 5 (len(json.load(open('results/frozen_manifest.json')))) | MATCH |
| Rank 1 SHA-256 Checksum | `ea63ee26a99f9fda...` | `ea63ee26a99f9fda...` (hashlib.sha256 on frozen checkpoint) | MATCH |

## Invariants Checked

1. **Family Diversity Invariant:** The selected Top 5 models represent 5 completely distinct algorithm families: `supervised` (C12), `exploration` (C09), `structure_aware` (C02), `recurrent` (C03), and `policy_gradient` (C06). The maximum count per family is 1, strictly obeying the $\le 2$ rule. **PASS**
2. **Action Mask Compliance Across All Ensembles:** In unit tests and validation rollouts, 100% of actions produced by Soft Vote, Borda Rank, and Gated Controller ensembles obeyed `action_mask == 1`, with zero illegal actions. **PASS**
3. **Ensemble Gain Invariant:** Meta-ensemble discovery efficiency exceeds that of the best single agent: E3 achieved 0.0980 vs. 0.0750 (+30.7% relative gain). **PASS**
4. **Cryptographic Immutability:** All 5 checkpoints copied to `results/checkpoints/frozen_top5/` have verified SHA-256 hashes recorded in `results/frozen_manifest.json`. **PASS**

## Adversarial Review

| Risk | How Tested | Outcome | Action Taken |
| :--- | :--- | :--- | :--- |
| Model weights modified after observing validation | Checked file write times and SHA-256 checksums | Checksums locked in manifest before Stage 9 | Verified checksums match prior to test access |
| Action mask violation in ensemble combination | Evaluated ensembles in edge-case environments with restricted masks | Zero illegal actions chosen | Masking enforced before softmax and rank scoring |
| Uncalibrated logits distorting soft vote | Tested with heterogeneous model types (RF, GNN, PPO) | Borda rank and Gated Controller provide non-parametric alternatives | Provided multiple complementary ensemble paradigms |
| Gated controller overfitting to training graph scale | Tested gated routing across graphs of $N=20$ and $N=100$ | Features normalized by graph scale | Validated scale-invariant feature extraction |
| Family diversity bypass via alias | Audited candidate registry mappings | Each candidate has immutable family tag | Verified uniqueness in unit tests |

## Figures Inspected

- `docs/figures/stage8_top5_diversity_selection.png`: Bar chart of Top 5 selected models colored by distinct algorithm families; confirms representation across supervised, exploration, GNN, recurrent, and policy-gradient paradigms.
- `docs/figures/stage8_ensemble_vs_single_discovery.png`: Grouped comparison showing normalized AUDC across Top-1 single model and all three meta-ensembles, highlighting the superior performance of the Gated Controller.

## Issues Found and Fixed

- **Issue 1:** Palette lookup error `KeyError: 'purple'` in figure generation. Fixed by using `CB_PALETTE["reddish_purple"]` per Okabe-Ito specification.
- **Issue 2:** Matplotlib `FixedFormatter` warning on tick labels. Fixed by setting explicit tick positions with `ax.set_xticks(range(len(...)))`.

## Issues Remaining (Accepted Limitations)

- Ensembles were evaluated on validation systems. The definitive comparative evaluation across all scales ($N=20$ to $N=500$), topology families, and statistical significance tests will occur strictly on the locked test set in Stage 9.

## Verdict

**PASS** (All exit criteria verified, all invariants satisfied, recomputations match, adversarial review resolved).
- Iteration number: 1
