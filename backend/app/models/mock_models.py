from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.orm import declarative_base

# Separate Base so these demo tables never collide with the real ai models
Base = declarative_base()

# --- Person 2: National Material Master ---
class NationalMaterial(Base):
    __tablename__ = "ds_national_materials"
    
    id = Column(String, primary_key=True, index=True) # e.g. CNMC-000001
    canonical_description = Column(String)
    category = Column(String)
    status = Column(String, default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attributes = relationship("MaterialAttribute", back_populates="material")
    cpse_mappings = relationship("CpseMapping", back_populates="material")
    inventory = relationship("Inventory", back_populates="material")
    demand = relationship("Demand", back_populates="material")
    vendors = relationship("MaterialVendor", back_populates="material")

class CpseMapping(Base):
    __tablename__ = "ds_cpse_material_mappings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cnmc_id = Column(String, ForeignKey("ds_national_materials.id"))
    cpse_name = Column(String)
    cpse_code = Column(String)
    original_description = Column(String)
    mapping_status = Column(String, default="APPROVED")
    
    material = relationship("NationalMaterial", back_populates="cpse_mappings")

# --- Person 1: Core Material AI ---
class MaterialAttribute(Base):
    __tablename__ = "ds_material_attributes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cnmc_id = Column(String, ForeignKey("ds_national_materials.id"))
    attribute_name = Column(String) # e.g. material, grade, diameter_mm, standard
    attribute_value = Column(String)
    
    material = relationship("NationalMaterial", back_populates="attributes")

class MaterialConflict(Base):
    __tablename__ = "ds_material_conflicts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cnmc_id = Column(String, ForeignKey("ds_national_materials.id"))
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
    cnmc_id = Column(String, ForeignKey("ds_national_materials.id"))
    vendor_id = Column(Integer, ForeignKey("ds_vendors.id"))
    
    material = relationship("NationalMaterial", back_populates="vendors")
    vendor = relationship("Vendor")

class Inventory(Base):
    __tablename__ = "ds_inventory"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cnmc_id = Column(String, ForeignKey("ds_national_materials.id"))
    location = Column(String)
    total_quantity = Column(Float)
    reserved_quantity = Column(Float)
    as_of_date = Column(DateTime, default=datetime.utcnow)
    
    material = relationship("NationalMaterial", back_populates="inventory")

class Demand(Base):
    __tablename__ = "ds_demand"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cnmc_id = Column(String, ForeignKey("ds_national_materials.id"))
    period = Column(String) # e.g. "2026-Q4"
    demand_type = Column(String) # CURRENT, FORECAST
    quantity = Column(Float)
    
    material = relationship("NationalMaterial", back_populates="demand")
