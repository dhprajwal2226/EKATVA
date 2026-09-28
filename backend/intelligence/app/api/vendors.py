from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.schemas.vendor import Vendor, VendorCreate, VendorUpdate
from app.services import vendor_service

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
def read_vendors(skip: int = Query(0, alias="page"), limit: int = Query(20), db: Session = Depends(get_db)):
    vendors = vendor_service.get_vendors(db, skip=skip, limit=limit)
    total = db.query(vendor_service.Vendor).count()
    return {
        "items": [vendor for vendor in vendors],
        "pagination": {
            "page": skip,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }

@router.post("/", response_model=Dict[str, Any])
def create_vendor(vendor: VendorCreate, db: Session = Depends(get_db)):
    db_vendor = vendor_service.create_vendor(db=db, vendor=vendor)
    return {"data": db_vendor}

@router.get("/{vendor_id}", response_model=Dict[str, Any])
def read_vendor(vendor_id: int, db: Session = Depends(get_db)):
    db_vendor = vendor_service.get_vendor(db, vendor_id=vendor_id)
    if db_vendor is None:
        raise HTTPException(status_code=404, detail={"code": "VENDOR_NOT_FOUND", "message": "The requested vendor was not found."})
    return {"data": db_vendor}

@router.patch("/{vendor_id}", response_model=Dict[str, Any])
def update_vendor(vendor_id: int, vendor: VendorUpdate, db: Session = Depends(get_db)):
    db_vendor = vendor_service.update_vendor(db, vendor_id, vendor)
    if db_vendor is None:
        raise HTTPException(status_code=404, detail={"code": "VENDOR_NOT_FOUND", "message": "The requested vendor was not found."})
    return {"data": db_vendor}
