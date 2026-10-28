# Table A10-1: Formal Research Question & Hypothesis Reconciliation

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

