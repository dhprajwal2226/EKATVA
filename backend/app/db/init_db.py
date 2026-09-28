from app.db.database import engine, Base, SessionLocal
from app.models.mock_models import *
from app.db.synthetic_data import seed_demo_data
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)
    
    logger.info("Seeding demo data")
    db = SessionLocal()
    try:
        seed_demo_data(db)
        logger.info("Database seeded successfully")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
