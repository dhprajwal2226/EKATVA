from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class DemandBase(BaseModel):
    national_material_id: str
    cpse_id: str
    location_id: Optional[int] = None
    period: Optional[str] = None
    requested_quantity: float = 0.0
    forecast_quantity: float = 0.0
    fulfilled_quantity: float = 0.0
    unit: Optional[str] = None
    source_reference: Optional[str] = None

class DemandCreate(DemandBase):
    pass

class DemandUpdate(DemandBase):
    pass

class Demand(DemandBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
