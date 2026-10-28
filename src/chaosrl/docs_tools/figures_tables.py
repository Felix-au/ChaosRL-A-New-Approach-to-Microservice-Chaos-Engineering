"""Figure and table generation helpers for ChaosRL."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List, Sequence, Union

import matplotlib.pyplot as plt

FIGURES_DIR = Path("docs/figures")
TABLES_DIR = Path("docs/tables")
RESULTS_TABLES_DIR = Path("results/tables")

# Colorblind-safe palette (Wong 2011 / Okabe-Ito)
CB_PALETTE = {
    "black": "#000000",
    "orange": "#E69F00",
    "sky_blue": "#56B4E9",
    "bluish_green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermilion": "#D55E00",
    "reddish_purple": "#CC79A7",
    "gray": "#7F7F7F",
}

METHOD_COLORS = {
    "chaos_monkey": CB_PALETTE["gray"],
    "chaos_monkey_2": CB_PALETTE["yellow"],
    "random_all": CB_PALETTE["orange"],
    "round_robin": CB_PALETTE["sky_blue"],
    "bandit_ucb": CB_PALETTE["reddish_purple"],
    "heuristic": CB_PALETTE["vermilion"],
    "oracle": CB_PALETTE["black"],
    "c01_ppo_mlp": CB_PALETTE["blue"],
    "c02_ppo_gnn": CB_PALETTE["bluish_green"],
    "chaosrl_top1": CB_PALETTE["blue"],
    "ensemble_e1": CB_PALETTE["bluish_green"],
    "ensemble_e2": CB_PALETTE["vermilion"],
    "ensemble_e3": "#8B008B",
}


def setup_matplotlib_style() -> None:
    """Set publication-grade, accessible matplotlib defaults."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "legend.fontsize": 9,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "figure.autolayout": True,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linestyle": "--",
    })


def save_figure(fig: plt.Figure, base_name: str, dpi: int = 200) -> Dict[str, Path]:
    """Save figure as both PNG (at specified DPI) and SVG."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    png_path = FIGURES_DIR / f"{base_name}.png"
    svg_path = FIGURES_DIR / f"{base_name}.svg"

    fig.savefig(png_path, dpi=dpi, bbox_inches="tight")
    fig.savefig(svg_path, format="svg", bbox_inches="tight")
    plt.close(fig)
    return {"png": png_path, "svg": svg_path}


def _normalize_table_data(data: Any) -> Tuple[List[str], List[List[Any]]]:
    """Normalize input into headers and rows of values."""
    # Check if pandas DataFrame (by class name to avoid hard import error)
    if hasattr(data, "columns") and hasattr(data, "values"):
        headers = [str(c) for c in data.columns]
        rows = [list(r) for r in data.values]
        return headers, rows

    if isinstance(data, dict):
        # Dict of lists: {"col1": [1, 2], "col2": [3, 4]}
        headers = list(data.keys())
        num_rows = len(next(iter(data.values()))) if data else 0
        rows = []
        for i in range(num_rows):
            rows.append([data[h][i] for h in headers])
        return headers, rows

    if isinstance(data, list) and data and isinstance(data[0], dict):
        # List of dicts: [{"col1": 1, "col2": 3}, ...]
        headers = list(data[0].keys())
        rows = []
        for item in data:
            rows.append([item.get(h, "") for h in headers])
        return headers, rows

    if isinstance(data, (list, tuple)) and data and isinstance(data[0], (list, tuple)):
        # List of rows with first row as header or separate
        headers = [f"col_{i}" for i in range(len(data[0]))]
        rows = [list(r) for r in data]
        return headers, rows

    return [], []


def save_table(
    data: Any,
    base_name: str,
    highlight_max_cols: Sequence[str] = (),
    highlight_min_cols: Sequence[str] = (),
) -> Dict[str, Path]:
    """Save tabular data as CSV and Markdown table in docs/tables/ and results/tables/."""
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_TABLES_DIR.mkdir(parents=True, exist_ok=True)

    csv_path_docs = TABLES_DIR / f"{base_name}.csv"
    csv_path_results = RESULTS_TABLES_DIR / f"{base_name}.csv"
    md_path_docs = TABLES_DIR / f"{base_name}.md"

    headers, rows = _normalize_table_data(data)

    # Write CSVs
    for p in [csv_path_docs, csv_path_results]:
        with open(p, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if headers:
                writer.writerow(headers)
            for r in rows:
                writer.writerow(r)

    # Format Markdown
    # Find max/min for highlighted cols
    max_vals = {}
    min_vals = {}
    for col_name in highlight_max_cols:
        if col_name in headers:
            idx = headers.index(col_name)
            numeric_vals = [r[idx] for r in rows if isinstance(r[idx], (int, float))]
            if numeric_vals:
                max_vals[col_name] = max(numeric_vals)

    for col_name in highlight_min_cols:
        if col_name in headers:
            idx = headers.index(col_name)
            numeric_vals = [r[idx] for r in rows if isinstance(r[idx], (int, float))]
            if numeric_vals:
                min_vals[col_name] = min(numeric_vals)

    md_lines = [f"<!-- Table: {base_name} -->", ""]
    if headers:
        md_lines.append("| " + " | ".join(headers) + " |")
        md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for r in rows:
            formatted_cells = []
            for col_idx, cell in enumerate(r):
                col_name = headers[col_idx]
                if isinstance(cell, float):
                    cell_str = f"{cell:.4f}" if abs(cell) < 1000 else f"{cell:.2f}"
                else:
                    cell_str = str(cell)

                if col_name in max_vals and isinstance(cell, (int, float)) and abs(cell - max_vals[col_name]) < 1e-9:
                    cell_str = f"**{cell_str}**"
                elif col_name in min_vals and isinstance(cell, (int, float)) and abs(cell - min_vals[col_name]) < 1e-9:
                    cell_str = f"**{cell_str}**"
                formatted_cells.append(cell_str)
            md_lines.append("| " + " | ".join(formatted_cells) + " |")
    md_lines.append("")

    with open(md_path_docs, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    return {
        "csv_docs": csv_path_docs,
        "csv_results": csv_path_results,
        "md_docs": md_path_docs,
    }
