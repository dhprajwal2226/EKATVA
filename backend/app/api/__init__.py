"""API router aggregator."""

from fastapi import APIRouter
from app.api.ingestion import router as ingestion_router
from app.api.materials import router as materials_router
from app.api.normalization import router as normalization_router
from app.api.material_dna import router as dna_router
from app.api.matching import router as matching_router
from app.api.conflicts import router as conflicts_router
from app.api.classification import router as classification_router
from app.api.cnmc import router as cnmc_router

api_router = APIRouter()

api_router.include_router(ingestion_router)
api_router.include_router(materials_router)
api_router.include_router(normalization_router)
api_router.include_router(dna_router)
api_router.include_router(matching_router)
api_router.include_router(conflicts_router)
api_router.include_router(classification_router)
api_router.include_router(cnmc_router)

__all__ = ["api_router"]
