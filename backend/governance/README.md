# AI-DRIVEN NATIONAL MATERIAL MASTER & INTELLIGENCE PLATFORM FOR CPSEs

**Person 2 — National Material Master & Governance Engine**

## Purpose

The Governance Engine is the central human-in-the-loop validation layer for the SIH 2026 National Material Master project.
It receives AI matching recommendations (from Person 1) and enforces a strict governance workflow to create, manage, and audit the **Common National Material Code (CNMC)**.

The system ensures that **AI NEVER silently replaces human decisions** and provides full append-only audit traceability for every action.

## Governance Architecture

```text
                 PERSON 1
              AI MATCH ENGINE
                     │
                     ▼
              AI RECOMMENDATION
                     │
                     ▼
             ┌───────────────┐
             │ PERSON 2      │
             │ REVIEW QUEUE  │
             └───────┬───────┘
                     │
             ┌───────┼────────┐
             ↓       ↓        ↓
          APPROVE  REJECT   EDIT
             │       │        │
             │       │        │
             ↓       ↓        ↓
         NATIONAL   NO       HUMAN
          MASTER   MAPPING  CORRECTION
             │                │
             └───────┬────────┘
                     ↓
                  CNMC
                     │
                     ↓
             CPSE MAPPINGS
                     │
                     ↓
                AUDIT TRAIL
                     │
          ┌──────────┴──────────┐
          ↓                     ↓
      PERSON 3              PERSON 4
   INTELLIGENCE          DECISION SUPPORT
```

## Workflows

### Authentication & Authorization (RBAC)
- **JWT-based authentication** with access and refresh tokens.
- **Passwords are hashed** (Argon2) and never stored in plain text.
- Roles: `ADMIN`, `NATIONAL_REVIEWER`, `CPSE_REVIEWER`, `INVESTIGATOR`, `VIEWER`.
- Scoping: `CPSE_REVIEWER` can only access records relevant to their respective CPSE.

### Review Workflow
- **Claim:** A reviewer claims a `PENDING` AI recommendation.
- **Approve:** Merges the materials into the National Material Master. 
  - *Critical Conflict Rule:* If the AI detected a critical technical conflict (e.g. Grade SS304 vs SS316), the reviewer *must* explicitly acknowledge it and provide a justification comment.
- **Reject:** Marks the match as invalid. Requires a mandatory rejection reason.
- **Edit:** Reviewer overrides the AI classification (e.g., changes `NEAR_DUPLICATE` to `FUNCTIONALLY_EQUIVALENT`). Both the original AI classification and the final human classification are preserved.
- **Escalate:** Pushes a difficult review to a senior reviewer.

### National Material Master & CNMC
- A deterministic `identity_hash` (SHA-256) is generated from canonical attributes to ensure uniqueness across the system.
- Upon approval, a unique `CNMC-XXXXXX` code is generated.
- Status flow: `DRAFT` → `PENDING_APPROVAL` → `ACTIVE` → `SUSPENDED` → `DEPRECATED`.

### CPSE Mappings
- **Original CPSE material codes are never renamed or modified.**
- The system maps multiple CPSE codes to a single CNMC. 
- Mappings have confidence levels and matching types.

### Audit Trail & Data Lineage
- **Append-Only:** Normal users cannot modify or delete audit logs.
- Captures `WHO, WHAT, WHEN, WHY, BEFORE, AFTER`.
- Maintains the full history of decisions, providing a robust chain of evidence for every material mapped to the CNMC.

## API Documentation
The API documentation is available via Swagger UI.
Once the application is running, navigate to:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Setup & Execution

### Environment Variables
Copy `.env.example` to `.env` and fill in the necessary secrets (especially `JWT_SECRET_KEY` and database credentials).

### Docker (Recommended)
You can bring up the entire stack (PostgreSQL + FastAPI backend) using Docker Compose:

```bash
docker-compose up --build
```
This automatically runs Alembic migrations and the database seed script.

### Local Setup
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `alembic upgrade head`
5. Seed synthetic data: `python scripts/seed.py`
6. Start the server: `uvicorn app.main:app --reload`

## Migration Commands
- Create a new migration: `alembic revision --autogenerate -m "Description"`
- Apply migrations: `alembic upgrade head`
- Rollback migration: `alembic downgrade -1`

## Seed Commands
To populate the database with synthetic users and review data (Demo only):
```bash
python scripts/seed.py
```

## Testing
The project uses `pytest` and `pytest-asyncio` with an in-memory SQLite database (`aiosqlite`) to run isolated tests quickly.
```bash
pytest
```
Coverage includes mandatory tests for critical conflict handling, CNMC uniqueness, duplicate mapping prevention, and role-based access control.

## Security Considerations
- Backend completely enforces all authorizations (frontend UI hiding elements is not relied upon).
- No hardcoded API keys or passwords in the source.
- Argon2 password hashes.
- Row-level scoping ensures a reviewer from one CPSE cannot approve materials restricted to another CPSE.
- Concurrent modification prevention via optimistic versioning (returns `409 Conflict`).
