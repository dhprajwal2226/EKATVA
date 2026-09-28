from sqlalchemy.orm import Session
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryCreate, InventoryUpdate
from typing import List, Optional

def get_inventory(db: Session, inventory_id: int) -> Optional[Inventory]:
    return db.query(Inventory).filter(Inventory.id == inventory_id).first()

def get_inventories(db: Session, skip: int = 0, limit: int = 100) -> List[Inventory]:
    return db.query(Inventory).offset(skip).limit(limit).all()

def get_inventory_by_cnmc(db: Session, cnmc_id: str) -> List[Inventory]:
    return db.query(Inventory).filter(Inventory.national_material_id == cnmc_id).all()

def create_inventory(db: Session, inventory: InventoryCreate) -> Inventory:
    data = inventory.model_dump()
    # Apply core rule: available = quantity - reserved
    data["available_quantity"] = max(0.0, data.get("quantity", 0.0) - data.get("reserved_quantity", 0.0))
    
    db_inventory = Inventory(**data)
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

def update_inventory(db: Session, inventory_id: int, inventory: InventoryUpdate) -> Optional[Inventory]:
    db_inventory = get_inventory(db, inventory_id)
    if db_inventory:
        update_data = inventory.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_inventory, key, value)
            
        # Re-calculate available_quantity upon update
        db_inventory.available_quantity = max(0.0, db_inventory.quantity - db_inventory.reserved_quantity)
        
        db.commit()
        db.refresh(db_inventory)
    return db_inventory
