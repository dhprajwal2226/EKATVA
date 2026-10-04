from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    employee_id: str
    name: str
    email: str
    role: str
    department: Optional[str] = None
    cpse_id: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True
