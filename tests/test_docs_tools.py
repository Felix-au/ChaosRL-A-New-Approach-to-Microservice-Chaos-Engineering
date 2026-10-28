"""Unit tests for facts registry, docs-build, docs-check, and figure/table helpers."""

import json
from pathlib import Path
import pytest
import matplotlib.pyplot as plt

from chaosrl.docs_tools.facts_registry import (
    register_fact,
    get_fact,
    get_fact_value,
    load_all_facts,
    generate_facts_markdown,
)
from chaosrl.docs_tools.figures_tables import (
    save_figure,
    save_table,
    setup_matplotlib_style,
)
from chaosrl.docs_tools.docs_build import resolve_placeholders_in_text, build_all_docs
from chaosrl.docs_tools.docs_check import count_prose_words, check_single_section


def test_facts_registry(tmp_path, monkeypatch):
    test_facts_file = tmp_path / "facts.json"
    monkeypatch.setattr("chaosrl.docs_tools.facts_registry.FACTS_FILE", test_facts_file)
    monkeypatch.setattr("chaosrl.docs_tools.facts_registry.RESULTS_DIR", tmp_path)

    register_fact("test.metric.throughput", 1420.5, unit="exp/min", source_file="test.py")
    fact = get_fact("test.metric.throughput")
    assert fact is not None
    assert fact["value"] == 1420.5
    assert fact["unit"] == "exp/min"
    assert get_fact_value("test.metric.throughput") == 1420.5
    assert get_fact_value("nonexistent.key", default=42) == 42


def test_placeholder_resolution():
    facts = {
        "scale100.mean": {"value": 85.25},
        "version": {"value": "0.1.0"},
    }
    sample = "At scale 100, the result is {{fact:scale100.mean}}% under v{{fact:version}}."
    resolved, unresolved = resolve_placeholders_in_text(sample, facts)
    assert unresolved == []
    assert "85.25" in resolved
    assert "0.1.0" in resolved

    # Unresolved check
    sample_bad = "Missing {{fact:not_found}} here."
    _, unres = resolve_placeholders_in_text(sample_bad, facts)
    assert unres == ["not_found"]


def test_prose_word_count():
    text = (
        "# Title\n\n"
        "Here is a paragraph of ordinary prose describing the architecture.\n\n"
        "```python\ndef ignore_me():\n    pass\n```\n\n"
        "| Header | Value |\n|---|---|\n| ignore | table |\n\n"
        "And another paragraph with more words."
    )
    words = count_prose_words(text)
    # The code block and table rows are stripped
    assert words > 10
    assert words < 35


def test_figure_table_helpers(tmp_path, monkeypatch):
    monkeypatch.setattr("chaosrl.docs_tools.figures_tables.FIGURES_DIR", tmp_path / "figures")
    monkeypatch.setattr("chaosrl.docs_tools.figures_tables.TABLES_DIR", tmp_path / "tables")
    monkeypatch.setattr("chaosrl.docs_tools.figures_tables.RESULTS_TABLES_DIR", tmp_path / "res_tables")

    setup_matplotlib_style()
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    paths = save_figure(fig, "test_fig")
    assert paths["png"].exists()
    assert paths["svg"].exists()

    data = {"method": ["A", "B"], "score": [0.8, 0.9]}
    t_paths = save_table(data, "test_tbl", highlight_max_cols=["score"])
    assert t_paths["csv_docs"].exists()
    assert t_paths["md_docs"].exists()
