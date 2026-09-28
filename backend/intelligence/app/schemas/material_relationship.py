from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class MaterialRelationshipBase(BaseModel):
    source_national_material_id: str
    target_national_material_id: str
    relationship_type: Optional[str] = None
    confidence: Optional[float] = None
    reason: Optional[str] = None
    source_reference: Optional[str] = None

class MaterialRelationshipCreate(MaterialRelationshipBase):
    pass

class MaterialRelationshipUpdate(MaterialRelationshipBase):
    pass

class MaterialRelationship(MaterialRelationshipBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
