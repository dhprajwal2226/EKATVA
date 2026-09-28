from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.schemas.location import Location, LocationCreate, LocationUpdate
from app.services import location_service

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
def read_locations(skip: int = Query(0, alias="page"), limit: int = Query(20), db: Session = Depends(get_db)):
    locations = location_service.get_locations(db, skip=skip, limit=limit)
    total = db.query(location_service.Location).count()
    return {
        "items": [loc for loc in locations],
        "pagination": {
            "page": skip,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }

@router.post("/", response_model=Dict[str, Any])
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    db_location = location_service.create_location(db=db, location=location)
    return {"data": db_location}

@router.get("/{location_id}", response_model=Dict[str, Any])
def read_location(location_id: int, db: Session = Depends(get_db)):
    db_location = location_service.get_location(db, location_id=location_id)
    if db_location is None:
        raise HTTPException(status_code=404, detail={"code": "LOCATION_NOT_FOUND", "message": "The requested location was not found."})
    return {"data": db_location}

@router.patch("/{location_id}", response_model=Dict[str, Any])
def update_location(location_id: int, location: LocationUpdate, db: Session = Depends(get_db)):
    db_location = location_service.update_location(db, location_id, location)
    if db_location is None:
        raise HTTPException(status_code=404, detail={"code": "LOCATION_NOT_FOUND", "message": "The requested location was not found."})
    return {"data": db_location}
