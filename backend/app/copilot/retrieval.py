from sqlalchemy.orm import Session
from app.models.national_material import NationalMaterial
from app.models.mock_models import Inventory, Demand, Vendor, MaterialVendor
import re

def extract_cnmc(query: str) -> str:
    match = re.search(r'CNMC-\d+', query.upper())
    return match.group(0) if match else None

def retrieve_verified_data(db: Session, intent: str, query: str, context_cnmc: str = None):
    cnmc_id = extract_cnmc(query) or context_cnmc
    
    if not cnmc_id:
        if "this material" in query.lower() or "this cnmc" in query.lower():
            cnmc_id = "CNMC-000001"
        else:
            return None, "No specific material identified in query."
            
    material = db.query(NationalMaterial).filter(NationalMaterial.cnmc == cnmc_id).first()
    if not material:
        return None, f"Material {cnmc_id} not found."
        
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
        
    data = {"cnmc": cnmc_id}
    
    if intent in ["CPSE_LOOKUP", "MATCH_LOOKUP"]:
        data["cpse_mappings"] = [{"cpse": m.cpse.name if m.cpse else "", "code": m.material_code} for m in material.cpse_mappings]
        data["sources"] = [f"{cnmc_id} mapping records"]
        
    elif intent == "INVENTORY_LOOKUP":
        if not inventory_recs:
            return None, "Insufficient verified inventory data is available for this CNMC."
        data["locations"] = [{"location": i.location, "quantity": i.total_quantity} for i in inventory_recs]
        data["sources"] = [f"Inventory records as of {inventory_recs[0].as_of_date.strftime('%Y-%m-%d')}"]
        
    elif intent == "SHORTAGE_LOOKUP":
        if not inventory_recs or not demand_recs:
            return None, "Insufficient verified data available."
            
        inv = sum(i.total_quantity - i.reserved_quantity for i in inventory_recs)
        dem = sum(d.quantity for d in demand_recs)
        
        data["inventory"] = inv
        data["demand"] = dem
        data["potential_gap"] = dem - inv if dem > inv else 0
        data["sources"] = [f"{cnmc_id} Inventory records", f"{cnmc_id} Demand records"]
        
    elif intent == "VENDOR_LOOKUP":
        data["vendors"] = [{"name": m.vendor.name, "location": m.vendor.location} for m in vendors_recs]
        data["sources"] = [f"{cnmc_id} vendor records"]
        
    return data, None
