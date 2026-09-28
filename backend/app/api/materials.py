"""
Materials API Routes.
Material master search, details, DNA, matches, and conflicts.
SIH 2026 - National Material Master Platform.
"""

import math
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.database import get_db
from app.models.material import Material
from app.models.cpse import CPSE
from app.models.material_match import MaterialMatch
from app.models.material_conflict import MaterialConflict
from app.schemas.material import (
    MaterialDetailResponse,
    MaterialSummary,
    PaginatedMaterialsResponse,
)
from app.schemas.material_dna import MaterialDNAResponse, MaterialAttributeSchema
from app.schemas.matching import MatchResponse, MaterialItemReference, MatchScores, MatchExplanation
from app.schemas.conflict import ConflictDetailResponse, ConflictItem

router = APIRouter(prefix="/materials", tags=["Materials Master"])


@router.get("", response_model=PaginatedMaterialsResponse, summary="List and filter materials")
def list_materials(
    search: Optional[str] = Query(None, description="Keyword search in original or normalized description"),
    cpse: Optional[str] = Query(None, description="Filter by CPSE code (IOCL, NTPC, BHEL, GAIL)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by material status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Retrieve paginated materials master list with multi-parameter filtering."""
    query = db.query(Material).join(CPSE)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Material.material_code.ilike(search_term),
                Material.original_description.ilike(search_term),
                Material.normalized_description.ilike(search_term),
            )
        )

    if cpse:
        query = query.filter(CPSE.code == cpse.strip().upper())

    if category:
        query = query.filter(Material.category == category.strip())

    if status_filter:
        query = query.filter(Material.status == status_filter.strip())

    total = query.count()
    items_raw = query.order_by(Material.id.asc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [
        MaterialSummary(
            id=m.id,
            cpse_code=m.cpse.code if m.cpse else "UNKNOWN",
            material_code=m.material_code,
            original_description=m.original_description,
            normalized_description=m.normalized_description,
            category=m.category,
            status=m.status,
            created_at=m.created_at,
        )
        for m in items_raw
    ]

    return PaginatedMaterialsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 1,
    )


@router.get("/{material_id}", response_model=MaterialDetailResponse, summary="Get material detail")
def get_material_detail(
    material_id: int,
    db: Session = Depends(get_db),
):
    """Get single material record including its CPSE details and extracted DNA attributes."""
    m = db.query(Material).filter(Material.id == material_id).first()
    if not m:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "MATERIAL_NOT_FOUND", "message": f"Material with ID {material_id} not found."},
        )

    attr_schema = None
    if m.attributes:
        other = m.attributes.other_attributes or {}
        attr_schema = MaterialAttributeSchema(
            material_type=m.attributes.material_type,
            material=m.attributes.material,
            grade=m.attributes.grade,
            size=m.attributes.size,
            diameter=m.attributes.diameter,
            length=m.attributes.length,
            width=m.attributes.width,
            height=m.attributes.height,
            thickness=m.attributes.thickness,
            pressure=m.attributes.pressure,
            schedule=m.attributes.schedule,
            form=m.attributes.form,
            standard=m.attributes.standard,
            application=m.attributes.application,
            manufacturer=m.attributes.manufacturer,
            confidence_scores=other.get("confidence_scores", {}),
            fingerprint_hash=other.get("fingerprint_hash"),
        )

    return MaterialDetailResponse(
        id=m.id,
        cpse_id=m.cpse_id,
        cpse_code=m.cpse.code if m.cpse else "UNKNOWN",
        cpse_name=m.cpse.name if m.cpse else "UNKNOWN",
        material_code=m.material_code,
        original_description=m.original_description,
        normalized_description=m.normalized_description,
        category=m.category,
        source_reference=m.source_reference,
        status=m.status,
        attributes=attr_schema,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


@router.get("/{material_id}/dna", response_model=MaterialDNAResponse, summary="Get material technical DNA")
def get_material_dna(
    material_id: int,
    db: Session = Depends(get_db),
):
    """Get material technical fingerprint and structured attribute extraction breakdown."""
    m = db.query(Material).filter(Material.id == material_id).first()
    if not m:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "MATERIAL_NOT_FOUND", "message": f"Material with ID {material_id} not found."},
        )

    if not m.attributes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DNA_NOT_EXTRACTED", "message": f"DNA attributes have not been extracted for material {material_id}."},
        )

    other = m.attributes.other_attributes or {}
    attr_schema = MaterialAttributeSchema(
        material_type=m.attributes.material_type,
        material=m.attributes.material,
        grade=m.attributes.grade,
        size=m.attributes.size,
        diameter=m.attributes.diameter,
        length=m.attributes.length,
        width=m.attributes.width,
        height=m.attributes.height,
        thickness=m.attributes.thickness,
        pressure=m.attributes.pressure,
        schedule=m.attributes.schedule,
        form=m.attributes.form,
        standard=m.attributes.standard,
        application=m.attributes.application,
        manufacturer=m.attributes.manufacturer,
        confidence_scores=other.get("confidence_scores", {}),
        fingerprint_hash=other.get("fingerprint_hash"),
    )

    return MaterialDNAResponse(
        material_id=m.id,
        material_code=m.material_code,
        original_description=m.original_description,
        normalized_description=m.normalized_description or m.original_description,
        attributes=attr_schema,
        fingerprint_hash=other.get("fingerprint_hash") or "",
        overall_confidence=other.get("overall_confidence", 0.5),
    )


@router.get("/{material_id}/matches", response_model=List[MatchResponse], summary="Get matches for a material")
def get_material_matches(
    material_id: int,
    db: Session = Depends(get_db),
):
    """List all candidate matches involving this material (as source or target)."""
    matches = db.query(MaterialMatch).filter(
        or_(
            MaterialMatch.source_material_id == material_id,
            MaterialMatch.target_material_id == material_id,
        )
    ).all()

    results = []
    for match in matches:
        src = match.source_material
        tgt = match.target_material
        conflicts = [
            ConflictItem(
                id=c.id,
                attribute=c.attribute,
                source_value=c.source_value,
                target_value=c.target_value,
                severity=c.severity,
                reason=c.reason,
                created_at=c.created_at,
            )
            for c in match.conflicts
        ]
        expl_data = match.explanation or {}
        explanation = MatchExplanation(
            why_matched=expl_data.get("why_matched", []),
            what_matched=expl_data.get("what_matched", []),
            what_differed=expl_data.get("what_differed", []),
            recommendation=expl_data.get("recommendation", "REVIEW"),
            review_required=match.review_required,
            confidence=expl_data.get("confidence"),
            technical_conflicts=conflicts,
        )

        results.append(
            MatchResponse(
                id=f"MATCH-{match.id:04d}",
                source_material=MaterialItemReference(
                    id=src.id,
                    cpse=src.cpse.code if src.cpse else "UNKNOWN",
                    code=src.material_code,
                    description=src.original_description,
                    normalized_description=src.normalized_description,
                ),
                target_material=MaterialItemReference(
                    id=tgt.id,
                    cpse=tgt.cpse.code if tgt.cpse else "UNKNOWN",
                    code=tgt.material_code,
                    description=tgt.original_description,
                    normalized_description=tgt.normalized_description,
                ),
                scores=MatchScores(
                    semantic=match.semantic_score,
                    fuzzy=match.fuzzy_score,
                    attribute=match.attribute_score,
                    technical=match.technical_score,
                    final=match.final_score,
                ),
                classification=match.classification,
                technical_conflicts=conflicts,
                explanation=explanation,
                status=match.status,
                review_required=match.review_required,
                created_at=match.created_at,
            )
        )

    return results


@router.get("/{material_id}/conflicts", response_model=List[ConflictDetailResponse], summary="Get conflicts for a material")
def get_material_conflicts(
    material_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve all technical conflicts logged against matches of this material."""
    matches = db.query(MaterialMatch.id).filter(
        or_(
            MaterialMatch.source_material_id == material_id,
            MaterialMatch.target_material_id == material_id,
        )
    ).all()
    match_ids = [m[0] for m in matches]

    if not match_ids:
        return []

    conflicts = db.query(MaterialConflict).filter(MaterialConflict.match_id.in_(match_ids)).all()
    return [
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
        for c in conflicts
    ]
