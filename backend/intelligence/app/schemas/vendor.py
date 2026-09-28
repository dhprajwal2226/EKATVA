from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class VendorBase(BaseModel):
    vendor_code: str
    name: str
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    vendor_type: Optional[str] = None
    status: Optional[str] = None

class VendorCreate(VendorBase):
    pass

class VendorUpdate(VendorBase):
    pass

class Vendor(VendorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
