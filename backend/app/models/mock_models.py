from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.orm import declarative_base

# Separate Base so these demo tables never collide with the real ai models
Base = declarative_base()

# Removed NationalMaterial, CpseMapping, MaterialAttribute as they are now in app.models.national_material and app.models.cpse_material_mapping.

class MaterialConflict(Base):
    __tablename__ = "ds_material_conflicts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cnmc_id = Column(String, ForeignKey("national_materials.cnmc"))
    conflict_type = Column(String) # e.g. Grade, Dimension
    description = Column(String)
    status = Column(String, default="UNRESOLVED") # RESOLVED, UNRESOLVED

class MatchResult(Base):
    __tablename__ = "ds_material_matches"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_cpse = Column(String)
    source_code = Column(String)
    target_cnmc = Column(String)
    match_type = Column(String) # IDENTICAL, NEAR_DUPLICATE, DIFFERENT
    confidence = Column(Float)
    status = Column(String) # APPROVED, REJECTED, REVIEW_REQUIRED

# --- Person 3: National Material Intelligence ---
class Vendor(Base):
    __tablename__ = "ds_vendors"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    location = Column(String)
    qualification_status = Column(String)

class MaterialVendor(Base):
    __tablename__ = "ds_material_vendors"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cnmc_id = Column(String, ForeignKey("national_materials.cnmc"))
    vendor_id = Column(Integer, ForeignKey("ds_vendors.id"))
    
    vendor = relationship("Vendor")

class Inventory(Base):
    __tablename__ = "ds_inventory"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cnmc_id = Column(String, ForeignKey("national_materials.cnmc"))
    location = Column(String)
    total_quantity = Column(Float)
    reserved_quantity = Column(Float)
    as_of_date = Column(DateTime, default=datetime.utcnow)

class Demand(Base):
    __tablename__ = "ds_demand"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cnmc_id = Column(String, ForeignKey("national_materials.cnmc"))
    period = Column(String) # e.g. "2026-Q4"
    demand_type = Column(String) # CURRENT, FORECAST
    quantity = Column(Float)
