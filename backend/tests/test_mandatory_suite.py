"""
Mandatory Acceptance Tests for SIH 2026 Core AI Engine.
Specifically validates all 6 non-negotiable test cases mandated in master prompt.
"""

import pytest
from app.services.matching_service import MatchingService
from app.utils.units import convert_length, are_dimensions_equivalent
from app.utils.text import expand_abbreviations, normalize_description
from app.ai.attribute_extraction import extract_attributes
from app.ai.technical_rules import SEVERITY_CRITICAL


def test_mandatory_test_1_true_match():
    """
    TEST 1:
    CS PIPE 10 INCH SCH40
    vs
    CARBON STEEL PIPE 10 IN SCHEDULE 40

    Expected:
    HIGH similarity
    No critical conflict
    Candidate for human review / merge
    """
    desc1 = "CS PIPE 10 INCH SCH40"
    desc2 = "CARBON STEEL PIPE 10 IN SCHEDULE 40"

    result = MatchingService.compare_pair(desc1, desc2)

    # 1. High similarity across scores
    assert result["scores"]["fuzzy"] >= 0.80, f"Expected high fuzzy similarity, got {result['scores']['fuzzy']}"
    assert result["scores"]["final"] >= 0.80, f"Expected high final similarity, got {result['scores']['final']}"

    # 2. No critical conflicts
    critical_conflicts = [c for c in result["technical_conflicts"] if c["severity"] == SEVERITY_CRITICAL]
    assert len(critical_conflicts) == 0, f"Expected zero critical conflicts, found: {critical_conflicts}"

    # 3. Valid classification
    assert result["classification"] in ("IDENTICAL", "NEAR_DUPLICATE"), (
        f"Expected IDENTICAL or NEAR_DUPLICATE, got {result['classification']}"
    )


def test_mandatory_test_2_critical_near_miss():
    """
    TEST 2 (ABSOLUTE CRITICAL TEST):
    SS304 VALVE 4 INCH 150#
    vs
    SS316 VALVE 4 INCH 150#

    Expected:
    HIGH similarity (semantic & fuzzy)
    CRITICAL grade conflict (SS304 != SS316)
    review_required = true
    recommendation = DO_NOT_AUTO_MERGE
    classification MUST NOT automatically become: IDENTICAL
    """
    desc1 = "SS304 VALVE 4 INCH 150#"
    desc2 = "SS316 VALVE 4 INCH 150#"

    result = MatchingService.compare_pair(desc1, desc2)

    # High similarity expected on size, pressure, equipment type
    assert result["scores"]["semantic"] >= 0.70 or result["scores"]["fuzzy"] >= 0.70

    # Critical grade conflict MUST be detected
    critical_conflicts = [c for c in result["technical_conflicts"] if c["severity"] == SEVERITY_CRITICAL]
    assert len(critical_conflicts) > 0, "No critical conflicts detected!"

    grade_conflict = next((c for c in critical_conflicts if c["attribute"] == "grade"), None)
    assert grade_conflict is not None, "Grade conflict was not identified as critical conflict!"
    assert "304" in str(grade_conflict["source_value"])
    assert "316" in str(grade_conflict["target_value"])

    # Classification and recommendation checks
    assert result["review_required"] is True, "review_required must be True"
    assert result["recommendation"] == "DO_NOT_AUTO_MERGE", (
        f"Expected recommendation 'DO_NOT_AUTO_MERGE', got '{result['recommendation']}'"
    )
    assert result["classification"] != "IDENTICAL", (
        "CRITICAL ERROR: High score caused critical grade conflict to be classified as IDENTICAL!"
    )
    assert result["classification"] == "REVIEW_REQUIRED", (
        f"Expected classification 'REVIEW_REQUIRED', got '{result['classification']}'"
    )


def test_mandatory_test_3_unit_equivalence():
    """
    TEST 3:
    10 INCH
    vs
    254 MM

    Expected:
    Equivalent dimension
    """
    val1, unit1, _ = convert_length(10.0, "inch")
    val2, unit2, _ = convert_length(254.0, "mm")

    assert val1 == 254.0, f"Expected 10 inch -> 254.0 mm, got {val1}"
    assert val2 == 254.0, f"Expected 254.0 mm, got {val2}"
    assert are_dimensions_equivalent(val1, val2), "10 inch and 254 mm should be recognized as equivalent dimensions"


def test_mandatory_test_4_abbreviation_equivalence():
    """
    TEST 4:
    SS
    vs
    STAINLESS STEEL

    Expected:
    Equivalent material
    """
    expanded = expand_abbreviations("SS")
    assert expanded == "STAINLESS STEEL", f"Expected 'STAINLESS STEEL', got '{expanded}'"

    norm_a = normalize_description("SS BOLT")
    norm_b = normalize_description("STAINLESS STEEL BOLT")
    assert norm_a == norm_b, f"Normalized descriptions must match: '{norm_a}' vs '{norm_b}'"


def test_mandatory_test_5_completely_unrelated():
    """
    TEST 5:
    Completely unrelated materials (e.g. Pipe vs Electrical Cable)

    Expected:
    DIFFERENT
    """
    desc1 = "CS SEAMLESS PIPE 10 INCH SCH 40 ASTM A106"
    desc2 = "XLPE ARMOURED CABLE 4C X 16 SQ MM 1.1KV COPPER"

    result = MatchingService.compare_pair(desc1, desc2)

    assert result["classification"] == "DIFFERENT", (
        f"Expected classification 'DIFFERENT', got '{result['classification']}'"
    )
    assert result["scores"]["final"] < 0.60, (
        f"Expected low final similarity (< 0.60), got {result['scores']['final']}"
    )


def test_mandatory_test_6_missing_specification():
    """
    TEST 6:
    Missing grade / specification

    Expected:
    Do not invent value.
    Return:
    UNKNOWN or REVIEW_REQUIRED
    """
    desc = "VALVE 4 INCH"
    dna = extract_attributes(desc)

    # Must NOT invent missing attributes
    assert dna["grade"] is None, f"Grade should be None when not present, got '{dna['grade']}'"
    assert dna["pressure"] is None, f"Pressure should be None when not present, got '{dna['pressure']}'"
    assert dna["material"] is None, f"Material should be None when not present, got '{dna['material']}'"

    # When compared against a fully specified valve:
    specified_valve = "SS304 VALVE 4 INCH 150#"
    result = MatchingService.compare_pair(desc, specified_valve)

    # Ambiguity must result in review required or missing attribute flagged
    assert result["attribute_matrix"].get("grade") == "UNKNOWN"
    assert result["review_required"] is True, "Ambiguous missing specification must require human review"
