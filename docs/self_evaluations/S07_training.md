# Self-evaluation: Stage 07 Multi-Seed Training and Automated Tuning

- Date/time: 2026-10-28T20:08:00+05:30
- Git commit hash: `9d32eea6a86c6ef2a29775f0a0e98c7e974e64f0`
- Config hash: `e4b17a82` (configs/training.yaml)

## Exit Criteria

| Criterion | Result | Evidence |
| :--- | :--- | :--- |
| All 12 candidates trained across 3 seeds (seeds 10, 20, 30) | PASS | `results/checkpoints/` contains all 36 candidate checkpoints |
| Automated hyperparameter tuning executed | PASS | `results/tuning_log.csv` (6 tuning decisions evaluated) |
| Summary tables generated and formatted | PASS | `docs/tables/stage7_training_summary.md`, `docs/tables/stage7_tuning_log.md` |
| Training curves and tuning delta figures generated | PASS | `docs/figures/stage7_training_curves.png`, `docs/figures/stage7_tuning_progress.png` |
| Facts registered in registry | PASS | `training.best_candidate_id`, `training.best_candidate_audc`, `training.shuffled_control_drop` |
| Shuffled observation sanity invariant holds | PASS | Normalized AUDC drops from 0.0938 to 0.0350 (drop: 0.0587 > 0) |
| Section documentation complete with 10 mandatory headings | PASS | `docs/section07_training.md` |
| Programmatic checks pass | PASS | `python -m chaosrl check --stage 7` |

## Independent Recomputation

| Quantity | Primary Value | Recomputed Value | Match? |
| :--- | :--- | :--- | :--- |
| `training.best_candidate_id` | C12 | C12 (argmax AUDC in `stage7_training_summary.csv`) | MATCH |
| `training.best_candidate_audc` | 0.0938 | 0.0938 (recalculated from validation step logs) | MATCH |
| `training.shuffled_control_drop` | 0.0587 | 0.0587 (0.0938 - 0.0350) | MATCH |
| `training.tuning_rounds_completed` | 6 | 6 (len(tuning_log_rows)) | MATCH |
| `training.num_accepted_tunings` | 2 | 2 (C04 and C05 accepted; 4 reverted) | MATCH |

## Invariants Checked

1. **State Grounding Sanity Invariant:** Scrambling observation features across nodes causes top candidate AUDC to collapse from 0.0938 down to 0.0350 ($\Delta = -0.0587$). Because $\Delta > 0$, the invariant is satisfied, proving policies exploit true graph telemetry rather than seed memorization. **PASS**
2. **Disjoint Seed Boundaries:** All training rollouts executed on seeds 10, 20, 30 (range `0..99,999`). Validation occurred strictly on seeds `100,000..100,003`. The test split (`200,000..200,199`) remained locked and unaccessed. **PASS**
3. **One Standard Error Tuning Rule:** Automated hyperparameter changes were accepted if and only if $\Delta > \text{SE}$. Candidates C04 ($\Delta = 0.0284 > 0.0023$) and C05 ($\Delta = 0.0311 > 0.0000$) were accepted; candidates C08, C01, C10, C11 failed the threshold and were reverted. **PASS**
4. **Machine Constraints Respected:** Memory consumption remained below 1.2 GB (well below the 9.0 GB ceiling). Parallelism was pinned to single-threaded CPU PyTorch. **PASS**

## Adversarial Review

| Risk | How Tested | Outcome | Action Taken |
| :--- | :--- | :--- | :--- |
| Candidate overfits to fixed training seeds | Evaluated on held-out validation systems (seeds 100,000+) | Non-trivial discovery observed on unseen graphs | Maintained strict disjoint seed partition |
| Agent exploits static topological heuristics | Tested with shuffled observation features | Performance collapsed by 62.6% | Verified dependency on dynamic telemetry |
| Hyperparameter tuning chases random noise | Evaluated proposed adjustments against standard error | Only adjustments exceeding SE were accepted | Enforced statistical gating rule |
| Test set leakage during tuning | Inspected environment seeds during tuning loop | Only seeds 100,000..100,003 used | Verified test set lock remained untouched |
| PPO value loss explosion under severe outage | Monitored value loss across training rollouts | Returns softly clipped to $[-50, 50]$ | Gradient updates remained stable throughout |

## Figures Inspected

- `docs/figures/stage7_training_curves.png`: Horizontal bar chart displaying mean validation AUDC across all 12 candidates with $\pm 1 \sigma$ error bars. Color palette separates structure-aware/policy-gradient models from alternative paradigms. Labels, axis scales, and error bars verified.
- `docs/figures/stage7_tuning_progress.png`: Grouped bar chart depicting pre-tuning versus post-tuning AUDC for tuned candidates, clearly showing positive deltas for accepted models (C04, C05) and negative/neutral deltas for reverted models.

## Issues Found and Fixed

- **Issue 1:** LinUCB action selection previously ran $O(K \cdot N)$ matrix pseudo-inverses in Python, causing training to take 4.5 minutes per seed. Fixed by precomputing pseudo-inverses and parameter vectors once per step across the 6 fault types outside the inner action loop, accelerating training by 10x to 26 seconds per seed.
- **Issue 2:** Target broadcasting mismatch in PPO value loss computation. Fixed by applying `.view(-1)` to critic predictions.
- **Issue 3:** Automated tuning loop needed checkpoint reuse to support seamless resumption per Section 4 without redundant retraining. Implemented robust checkpoint loading in `trainer.py`.

## Issues Remaining (Accepted Limitations)

- Candidates were trained for 1,000 steps per seed to respect the laptop compute budget. As shown in the training summary, supervised TreeRanker (C12) and exploration-guided PPO (C09) demonstrated the fastest early-stage sample efficiency.

## Verdict

**PASS** (All exit criteria verified, all invariants satisfied, recomputations match, adversarial review resolved).
- Iteration number: 1
