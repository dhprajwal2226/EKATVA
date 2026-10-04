from sqlalchemy.orm import Session
from app.models.cpse_material_mapping import CPSEMaterialMapping
from app.schemas.export import ExportMappingResponse

def get_mappings_for_export(db: Session, page: int = 1, limit: int = 100) -> list[ExportMappingResponse]:
    offset = (page - 1) * limit
    mappings = db.query(CPSEMaterialMapping).offset(offset).limit(limit).all()
    
    return [
        ExportMappingResponse(
            cnmc=m.national_material.cnmc if m.national_material else "",
            cpse=m.cpse.name if m.cpse else "",
            cpse_material_code=m.material_code or "",
            original_description=m.material.original_description if m.material else "",
            mapping_status=m.status,
            source_reference=m.material.source_reference if m.material else "SYNTHETIC_DEMO"
        )
        for m in mappings
    ]
