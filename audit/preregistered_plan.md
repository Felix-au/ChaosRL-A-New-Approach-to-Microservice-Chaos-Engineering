# ChaosRL Independent Audit: Pre-Registered Re-Evaluation Plan

- **Pre-Registration Timestamp:** 2026-10-29T01:25:00+05:30
- **Auditor Role:** Independent Verification Engineer & Research Auditor
- **Status:** **LOCKED & PRE-REGISTERED PRIOR TO TEST-SET ACCESS**

---

## 1. Purpose and Governance

In accordance with Section 3 (Integrity Rules), Section 4 (Re-evaluation Policy), and Section 5.6 (Test-Set Lock), this document formally pre-registers the complete experimental design, system cohort partitions, candidate methods, primary metrics, statistical procedures, and decision rules before any audit evaluation touches the locked test set.

No parameter, hyperparameter, model weight, or prompt may be adjusted in response to rerun results. All access to locked test seeds (`200,000` to `200,199`) is programmatically audited in `results/test_access_log.csv` under the label `audit`.

---

## 2. System Cohort Sizing and Seed Partitions

All test systems are instantiated deterministically from the locked seed range `[200,000, 200,199]`. To ensure rigorous statistical power while respecting the 35-minute P5 time allocation and CPU execution constraints, the audit test evaluation partitions the seed space as follows:

### 2.1 Core Scale 100 Cohort ($N=100$, Budget $B=100$)
- **Original Slice (Identifiable):** Seeds `200,000` through `200,009` ($n=10$ systems).
- **Extended Audit Slice:** Seeds `200,010` through `200,029` ($n=20$ new systems).
- **Combined Cohort:** Seeds `200,000` through `200,029` ($N_{\text{total}} = 30$ systems).
- **Reporting Requirement:** All metrics reported for (1) Original Slice only, (2) New Systems only, and (3) Combined Cohort.

### 2.2 Multi-Scale Generalization Cohort ($N \in \{20, 100, 300, 500\}$, $B=100$)
- **Scale 20:** Seeds `200,050` through `200,069` ($n=20$ systems; includes original 8 seeds `200,050..200,057`).
- **Scale 100:** Seeds `200,050` through `200,069` ($n=20$ systems; includes original 8 seeds `200,050..200,057`).
- **Scale 300:** Seeds `200,050` through `200,069` ($n=20$ systems; includes original 8 seeds `200,050..200,057`).
- **Scale 500 (Out-of-Distribution):** Seeds `200,050` through `200,069` ($n=20$ systems; includes original 8 seeds `200,050..200,057`).

### 2.3 Topological Generalization Cohort (Held-Out Family M Mesh, $N=100$, $B=100$)
- **Original Slice:** Seeds `200,100` through `200,107` ($n=8$ systems).
- **Extended Slice:** Seeds `200,108` through `200,119` ($n=12$ new systems).
- **Combined Family M Cohort:** Seeds `200,100` through `200,119` ($n=20$ systems).

### 2.4 Budget Sweep Cohort ($B \in \{25, 50, 100, 200\}$, $N=100$)
- Evaluated on seeds `200,000` through `200,015` ($n=16$ systems).

---

## 3. Evaluated Methods

All methods are evaluated on identical systems, identical random seeds, and identical experiment budgets:

1. **Chaos Monkey (Faithful):** Netflix reference policy; uniform random container termination only.
2. **Heuristic Expert:** SRE domain rule baseline; targets high-centrality hubs, single-replica services, and co-located instances.
3. **ChaosRL Top-1 (TreeRanker / C12):** Single best candidate selected under Stage 8 diversity rules; frozen checkpoint `rank1_C12_TreeRanker.pkl`.
4. **ChaosRL Ensemble (Gated Controller / E3):** Multi-paradigm meta-controller routing across frozen Top 5 models.
5. **Oracle (Reference Upper Bound):** Ground-truth guided reference for measuring theoretical optimality gap.

---

## 4. Primary Metrics and Definitions

1. **Normalized Area Under the Discovery Curve (AUDC):**
   $$\text{AUDC} = \frac{1}{B} \int_{0}^{B} \frac{W_{\text{found}}(t)}{W_{\text{total}}} \, dt = \frac{1}{B} \sum_{t=1}^{B} \frac{W_{\text{found}}(t)}{W_{\text{total}}}$$
   *Justification:* Captures discovery speed and sample efficiency; rewards finding weaknesses early.
2. **Weakness Recall:**
   $$\text{Recall} = \frac{W_{\text{found}}(B)}{W_{\text{total}}}$$
   *Justification:* Measures overall vulnerability coverage regardless of discovery timing.
3. **Cumulative Severity-Weighted Damage:**
   $$\text{Damage} = \sum_{t=1}^{B} \left( \lambda_{\text{latency}} \cdot \Delta L(t) + \lambda_{\text{error}} \cdot \Delta E(t) \right)$$
   *Justification:* Measures collateral customer SLO impact and test safety.

---

## 5. Statistical Hypothesis Testing Procedure

1. **Paired Comparisons:** Because methods are evaluated on identical system topologies, comparisons are strictly paired by system seed.
2. **Test Statistic:** Paired two-sided Wilcoxon signed-rank test (`scipy.stats.wilcoxon`). If all paired differences are zero, $p=1.0, W=0.0$.
3. **Family-Wise Error Control:** Holm-Bonferroni step-down correction applied across the family of 4 primary hypothesis tests at nominal $\alpha = 0.05$:
   - ChaosRL Ensemble vs. Chaos Monkey (Faithful)
   - ChaosRL Top-1 vs. Chaos Monkey (Faithful)
   - ChaosRL Ensemble vs. Heuristic Expert
   - ChaosRL Ensemble vs. ChaosRL Top-1
4. **Confidence Intervals:** 95% non-parametric bootstrap confidence intervals computed over systems using 2,000 bootstrap resamples.

---

## 6. Pre-Registered Decision Rules

| Claim / Question | Decision Rule for "SUPPORTED" | Decision Rule for "PARTLY SUPPORTED" | Decision Rule for "NOT SUPPORTED" |
|---|---|---|---|
| **RQ1: Discovery vs Chaos Monkey** | Ensemble or Top-1 achieves statistically significant higher AUDC ($p < 0.05$, Holm-Bonferroni) on combined cohort, OR achieves higher recall with $\le 1.5\times$ damage | Superiority holds on large scales ($N \ge 300$) and mesh topologies, or at low budget ($B=25$), but not on small layered slice | Chaos Monkey matches or exceeds ChaosRL across all scales, budgets, and topologies |
| **RQ2: Best Paradigm** | Structure-aware GNN (C02) or TreeRanker (C12) achieves highest validation AUDC and maintains scaling up to $N=500$ | Learned models outperform flat baselines on some scales but struggle on others | Flat non-structural models outperform graph-aware policies across all scales |
| **RQ3: Ensemble Advantage** | Meta-Ensemble achieves $\ge 10\%$ relative gain in AUDC or recall over single Top-1 on validation and out-of-distribution cohorts | Meta-Ensemble achieves highest recall on mesh and budget sweeps, but ties on specific small slices | Single model strictly dominates ensemble across all metrics and scales |
| **RQ4: Generalization** | Top-1 and Ensemble retain $\ge 50\%$ discovery efficiency at $N=500$ and on Family M mesh, outperforming Chaos Monkey by $\ge 2\times$ | Models generalize on one dimension (scale or topology) but fail on the other | Performance collapses to random baseline ($< 1.1\times$ Chaos Monkey) on both OOD test sets |

---

## 7. Storage and Audit Trail

- All newly generated raw logs, trajectories, and tables will be stored in `results/audit_rerun/`.
- Preserved baseline results remain untouched in `results/original_run/`.
- Accesses will be logged to `results/test_access_log.csv` with label `audit`.

