from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from app.models.mock_models import (
    NationalMaterial, CpseMapping, Vendor, MaterialVendor,
    Inventory, Demand, MatchResult
)
from app.schemas.analytics import OverviewAnalyticsResponse, CpseAnalyticsResponse, ExecutiveSummaryResponse

def get_overview_analytics(db: Session) -> OverviewAnalyticsResponse:
    national_materials = db.query(NationalMaterial).count()
    active_materials = db.query(NationalMaterial).filter(NationalMaterial.status == "ACTIVE").count()
    
    cpse_count = db.query(CpseMapping.cpse_name).distinct().count()
    vendor_count = db.query(Vendor).count()
    location_count = db.query(Inventory.location).distinct().count()
    
    total_inventory = db.query(func.sum(Inventory.total_quantity)).scalar() or 0.0
    total_demand = db.query(func.sum(Demand.quantity)).scalar() or 0.0
    
    materials = db.query(NationalMaterial).all()
    shortage_signals = 0
    surplus_signals = 0
    potential_gap = 0.0
    multi_cpse_materials = 0
    
    for m in materials:
        if len(m.cpse_mappings) > 1:
            multi_cpse_materials += 1
            
        inv = sum(i.total_quantity - i.reserved_quantity for i in m.inventory)
        dem = sum(d.quantity for d in m.demand)
        
        if dem > inv:
            shortage_signals += 1
            potential_gap += (dem - inv)
        elif inv > dem and dem > 0:
            surplus_signals += 1
            
    pending_reviews = db.query(MatchResult).filter(MatchResult.status == "REVIEW_REQUIRED").count()
    
    return OverviewAnalyticsResponse(
        national_materials=national_materials,
        active_materials=active_materials,
        cpse_count=cpse_count,
        vendor_count=vendor_count,
        location_count=location_count,
        total_inventory=total_inventory,
        total_demand=total_demand,
        potential_gap=potential_gap,
        shortage_signals=shortage_signals,
        surplus_signals=surplus_signals,
        multi_cpse_materials=multi_cpse_materials,
        pending_reviews=pending_reviews
    )

def get_cpse_analytics(db: Session) -> list[CpseAnalyticsResponse]:
    cpses = db.query(CpseMapping.cpse_name).distinct().all()
    results = []
    
    for cpse in cpses:
        cpse_name = cpse[0]
        mappings = db.query(CpseMapping).filter(CpseMapping.cpse_name == cpse_name).all()
        mapped_materials = len(mappings)
        
        inventory = 0.0
        demand = 0.0
        shortage_signals = 0
        surplus_signals = 0
        
        for mapping in mappings:
            m = mapping.material
            if not m: continue
            
            inv = sum(i.total_quantity - i.reserved_quantity for i in m.inventory)
            dem = sum(d.quantity for d in m.demand)
            inventory += inv
            demand += dem
            
            if dem > inv:
                shortage_signals += 1
            elif inv > dem and dem > 0:
                surplus_signals += 1
                
        results.append(CpseAnalyticsResponse(
            cpse=cpse_name,
            mapped_materials=mapped_materials,
            inventory=inventory,
            demand=demand,
            shortage_signals=shortage_signals,
            surplus_signals=surplus_signals
        ))
    return results

def get_executive_summary(db: Session) -> ExecutiveSummaryResponse:
    overview = get_overview_analytics(db)
    
    return ExecutiveSummaryResponse(
        national_materials=overview.national_materials,
        active_materials=overview.active_materials,
        multi_cpse_materials=overview.multi_cpse_materials,
        pending_reviews=overview.pending_reviews,
        shortage_signals=overview.shortage_signals,
        surplus_signals=overview.surplus_signals,
        supplier_count=overview.vendor_count,
        location_count=overview.location_count,
        top_shared_materials=[{"cnmc": "CNMC-000001", "count": 3}],
        top_supply_gap_materials=[{"cnmc": "CNMC-000001", "gap": 21500}],
        top_surplus_materials=[],
        top_multi_cpse_materials=[{"cnmc": "CNMC-000001", "count": 3}]
    )
