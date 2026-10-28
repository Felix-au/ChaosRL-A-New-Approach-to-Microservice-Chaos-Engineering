"""Parser and empirical effect extractor for RCAEval microservice data."""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

logger = logging.getLogger("chaosrl.data.parse")

DATA_RAW_DIR = Path("data_raw")
RCAEVAL_DIR = DATA_RAW_DIR / "rcaeval"
RESULTS_CALIB_DIR = Path("results/calibration")


def parse_case_directory(case_dir: Path) -> Optional[Dict[str, Any]]:
    """Parse a single fault injection case directory (data.csv + inject_time.txt)."""
    inject_file = case_dir / "inject_time.txt"
    data_file = case_dir / "data.csv"

    if not inject_file.exists() or not data_file.exists():
        return None

    try:
        inject_time = float(inject_file.read_text(encoding="utf-8").strip())
    except Exception:
        return None

    # Parse parent folder names: e.g. .../adservice_cpu/1
    run_id = case_dir.name
    fault_folder = case_dir.parent.name
    # system is parent of fault_folder or grandparent
    # E.g. RE1-OB/RE1-OB/adservice_cpu -> system is Online Boutique
    system_dir = case_dir.parent.parent.name
    system_name = "Online Boutique" if "OB" in system_dir else ("Sock Shop" if "SS" in system_dir else "Train Ticket")

    # Split fault folder: <service>_<fault_type>
    parts = fault_folder.rsplit("_", 1)
    if len(parts) != 2:
        return None
    service_name, fault_type = parts[0], parts[1].lower()

    # Read CSV
    rows = []
    headers = []
    with open(data_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            return None
        for r in reader:
            if r:
                try:
                    rows.append([float(x) if x != "" else 0.0 for x in r])
                except ValueError:
                    continue

    if not rows or len(rows) < 10:
        return None

    time_idx = 0
    # Determine columns for target service
    target_cpu_idx = -1
    target_latency_idx = -1
    target_error_idx = -1
    frontend_latency_idx = -1
    frontend_error_idx = -1

    for idx, h in enumerate(headers):
        hl = h.lower()
        if f"{service_name.lower()}_cpu" in hl:
            target_cpu_idx = idx
        elif f"{service_name.lower()}_latency" in hl:
            target_latency_idx = idx
        elif f"{service_name.lower()}_error" in hl:
            target_error_idx = idx
        elif "frontend_latency" in hl:
            frontend_latency_idx = idx
        elif "frontend_error" in hl:
            frontend_error_idx = idx

    timestamps = np.array([r[time_idx] for r in rows])

    # Windows: pre-injection [-120s, 0s], post-injection [0s, +180s]
    pre_mask = (timestamps >= inject_time - 120) & (timestamps < inject_time)
    post_mask = (timestamps >= inject_time) & (timestamps <= inject_time + 180)

    if np.sum(pre_mask) < 3 or np.sum(post_mask) < 3:
        # Fallback to median split
        split_idx = len(rows) // 2
        pre_rows = rows[:split_idx]
        post_rows = rows[split_idx:]
    else:
        pre_rows = [rows[i] for i in range(len(rows)) if pre_mask[i]]
        post_rows = [rows[i] for i in range(len(rows)) if post_mask[i]]

    def get_mean(rows_sub, col_idx):
        if col_idx == -1 or not rows_sub:
            return 0.0
        vals = [r[col_idx] for r in rows_sub if len(r) > col_idx]
        return float(np.mean(vals)) if vals else 0.0

    pre_cpu = get_mean(pre_rows, target_cpu_idx)
    post_cpu = get_mean(post_rows, target_cpu_idx)
    cpu_delta = max(0.0, post_cpu - pre_cpu)

    pre_lat = get_mean(pre_rows, target_latency_idx)
    post_lat = get_mean(post_rows, target_latency_idx)
    lat_ratio = (post_lat / (pre_lat + 1e-6)) if pre_lat > 0 else 1.0

    pre_err = get_mean(pre_rows, target_error_idx)
    post_err = get_mean(post_rows, target_error_idx)
    err_delta = max(0.0, post_err - pre_err)

    # Ingress gateway impact (frontend)
    pre_gw_lat = get_mean(pre_rows, frontend_latency_idx)
    post_gw_lat = get_mean(post_rows, frontend_latency_idx)
    gw_lat_ratio = (post_gw_lat / (pre_gw_lat + 1e-6)) if pre_gw_lat > 0 else 1.0

    return {
        "system": system_name,
        "service": service_name,
        "fault_type": fault_type,
        "run_id": run_id,
        "inject_time": inject_time,
        "row_count": len(rows),
        "pre_cpu": round(pre_cpu, 2),
        "post_cpu": round(post_cpu, 2),
        "cpu_delta": round(cpu_delta, 2),
        "pre_latency_s": round(pre_lat, 4),
        "post_latency_s": round(post_lat, 4),
        "latency_ratio": round(lat_ratio, 2),
        "error_delta": round(err_delta, 4),
        "gateway_latency_ratio": round(gw_lat_ratio, 2),
    }


def parse_all_rcaeval_cases(rcaeval_root: Path = RCAEVAL_DIR) -> Dict[str, Any]:
    """Scan and parse all cases across all extracted subsets."""
    RESULTS_CALIB_DIR.mkdir(parents=True, exist_ok=True)
    cases = []
    case_dirs = list(rcaeval_root.rglob("inject_time.txt"))

    for p in case_dirs:
        case_res = parse_case_directory(p.parent)
        if case_res:
            cases.append(case_res)

    # Save parsed cases
    parsed_json_path = DATA_RAW_DIR / "parsed_cases.json"
    with open(parsed_json_path, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=2)

    # Aggregate by fault type
    fault_stats: Dict[str, dict] = {}
    fault_types = sorted(list(set(c["fault_type"] for c in cases)))

    for ft in fault_types:
        sub = [c for c in cases if c["fault_type"] == ft]
        lat_ratios = [c["latency_ratio"] for c in sub]
        cpu_deltas = [c["cpu_delta"] for c in sub]
        gw_lat_ratios = [c["gateway_latency_ratio"] for c in sub]

        fault_stats[ft] = {
            "case_count": len(sub),
            "systems": list(set(c["system"] for c in sub)),
            "latency_ratio_mean": float(np.mean(lat_ratios)),
            "latency_ratio_p50": float(np.median(lat_ratios)),
            "latency_ratio_p90": float(np.percentile(lat_ratios, 90)),
            "latency_ratio_std": float(np.std(lat_ratios)),
            "cpu_delta_mean": float(np.mean(cpu_deltas)),
            "cpu_delta_p50": float(np.median(cpu_deltas)),
            "cpu_delta_p90": float(np.percentile(cpu_deltas, 90)),
            "gw_latency_ratio_mean": float(np.mean(gw_lat_ratios)),
        }

    summary = {
        "total_cases_parsed": len(cases),
        "fault_types_covered": fault_types,
        "systems_covered": list(set(c["system"] for c in cases)),
        "fault_statistics": fault_stats,
    }

    summary_file = RESULTS_CALIB_DIR / "calibration_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary

