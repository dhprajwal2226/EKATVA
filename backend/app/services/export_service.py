from sqlalchemy.orm import Session
from app.models.mock_models import CpseMapping
from app.schemas.export import ExportMappingResponse

def get_mappings_for_export(db: Session, page: int = 1, limit: int = 100) -> list[ExportMappingResponse]:
    offset = (page - 1) * limit
    mappings = db.query(CpseMapping).offset(offset).limit(limit).all()
    
    return [
        ExportMappingResponse(
            cnmc=m.cnmc_id,
            cpse=m.cpse_name,
            cpse_material_code=m.cpse_code,
            original_description=m.original_description,
            mapping_status=m.mapping_status,
            source_reference="SYNTHETIC_DEMO"
        )
        for m in mappings
    ]
