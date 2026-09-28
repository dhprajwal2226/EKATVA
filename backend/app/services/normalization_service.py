"""
Normalization Service.
Executes deterministic text normalization, unit conversions, and domain expansions.
SIH 2026 - National Material Master Platform.
"""

from typing import Dict, Any
from app.utils.text import normalize_description, DOMAIN_ABBREVIATIONS
from app.utils.units import parse_dimension_string


class NormalizationService:
    @staticmethod
    def process_description(raw_description: str) -> Dict[str, Any]:
        """
        Normalize raw material description while strictly preserving the original.
        Extracts dimensional units and records detected domain abbreviations.
        """
        if not raw_description:
            return {
                "original_description": "",
                "normalized_description": "",
                "expanded_abbreviations": [],
                "dimensions": [],
            }

        normalized = normalize_description(raw_description)
        raw_upper = raw_description.upper()

        # Track which abbreviations were present in original
        tokens = set(raw_upper.split())
        expanded = [
            {"abbr": tok, "expansion": DOMAIN_ABBREVIATIONS[tok]}
            for tok in tokens
            if tok in DOMAIN_ABBREVIATIONS
        ]

        # Parse units and dimensions
        dim_info = parse_dimension_string(raw_description)

        return {
            "original_description": raw_description,
            "normalized_description": normalized,
            "expanded_abbreviations": expanded,
            "dimensions": dim_info.get("dimensions", []),
        }
