# ChaosRL Documentation Index

This index catalogs all technical documentation, experimental monographs, logs, and self-evaluations for the ChaosRL research project.

## Core Monographs and Registers
- [OVERALL.md](OVERALL.md): Comprehensive, end-to-end research monograph presenting all architecture, calibration, candidate comparisons, ensembles, and statistical evaluations.
- [FACTS.md](FACTS.md): Central registry of verified experimental facts and quantitative measurements produced by code.
- [decision_log.md](decision_log.md): Chronological ledger of engineering decisions, deviations, and rationale.
- [PROGRESS.md](PROGRESS.md): Live progress tracker recording stage milestones, runtimes, and status.
- [ASSUMPTIONS.md](ASSUMPTIONS.md): Explicit catalog of simulator assumptions, modeling boundaries, and fidelity limits.
- [EXPLAINER.md](EXPLAINER.md): Plain-language guide explaining ChaosRL concepts, algorithms, rewards, and figures for all stakeholders.
- [QA.md](QA.md): Comprehensive defense catalog addressing over 25 critical examiner and peer-review questions.
- [PRESENTATION_OUTLINE.md](PRESENTATION_OUTLINE.md): 8–10 slide executive presentation deck with recommended figures and tables.
- [GLOSSARY.md](GLOSSARY.md): Complete lexicon of terms across distributed systems, reinforcement learning, and chaos engineering.

## Stage Documentation
- [section01_design.md](section01_design.md): Stage 1 — Research questions, formal hypotheses, mathematical metrics, and risk register.
- [section02_data_calibration.md](section02_data_calibration.md): Stage 2 — Empirical dataset ingestion (RCAEval) and distribution fitting.
- [section03_simulator.md](section03_simulator.md): Stage 3 — Discrete-time microservice simulator, cascading dynamics, and weakness catalog.
- [section04_environment.md](section04_environment.md): Stage 4 — Gymnasium-compliant environment, graph observation spaces, action masks, and reward formulations.
- [section05_baselines.md](section05_baselines.md): Stage 5 — Implementation and validation evaluation of non-learned baselines (Chaos Monkey, Random, Round-Robin, UCB, Heuristic, Oracle).
- [section06_candidates.md](section06_candidates.md): Stage 6 — 12-candidate learning pool architecture and SB3 cross-check.
- [section07_training.md](section07_training.md): Stage 7 — Multi-seed training, automated tuning playbook, and validation curves.
- [section08_selection_ensembles.md](section08_selection_ensembles.md): Stage 8 — Diversity-constrained Top-5 selection, SHA-256 model freeze, and ensemble controllers (E1, E2, E3).
- [section09_final_evaluation.md](section09_final_evaluation.md): Stage 9 — Locked test set evaluation, statistical significance testing, OOD generalization, budget sweep, and ablations.
- [section10_analysis_limitations.md](section10_analysis_limitations.md): Stage 10 — Hypothesis testing verdicts (RQ1–RQ4), interpretability analysis, failure cases, and threats to validity.
- [section11_reproducibility.md](section11_reproducibility.md): Stage 11 — Clean-copy verification, reproduction commands, and execution ledger.

