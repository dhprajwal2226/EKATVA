"""
CNMC (Common National Material Code) API Routes.
Manages national material identifiers and CPSE mapping links.
SIH 2026 - National Material Master Platform.
"""

import math
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.national_material import NationalMaterial
from app.models.cpse_material_mapping import CPSEMaterialMapping
from app.models.material import Material
from app.schemas.cnmc import (
    CreateCNMCRequest,
    CNMCDetailResponse,
    CPSEMappingSummary,
    CanonicalDescriptionSelectionResponse,
    PaginatedCNMCResponse,
)
from app.services.cnmc_service import CNMCService

router = APIRouter(prefix="/cnmc", tags=["CNMC & National Master"])


@router.post("", response_model=CNMCDetailResponse, summary="Generate or retrieve CNMC for material cluster")
def create_or_assign_cnmc(
    payload: CreateCNMCRequest,
    db: Session = Depends(get_db),
):
    """
    Cluster accepted materials under a stable, collision-safe CNMC.
    1. Selects the highest quality canonical description
    2. Hashes canonical attributes into a SHA-256 fingerprint
    3. Issues or matches CNMC (e.g. CNMC-000001)
    4. Establishes CPSE mapping links
    """
    materials = db.query(Material).filter(Material.id.in_(payload.material_ids)).all()
    if not materials:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "MATERIALS_NOT_FOUND", "message": "No matching materials found for provided IDs."},
        )

    # Pick the strongest canonical description
    canonical_selection = CNMCService.select_canonical_description(materials)
    best_mat = next(m for m in materials if m.id == canonical_selection["selected_material_id"])

    # Aggregate canonical attributes from best candidate
    attr = best_mat.attributes
    canonical_attrs = {
        "material_type": attr.material_type if attr else None,
        "material": attr.material if attr else None,
        "grade": attr.grade if attr else None,
        "diameter": attr.diameter if attr else None,
        "length": attr.length if attr else None,
        "pressure": attr.pressure if attr else None,
        "schedule": attr.schedule if attr else None,
        "form": attr.form if attr else None,
        "standard": attr.standard if attr else None,
    }

    # Generate or reuse CNMC
    nat_mat = CNMCService.generate_or_get_cnmc(
        db=db,
        canonical_attributes=canonical_attrs,
        standard_description=canonical_selection["standard_description"],
        category=payload.category or best_mat.category,
        status="DRAFT",
    )

    # Establish CPSE mappings
    for m in materials:
        CNMCService.map_cpse_material(
            db=db,
            national_material_id=nat_mat.id,
            cpse_id=m.cpse_id,
            material_id=m.id,
            mapping_type="IDENTICAL",
        )

    # Refresh mappings
    mappings = [
        CPSEMappingSummary(
            id=map_item.id,
            cpse_code=map_item.cpse.code if map_item.cpse else "UNKNOWN",
            material_id=map_item.material_id,
            material_code=map_item.material.material_code,
            original_description=map_item.material.original_description,
            mapping_type=map_item.mapping_type,
            created_at=map_item.created_at,
        )
        for map_item in nat_mat.cpse_mappings
    ]

    return CNMCDetailResponse(
        id=nat_mat.id,
        cnmc=nat_mat.cnmc,
        standard_description=nat_mat.standard_description,
        category=nat_mat.category,
        canonical_attributes=nat_mat.canonical_attributes,
        identity_hash=nat_mat.identity_hash,
        status=nat_mat.status,
        created_at=nat_mat.created_at,
        updated_at=nat_mat.updated_at,
        mappings=mappings,
    )


@router.get("", response_model=PaginatedCNMCResponse, summary="List all national material CNMC records")
def list_cnmc(
    category: Optional[str] = Query(None, description="Filter by category"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (DRAFT, ACTIVE, etc.)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Retrieve paginated catalog of all issued Common National Material Codes."""
    query = db.query(NationalMaterial)

    if category:
        query = query.filter(NationalMaterial.category == category.strip())

    if status_filter:
        query = query.filter(NationalMaterial.status == status_filter.strip())

    total = query.count()
    records = query.order_by(NationalMaterial.id.asc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for r in records:
        mappings = [
            CPSEMappingSummary(
                id=map_item.id,
                cpse_code=map_item.cpse.code if map_item.cpse else "UNKNOWN",
                material_id=map_item.material_id,
                material_code=map_item.material.material_code,
                original_description=map_item.material.original_description,
                mapping_type=map_item.mapping_type,
                created_at=map_item.created_at,
            )
            for map_item in r.cpse_mappings
        ]
        items.append(
            CNMCDetailResponse(
                id=r.id,
                cnmc=r.cnmc,
                standard_description=r.standard_description,
                category=r.category,
                canonical_attributes=r.canonical_attributes,
                identity_hash=r.identity_hash,
                status=r.status,
                created_at=r.created_at,
                updated_at=r.updated_at,
                mappings=mappings,
            )
        )

    return PaginatedCNMCResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 1,
    )


@router.get("/{cnmc_id}", response_model=CNMCDetailResponse, summary="Get CNMC record details")
def get_cnmc_detail(
    cnmc_id: int,
    db: Session = Depends(get_db),
):
    """Get single National Material record by its internal integer ID."""
    r = db.query(NationalMaterial).filter(NationalMaterial.id == cnmc_id).first()
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CNMC_NOT_FOUND", "message": f"National Material with ID {cnmc_id} not found."},
        )

    mappings = [
        CPSEMappingSummary(
            id=map_item.id,
            cpse_code=map_item.cpse.code if map_item.cpse else "UNKNOWN",
            material_id=map_item.material_id,
            material_code=map_item.material.material_code,
            original_description=map_item.material.original_description,
            mapping_type=map_item.mapping_type,
            created_at=map_item.created_at,
        )
        for map_item in r.cpse_mappings
    ]

    return CNMCDetailResponse(
        id=r.id,
        cnmc=r.cnmc,
        standard_description=r.standard_description,
        category=r.category,
        canonical_attributes=r.canonical_attributes,
        identity_hash=r.identity_hash,
        status=r.status,
        created_at=r.created_at,
        updated_at=r.updated_at,
        mappings=mappings,
    )


@router.get("/{cnmc_id}/mappings", response_model=List[CPSEMappingSummary], summary="Get CPSE mappings for CNMC")
def get_cnmc_mappings(
    cnmc_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve all linked enterprise material items under a national code."""
    r = db.query(NationalMaterial).filter(NationalMaterial.id == cnmc_id).first()
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CNMC_NOT_FOUND", "message": f"National Material with ID {cnmc_id} not found."},
        )

    return [
        CPSEMappingSummary(
            id=map_item.id,
            cpse_code=map_item.cpse.code if map_item.cpse else "UNKNOWN",
            material_id=map_item.material_id,
            material_code=map_item.material.material_code,
            original_description=map_item.material.original_description,
            mapping_type=map_item.mapping_type,
            created_at=map_item.created_at,
        )
        for map_item in r.cpse_mappings
    ]
