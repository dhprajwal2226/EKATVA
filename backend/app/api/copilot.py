from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.copilot import CopilotRequest, CopilotResponse
from app.services.copilot_service import process_copilot_query

router = APIRouter(prefix="/api/v1/copilot", tags=["copilot"])

@router.post("/query", response_model=CopilotResponse)
def query_copilot(request: CopilotRequest, db: Session = Depends(get_db)):
    return process_copilot_query(db, request)
