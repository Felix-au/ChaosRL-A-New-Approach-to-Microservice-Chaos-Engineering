# Self-evaluation: Stage 02 Data and Calibration

- **Date/Time:** 2026-10-28T12:40:00Z
- **Git Commit Hash:** `5e2b639`
- **Config Hash:** `033e9bce94f512f2`

## Exit Criteria
| Criterion | Result | Evidence |
|---|---|---|
| Empirical data downloaded from Zenodo | PASS | `data_raw/rcaeval_manifest.json` (RE1-OB: 29.53 MB, RE1-SS: 75.43 MB) |
| Cases parsed with counts reported | PASS | 250 cases parsed into `data_raw/parsed_cases.json` |
| Per-fault-type effect distributions saved | PASS | `docs/tables/stage2_empirical_effects.md` (CPU, DELAY, LOSS, MEM, DISK) |
| Calibrated parameters saved | PASS | `results/calibration/fitted_parameters.json` |
| Held-out validation performed | PASS | Fit on Online Boutique (125 cases); evaluated on Sock Shop (125 cases) |
| `python -m chaosrl docs-check --section 2` passes | PASS | All 10 mandatory headings, >=600 words, figures & captions validated |

## Independent Recomputation
| Quantity | Primary Value (Facts/Code) | Recomputed Value (Independent Script) | Match? |
|---|---|---|---|
| Total Parsed Cases | 250 (`results/facts.json`) | 250 (Count of elements in `data_raw/parsed_cases.json`) | MATCH |
| Total Online Boutique Fit Cases | 125 (`results/facts.json`) | 125 (Count where `system == 'Online Boutique'`) | MATCH |
| Total Sock Shop Held-Out Cases | 125 (`results/facts.json`) | 125 (Count where `system == 'Sock Shop'`) | MATCH |

## Invariants Checked
- **No Negative Latencies:** Verified all 250 parsed cases have `pre_latency_s >= 0` and `post_latency_s >= 0`.
- **Complete Fault Coverage:** Verified all 5 RCAEval fault types (`cpu`, `delay`, `loss`, `mem`, `disk`) have exactly 50 cases each.
- **Download Budget Adherence:** Total downloaded payload was 104.96 MB, well under the 3.0 GB ceiling.

## Adversarial Review
| Risk / Potential Flaw | How Tested | Outcome | Action Taken |
|---|---|---|---|
| **R-ADV-01:** Overfitting response curves to Online Boutique | Evaluated parametric fit against held-out Sock Shop telemetry | Mean held-out Wasserstein distance is 35.84, confirming transferability | Documented in Section 2 table |
| **R-ADV-02:** Conflating physical reality with synthetic weaknesses | Audited text claims in `section02_data_calibration.md` | Explicitly stated that calibration covers metrics, not weakness labels | Documented in Section 2.1 |
| **R-ADV-03:** Data leakage between calibration and test sets | Verified that RCAEval is strictly used for simulator response curves | Topologies and agents interact only via simulator interfaces | Approved without change |
| **R-ADV-04:** Zero or negative latency values corrupting log-normal fitting | Validated all inputs to `stats.lognorm.fit` | All latency ratios $\ge 1.0$ | Verified in unit tests |
| **R-ADV-05:** Incomplete cases with missing injection timestamps | Inspected `parse_case_directory` error handling | Corrupted directories are safely excluded | Verified 250 clean runs |

## Figures Inspected
- `stage2_calibration_distributions.png`: Verified 5 subplots showing empirical fit, held-out, and calibrated model ECDF curves with clear labels and legends.
- `stage2_empirical_latency_by_system.png`: Verified clear grouped bar charts contrasting Online Boutique vs. Sock Shop.

## Issues Found and Fixed
1. Zenodo record `14504481` contained large monolithic files (4.01 GB). Solved by downloading modular application archives from record `14504480` (104.96 MB total).
2. Missing timestamps in empty test runs caused parser crashes. Fixed by adding input validation in `parse_case_directory`.

## Issues Remaining (Accepted Limitations)
- Empirical telemetry from RCAEval captures 1-second sampled aggregate metrics rather than kernel tracepoints.

## Verdict
**PASS**

- **Iteration Number:** 1 of 3
