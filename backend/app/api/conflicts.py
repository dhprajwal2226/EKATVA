"""
Conflicts API Routes.
Technical conflict discovery and drill-down.
SIH 2026 - National Material Master Platform.
"""

import math
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.material_conflict import MaterialConflict
from app.schemas.conflict import ConflictDetailResponse, PaginatedConflictsResponse

router = APIRouter(prefix="/conflicts", tags=["Technical Conflicts"])


@router.get("", response_model=PaginatedConflictsResponse, summary="List and filter technical conflicts")
def list_conflicts(
    severity: Optional[str] = Query(None, description="Filter by severity: INFO, MINOR, MAJOR, CRITICAL"),
    attribute: Optional[str] = Query(None, description="Filter by conflicting attribute (grade, diameter, pressure, etc.)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Retrieve paginated list of technical discrepancies detected by the rule engine."""
    query = db.query(MaterialConflict)

    if severity:
        query = query.filter(MaterialConflict.severity == severity.strip().upper())

    if attribute:
        query = query.filter(MaterialConflict.attribute == attribute.strip().lower())

    total = query.count()
    conflicts_raw = query.order_by(MaterialConflict.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [
        ConflictDetailResponse(
            id=c.id,
            match_id=c.match_id,
            attribute=c.attribute,
            source_value=c.source_value,
            target_value=c.target_value,
            severity=c.severity,
            reason=c.reason,
            created_at=c.created_at,
        )
        for c in conflicts_raw
    ]

    return PaginatedConflictsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 1,
    )


@router.get("/{conflict_id}", response_model=ConflictDetailResponse, summary="Get conflict detail by ID")
def get_conflict_detail(
    conflict_id: int,
    db: Session = Depends(get_db),
):
    """Get single conflict record with reason and values."""
    c = db.query(MaterialConflict).filter(MaterialConflict.id == conflict_id).first()
    if not c:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CONFLICT_NOT_FOUND", "message": f"Conflict with ID {conflict_id} not found."},
        )

    return ConflictDetailResponse(
        id=c.id,
        match_id=c.match_id,
        attribute=c.attribute,
        source_value=c.source_value,
        target_value=c.target_value,
        severity=c.severity,
        reason=c.reason,
        created_at=c.created_at,
    )
