"""
Text Normalization & Centralized Domain Abbreviation Dictionary.
SIH 2026 - National Material Master Platform.
"""

import re
from typing import Dict, Tuple

# Centralized Domain Abbreviation Dictionary for CPSE Materials
# Rules: Lookups are matched on token boundaries to prevent substring corruption
DOMAIN_ABBREVIATIONS: Dict[str, str] = {
    # Materials / Metallurgy
    "SS": "STAINLESS STEEL",
    "CS": "CARBON STEEL",
    "MS": "MILD STEEL",
    "GI": "GALVANIZED IRON",
    "CI": "CAST IRON",
    "DI": "DUCTILE IRON",
    "AS": "ALLOY STEEL",
    "CU": "COPPER",
    "BR": "BRASS",
    "AL": "ALUMINUM",
    "PVC": "POLYVINYL CHLORIDE",
    "HDPE": "HIGH DENSITY POLYETHYLENE",
    "PTFE": "TEFLON",
    "TI": "TITANIUM",

    # Piping & Dimensions
    "NB": "NOMINAL BORE",
    "DN": "DIAMETRE NOMINAL",
    "OD": "OUTSIDE DIAMETER",
    "ID": "INSIDE DIAMETER",
    "SCH": "SCHEDULE",
    "SCHED": "SCHEDULE",
    "THK": "THICKNESS",
    "WT": "WALL THICKNESS",
    "STD": "STANDARD",
    "XS": "EXTRA STRONG",
    "XXS": "DOUBLE EXTRA STRONG",
    "SMLS": "SEAMLESS",
    "SEAML": "SEAMLESS",
    "ERW": "ELECTRIC RESISTANCE WELDED",
    "SAW": "SUBMERGED ARC WELDED",
    "WLD": "WELDED",
    "FORG": "FORGED",
    "FGD": "FORGED",

    # Hardware & Fasteners
    "HEX": "HEXAGONAL",
    "SOC": "SOCKET",
    "SKT": "SOCKET",
    "BLT": "BOLT",
    "SCR": "SCREW",
    "WSHR": "WASHER",
    "FLG": "FLANGE",
    "VLV": "VALVE",
    "GSKT": "GASKET",
    "ELB": "ELBOW",
    "CONC": "CONCENTRIC",
    "ECC": "ECCENTRIC",
    "RED": "REDUCER",
    "CPLG": "COUPLING",

    # End Connections & Pressure
    "SW": "SOCKET WELD",
    "BW": "BUTT WELD",
    "THD": "THREADED",
    "NPT": "NATIONAL PIPE THREAD",
    "BSP": "BRITISH STANDARD PIPE",
    "BSPT": "BRITISH STANDARD PIPE TAPER",
    "RF": "RAISED FACE",
    "FF": "FLAT FACE",
    "RTJ": "RING TYPE JOINT",
    "PN": "PRESSURE NOMINAL",
    "CL": "CLASS",
    "PRESS": "PRESSURE",
    "RATG": "RATING",
    "TEMP": "TEMPERATURE",
    "GALV": "GALVANIZED",
}

# Compiled regex for token replacement
_ABBR_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in sorted(DOMAIN_ABBREVIATIONS.keys(), key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)

# Common multiplication signs & separators: 'x', 'X', '*', '×', 'by'
_MULTIPLICATION_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*(?:[xX*×]|\bby\b)\s*(\d+(?:\.\d+)?)")

# Dimension symbol pattern: e.g., 10" or 10 '
_QUOTE_INCH_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*(?:"|”|inch(?:es)?|in\b)', re.IGNORECASE)
_QUOTE_FEET_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*(?:'|’|ft\b|feet\b)", re.IGNORECASE)
_MM_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*(?:mm\b|millimeter(?:s)?)", re.IGNORECASE)
_METER_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*(?:m\b|meter(?:s)?|mtr(?:s)?)", re.IGNORECASE)
_PRESSURE_HASH_PATTERN = re.compile(r"(\d+)\s*(?:#|lb\b|lbs\b|class\s*\d+)", re.IGNORECASE)


def normalize_whitespace(text: str) -> str:
    """Collapse consecutive spaces and strip edge whitespace."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def normalize_separators(text: str) -> str:
    """
    Standardize multiplication characters (*, ×, x, by) into uniform 'X'.
    e.g., 'M16*50' -> 'M16 X 50', 'M16 × 50' -> 'M16 X 50', 'M16x50' -> 'M16 X 50'.
    """
    if not text:
        return ""
    # Standardize 'M16x50' or '16*50' or '16 × 50'
    text = re.sub(r"\bM(\d+)\s*[xX*×]\s*(\d+)\b", r"M\1 X \2", text)
    text = _MULTIPLICATION_PATTERN.sub(r"\1 X \2", text)
    # Standardize slash and dash spacing
    text = re.sub(r"\s*/\s*", "/", text)
    text = re.sub(r"\s*-\s*", "-", text)
    return text


def expand_abbreviations(text: str) -> str:
    """
    Expand domain-specific industrial abbreviations based on centralized dictionary.
    Safe boundary checking ensures that subwords like 'ASSIST' are not altered.
    """
    if not text:
        return ""

    def replace_match(match: re.Match) -> str:
        word = match.group(0).upper()
        # Don't expand if part of compound grade like SS304, CS-A106
        return DOMAIN_ABBREVIATIONS.get(word, word)

    return _ABBR_PATTERN.sub(replace_match, text)


def normalize_description(text: str) -> str:
    """
    Full deterministic normalization pipeline for material descriptions.
    Preserves technical intent while harmonizing formatting across CPSEs.
    """
    if not text:
        return ""

    # 1. Clean casing and whitespace
    normalized = text.strip()

    # 2. Harmonize dimensional operators
    normalized = normalize_separators(normalized)

    # 3. Standardize common schedule syntax e.g. SCH40 -> SCH 40
    normalized = re.sub(r"\bSCH(?:EDULE)?\s*[-:]?\s*(\d+|STD|XS|XXS)\b", r"SCHEDULE \1", normalized, flags=re.IGNORECASE)

    # 4. Standardize pressure class e.g. 150# -> 150 LBS / 150 CLASS
    normalized = re.sub(r"\b(\d+)\s*#(?!\w)", r"\1 CLASS", normalized)

    # 5. Expand domain abbreviations
    normalized = expand_abbreviations(normalized)

    # 6. Normalize punctuation (replace odd symbols, preserve slashes, dashes, dots)
    normalized = re.sub(r"[;,~_]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip().upper()

    return normalized
