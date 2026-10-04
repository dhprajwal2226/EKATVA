from sqlalchemy.orm import Session
from app.models.national_material import NationalMaterial
from app.models.mock_models import (
    MaterialVendor, Inventory, Demand
)
from app.schemas.passport import MaterialPassportResponse

def get_material_passport(db: Session, cnmc_id: str) -> MaterialPassportResponse:
    material = db.query(NationalMaterial).filter(NationalMaterial.cnmc == cnmc_id).first()
    if not material:
        return None

    attributes = material.canonical_attributes or {}
    
    cpse_mappings = [
        {"cpse": mapping.cpse.name if mapping.cpse else "", "code": mapping.material_code}
        for mapping in material.cpse_mappings
    ]

    from sqlalchemy.exc import OperationalError
    try:
        inventory_recs = db.query(Inventory).filter(Inventory.cnmc_id == cnmc_id).all()
        demand_recs = db.query(Demand).filter(Demand.cnmc_id == cnmc_id).all()
        vendors_recs = db.query(MaterialVendor).filter(MaterialVendor.cnmc_id == cnmc_id).all()
    except OperationalError:
        inventory_recs = []
        demand_recs = []
        vendors_recs = []
        db.rollback()

    # Inventory calculation
    total_inventory = sum(inv.total_quantity for inv in inventory_recs)
    total_reserved = sum(inv.reserved_quantity for inv in inventory_recs)
    total_available = total_inventory - total_reserved

    # Vendor calculation
    vendor_count = len(vendors_recs)
    
    # Demand calculation
    current_demand = sum(d.quantity for d in demand_recs if d.demand_type == "CURRENT")
    forecast_demand = sum(d.quantity for d in demand_recs if d.demand_type == "FORECAST")
    total_demand_val = current_demand + forecast_demand

    # Intelligence calculation
    if not inventory_recs and not demand_recs:
        signal = "INSUFFICIENT_DATA"
        potential_gap = None
        potential_surplus = None
    elif not inventory_recs:
        signal = "INSUFFICIENT_DATA"
        potential_gap = None
        potential_surplus = None
    elif not demand_recs:
        signal = "INSUFFICIENT_DATA"
        potential_gap = None
        potential_surplus = None
    else:
        if total_demand_val > total_available:
            signal = "SHORTAGE_SIGNAL"
            potential_gap = total_demand_val - total_available
            potential_surplus = None
        elif total_available > total_demand_val:
            signal = "SURPLUS_SIGNAL"
            potential_surplus = total_available - total_demand_val
            potential_gap = None
        else:
            signal = "BALANCED"
            potential_gap = 0
            potential_surplus = 0

    # Graph summary
    location_count = len(set(inv.location for inv in inventory_recs))
    
    return MaterialPassportResponse(
        cnmc=material.cnmc,
        status=material.status,
        identity={
            "description": material.standard_description,
            "category": material.category
        },
        technical_attributes=attributes,
        cpse_mappings=cpse_mappings,
        supply={
            "inventory": total_inventory,
            "reserved": total_reserved,
            "available": total_available,
            "vendor_count": vendor_count
        },
        demand={
            "current": current_demand,
            "forecast": forecast_demand
        },
        intelligence={
            "potential_gap": potential_gap,
            "potential_surplus": potential_surplus,
            "signal": signal
        },
        graph_summary={
            "cpse_count": len(cpse_mappings),
            "vendor_count": vendor_count,
            "location_count": location_count
        }
    )
