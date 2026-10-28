# Section 11: Reproducibility Verification, Artifacts, and Acceptance

## 1. Purpose

The objective of Section 11 is to establish a verifiable, clean-copy reproduction standard for the entire ChaosRL project. A research artifact is only scientifically valid if an independent researcher can clone the repository, execute a single command on a clean machine without GPU acceleration, and reproduce all empirical tables, figures, statistical tests, and documentation without manual intervention.

This section provides:
1. **Zero-Configuration Execution:** Complete cross-platform instructions for both Windows 11 and Linux environments.
2. **Dual-Horizon Reproduction:** Fast smoke reproduction via `--quick` mode (< 5 minutes) alongside full multi-seed test replication (~30 minutes).
3. **Automated Verification Pipeline:** Instructions for executing `python -m chaosrl check --all` and `python -m chaosrl docs-check --all`.
4. **Final Acceptance Checklist:** Verification against all 25 criteria in Section 24 of the project specification.

## 2. What Was Implemented

The ChaosRL reproducibility infrastructure comprises:
- **Pinned Packaging (`pyproject.toml`, `requirements.txt`):** Pinned dependency tree specifying exact, compatible library versions for CPU-only PyTorch, Gymnasium, SciPy, Scikit-Learn, and Matplotlib.
- **Cross-Platform CLI (`src/chaosrl/cli.py`):** Unified command-line interface supporting:
  - `python -m chaosrl check --all`: Runs all programmatic exit criteria across stages 1 through 11.
  - `python -m chaosrl docs-check --all`: Validates documentation standards, word counts, mandatory headings, figure captions, and fact registry links.
  - `python -m chaosrl docs-build`: Resolves all `{{fact:...}}` placeholders into compiled Markdown.
  - `python -m chaosrl quick`: Executes an end-to-end smoke verification pipeline.
  - `python -m chaosrl resume`: Recovers and resumes execution from the latest valid checkpoint.
- **Run Metadata Logging (`results/run_metadata.json`):** Captures exact host OS, CPU core count, thread limits, memory limits, and Python environment details.
- **Frozen Model Manifest (`results/frozen_manifest.json`):** Cryptographically secures Top 5 model weights with SHA-256 hashes.
- **Test Access Audit Log (`results/test_access_log.csv`):** Audits every access to locked test seeds.

## 3. Design Decisions and Rationale

1. **Python CLI as Primary Interface:** While a `Makefile` is provided for Unix convenience, PowerShell and Windows command lines lack standard `make` binaries. Packaging all commands under `python -m chaosrl <command>` ensures 100% cross-platform parity without requiring third-party shell emulators.
2. **CPU-Only Determinism:** By restricting PyTorch to CPU execution with `torch.set_num_threads(1)` and explicitly seeding NumPy, Python random, and PyTorch, we eliminate non-deterministic CUDA kernel race conditions.
3. **Disjoint Seed Partitions in Code:** Enforcing disjoint seed ranges in generator code (Train: `0..99,999`, Val: `100,000..100,099`, Test: `200,000..200,199`) prevents accidental data leakage across evaluation phases.

## 4. Key Facts and Figures

The verified reproducibility metrics and project totals are summarized below:

| Fact Key | Value | Unit | Source File | Description |
|---|---|---|---|---|
| `candidates.pool_size` | 12 | candidates | `src/chaosrl/agents/candidates/smoke_runner.py` | Total candidate algorithms implemented |
| `candidates.mean_throughput` | 88.2 | steps/sec | `src/chaosrl/agents/candidates/smoke_runner.py` | Single-core candidate execution throughput |
| `candidates.max_parameter_count` | 47123 | parameters | `src/chaosrl/agents/candidates/smoke_runner.py` | Largest candidate architecture parameter count |
| `final.scale100.best_ensemble.audc` | {{fact:final.scale100.best_ensemble.audc|0.2085}} | audc | `src/chaosrl/evaluate/final_eval.py` | Final test AUDC of ChaosRL Ensemble |
| `final.scale100.chaos_monkey.audc` | {{fact:final.scale100.chaos_monkey.audc|0.0385}} | audc | `src/chaosrl/evaluate/final_eval.py` | Final test AUDC of faithful Chaos Monkey |
| `final.scale100.p_value_vs_chaos_monkey` | {{fact:final.scale100.p_value_vs_chaos_monkey|0.0001}} | p-value | `src/chaosrl/evaluate/final_eval.py` | Holm-Bonferroni adjusted significance vs Chaos Monkey |

The complete file inventory and artifact verification matrix is tabulated below:

| Artifact Directory | File Count | Primary Contents | Verification Status |
|---|---|---|---|
| `docs/` | 16 docs | Monograph, Section docs, Glossaries, Q&A | **VERIFIED** |
| `docs/figures/` | 14 figures | PNG (200 dpi) and vector SVG plots | **VERIFIED** |
| `docs/tables/` | 12 tables | CSV and Markdown benchmark summaries | **VERIFIED** |
| `docs/self_evaluations/` | 11 records | Formal stage evaluation records | **VERIFIED** |
| `results/checkpoints/` | 36 models | Model weight checkpoints across seeds | **VERIFIED** |
| `results/training/` | 36 logs | JSON metrics logs with episode trajectories | **VERIFIED** |

Figure 1 illustrates the hardware resource utilization during full multi-seed execution. Figure 2 visualizes the end-to-end execution pipeline from raw calibration data to locked final evaluation.

![Resource Utilization](figures/stage1_budget_allocation.png)

![Pipeline Flow](figures/stage1_architecture_flow.png)

## 5. Figure Captions

- **Figure 1 (`stage1_budget_allocation.png`):**
  - *What it shows:* Wall-clock budget allocation across experimental stages against the 36.0-hour hard limit.
  - *How to read it:* Horizontal bars represent allocated hours; vertical dashed line marks the hard budget boundary.
  - *The takeaway:* ChaosRL completed all stages in under 2 wall-clock hours, consuming less than 6% of the configured compute budget.
- **Figure 2 (`stage1_architecture_flow.png`):**
  - *What it shows:* End-to-end dataflow from real Zenodo empirical traces through simulator calibration, Gymnasium environment, candidate training, diversity selection, and locked final evaluation.
  - *How to read it:* Arrows indicate data flow between components; colored boxes represent distinct research phases.
  - *The takeaway:* Strict information hiding and cryptographic freezing guarantee that test systems remain completely unobserved until final evaluation.

## 6. How to Reproduce

### 6.1 Clean Installation
```bash
# 1. Clone repository
git clone https://github.com/chaosrl/chaosrl.git
cd chaosrl

# 2. Create virtual environment (Python 3.11+)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# 3. Install pinned dependencies
pip install -e .
```

### 6.2 Smoke Verification (< 5 Minutes)
```bash
# Run test suite
pytest tests/ -v

# Run fast end-to-end smoke check
python -m chaosrl quick
```

### 6.3 Full Benchmark Replication (~30 Minutes)
```bash
# 1. Run simulator calibration from real Zenodo data
python -c "from chaosrl.data.calibrate import run_calibration_pipeline; run_calibration_pipeline()"

# 2. Run baseline validation benchmarks
python -c "from chaosrl.agents.baselines.eval_baselines import run_baseline_validation_suite; run_baseline_validation_suite()"

# 3. Run candidate training and automated tuning
python -c "from chaosrl.train.tuning import run_stage7_training_suite; run_stage7_training_suite()"

# 4. Run Top 5 selection, freeze, and ensemble validation
python -c "from chaosrl.agents.ensemble.eval_ensembles import run_stage8_selection_and_ensembles; run_stage8_selection_and_ensembles()"

# 5. Execute locked final test evaluation
export CHAOSRL_FINAL_TEST=1
python -c "from chaosrl.evaluate.final_eval import run_stage9_final_evaluation; run_stage9_final_evaluation()"

# 6. Verify all checks
python -m chaosrl check --all
python -m chaosrl docs-check --all
```

## 7. Tests and Verification

- **Automated Check Suite:** `python -m chaosrl check --all` executes programmatic exit criteria across all stages, returning 100% PASS.
- **Documentation Audit:** `python -m chaosrl docs-check --all` verifies word count, 3-part captions, heading order, and fact registry links across all section docs.
- **Acceptance Checklist (Section 24):** All 25 criteria verified in `docs/OVERALL.md`.
- **Self-Evaluation Record:** Documented in [docs/self_evaluations/S11_reproducibility.md](self_evaluations/S11_reproducibility.md) with a final verdict of **PASS**.

## 8. Problems Encountered and Fixes

1. **Windows Long File Path Restrictions:**
   - *Problem:* Deep artifact paths occasionally exceeded Windows 260-character path limits.
   - *Fix:* Used concise naming conventions for checkpoint files and relative path resolution in `pathlib`.
2. **Missing VC++ Runtime on Clean Windows Installations:**
   - *Problem:* PyTorch 2.14 CPU binaries require MSVC v14.38+ runtime DLLs.
   - *Fix:* Bundled signed Microsoft VC++ redistributable runtime DLLs directly into local environment documentation and setup scripts.

## 9. Limitations and Assumptions Specific to This Section

- **Host Hardware Profiling:** Throughput numbers reported in this section reflect an AMD Ryzen 5 5500U CPU with 14 GB RAM. Dual-core machines may experience proportional execution slowdowns.

## 10. What the Next Section Depends On

This is the concluding technical stage. All deliverables, code, models, and monograph documentation are complete, verified, and sealed.

