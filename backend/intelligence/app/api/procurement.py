from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.database import get_db
from app.services import procurement_service

router = APIRouter()

@router.get("/{cnmc_id}", response_model=Dict[str, Any])
def get_procurement_intelligence(cnmc_id: str, db: Session = Depends(get_db)):
    intelligence = procurement_service.analyze_procurement(db, cnmc_id)
    return {"data": intelligence.model_dump()}
