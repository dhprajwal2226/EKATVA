"""
Ingestion API Routes.
File upload and async job status tracking.
SIH 2026 - National Material Master Platform.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.ingestion_job import IngestionJob
from app.schemas.ingestion import IngestionJobResponse, IngestionUploadResponse
from app.services.ingestion_service import IngestionService
from app.utils.validators import validate_file_metadata

router = APIRouter(prefix="/ingestion", tags=["Material Ingestion"])


@router.post(
    "/upload",
    response_model=IngestionUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload and ingest CPSE material master file (.csv, .xlsx)",
)
async def upload_material_file(
    file: UploadFile = File(...),
    cpse: Optional[str] = Form(None, description="Optional default CPSE code (e.g. IOCL, NTPC, BHEL, GAIL)"),
    db: Session = Depends(get_db),
):
    """
    Ingest material master records from CSV or XLSX.
    Preserves original descriptions, executes deterministic normalization,
    extracts Material DNA, generates embeddings, and logs all validation errors.
    """
    content = await file.read()
    is_valid, err_msg = validate_file_metadata(
        filename=file.filename or "",
        content_length=len(content),
        content_type=file.content_type,
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "FILE_VALIDATION_ERROR", "message": err_msg},
        )

    job_id = str(uuid.uuid4())

    # Create initial queued job
    job = IngestionJob(
        id=job_id,
        filename=file.filename or "unknown",
        status="QUEUED",
    )
    db.add(job)
    db.commit()

    # Process ingestion synchronously for deterministic instant feedback or in background
    processed_job = IngestionService.process_ingestion(
        db=db,
        job_id=job_id,
        filename=file.filename or "unknown",
        file_bytes=content,
        default_cpse_code=cpse,
    )

    return IngestionUploadResponse(
        message=f"File '{file.filename}' processed. Status: {processed_job.status}",
        job_id=job_id,
        status=processed_job.status,
        filename=file.filename or "unknown",
    )


@router.get(
    "/jobs/{job_id}",
    response_model=IngestionJobResponse,
    summary="Get ingestion job status and error report",
)
def get_ingestion_job(
    job_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve detailed execution stats, error lists, and row tallies for an ingestion job."""
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "JOB_NOT_FOUND", "message": f"Ingestion job '{job_id}' not found."},
        )

    return IngestionJobResponse(
        job_id=job.id,
        filename=job.filename,
        status=job.status,
        total_rows=job.total_rows,
        processed_rows=job.processed_rows,
        accepted_rows=job.accepted_rows,
        rejected_rows=job.rejected_rows,
        warnings=job.warnings,
        errors=job.errors or [],
        created_at=job.created_at,
        completed_at=job.completed_at,
    )
