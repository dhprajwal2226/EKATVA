"""Utils package exports."""

from app.utils.text import (
    normalize_description,
    expand_abbreviations,
    normalize_separators,
    DOMAIN_ABBREVIATIONS,
)
from app.utils.units import (
    convert_length,
    convert_pressure,
    are_dimensions_equivalent,
    parse_dimension_string,
)
from app.utils.validators import validate_file_metadata, validate_material_row

__all__ = [
    "normalize_description",
    "expand_abbreviations",
    "normalize_separators",
    "DOMAIN_ABBREVIATIONS",
    "convert_length",
    "convert_pressure",
    "are_dimensions_equivalent",
    "parse_dimension_string",
    "validate_file_metadata",
    "validate_material_row",
]
