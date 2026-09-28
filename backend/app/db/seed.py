"""Seed initial CPSE master records."""

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, Base, engine
from app.models.cpse import CPSE

SEED_CPSES = [
    {
        "name": "Indian Oil Corporation Limited",
        "code": "IOCL",
        "sector": "Oil & Gas",
        "description": "Refining, pipeline transportation, marketing of petroleum products and petrochemicals.",
    },
    {
        "name": "NTPC Limited",
        "code": "NTPC",
        "sector": "Power Generation",
        "description": "India's largest energy conglomerate specializing in thermal, hydro and renewable energy.",
    },
    {
        "name": "Bharat Heavy Electricals Limited",
        "code": "BHEL",
        "sector": "Heavy Engineering",
        "description": "Engineering and manufacturing enterprise in power, transmission, industry, transportation, and defense.",
    },
    {
        "name": "GAIL (India) Limited",
        "code": "GAIL",
        "sector": "Natural Gas",
        "description": "Natural gas transmission, distribution, processing, and petrochemicals.",
    },
]


def seed_cpse_data(db: Session) -> None:
    """Seed default CPSE records if not already existing."""
    for cpse_data in SEED_CPSES:
        existing = db.query(CPSE).filter(CPSE.code == cpse_data["code"]).first()
        if not existing:
            cpse = CPSE(**cpse_data)
            db.add(cpse)
    db.commit()


def init_db() -> None:
    """Initialize all tables and populate initial seed data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_cpse_data(db)
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database tables and seeding CPSEs...")
    init_db()
    print("Database initialization completed successfully.")
