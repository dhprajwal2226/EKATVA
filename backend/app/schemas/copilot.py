from pydantic import BaseModel
from typing import List, Optional

class CopilotRequest(BaseModel):
    query: str
    cnmc_id: Optional[str] = None # Optional context

class CopilotResponse(BaseModel):
    answer: str
    key_findings: List[str]
    sources: List[str]
    data_limitation: Optional[str] = None
    intent: str
