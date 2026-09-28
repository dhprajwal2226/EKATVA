from sqlalchemy.orm import Session
from app.models.mock_models import NationalMaterial
from app.schemas.integration import IntegrationMaterialResponse

def get_integration_material(db: Session, cnmc_id: str) -> IntegrationMaterialResponse:
    material = db.query(NationalMaterial).filter(NationalMaterial.id == cnmc_id).first()
    if not material:
        return None
        
    return IntegrationMaterialResponse(
        cnmc=material.id,
        canonical_material={
            "description": material.canonical_description,
            "category": material.category
        },
        cpse_mappings=[
            {"cpse": m.cpse_name, "material_code": m.cpse_code}
            for m in material.cpse_mappings
        ],
        status=material.status
    )
