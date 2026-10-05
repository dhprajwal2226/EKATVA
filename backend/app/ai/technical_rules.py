"""
Technical Rule Engine & Critical Conflict Detection.
Enforces industrial engineering precedence:
CRITICAL CONFLICT > SIMILARITY SCORE.
SIH 2026 - National Material Master Platform.

Changes vs. previous version:
- New attribute comparators: power_kw, voltage, rpm, phases, cores,
  cross_section_sqmm, pipe_class (DI K7/K9, GI class B...), conductor,
  valve_type, manufacturing_method, head_type.
- Missing information is no longer treated as agreement: if ONE side states
  an attribute and the other doesn't, an UNVERIFIED (MAJOR) conflict is raised.
- Items with no technical specification at all (e.g. "SS BOLT") raise an
  UNDERSPECIFIED (MAJOR) conflict, so they can never be auto-classified IDENTICAL.
"""

from typing import Dict, Any, List, Tuple, Optional
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
STATUS_UNVERIFIED = "UNVERIFIED"  # stated on one side only

Result = Tuple[str, str, str]

_SYNONYMS = {
    "SMLS": "SEAMLESS",
    "SEAMLESS": "SEAMLESS",
    "WELDED": "ERW",
    "ERW": "ERW",
    "CU": "COPPER",
    "COPPER": "COPPER",
    "AL": "ALUMINIUM",
    "ALUMINUM": "ALUMINIUM",
    "ALUMINIUM": "ALUMINIUM",
    "HEXAGON": "HEX",
    "HEXAGONAL": "HEX",
    "HEX": "HEX",
}


def _blank(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def _to_float(value: Any) -> Optional[float]:
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return None


def _norm(value: Any) -> str:
    text = str(value or "").strip().upper().replace(" ", "").replace("-", "")
    return _SYNONYMS.get(text, text)


# ---------------------------------------------------------------------------
# Existing comparators (unchanged behaviour)
# ---------------------------------------------------------------------------

def compare_grades(grade1: Any, grade2: Any) -> Result:
    """Compare metallurgical / material grades."""
    g1 = str(grade1 or "").strip().upper()
    g2 = str(grade2 or "").strip().upper()

    if not g1 or not g2:
        return STATUS_UNKNOWN, SEVERITY_INFO, "One or both material grades are unspecified (UNKNOWN)"

    clean1 = g1.replace(" ", "").replace("-", "")
    clean2 = g2.replace(" ", "").replace("-", "")

    if clean1 == clean2:
        return STATUS_MATCH, SEVERITY_INFO, f"Grades match perfectly ({g1})"

    if ("304" in clean1 and "316" in clean2) or ("316" in clean1 and "304" in clean2):
        return (
            STATUS_CRITICAL,
            SEVERITY_CRITICAL,
            "Critical metallurgy conflict: SS304 vs SS316 have fundamentally different corrosion resistance (Molybdenum content). NEVER auto-merge.",
        )

    return (
        STATUS_CRITICAL,
        SEVERITY_CRITICAL,
        f"Critical grade discrepancy: '{g1}' vs '{g2}'. Chemical and tensile properties differ.",
    )


def compare_materials(mat1: Any, mat2: Any) -> Result:
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


def compare_material_types(type1: Any, type2: Any) -> Result:
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
) -> Result:
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


def compare_pressure(press1: Any, press2: Any) -> Result:
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


def compare_schedule(sch1: Any, sch2: Any) -> Result:
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


def compare_standards(std1: Any, std2: Any) -> Result:
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


# ---------------------------------------------------------------------------
# New comparators
# ---------------------------------------------------------------------------

def compare_numeric_spec(
    v1: Any,
    v2: Any,
    name: str,
    unit: str = "",
    severity: str = SEVERITY_CRITICAL,
    rel_tolerance: float = 0.01,
) -> Result:
    """Exact-ish numeric comparison (power, voltage, cores, cross-section...)."""
    if _blank(v1) or _blank(v2):
        return STATUS_UNKNOWN, SEVERITY_INFO, f"{name} unspecified on one or both items"

    f1, f2 = _to_float(v1), _to_float(v2)
    suffix = f" {unit}" if unit else ""

    if f1 is None or f2 is None:
        if _norm(v1) == _norm(v2):
            return STATUS_MATCH, SEVERITY_INFO, f"{name} matches ({v1})"
        f1s, f2s = str(v1), str(v2)
        status = STATUS_CRITICAL if severity == SEVERITY_CRITICAL else STATUS_MAJOR_DIFF
        return status, severity, f"{name} conflict: {f1s} vs {f2s}"

    if abs(f1 - f2) <= rel_tolerance * max(abs(f1), abs(f2), 1e-9):
        return STATUS_MATCH, SEVERITY_INFO, f"{name} matches ({f1:g}{suffix})"

    status = STATUS_CRITICAL if severity == SEVERITY_CRITICAL else STATUS_MAJOR_DIFF
    return (
        status,
        severity,
        f"{name} conflict: {f1:g}{suffix} vs {f2:g}{suffix}. Items are not interchangeable.",
    )


def compare_code_spec(
    v1: Any,
    v2: Any,
    name: str,
    severity: str = SEVERITY_CRITICAL,
) -> Result:
    """Compare class / rating codes (DI class K7 vs K9, GI class B vs C)."""
    if _blank(v1) or _blank(v2):
        return STATUS_UNKNOWN, SEVERITY_INFO, f"{name} unspecified on one or both items"

    if _norm(v1) == _norm(v2):
        return STATUS_MATCH, SEVERITY_INFO, f"{name} matches ({v1})"

    status = STATUS_CRITICAL if severity == SEVERITY_CRITICAL else STATUS_MAJOR_DIFF
    return (
        status,
        severity,
        f"{name} conflict: '{v1}' vs '{v2}'. Thickness / rating differs.",
    )


def compare_text_spec(
    v1: Any,
    v2: Any,
    name: str,
    severity: str = SEVERITY_MAJOR,
) -> Result:
    """Compare categorical specs (valve type, seamless vs ERW, conductor...)."""
    if _blank(v1) or _blank(v2):
        return STATUS_UNKNOWN, SEVERITY_INFO, f"{name} unspecified on one or both items"

    if _norm(v1) == _norm(v2):
        return STATUS_MATCH, SEVERITY_INFO, f"{name} matches ({v1})"

    status = STATUS_CRITICAL if severity == SEVERITY_CRITICAL else STATUS_MAJOR_DIFF
    return status, severity, f"{name} conflict: '{v1}' vs '{v2}'."


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

# Attributes never flagged as one-sided (length is often legitimately omitted)
_ONE_SIDED_EXEMPT = {"length"}

# Attributes that count as "technical specification" for the underspecified rule
_IDENTITY_ONLY = {"material_type", "material"}


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

    def g(attrs: Dict[str, Any], key: str) -> Any:
        return attrs.get(key)

    comparisons: List[Tuple[str, Result]] = [
        ("material_type", compare_material_types(g(attr_a, "material_type"), g(attr_b, "material_type"))),
        ("material", compare_materials(g(attr_a, "material"), g(attr_b, "material"))),
        ("grade", compare_grades(g(attr_a, "grade"), g(attr_b, "grade"))),
        ("diameter", compare_dimensions(g(attr_a, "diameter"), g(attr_b, "diameter"), "diameter")),
        (
            "length",
            compare_dimensions(g(attr_a, "length"), g(attr_b, "length"), "length")
            if g(attr_a, "length") and g(attr_b, "length")
            else (STATUS_UNKNOWN, SEVERITY_INFO, "Length unspec"),
        ),
        ("pressure", compare_pressure(g(attr_a, "pressure"), g(attr_b, "pressure"))),
        ("schedule", compare_schedule(g(attr_a, "schedule"), g(attr_b, "schedule"))),
        ("standard", compare_standards(g(attr_a, "standard"), g(attr_b, "standard"))),
        # --- new ---
        ("power_kw", compare_numeric_spec(g(attr_a, "power_kw"), g(attr_b, "power_kw"), "Power rating", "kW")),
        ("voltage", compare_numeric_spec(g(attr_a, "voltage"), g(attr_b, "voltage"), "Voltage", "V")),
        ("rpm", compare_numeric_spec(g(attr_a, "rpm"), g(attr_b, "rpm"), "Speed", "RPM", SEVERITY_MAJOR)),
        ("phases", compare_numeric_spec(g(attr_a, "phases"), g(attr_b, "phases"), "Phases")),
        ("cores", compare_numeric_spec(g(attr_a, "cores"), g(attr_b, "cores"), "Cable cores")),
        (
            "cross_section_sqmm",
            compare_numeric_spec(
                g(attr_a, "cross_section_sqmm"), g(attr_b, "cross_section_sqmm"),
                "Conductor cross-section", "sq mm",
            ),
        ),
        ("pipe_class", compare_code_spec(g(attr_a, "pipe_class"), g(attr_b, "pipe_class"), "Pipe class")),
        ("conductor", compare_text_spec(g(attr_a, "conductor"), g(attr_b, "conductor"), "Conductor material", SEVERITY_CRITICAL)),
        ("valve_type", compare_text_spec(g(attr_a, "valve_type"), g(attr_b, "valve_type"), "Valve type", SEVERITY_CRITICAL)),
        ("manufacturing_method", compare_text_spec(g(attr_a, "manufacturing_method"), g(attr_b, "manufacturing_method"), "Manufacturing method")),
        ("head_type", compare_text_spec(g(attr_a, "head_type"), g(attr_b, "head_type"), "Head type")),
    ]

    # Missing information is not agreement: stated on one side only -> UNVERIFIED
    adjusted: List[Tuple[str, Result]] = []
    for attr_name, (status, severity, reason) in comparisons:
        if status == STATUS_UNKNOWN and attr_name not in _ONE_SIDED_EXEMPT:
            a_has = not _blank(g(attr_a, attr_name))
            b_has = not _blank(g(attr_b, attr_name))
            if a_has != b_has:
                side = "source" if a_has else "target"
                status, severity, reason = (
                    STATUS_UNVERIFIED,
                    SEVERITY_MAJOR,
                    f"{attr_name} is specified only on the {side} item; equivalence cannot be verified.",
                )
        adjusted.append((attr_name, (status, severity, reason)))

    match_points = 0.0
    total_evaluable = 0

    for attr_name, (status, severity, reason) in adjusted:
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
        elif status in (STATUS_MAJOR_DIFF, STATUS_CRITICAL, STATUS_UNVERIFIED):
            total_evaluable += 1
            conflicts.append({
                "attribute": attr_name,
                "source_value": str(attr_a.get(attr_name)),
                "target_value": str(attr_b.get(attr_name)),
                "severity": severity,
                "reason": reason,
            })

    # Underspecified items (e.g. "SS BOLT") can never be called identical
    spec_keys = [name for name, _ in adjusted if name not in _IDENTITY_ONLY]
    a_specs = sum(1 for k in spec_keys if not _blank(g(attr_a, k)))
    b_specs = sum(1 for k in spec_keys if not _blank(g(attr_b, k)))
    if a_specs == 0 or b_specs == 0:
        matrix["specification"] = "UNDERSPECIFIED"
        total_evaluable += 1
        conflicts.append({
            "attribute": "specification",
            "source_value": f"{a_specs} technical attributes",
            "target_value": f"{b_specs} technical attributes",
            "severity": SEVERITY_MAJOR,
            "reason": "One or both items have no technical specification (size, grade, rating). Cannot confirm interchangeability.",
        })

    tech_score = round(match_points / total_evaluable, 3) if total_evaluable > 0 else 0.50
    return conflicts, matrix, tech_score