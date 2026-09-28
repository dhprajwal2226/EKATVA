"""
Tests for Text Normalization, Separators, Abbreviations, and Units.
SIH 2026 - National Material Master Platform.
"""

import pytest
from app.utils.text import (
    normalize_description,
    normalize_separators,
    expand_abbreviations,
    DOMAIN_ABBREVIATIONS,
)
from app.utils.units import (
    convert_length,
    convert_pressure,
    are_dimensions_equivalent,
    parse_dimension_string,
)


def test_separator_standardization():
    """Verify multiplication characters are harmonized to 'X'."""
    assert normalize_separators("M16*50") == "M16 X 50"
    assert normalize_separators("M16 × 50") == "M16 X 50"
    assert normalize_separators("M16x50") == "M16 X 50"
    assert normalize_separators("M16 X 50") == "M16 X 50"
    assert normalize_separators("50 by 10") == "50 X 10"


def test_domain_abbreviation_expansion():
    """Verify abbreviation dictionary expands on word boundaries without corrupting non-target words."""
    # Boundary check: 'ASSIST' should not expand 'SS'
    assert expand_abbreviations("ASSIST") == "ASSIST"

    # Known abbreviations
    assert expand_abbreviations("CS PIPE") == "CARBON STEEL PIPE"
    assert expand_abbreviations("MS PLATE") == "MILD STEEL PLATE"
    assert expand_abbreviations("GI PIPE") == "GALVANIZED IRON PIPE"
    assert expand_abbreviations("CI VALVE") == "CAST IRON VALVE"
    assert expand_abbreviations("DI PIPE") == "DUCTILE IRON PIPE"
    assert expand_abbreviations("SCH 40") == "SCHEDULE 40"
    assert expand_abbreviations("10 MM THK") == "10 MM THICKNESS"


def test_full_normalization_pipeline():
    """Verify full string normalization."""
    raw = "  cs   seamless   pipe 10\" sch40  "
    norm = normalize_description(raw)
    assert "CARBON STEEL" in norm
    assert "SEAMLESS" in norm
    assert "SCHEDULE 40" in norm


def test_unit_conversions():
    """Test deterministic metric conversions."""
    # Inches to mm
    v, u, amb = convert_length(10, "inch")
    assert v == 254.0
    assert u == "mm"
    assert not amb

    # Feet to mm
    v, u, amb = convert_length(1, "ft")
    assert v == 304.8
    assert u == "mm"

    # Meter to mm
    v, u, amb = convert_length(6, "m")
    assert v == 6000.0
    assert u == "mm"

    # Ambiguous unit
    v, u, amb = convert_length(10, "unknown_unit")
    assert amb is True


def test_pressure_conversion():
    """Test pressure conversion to bar."""
    v, u, amb = convert_pressure(100, "psi")
    assert round(v, 2) == 6.89
    assert u == "bar"
    assert not amb


def test_dimension_equivalence():
    """Test engineering tolerances in dimensional comparisons."""
    assert are_dimensions_equivalent(254.0, 254.0)
    assert are_dimensions_equivalent(254.0, 253.5)  # within 2%
    assert not are_dimensions_equivalent(254.0, 300.0)
