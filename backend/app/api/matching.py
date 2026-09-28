"""
Matching API Routes.
Executes candidate generation, hybrid matching, explainable comparison, and match retrieval.
SIH 2026 - National Material Master Platform.
"""

import math
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.database import get_db
from app.models.material_match import MaterialMatch
from app.models.material import Material
from app.models.cpse import CPSE
from app.schemas.matching import (
    MatchResponse,
    MaterialItemReference,
    MatchScores,
    MatchExplanation,
    RunMatchingRequest,
    RunMatchingResponse,
    StandaloneMatchRequest,
    StandaloneMatchResponse,
    PaginatedMatchesResponse,
)
from app.schemas.conflict import ConflictItem
from app.services.matching_service import MatchingService

router = APIRouter(prefix="/matching", tags=["Matching & Intelligence Engine"])


@router.post(
    "/run",
    response_model=RunMatchingResponse,
    summary="Run full candidate blocking and hybrid matching pipeline across CPSE materials",
)
def run_batch_matching(
    payload: RunMatchingRequest,
    db: Session = Depends(get_db),
):
    """
    Executes the complete matching pipeline:
    1. Candidate generation using domain blocking (avoids O(N²))
    2. Vector semantic similarity search
    3. Multi-strategy RapidFuzz lexical analysis
    4. Structured attribute matrix evaluation
    5. Technical conflict engine (enforcing: CRITICAL CONFLICT > SIMILARITY SCORE)
    6. Persists matches with status PENDING_REVIEW
    """
    result = MatchingService.run_pipeline(db, limit_materials=payload.limit_materials)
    return RunMatchingResponse(
        message="Matching pipeline executed successfully.",
        total_pairs_evaluated=result["total_pairs_evaluated"],
        matches_recorded=result["matches_recorded"],
        conflicts_detected=result["conflicts_detected"],
        classifications_tally=result["classifications_tally"],
    )


@router.post(
    "/compare",
    response_model=StandaloneMatchResponse,
    summary="Compare two descriptions on-the-fly with full technical explainability",
)
def compare_descriptions_adhoc(payload: StandaloneMatchRequest):
    """
    Compare any two raw descriptions directly.
    Computes semantic score, fuzzy score, extracted DNA attributes,
    technical conflicts, and explainable recommendation.
    """
    res = MatchingService.compare_pair(
        source_desc=payload.source_description,
        target_desc=payload.target_description,
    )

    conflicts = [
        ConflictItem(
            attribute=c["attribute"],
            source_value=c.get("source_value"),
            target_value=c.get("target_value"),
            severity=c["severity"],
            reason=c["reason"],
        )
        for c in res["technical_conflicts"]
    ]

    expl_data = res["explanation"]
    explanation = MatchExplanation(
        why_matched=expl_data.get("why_matched", []),
        what_matched=expl_data.get("what_matched", []),
        what_differed=expl_data.get("what_differed", []),
        recommendation=expl_data.get("recommendation", "REVIEW"),
        review_required=res["review_required"],
        confidence=res["confidence"],
        technical_conflicts=conflicts,
    )

    return StandaloneMatchResponse(
        source_description=payload.source_description,
        target_description=payload.target_description,
        scores=MatchScores(
            semantic=res["scores"]["semantic"],
            fuzzy=res["scores"]["fuzzy"],
            attribute=res["scores"]["attribute"],
            technical=res["scores"]["technical"],
            final=res["scores"]["final"],
        ),
        classification=res["classification"],
        review_required=res["review_required"],
        recommendation=res["recommendation"],
        confidence=res["confidence"],
        technical_conflicts=conflicts,
        explanation=explanation,
    )


@router.get("", response_model=PaginatedMatchesResponse, summary="List and filter material matches")
def list_matches(
    cpse: Optional[str] = Query(None, description="Filter by CPSE code of source or target material"),
    classification: Optional[str] = Query(None, description="Filter by classification (IDENTICAL, NEAR_DUPLICATE, etc.)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by match status (PENDING_REVIEW, etc.)"),
    review_required: Optional[bool] = Query(None, description="Filter by review_required flag"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Retrieve paginated matches with rich filters for human reviewer dashboard."""
    query = db.query(MaterialMatch)

    if classification:
        query = query.filter(MaterialMatch.classification == classification.strip())

    if status_filter:
        query = query.filter(MaterialMatch.status == status_filter.strip())

    if review_required is not None:
        query = query.filter(MaterialMatch.review_required == review_required)

    if cpse:
        cpse_code = cpse.strip().upper()
        query = query.join(Material, MaterialMatch.source_material_id == Material.id).join(CPSE).filter(CPSE.code == cpse_code)

    total = query.count()
    matches_raw = query.order_by(MaterialMatch.final_score.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for match in matches_raw:
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

        items.append(
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

    return PaginatedMatchesResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 1,
    )


@router.get("/{match_id}", response_model=MatchResponse, summary="Get single match by ID")
def get_match_detail(
    match_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve full explainable match details including conflict items."""
    match = db.query(MaterialMatch).filter(MaterialMatch.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "MATCH_NOT_FOUND", "message": f"Match with ID {match_id} not found."},
        )

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

    return MatchResponse(
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
