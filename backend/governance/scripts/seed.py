"""
scripts/seed.py

Initializes the database with synthetic demo data for the SIH 2026 project.
Creates initial roles, users, and sample reviews.

WARNING: This data is purely synthetic and meant for demonstration purposes.
"""
import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.database import Base
from app.core.security import hash_password
from app.models.user import User
from app.models.review import Review

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    # For demo script purposes, just use Base.metadata.create_all if alembic hasn't run.
    # In docker-compose, alembic upgrade head runs first.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with SessionLocal() as db:
        # Check if admin already exists
        result = await db.execute(select(User).where(User.employee_id == settings.ADMIN_EMPLOYEE_ID))
        admin = result.scalar_one_or_none()
        
        if admin:
            logger.info("Demo data already seeded.")
            return

        logger.info("Seeding demo users...")
        
        users = [
            User(
                employee_id=settings.ADMIN_EMPLOYEE_ID,
                name=settings.ADMIN_NAME,
                email=settings.ADMIN_EMAIL,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                role="ADMIN",
                department="Central Administration",
                is_active=True
            ),
            User(
                employee_id="NR-001",
                name="Demo National Reviewer",
                email="national.reviewer@demo.gov.in",
                password_hash=hash_password("DemoPassword123!"),
                role="NATIONAL_REVIEWER",
                department="National Standardization Board",
                is_active=True
            ),
            User(
                employee_id="CPSE-IOCL",
                name="IOCL Reviewer",
                email="iocl.reviewer@demo.gov.in",
                password_hash=hash_password("DemoPassword123!"),
                role="CPSE_REVIEWER",
                department="IOCL Procurement",
                cpse_id="IOCL",
                is_active=True
            ),
            User(
                employee_id="INV-001",
                name="Demo Investigator",
                email="investigator@demo.gov.in",
                password_hash=hash_password("DemoPassword123!"),
                role="INVESTIGATOR",
                department="Audit & Compliance",
                is_active=True
            ),
            User(
                employee_id="VIEW-001",
                name="Demo Viewer",
                email="viewer@demo.gov.in",
                password_hash=hash_password("DemoPassword123!"),
                role="VIEWER",
                department="General Operations",
                is_active=True
            ),
        ]
        
        db.add_all(users)
        await db.commit()
        
        logger.info("Seeding synthetic reviews...")
        
        reviews = [
            # 1. Identical
            Review(
                match_id="SYN-MATCH-001",
                original_ai_classification="IDENTICAL",
                ai_confidence=0.98,
                has_critical_conflict=False,
                source_cpse_id="IOCL",
                target_cpse_id="NTPC",
                source_material_code="IOCL-123",
                target_material_code="NTPC-789",
                priority="NORMAL",
                status="PENDING",
                version=1
            ),
            # 2. Near duplicate
            Review(
                match_id="SYN-MATCH-002",
                original_ai_classification="NEAR_DUPLICATE",
                ai_confidence=0.85,
                has_critical_conflict=False,
                source_cpse_id="BHEL",
                target_cpse_id="GAIL",
                source_material_code="BHEL-456",
                target_material_code="GAIL-001",
                priority="NORMAL",
                status="PENDING",
                version=1
            ),
            # 3. Functional equivalent
            Review(
                match_id="SYN-MATCH-003",
                original_ai_classification="FUNCTIONALLY_EQUIVALENT",
                ai_confidence=0.75,
                has_critical_conflict=False,
                source_cpse_id="NTPC",
                target_cpse_id="BHEL",
                source_material_code="NTPC-999",
                target_material_code="BHEL-999",
                priority="MEDIUM",
                status="PENDING",
                version=1
            ),
            # 4. Critical conflict
            Review(
                match_id="SYN-MATCH-004",
                original_ai_classification="REVIEW_REQUIRED",
                ai_confidence=0.60,
                has_critical_conflict=True,
                critical_conflict_details={"conflict_type": "grade", "source": "SS304", "target": "SS316"},
                source_cpse_id="IOCL",
                target_cpse_id="GAIL",
                source_material_code="IOCL-SS304-VALVE",
                target_material_code="GAIL-SS316-VALVE",
                priority="HIGH",
                status="PENDING",
                version=1
            ),
            # 5. Different
            Review(
                match_id="SYN-MATCH-005",
                original_ai_classification="DIFFERENT",
                ai_confidence=0.95,
                has_critical_conflict=False,
                source_cpse_id="NTPC",
                target_cpse_id="GAIL",
                source_material_code="NTPC-PUMP-A",
                target_material_code="GAIL-PIPE-B",
                priority="NORMAL",
                status="PENDING",
                version=1
            )
        ]
        
        db.add_all(reviews)
        await db.commit()
        
        logger.info("Demo data seeding complete.")
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())
