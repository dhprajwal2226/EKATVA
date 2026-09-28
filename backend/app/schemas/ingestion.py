"""Pydantic schemas for file ingestion and job tracking."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class IngestionJobError(BaseModel):
    row: int
    field: str
    message: str


class IngestionJobResponse(BaseModel):
    job_id: str
    filename: str
    status: str
    total_rows: int
    processed_rows: int
    accepted_rows: int
    rejected_rows: int
    warnings: int
    errors: List[IngestionJobError] = []
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class IngestionUploadResponse(BaseModel):
    message: str
    job_id: str
    status: str
    filename: str
