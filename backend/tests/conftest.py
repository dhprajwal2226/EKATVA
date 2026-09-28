"""
Pytest Fixtures and In-Memory Database Configuration for Tests.
SIH 2026 - National Material Master Platform.
"""

import os
import sys
from pathlib import Path

# Add backend directory to sys.path so app imports resolve smoothly
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Configure SQLite in-memory for testing
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.db.seed import seed_cpse_data
from app.models.cpse import CPSE
from app.models.material import Material
from app.models.material_attribute import MaterialAttribute
from app.models.material_match import MaterialMatch
from app.models.material_conflict import MaterialConflict
from app.models.national_material import NationalMaterial
from app.models.cpse_material_mapping import CPSEMaterialMapping
from sqlalchemy.pool import StaticPool
from app.models.ingestion_job import IngestionJob


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def db_session(engine):
    """Provide a clean DB session per test with seeded CPSEs."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()

    # Seed CPSEs
    seed_cpse_data(session)

    yield session

    session.rollback()
    session.close()
