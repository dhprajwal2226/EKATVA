"""
Main FastAPI Application Entrypoint.
National Material Master & Intelligence Platform for CPSEs (SIH 2026).
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import api_router
from app.db.seed import init_db
from app.db.init_db import init_db as init_decision_support_db
from app.api.passport import router as passport_router
from app.api.analytics import router as analytics_router
from app.api.copilot import router as copilot_router
from app.api.export import router as export_router
from app.api.integration import router as integration_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database tables exist and seed baseline CPSE records
    init_db()
    init_decision_support_db()
    yield
    # Shutdown logic if needed


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
## National Material Master & Intelligence Platform for CPSEs
Core AI Material Intelligence Engine (SIH 2026)

### Key Capabilities:
- **Material Data Ingestion**: Robust CSV/Excel parsing, row validation, and job tracking.
- **Normalization Engine**: Deterministic formatting, punctuation standardization, and centralized CPSE domain abbreviation expansion.
- **Unit Normalization**: Deterministic conversion to standard metric SI units (e.g. 10 inch -> 254 mm).
- **Material DNA Extraction**: Structured engineering taxonomy, dimensions, pressure, schedule, and ASTM/ASME standards.
- **Vector Embeddings**: Sentence Transformers integration with pgvector cosine similarity.
- **Fuzzy Matching**: RapidFuzz multi-metric lexical analysis (token_set, token_sort, WRatio).
- **Hybrid Matching Engine**: Configurable weighted scoring (Semantic 30%, Fuzzy 20%, Attribute 30%, Technical 20%).
- **Technical Conflict Engine**: Strict enforcement of **CRITICAL CONFLICT > SIMILARITY SCORE**.
- **Classification & Explainability**: Grounded explanations detailing why items matched, what differed, and whether human review is required.
- **CNMC Generation & CPSE Mapping**: Deterministic SHA-256 fingerprinting for stable national material master codes.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Standardized Error Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Ensure predictable, safe error responses without raw stack trace leakage."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred during processing. Please review request payload.",
                "details": str(exc) if not isinstance(exc, AssertionError) else "Assertion failed",
            }
        },
    )


# Mount API Routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Decision support / analytics routes (from decision-support branch)
for _router in (passport_router, analytics_router, copilot_router, export_router, integration_router):
    app.include_router(_router)


@app.get("/", tags=["System"])
def root():
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "ONLINE",
        "documentation": "/docs",
        "api_root": settings.API_V1_STR,
    }


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "HEALTHY",
        "database": "CONNECTED",
        "version": settings.VERSION,
    }
