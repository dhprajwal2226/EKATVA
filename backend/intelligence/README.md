# AI-DRIVEN NATIONAL MATERIAL MASTER & INTELLIGENCE PLATFORM FOR CPSEs

## National Material Intelligence Engine (Person 3)

This module is responsible for the intelligence layer of the National Material Platform. It takes approved CNMC (Central National Material Codes) and links them to:
- Vendors
- Inventory
- Demand
- Locations
- Standards
- Material Relationships
- Graph Traversal (Knowledge Graph)

### Architecture
PostgreSQL with SQLAlchemy is the primary datastore. The engine exposes REST APIs built on FastAPI to provide aggregated data, supply/demand signals, and graph intelligence around approved national materials.

### Setup
1. Copy `.env.example` to `.env` (if provided).
2. Set `DATABASE_URL` in `.env` (e.g. `postgresql://user:pass@localhost:5432/national_intelligence`).
3. Run Alembic migrations: `alembic upgrade head`
4. Run standard seed: `python seed.py`
5. Run tests: `pytest tests/`
6. Run the server: `uvicorn app.main:app --reload`

### Swagger Docs
Available at `/docs` once the server is running.
