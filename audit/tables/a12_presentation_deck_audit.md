# Table A12-1: Executive Presentation Deck Structure & Fact Traceability Audit

| Slide Index | Slide Title & Theme | Key Empirical Takeaway | Referenced Fact Keys | Narrative Status |
|---|---|---|---|---|
| **Slide 1** | The Failure of Random Chaos | Chaos Monkey misses multi-fault and non-kill weaknesses ($>70\%$ missed) | `calibration.total_cases`, `simulator.scale100_decoys` | Verified |
| **Slide 2** | Research Questions & Core Hypotheses | Pre-registered hypotheses for RQ1..RQ4 and formal decision criteria | `preregistered_plan.md` | Verified |
| **Slide 3** | Grounded in Reality: Data-Calibrated Simulation | 250 empirical cases from RCAEval; held-out Wasserstein distance $35.89$ | `calibration.mean_held_out_wasserstein` | Verified |
| **Slide 4** | Candidate Pool & Diverse Algorithm Families | 12 candidate architectures across 8 distinct paradigms ($< 48\text{k}$ params) | `candidates.mean_throughput` | Verified |
| **Slide 5** | The Top-5 Selection & Ensembling | Diversity-constrained Top 5 selection; Soft Vote, Borda, and Gated Ensembles | `results/frozen_manifest.json` | Verified |
| **Slide 6** | Main Evaluation Results (RQ1 & RQ2) | Rigorous reporting of Scale 100 test results: Chaos Monkey ($0.0853$) vs Top-1 ($0.0500$) | `final.scale100.best_ensemble.audc`, `final.scale100.chaos_monkey.audc` | **Audited & Reconciled** |
| **Slide 7** | Out-of-Distribution Generalization (RQ4) | Performance drop on Scale 500 ($0.0007$) due to action space dilution | `final.generalization.scale500_audc`, `final.generalization.family_m_audc` | **Audited & Reconciled** |
| **Slide 8** | What Did the Agents Learn? (Interpretability) | TreeRanker and GNN policies focus on critical hubs and unshielded paths | Feature importance matrices | Verified |
| **Slide 9** | Integrity, Limitations, and Future Horizons | Full disclosure of negative results, threats to validity, and roadmap | `test_access_log.csv` | **Audited & Reconciled** |

*Caption (Table A12-1):*
- **What the reader sees:** Slide index, topic, empirical takeaways, and fact keys referenced in the executive presentation deck.
- **What it implies:** The presentation deck covers all required research phases and can be delivered with complete scientific defensibility once updated with true test facts.
- **Traceability link:** Outline file [PRESENTATION_OUTLINE.md](file:///c:/Users/Felix/Desktop/chaos%20final/docs/PRESENTATION_OUTLINE.md) and test [test_audit_s12_presentation.py](file:///c:/Users/Felix/Desktop/chaos%20final/tests/audit/test_audit_s12_presentation.py).
