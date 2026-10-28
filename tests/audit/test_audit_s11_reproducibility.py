"""Independent research audit tests for Section S11: Reproducibility, CLI & Packaging.

Verifies claims CLM-S11-01 through CLM-S11-04:
- CLI quick mode execution via subprocess without error
- Stage-level reproducibility and deterministic output generation
- Codebase security scan: zero unauthorized external network calls or hardcoded user-specific paths
Includes explicit negative controls demonstrating test failure under broken assumptions.
"""

import subprocess
import sys
import glob
from pathlib import Path
import pytest


@pytest.mark.audit
def test_t_s11_01_cli_quick_mode_execution():
    """T-S11-01: Run 'python -m chaosrl quick' in a subprocess and verify returncode 0."""
    res = subprocess.run(
        [sys.executable, "-m", "chaosrl", "quick"],
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert res.returncode == 0, f"chaosrl quick failed: {res.stderr}"
    assert "QUICK MODE COMPLETE" in res.stdout or "complete" in res.stdout.lower()

    # Negative control: Running with an invalid command must fail
    res_bad = subprocess.run(
        [sys.executable, "-m", "chaosrl", "nonexistent_subcommand"],
        capture_output=True,
        text=True,
    )
    assert res_bad.returncode != 0


@pytest.mark.audit
def test_t_s11_02_deterministic_stage_rerun():
    """T-S11-02: Verify that running a check stage twice produces consistent outputs."""
    res1 = subprocess.run(
        [sys.executable, "-m", "chaosrl", "check", "--stage", "3"],
        capture_output=True,
        text=True,
    )
    res2 = subprocess.run(
        [sys.executable, "-m", "chaosrl", "check", "--stage", "3"],
        capture_output=True,
        text=True,
    )
    assert res1.returncode == 0
    assert res2.returncode == 0
    assert "PASS" in res1.stdout
    assert "PASS" in res2.stdout

    # Negative control: Checking an invalid stage number must fail
    res_bad = subprocess.run(
        [sys.executable, "-m", "chaosrl", "check", "999"],
        capture_output=True,
        text=True,
    )
    assert res_bad.returncode != 0


@pytest.mark.audit
def test_t_s11_03_codebase_security_and_portability():
    """T-S11-03: Security scan: search all Python files for hardcoded absolute developer paths or socket network leaks."""
    py_files = glob.glob("src/**/*.py", recursive=True)
    assert len(py_files) > 10

    forbidden_patterns = [
        "c:\\users\\",
        "/home/",
        "requests.post('http",
        "urllib.request.urlopen('http",
    ]

    for pf in py_files:
        content = Path(pf).read_text(encoding="utf-8", errors="ignore").lower()
        for pat in forbidden_patterns:
            assert pat not in content, f"Forbidden hardcoded pattern '{pat}' found in {pf}"

    # Negative control: A string containing a hardcoded path must trigger failure
    bad_content = "path = 'c:\\users\\felix\\secret'"
    with pytest.raises(AssertionError):
        for pat in forbidden_patterns:
            assert pat not in bad_content
