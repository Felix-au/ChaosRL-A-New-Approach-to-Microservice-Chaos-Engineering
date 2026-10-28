<!-- Table: stage1_hypotheses -->

| RQ | Focus | Falsifiable Hypothesis | Evidence Metric | Decision Threshold |
| --- | --- | --- | --- | --- |
| RQ1 | Learned vs Random Injection | Learned agent C01 achieves >=25% higher normalized AUDC and >=30% lower cumulative damage than Chaos Monkey and Random-All at scale 100. | Weakness discovery curve AUDC and cumulative damage | Wilcoxon paired signed-rank p < 0.01 with Holm-Bonferroni correction |
| RQ2 | Algorithm Family Comparison | Structure-aware policy gradient (C02 GNN) outperforms value-based (C05 DQN) and gradient-free (C10 ES) across diverse topologies. | Cross-scale mean AUDC across 5 evaluation seeds | Cliff's delta >= 0.33 (medium effect size) |
| RQ3 | Ensemble Superiority | The RF-gated ensemble E3 discovers >=10% more planted compound weaknesses than the single best constituent agent. | Compound weakness recall at B=100 | Statistically significant paired bootstrap difference > 0 |
| RQ4 | Out-of-Distribution Generalization | Agents trained exclusively on Family L (<=300 services) retain >=75% of their AUDC advantage over Random-All when tested zero-shot on Family M at scale 500. | Generalization retention ratio AUDC_gain(OOD) / AUDC_gain(ID) | Retention ratio >= 0.75 across 200 test systems |
