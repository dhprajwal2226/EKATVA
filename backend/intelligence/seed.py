import random
from datetime import datetime
from app.core.database import SessionLocal, Base, engine
from app.models.vendor import Vendor
from app.models.location import Location
from app.models.inventory import Inventory
from app.models.demand import Demand
from app.models.standard import Standard
from app.models.material_relationship import MaterialRelationship

# Create tables
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # Simple seeding logic mimicking constraints
    cpses = ["IOCL", "NTPC", "BHEL", "GAIL"]
    
    for i in range(1, 16):
        db.add(Vendor(vendor_code=f"VEND-{i}", name=f"Synthetic Vendor {i}", city="Bengaluru", status="ACTIVE"))
        
    for i in range(1, 21):
        db.add(Location(name=f"Location {i}", location_type="WAREHOUSE", city="Mumbai", cpse_id=random.choice(cpses)))
        
    for i in range(1, 21):
        db.add(Standard(standard_code=f"STD-{i}", name=f"Synthetic Standard {i}"))
        
    db.commit()

    # Create 20 CNMCs
    for i in range(1, 21):
        cnmc_id = f"CNMC-{i:06d}"
        
        # Add 5 inventory records
        for j in range(5):
            db.add(Inventory(
                national_material_id=cnmc_id,
                cpse_id=random.choice(cpses),
                quantity=1000.0 * j,
                reserved_quantity=100.0 * j,
                available_quantity=900.0 * j,
                source_reference="SYNTHETIC_DEMO"
            ))
            
        # Add 5 demand records
        for j in range(5):
            db.add(Demand(
                national_material_id=cnmc_id,
                cpse_id=random.choice(cpses),
                requested_quantity=1500.0 * j,
                forecast_quantity=1500.0 * j,
                source_reference="SYNTHETIC_DEMO"
            ))
            
    db.commit()
    db.close()
    print("Database seeded with synthetic data successfully.")

if __name__ == "__main__":
    seed_data()
