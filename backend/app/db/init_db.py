from app.db.database import engine, Base, SessionLocal
from app.models.mock_models import *
from app.db.synthetic_data import seed_demo_data
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Assuming Alembic has created database tables")
    # Base.metadata.create_all(bind=engine) - handled exclusively by Alembic migrations
    
    logger.info("Seeding demo data")
    db = SessionLocal()
    try:
        # Temporarily disabled to prevent inserting fake materials into real tables
        # and because mock tables (like ds_inventory) are not yet managed by Alembic.
        # seed_demo_data(db)
        logger.info("Database seeding is disabled in this checkpoint to protect real tables")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
