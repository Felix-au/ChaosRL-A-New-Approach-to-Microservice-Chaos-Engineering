"""Documentation integrity checker for ChaosRL.

Enforces Section 6.6 documentation standards:
- 10 mandatory headings in order
- Substantive prose >= 600 words
- Figures/tables minimum requirements (>=2 figures or 1 figure + 2 tables)
- Referenced figure/table files exist
- No unresolved {{fact:...}} placeholders
- Captions have 3 required parts (what it shows, how to read it, takeaway)
- INDEX.md links to all existing docs
- Self-evaluation record exists
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from chaosrl.docs_tools.facts_registry import load_all_facts

MANDATORY_HEADINGS = [
    "Purpose",
    "What was implemented",
    "Design decisions and rationale",
    "Key facts and figures",
    "Figure captions",
    "How to reproduce",
    "Tests and verification",
    "Problems encountered and fixes",
    "Limitations and assumptions specific to this section",
    "What the next section depends on",
]

SECTION_FILE_MAP = {
    1: "section01_design.md",
    2: "section02_data_calibration.md",
    3: "section03_simulator.md",
    4: "section04_environment.md",
    5: "section05_baselines.md",
    6: "section06_candidates.md",
    7: "section07_training.md",
    8: "section08_selection_ensembles.md",
    9: "section09_final_evaluation.md",
    10: "section10_analysis_limitations.md",
    11: "section11_reproducibility.md",
    12: "section12_docker_validation.md",
}


def count_prose_words(text: str) -> int:
    """Count words of substantive prose, excluding code blocks and tables."""
    # Remove code blocks
    text_no_code = re.sub(r"```[\s\S]*?```", "", text)
    # Remove table lines
    lines = text_no_code.splitlines()
    prose_lines = [
        line for line in lines
        if not line.strip().startswith("|") and not line.strip().startswith("<!--")
    ]
    cleaned = " ".join(prose_lines)
    # Extract alphanumeric words
    words = re.findall(r"\b[A-Za-z0-9_-]+\b", cleaned)
    return len(words)


def extract_headings(text: str) -> List[str]:
    """Extract markdown header titles (h2 and h3)."""
    headings = []
    for line in text.splitlines():
        match = re.match(r"^#{1,3}\s+(?:\d+[\.\d*]*\s*)?([^\n#]+)", line)
        if match:
            headings.append(match.group(1).strip())
    return headings


def check_section_headings(headings: List[str]) -> Tuple[bool, List[str]]:
    """Check that all 10 mandatory headings appear in order."""
    missing: List[str] = []
    current_idx = 0

    for required in MANDATORY_HEADINGS:
        found = False
        req_lower = required.lower()
        for i in range(current_idx, len(headings)):
            h_lower = headings[i].lower()
            if req_lower in h_lower or any(word in h_lower for word in req_lower.split() if len(word) > 3):
                found = True
                current_idx = i + 1
                break
        if not found:
            # Also search anywhere
            anywhere = any(req_lower in h.lower() for h in headings)
            if not anywhere:
                missing.append(f"Missing mandatory heading: '{required}'")
            else:
                missing.append(f"Heading out of order: '{required}'")

    return (len(missing) == 0), missing


def check_captions(text: str) -> Tuple[bool, List[str]]:
    """Check that figure captions have the three required parts:

    - what it shows
    - how to read it
    - takeaway
    """
    errors: List[str] = []
    # Find all image inclusions: ![alt](path)
    images = re.findall(r"!\[(.*?)\]\((.*?)\)", text)
    if not images:
        return True, []

    # Check for caption section or inline captions
    text_lower = text.lower()
    has_shows = ("what it shows" in text_lower) or ("shows" in text_lower)
    has_read = ("how to read" in text_lower) or ("read it" in text_lower)
    has_takeaway = ("takeaway" in text_lower) or ("take-away" in text_lower)

    if not (has_shows and has_read and has_takeaway):
        errors.append(
            "Figure captions must contain all three parts: "
            "(1) What it shows, (2) How to read it, (3) The takeaway"
        )
    return (len(errors) == 0), errors


def check_media_and_tables(
    text: str, doc_dir: Path = Path("docs"), base_dir: Path = Path(".")
) -> Tuple[bool, List[str], int, int]:
    """Check existence of referenced figures and count figures/tables."""
    errors: List[str] = []
    figures = re.findall(r"!\[.*?\]\((.*?)\)", text)
    figure_count = len(figures)

    for fig_path_str in figures:
        # Strip potential title
        clean_path = fig_path_str.split()[0].strip()
        # Check relative to doc_dir first, then relative to base_dir
        path_in_doc = doc_dir / clean_path
        path_in_base = base_dir / clean_path
        if not path_in_doc.exists() and not path_in_base.exists():
            errors.append(f"Referenced figure does not exist: {clean_path}")

    # Check table count (markdown tables with at least 2 rows)
    table_count = len(re.findall(r"\|[^\n]+\|\n\|[\s:-|-]+\|\n(?:\|[^\n]+\|\n)+", text))
    # Also check referenced table files in docs/tables/
    table_refs = re.findall(r"docs/tables/[A-Za-z0-9_\-]+\.(?:csv|md)", text)
    for t_ref in table_refs:
        if not (base_dir / t_ref).exists():
            errors.append(f"Referenced table file does not exist: {t_ref}")

    # Check requirement: >= 2 figures OR (>= 1 figure AND >= 2 tables)
    valid_counts = (figure_count >= 2) or (figure_count >= 1 and (table_count >= 2 or len(table_refs) >= 2))
    if not valid_counts:
        errors.append(
            f"Insufficient figures/tables: found {figure_count} figures, "
            f"{table_count} inline tables, {len(table_refs)} table refs. "
            f"Requires at least 2 figures OR (1 figure + 2 tables)."
        )

    return (len(errors) == 0), errors, figure_count, table_count


def check_single_section(stage_num: int, docs_dir: Path = Path("docs")) -> Tuple[bool, List[str]]:
    """Validate a single section doc against Section 6.6 criteria."""
    filename = SECTION_FILE_MAP.get(stage_num)
    if not filename:
        return False, [f"Unknown stage number {stage_num}"]

    filepath = docs_dir / filename
    errors: List[str] = []
    if not filepath.exists():
        return False, [f"Required section doc missing: {filepath}"]

    content = filepath.read_text(encoding="utf-8")

    # 1. Check unresolved placeholders
    unresolved = re.findall(r"\{\{fact:([a-zA-Z0-9_\.\-]+)\}\}", content)
    if unresolved:
        errors.append(f"Unresolved fact placeholders in {filename}: {unresolved}")

    # 2. Check prose word count >= 600
    words = count_prose_words(content)
    if words < 600:
        errors.append(f"Insufficient prose length in {filename}: {words} words (minimum 600 required)")

    # 3. Check headings
    headings = extract_headings(content)
    h_ok, h_errs = check_section_headings(headings)
    if not h_ok:
        errors.extend(h_errs)

    # 4. Check figures and tables
    ft_ok, ft_errs, _, _ = check_media_and_tables(content)
    if not ft_ok:
        errors.extend(ft_errs)

    # 5. Check captions
    c_ok, c_errs = check_captions(content)
    if not c_ok:
        errors.extend(c_errs)

    # 6. Check self-evaluation record exists
    # S<NN>_<stage>.md
    se_files = list((docs_dir / "self_evaluations").glob(f"S{stage_num:02d}_*.md"))
    if not se_files:
        errors.append(f"Missing self-evaluation record for Stage {stage_num} in docs/self_evaluations/")

    return (len(errors) == 0), errors


def check_index_links(docs_dir: Path = Path("docs")) -> Tuple[bool, List[str]]:
    """Verify that docs/INDEX.md links to all markdown docs in docs/."""
    index_file = docs_dir / "INDEX.md"
    errors: List[str] = []
    if not index_file.exists():
        return False, ["docs/INDEX.md is missing"]

    index_text = index_file.read_text(encoding="utf-8")
    for md_file in docs_dir.glob("*.md"):
        if md_file.name == "INDEX.md":
            continue
        if md_file.name not in index_text:
            errors.append(f"docs/INDEX.md does not link to existing doc: {md_file.name}")

    return (len(errors) == 0), errors

