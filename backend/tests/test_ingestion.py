"""
Tests for Data Ingestion, Validation, and Job Tracking.
SIH 2026 - National Material Master Platform.
"""

import pytest
from app.services.ingestion_service import IngestionService
from app.models.material import Material
from app.models.cpse import CPSE


def test_valid_csv_ingestion(db_session):
    """Verify clean ingestion of CSV records with CPSE matching."""
    csv_data = """material_code,description,cpse,category,source_reference
IOCL-TEST-1,CS PIPE 10 INCH SCH40,IOCL,Piping,PO-101
NTPC-TEST-1,CARBON STEEL PIPE 10 IN SCHEDULE 40,NTPC,Piping,PO-102
"""
    job = IngestionService.process_ingestion(
        db=db_session,
        job_id="test-job-1",
        filename="test.csv",
        file_bytes=csv_data.encode("utf-8"),
    )

    assert job.status == "COMPLETED"
    assert job.total_rows == 2
    assert job.accepted_rows == 2
    assert job.rejected_rows == 0

    # Verify material persisted in DB
    m = db_session.query(Material).filter(Material.material_code == "IOCL-TEST-1").first()
    assert m is not None
    assert m.original_description == "CS PIPE 10 INCH SCH40"
    assert m.normalized_description is not None
    assert m.attributes is not None
    assert m.attributes.diameter == 254.0


def test_ingestion_validation_errors(db_session):
    """Verify invalid rows (missing code, unknown CPSE) are rejected and logged in job report."""
    csv_data = """material_code,description,cpse
,MISSING CODE MATERIAL,IOCL
VALID-CODE-1,,IOCL
VALID-CODE-2,VALID DESCRIPTION,UNKNOWN_CPSE_XYZ
"""
    job = IngestionService.process_ingestion(
        db=db_session,
        job_id="test-job-err",
        filename="err.csv",
        file_bytes=csv_data.encode("utf-8"),
    )

    assert job.status == "FAILED"
    assert job.total_rows == 3
    assert job.accepted_rows == 0
    assert job.rejected_rows == 3
    assert len(job.errors) >= 3


def test_immutable_original_description(db_session):
    """
    CRITICAL REQUIREMENT:
    original_description MUST NEVER be overwritten even if same item is re-ingested.
    """
    csv_initial = """material_code,description,cpse
IOCL-IMMUTABLE,ORIGINAL DESCRIPTION THAT MUST PERSIST,IOCL
"""
    job1 = IngestionService.process_ingestion(
        db=db_session,
        job_id="job-init",
        filename="initial.csv",
        file_bytes=csv_initial.encode("utf-8"),
    )
    assert job1.accepted_rows == 1

    # Re-ingest same code with slightly modified incoming description
    csv_update = """material_code,description,cpse
IOCL-IMMUTABLE,NEW DIFFERENT TEXT ATTEMPTING OVERWRITE,IOCL
"""
    job2 = IngestionService.process_ingestion(
        db=db_session,
        job_id="job-update",
        filename="update.csv",
        file_bytes=csv_update.encode("utf-8"),
    )

    mat = db_session.query(Material).filter(Material.material_code == "IOCL-IMMUTABLE").first()
    assert mat.original_description == "ORIGINAL DESCRIPTION THAT MUST PERSIST", (
        "CRITICAL ERROR: original_description was overwritten during re-ingestion!"
    )
