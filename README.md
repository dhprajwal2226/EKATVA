# Ekatva Backend — AI-Driven National Material Master & Intelligence Platform for CPSEs
## Person 1 — Core AI Material Intelligence Engine (SIH 2026)

This repository contains the complete backend implementation for **Backend Developer 1 (Core AI Material Intelligence Engine)**.

### Quick Start
All core engine files, APIs, AI pipeline, tests, and documentation are located in [`backend/`](./backend/):

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.db.seed
python -m data.seed_data
pytest -v
uvicorn app.main:app --reload
```

For complete technical documentation, architecture diagrams, API contracts, and explanations, see [backend/README.md](./backend/README.md).
