"""
API Integration Tests using FastAPI TestClient.
SIH 2026 - National Material Master Platform.
"""

import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_db


@pytest.fixture
def client(db_session):
    """Provide TestClient with dependency-injected test database session."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health_and_root(client):
    """Test health check and root service discovery."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "HEALTHY"

    resp_root = client.get("/")
    assert resp_root.status_code == 200
    assert resp_root.json()["status"] == "ONLINE"


def test_normalization_api(client):
    """Test interactive normalization preview endpoint."""
    payload = {"description": "CS PIPE 10 IN SCH40"}
    resp = client.post("/api/normalization/normalize", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "CARBON STEEL" in data["normalized_description"]
    assert "SCHEDULE 40" in data["normalized_description"]
    assert len(data["expanded_abbreviations"]) > 0


def test_dna_extraction_api(client):
    """Test interactive Material DNA extraction endpoint."""
    payload = {"description": "SS HEX BOLT M16 X 50 SS304 ASTM A193"}
    resp = client.post("/api/dna/extract", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["attributes"]["material_type"] == "Fastener"
    assert data["attributes"]["grade"] == "SS304"
    assert data["attributes"]["diameter"] == 16.0
    assert data["attributes"]["length"] == 50.0


def test_compare_matching_api(client):
    """Test on-the-fly pair matching comparison endpoint."""
    payload = {
        "source_description": "SS304 VALVE 4 INCH 150#",
        "target_description": "SS316 VALVE 4 INCH 150#",
    }
    resp = client.post("/api/matching/compare", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["classification"] == "REVIEW_REQUIRED"
    assert data["recommendation"] == "DO_NOT_AUTO_MERGE"
    assert len(data["technical_conflicts"]) > 0


def test_classification_rules_api(client):
    """Test retrieval of system scoring weights and conflict precedence policies."""
    resp = client.get("/api/classification/rules")
    assert resp.status_code == 200
    data = resp.json()
    assert "hybrid_weights" in data
    assert data["hybrid_weights"]["semantic_weight"] == 0.30
    assert data["critical_conflict_precedence"]["rule"] == "CRITICAL CONFLICT > SIMILARITY SCORE"


def test_csv_upload_and_materials_api(client):
    """Test file upload endpoint followed by querying the materials list."""
    csv_content = b"material_code,description,cpse,category\nIOCL-API-1,CS PIPE 10 INCH SCH40,IOCL,Piping\n"
    files = {"file": ("materials.csv", io.BytesIO(csv_content), "text/csv")}

    resp = client.post("/api/ingestion/upload", files=files)
    assert resp.status_code == 202
    job_id = resp.json()["job_id"]

    # Check job status
    job_resp = client.get(f"/api/ingestion/jobs/{job_id}")
    assert job_resp.status_code == 200
    assert job_resp.json()["status"] in ("COMPLETED", "PROCESSING")

    # Check materials listing
    mat_resp = client.get("/api/materials")
    assert mat_resp.status_code == 200
    items = mat_resp.json()["items"]
    assert any(m["material_code"] == "IOCL-API-1" for m in items)
