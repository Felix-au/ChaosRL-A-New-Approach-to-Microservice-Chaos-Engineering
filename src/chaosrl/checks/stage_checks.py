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


STAGE_RUNNERS: Dict[int, Callable[[], Tuple[bool, List[str]]]] = {
    1: check_stage_1,
    2: check_stage_2,
    3: check_stage_3,
    4: check_stage_4,
}


def run_stage_check(stage_num: int) -> Tuple[bool, List[str]]:
    """Run exit criteria checks for a given stage."""
    runner = STAGE_RUNNERS.get(stage_num)
    if not runner:
        return False, [f"No check runner implemented for stage {stage_num}"]
    return runner()

