"""
Unit Normalization Engine.
Deterministic conversions for length, diameter, thickness, and pressure.
SIH 2026 - National Material Master Platform.
"""

import re
from typing import Optional, Tuple, Dict, Any

# Deterministic linear conversion factors to standard SI (length -> mm, pressure -> bar)
LENGTH_CONVERSIONS: Dict[str, float] = {
    "mm": 1.0,
    "millimeter": 1.0,
    "millimeters": 1.0,
    "cm": 10.0,
    "centimeter": 10.0,
    "centimeters": 10.0,
    "m": 1000.0,
    "meter": 1000.0,
    "meters": 1000.0,
    "mtr": 1000.0,
    "in": 25.4,
    "inch": 25.4,
    "inches": 25.4,
    '"': 25.4,
    "”": 25.4,
    "ft": 304.8,
    "feet": 304.8,
    "foot": 304.8,
    "'": 304.8,
    "’": 304.8,
}

PRESSURE_CONVERSIONS: Dict[str, float] = {
    "bar": 1.0,
    "mbar": 0.001,
    "psi": 0.0689476,
    "kg/cm2": 0.980665,
    "kg/cm^2": 0.980665,
    "mpa": 10.0,
    "kpa": 0.01,
}

# Regex to detect dimension with unit
_DIMENSION_REGEX = re.compile(
    r"(\d+(?:\.\d+)?)\s*(mm|cm|m|mtr|inch|inches|in|\"|”|ft|feet|foot|'|’)\b",
    re.IGNORECASE,
)

# Regex to detect pressure ratings
_PRESSURE_REGEX = re.compile(
    r"(\d+(?:\.\d+)?)\s*(bar|psi|kg/cm2|kg/cm\^2|mpa|kpa)\b",
    re.IGNORECASE,
)

# Pressure class patterns (e.g. 150#, 300#, Class 150, PN 16)
_PRESSURE_CLASS_REGEX = re.compile(
    r"\b(?:CLASS\s*(\d+)|(\d+)\s*(?:#|LBS?)|PN\s*(\d+))\b",
    re.IGNORECASE,
)


def convert_length(
    value: float,
    unit: str,
) -> Tuple[Optional[float], Optional[str], bool]:
    """
    Deterministic length conversion to standard 'mm'.
    Returns: (normalized_value, normalized_unit, is_ambiguous)
    """
    clean_unit = unit.strip().lower()
    if clean_unit in LENGTH_CONVERSIONS:
        factor = LENGTH_CONVERSIONS[clean_unit]
        norm_val = round(value * factor, 2)
        return norm_val, "mm", False

    # Ambiguous or unknown unit
    return None, None, True


def convert_pressure(
    value: float,
    unit: str,
) -> Tuple[Optional[float], Optional[str], bool]:
    """
    Deterministic pressure conversion to standard 'bar'.
    Returns: (normalized_value, normalized_unit, is_ambiguous)
    """
    clean_unit = unit.strip().lower()
    if clean_unit in PRESSURE_CONVERSIONS:
        factor = PRESSURE_CONVERSIONS[clean_unit]
        norm_val = round(value * factor, 3)
        return norm_val, "bar", False

    return None, None, True


def are_dimensions_equivalent(
    dim1: Optional[float],
    dim2: Optional[float],
    relative_tolerance: float = 0.02,
) -> bool:
    """
    Compare two normalized dimensions (in mm) with industrial engineering tolerance.
    e.g. 10 inch (254 mm) vs 254 mm -> True.
    """
    if dim1 is None or dim2 is None:
        return False
    if dim1 == 0 and dim2 == 0:
        return True
    diff = abs(dim1 - dim2)
    max_val = max(abs(dim1), abs(dim2))
    return (diff / max_val) <= relative_tolerance


def parse_dimension_string(text: str) -> Dict[str, Any]:
    """
    Scan string for dimensions and extract original & normalized units.
    """
    results = []
    for match in _DIMENSION_REGEX.finditer(text):
        raw_val = float(match.group(1))
        raw_unit = match.group(2)
        norm_val, norm_unit, is_ambig = convert_length(raw_val, raw_unit)
        results.append({
            "original_value": raw_val,
            "original_unit": raw_unit,
            "normalized_value": norm_val,
            "normalized_unit": norm_unit,
            "ambiguous": is_ambig,
        })
    return {"dimensions": results}
