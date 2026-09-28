from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.export import ExportMappingResponse
from app.services.export_service import get_mappings_for_export

router = APIRouter(prefix="/api/v1/export", tags=["export"])

@router.get("/mappings", response_model=List[ExportMappingResponse])
def export_mappings(page: int = 1, limit: int = 100, db: Session = Depends(get_db)):
    return get_mappings_for_export(db, page, limit)

@router.get("/national-materials")
def export_national_materials(page: int = 1, limit: int = 100, db: Session = Depends(get_db)):
    return {"message": "National materials export not implemented in demo"}

@router.get("/{cnmc_id}")
def export_cnmc(cnmc_id: str, db: Session = Depends(get_db)):
    return {"message": f"Single CNMC {cnmc_id} export not implemented in demo"}
