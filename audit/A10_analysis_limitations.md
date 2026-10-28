# Audit Report A10: Research Analysis, Failure Modes & Threats to Validity

## 1. Executive Summary & Verdict

- **Audit Verdict:** **REVISED VERDICT: CORE HYPOTHESES REFUTED ON TEST COHORT**
- **Primary Finding:** A rigorous independent scientific analysis of the final evaluation data demonstrates that three of the four core research hypotheses (RQ1, RQ3, and RQ4) are **REFUTED** by the empirical test evidence on the original $n=10$ test cohort:
  1. **RQ1 (Discovery Efficiency):** In the Scale 100 test set, Chaos Monkey achieved an AUDC of 0.0853 compared to 0.0500 for ChaosRL Top-1 and 0.0500 for the Soft-Vote Ensemble (Wilcoxon $W=16.0, p=1.000$). The hypothesis that learned agents outperform Chaos Monkey is not supported.
  2. **RQ2 (Best Training Paradigm):** Partially confirmed: while structure-aware GNN (C02) outperformed flat policy-gradient models on validation, the overall winner was C12 (TreeRanker), demonstrating the superiority of gradient-boosted structural ranking over pure RL.
  3. **RQ3 (Ensemble Advantage):** Refuted: the Top 5 Soft-Vote Ensemble achieved an AUDC of 0.0500, exactly tying the single best model (C12 TreeRanker, 0.0500; $\Delta = 0.0000, p=1.000$).
  4. **RQ4 (Multi-Scale Generalization):** Refuted: zero-shot transfer collapsed at $N=500$ (AUDC 0.0007, retaining only 1.4% of Scale 100 performance) due to action space dilution.

## 2. Scope & Verified Claims

This audit section verifies the following claims registered in [claim_ledger.csv](file:///c:/Users/Felix/Desktop/chaos%20final/audit/claim_ledger.csv):
- `CLM-S10-01`: Formal evaluation of pre-registered hypotheses RQ1 through RQ4 against recorded test facts.
- `CLM-S10-02`: Grounding of the four empirical failure modes in simulator dynamics and systems phenomena.
- `CLM-S10-03`: Thorough documentation of simulation-to-reality gaps and threats to validity.
- `CLM-S10-04`: Fact-checked reconciliation of all claims in `docs/QA.md` and presentation materials.

## 3. Independent Audit Methodology & Tests

The verification suite in [test_audit_s10_analysis.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s10_analysis.py) executes four validation modules:
1. `test_t_s10_01_rq_verdict_reconciliation`: Loads verified values from `results/facts.json` and evaluates the formal falsifiable conditions pre-registered in `docs/section01_design.md`.
2. `test_t_s10_02_failure_mode_documentation`: Validates documentation coverage for all four systems failure modes.
3. `test_t_s10_03_threats_to_validity_completeness`: Confirms critical threats to validity (discrete-time modeling, action space scaling, and synthetic weakness catalogs) are explicitly analyzed.
4. `test_t_s10_04_qa_factual_alignment`: Analyzes `docs/QA.md` for length, clarity, and factual grounding.

## 4. Empirical Findings & Reproduction Results

The formal reconciliation of research questions against empirical test set evidence is presented below:

| Research Question | Pre-Registered Falsifiable Hypothesis | Pre-Test Claimed Verdict | Observed Test Evidence (`facts.json`, $n=10$) | True Statistical Verdict | Audit Scientific Status |
|---|---|---|---|---|---|
| **RQ1 (Discovery Efficiency)** | Learned agents achieve $\ge 1.5\times$ higher AUDC than Chaos Monkey with lower damage ($p < 0.05$) | Claimed "CONFIRMED" | Ensemble AUDC ($0.0500$) $<$ Chaos Monkey ($0.0853$); Wilcoxon $p = 1.000$ | **REFUTED / NOT CONFIRMED** | Baseline out-performed agent on $N=100$ |
| **RQ2 (Best Training Paradigm)** | Structure-aware GNN outperforms flat policy-gradient and value-based models | Claimed "CONFIRMED" | Validation winner was C12 TreeRanker ($0.0938$), followed by C09 RND ($0.0489$) and C02 GNN ($0.0435$) | **PARTIALLY CONFIRMED** | GNN beat flat PPO, but TreeRanker won |
| **RQ3 (Ensemble Advantage)** | Meta-ensemble of Top 5 beats best single candidate by $\ge 0.02$ AUDC | Claimed "CONFIRMED" | Ensemble AUDC ($0.0500$) equals single Top-1 TreeRanker ($0.0500$); $\Delta = 0.0000, p=1.000$ | **REFUTED / NOT CONFIRMED** | Zero ensemble gain over single best |
| **RQ4 (Multi-Scale Generalization)** | Zero-shot transfer to $N=500$ and Family M retains $\ge 80\%$ performance | Claimed "CONFIRMED" | $N=500$ AUDC dropped to $0.0007$ ($1.4\%$ retention); Family M AUDC dropped to $0.0448$ | **REFUTED / NOT CONFIRMED** | Performance collapsed at $N=500$ scale |

*Caption (Table A10-1):*
- **What the reader sees:** Pre-registered hypotheses for RQ1 through RQ4 compared side-by-side with original claims and verified empirical test evidence.
- **What it implies:** Across the locked test evaluation, RQ1, RQ3, and RQ4 are refuted on the $n=10$ sample: learned agents did not outperform Chaos Monkey, ensembles provided zero gain over Top-1, and performance collapsed at $N=500$.
- **Traceability link:** Pre-registered plan [preregistered_plan.md](file:///c:/Users/Felix/Desktop/chaos%20final/audit/preregistered_plan.md), facts [facts.json](file:///c:/Users/Felix/Desktop/chaos%20final/results/facts.json), and statistical tests [test_audit_s10_analysis.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s10_analysis.py#L15-L45).

The four identified systems failure modes are catalogued below:

| Failure Mode Identifier | Manifestation in Simulator | Affected Algorithmic Families | Underlying Systems Root Cause | Empirical Severity on Scale 100 | Mitigation / Proposed Remedy |
|---|---|---|---|---|---|
| **FM1: Decoy Distraction** | Policies repeatedly probe fortified single-replica leaf services that absorb faults without violating SLO | Tabular heuristics, PPO-MLP (C01), LinUCB (C11) | High local structural prominence (e.g. low replica count) without downstream critical-path impact | High ($\approx 35\%$ of wasted experiments) | Contrastive loss weighting against non-critical leaf nodes |
| **FM2: Upstream Cascading Blindness** | Injecting an early upstream failure trips circuit breakers, preventing observation of deeper latent bugs | High-intensity policies (Chaos Monkey-2, Random-All) | Circuit breaker isolation sheds traffic, masking downstream timeout vulnerabilities | Critical (causes $> 150\text{k}$ collateral damage) | Introduce sequential low-intensity fault ramping before node kill |
| **FM3: Action Space Dilution** | Flat action exploration is overwhelmed as catalog expands ($18N$ actions: 360 at $N=20 \to 9,000$ at $N=500$) | Flat value-based RL (C05 DQN), ES (C10) | Exponential combinatorial explosion of valid action space dilutes policy gradient signals | Severe at $N \ge 300$ ($N=500$ AUDC dropped to $0.0007$) | Hierarchical two-tier policy: select target service $u$, then select fault modality |
| **FM4: Conservative Under-Injection** | RL policies avoid multi-fault compound injections due to risk-averse damage penalty $w_d$ | Safety-penalized PPO (C01, C04) | Default $R_2$ penalty dominates sparse compound discovery bonus ($+1.0$ vs $-0.05 \times \text{Damage}$) | Moderate (Zero compound weaknesses found by Top-1) | Dynamic curiosity shaping bonus for multi-target exploration |

*Caption (Table A10-2):*
- **What the reader sees:** Taxonomy of four empirical failure modes observed during test evaluations, detailing manifestation, affected families, root causes, and mitigations.
- **What it implies:** Performance degradation at large scales ($N=500$) and compound weakness blindness stem from action space dilution and reward-risk trade-offs rather than software bugs.
- **Traceability link:** Failure mode analysis in [section10_analysis_limitations.md](file:///c:/Users/Felix/Desktop/chaos%20final/docs/section10_analysis_limitations.md#L14-L20) and audit test [test_audit_s10_analysis.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s10_analysis.py#L48-L70).

## 5. Negative Controls & Stress Testing

Negative controls confirmed test sensitivity:
- **Refuted Hypothesis Assertion:** Asserting that the empirical data confirmed RQ1 ($0.0500 > 0.0853$) triggered immediate assertion failure, proving test fidelity.
- **Fictitious Failure Mode Check:** Searching for an unmodeled failure mode (`Quantum Teleportation Failure`) correctly failed.
- **Threat Discussion Keywords:** Verifying that simulation limitations are discussed in the markdown text passed.
- **Empty QA Control:** Testing whether the QA document was an empty stub correctly triggered assertion failure.

## 6. Discrepancy & Anomaly Analysis

- **Why TreeRanker Beat Pure RL:** Gradient-boosted decision trees over tabular graph features (in-degree, out-degree, replica count, co-location) outperformed pure neural RL on structured microservices because they directly partition topological heuristic signals without requiring tens of thousands of environment exploration steps.
- **Action Space Explosion at $N=500$:** On 500-service systems, the discrete action space comprises $18 \times 500 = 9,000$ actions. When an agent has an experiment budget of only $B=100$ steps, flat unguided exploration samples only $1.1\%$ of the action catalog, causing discovery collapse ($0.0007$ AUDC).

## 7. Impact on Downstream Stages & System Safety

Reporting negative results honestly is fundamental to scientific integrity. Rather than attempting to conceal the test cohort findings, ChaosRL's revised documentation highlights the conditions under which learned agents fail, providing crucial architectural insights for next-generation chaos engineering systems.

## 8. Audit Recommendations & Proposed Action Items

1. **Adopt Hierarchical Action Selection:** Decompose the $18N$ flat discrete action space into a two-level hierarchical policy: Level 1 selects the candidate service via GNN graph pooling, and Level 2 selects the fault type and intensity.
2. **Re-evaluate on Extended Cohort:** Execute the pre-registered extended test suite ($n=30$ Scale 100 systems) in Phase P5 to establish whether the $0.0500$ vs $0.0853$ outcome holds under high statistical power.
