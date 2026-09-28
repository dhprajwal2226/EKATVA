"""
Technical Rule Engine & Critical Conflict Detection.
Enforces industrial engineering precedence:
CRITICAL CONFLICT > SIMILARITY SCORE.
SIH 2026 - National Material Master Platform.
"""

from typing import Dict, Any, List, Tuple
from app.utils.units import are_dimensions_equivalent

# Conflict Severities
SEVERITY_INFO = "INFO"
SEVERITY_MINOR = "MINOR"
SEVERITY_MAJOR = "MAJOR"
SEVERITY_CRITICAL = "CRITICAL"

# Status Outcomes
STATUS_MATCH = "MATCH"
STATUS_MINOR_DIFF = "MINOR_DIFFERENCE"
STATUS_MAJOR_DIFF = "MAJOR_DIFFERENCE"
STATUS_CRITICAL = "CRITICAL_CONFLICT"
STATUS_UNKNOWN = "UNKNOWN"


def compare_grades(grade1: Any, grade2: Any) -> Tuple[str, str, str]:
    """
    Compare metallurgical / material grades.
    Returns: (status, severity, reason)
    """
    g1 = str(grade1 or "").strip().upper()
    g2 = str(grade2 or "").strip().upper()

    if not g1 or not g2:
        return STATUS_UNKNOWN, SEVERITY_INFO, "One or both material grades are unspecified (UNKNOWN)"

    # Clean punctuation
    clean1 = g1.replace(" ", "").replace("-", "")
    clean2 = g2.replace(" ", "").replace("-", "")

    if clean1 == clean2:
        return STATUS_MATCH, SEVERITY_INFO, f"Grades match perfectly ({g1})"

    # Check known critical grade mismatches in industrial piping & fasteners
    # E.g., SS304 vs SS316, A106 vs A333 (carbon steel vs low-temp carbon steel)
    if ("304" in clean1 and "316" in clean2) or ("316" in clean1 and "304" in clean2):
        return (
            STATUS_CRITICAL,
            SEVERITY_CRITICAL,
            f"Critical metallurgy conflict: SS304 vs SS316 have fundamentally different corrosion resistance (Molybdenum content). NEVER auto-merge.",
        )

    return (
        STATUS_CRITICAL,
        SEVERITY_CRITICAL,
        f"Critical grade discrepancy: '{g1}' vs '{g2}'. Chemical and tensile properties differ.",
    )


def compare_materials(mat1: Any, mat2: Any) -> Tuple[str, str, str]:
    """Compare base materials (Carbon Steel, Stainless Steel, Brass, etc.)."""
    m1 = str(mat1 or "").strip().upper()
    m2 = str(mat2 or "").strip().upper()

    if not m1 or not m2:
        return STATUS_UNKNOWN, SEVERITY_INFO, "One or both base materials are unspecified"

    if m1 == m2:
        return STATUS_MATCH, SEVERITY_INFO, f"Base materials match ({m1})"

    return (
        STATUS_CRITICAL,
        SEVERITY_CRITICAL,
        f"Critical material mismatch: '{m1}' vs '{m2}'. Incompatible base material classes.",
    )


def compare_material_types(type1: Any, type2: Any) -> Tuple[str, str, str]:
    """Compare high-level item type (Pipe vs Valve vs Bolt, etc.)."""
    t1 = str(type1 or "").strip().upper()
    t2 = str(type2 or "").strip().upper()

    if not t1 or not t2:
        return STATUS_UNKNOWN, SEVERITY_INFO, "Item type unspecified"

    if t1 == t2:
        return STATUS_MATCH, SEVERITY_INFO, f"Material types match ({t1})"

    return (
        STATUS_CRITICAL,
        SEVERITY_CRITICAL,
        f"Critical taxonomy mismatch: '{t1}' vs '{t2}'. Different functional equipment.",
    )


def compare_dimensions(
    dim1: Any,
    dim2: Any,
    dim_name: str = "diameter",
) -> Tuple[str, str, str]:
    """Compare normalized numeric dimensions (in mm) with engineering tolerances."""
    if dim1 is None or dim2 is None:
        return STATUS_UNKNOWN, SEVERITY_INFO, f"{dim_name} missing on one or both items"

    try:
        val1 = float(dim1)
        val2 = float(dim2)
    except (ValueError, TypeError):
        return STATUS_UNKNOWN, SEVERITY_INFO, f"Invalid numeric dimension format for {dim_name}"

    if are_dimensions_equivalent(val1, val2, relative_tolerance=0.02):
        return STATUS_MATCH, SEVERITY_INFO, f"{dim_name} matches ({val1:.1f} mm vs {val2:.1f} mm within tolerance)"

    # Calculate percentage difference
    pct_diff = abs(val1 - val2) / max(val1, val2)
    if pct_diff <= 0.10:
        return (
            STATUS_MAJOR_DIFF,
            SEVERITY_MAJOR,
            f"{dim_name} difference of {pct_diff * 100:.1f}% ({val1:.1f} mm vs {val2:.1f} mm)",
        )

    return (
        STATUS_CRITICAL,
        SEVERITY_CRITICAL,
        f"Critical {dim_name} conflict: {val1:.1f} mm vs {val2:.1f} mm ({pct_diff * 100:.1f}% difference). Physical fit will fail.",
    )


def compare_pressure(press1: Any, press2: Any) -> Tuple[str, str, str]:
    """Compare pressure classes or ratings."""
    p1 = str(press1 or "").strip().upper().replace(" ", "")
    p2 = str(press2 or "").strip().upper().replace(" ", "")

    if not p1 or not p2:
        return STATUS_UNKNOWN, SEVERITY_INFO, "Pressure rating unspecified"

    if p1 == p2:
        return STATUS_MATCH, SEVERITY_INFO, f"Pressure ratings match ({press1})"

    return (
        STATUS_CRITICAL,
        SEVERITY_CRITICAL,
        f"Critical pressure conflict: '{press1}' vs '{press2}'. Overpressure risk in plant operations.",
    )


def compare_schedule(sch1: Any, sch2: Any) -> Tuple[str, str, str]:
    """Compare pipe schedules / wall thickness codes."""
    s1 = str(sch1 or "").strip().upper()
    s2 = str(sch2 or "").strip().upper()

    if not s1 or not s2:
        return STATUS_UNKNOWN, SEVERITY_INFO, "Pipe schedule unspecified"

    if s1 == s2:
        return STATUS_MATCH, SEVERITY_INFO, f"Pipe schedule matches (SCH {s1})"

    return (
        STATUS_MAJOR_DIFF,
        SEVERITY_MAJOR,
        f"Schedule mismatch: SCH {s1} vs SCH {s2}. Wall thickness and internal pressure capability differ.",
    )


def compare_standards(std1: Any, std2: Any) -> Tuple[str, str, str]:
    """Compare compliance standards (ASTM, ASME, DIN, IS)."""
    st1 = str(std1 or "").strip().upper().replace(" ", "")
    st2 = str(std2 or "").strip().upper().replace(" ", "")

    if not st1 or not st2:
        return STATUS_UNKNOWN, SEVERITY_INFO, "Compliance standard unspecified"

    if st1 == st2:
        return STATUS_MATCH, SEVERITY_INFO, f"Standard matches ({std1})"

    return (
        STATUS_MAJOR_DIFF,
        SEVERITY_MAJOR,
        f"Specification standard difference: '{std1}' vs '{std2}'.",
    )


def evaluate_technical_conflicts(
    attr_a: Dict[str, Any],
    attr_b: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], Dict[str, str], float]:
    """
    Execute full technical conflict validation matrix.
    Returns:
    - conflicts_list: list of conflict dictionaries suitable for DB storage
    - attribute_matrix: detailed match status per attribute
    - technical_score: technical compliance score (0.0 to 1.0)
    """
    conflicts: List[Dict[str, Any]] = []
    matrix: Dict[str, str] = {}

    comparisons = [
        ("material_type", compare_material_types(attr_a.get("material_type"), attr_b.get("material_type"))),
        ("material", compare_materials(attr_a.get("material"), attr_b.get("material"))),
        ("grade", compare_grades(attr_a.get("grade"), attr_b.get("grade"))),
        ("diameter", compare_dimensions(attr_a.get("diameter"), attr_b.get("diameter"), "diameter")),
        ("length", compare_dimensions(attr_a.get("length"), attr_b.get("length"), "length") if attr_a.get("length") and attr_b.get("length") else (STATUS_UNKNOWN, SEVERITY_INFO, "Length unspec")),
        ("pressure", compare_pressure(attr_a.get("pressure"), attr_b.get("pressure"))),
        ("schedule", compare_schedule(attr_a.get("schedule"), attr_b.get("schedule"))),
        ("standard", compare_standards(attr_a.get("standard"), attr_b.get("standard"))),
    ]

    match_points = 0.0
    total_evaluable = 0

    for attr_name, (status, severity, reason) in comparisons:
        matrix[attr_name] = status

        if status == STATUS_MATCH:
            match_points += 1.0
            total_evaluable += 1
        elif status == STATUS_MINOR_DIFF:
            match_points += 0.7
            total_evaluable += 1
            conflicts.append({
                "attribute": attr_name,
                "source_value": str(attr_a.get(attr_name)),
                "target_value": str(attr_b.get(attr_name)),
                "severity": severity,
                "reason": reason,
            })
        elif status in (STATUS_MAJOR_DIFF, STATUS_CRITICAL):
            match_points += 0.0
            total_evaluable += 1
            conflicts.append({
                "attribute": attr_name,
                "source_value": str(attr_a.get(attr_name)),
                "target_value": str(attr_b.get(attr_name)),
                "severity": severity,
                "reason": reason,
            })

    tech_score = round(match_points / total_evaluable, 3) if total_evaluable > 0 else 0.50
    return conflicts, matrix, tech_score
