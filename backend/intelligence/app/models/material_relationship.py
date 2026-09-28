from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from app.core.database import Base

class MaterialRelationship(Base):
    __tablename__ = "material_relationships"

    id = Column(Integer, primary_key=True, index=True)
    source_national_material_id = Column(String, index=True, nullable=False)
    target_national_material_id = Column(String, index=True, nullable=False)
    relationship_type = Column(String, index=True) # RELATED_MATERIAL, ALTERNATIVE, etc.
    confidence = Column(Float)
    reason = Column(String)
    source_reference = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
