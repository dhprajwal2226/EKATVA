from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class StandardBase(BaseModel):
    standard_code: str
    name: Optional[str] = None
    issuing_body: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None

class StandardCreate(StandardBase):
    pass

class StandardUpdate(StandardBase):
    pass

class Standard(StandardBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
