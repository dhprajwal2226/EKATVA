"""
app/main.py

FastAPI application entry point.

Registers all routers, configures CORS, Swagger metadata, and global
error handlers. Secrets are NEVER hard-coded — all configuration
is read from environment variables via app.core.config.settings.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.APP_DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    logger.info("Starting National Material Master Governance API v%s", settings.APP_VERSION)
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="""
## National Material Master & Governance Engine

**Person 2 — Governance Module**

This API provides:

- 🔐 **Authentication** — JWT-based login, refresh, logout
- 👤 **User Management** — RBAC with roles: ADMIN, NATIONAL_REVIEWER, CPSE_REVIEWER, INVESTIGATOR, VIEWER
- 🔍 **Human Review Workflow** — Claim, Approve, Reject, Edit, Escalate AI matches
- 🏛️ **National Material Master** — CNMC generation, governance status lifecycle
- 🔗 **CPSE Mappings** — Governed mapping of CPSE material codes to CNMC
- 📋 **Audit Trail** — Append-only, full lineage traceability

**Architecture:**

```
AI RECOMMENDS → PERSON 2 REVIEWS → HUMAN DECIDES → NATIONAL MASTER → CPSE MAPPINGS → AUDIT TRAIL
```

### Security Notes
- Passwords are hashed using Argon2 — never stored in plain text.
- JWT access tokens expire in 30 minutes; refresh tokens in 7 days.
- All permission checks are enforced at the backend — never trust frontend.
- Audit logs are append-only — normal users cannot modify them.
""",
    openapi_tags=[
        {"name": "Authentication", "description": "Login, logout, and token refresh."},
        {"name": "User Management", "description": "Create, update, activate/deactivate users. ADMIN only."},
        {"name": "Human Review Workflow", "description": "Review queue management — claim, approve, reject, edit, escalate AI matches."},
        {"name": "National Material Master", "description": "CNMC-governed national material lifecycle."},
        {"name": "CPSE Material Mappings", "description": "Governed CPSE-to-CNMC material mappings."},
        {"name": "Audit Trail", "description": "Read-only governance audit log."},
    ],
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
from app.api import auth, audit, mappings, national_materials, reviews, users  # noqa: E402

API_PREFIX = "/api"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)
app.include_router(reviews.router, prefix=API_PREFIX)
app.include_router(national_materials.router, prefix=API_PREFIX)
app.include_router(mappings.router, prefix=API_PREFIX)
app.include_router(audit.router, prefix=API_PREFIX)


# ── Global error handler ──────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please contact the administrator.",
            }
        },
    )


@app.get("/health", tags=["Health"], summary="Health check")
async def health() -> dict:
    return {"status": "ok", "version": settings.APP_VERSION}
