# Self-evaluation: Stage 06 Candidate Pool

- Date/time: 2026-10-28T18:44:00+05:30
- Git commit hash: `71caaf56a2d8fd1dc97c70c3e6dd7f2831cd908d`
- Config hash: `e4b17a82` (configs/training.yaml)

## Exit Criteria

| Criterion | Result | Evidence |
| :--- | :--- | :--- |
| All 12 candidates implemented (C01..C12) | PASS | `src/chaosrl/agents/candidates/registry.py` (C01..C12 registered) |
| Smoke benchmark runs on all 12 candidates | PASS | `docs/tables/stage6_candidate_smoke_benchmarks.md` (30 steps each) |
| Gradient updates succeed without NaN or error | PASS | `Gradient Update Clean = PASS` on all 12 candidates |
| Scorer networks topology-agnostic | PASS | Evaluated on $N=20, 50, 100, 300$ with identical weights |
| SB3 MaskablePPO cross-check passes | PASS | Custom PPO matches SB3 within 0.0019 reward units (<0.5 threshold) |
| Throughput and parameter count figures saved | PASS | `stage6_candidate_throughput.png`, `stage6_candidate_parameter_counts.png` |
| Machine constraint respected | PASS | Max parameter count is 47,123 (< 1,000,000 budget) |
| Section documentation complete | PASS | `docs/section06_candidates.md` (all 10 mandatory headings, >=600 words) |
| Unit tests pass | PASS | `pytest tests/test_candidates.py` (15/15 passed) |

## Independent Recomputation

| Quantity | Primary Value | Recomputed Value | Match? |
| :--- | :--- | :--- | :--- |
| `candidates.pool_size` | 12 | 12 (len(CANDIDATE_REGISTRY)) | MATCH |
| `candidates.max_parameter_count` | 47123 | 47123 (recomputed from `stage6_candidate_smoke_benchmarks.csv`) | MATCH |
| `candidates.mean_throughput` | 88.2 | 88.2 (mean of throughput column in CSV) | MATCH |
| `candidates.cross_check_diff` | 0.0019 | 0.0019 (abs(-0.0418 - (-0.0437))) | MATCH |

## Invariants Checked

1. **Topology Invariance:** All scorer architectures accept inputs of arbitrary size $N$ without changing weight parameters or failing. **PASS**
2. **Action Mask Compliance:** 100% of candidate actions obey `obs["action_mask"]`, with zero illegal gateway terminations. **PASS**
3. **Parameter Ceiling Invariant:** Max parameters across all candidates is 47,123, which is 4.7% of the 1,000,000 parameter budget. **PASS**
4. **Gradient Stability Invariant:** No NaN or Inf observed during gradient updates across any candidate. **PASS**
5. **Cross-Check Parity:** Custom PPO matches `sb3-contrib` `MaskablePPO` within 0.0019 reward units. **PASS**

## Adversarial Review

| Risk | How Tested | Outcome | Action Taken |
| :--- | :--- | :--- | :--- |
| Action space changes with $N$ breaking fixed layers | Tested forward pass with $N \in [20, 50, 100, 300]$ | Output logits scale dynamically as $(N \times 18)$ | Verified per-node scoring factored formulation |
| Large outage damage exploding PPO gradients | Simulated extreme outage with reward -167 | Initial step-level SGD diverged | Implemented return clipping and trajectory batch accumulation |
| SB3 cross-check unfair comparison | Trained both models for 300 steps under identical seeds | Evaluated returns matched closely (-0.0418 vs -0.0437) | Retrained and evaluated both on held-out environment |
| GRU hidden state carrying across episodes | Checked episode boundary reset logic | `reset_episode` clears hidden state | Added automated assertion in test suite |
| TreeRanker failing on cold-start | Checked behavior before dataset fitting | Falls back to masked random exploration | Documented limitation in Section 06 |

## Figures Inspected

- `docs/figures/stage6_candidate_throughput.png`: Visualizes steps/sec across all 12 candidates, clearly demonstrating that all models exceed 30 steps/sec with mean of 88.2 steps/sec.
- `docs/figures/stage6_candidate_parameter_counts.png`: Log-scale parameter plot with horizontal red reference line at 1M budget; confirms all architectures are ultra-compact (<48k parameters).

## Issues Found and Fixed

- **Issue 1:** `NameError: name 'F' is not defined` occurred during C01 update. Fixed by importing `torch.nn.functional as F` in `ppo_agents.py`.
- **Issue 2:** Target shape mismatch warning in PPO value loss (`torch.Size([1])` vs `torch.Size([])`). Fixed by using `.view(-1)` on critic predictions.
- **Issue 3:** PPO step-level SGD caused gradient instability under large negative returns. Refactored into a clean trajectory-averaged batch update with return clipping.

## Issues Remaining (Accepted Limitations)

- Full multi-seed training and hyperparameter tuning will be executed in Stage 7 across 3 random training seeds.

## Verdict

**PASS** (All exit criteria pass, all invariants hold, recomputations match, adversarial review resolved).
- Iteration number: 1

