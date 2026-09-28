from pydantic import BaseModel
from typing import List, Optional

class ExportMappingResponse(BaseModel):
    cnmc: str
    cpse: str
    cpse_material_code: str
    original_description: str
    mapping_status: str
    source_reference: Optional[str] = None
