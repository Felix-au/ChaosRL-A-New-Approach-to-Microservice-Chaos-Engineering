"""Generate comprehensive claim ledger for ChaosRL audit."""
import csv
import json
from pathlib import Path

facts = json.load(open("results/facts.json", encoding="utf-8"))

claims = []

def add_claim(cid, source, loc, text, ctype, dep_data, tids, status="PENDING", evidence="", notes=""):
    claims.append({
        "claim_id": cid,
        "source_file": source,
        "location": loc,
        "claim_text": text,
        "claim_type": ctype,
        "depends_on_data": dep_data,
        "test_ids": tids,
        "status": status,
        "evidence": evidence,
        "notes": notes,
    })

# S1 Claims: Design & Hypotheses
add_claim("CLM-S01-01", "docs/section01_design.md", "Section 1", "Four core research hypotheses pre-registered with date/time before experiments", "procedural", "No", "T-S01-01")
add_claim("CLM-S01-02", "docs/section01_design.md", "Section 2", "Total compute budget ceiling is 36.0 wall-clock hours", "scope", "No", "T-S01-02")
add_claim("CLM-S01-03", "docs/section01_design.md", "Section 4", "Disjoint seed ranges: Train 0..99999, Val 100000..100099, Test 200000..200199", "procedural", "No", "T-S01-03")

# S2 Claims: Data & Calibration
add_claim("CLM-S02-01", "docs/section02_data_calibration.md", "Section 4", f"Total RCAEval empirical calibration cases is {facts['calibration.total_cases']['value']}", "numeric", "Yes", "T-S02-01")
add_claim("CLM-S02-02", "docs/section02_data_calibration.md", "Section 4", f"Fit cases on Online Boutique is {facts['calibration.fit_cases_ob']['value']}", "numeric", "Yes", "T-S02-02")
add_claim("CLM-S02-03", "docs/section02_data_calibration.md", "Section 4", f"Held-out test cases on Sock Shop is {facts['calibration.held_out_cases_ss']['value']}", "numeric", "Yes", "T-S02-03")
add_claim("CLM-S02-04", "docs/section02_data_calibration.md", "Section 4", f"Mean held-out Wasserstein distance is {facts['calibration.mean_held_out_wasserstein']['value']}", "numeric", "Yes", "T-S02-04")
add_claim("CLM-S02-05", "docs/section02_data_calibration.md", "Section 1", "Calibration response functions match physical effect directions (latency up, cpu up)", "causal", "Yes", "T-S02-05")

# S3 Claims: Simulator Engine
add_claim("CLM-S03-01", "docs/section03_simulator.md", "Section 4", f"Simulator throughput on Scale 20 is {facts['simulator.throughput_scale20']['value']} steps/sec", "numeric", "Yes", "T-S03-01")
add_claim("CLM-S03-02", "docs/section03_simulator.md", "Section 4", f"Simulator throughput on Scale 100 is {facts['simulator.throughput_scale100']['value']} steps/sec", "numeric", "Yes", "T-S03-02")
add_claim("CLM-S03-03", "docs/section03_simulator.md", "Section 4", f"Simulator throughput on Scale 300 is {facts['simulator.throughput_scale300']['value']} steps/sec", "numeric", "Yes", "T-S03-03")
add_claim("CLM-S03-04", "docs/section03_simulator.md", "Section 4", f"Scale 100 planted simple weaknesses is {facts['simulator.scale100_simple_weaknesses']['value']}", "numeric", "Yes", "T-S03-04")
add_claim("CLM-S03-05", "docs/section03_simulator.md", "Section 4", f"Scale 100 planted compound weaknesses is {facts['simulator.scale100_compound_weaknesses']['value']}", "numeric", "Yes", "T-S03-05")
add_claim("CLM-S03-06", "docs/section03_simulator.md", "Section 4", f"Scale 100 planted decoy count is {facts['simulator.scale100_decoys']['value']}", "numeric", "Yes", "T-S03-06")
add_claim("CLM-S03-07", "docs/section03_simulator.md", "Section 2", "Simulator is deterministic given fixed random seed", "procedural", "No", "T-S03-07")
add_claim("CLM-S03-08", "docs/section03_simulator.md", "Section 2", "Fault rollback returns system to steady state meeting SLO", "causal", "Yes", "T-S03-08")

# S4 Claims: Environment & Rewards
add_claim("CLM-S04-01", "docs/section04_environment.md", "Section 4", f"Scale 100 discrete action catalog size is {facts['environment.scale100_action_count']['value']}", "numeric", "Yes", "T-S04-01")
add_claim("CLM-S04-02", "docs/section04_environment.md", "Section 4", f"Damage Maximizer return under R2 is {facts['environment.r2_dm_return']['value']}", "numeric", "Yes", "T-S04-02")
add_claim("CLM-S04-03", "docs/section04_environment.md", "Section 4", f"Random policy return under R2 is {facts['environment.r2_rnd_return']['value']}", "numeric", "Yes", "T-S04-03")
add_claim("CLM-S04-04", "docs/section04_environment.md", "Section 2", "Observations contain zero ground-truth weakness or target ID information", "procedural", "No", "T-S04-04")
add_claim("CLM-S04-05", "docs/section04_environment.md", "Section 2", "Action masking guarantees masked invalid actions have zero execution probability", "procedural", "No", "T-S04-05")

# S5 Claims: Baselines
add_claim("CLM-S05-01", "docs/section05_baselines.md", "Section 4", f"Faithful Chaos Monkey validation AUDC is {facts['baseline.chaos_monkey.audc']['value']}", "numeric", "Yes", "T-S05-01")
add_claim("CLM-S05-02", "docs/section05_baselines.md", "Section 4", f"Faithful Chaos Monkey validation damage is {facts['baseline.chaos_monkey.damage']['value']}", "numeric", "Yes", "T-S05-02")
add_claim("CLM-S05-03", "docs/section05_baselines.md", "Section 4", f"Faithful Chaos Monkey validation recall is {facts['baseline.chaos_monkey.recall']['value']}", "numeric", "Yes", "T-S05-03")
add_claim("CLM-S05-04", "docs/section05_baselines.md", "Section 4", f"Heuristic Expert validation AUDC is {facts['baseline.heuristic.audc']['value']}", "numeric", "Yes", "T-S05-04")
add_claim("CLM-S05-05", "docs/section05_baselines.md", "Section 4", f"Heuristic Expert validation damage is {facts['baseline.heuristic.damage']['value']}", "numeric", "Yes", "T-S05-05")
add_claim("CLM-S05-06", "docs/section05_baselines.md", "Section 4", f"Heuristic Expert validation recall is {facts['baseline.heuristic.recall']['value']}", "numeric", "Yes", "T-S05-06")
add_claim("CLM-S05-07", "docs/section05_baselines.md", "Section 4", f"Oracle reference validation AUDC is {facts['baseline.oracle.audc']['value']}", "numeric", "Yes", "T-S05-07")
add_claim("CLM-S05-08", "docs/section05_baselines.md", "Section 4", f"Oracle reference validation damage is {facts['baseline.oracle.damage']['value']}", "numeric", "Yes", "T-S05-08")
add_claim("CLM-S05-09", "docs/section05_baselines.md", "Section 4", f"Oracle reference validation recall is {facts['baseline.oracle.recall']['value']}", "numeric", "Yes", "T-S05-09")
add_claim("CLM-S05-10", "docs/section05_baselines.md", "Section 4", f"Random-All validation damage is {facts['baseline.random_all.damage']['value']}", "numeric", "Yes", "T-S05-10")
add_claim("CLM-S05-11", "docs/section05_baselines.md", "Section 2", "Faithful Chaos Monkey only terminates containers and never injects latency or loss", "procedural", "No", "T-S05-11")

# S6 Claims: Candidates
add_claim("CLM-S06-01", "docs/section06_candidates.md", "Section 4", f"Candidate pool size is {facts['candidates.pool_size']['value']}", "numeric", "No", "T-S06-01")
add_claim("CLM-S06-02", "docs/section06_candidates.md", "Section 4", f"Candidate mean throughput is {facts['candidates.mean_throughput']['value']} steps/sec", "numeric", "Yes", "T-S06-02")
add_claim("CLM-S06-03", "docs/section06_candidates.md", "Section 4", f"Max parameter count is {facts['candidates.max_parameter_count']['value']}", "numeric", "No", "T-S06-03")
add_claim("CLM-S06-04", "docs/section06_candidates.md", "Section 4", f"Custom PPO vs SB3 PPO cross-check difference is {facts['candidates.cross_check_diff']['value']}", "numeric", "Yes", "T-S06-04")
add_claim("CLM-S06-05", "docs/section06_candidates.md", "Section 3", "All candidate neural networks have fewer than 1,000,000 parameters", "scope", "No", "T-S06-05")

# S7 Claims: Training & Tuning
add_claim("CLM-S07-01", "docs/section07_training.md", "Section 4", f"Best candidate ID on validation is {facts['training.best_candidate_id']['value']}", "procedural", "Yes", "T-S07-01")
add_claim("CLM-S07-02", "docs/section07_training.md", "Section 4", f"Best candidate validation AUDC is {facts['training.best_candidate_audc']['value']}", "numeric", "Yes", "T-S07-02")
add_claim("CLM-S07-03", "docs/section07_training.md", "Section 4", f"Shuffled observation control drop is {facts['training.shuffled_control_drop']['value']}", "numeric", "Yes", "T-S07-03")
add_claim("CLM-S07-04", "docs/section07_training.md", "Section 4", f"Tuning rounds completed is {facts['training.tuning_rounds_completed']['value']}", "numeric", "No", "T-S07-04")
add_claim("CLM-S07-05", "docs/section07_training.md", "Section 2", "All 12 candidates were trained across 3 distinct seeds (seeds 10, 20, 30)", "procedural", "No", "T-S07-05")

# S8 Claims: Selection & Ensembles
add_claim("CLM-S08-01", "docs/section08_selection_ensembles.md", "Section 4", f"Top-1 single candidate validation AUDC is {facts['ensemble.top1_single_audc']['value']}", "numeric", "Yes", "T-S08-01")
add_claim("CLM-S08-02", "docs/section08_selection_ensembles.md", "Section 4", f"Best ensemble validation AUDC is {facts['ensemble.best_ensemble_audc']['value']}", "numeric", "Yes", "T-S08-02")
add_claim("CLM-S08-03", "docs/section08_selection_ensembles.md", "Section 4", f"Ensemble absolute AUDC gain over Top-1 is {facts['ensemble.audc_gain']['value']}", "numeric", "Yes", "T-S08-03")
add_claim("CLM-S08-04", "docs/section08_selection_ensembles.md", "Section 2", "Diversity constraint enforces at most 2 candidates per algorithmic family", "procedural", "No", "T-S08-04")
add_claim("CLM-S08-05", "docs/section08_selection_ensembles.md", "Section 2", "Frozen checkpoint SHA-256 hashes verified before test set execution", "procedural", "No", "T-S08-05")

# S9 Claims: Final Evaluation (Scale 100, Multiscale, Family M, Budget, Ablations)
add_claim("CLM-S09-01", "docs/section09_final_evaluation.md", "Section 4", f"Scale 100 test AUDC for Chaos Monkey is {facts['final.scale100.chaos_monkey.audc']['value']}", "numeric", "Yes", "T-S09-01")
add_claim("CLM-S09-02", "docs/section09_final_evaluation.md", "Section 4", f"Scale 100 test AUDC for Heuristic Expert is {facts['final.scale100.heuristic.audc']['value']}", "numeric", "Yes", "T-S09-02")
add_claim("CLM-S09-03", "docs/section09_final_evaluation.md", "Section 4", f"Scale 100 test AUDC for ChaosRL Top-1 is {facts['final.scale100.chaosrl_top1.audc']['value']}", "numeric", "Yes", "T-S09-03")
add_claim("CLM-S09-04", "docs/section09_final_evaluation.md", "Section 4", f"Scale 100 test AUDC for Best Ensemble is {facts['final.scale100.best_ensemble.audc']['value']}", "numeric", "Yes", "T-S09-04")
add_claim("CLM-S09-05", "docs/section09_final_evaluation.md", "Section 4", f"Scale 100 test weakness recall for Best Ensemble is {facts['final.scale100.best_ensemble.recall']['value']}", "numeric", "Yes", "T-S09-05")
add_claim("CLM-S09-06", "docs/section09_final_evaluation.md", "Section 4", f"Scale 100 p-value vs Chaos Monkey is {facts['final.scale100.p_value_vs_chaos_monkey']['value']}", "numeric", "Yes", "T-S09-06")
add_claim("CLM-S09-07", "docs/section09_final_evaluation.md", "Section 4", f"Held-out Scale 500 test AUDC for Ensemble is {facts['final.generalization.scale500_audc']['value']}", "numeric", "Yes", "T-S09-07")
add_claim("CLM-S09-08", "docs/section09_final_evaluation.md", "Section 4", f"Held-out Family M mesh test AUDC for Ensemble is {facts['final.generalization.family_m_audc']['value']}", "numeric", "Yes", "T-S09-08")
add_claim("CLM-S09-09", "docs/tables/stage9_multiscale_comparison.md", "Row 4", "Scale 500 ChaosRL Top-1 AUDC is 0.0156 vs Chaos Monkey 0.0010 (15.6x advantage)", "comparative", "Yes", "T-S09-09")
add_claim("CLM-S09-10", "docs/tables/stage9_generalization_family_m.md", "Row 4", "Family M ChaosRL Ensemble recall is 0.1250 vs Chaos Monkey 0.0469 (2.66x advantage)", "comparative", "Yes", "T-S09-10")
add_claim("CLM-S09-11", "docs/tables/stage9_budget_sweep.md", "Row 1", "At budget B=25, ChaosRL Ensemble recall is 0.1094 vs Chaos Monkey 0.0000", "comparative", "Yes", "T-S09-11")
add_claim("CLM-S09-12", "docs/tables/stage9_budget_sweep.md", "Row 4", "ChaosRL Ensemble achieves recall 0.1094 at B=25 matching Chaos Monkey at B=200 (8x efficiency)", "comparative", "Yes", "T-S09-12")

# S10 Claims: Analysis & Monograph
add_claim("CLM-S10-01", "docs/OVERALL.md", "Section 1", "docs/OVERALL.md is a complete 20-section monograph with >= 3000 words", "scope", "No", "T-S10-01")
add_claim("CLM-S10-02", "REPORT.md", "Entire doc", "REPORT.md is a complete research report with >= 4000 words and 12 sections", "scope", "No", "T-S10-02")
add_claim("CLM-S10-03", "docs/QA.md", "Entire doc", "docs/QA.md contains at least 25 deep technical entries", "scope", "No", "T-S10-03")
add_claim("CLM-S10-04", "docs/OVERALL.md", "Section 14", "RQ1 verdict is CONFIRMED on Multi-Scale and Mesh, with honest disclosure on Scale 100", "comparative", "Yes", "T-S10-04")
add_claim("CLM-S10-05", "docs/OVERALL.md", "Section 14", "RQ2 verdict is CONFIRMED: structure-aware GNN and tree ranker beat flat policy gradients", "comparative", "Yes", "T-S10-05")
add_claim("CLM-S10-06", "docs/OVERALL.md", "Section 14", "RQ3 verdict is CONFIRMED: meta-ensemble beats single models on validation and OOD", "comparative", "Yes", "T-S10-06")
add_claim("CLM-S10-07", "docs/OVERALL.md", "Section 14", "RQ4 verdict is STRONGLY CONFIRMED: zero-shot scale transfer to N=500 and Family M mesh", "comparative", "Yes", "T-S10-07")

# S11 Claims: Reproducibility
add_claim("CLM-S11-01", "docs/section11_reproducibility.md", "Section 6", "python -m chaosrl quick executes complete end-to-end smoke verification in < 5 min", "procedural", "No", "T-S11-01")
add_claim("CLM-S11-02", "docs/section11_reproducibility.md", "Section 7", "100% of Acceptance Checklist criteria (25/25) verified", "procedural", "No", "T-S11-02")
add_claim("CLM-S11-03", "docs/section11_reproducibility.md", "Section 7", "All 44 unit and integration tests in tests/ pass cleanly", "procedural", "No", "T-S11-03")

# S12 Claims: Presentation Materials
add_claim("CLM-S12-01", "docs/PRESENTATION_OUTLINE.md", "Slide 10", "Slide 10 claims 15.6x discovery advantage at scale 500", "numeric", "Yes", "T-S12-01")
add_claim("CLM-S12-02", "docs/PRESENTATION_OUTLINE.md", "Slide 11", "Slide 11 claims 8x sample efficiency advantage at budget B=25", "numeric", "Yes", "T-S12-02")
add_claim("CLM-S12-03", "docs/PRESENTATION_OUTLINE.md", "Slide 12", "Slide 12 claims 2.66x weakness recall on held-out Family M mesh", "numeric", "Yes", "T-S12-03")

fieldnames = ["claim_id", "source_file", "location", "claim_text", "claim_type", "depends_on_data", "test_ids", "status", "evidence", "notes"]
with open("audit/claim_ledger.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(claims)

print(f"Generated audit/claim_ledger.csv with {len(claims)} checkable claims.")

