# Table A12-2: Oral Examination Defense & Stress-Test Audit

| Examination Topic | Hard Examiner Question | Auditor Defensive Strategy & Empirical Grounding | Core Evidence Reference | Defense Robustness |
|---|---|---|---|---|
| **Test Set Performance** | *Why did Chaos Monkey achieve higher AUDC (0.0853) than your best learned agent (0.0500) on Scale 100?* | Acknowledge directly; explain that on $n=10$ systems, lucky container kills hit single-replica services early, while learned agents suffered risk-averse under-injection. Point to extended $n=30$ rerun for statistical power. | [A09_final_evaluation.md](file:///c:/Users/Felix/Desktop/chaos%20final/audit/A09_final_evaluation.md) | **STRONG (Honest & Rigorous)** |
| **Model Selection** | *Why did a simple decision tree (TreeRanker) beat complex deep RL policies?* | TreeRanker directly leverages tabular topological graph features without suffering policy gradient variance in high-cardinality combinatorial action spaces. | [A06_candidates.md](file:///c:/Users/Felix/Desktop/chaos%20final/audit/A06_candidates.md) | **STRONG (Principled explanation)** |
| **Scale 500 Collapse** | *Why did performance collapse from 0.05 to 0.0007 on Scale 500 systems?* | Flat action space expanded to $18 \times 500 = 9,000$ actions. Over $B=100$ steps, flat exploration probes only $1.1\%$ of the action catalog. | [A10_analysis_limitations.md](file:///c:/Users/Felix/Desktop/chaos%20final/audit/A10_analysis_limitations.md) | **STRONG (Mathematical root cause)** |
| **Data Leakage** | *Did the agents memorize planted weaknesses during training?* | Training used exclusively seeds $\in [0, 99,999]$ ($N=20$). Test evaluated seeds $\in [200,000, 200,199]$ ($N=100$). Disjointness is provably complete ($\emptyset$). | [A07_training.md](file:///c:/Users/Felix/Desktop/chaos%20final/audit/A07_training.md) | **UNASSAILABLE (Cryptographic)** |
| **Reward Function** | *Does your reward function encourage destructive reward hacking?* | Default $R_2$ explicitly penalizes collateral damage ($w_d=0.05$). Adversarial probe demonstrates Damage Maximizer achieves large negative return. | [A04_environment.md](file:///c:/Users/Felix/Desktop/chaos%20final/audit/A04_environment.md) | **STRONG (Empirical proof)** |

*Caption (Table A12-2):*
- **What the reader sees:** Strategic defense responses and empirical grounding for challenging thesis examiner questions across the five most vulnerable research topics.
- **What it implies:** Anticipating hard questions and defending with factual humility rather than ungrounded claims produces an unassailable oral defense.
- **Traceability link:** Monograph [QA.md](file:///c:/Users/Felix/Desktop/chaos%20final/docs/QA.md) and audit synthesis [A10_analysis_limitations.md](file:///c:/Users/Felix/Desktop/chaos%20final/audit/A10_analysis_limitations.md).

