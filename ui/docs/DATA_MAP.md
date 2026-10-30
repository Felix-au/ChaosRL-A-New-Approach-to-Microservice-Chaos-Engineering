# ChaosRL UI Data Map

This document establishes the bidirectional traceability matrix connecting all project artifacts in `results/`, `docs/`, `audit/`, and `src/` to their presentation representations in `ui/public/data/`, `ui/public/docs/`, and `ui/public/figures/`.

## 1. Principles

1. **Zero Hand-Typed Values:** Every number, confidence interval, p-value, and table cell displayed in the UI is derived directly from repository files via `ui/scripts/build_data.py`.
2. **Dual-Run Provenance:** Data from the Original Run ($n=10$ systems, pre-audit) and the Extended Audited Run ($n=30$ systems, post-audit) are partitioned into `pre_audit.json` and `post_audit.json` respectively.
3. **Cryptographic Grounding:** The data build pipeline computes SHA-256 hashes for every input file, registered in `ui/public/data/manifest.json`.

---

## 2. Table & Metrics Mapping

| UI Data Target | Source File(s) | Key Fields / Data Extracted | UI Consumers / Tabs |
|---|---|---|---|
| `data/pre_audit.json` `-> scale100` | `results/original_run/tables/stage9_main_comparison_scale100.csv` | Method, AUDC, Recall, Damage, AUDC 95% CI, Recall 95% CI, Damage 95% CI, Simple Found, Compound Found | **Results Tab** (Table & Leaderboard), **Safety & Cost Tab** |
| `data/post_audit.json` `-> scale100` | `audit/tables/a13_extended_scale100_comparison.md`, `results/audit_rerun/extended_scale100_summary.json` | Method, Combined $n=30$ AUDC, Recall, Damage, 95% CIs, Simple & Compound averages | **Results Tab**, **Overview Tab**, **Original vs Audited Tab** |
| `data/pre_audit.json` `-> statistical_tests` | `results/original_run/tables/stage9_statistical_tests.csv` | Comparison, Mean Diff, Wilcoxon $W$, p-value, FDR adjusted p-value, Cohen's $d$, Power | **Results Tab** (Hypothesis Testing Card) |
| `data/post_audit.json` `-> statistical_tests` | `audit/tables/a13_extended_statistical_tests.md`, `results/audit_rerun/extended_statistical_tests.json` | Original Slice ($n=10$), Extended Slice ($n=20$), Combined Cohort ($n=30$): p-values, power, effect sizes | **Results Tab**, **Rigor & Reproducibility Tab**, **Original vs Audited Tab** |
| `data/pre_audit.json` `-> multiscale` | `results/original_run/tables/stage9_multiscale_comparison.csv` | Scale ($N=20, 50, 100, 200, 500$), AUDC, Relative Gain | **Efficiency & Generalization Tab** |
| `data/post_audit.json` `-> multiscale` | `audit/tables/a13_extended_multiscale.md`, `results/audit_rerun/extended_multiscale_summary.json` | Scale ($N=20, 100, 300, 500$), Chaos Monkey vs Top-1 vs Heuristic vs Ensemble AUDCs | **Efficiency & Generalization Tab** (Scaling Chart) |
| `data/pre_audit.json` `-> budget_sweep` | `results/original_run/tables/stage9_budget_sweep.csv` | Budget ($B=25, 50, 100, 200$), AUDC, Sample efficiency | **Efficiency & Generalization Tab** (Budget Chart) |
| `data/post_audit.json` `-> budget_sweep` | `audit/tables/a13_extended_budget_sweep.md`, `results/audit_rerun/extended_budget_summary.json` | Budget ($B=25, 50, 100, 200$), AUDC across $n=30$ systems | **Efficiency & Generalization Tab** |
| `data/pre_audit.json` `-> family_m` | `results/original_run/tables/stage9_generalization_family_m.csv` | Mesh topology transfer AUDC, Recall, Damage | **Efficiency & Generalization Tab** (Topology Transfer) |
| `data/post_audit.json` `-> family_m` | `audit/tables/a13_extended_family_m.md`, `results/audit_rerun/extended_familym_summary.json` | Mesh topology transfer performance on extended evaluation | **Efficiency & Generalization Tab** |
| `data/pre_audit.json` `-> ablation` | `results/original_run/tables/stage9_ablation_study.csv` | Reward weights (R1/R2/R3), Observation modes, Component ablations | **Insights Tab** (Ablation Section) |
| `data/post_audit.json` `-> ablation` | `results/original_run/tables/stage9_ablation_study.csv`, `audit/tables/a04_reward_safety_audit.md` | Re-verified reward safety coefficients & feature ablations | **Insights Tab** |

---

## 3. Continuous Discovery Trajectories (`curves.json`)

| Entity | Source File | Description |
|---|---|---|
| Pre-Audit Discovery Curves | `results/scale100_raw_results.pkl` | Step-by-step mean weakness discovery and 95% bootstrap confidence band for all 11 methods over $T=100$ steps across $n=10$ systems. Downsampled to 100 discrete evaluation steps. |
| Post-Audit Discovery Curves | `results/audit_rerun/extended_results.pkl` | Combined cohort ($n=30$ systems) trajectories over $T=100$ steps for all 11 methods with exact step-by-step mean and 95% confidence intervals. |

---

## 4. Method Metadata (`methods.json`)

| Method Key | Name | Family | Description | Source File / Checkpoint |
|---|---|---|---|---|
| `C12` | TreeRanker (ChaosRL Top-1) | Tabular / Tree | GBDT-style decision tree ranker over graph centrality & telemetry features | `results/checkpoints/frozen_top5/C12/`, `stage8_top5_frozen_manifest.csv` |
| `C01` | PPO-MLP | Deep RL | Proximal Policy Optimization with 2-layer MLP | `results/checkpoints/frozen_top5/C01/` |
| `C03` | DQN-EpsGreedy | Deep RL | Deep Q-Network with $\epsilon$-greedy exploration | `results/checkpoints/frozen_top5/C03/` |
| `C07` | LinUCB-Graph | Contextual Bandit | Linear Upper Confidence Bound bandit using graph features | `results/checkpoints/frozen_top5/C07/` |
| `C09` | ActorCritic-GCN | Graph RL | Graph Convolutional Network Actor-Critic policy | `results/checkpoints/frozen_top5/C09/` |
| `e1_soft` | ChaosRL Soft-Vote | Ensemble | Probability-weighted soft voting across Top-5 candidates | `results/original_run/tables/stage8_ensemble_validation_results.csv` |
| `e2_borda` | ChaosRL Borda-Rank | Ensemble | Rank-aggregation Borda count ensemble | `results/original_run/tables/stage8_ensemble_validation_results.csv` |
| `e3_gated` | ChaosRL Gated Controller | Ensemble | Metacognitive gated switching controller | `results/original_run/tables/stage8_ensemble_validation_results.csv` |
| `chaos_monkey` | Chaos Monkey (Faithful) | Baseline | Netflix-faithful random service instance termination (pod kill only) | `src/baselines/chaos_monkey.py` |
| `chaos_monkey_2` | Chaos Monkey-2 | Baseline | Dual-target instance termination | `src/baselines/chaos_monkey.py` |
| `random_all` | Random-All | Baseline | Uniform random selection over all 4 fault dimensions | `src/baselines/random_all.py` |
| `round_robin` | Round-Robin Sweep | Baseline | Deterministic cyclic sweep across all services and faults | `src/baselines/round_robin.py` |
| `bandit_ucb` | Bandit UCB | Baseline | Standard multi-armed bandit with UCB1 exploration | `src/baselines/bandit_ucb.py` |
| `heuristic` | Heuristic Expert | Baseline | Domain-expert rule set targeting critical path, high degree, and low redundancy | `src/baselines/heuristic.py` |
| `oracle` | Oracle (Upper Bound) | Reference | Full-knowledge upper bound with omniscient weakness localization | `src/baselines/oracle.py` |

---

## 5. Figures & Visual Assets (`ui/public/figures/`)

Copied verbatim from `docs/figures/` and `audit/figures/`:
- `stage1_topology_dag.svg` -> Architecture and Overview tab
- `stage2_calibration_curves.png` -> Approach tab (Calibration walkthrough)
- `stage3_microservice_callgraph.png` -> Overview tab
- `stage4_observation_tensor.png` -> Approach tab
- `stage7_training_curves.png` -> Methods tab
- `stage9_discovery_curves.png` -> Results tab
- `stage9_multiscale_scaling.png` -> Efficiency tab
- `stage9_safety_damage_scatter.png` -> Safety & Cost tab
- `extended_scale100_comparison.svg` / `png` -> Results tab & Original vs Audited
- `extended_multiscale_scaling.svg` / `png` -> Efficiency tab
- `extended_statistical_power.svg` / `png` -> Rigor & Reproducibility tab
- `extended_damage_tradeoff.svg` / `png` -> Safety & Cost tab

---

## 6. Document Library (`ui/public/docs/`)

All markdown documents indexed in `docs_index.json` via MiniSearch for instant full-text search:
- `REPORT.md` (Executive Research Report)
- `README.md` (Project Overview)
- `audit/REPORT.md` (Independent Audit Report)
- `audit/INDEX.md` (Audit Navigation Index)
- `audit/IMPROVEMENT_SUGGESTIONS.md` (Future Roadmap & Engineering Upgrades)
- `audit/claim_ledger.csv` (72 Pre-Registered Claims Verification)
- `docs/stage01_hypotheses.md` through `docs/stage10_postmortem.md`
- `docs/qa_examiner.md` (Oral Examination Q&A Defense)
- `docs/presentation_outline.md` (Presentation Structure)

