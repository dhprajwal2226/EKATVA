"""Ingestion Job Tracking Model."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from app.db.database import Base


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    cpse_id = Column(Integer, ForeignKey("cpse.id"), nullable=True)
    
    status = Column(
        String(50),
        nullable=False,
        default="QUEUED",
        index=True,
    )  # QUEUED, PROCESSING, COMPLETED, PARTIAL_SUCCESS, FAILED

    total_rows = Column(Integer, default=0, nullable=False)
    processed_rows = Column(Integer, default=0, nullable=False)
    accepted_rows = Column(Integer, default=0, nullable=False)
    rejected_rows = Column(Integer, default=0, nullable=False)
    warnings = Column(Integer, default=0, nullable=False)
    
    # List of detailed errors: [{"row": 23, "field": "material_code", "message": "Missing material code"}]
    errors = Column(JSON, default=list, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)
