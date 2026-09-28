from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class InventoryBase(BaseModel):
    national_material_id: str
    cpse_id: str
    location_id: Optional[int] = None
    quantity: float = 0.0
    reserved_quantity: float = 0.0
    available_quantity: float = 0.0
    unit: Optional[str] = None
    as_of_date: Optional[datetime] = None
    source_reference: Optional[str] = None

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(InventoryBase):
    pass

class Inventory(InventoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
