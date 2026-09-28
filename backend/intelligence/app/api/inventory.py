from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.schemas.inventory import Inventory, InventoryCreate, InventoryUpdate
from app.services import inventory_service

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
def read_inventories(skip: int = Query(0, alias="page"), limit: int = Query(20), db: Session = Depends(get_db)):
    inventories = inventory_service.get_inventories(db, skip=skip, limit=limit)
    total = db.query(inventory_service.Inventory).count()
    return {
        "items": [inv for inv in inventories],
        "pagination": {
            "page": skip,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }

@router.post("/", response_model=Dict[str, Any])
def create_inventory(inventory: InventoryCreate, db: Session = Depends(get_db)):
    db_inventory = inventory_service.create_inventory(db=db, inventory=inventory)
    return {"data": db_inventory}

@router.get("/{inventory_id}", response_model=Dict[str, Any])
def read_inventory(inventory_id: int, db: Session = Depends(get_db)):
    db_inventory = inventory_service.get_inventory(db, inventory_id=inventory_id)
    if db_inventory is None:
        raise HTTPException(status_code=404, detail={"code": "INVENTORY_NOT_FOUND", "message": "The requested inventory was not found."})
    return {"data": db_inventory}

@router.patch("/{inventory_id}", response_model=Dict[str, Any])
def update_inventory(inventory_id: int, inventory: InventoryUpdate, db: Session = Depends(get_db)):
    db_inventory = inventory_service.update_inventory(db, inventory_id, inventory)
    if db_inventory is None:
        raise HTTPException(status_code=404, detail={"code": "INVENTORY_NOT_FOUND", "message": "The requested inventory was not found."})
    return {"data": db_inventory}

@router.get("/national-materials/{cnmc_id}/inventory", response_model=Dict[str, Any])
def read_inventory_by_cnmc(cnmc_id: str, db: Session = Depends(get_db)):
    items = inventory_service.get_inventory_by_cnmc(db, cnmc_id=cnmc_id)
    return {"data": items}
