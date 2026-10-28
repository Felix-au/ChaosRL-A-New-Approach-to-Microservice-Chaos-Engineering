# Repository & Environment Inventory (Audit Baseline)

- **Audit Start Timestamp:** 2026-10-29T01:19:40+05:30
- **Git Commit (Preserved Baseline):** `4ade4e9a10276817b483dc45ed42f51033e8c8c0` (branch: `master`)
- **Git Working Tree Status:** Clean prior to audit directory initialization
- **Python Version:** `3.14.7` (`C:\Users\Felix\AppData\Local\Programs\Python\Python314\python.exe`)
- **Platform / OS:** `win32` (`nt`, Windows 11)
- **Logical CPU Cores:** 12 (AMD Ryzen 5 5500U, 6 cores / 12 threads)
- **Total RAM:** 13.85 GB (Available: 4.70 GB)

## Configuration Hashes (`configs/*.yaml`)
- `configs/budget.yaml`: `1d27a1140845f3e9`
- `configs/faults.yaml`: `c87c5d3252e7d842`
- `configs/rewards.yaml`: `3a80ef90b28a04f9`
- `configs/scales.yaml`: `e5cf04a6d03f72d4`
- `configs/seeds.yaml`: `1a95ae90361e2912`
- `configs/simulator.yaml`: `2168792cd092b1d0`
- `configs/training.yaml`: `4d151299e0a6ae72`

## Source Code & Deliverables Inventory

| Subsystem / Directory | File Count | Total Lines of Code / Prose | Description |
|---|---|---|---|
| `src/chaosrl/` | 44 | 6,661 | Core simulator, environments, baselines, candidates, training, eval |
| `tests/` | 8 | 614 | Unit, property, and integration test suite |
| `docs/` | 53 | 3,365 | Research monograph, 11 section docs, self-evals, QA, explainer |
| `configs/` | 7 | N/A | Scales, faults, and training hyperparameters |
| `docs/tables/` | 21 | N/A | Generated empirical tables (CSV and Markdown pairs) |
| `docs/figures/` | 21 | N/A | Generated 200 DPI PNG plots and vector SVGs |
| `results/checkpoints/` | 41 | N/A | Model checkpoints across seeds and frozen top 5 |
| `results/original_run/` | 226 | N/A | Read-only baseline copy with SHA-256 hash manifest |

## Key Preserved Baseline Facts
- `results/frozen_manifest.json` SHA-256 prefix: `681bc34f1e69a728`
- `results/facts.json` SHA-256 prefix: `c52c5fa7ae3fbb09`
- `results/scale100_raw_results.pkl` SHA-256 prefix: `36569114eb6c73df`
