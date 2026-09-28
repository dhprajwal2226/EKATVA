from sqlalchemy.orm import Session
from app.models.mock_models import (
    NationalMaterial, CpseMapping, MaterialAttribute, Vendor,
    MaterialVendor, Inventory, Demand, MaterialConflict, MatchResult
)
from datetime import datetime

def seed_demo_data(db: Session):
    # Check if data already exists
    if db.query(NationalMaterial).filter(NationalMaterial.id == "CNMC-000001").first():
        return
        
    # Create National Material
    cnmc1 = NationalMaterial(
        id="CNMC-000001",
        canonical_description="Stainless Steel Hex Bolt M16 x 50 mm",
        category="Fastener",
        status="ACTIVE"
    )
    db.add(cnmc1)
    
    # Create CPSE Mappings
    mappings = [
        CpseMapping(cnmc_id="CNMC-000001", cpse_name="IOCL", cpse_code="IOCL-123", original_description="SS HEX BOLT M16 X 50"),
        CpseMapping(cnmc_id="CNMC-000001", cpse_name="NTPC", cpse_code="NTPC-789", original_description="Bolt Hex SS304 16x50"),
        CpseMapping(cnmc_id="CNMC-000001", cpse_name="BHEL", cpse_code="BHEL-456", original_description="HEX BOLT 16MM 50MM SS")
    ]
    db.add_all(mappings)
    
    # Create Attributes
    attributes = [
        MaterialAttribute(cnmc_id="CNMC-000001", attribute_name="material", attribute_value="Stainless Steel"),
        MaterialAttribute(cnmc_id="CNMC-000001", attribute_name="grade", attribute_value="SS304"),
        MaterialAttribute(cnmc_id="CNMC-000001", attribute_name="diameter_mm", attribute_value="16"),
        MaterialAttribute(cnmc_id="CNMC-000001", attribute_name="length_mm", attribute_value="50"),
        MaterialAttribute(cnmc_id="CNMC-000001", attribute_name="standard", attribute_value="ASTM A193")
    ]
    db.add_all(attributes)
    
    # Create Vendors (8 vendors for demo)
    for i in range(1, 9):
        vendor = Vendor(name=f"Vendor {chr(64+i)}", location=f"City {i}", qualification_status="QUALIFIED")
        db.add(vendor)
        db.flush()
        mv = MaterialVendor(cnmc_id="CNMC-000001", vendor_id=vendor.id)
        db.add(mv)
        
    # Create Inventory (Total 11,500, Reserved 1,500, Available 10,000)
    inv1 = Inventory(cnmc_id="CNMC-000001", location="Warehouse Bengaluru", total_quantity=6000, reserved_quantity=1000)
    inv2 = Inventory(cnmc_id="CNMC-000001", location="Warehouse Chennai", total_quantity=5500, reserved_quantity=500)
    db.add_all([inv1, inv2])
    
    # Create Demand (Current 18,000, Forecast 15,000)
    d1 = Demand(cnmc_id="CNMC-000001", period="CURRENT", demand_type="CURRENT", quantity=18000)
    d2 = Demand(cnmc_id="CNMC-000001", period="2026-Q4", demand_type="FORECAST", quantity=15000)
    db.add_all([d1, d2])
    
    db.commit()
