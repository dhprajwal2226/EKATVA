from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.services.analytics_service import (
    get_overview_analytics,
    get_cpse_analytics,
    get_executive_summary
)
from app.schemas.analytics import (
    OverviewAnalyticsResponse,
    CpseAnalyticsResponse,
    ExecutiveSummaryResponse
)

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/overview", response_model=OverviewAnalyticsResponse)
def overview(db: Session = Depends(get_db)):
    return get_overview_analytics(db)

@router.get("/cpse", response_model=List[CpseAnalyticsResponse])
def cpse_analytics(db: Session = Depends(get_db)):
    return get_cpse_analytics(db)

@router.get("/executive-summary", response_model=ExecutiveSummaryResponse)
def executive_summary(db: Session = Depends(get_db)):
    return get_executive_summary(db)

@router.get("/categories")
def categories(db: Session = Depends(get_db)):
    return {"message": "Categories analytics not implemented in demo"}

@router.get("/matching")
def matching(db: Session = Depends(get_db)):
    return {"message": "Matching analytics not implemented in demo"}

@router.get("/conflicts")
def conflicts(db: Session = Depends(get_db)):
    return {"message": "Conflicts analytics not implemented in demo"}

@router.get("/trends")
def trends(db: Session = Depends(get_db)):
    return {"message": "Trends analytics not implemented in demo"}
