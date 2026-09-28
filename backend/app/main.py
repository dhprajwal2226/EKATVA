from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.init_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB on startup
    init_db()
    yield
    # Clean up on shutdown if needed

from app.api.passport import router as passport_router
from app.api.analytics import router as analytics_router
from app.api.copilot import router as copilot_router
from app.api.export import router as export_router
from app.api.integration import router as integration_router

app = FastAPI(
    title="Person 4 - Decision Support & Analytics",
    description="National Unified Material Master Framework for CPSEs",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(passport_router)
app.include_router(analytics_router)
app.include_router(copilot_router)
app.include_router(export_router)
app.include_router(integration_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.APP_ENV}
