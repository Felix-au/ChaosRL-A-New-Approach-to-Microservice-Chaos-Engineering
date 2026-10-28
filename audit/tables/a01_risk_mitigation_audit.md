# Table: A01 Risk Register & Mitigation Code Audit

| Risk ID | Risk Description | Documented Mitigation | Code Location | Verified in Code? |
|---|---|---|---|---|
| **R01** | Simulator-to-real divergence | Calibration on real RCAEval failure cases via distribution matching | `src/chaosrl/data/calibrate.py` | **YES** |
| **R02** | Test-set snooping & p-hacking | Hard programmatic test-set lock with mandatory environment variable | `src/chaosrl/simulator/system_generator.py` | **YES** |
| **R03** | Reward hacking & damage | Regularized reward $R_2$ explicitly penalizing collateral SLO degradation | `src/chaosrl/env/chaos_env.py` | **YES** |
| **R04** | Topological index exploitation | Vectorized node-level scoring with permutation invariant message passing | `src/chaosrl/agents/candidates/networks.py` | **YES** |
| **R05** | Ensemble signal dilution | Diversity-constrained selection ($\le 2$ models per family) + gating | `src/chaosrl/agents/ensemble/meta_controllers.py` | **YES** |
| **R06** | Hardware thermal throttling | CPU-only PyTorch execution with single-threaded workers | `src/chaosrl/evaluate/final_eval.py` | **YES** |

