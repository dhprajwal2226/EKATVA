from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class IdentitySchema(BaseModel):
    description: str
    category: str

class CpseMappingSchema(BaseModel):
    cpse: str
    code: str

class SupplySchema(BaseModel):
    inventory: float
    reserved: float
    available: float
    vendor_count: int

class DemandSchema(BaseModel):
    current: float
    forecast: float

class IntelligenceSchema(BaseModel):
    potential_gap: Optional[float] = None
    potential_surplus: Optional[float] = None
    signal: str

class GraphSummarySchema(BaseModel):
    cpse_count: int
    vendor_count: int
    location_count: int

class MaterialPassportResponse(BaseModel):
    cnmc: str
    status: str
    identity: IdentitySchema
    technical_attributes: Dict[str, Any]
    cpse_mappings: List[CpseMappingSchema]
    supply: SupplySchema
    demand: DemandSchema
    intelligence: IntelligenceSchema
    graph_summary: GraphSummarySchema
