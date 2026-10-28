"""CLI Entrypoint for ChaosRL."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import psutil

from chaosrl.docs_tools.docs_build import build_all_docs
from chaosrl.docs_tools.docs_check import (
    check_index_links,
    check_single_section,
)
from chaosrl.docs_tools.facts_registry import generate_facts_markdown, load_all_facts
from chaosrl.checks.stage_checks import run_stage_check


def update_heartbeat(stage: str, progress: float, eta_sec: float, extra: dict = None) -> None:
    """Write heartbeat status to results/heartbeat.json."""
    heartbeat_path = Path("results/heartbeat.json")
    heartbeat_path.parent.mkdir(parents=True, exist_ok=True)
    mem = psutil.virtual_memory()
    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "progress_percent": progress,
        "eta_seconds": eta_sec,
        "memory_used_gb": round(mem.used / (1024**3), 2),
        "memory_available_gb": round(mem.available / (1024**3), 2),
        "memory_percent": mem.percent,
    }
    if extra:
        data.update(extra)
    with open(heartbeat_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def cmd_check(args: argparse.Namespace) -> int:
    """Run exit criteria checks."""
    if args.stage is not None:
        stages = [args.stage]
    else:
        stages = [1]  # Default or all registered

    overall_pass = True
    for s in stages:
        passed, errors = run_stage_check(s)
        print(f"\n================ Stage {s} Check ================")
        if passed:
            print(f"[PASS] Stage {s} exit criteria verified.")
        else:
            print(f"[FAIL] Stage {s} check failed with {len(errors)} error(s):")
            for err in errors:
                print(f"  - {err}")
            overall_pass = False

    return 0 if overall_pass else 1


def cmd_docs_check(args: argparse.Namespace) -> int:
    """Validate documentation integrity."""
    overall_pass = True
    docs_dir = Path("docs")

    if args.section is not None:
        sections = [args.section]
    else:
        # Check all existing section docs
        sections = []
        for s in range(1, 13):
            filename = f"section{s:02d}_"
            matched = list(docs_dir.glob(f"{filename}*.md"))
            if matched:
                sections.append(s)
        if not sections:
            sections = [1]

    print("\n================ Documentation Check ================")
    for s in sections:
        passed, errors = check_single_section(s, docs_dir=docs_dir)
        sec_name = f"Section {s:02d}"
        if passed:
            print(f"[PASS] {sec_name} meets all documentation standards.")
        else:
            print(f"[FAIL] {sec_name} failed check:")
            for err in errors:
                print(f"  - {err}")
            overall_pass = False

    # Check INDEX.md links
    idx_pass, idx_errs = check_index_links(docs_dir=docs_dir)
    if not idx_pass:
        print("[FAIL] docs/INDEX.md check failed:")
        for err in idx_errs:
            print(f"  - {err}")
        overall_pass = False
    else:
        print("[PASS] docs/INDEX.md links verified.")

    return 0 if overall_pass else 1


def cmd_docs_build(args: argparse.Namespace) -> int:
    """Build docs from facts registry."""
    print("Building documentation from facts registry...")
    report = build_all_docs()
    if report:
        print("Notice: Unresolved placeholders detected:")
        for doc, missing in report.items():
            print(f"  {doc}: {missing}")
    print("Regenerated docs/FACTS.md and updated placeholders.")
    return 0


def cmd_heartbeat(args: argparse.Namespace) -> int:
    """Update heartbeat."""
    update_heartbeat(args.stage or "idle", args.progress or 0.0, args.eta or 0.0)
    print("Heartbeat updated.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="chaosrl", description="ChaosRL Engine")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # check
    p_check = subparsers.add_parser("check", help="Run stage exit criteria check")
    p_check.add_argument("--stage", type=int, help="Stage number (1..11)")
    p_check.add_argument("--all", action="store_true", help="Check all stages")
    p_check.set_defaults(func=cmd_check)

    # docs-check
    p_docs_check = subparsers.add_parser("docs-check", help="Validate documentation integrity")
    p_docs_check.add_argument("--section", type=int, help="Section number (1..12)")
    p_docs_check.add_argument("--all", action="store_true", help="Check all sections")
    p_docs_check.set_defaults(func=cmd_docs_check)

    # docs-build
    p_docs_build = subparsers.add_parser("docs-build", help="Build docs and resolve facts")
    p_docs_build.set_defaults(func=cmd_docs_build)

    # heartbeat
    p_hb = subparsers.add_parser("heartbeat", help="Update heartbeat file")
    p_hb.add_argument("--stage", type=str, default="idle")
    p_hb.add_argument("--progress", type=float, default=0.0)
    p_hb.add_argument("--eta", type=float, default=0.0)
    p_hb.set_defaults(func=cmd_heartbeat)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    ret = args.func(args)
    sys.exit(ret)


if __name__ == "__main__":
    main()

