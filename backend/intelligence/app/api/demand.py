from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.schemas.demand import Demand, DemandCreate, DemandUpdate
from app.services import demand_service

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
def read_demands(skip: int = Query(0, alias="page"), limit: int = Query(20), db: Session = Depends(get_db)):
    demands = demand_service.get_demands(db, skip=skip, limit=limit)
    total = db.query(demand_service.Demand).count()
    return {
        "items": [dem for dem in demands],
        "pagination": {
            "page": skip,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }

@router.post("/", response_model=Dict[str, Any])
def create_demand(demand: DemandCreate, db: Session = Depends(get_db)):
    db_demand = demand_service.create_demand(db=db, demand=demand)
    return {"data": db_demand}

@router.get("/{demand_id}", response_model=Dict[str, Any])
def read_demand(demand_id: int, db: Session = Depends(get_db)):
    db_demand = demand_service.get_demand(db, demand_id=demand_id)
    if db_demand is None:
        raise HTTPException(status_code=404, detail={"code": "DEMAND_NOT_FOUND", "message": "The requested demand was not found."})
    return {"data": db_demand}

@router.patch("/{demand_id}", response_model=Dict[str, Any])
def update_demand(demand_id: int, demand: DemandUpdate, db: Session = Depends(get_db)):
    db_demand = demand_service.update_demand(db, demand_id, demand)
    if db_demand is None:
        raise HTTPException(status_code=404, detail={"code": "DEMAND_NOT_FOUND", "message": "The requested demand was not found."})
    return {"data": db_demand}

@router.get("/national-materials/{cnmc_id}/demand", response_model=Dict[str, Any])
def read_demand_by_cnmc(cnmc_id: str, db: Session = Depends(get_db)):
    items = demand_service.get_demand_by_cnmc(db, cnmc_id=cnmc_id)
    return {"data": items}
