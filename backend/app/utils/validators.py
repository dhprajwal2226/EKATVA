"""
File and Data Validators for Ingestion & API Requests.
SIH 2026 - National Material Master Platform.
"""

import os
from typing import Tuple, Optional, List, Dict, Any
from app.core.config import settings


def validate_file_metadata(
    filename: str,
    content_length: Optional[int],
    content_type: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file extension, size, and content type.
    """
    if not filename:
        return False, "Filename cannot be empty"

    ext = os.path.splitext(filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        return (
            False,
            f"Invalid file extension '{ext}'. Allowed extensions are: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )

    if content_length is not None and content_length > settings.MAX_UPLOAD_SIZE_BYTES:
        max_mb = settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
        return False, f"File size exceeds maximum allowed limit of {max_mb} MB"

    if content_type and content_type not in settings.ALLOWED_MIME_TYPES:
        # Warning/log only if MIME is generic binary or recognized
        pass

    return True, None


def validate_material_row(
    row_idx: int,
    data: Dict[str, Any],
) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Validate a single material master ingestion row.
    Returns: (is_valid, list_of_errors)
    """
    errors: List[Dict[str, Any]] = []

    code = str(data.get("material_code") or "").strip()
    if not code:
        errors.append({
            "row": row_idx,
            "field": "material_code",
            "message": "Missing required material_code",
        })

    description = str(data.get("description") or data.get("original_description") or "").strip()
    if not description:
        errors.append({
            "row": row_idx,
            "field": "description",
            "message": "Missing required material description",
        })
    elif len(description) < 3:
        errors.append({
            "row": row_idx,
            "field": "description",
            "message": "Description is too short (< 3 characters)",
        })

    return len(errors) == 0, errors
