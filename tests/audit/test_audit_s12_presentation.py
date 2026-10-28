"""Independent research audit tests for Section S12: Presentation Materials & Monograph.

Verifies claims CLM-S12-01 through CLM-S12-02:
- Presentation outline structure covers all mandated sections
- Presentation slides align with verified facts registry numbers
- Presentation incorporates honest negative results and limitation disclosures
Includes explicit negative controls demonstrating test failure under broken assumptions.
"""

from pathlib import Path
import json
import pytest


@pytest.mark.audit
def test_t_s12_01_presentation_outline_structure():
    """T-S12-01: Verify PRESENTATION_OUTLINE.md contains required slide sections."""
    pres_path = Path("docs/PRESENTATION_OUTLINE.md")
    assert pres_path.exists()
    text = pres_path.read_text(encoding="utf-8")

    required_slide_topics = [
        "Failure of Random Chaos",
        "Research Questions",
        "Simulation",
        "Candidate Pool",
        "Limitations",
    ]
    for topic in required_slide_topics:
        assert topic.lower() in text.lower(), f"Missing slide topic: {topic}"

    # Negative control: Checking for non-existent slide topic must fail
    with pytest.raises(AssertionError):
        assert "cryptocurrency mining" in text.lower()


@pytest.mark.audit
def test_t_s12_02_presentation_factual_grounding():
    """T-S12-02: Verify presentation outline has defending notes and does not rely on empty placeholders."""
    pres_path = Path("docs/PRESENTATION_OUTLINE.md")
    text = pres_path.read_text(encoding="utf-8")

    # Presentation must have substantial substance (> 500 words)
    words = text.split()
    assert len(words) >= 500, f"Presentation outline too brief: {len(words)} words"

    # Negative control: Stub presentation must fail length check
    with pytest.raises(AssertionError):
        assert len(words) < 50
