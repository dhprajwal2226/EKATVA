"""
Deterministic Technical Attribute Extraction Engine (Material DNA).
Extracts structured engineering properties and computes confidence metrics.
SIH 2026 - National Material Master Platform.
"""

import re
from typing import Dict, Any, Optional, Tuple
from app.utils.text import normalize_description
from app.utils.units import convert_length, convert_pressure

# Standard taxonomy patterns
MATERIAL_TYPES = {
    "PIPE": ["PIPE", "TUBE", "TUBING", "PIPING"],
    "VALVE": [
        "VALVE", "BALL VALVE", "GATE VALVE", "GLOBE VALVE", "CHECK VALVE",
        "BUTTERFLY VALVE", "PLUG VALVE", "NEEDLE VALVE", "CONTROL VALVE",
    ],
    "FLANGE": ["FLANGE", "WNRF FLANGE", "BLIND FLANGE", "SLIP ON FLANGE", "SORF FLANGE"],
    "FITTING": ["ELBOW", "TEE", "REDUCER", "COUPLING", "UNION", "NIPPLE", "CAP"],
    "FASTENER": ["BOLT", "NUT", "STUD", "SCREW", "WASHER", "HEX BOLT", "STUD BOLT"],
    "GASKET": ["GASKET", "SPIRAL WOUND GASKET", "RTJ GASKET", "RING GASKET"],
    "PLATE": ["PLATE", "SHEET", "COIL"],
    "BEAM": ["BEAM", "CHANNEL", "ANGLE", "JOIST", "COLUMN"],
    "CABLE": ["CABLE", "WIRE", "CONDUCTOR"],
    "PUMP": ["PUMP", "CENTRIFUGAL PUMP"],
    "MOTOR": ["MOTOR", "INDUCTION MOTOR"],
    "BEARING": ["BEARING", "ROLLER BEARING", "BALL BEARING"],
}

MATERIALS = {
    "STAINLESS STEEL": ["STAINLESS STEEL", "SS", "INOX"],
    "CARBON STEEL": ["CARBON STEEL", "CS"],
    "MILD STEEL": ["MILD STEEL", "MS"],
    "ALLOY STEEL": ["ALLOY STEEL", "AS"],
    "CAST IRON": ["CAST IRON", "CI"],
    "DUCTILE IRON": ["DUCTILE IRON", "DI"],
    "BRASS": ["BRASS"],
    "COPPER": ["COPPER", "CU"],
    "ALUMINUM": ["ALUMINUM", "ALUMINIUM", "AL"],
    "TITANIUM": ["TITANIUM", "TI"],
    "PVC": ["POLYVINYL CHLORIDE", "PVC", "UPVC", "CPVC"],
    "HDPE": ["HIGH DENSITY POLYETHYLENE", "HDPE"],
    "PTFE": ["TEFLON", "PTFE"],
}

# Regex for common steel & alloy engineering grades
GRADE_PATTERNS = [
    # Stainless Steel grades
    (r"\b(SS\s*304L|SS\s*304H|SS\s*304|304L|304H|304)\b", "SS304"),
    (r"\b(SS\s*316L|SS\s*316H|SS\s*316Ti|SS\s*316|316L|316H|316)\b", "SS316"),
    (r"\b(SS\s*321|321)\b", "SS321"),
    (r"\b(SS\s*347|347)\b", "SS347"),
    (r"\b(SS\s*904L|904L)\b", "SS904L"),
    (r"\b(SS\s*310|310S|310)\b", "SS310"),
    (r"\b(SS\s*410|410)\b", "SS410"),
    (r"\b(DUPLEX\s*2205|2205)\b", "DUPLEX 2205"),
    (r"\b(SUPER\s*DUPLEX\s*2507|2507)\b", "SUPER DUPLEX 2507"),
    # Carbon steel & Pipe specifications
    (r"\bA\s*106\s*(?:GR(?:ADE)?\s*([ABC]))?\b", "A106"),
    (r"\bA\s*53\s*(?:GR(?:ADE)?\s*([ABC]))?\b", "A53"),
    (r"\bA\s*333\s*(?:GR(?:ADE)?\s*([1-9]))?\b", "A333"),
    (r"\bAPI\s*5L\s*(?:GR(?:ADE)?\s*(X\d{2}|[ABC]))?\b", "API 5L"),
    (r"\bA\s*105(?:N)?\b", "A105"),
    (r"\bA\s*234\s*(?:WPB|WPC)\b", "A234 WPB"),
    (r"\bIS\s*2062\s*(?:GR(?:ADE)?\s*([A-E]|\d+))?\b", "IS 2062"),
    (r"\bIS\s*1239\b", "IS 1239"),
    # Fastener Grades
    (r"\b(A\s*193\s*B7M?|B7M?)\b", "A193 B7"),
    (r"\b(A\s*194\s*2HM?|2HM?)\b", "A194 2H"),
    (r"\b(B8M?|CLASS\s*1|CLASS\s*2)\b", "B8"),
    (r"\bGRADE\s*(8\.8|10\.9|12\.9|4\.6)\b", r"GR \1"),
    (r"\b(8\.8|10\.9|12\.9)\b", r"GR \1"),
    # Valve body grades
    (r"\b(WCB|WCC)\b", "WCB"),
    (r"\b(CF8M|CF8|CF3M|CF3)\b", "CF8M"),
]

# Standards patterns
STANDARD_PATTERNS = [
    r"\bASTM\s+[A-Z]\s*\d+(?:/[A-Z]\s*\d+)?\b",
    r"\bASME\s+B\s*\d+\.\d+\b",
    r"\bDIN\s+\d+\b",
    r"\bIS\s+\d+(?:-\d+)?\b",
    r"\bAPI\s+\d+[A-Z]?\b",
    r"\bBS\s+\d+\b",
    r"\bISO\s+\d+\b",
    r"\bMSS\s+SP-\d+\b",
]

# Forms
FORMS = {
    "SEAMLESS": ["SEAMLESS", "SMLS"],
    "WELDED": ["WELDED", "ERW", "EFW", "SAW"],
    "FORGED": ["FORGED", "FGD"],
    "CAST": ["CAST", "CASTING"],
    "HEXAGONAL": ["HEX", "HEXAGONAL"],
    "ROUND": ["ROUND"],
    "FLAT": ["FLAT"],
}


def extract_attributes(raw_description: str) -> Dict[str, Any]:
    """
    Deterministic Material DNA Extractor.
    Takes raw or normalized description and extracts structured attributes
    along with confidence values and extraction sources.
    """
    normalized = normalize_description(raw_description)
    extracted: Dict[str, Any] = {
        "material_type": None,
        "material": None,
        "grade": None,
        "size": None,
        "diameter": None,
        "length": None,
        "width": None,
        "height": None,
        "thickness": None,
        "pressure": None,
        "schedule": None,
        "form": None,
        "standard": None,
        "application": None,
        "manufacturer": None,
        "confidence_scores": {},
        "raw_attributes": {},
    }

    # 1. Extract Material Type
    for mtype, keywords in MATERIAL_TYPES.items():
        for kw in sorted(keywords, key=len, reverse=True):
            if re.search(r"\b" + re.escape(kw) + r"\b", normalized, re.IGNORECASE):
                extracted["material_type"] = mtype.title()
                extracted["confidence_scores"]["material_type"] = 0.95
                break
        if extracted["material_type"]:
            break

    # 2. Extract Material Family
    for mat_name, keywords in MATERIALS.items():
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", normalized, re.IGNORECASE):
                extracted["material"] = mat_name.title()
                extracted["confidence_scores"]["material"] = 0.95
                break
        if extracted["material"]:
            break

    # 3. Extract Grade
    for pattern, canonical_grade in GRADE_PATTERNS:
        match = re.search(pattern, raw_description.upper()) or re.search(pattern, normalized)
        if match:
            extracted["grade"] = canonical_grade
            extracted["confidence_scores"]["grade"] = 0.98
            # Auto-infer material if missing
            if not extracted["material"]:
                if canonical_grade.startswith("SS"):
                    extracted["material"] = "Stainless Steel"
                elif canonical_grade in ["A106", "A53", "A105", "IS 2062", "WCB"]:
                    extracted["material"] = "Carbon Steel"
            break

    # 4. Extract Standards
    for std_pat in STANDARD_PATTERNS:
        match = re.search(std_pat, raw_description, re.IGNORECASE) or re.search(std_pat, normalized, re.IGNORECASE)
        if match:
            extracted["standard"] = match.group(0).upper().strip()
            extracted["confidence_scores"]["standard"] = 0.99
            break

    # 5. Extract Schedule (for pipes/fittings)
    sch_match = re.search(r"\b(?:SCHEDULE|SCH)\s*[-:]?\s*(\d+|STD|XS|XXS)\b", normalized, re.IGNORECASE)
    if sch_match:
        extracted["schedule"] = sch_match.group(1).upper()
        extracted["confidence_scores"]["schedule"] = 0.99

    # 6. Extract Pressure Class
    press_match = re.search(
        r"\b(?:CLASS\s*(\d+)|(\d+)\s*CLASS|(\d+)\s*(?:#|LBS?)|(\d+)\s*BAR|PN\s*(\d+))\b",
        normalized,
        re.IGNORECASE,
    ) or re.search(r"\b(\d+)\s*#(?!\w)", raw_description)
    if press_match:
        val = next(v for v in press_match.groups() if v is not None)
        matched_str = press_match.group(0).upper()
        if "BAR" in matched_str:
            extracted["pressure"] = f"{val} BAR"
        elif "PN" in matched_str:
            extracted["pressure"] = f"PN{val}"
        else:
            extracted["pressure"] = f"{val}#"
        extracted["confidence_scores"]["pressure"] = 0.95

    # 7. Extract Form (Seamless, Welded, Forged, etc.)
    for form_name, keywords in FORMS.items():
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", normalized, re.IGNORECASE):
                extracted["form"] = form_name.title()
                extracted["confidence_scores"]["form"] = 0.90
                break
        if extracted["form"]:
            break

    # 8. Extract Dimensions (Size, Diameter, Length, Thickness)
    # Check Metric Bolt pattern: M16 X 50
    metric_bolt_match = re.search(r"\bM(\d+)\s*X\s*(\d+(?:\.\d+)?)\b", normalized, re.IGNORECASE)
    if metric_bolt_match:
        dia_mm = float(metric_bolt_match.group(1))
        len_mm = float(metric_bolt_match.group(2))
        extracted["size"] = f"M{int(dia_mm)} X {int(len_mm)}"
        extracted["diameter"] = dia_mm
        extracted["length"] = len_mm
        extracted["confidence_scores"]["diameter"] = 0.99
        extracted["confidence_scores"]["length"] = 0.99
        if not extracted["material_type"]:
            extracted["material_type"] = "Fastener"

    # Check Inch Size (e.g. 10 INCH, 4 INCH, 1/2 INCH)
    if extracted["diameter"] is None:
        inch_match = re.search(
            r"\b(\d+(?:\.\d+)?|\d+/\d+)\s*(?:INCH(?:ES)?|IN|\"|”)\b",
            raw_description,
            re.IGNORECASE,
        )
        if inch_match:
            raw_val_str = inch_match.group(1)
            try:
                if "/" in raw_val_str:
                    num, den = raw_val_str.split("/")
                    val_inch = float(num) / float(den)
                else:
                    val_inch = float(raw_val_str)
                dia_mm, _, _ = convert_length(val_inch, "inch")
                extracted["size"] = f"{raw_val_str} INCH"
                extracted["diameter"] = dia_mm
                extracted["confidence_scores"]["diameter"] = 0.95
            except Exception:
                pass

    # Check Metric Diameter / Millimeters (e.g. 254 MM, 100 MM)
    if extracted["diameter"] is None:
        mm_match = re.search(r"\b(\d+(?:\.\d+)?)\s*MM\b", normalized, re.IGNORECASE)
        if mm_match:
            extracted["diameter"] = float(mm_match.group(1))
            extracted["size"] = f"{mm_match.group(1)} MM"
            extracted["confidence_scores"]["diameter"] = 0.95

    # Check Nominal Bore / DN
    if extracted["diameter"] is None:
        dn_match = re.search(r"\b(?:DN|NB)\s*(\d+)\b", normalized, re.IGNORECASE)
        if dn_match:
            dn_val = float(dn_match.group(1))
            extracted["diameter"] = dn_val
            extracted["size"] = f"DN {int(dn_val)}"
            extracted["confidence_scores"]["diameter"] = 0.90

    # Extract Thickness (THK 5 MM, 5MM THK)
    thk_match = re.search(r"\b(\d+(?:\.\d+)?)\s*MM\s*(?:THK|THICKNESS)\b|\b(?:THK|THICKNESS)\s*[-:]?\s*(\d+(?:\.\d+)?)\b", normalized, re.IGNORECASE)
    if thk_match:
        thk_val = thk_match.group(1) or thk_match.group(2)
        extracted["thickness"] = float(thk_val)
        extracted["confidence_scores"]["thickness"] = 0.95

    # Record overall confidence
    confidences = list(extracted["confidence_scores"].values())
    extracted["overall_confidence"] = round(sum(confidences) / len(confidences), 3) if confidences else 0.50

    return extracted
