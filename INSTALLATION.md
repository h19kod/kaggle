# Installation Guide — Kaggle-like Data Science Platform

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start (Docker — Recommended)](#quick-start-docker--recommended)
- [Local Development Setup](#local-development-setup)
  - [Backend](#backend-setup)
  - [Frontend](#frontend-setup)
- [Environment Variables](#environment-variables)
- [Database Migrations](#database-migrations)
- [Running the Services](#running-the-services)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Tool | Minimum Version | Notes |
|------|----------------|-------|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend runtime |
| npm | 9+ | Frontend package manager |
| Docker | 24+ | Required for full-stack setup |
| Docker Compose | v2.20+ | Orchestration |
| Git | any | Source control |

---

## Quick Start (Docker — Recommended)

This method spins up **all services** (PostgreSQL, Redis, MinIO, Backend, Celery Worker, Frontend) with a single command.

### 1. Clone the repository

```bash
git clone <repository-url>
cd kaggle
```

### 2. Copy and configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

```env
SECRET_KEY="your-very-secret-key-here"
```

### 3. Start all services

```bash
docker compose up --build
```

> First build may take 3–5 minutes while Docker downloads base images and installs dependencies.

### 4. Run database migrations

In a **separate terminal**, after containers are healthy:

```bash
docker compose exec backend alembic upgrade head
```

### 5. Access the application

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |
| MinIO Console | http://localhost:9001 |

**MinIO default credentials:** `minioadmin` / `minioadmin`

### Stop all services

```bash
docker compose down
```

To also remove persisted volumes (wipes database and storage data):

```bash
docker compose down -v
```

---

## Local Development Setup

Use this approach if you want to run the backend or frontend without Docker.

### Backend Setup

#### 1. Create a Python virtual environment

```bash
python -m venv venv
```

Activate it:

- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

#### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

#### 3. Configure environment variables

```bash
cp .env.example .env
```

For local development with SQLite (no PostgreSQL needed), the defaults in `.env.example` work out of the box.  
For PostgreSQL, update `DATABASE_URL`:

```env
DATABASE_URL="postgresql://kaggle:kaggle_pass@localhost:5432/kaggle_platform"
```

#### 4. Run database migrations

```bash
alembic upgrade head
```

> For SQLite the database file `kaggle_platform.db` is created automatically in the project root.

#### 5. Start the backend server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API is now available at **http://localhost:8000**.

#### 6. (Optional) Start the Celery worker

Celery is required for background tasks (notebook compute sessions, competition evaluation). Make sure Redis is running first.

```bash
celery -A app.tasks worker --loglevel=info
```

---

### Frontend Setup

#### 1. Navigate to the frontend directory

```bash
cd frontend
```

#### 2. Install Node dependencies

```bash
npm install
```

#### 3. Start the development server

```bash
npm run dev
```

The frontend is available at **http://localhost:5173** by default (Vite default port).

#### 4. Build for production

```bash
npm run build
```

Output is placed in `frontend/dist/`.

---

## Environment Variables

All variables are defined in `.env` (copy from `.env.example`).

| Variable | Default | Description |
|----------|---------|-------------|
| `PROJECT_NAME` | `Kaggle-like Data Science Platform` | Application display name |
| `DATABASE_URL` | `sqlite:///./kaggle_platform.db` | Database connection string |
| `SECRET_KEY` | `change-me-in-production` | **Change this!** JWT signing secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` (7 days) | JWT token lifetime |
| `REDIS_HOST` | `localhost` | Redis hostname |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_DB` | `0` | Redis database index |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Celery message broker |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/0` | Celery result storage |
| `S3_ENDPOINT` | `http://localhost:9000` | MinIO / S3 endpoint |
| `S3_ACCESS_KEY` | `minioadmin` | Object storage access key |
| `S3_SECRET_KEY` | `minioadmin` | Object storage secret key |
| `S3_BUCKET_NAME` | `kaggle-platform` | Default storage bucket |
| `S3_REGION` | `us-east-1` | Storage region |
| `S3_USE_SSL` | `false` | Enable SSL for S3 |
| `DATA_SCIENCE_IMAGE` | `jupyter/datascience-notebook:latest` | Docker image for compute sessions |

> **Security:** Never commit your real `.env` file. The `.gitignore` already excludes it.

---

## Database Migrations

The project uses **Alembic** for schema management.

```bash
# Apply all pending migrations
alembic upgrade head

# Check current revision
alembic current

# Create a new migration after model changes
alembic revision --autogenerate -m "describe your change"

# Downgrade one step
alembic downgrade -1

# Downgrade to base (empty schema)
alembic downgrade base
```

---

## Running the Services

### Summary of all commands (local dev)

```bash
# Terminal 1 — Backend API
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Celery Worker (requires Redis)
celery -A app.tasks worker --loglevel=info

# Terminal 3 — Frontend
cd frontend && npm run dev
```

### Docker Compose service reference

| Service | Container name | Port(s) |
|---------|---------------|---------|
| PostgreSQL 15 | `kaggle_db` | `5432` |
| Redis 7 | `kaggle_redis` | `6379` |
| MinIO | `kaggle_minio` | `9000`, `9001` |
| Backend (FastAPI) | `kaggle_backend` | `8000` |
| Celery Worker | `kaggle_celery` | — |
| Frontend (Vite / React) | `kaggle_frontend` | `3000` |

---

## Verification

After startup, confirm the backend is healthy:

```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}
```

Check the root endpoint:

```bash
curl http://localhost:8000/
```

Expected response:

```json
{
  "message": "Welcome to Kaggle Platform API",
  "docs": "/docs",
  "api_version": "v1",
  "health_check": "/health"
}
```

Open **http://localhost:8000/docs** in your browser to explore the interactive Swagger UI.

---

## Troubleshooting

### `alembic upgrade head` fails with "can't connect to database"

Make sure the database service is running before applying migrations. With Docker:

```bash
docker compose up db -d
# Wait for the health check to pass, then:
docker compose exec backend alembic upgrade head
```

### Backend fails to start: `ModuleNotFoundError`

Ensure the virtual environment is activated and dependencies are installed:

```bash
pip install -r requirements.txt
```

### Frontend can't reach the API (`CORS` or `Network Error`)

The backend allows all origins by default (`allow_origins=["*"]`). Make sure the backend is running on port `8000` and the frontend `vite.config.ts` proxy is configured correctly.

### MinIO bucket not found

The bucket `kaggle-platform` must exist before the backend can store files. Create it via the MinIO console at **http://localhost:9001** (credentials: `minioadmin` / `minioadmin`) or run:

```bash
docker compose exec minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker compose exec minio mc mb local/kaggle-platform
```

### Port conflicts

If any port (`8000`, `6379`, `5432`, `9000`, `3000`) is already in use, either stop the conflicting process or edit the port mapping in `docker-compose.yml`.

### Windows: `venv\Scripts\Activate.ps1` blocked by execution policy

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
