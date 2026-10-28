# Self-evaluation: Stage 05 Non-Learned Baselines

- Date/time: 2026-10-28T18:31:00+05:30
- Git commit hash: `0cd0576a3a8628d9c4f0301bfd9a62f816a1132a`
- Config hash: `f8a42e9d` (configs/seeds.yaml, configs/simulator.yaml)

## Exit Criteria

| Criterion | Result | Evidence |
| :--- | :--- | :--- |
| Baseline suite implemented (7 baselines) | PASS | `src/chaosrl/agents/baselines/baselines.py` (ChaosMonkey, ChaosMonkey2, RandomAll, RoundRobin, UCBBandit, HeuristicExpert, Oracle) |
| Baselines evaluated on validation systems | PASS | Evaluated on 10 validation systems (seeds 100,000..100,009), scale 100, budget 100 |
| Validation results table saved | PASS | `docs/tables/stage5_baseline_validation_results.md` |
| Weakness breakdown table saved | PASS | `docs/tables/stage5_weakness_breakdown_by_baseline.md` |
| Weakness discovery curves plotted | PASS | `docs/figures/stage5_baseline_discovery_curves.png` |
| Damage vs. discovery trade-off plotted | PASS | `docs/figures/stage5_baseline_damage_vs_discovery.png` |
| Baseline facts registered | PASS | `baseline.oracle.audc`, `baseline.heuristic.audc`, etc. in `results/facts.json` |
| Section documentation complete | PASS | `docs/section05_baselines.md` (all 10 mandatory headings, >=600 words) |
| Unit tests pass | PASS | `pytest tests/test_baselines.py` (4/4 passed) |

## Independent Recomputation

| Quantity | Primary Value | Recomputed Value | Match? |
| :--- | :--- | :--- | :--- |
| `baseline.oracle.audc` | 0.24825 | 0.24825 (recomputed from `stage5_baseline_validation_results.csv`) | MATCH |
| `baseline.heuristic.audc` | 0.105375 | 0.105375 (recomputed from `stage5_baseline_validation_results.csv`) | MATCH |
| `baseline.chaos_monkey.audc` | 0.0395 | 0.0395 (recomputed from `stage5_baseline_validation_results.csv`) | MATCH |
| `baseline.heuristic.recall` | 0.175 | 0.175 (recomputed from `stage5_baseline_validation_results.csv`) | MATCH |

## Invariants Checked

1. **Oracle Dominance:** Oracle AUDC (0.24825) > Heuristic Expert AUDC (0.105375) > all other baselines. **PASS**
2. **Heuristic Incompleteness:** Heuristic Expert recall = 0.1750 < 1.0 (fortified decoys trick static rules). **PASS**
3. **Chaos Monkey Modality Restriction:** Faithful Chaos Monkey finds 0.6 simple weaknesses, 0.0 compound weaknesses, failing to detect network/resource faults. **PASS**
4. **Fair Comparison:** All baselines evaluated on identical validation architectures (seeds 100,000..100,009) with identical action masks and budget $B=100$. **PASS**
5. **Zero Hidden Leak in Non-Oracle Baselines:** Verified non-oracle baselines do not access `system.ground_truth_weaknesses`. **PASS**

## Adversarial Review

| Risk | How Tested | Outcome | Action Taken |
| :--- | :--- | :--- | :--- |
| Baseline action masks bypassed | Inspected `select_action` in each baseline | All agents filter valid actions through `obs["action_mask"]` | Added assertion tests in `test_baselines.py` |
| Heuristic Expert cheating on decoys | Tested on systems with planted fortified decoys | Heuristic recall capped at 17.5%, decoy resilience verified | Documented decoy resistance in Section 05 |
| Oracle agent fails to breach SLO | Checked Oracle action intensity in catalog | Oracle initially chose low intensity; fixed to HIGH intensity | High intensity ensures decisive SLO trigger |
| Multi-Armed Bandit fails on cold start | Inspected arm selection counts over $B=100$ | 1500 arms cannot be explored in 100 steps | Confirmed flat bandits require structural inductive biases |
| Random-All causes uncontrolled collateral | Measured cumulative damage across steps | Random-All averaged 169,221.9 damage vs 42.9 for Oracle | Highlighted catastrophic collateral risk in discussion |

## Figures Inspected

- `docs/figures/stage5_baseline_discovery_curves.png`: Labels, units, legends, and 0.5-sigma confidence bands verified. Distinguishable color palette used.
- `docs/figures/stage5_baseline_damage_vs_discovery.png`: Scatter plot clearly positions methods in discovery vs. damage space; Oracle in top-left frontier, Round-Robin in bottom-right catastrophic region.

## Issues Found and Fixed

- **Issue 1:** Backwards caller latency/error propagation was missing in `dynamics.py`, preventing downstream service latency from affecting gateway p99. Fixed by implementing backward critical path propagation (`max_callee_lat * 0.85`).
- **Issue 2:** `int(np.round(1 * scale))` rounded to 0 for low scale values; fixed to `max(1, int(np.ceil(1.0 * scale)))`.
- **Issue 3:** Oracle agent selected lowest intensity index by default; updated to select `FaultIntensity.HIGH`.

## Issues Remaining (Accepted Limitations)

- Baselines in this stage were evaluated on scale $N=100$ validation systems; full cross-scale sweep ($N=20, 100, 300, 500$) and Family M generalization are reserved for locked Stage 9 final evaluation.

## Verdict

**PASS** (All exit criteria pass, all invariants hold, recomputations match, adversarial review resolved).
- Iteration number: 1
