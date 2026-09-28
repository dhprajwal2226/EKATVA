from pydantic import BaseModel
from typing import List

class CanonicalMaterialSchema(BaseModel):
    description: str
    category: str

class IntegrationCpseMappingSchema(BaseModel):
    cpse: str
    material_code: str

class IntegrationMaterialResponse(BaseModel):
    cnmc: str
    canonical_material: CanonicalMaterialSchema
    cpse_mappings: List[IntegrationCpseMappingSchema]
    status: str
