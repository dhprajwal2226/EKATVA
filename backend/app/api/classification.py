"""
Classification Rules API Routes.
Exposes engine scoring weights, critical conflict rules, and thresholds for transparency.
SIH 2026 - National Material Master Platform.
"""

from typing import Dict, Any
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/classification", tags=["Classification Rules"])


@router.get("/rules", summary="Get active hybrid matching weights and classification thresholds")
def get_classification_rules() -> Dict[str, Any]:
    """
    Returns current configuration weights and conflict policies:
    SEMANTIC_WEIGHT, FUZZY_WEIGHT, ATTRIBUTE_WEIGHT, TECHNICAL_WEIGHT,
    thresholds, and critical conflict precedence policy.
    """
    return {
        "hybrid_weights": {
            "semantic_weight": settings.SEMANTIC_WEIGHT,
            "fuzzy_weight": settings.FUZZY_WEIGHT,
            "attribute_weight": settings.ATTRIBUTE_WEIGHT,
            "technical_weight": settings.TECHNICAL_WEIGHT,
            "formula": "FINAL = (0.30*semantic) + (0.20*fuzzy) + (0.30*attribute) + (0.20*technical)",
        },
        "thresholds": {
            "identical_threshold": settings.IDENTICAL_THRESHOLD,
            "near_duplicate_threshold": settings.NEAR_DUPLICATE_THRESHOLD,
            "functional_equivalent_threshold": settings.FUNCTIONAL_EQUIVALENT_THRESHOLD,
            "review_threshold": settings.REVIEW_THRESHOLD,
        },
        "critical_conflict_precedence": {
            "rule": "CRITICAL CONFLICT > SIMILARITY SCORE",
            "enforcement": "If ANY critical conflict (e.g. metallurgical grade, major diameter mismatch) is detected, classification is forced to REVIEW_REQUIRED and recommendation is DO_NOT_AUTO_MERGE regardless of similarity percentage.",
            "action": settings.CRITICAL_CONFLICT_BEHAVIOR,
        },
        "embedding_model": settings.EMBEDDING_MODEL,
        "candidate_top_k": settings.CANDIDATE_TOP_K,
    }
