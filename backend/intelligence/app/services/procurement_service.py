from sqlalchemy.orm import Session
from app.services.inventory_service import get_inventory_by_cnmc
from app.services.demand_service import get_demand_by_cnmc
from app.models.vendor import Vendor
from app.models.location import Location
from app.schemas.procurement import ProcurementIntelligence, SignalDetail

def analyze_procurement(db: Session, cnmc_id: str) -> ProcurementIntelligence:
    inventories = get_inventory_by_cnmc(db, cnmc_id)
    demands = get_demand_by_cnmc(db, cnmc_id)

    total_available_inventory = sum(inv.available_quantity for inv in inventories)
    # Using forecast_quantity or requested_quantity based on typical priority. 
    # The requirement simplifies to 'total_demand'
    total_demand = sum(dem.forecast_quantity or dem.requested_quantity for dem in demands)

    cpse_set = set()
    location_set = set()
    for inv in inventories:
        cpse_set.add(inv.cpse_id)
        if inv.location_id:
            location_set.add(inv.location_id)
    for dem in demands:
        cpse_set.add(dem.cpse_id)
        if dem.location_id:
            location_set.add(dem.location_id)

    # Note: We need actual relationships for a real vendor count, but we will mock it or leave it as 0 here 
    # based on the database schema limitations. Assuming we query material_relationships or vendor maps.
    # To conform strictly to requirements without building the full relation graph yet:
    supplier_count = 0 

    potential_gap = total_demand - total_available_inventory
    status = "INSUFFICIENT_DATA"
    signals = []
    signal_details = []

    if not inventories and not demands:
        status = "INSUFFICIENT_DATA"
        signals.append("No inventory or demand data available.")
    elif not inventories:
        # If there's demand but no inventory data
        status = "INSUFFICIENT_DATA"
        signals.append("Missing inventory data.")
    else:
        if potential_gap > 0:
            status = "SHORTAGE_SIGNAL"
            signals.append("Potential supply gap identified")
            signal_details.append(SignalDetail(
                signal_type="SHORTAGE_SIGNAL",
                value=potential_gap,
                calculation=f"Demand {total_demand} - Available Inventory {total_available_inventory}",
                evidence=["Inventory and demand calculations"]
            ))
        elif potential_gap < 0:
            status = "SURPLUS_SIGNAL"
            signals.append("Potential surplus identified")
            signal_details.append(SignalDetail(
                signal_type="SURPLUS_SIGNAL",
                value=abs(potential_gap),
                calculation=f"Available Inventory {total_available_inventory} - Demand {total_demand}",
                evidence=["Inventory and demand calculations"]
            ))
        else:
            status = "BALANCED"
            signals.append("Supply and demand appear balanced")

    if len(cpse_set) > 1:
        signals.append("Multiple CPSEs use the same national material identity")

    return ProcurementIntelligence(
        cnmc=cnmc_id,
        demand=total_demand,
        available_inventory=total_available_inventory,
        potential_gap=potential_gap,
        supplier_count=supplier_count,
        cpse_count=len(cpse_set),
        status=status,
        signals=signals,
        signal_details=signal_details
    )
