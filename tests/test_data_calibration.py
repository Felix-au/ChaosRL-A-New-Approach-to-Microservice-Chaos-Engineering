"""Tests for empirical data parsing, distribution fitting, and calibration."""

import json
from pathlib import Path
import pytest
import numpy as np

from chaosrl.data.calibrate import load_parsed_cases, fit_fault_distributions


def test_parsed_cases_integrity():
    parsed_path = Path("data_raw/parsed_cases.json")
    assert parsed_path.exists(), "parsed_cases.json must exist"
    with open(parsed_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    assert len(cases) >= 100, f"Expected at least 100 parsed cases, found {len(cases)}"
    fault_types = set(c["fault_type"] for c in cases)
    for expected_ft in ["cpu", "delay", "disk", "loss", "mem"]:
        assert expected_ft in fault_types, f"Missing fault type: {expected_ft}"

    # Verify invariants: no negative latencies, reasonable values
    for c in cases:
        assert c["pre_latency_s"] >= 0.0, "Pre-latency must be non-negative"
        assert c["post_latency_s"] >= 0.0, "Post-latency must be non-negative"
        assert c["latency_ratio"] >= 0.0, "Latency ratio must be non-negative"
        assert c["cpu_delta"] >= 0.0, "CPU delta must be non-negative"


def test_calibration_fitting():
    res = fit_fault_distributions()
    assert "fitted_params" in res
    assert "mean_held_out_wasserstein" in res
    assert res["mean_held_out_wasserstein"] >= 0.0
    for ft in ["cpu", "delay", "loss", "mem", "disk"]:
        assert ft in res["fitted_params"]
