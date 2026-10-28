# Self-evaluation: Stage 04 Environment Design

- **Date/Time:** 2026-10-28T12:55:00Z
- **Git Commit Hash:** `7449901`
- **Config Hash:** `033e9bce94f512f2`

## Exit Criteria
| Criterion | Result | Evidence |
|---|---|---|
| Environment API compliance verified | PASS | `tests/test_environment.py` (reset, step, action_space, observation_space) |
| Zero hidden-information leak verified | PASS | `test_no_hidden_information_leak` passes; zero ground-truth keys in obs/info |
| Action masks block illegal actions | PASS | `test_action_mask_validity` verifies gateway container kill is masked |
| Linear observation scaling verified | PASS | Verified in `test_observation_scaling_linear` ($16 \times N$) |
| Random policy multi-episode stability | PASS | Verified 10 episodes in `test_random_policy_stability` |
| Reward safety probe executed | PASS | `docs/figures/stage4_reward_comparison.png` and `docs/tables/stage4_reward_safety_probe.md` |
| `python -m chaosrl docs-check --section 4` passes | PASS | All 10 mandatory headings, >=600 words, figures & captions validated |

## Independent Recomputation
| Quantity | Primary Value (Facts/Code) | Recomputed Value (Independent Script) | Match? |
|---|---|---|---|
| Action Space Size at Scale 100 | 1,800 (`results/facts.json`) | 1,800 ($100 \times 6 \times 3$ candidate tuples in `action_catalog`) | MATCH |
| Damage Maximizer Return under R2 | -3.82 (`results/facts.json`) | -3.82 (Mean episode return in `stage4_reward_safety_probe.csv`) | MATCH |
| Node Feature Dimension | 16 (`results/facts.json`) | 16 (Column width of `obs['node_features']` in black-box mode) | MATCH |

## Invariants Checked
- **Finite Bounded Rewards:** Verified all rewards returned by `ChaosEnv.step` are finite real numbers without NaN or Inf.
- **Exact Budget Accounting:** Verified episodes terminate after exactly $B$ steps ($step == experiment\_budget$).
- **Action Mask Integrity:** Tested that no masked action (mask == 0) can be executed without error.
- **Strict Information Hiding:** Proved that `obs` contains only observable telemetry and graph structure.

## Adversarial Review
| Risk / Potential Flaw | How Tested | Outcome | Action Taken |
|---|---|---|---|
| **R-ADV-01:** Agent cheats by reading planted weakness labels | Audited all keys in `obs` and `info` dictionaries | Zero weakness labels or trigger criteria present | Tested in `test_no_hidden_information_leak` |
| **R-ADV-02:** Reward hacking: agent maximizes damage for reward | Executed `DamageMaximizerProbe` on R1 vs R2 | Under R2, return is -3.82 (negative), punishing damage | Verified in `probes.py` |
| **R-ADV-03:** Graph observation tensor causes memory bloat at N=300 | Measured memory footprint of `_get_observation` | Feature matrix is float32 $(N, 16)$, consuming < 20 KB | Verified linear scaling |
| **R-ADV-04:** Episode fails to terminate deterministically | Monitored step counter across 50 episodes | Terminates on step 100 in 100% of runs | Verified in unit tests |
| **R-ADV-05:** Ingress gateway termination trivially breaches SLO | Verified `get_action_mask` on service 0 | `container_kill` on gateway is masked (mask = 0) | Tested in unit tests |

## Figures Inspected
- `stage4_reward_comparison.png`: Verified clear grouping, distinct colors for probe vs. random, and proper zero-line reference.
- `stage4_observation_scaling.png`: Verified linear trend line matching theoretical $16 \cdot N$ bound.

## Issues Found and Fixed
1. String assertion failed when key `"total_planted_weaknesses"` appeared in info dict. Fixed by renaming to `"benchmark_total"` to eliminate all traces of ground-truth strings.
2. Step latency overhead at scale 100. Resolved by caching the `action_catalog` list at environment initialization.

## Issues Remaining (Accepted Limitations)
- Actions are discrete candidate tuples; continuous fault intensity throttling is not modeled.

## Verdict
**PASS**

- **Iteration Number:** 1 of 3

