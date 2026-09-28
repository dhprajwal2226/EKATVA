"""
Tests for Hybrid Matching, Technical Conflict Engine, and Explainability.
SIH 2026 - National Material Master Platform.
"""

import pytest
from app.services.matching_service import MatchingService
from app.ai.technical_rules import SEVERITY_CRITICAL, SEVERITY_MAJOR


def test_pressure_conflict():
    """Verify different pressure ratings trigger critical conflict."""
    desc1 = "CS GATE VALVE 6 INCH 150# WCB"
    desc2 = "CS GATE VALVE 6 INCH 300# WCB"

    result = MatchingService.compare_pair(desc1, desc2)

    crit_conflicts = [c for c in result["technical_conflicts"] if c["severity"] == SEVERITY_CRITICAL]
    assert any(c["attribute"] == "pressure" for c in crit_conflicts)
    assert result["review_required"] is True
    assert result["recommendation"] == "DO_NOT_AUTO_MERGE"


def test_schedule_difference():
    """Verify schedule mismatch between SCH 40 and SCH 80 is detected."""
    desc1 = "CS PIPE 6 INCH SCH 40 ASTM A106"
    desc2 = "CS PIPE 6 INCH SCH 80 ASTM A106"

    result = MatchingService.compare_pair(desc1, desc2)

    schedule_conflicts = [c for c in result["technical_conflicts"] if c["attribute"] == "schedule"]
    assert len(schedule_conflicts) > 0
    assert result["classification"] in ("FUNCTIONALLY_EQUIVALENT", "REVIEW_REQUIRED")


def test_diameter_critical_difference():
    """Verify large dimensional discrepancy triggers critical conflict."""
    desc1 = "CS PIPE 6 INCH SCH 40"
    desc2 = "CS PIPE 10 INCH SCH 40"

    result = MatchingService.compare_pair(desc1, desc2)

    dia_conflicts = [c for c in result["technical_conflicts"] if c["attribute"] == "diameter"]
    assert len(dia_conflicts) > 0
    assert dia_conflicts[0]["severity"] == SEVERITY_CRITICAL


def test_explainable_match_structure():
    """Verify explainable match contains grounded, non-empty reasons."""
    desc1 = "SS304 VALVE 4 INCH 150#"
    desc2 = "SS316 VALVE 4 INCH 150#"

    result = MatchingService.compare_pair(desc1, desc2)
    expl = result["explanation"]

    assert "why_matched" in expl and len(expl["why_matched"]) > 0
    assert "what_matched" in expl and len(expl["what_matched"]) > 0
    assert "what_differed" in expl and len(expl["what_differed"]) > 0
    assert expl["recommendation"] == "DO_NOT_AUTO_MERGE"
    assert expl["review_required"] is True
