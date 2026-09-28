"""Schemas module exports."""

from app.schemas.ingestion import IngestionJobResponse, IngestionUploadResponse
from app.schemas.material import MaterialDetailResponse, MaterialSummary, PaginatedMaterialsResponse
from app.schemas.material_dna import MaterialDNAResponse, MaterialAttributeSchema
from app.schemas.matching import (
    MatchResponse,
    MatchScores,
    MatchExplanation,
    RunMatchingRequest,
    RunMatchingResponse,
    StandaloneMatchRequest,
    StandaloneMatchResponse,
    PaginatedMatchesResponse,
)
from app.schemas.conflict import ConflictItem, ConflictDetailResponse, PaginatedConflictsResponse
from app.schemas.cnmc import (
    CreateCNMCRequest,
    CNMCDetailResponse,
    CPSEMappingSummary,
    CanonicalDescriptionSelectionResponse,
    PaginatedCNMCResponse,
)

__all__ = [
    "IngestionJobResponse",
    "IngestionUploadResponse",
    "MaterialDetailResponse",
    "MaterialSummary",
    "PaginatedMaterialsResponse",
    "MaterialDNAResponse",
    "MaterialAttributeSchema",
    "MatchResponse",
    "MatchScores",
    "MatchExplanation",
    "RunMatchingRequest",
    "RunMatchingResponse",
    "StandaloneMatchRequest",
    "StandaloneMatchResponse",
    "PaginatedMatchesResponse",
    "ConflictItem",
    "ConflictDetailResponse",
    "PaginatedConflictsResponse",
    "CreateCNMCRequest",
    "CNMCDetailResponse",
    "CPSEMappingSummary",
    "CanonicalDescriptionSelectionResponse",
    "PaginatedCNMCResponse",
]
