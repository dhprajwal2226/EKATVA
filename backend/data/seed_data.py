"""
Script to seed the 120+ synthetic CPSE materials into the database.
SIH 2026 - National Material Master Platform.
"""

import os
from pathlib import Path
from app.db.database import SessionLocal
from app.db.seed import init_db
from app.services.ingestion_service import IngestionService

DATA_CSV_PATH = Path(__file__).parent / "seed_materials.csv"


def seed_synthetic_dataset():
    """Initialize DB and ingest synthetic materials."""
    print("Initializing database...")
    init_db()

    db = SessionLocal()
    try:
        if not DATA_CSV_PATH.exists():
            print(f"File not found: {DATA_CSV_PATH}")
            return

        with open(DATA_CSV_PATH, "rb") as f:
            content = f.read()

        job_id = "seed-job-001"
        print(f"Ingesting synthetic dataset from {DATA_CSV_PATH}...")
        job = IngestionService.process_ingestion(
            db=db,
            job_id=job_id,
            filename="seed_materials.csv",
            file_bytes=content,
        )
        print(f"Seeding completed! Status: {job.status}")
        print(f"Total rows: {job.total_rows}, Accepted: {job.accepted_rows}, Rejected: {job.rejected_rows}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_synthetic_dataset()
