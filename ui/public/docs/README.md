# ChaosRL: Autonomous RL-Driven Chaos Engineering for Microservice Weakness Discovery

> **IMPORTANT NOTICE FOR LONG-RUNNING EXPERIMENTS:**
> Please ensure your laptop is **plugged into the charger** and that **system sleep / suspend is disabled** in power settings before launching full-scale training or evaluation runs. ChaosRL automatically logs progress to `results/heartbeat.json` and supports automatic resumption via `python -m chaosrl resume`.

---

## 1. Overview

ChaosRL replaces the unguided random service termination of Netflix Chaos Monkey with a family of learned, topology-agnostic policies (PPO, GNN, DQN, A2C, Contextual Bandits, Evolution Strategies, and Ensembles). These agents intelligently navigate the microservice call graph to locate systemic vulnerabilities (such as cascading retry storms, missing timeouts, and co-location bottlenecks) while minimizing collateral damage to Service Level Objectives (SLOs).

## 2. Quick Start

Install dependencies and ChaosRL in editable mode:
```bash
pip install -e .
```

Verify installation and test suite:
```bash
pytest tests/ -v
python -m chaosrl check --stage 1
```

Run a fast smoke test across all components:
```bash
python -m chaosrl quick
```

Validate documentation integrity:
```bash
python -m chaosrl docs-check --all
```

## 3. Documentation Structure

- [Overview & Standalone Monograph](docs/OVERALL.md)
- [Documentation Index](docs/INDEX.md)
- [Facts Registry](docs/FACTS.md)
- [Architecture & Hypotheses (Stage 1)](docs/section01_design.md)
- [Data & Calibration (Stage 2)](docs/section02_data_calibration.md)
- [Discrete-Time Simulator (Stage 3)](docs/section03_simulator.md)
- [Gymnasium Environment (Stage 4)](docs/section04_environment.md)
- [Non-Learned Baselines (Stage 5)](docs/section05_baselines.md)
- [Candidate Pool (Stage 6)](docs/section06_candidates.md)
- [Training & Auto-Tuning (Stage 7)](docs/section07_training.md)
- [Selection & Ensembles (Stage 8)](docs/section08_selection_ensembles.md)
- [Final Evaluation (Stage 9)](docs/section09_final_evaluation.md)
- [Analysis & Limitations (Stage 10)](docs/section10_analysis_limitations.md)
- [Reproducibility & Verification (Stage 11)](docs/section11_reproducibility.md)
- [Self-Evaluations Log](docs/self_evaluations/)
- [Decision Log](docs/decision_log.md)
- [Progress Log](docs/PROGRESS.md)
- [Assumptions](docs/ASSUMPTIONS.md)
- [Plain-Language Explainer](docs/EXPLAINER.md)
- [Examiner Q&A](docs/QA.md)
- [Presentation Outline](docs/PRESENTATION_OUTLINE.md)
- [Glossary](docs/GLOSSARY.md)

