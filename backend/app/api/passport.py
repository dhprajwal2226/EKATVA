from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.passport_service import get_material_passport
from app.schemas.passport import MaterialPassportResponse

router = APIRouter(prefix="/api/v1/passport", tags=["passport"])

@router.get("/{cnmc_id}", response_model=MaterialPassportResponse)
def get_passport(cnmc_id: str, db: Session = Depends(get_db)):
    passport = get_material_passport(db, cnmc_id)
    if not passport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CNMC_NOT_FOUND", "message": "The requested national material was not found."}
        )
    return passport
