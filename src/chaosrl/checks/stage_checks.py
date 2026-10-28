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


STAGE_RUNNERS: Dict[int, Callable[[], Tuple[bool, List[str]]]] = {
    1: check_stage_1,
}


def run_stage_check(stage_num: int) -> Tuple[bool, List[str]]:
    """Run exit criteria checks for a given stage."""
    runner = STAGE_RUNNERS.get(stage_num)
    if not runner:
        return False, [f"No check runner implemented for stage {stage_num}"]
    return runner()

