"""Documentation builder for ChaosRL.

Replaces {{fact:<key>}} placeholders with real numbers from results/facts.json
and regenerates docs/FACTS.md.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

from chaosrl.docs_tools.facts_registry import (
    generate_facts_markdown,
    load_all_facts,
)

FACT_PATTERN = re.compile(r"\{\{fact:([a-zA-Z0-9_\.\-]+)\}\}")


def resolve_placeholders_in_text(text: str, facts: Dict[str, dict]) -> Tuple[str, List[str]]:
    """Replace {{fact:key}} placeholders in text with actual values."""
    unresolved: List[str] = []

    def replace_match(match: re.Match) -> str:
        key = match.group(1)
        if key in facts:
            val = facts[key]["value"]
            if isinstance(val, float):
                return f"{val:.4f}" if abs(val) < 1000 else f"{val:.2f}"
            return str(val)
        unresolved.append(key)
        return match.group(0)

    resolved_text = FACT_PATTERN.sub(replace_match, text)
    return resolved_text, unresolved


def build_all_docs(docs_dir: Path = Path("docs")) -> Dict[str, List[str]]:
    """Scan docs directory and REPORT.md, resolve placeholders and rebuild FACTS.md."""
    facts = load_all_facts()
    generate_facts_markdown()

    md_files = list(docs_dir.rglob("*.md"))
    report_file = Path("REPORT.md")
    if report_file.exists():
        md_files.append(report_file)

    report: Dict[str, List[str]] = {}
    for md_file in md_files:
        if md_file.name == "FACTS.md":
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue
        new_content, unresolved = resolve_placeholders_in_text(content, facts)
        if unresolved:
            report[str(md_file)] = unresolved
        if new_content != content:
            md_file.write_text(new_content, encoding="utf-8")

    return report

