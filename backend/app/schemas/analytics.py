from pydantic import BaseModel
from typing import List, Optional

class OverviewAnalyticsResponse(BaseModel):
    national_materials: int
    active_materials: int
    cpse_count: int
    vendor_count: int
    location_count: int
    total_inventory: float
    total_demand: float
    potential_gap: float
    shortage_signals: int
    surplus_signals: int
    multi_cpse_materials: int
    pending_reviews: int

class CpseAnalyticsResponse(BaseModel):
    cpse: str
    mapped_materials: int
    inventory: float
    demand: float
    shortage_signals: int
    surplus_signals: int

class ExecutiveSummaryResponse(BaseModel):
    national_materials: int
    active_materials: int
    multi_cpse_materials: int
    pending_reviews: int
    shortage_signals: int
    surplus_signals: int
    supplier_count: int
    location_count: int
    top_shared_materials: List[dict]
    top_supply_gap_materials: List[dict]
    top_surplus_materials: List[dict]
    top_multi_cpse_materials: List[dict]

class TrendResponse(BaseModel):
    period: str
    type: str # CURRENT, FORECAST, etc.
    value: float
