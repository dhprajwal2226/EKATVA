# EKATVA Deployment Documentation

## Architecture

- **Frontend:** Vercel (React/Vite)
- **Backend:** FastAPI Hosting (e.g., Render, Railway, DigitalOcean App Platform)
- **Database:** PostgreSQL (with pgvector if vector search is enabled)

Do NOT attempt to deploy the FastAPI backend as a normal static Vercel frontend deployment.

## Backend Environment Variables
List of required backend environment variable names (values must be set securely in your hosting provider's dashboard):

- `DATABASE_URL` (Must be the production PostgreSQL URL)
- `JWT_SECRET` (Securely generated long random string)
- `CORS_ORIGINS` (Comma-separated list containing your Vercel frontend domain)
- `LLM_API_KEY` (Required for AI copilot functions)
- `APP_ENV` (Set to `production`)

## Frontend Environment Variables
List of required frontend environment variables (set in Vercel settings):

- `VITE_API_BASE_URL` (Set to the production backend URL, e.g. `https://ekatva-api.yourdomain.com`)

## Commands

### Backend Startup Command
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
*(Ensure your hosting provider injects the correct `$PORT` variable)*

### Build Commands
**Frontend:**
```bash
npm install
npm run build
```

**Backend:**
Not typically needed for Python/FastAPI beyond `pip install -r requirements.txt`, which is handled by the `Dockerfile`.

### Database Migration Command
Before starting the application, the production database must be migrated using Alembic. Do NOT execute destructive commands.
```bash
alembic upgrade head
```
