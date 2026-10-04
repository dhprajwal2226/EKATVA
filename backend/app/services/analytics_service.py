from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from app.models.national_material import NationalMaterial
from app.models.cpse_material_mapping import CPSEMaterialMapping
from app.models.mock_models import Vendor, MaterialVendor, Inventory, Demand, MatchResult
from app.schemas.analytics import OverviewAnalyticsResponse, CpseAnalyticsResponse, ExecutiveSummaryResponse

def get_overview_analytics(db: Session) -> OverviewAnalyticsResponse:
    national_materials = db.query(NationalMaterial).count()
    active_materials = db.query(NationalMaterial).filter(NationalMaterial.status == "ACTIVE").count()
    
    from app.models.cpse import CPSE
    cpse_count = db.query(CPSE.name).join(CPSEMaterialMapping).distinct().count()
    from sqlalchemy.exc import OperationalError
    
    try:
        vendor_count = db.query(Vendor).count()
        location_count = db.query(Inventory.location).distinct().count()
        total_inventory = db.query(func.sum(Inventory.total_quantity)).scalar() or 0.0
        total_demand = db.query(func.sum(Demand.quantity)).scalar() or 0.0
    except OperationalError:
        vendor_count = 0
        location_count = 0
        total_inventory = 0.0
        total_demand = 0.0
        db.rollback()
    
    materials = db.query(NationalMaterial).all()
    shortage_signals = 0
    surplus_signals = 0
    potential_gap = 0.0
    multi_cpse_materials = 0
    
    for m in materials:
        if len(m.cpse_mappings) > 1:
            multi_cpse_materials += 1
            
        try:
            inventory_recs = db.query(Inventory).filter(Inventory.cnmc_id == m.cnmc).all()
            demand_recs = db.query(Demand).filter(Demand.cnmc_id == m.cnmc).all()
        except OperationalError:
            inventory_recs = []
            demand_recs = []
            db.rollback()
            
        inv = sum(i.total_quantity - i.reserved_quantity for i in inventory_recs)
        dem = sum(d.quantity for d in demand_recs)
        
        if dem > inv:
            shortage_signals += 1
            potential_gap += (dem - inv)
        elif inv > dem and dem > 0:
            surplus_signals += 1
            
    try:
        pending_reviews = db.query(MatchResult).filter(MatchResult.status == "REVIEW_REQUIRED").count()
    except OperationalError:
        pending_reviews = 0
        db.rollback()
    
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
    from app.models.cpse import CPSE
    cpses = db.query(CPSE.name).join(CPSEMaterialMapping).distinct().all()
    results = []
    
    for cpse in cpses:
        cpse_name = cpse[0]
        mappings = db.query(CPSEMaterialMapping).join(CPSE).filter(CPSE.name == cpse_name).all()
        mapped_materials = len(mappings)
        
        inventory = 0.0
        demand = 0.0
        shortage_signals = 0
        surplus_signals = 0
        
        for mapping in mappings:
            m = mapping.national_material
            if not m: continue
            
            try:
                inventory_recs = db.query(Inventory).filter(Inventory.cnmc_id == m.cnmc).all()
                demand_recs = db.query(Demand).filter(Demand.cnmc_id == m.cnmc).all()
            except OperationalError:
                inventory_recs = []
                demand_recs = []
                db.rollback()
                
            inv = sum(i.total_quantity - i.reserved_quantity for i in inventory_recs)
            dem = sum(d.quantity for d in demand_recs)
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
        top_shared_materials=[],
        top_supply_gap_materials=[],
        top_surplus_materials=[],
        top_multi_cpse_materials=[]
    )
