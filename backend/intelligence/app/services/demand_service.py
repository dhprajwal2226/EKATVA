from sqlalchemy.orm import Session
from app.models.demand import Demand
from app.schemas.demand import DemandCreate, DemandUpdate
from typing import List, Optional

def get_demand(db: Session, demand_id: int) -> Optional[Demand]:
    return db.query(Demand).filter(Demand.id == demand_id).first()

def get_demands(db: Session, skip: int = 0, limit: int = 100) -> List[Demand]:
    return db.query(Demand).offset(skip).limit(limit).all()

def get_demand_by_cnmc(db: Session, cnmc_id: str) -> List[Demand]:
    return db.query(Demand).filter(Demand.national_material_id == cnmc_id).all()

def create_demand(db: Session, demand: DemandCreate) -> Demand:
    db_demand = Demand(**demand.model_dump())
    db.add(db_demand)
    db.commit()
    db.refresh(db_demand)
    return db_demand

def update_demand(db: Session, demand_id: int, demand: DemandUpdate) -> Optional[Demand]:
    db_demand = get_demand(db, demand_id)
    if db_demand:
        update_data = demand.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_demand, key, value)
        db.commit()
        db.refresh(db_demand)
    return db_demand
