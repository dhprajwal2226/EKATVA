from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.integration import IntegrationMaterialResponse
from app.services.integration_service import get_integration_material

router = APIRouter(prefix="/api/v1/integration", tags=["integration"])

@router.get("/material/{cnmc_id}", response_model=IntegrationMaterialResponse)
def get_material_for_integration(cnmc_id: str, db: Session = Depends(get_db)):
    material = get_integration_material(db, cnmc_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CNMC_NOT_FOUND", "message": "Material not found"}
        )
    return material
