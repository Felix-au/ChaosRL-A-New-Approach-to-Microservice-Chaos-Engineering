"""Unit tests for ChaosRL CLI commands."""

from __future__ import annotations

import json
from pathlib import Path
import pytest
from chaosrl.cli import build_parser, cmd_check, cmd_docs_check, cmd_heartbeat, cmd_quick


def test_cli_heartbeat(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    parser = build_parser()
    args = parser.parse_args(["heartbeat", "--stage", "testing", "--progress", "50.0", "--eta", "120.0"])
    assert args.stage == "testing"
    assert args.progress == 50.0
    assert args.eta == 120.0
    ret = cmd_heartbeat(args)
    assert ret == 0
    hb = Path("results/heartbeat.json")
    assert hb.exists()
    with open(hb, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["stage"] == "testing"
    assert data["progress_percent"] == 50.0


def test_cli_check_stage1() -> None:
    parser = build_parser()
    args = parser.parse_args(["check", "--stage", "1"])
    ret = cmd_check(args)
    assert ret == 0


def test_cli_docs_check_section1() -> None:
    parser = build_parser()
    args = parser.parse_args(["docs-check", "--section", "1"])
    ret = cmd_docs_check(args)
    assert ret == 0


def test_cli_quick() -> None:
    parser = build_parser()
    args = parser.parse_args(["quick"])
    ret = cmd_quick(args)
    assert ret == 0

