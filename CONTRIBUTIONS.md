# Contributions

This document outlines the primary areas of ownership and contributions for the **ChaosRL** project.

---

## Contributors

| Contributor | GitHub / Handle | Primary Focus |
| :--- | :--- | :--- |
| **Harshit Soni** | `Felix-au` | Core Research, Simulation, RL Pipeline, Audit & Verification |
| **Aarav Pratap Singh** | — | Presentation UI, Visualization, Insight Engine & Polish |

---

## Detailed Breakdown

### Harshit Soni (`Felix-au`) — Core System & Research Pipeline
Responsible for the end-to-end core ChaosRL architecture, experimental methodology, and verification:

- **Core Engine & Simulator (`src/chaosrl/`, `configs/`)**:
  - Designed and implemented the discrete-time microservice call-graph simulator, fault injection mechanics, and Gymnasium environment.
  - Built empirical latency and workload calibration pipelines (`data_raw/`).
- **Baselines, RL Candidates & Training (`src/chaosrl/`, `results/`)**:
  - Implemented non-learned baselines and the candidate policy pool (PPO, GNN, DQN, A2C, Contextual Bandits, Evolution Strategies, and Ensembles).
  - Executed multi-seed training, hyperparameter auto-tuning, top-5 model selection, ensemble benchmarking, and locked test-set statistical evaluation.
- **Verification & Audit (`tests/`, `tests/audit/`, `audit/`)**:
  - Authored the core test suite covering calibration, simulator dynamics, environment contracts, baselines, candidates, ensembles, CLI, and documentation checks.
  - Conducted the pre-registered re-evaluation plan, section-by-section audit verification, and reproducibility checks.
- **Technical Documentation (`docs/`, `REPORT.md`, `README.md`)**:
  - Authored the standalone research monograph, stage-by-stage technical sections, facts registry, decision logs, and examiner Q&A.

---

### Aarav Pratap Singh — Presentation UI & Finesse
Responsible for the interactive presentation dashboard, visual polish, and frontend developer experience:

- **Presentation Application (`ui/src/`, `ui/index.html`, `ui/vite.config.ts`, `ui/tailwind.config.js`)**:
  - Built the React + TypeScript + Vite + Tailwind CSS presentation dashboard (`AppShell`, `CommandPalette`, `GuidedTour`, `PresentationOverlay`, and all tab views under `ui/src/tabs/`).
- **Data Visualization & Rendering (`ui/src/charts/`, `ui/src/tables/`, `ui/src/markdown/`)**:
  - Implemented interactive ECharts discovery/tradeoff visualizations, TanStack data tables, and rich Markdown rendering with KaTeX math and Mermaid diagram support.
- **Automated Insight Engine & Data Bundling (`ui/src/insight/`, `ui/scripts/build_data.py`, `ui/public/`)**:
  - Built the role-tailored insight generation engine and the `build_data.py` pipeline bundling JSON datasets, figures, and documentation for the UI.
- **UI/UX Finesse & Frontend Testing (`ui/tests/`, `ui/docs/`, `ui/start-ui.sh`, `ui/start-ui.bat`)**:
  - Polished layout, interactive walkthroughs, cross-platform launch scripts, UI documentation (`ui/docs/`), and Vitest data-integrity and rendering tests.
