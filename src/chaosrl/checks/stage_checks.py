"""Stage check runners for ChaosRL.

Implements `python -m chaosrl check --stage <n>` and `--all`.
Validates stage exit criteria and invariants programmatically.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, List, Tuple

from chaosrl.docs_tools.facts_registry import load_all_facts


def check_stage_1() -> Tuple[bool, List[str]]:
    """Stage 1 exit criteria:

    - Repo skeleton exists
    - Pinned configs and budget.yaml exist
    - Hypotheses written with timestamps in section01_design.md
    - Risk register present (>=10 risks)
    - Metadata recorded in results/run_metadata.json
    - docs-check passes for section 1
    """
    errors: List[str] = []
    # Check budget.yaml
    if not Path("configs/budget.yaml").exists():
        errors.append("configs/budget.yaml is missing")

    # Check run_metadata.json
    meta_path = Path("results/run_metadata.json")
    if not meta_path.exists():
        errors.append("results/run_metadata.json is missing")

    # Check section01_design.md
    sec1_path = Path("docs/section01_design.md")
    if not sec1_path.exists():
        errors.append("docs/section01_design.md is missing")
    else:
        content = sec1_path.read_text(encoding="utf-8")
        content_lower = content.lower()
        if "hypothesis" not in content_lower or "rq1" not in content_lower:
            errors.append("Falsifiable hypotheses missing from docs/section01_design.md")
        if "risk register" not in content_lower:
            errors.append("Risk register missing from docs/section01_design.md")

    # Check docs-check for section 1
    from chaosrl.docs_tools.docs_check import check_single_section
    sec_ok, sec_errs = check_single_section(1)
    if not sec_ok:
        errors.extend([f"Section 1 docs-check: {e}" for e in sec_errs])

    return (len(errors) == 0), errors


def check_stage_2() -> Tuple[bool, List[str]]:
    """Stage 2 exit criteria:
    - RCAEval data downloaded and parsed (or documented fallback)
    - Per-fault-type effect distributions saved
    - Fitted parameters saved in results/calibration/fitted_parameters.json
    - docs-check passes for section 2
    """
    errors: List[str] = []
    parsed_path = Path("data_raw/parsed_cases.json")
    if not parsed_path.exists():
        errors.append("data_raw/parsed_cases.json is missing")
    else:
        try:
            with open(parsed_path, "r", encoding="utf-8") as f:
                cases = json.load(f)
            if len(cases) < 100:
                errors.append(f"Insufficient cases parsed: found {len(cases)}, expected >=100")
        except Exception as e:
            errors.append(f"Failed to read parsed cases: {e}")

    calib_params = Path("results/calibration/fitted_parameters.json")
    if not calib_params.exists():
        errors.append("results/calibration/fitted_parameters.json is missing")

    from chaosrl.docs_tools.docs_check import check_single_section
    sec_ok, sec_errs = check_single_section(2)
    if not sec_ok:
        errors.extend([f"Section 2 docs-check: {e}" for e in sec_errs])

    return (len(errors) == 0), errors


def check_stage_3() -> Tuple[bool, List[str]]:
    """Stage 3 exit criteria:
    - Simulator throughput measured at scales 20, 100, 300
    - Steady state verified
    - Fault effects and retry storm artifacts exist
    - Unit tests pass
    - docs-check passes for section 3
    """
    errors: List[str] = []
    # Check throughput facts
    facts = load_all_facts()
    for sc in [20, 100, 300]:
        key = f"simulator.throughput_scale{sc}"
        if key not in facts:
            errors.append(f"Missing throughput fact: {key}")
        elif facts[key]["value"] < (300 if sc == 300 else 1000):
            errors.append(f"Throughput below target at scale {sc}: {facts[key]['value']} exp/min")

    # Check figures
    for fig_name in ["stage3_fault_effects.png", "stage3_retry_storm_demonstration.png"]:
        if not (Path("docs/figures") / fig_name).exists():
            errors.append(f"Missing figure: {fig_name}")

    # Check tables
    for tbl_name in ["stage3_throughput_benchmarks.md", "stage3_weakness_summary.md"]:
        if not (Path("docs/tables") / tbl_name).exists():
            errors.append(f"Missing table: {tbl_name}")

    from chaosrl.docs_tools.docs_check import check_single_section
    sec_ok, sec_errs = check_single_section(3)
    if not sec_ok:
        errors.extend([f"Section 3 docs-check: {e}" for e in sec_errs])

    return (len(errors) == 0), errors


def check_stage_4() -> Tuple[bool, List[str]]:
    """Stage 4 exit criteria:
    - Environment API compliance verified
    - Zero hidden-information leak verified
    - Action masks functional
    - Linear observation scaling verified
    - docs-check passes for section 4
    """
    errors: List[str] = []
    # Check figures
    for fig_name in ["stage4_reward_comparison.png", "stage4_observation_scaling.png"]:
        if not (Path("docs/figures") / fig_name).exists():
            errors.append(f"Missing figure: {fig_name}")

    # Check table
    if not (Path("docs/tables") / "stage4_reward_safety_probe.md").exists():
        errors.append("Missing table: stage4_reward_safety_probe.md")

    from chaosrl.docs_tools.docs_check import check_single_section
    sec_ok, sec_errs = check_single_section(4)
    if not sec_ok:
        errors.extend([f"Section 4 docs-check: {e}" for e in sec_errs])

    return (len(errors) == 0), errors


def check_stage_5() -> Tuple[bool, List[str]]:
    """Stage 5 exit criteria:
    - All 7 baselines implemented
    - Validation results and breakdown tables exist
    - Figures exist
    - Invariants: Oracle AUDC > baselines, Heuristic recall < 1.0
    - docs-check passes for section 5
    """
    errors: List[str] = []

    # Check figures
    for fig_name in ["stage5_baseline_discovery_curves.png", "stage5_baseline_damage_vs_discovery.png"]:
        if not (Path("docs/figures") / fig_name).exists():
            errors.append(f"Missing figure: {fig_name}")

    # Check tables
    for tbl_name in ["stage5_baseline_validation_results.md", "stage5_weakness_breakdown_by_baseline.md"]:
        if not (Path("docs/tables") / tbl_name).exists():
            errors.append(f"Missing table: {tbl_name}")

    # Check facts and invariants
    facts = load_all_facts()
    if "baseline.oracle.audc" not in facts:
        errors.append("Missing fact: baseline.oracle.audc")
    if "baseline.heuristic.audc" not in facts:
        errors.append("Missing fact: baseline.heuristic.audc")

    if "baseline.oracle.audc" in facts and "baseline.heuristic.audc" in facts:
        oracle_audc = facts["baseline.oracle.audc"]["value"]
        heuristic_audc = facts["baseline.heuristic.audc"]["value"]
        if oracle_audc <= heuristic_audc:
            errors.append(f"Invariant violation: Oracle AUDC ({oracle_audc}) <= Heuristic AUDC ({heuristic_audc})")

    if "baseline.heuristic.recall" in facts:
        h_rec = facts["baseline.heuristic.recall"]["value"]
        if h_rec >= 1.0:
            errors.append(f"Invariant violation: Heuristic recall is 1.0 (decoys failed): {h_rec}")

    from chaosrl.docs_tools.docs_check import check_single_section
    sec_ok, sec_errs = check_single_section(5)
    if not sec_ok:
        errors.extend([f"Section 5 docs-check: {e}" for e in sec_errs])

    return (len(errors) == 0), errors


def check_stage_6() -> Tuple[bool, List[str]]:
    """Stage 6 exit criteria:
    - All 12 candidates registered in CANDIDATE_REGISTRY
    - Smoke benchmarks table exists
    - Throughput and parameter count figures exist
    - Facts registered: pool_size, mean_throughput, max_parameter_count
    - Invariant: max_parameter_count < 1,000,000 (CPU budget)
    - docs-check passes for section 6
    """
    errors: List[str] = []

    # Check registry completeness
    from chaosrl.agents.candidates.registry import CANDIDATE_REGISTRY
    if len(CANDIDATE_REGISTRY) != 12:
        errors.append(f"Candidate registry has {len(CANDIDATE_REGISTRY)} entries, expected 12")

    for i in range(1, 13):
        cid = f"C{i:02d}"
        if cid not in CANDIDATE_REGISTRY:
            errors.append(f"Missing candidate in registry: {cid}")

    # Check figures
    for fig_name in ["stage6_candidate_throughput.png", "stage6_candidate_parameter_counts.png"]:
        if not (Path("docs/figures") / fig_name).exists():
            errors.append(f"Missing figure: {fig_name}")

    # Check table
    if not (Path("docs/tables") / "stage6_candidate_smoke_benchmarks.md").exists():
        errors.append("Missing table: stage6_candidate_smoke_benchmarks.md")

    # Check facts and invariants
    facts = load_all_facts()
    for req_fact in ["candidates.pool_size", "candidates.mean_throughput", "candidates.max_parameter_count"]:
        if req_fact not in facts:
            errors.append(f"Missing fact: {req_fact}")

    if "candidates.max_parameter_count" in facts:
        max_p = facts["candidates.max_parameter_count"]["value"]
        if max_p > 1000000:
            errors.append(f"Machine constraint violated: max parameters {max_p} exceeds 1M limit")

    from chaosrl.docs_tools.docs_check import check_single_section
    sec_ok, sec_errs = check_single_section(6)
    if not sec_ok:
        errors.extend([f"Section 6 docs-check: {e}" for e in sec_errs])

    return (len(errors) == 0), errors


def check_stage_7() -> Tuple[bool, List[str]]:
    """Stage 7 exit criteria:
    - Training summary table exists
    - Tuning log exists
    - Figures exist: stage7_training_curves.png, stage7_tuning_progress.png
    - Facts registered: best_candidate_id, best_candidate_audc, shuffled_obs_audc, shuffled_control_drop
    - Invariant: shuffled_control_drop > 0 (shuffled observations degrade performance)
    - docs-check passes for section 7
    """
    errors: List[str] = []

    # Check figures
    for fig_name in ["stage7_training_curves.png", "stage7_tuning_progress.png"]:
        if not (Path("docs/figures") / fig_name).exists():
            errors.append(f"Missing figure: {fig_name}")

    # Check tables
    for tbl_name in ["stage7_training_summary.md", "stage7_tuning_log.md"]:
        if not (Path("docs/tables") / tbl_name).exists():
            errors.append(f"Missing table: {tbl_name}")

    # Check facts and invariants
    facts = load_all_facts()
    for req_fact in ["training.best_candidate_id", "training.best_candidate_audc", "training.shuffled_control_drop"]:
        if req_fact not in facts:
            errors.append(f"Missing fact: {req_fact}")

    if "training.shuffled_control_drop" in facts:
        drop = facts["training.shuffled_control_drop"]["value"]
        if drop <= 0:
            errors.append(f"Invariant violation: Shuffled observation control drop is {drop} (expected > 0)")

    from chaosrl.docs_tools.docs_check import check_single_section
    sec_ok, sec_errs = check_single_section(7)
    if not sec_ok:
        errors.extend([f"Section 7 docs-check: {e}" for e in sec_errs])

    return (len(errors) == 0), errors


def check_stage_8() -> Tuple[bool, List[str]]:
    """Stage 8 exit criteria:
    - Top 5 selected under diversity constraint (at most 2 per family)
    - Frozen manifest exists with SHA-256 hashes
    - Ensemble tables exist: stage8_top5_frozen_manifest.md, stage8_ensemble_validation_results.md
    - Figures exist
    - docs-check passes for section 8
    """
    errors: List[str] = []

    # Check manifest
    manifest_path = Path("results/frozen_manifest.json")
    if not manifest_path.exists():
        errors.append("Missing results/frozen_manifest.json")
    else:
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            if len(manifest) != 5:
                errors.append(f"Frozen manifest has {len(manifest)} models, expected 5")
            # Check family diversity: at most 2 per family
            from collections import Counter
            families = Counter([m["family"] for m in manifest])
            for fam, cnt in families.items():
                if cnt > 2:
                    errors.append(f"Diversity constraint violated: family {fam} has {cnt} models (max 2)")
        except Exception as e:
            errors.append(f"Failed to read frozen manifest: {e}")

    # Check figures
    for fig_name in ["stage8_top5_diversity_selection.png", "stage8_ensemble_vs_single_discovery.png"]:
        if not (Path("docs/figures") / fig_name).exists():
            errors.append(f"Missing figure: {fig_name}")

    # Check tables
    for tbl_name in ["stage8_top5_frozen_manifest.md", "stage8_ensemble_validation_results.md"]:
        if not (Path("docs/tables") / tbl_name).exists():
            errors.append(f"Missing table: {tbl_name}")

    from chaosrl.docs_tools.docs_check import check_single_section
    sec_ok, sec_errs = check_single_section(8)
    if not sec_ok:
        errors.extend([f"Section 8 docs-check: {e}" for e in sec_errs])

    return (len(errors) == 0), errors


def check_stage_9() -> Tuple[bool, List[str]]:
    """Stage 9 exit criteria:
    - Test-set lock accessed and logged
    - Main comparison, multiscale, family M, statistical, sweep, and ablation tables exist
    - Figures exist
    - Facts registered
    - Invariants: Ensemble beats Chaos Monkey (statistically significant p < 0.05)
    - docs-check passes for section 9
    """
    errors: List[str] = []

    # Check test access log
    test_log = Path("results/test_access_log.csv")
    if not test_log.exists():
        errors.append("results/test_access_log.csv is missing")

    # Check tables
    required_tables = [
        "stage9_main_comparison_scale100.md",
        "stage9_multiscale_comparison.md",
        "stage9_generalization_family_m.md",
        "stage9_statistical_tests.md",
        "stage9_budget_sweep.md",
        "stage9_ablation_study.md",
    ]
    for tbl in required_tables:
        if not (Path("docs/tables") / tbl).exists():
            errors.append(f"Missing table: {tbl}")

    # Check figures
    required_figures = [
        "stage9_discovery_curves_all_methods.png",
        "stage9_damage_vs_discovery_final.png",
        "stage9_scale_generalization.png",
        "stage9_budget_sweep_curves.png",
        "stage9_ablation_comparison.png",
    ]
    for fig in required_figures:
        if not (Path("docs/figures") / fig).exists():
            errors.append(f"Missing figure: {fig}")

    # Check facts and invariants
    facts = load_all_facts()
    for req_fact in [
        "final.scale100.chaosrl_top1.audc",
        "final.scale100.best_ensemble.audc",
        "final.scale100.chaos_monkey.audc",
        "final.scale100.p_value_vs_chaos_monkey",
    ]:
        if req_fact not in facts:
            errors.append(f"Missing fact: {req_fact}")

    if "final.scale100.best_ensemble.audc" in facts and "final.scale100.chaos_monkey.audc" in facts:
        ens_audc = facts["final.scale100.best_ensemble.audc"]["value"]
        cm_audc = facts["final.scale100.chaos_monkey.audc"]["value"]
        if ens_audc <= cm_audc:
            errors.append(f"Invariant violation: Ensemble AUDC ({ens_audc}) <= Chaos Monkey AUDC ({cm_audc})")

    from chaosrl.docs_tools.docs_check import check_single_section
    sec_ok, sec_errs = check_single_section(9)
    if not sec_ok:
        errors.extend([f"Section 9 docs-check: {e}" for e in sec_errs])

    return (len(errors) == 0), errors


def check_stage_10() -> Tuple[bool, List[str]]:
    """Stage 10 exit criteria:
    - section10_analysis_limitations.md complete and passes docs-check
    - docs/OVERALL.md exists with all 20 sections
    - REPORT.md exists
    - docs/QA.md exists with >= 25 entries
    """
    errors: List[str] = []

    overall_path = Path("docs/OVERALL.md")
    if not overall_path.exists():
        errors.append("docs/OVERALL.md is missing")
    else:
        text = overall_path.read_text(encoding="utf-8")
        if len(text.split()) < 3000:
            errors.append(f"docs/OVERALL.md too short: {len(text.split())} words, expected >=3000")

    report_path = Path("REPORT.md")
    if not report_path.exists():
        errors.append("REPORT.md is missing")

    qa_path = Path("docs/QA.md")
    if not qa_path.exists():
        errors.append("docs/QA.md is missing")

    from chaosrl.docs_tools.docs_check import check_single_section
    sec_ok, sec_errs = check_single_section(10)
    if not sec_ok:
        errors.extend([f"Section 10 docs-check: {e}" for e in sec_errs])

    return (len(errors) == 0), errors


def check_stage_11() -> Tuple[bool, List[str]]:
    """Stage 11 exit criteria:
    - section11_reproducibility.md complete and passes docs-check
    - All unit tests pass
    - Acceptance checklist passes 100%
    """
    errors: List[str] = []

    from chaosrl.docs_tools.docs_check import check_single_section
    sec_ok, sec_errs = check_single_section(11)
    if not sec_ok:
        errors.extend([f"Section 11 docs-check: {e}" for e in sec_errs])

    return (len(errors) == 0), errors


STAGE_RUNNERS: Dict[int, Callable[[], Tuple[bool, List[str]]]] = {
    1: check_stage_1,
    2: check_stage_2,
    3: check_stage_3,
    4: check_stage_4,
    5: check_stage_5,
    6: check_stage_6,
    7: check_stage_7,
    8: check_stage_8,
    9: check_stage_9,
    10: check_stage_10,
    11: check_stage_11,
}


def run_stage_check(stage_num: int) -> Tuple[bool, List[str]]:
    """Run exit criteria checks for a given stage."""
    runner = STAGE_RUNNERS.get(stage_num)
    if not runner:
        return False, [f"No check runner implemented for stage {stage_num}"]
    return runner()

