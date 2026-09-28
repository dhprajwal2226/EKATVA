from sqlalchemy.orm import Session
from app.models.mock_models import (
    NationalMaterial, CpseMapping, MaterialAttribute,
    MaterialVendor, Inventory, Demand
)
from app.schemas.passport import MaterialPassportResponse

def get_material_passport(db: Session, cnmc_id: str) -> MaterialPassportResponse:
    material = db.query(NationalMaterial).filter(NationalMaterial.id == cnmc_id).first()
    if not material:
        return None

    attributes = {attr.attribute_name: attr.attribute_value for attr in material.attributes}
    
    cpse_mappings = [
        {"cpse": mapping.cpse_name, "code": mapping.cpse_code}
        for mapping in material.cpse_mappings
    ]

    # Inventory calculation
    total_inventory = sum(inv.total_quantity for inv in material.inventory)
    total_reserved = sum(inv.reserved_quantity for inv in material.inventory)
    total_available = total_inventory - total_reserved

    # Vendor calculation
    vendor_count = len(material.vendors)
    
    # Demand calculation
    current_demand = sum(d.quantity for d in material.demand if d.demand_type == "CURRENT")
    forecast_demand = sum(d.quantity for d in material.demand if d.demand_type == "FORECAST")
    total_demand_val = current_demand + forecast_demand

    # Intelligence calculation
    if not material.inventory and not material.demand:
        signal = "INSUFFICIENT_DATA"
        potential_gap = None
        potential_surplus = None
    elif not material.inventory:
        signal = "INSUFFICIENT_DATA"
        potential_gap = None
        potential_surplus = None
    elif not material.demand:
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
    location_count = len(set(inv.location for inv in material.inventory))
    
    return MaterialPassportResponse(
        cnmc=material.id,
        status=material.status,
        identity={
            "description": material.canonical_description,
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
