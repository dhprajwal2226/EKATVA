from sqlalchemy.orm import Session
from app.models.national_material import NationalMaterial
from app.models.cpse_material_mapping import CPSEMaterialMapping
from app.models.mock_models import Vendor, MaterialVendor, Inventory, Demand, MaterialConflict, MatchResult
from datetime import datetime

def seed_demo_data(db: Session):
    # STOPPED: The existing synthetic-data system cannot work safely without
    # creating fake materials in the real national_materials table.
    # Therefore, demo seeding is disabled to prevent contaminating the real material master.
    pass
