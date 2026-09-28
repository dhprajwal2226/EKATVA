from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from app.core.database import Base

class Demand(Base):
    __tablename__ = "demand"

    id = Column(Integer, primary_key=True, index=True)
    national_material_id = Column(String, index=True, nullable=False)
    cpse_id = Column(String, index=True, nullable=False)
    location_id = Column(Integer, index=True)
    period = Column(String, index=True) # e.g. "2026-Q4"
    requested_quantity = Column(Float, default=0.0)
    forecast_quantity = Column(Float, default=0.0)
    fulfilled_quantity = Column(Float, default=0.0)
    unit = Column(String)
    source_reference = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
