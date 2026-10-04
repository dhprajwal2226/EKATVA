from sqlalchemy.orm import Session
from app.models.national_material import NationalMaterial
from app.schemas.integration import IntegrationMaterialResponse

def get_integration_material(db: Session, cnmc_id: str) -> IntegrationMaterialResponse:
    material = db.query(NationalMaterial).filter(NationalMaterial.cnmc == cnmc_id).first()
    if not material:
        return None
        
    return IntegrationMaterialResponse(
        cnmc=material.cnmc,
        canonical_material={
            "description": material.standard_description,
            "category": material.category
        },
        cpse_mappings=[
            {"cpse": m.cpse.name if m.cpse else "", "material_code": m.material_code}
            for m in material.cpse_mappings
        ],
        status=material.status
    )
