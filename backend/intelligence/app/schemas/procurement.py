from pydantic import BaseModel
from typing import List, Optional

class SignalDetail(BaseModel):
    signal_type: str
    value: float
    calculation: str
    evidence: List[str]

class ProcurementIntelligence(BaseModel):
    cnmc: str
    demand: float
    available_inventory: float
    potential_gap: float
    supplier_count: int
    cpse_count: int
    status: str
    signals: List[str]
    signal_details: List[SignalDetail]
