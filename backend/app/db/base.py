"""Alembic and database Base aggregator."""

from app.db.database import Base
from app.models.cpse import CPSE
from app.models.material import Material
from app.models.material_attribute import MaterialAttribute
from app.models.material_embedding import MaterialEmbedding
from app.models.material_match import MaterialMatch
from app.models.material_conflict import MaterialConflict
from app.models.national_material import NationalMaterial
from app.models.cpse_material_mapping import CPSEMaterialMapping
from app.models.ingestion_job import IngestionJob

__all__ = [
    "Base",
    "CPSE",
    "Material",
    "MaterialAttribute",
    "MaterialEmbedding",
    "MaterialMatch",
    "MaterialConflict",
    "NationalMaterial",
    "CPSEMaterialMapping",
    "IngestionJob",
]
