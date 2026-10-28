# Section 07: Training and Automated Hyperparameter Tuning

## 1. Purpose

The objective of Section 07 is to train all twelve candidate agents across multiple random training seeds, execute an automated validation-guided hyperparameter tuning loop, and verify the integrity of learned representations through adversarial shuffled-observation controls. In microservice chaos engineering, learning to inject the minimal, highest-leverage fault combination without causing catastrophic customer outages requires robust multi-objective optimization under severe stochasticity.

This stage addresses three fundamental research imperatives:
1. **Multi-Seed Stability:** Machine learning policies in complex combinatorial environments can be sensitive to initialization seeds. Evaluating each candidate across three independent training seeds ($10, 20, 30$) ensures that reported performance reflects genuine algorithmic superiority rather than lucky seed initialization.
2. **Autonomous Tuning Without Human Gates (Section 5.5):** To maintain strict autonomy without user intervention, an automated tuning loop proposes, tests, and evaluates hyperparameter adjustments from a pre-registered playbook on validation systems only.
3. **Representation Grounding via Shuffled-Observation Invariant:** To prove that trained agents genuinely exploit dynamic service telemetry and structural graph topology (rather than memorizing static procedural seed artifacts), we conduct a shuffled-observation control test where node features are randomly permuted.

## 2. What Was Implemented

The Stage 7 training architecture comprises three core modules in `src/chaosrl/train/`:
- **Multi-Seed Trainer (`trainer.py`):**
  - Manages rollout trajectory collection, GAE computation, clipped return estimation, and agent-specific policy updates (PPO clipped surrogate, A2C actor-critic, DQN target sync, REINFORCE baseline subtraction, ES parameter perturbation, LinUCB ridge regression, and TreeRanker dataset fitting).
  - Checkpoints model weights to `results/checkpoints/<candidate>_seed<seed>.pt` (or `.pkl`).
  - Logs step-by-step metrics (policy loss, value loss, entropy, return, discovered weaknesses) to `results/training/<candidate>_seed<seed>_metrics.json`.
- **Validation Evaluator (`trainer.py`):**
  - Evaluates candidates strictly on validation systems (seeds 100,000 to 100,009, scale 100, budget $B=100$).
  - Supports adversarial observation feature scrambling to execute the sanity invariant check.
- **Automated Tuning Harness (`tuning.py`):**
  - Orchestrates multi-candidate training and ranks candidates by normalized Area Under the Discovery Curve (AUDC).
  - Proposes hyperparameter changes (learning rate, entropy regularization, network width) for candidates performing below their family median.
  - Applies a rigorous statistical acceptance rule: accepts a proposed tuning change only if validation AUDC improves by more than one standard error across seeds; otherwise reverts.
  - Logs all decisions, empirical deltas, and outcomes to `results/tuning_log.csv`.

## 3. Design Decisions and Rationale

The training procedure was governed by several essential methodological principles:
1. **Strict Data Separation:** All training rollouts occur exclusively on systems drawn from the training seed range (`0..99,999`). All tuning evaluations occur exclusively on the validation cohort (`100,000..100,009`). The test cohort (`200,000..200,199`) remains strictly locked behind `CHAOSRL_FINAL_TEST=1` and is never accessed during training or tuning.
2. **Trajectory Batch Accumulation with Return Clipping:** In microservice environments, severe outages can produce large negative rewards. To prevent gradient explosion in CPU PyTorch, GAE returns are softly clipped to $[-50, 50]$, and gradients are accumulated across the entire trajectory rollout before executing a single clipped optimizer step (`max_norm = 0.5`).
3. **One Standard Error Acceptance Rule:** To prevent chasing validation noise, an automated tuning proposal is accepted if and only if:
   $$\Delta \text{AUDC} > \text{SE} = \frac{\sigma_{\text{seed}}}{\sqrt{N_{\text{seeds}}}}$$
   This guarantees that only statistically meaningful hyperparameter improvements are adopted.
4. **Shuffled-Observation Sanity Check:** If an agent relies on real state features, permuting node features across rows destroys state-action correlations, causing discovery performance to collapse toward random search.

## 4. Key Facts and Figures

The verified empirical facts established during Stage 7 training and automated tuning are summarized below:

| Fact Key | Value | Unit | Source File | Description |
|---|---|---|---|---|
| `training.best_candidate_id` | {{fact:training.best_candidate_id|C02}} | candidate | `src/chaosrl/train/tuning.py` | Top-performing candidate identifier on validation cohort |
| `training.best_candidate_audc` | {{fact:training.best_candidate_audc|0.1850}} | audc | `src/chaosrl/train/tuning.py` | Validation AUDC of best candidate |
| `training.tuning_rounds_completed` | {{fact:training.tuning_rounds_completed|6}} | rounds | `src/chaosrl/train/tuning.py` | Total automated tuning proposals evaluated |
| `training.shuffled_obs_audc` | {{fact:training.shuffled_obs_audc|0.0410}} | audc | `src/chaosrl/train/tuning.py` | Validation AUDC under shuffled observation control |
| `training.shuffled_control_drop` | {{fact:training.shuffled_control_drop|0.1440}} | audc | `src/chaosrl/train/tuning.py` | Performance drop verifying state-grounded learning |

Figure 1 illustrates the comparative validation AUDC performance across all 12 candidates averaged over three random seeds. Figure 2 displays the pre-tuning versus post-tuning AUDC deltas across tuned models.

![Candidate Validation Ranking](figures/stage7_training_curves.png)

![Automated Tuning Delta](figures/stage7_tuning_progress.png)

The complete candidate training summary across all 12 candidates is tabulated below:

<!-- Table: stage7_training_summary -->

The detailed audit log of all automated tuning proposals is documented below:

<!-- Table: stage7_tuning_log -->

## 5. Figure Captions

- **Figure 1 (`stage7_training_curves.png`):**
  - *What it shows:* Mean validation normalized AUDC with standard deviation error bars across three random training seeds ($10, 20, 30$) for all 12 candidate architectures on $N=100$ systems.
  - *How to read it:* The horizontal axis measures normalized AUDC; the vertical axis lists candidate IDs and model names. Blue bars highlight structure-aware and policy-gradient models; vermilion bars indicate value-based and alternative paradigms.
  - *The takeaway:* Structure-aware GCN (C02) and curriculum-trained PPO (C07) achieve the highest validation discovery efficiency, significantly outperforming flat value-based and unguided exploration candidates.
- **Figure 2 (`stage7_tuning_progress.png`):**
  - *What it shows:* Comparative bar chart of validation AUDC before tuning (gray bars) and after tuning (teal bars) for candidates subjected to the automated tuning playbook.
  - *How to read it:* The horizontal axis lists tuned candidate IDs; the vertical axis measures validation AUDC. A taller teal bar indicates successful hyperparameter optimization.
  - *The takeaway:* Playbook adjustments (e.g. learning rate reductions and entropy regularization increases) successfully rescued underperforming candidates by expanding exploration and stabilizing value estimates.

## 6. How to Reproduce

To reproduce the multi-seed training suite, run automated tuning, and execute validation checks:
```bash
# 1. Run full Stage 7 multi-seed training and tuning suite
python -c "from chaosrl.train.tuning import run_stage7_training_suite; run_stage7_training_suite(train_seeds=[10, 20, 30], steps_per_run=1000)"

# 2. Execute Stage 7 programmatic exit criteria check
python -m chaosrl check --stage 7

# 3. Verify documentation integrity
python -m chaosrl docs-check --section 7
```

## 7. Tests and Verification

Stage 7 execution was validated through multiple programmatic assertions:
- **Shuffled-Observation Control Invariant:** Permuting observation features reduced top candidate AUDC from {{fact:training.best_candidate_audc|0.1850}} down to {{fact:training.shuffled_obs_audc|0.0410}} (a drop of {{fact:training.shuffled_control_drop|0.1440}}), confirming that the learned policy relies on real state telemetry rather than trivial random heuristics.
- **Automated Checkpoint Verification:** All 36 training runs produced valid model checkpoints and JSON metrics logs in `results/checkpoints/` and `results/training/`.
- **Programmatic Stage Check (`python -m chaosrl check --stage 7`):** Verified presence of summary tables, tuning logs, figures, and invariants.
- **Self-Evaluation Record:** Documented in [docs/self_evaluations/S07_training.md](self_evaluations/S07_training.md) with a final verdict of **PASS**.

## 8. Problems Encountered and Fixes

1. **Initial SGD Instability under Outage Penalties:**
   - *Problem:* Extreme collateral damage in early episodes caused negative returns of magnitude $-100,000$, causing SGD gradient updates to diverge.
   - *Fix:* Softly clipped GAE returns to $[-50, 50]$, divided rollout loss by trajectory length $T$, and applied global gradient clipping at `max_norm = 0.5`.
2. **Entropy Collapse in Flat Action Spaces:**
   - *Problem:* Certain policy-gradient models rapidly collapsed entropy during early epochs, prematurely committing to suboptimal service targets.
   - *Fix:* Configured the automated tuning playbook to boost entropy regularization coefficient from 0.01 to 0.03 for affected candidates, maintaining exploration breadth.

## 9. Limitations and Assumptions Specific to This Section

- **Fixed Training Step Budget:** Candidates were trained for 1,000 steps per seed. While longer horizons could further optimize convergence, 1,000 steps balances sample efficiency within our hard wall-clock budget.
- **Tuning Playbook Scope:** Automated tuning explored learning rate and entropy regularization; full neural architecture search was excluded to adhere to the 1M parameter CPU machine constraint.

## 10. What the Next Section Depends On

Stage 8 (Selection, Freeze, and Ensembles) directly consumes:
- The candidate validation rankings and AUDC scores from `stage7_training_summary.md`.
- The trained model checkpoints from `results/checkpoints/` for selecting the Top 5 models under family diversity constraints.
- The cryptographic freeze manifest (`results/frozen_manifest.json`) locking model weights prior to final evaluation.

