# Kaggle-like Data Science Platform

A production-ready, full-stack data science competition and collaboration platform with enterprise-grade security, sandboxed code execution, and real-time features.

## Features

- **JWT Authentication & RBAC** — Token-based auth with role-based access control and resource ownership enforcement
- **Dataset Upload Pipeline** — Pre-signed S3/MinIO URLs for direct client uploads, async validation (magic bytes, virus scan, shape analysis)
- **Interactive Notebooks** — WebSocket-based code execution with Docker sandboxing, read-only dataset mounts, and live output streaming
- **Competitions & Leaderboards** — Automated grading pipeline with deadline enforcement, Redis caching, and real-time leaderboard updates
- **Community & Gamification** — Upvote system with tier advancement (Novice → Grandmaster) and Redis pub/sub notifications
- **E-Learning (LMS)** — Courses, lessons, and user progress tracking
- **Job Board** — Company postings with minimum tier requirements

## Tech Stack

### Backend
- **FastAPI** — ASGI web framework with auto-generated OpenAPI docs
- **SQLAlchemy 2.0 + Alembic** — ORM with PostgreSQL support and database migrations
- **Redis** — Caching, session store, Pub/Sub for real-time notifications
- **Celery** — Background task queue for dataset validation, competition grading, compute provisioning
- **Boto3/MinIO** — Object storage for datasets and notebook files
- **Docker SDK** — Sandbox container orchestration with network isolation, cgroups, and read-only mounts
- **WebSockets** — Real-time notebook execution output and leaderboard updates

### Frontend
- **React 18 + TypeScript** — Component-based SPA
- **Vite** — Build tooling with HMR
- **Tailwind CSS** — Utility-first styling
- **React Router** — Client-side routing
- **Axios** — API client with JWT interceptors

## Architecture

```
User Browser (React)
       |
       | HTTP / WebSocket
       v
+-------------------+     +------------------+
|   Nginx / CDN     |---->|  FastAPI Backend |
+-------------------+     +------------------+
                                 |
          +----------------------+----------------------+
          |                      |                      |
          v                      v                      v
+------------------+  +------------------+  +------------------+
|   PostgreSQL     |  |     Redis        |  |   MinIO / S3     |
|   (Users, Datasets |  | (Cache, Pub/Sub, |  | (File Storage)  |
|   Competitions...) |  |  Celery Broker)  |  |                  |
+------------------+  +------------------+  +------------------+
                               |
                               v
                       +------------------+
                       |  Celery Worker   |
                       |  (Docker Sandbox |
                       |   for notebooks, |
                       |   competition    |
                       |   grading)       |
                       +------------------+
```

## Security Architecture

### 1. Authentication & Authorization
- **JWT Token-Based Identity** — Encrypted, time-bound tokens (HS256, 7-day expiry)
- **RBAC Enforcement** — Users can only modify resources they own (`owner_id` / `creator_id` match)
- **Admin/Worker Exceptions** — System admins and background workers bypass ownership checks

### 2. Docker Sandbox (Compute Isolation)
- **No Root Privileges** — Containers run as `uid=1000` (guest user)
- **Network Isolation** — Internal Docker bridge network with no external internet access
- **Resource Caps** — CGroup limits: 2 CPUs, 4GB RAM, 12-hour max runtime
- **Read-Only Filesystem** — Dataset mounts are read-only volumes
- **Capability Drop** — `cap_drop=ALL` removes all Linux capabilities

### 3. Dataset Upload Security
- **Pre-Signed URLs** — 15-minute expiry direct-to-S3 upload URLs (server never touches the file)
- **Magic Bytes Check** — Validates file type matches extension
- **Virus Scan Placeholder** — Integration point for ClamAV or cloud AV
- **Shape Analysis** — Reads CSV/JSON row/column counts before marking dataset as Active

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/h19kod/kaggle.git
cd kaggle

# Start all services
docker-compose up --build

# Access the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# MinIO Console: http://localhost:9001 (minioadmin / minioadmin)
```

### Option 2: Local Development

#### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+ (or SQLite for quick testing)
- Redis 7+
- MinIO (or AWS S3 credentials)
- Docker (for notebook sandboxing)

#### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your database, Redis, and S3 credentials

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

#### Background Worker

```bash
# In a separate terminal
celery -A app.core.celery_app worker --loglevel=info
```

## API Documentation

Once the backend is running, explore the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

### Key Endpoints

| Module | Endpoint | Description |
|--------|----------|-------------|
| Auth | `POST /api/v1/auth/register` | User registration |
| Auth | `POST /api/v1/auth/login` | JWT token generation |
| Datasets | `POST /api/v1/datasets/` | Create dataset (returns pre-signed upload URL) |
| Datasets | `GET /api/v1/datasets/` | List active datasets with search/sort |
| Notebooks | `POST /api/v1/notebooks/` | Create notebook |
| Notebooks | `POST /api/v1/notebooks/{id}/session/start` | Launch Docker sandbox |
| Notebooks | `WS /api/v1/ws/notebooks/{id}/execute` | Real-time code execution |
| Competitions | `POST /api/v1/competitions/` | Create competition |
| Competitions | `POST /api/v1/competitions/{id}/submissions` | Submit predictions |
| Competitions | `GET /api/v1/competitions/{id}/leaderboard` | Cached leaderboard |
| Competitions | `WS /api/v1/ws/leaderboard/{id}` | Live leaderboard updates |
| Community | `POST /api/v1/posts/` | Create discussion post |
| Community | `POST /api/v1/upvote/` | Upvote content |
| Jobs | `GET /api/v1/jobs/` | List job postings |

## Testing

```bash
# Run all tests with pytest
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Run specific test file
python -m pytest tests/test_auth.py -v
```

### Test Suite Coverage

- **Auth Tests** — Registration, login, JWT validation, unauthorized access
- **Dataset Tests** — CRUD, ownership enforcement, public/private filtering
- **Notebook Tests** — Creation, forking, update restrictions
- **Competition Tests** — Creation, deadline enforcement, submission handling
- **Community Tests** — Post creation, upvote idempotency, profile sync

## Database Migrations

```bash
# Generate migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one revision
alembic downgrade -1
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `sqlite:///./kaggle_platform.db` |
| `SECRET_KEY` | JWT signing key | `super-secret-key-change-in-production` |
| `REDIS_HOST` | Redis server hostname | `localhost` |
| `REDIS_PORT` | Redis server port | `6379` |
| `S3_ENDPOINT` | S3/MinIO endpoint | `http://localhost:9000` |
| `S3_ACCESS_KEY` | S3 access key | `minioadmin` |
| `S3_SECRET_KEY` | S3 secret key | `minioadmin` |
| `S3_BUCKET_NAME` | S3 bucket name | `kaggle-platform` |
| `CELERY_BROKER_URL` | Celery message broker | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://localhost:6379/0` |

## Project Structure

```
kaggle/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration scripts
│   ├── env.py                  # Alembic environment config
│   └── script.py.mako          # Migration template
├── app/                        # FastAPI backend
│   ├── api/                    # API layer
│   │   ├── deps.py             # Auth dependencies (JWT, current_user)
│   │   └── v1/
│   │       ├── api.py          # Router aggregation
│   │       └── endpoints/      # Route handlers
│   │           ├── auth.py
│   │           ├── community.py
│   │           ├── competitions.py
│   │           ├── courses.py
│   │           ├── datasets.py
│   │           ├── jobs.py
│   │           ├── notebooks.py
│   │           ├── users.py
│   │           └── ws.py       # WebSocket endpoints
│   ├── core/                   # Core infrastructure
│   │   ├── celery_app.py       # Celery configuration
│   │   ├── config.py           # Pydantic settings
│   │   ├── database.py         # SQLAlchemy engine & session
│   │   ├── docker_sandbox.py   # Docker container management
│   │   ├── redis_client.py     # Redis cache & pub/sub
│   │   ├── s3_client.py        # S3/MinIO service
│   │   └── security.py         # Password hashing & JWT
│   ├── crud/                   # CRUD operations per entity
│   ├── models/                   # SQLAlchemy ORM models
│   ├── schemas/                  # Pydantic request/response models
│   ├── tasks/                    # Celery background tasks
│   │   ├── compute.py            # Docker sandbox lifecycle
│   │   ├── datasets.py           # Dataset validation
│   │   └── evaluation.py         # Competition grading
│   └── main.py                   # Application entry point
├── frontend/                     # React SPA
│   ├── src/
│   │   ├── api/                  # Axios client with JWT interceptors
│   │   ├── components/           # Shared UI components
│   │   ├── context/              # React contexts (AuthProvider)
│   │   └── pages/                # Route-level pages
│   ├── Dockerfile.frontend
│   ├── package.json
│   └── vite.config.ts
├── tests/                        # Pytest test suite
│   ├── conftest.py               # Fixtures & test database setup
│   ├── test_auth.py
│   ├── test_community.py
│   ├── test_competitions.py
│   ├── test_datasets.py
│   └── test_notebooks.py
├── docker-compose.yml            # Full stack orchestration
├── Dockerfile.backend
├── requirements.txt
└── README.md
```

## Deployment

### Production Checklist

- [ ] Change `SECRET_KEY` to a cryptographically secure random string
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure real S3 bucket or production MinIO cluster
- [ ] Enable Redis password authentication
- [ ] Set up SSL/TLS termination (Nginx / Traefik / Cloudflare)
- [ ] Configure Docker daemon for secure sandboxing (userns-remap, seccomp profiles)
- [ ] Set up monitoring (Prometheus + Grafana) and logging (ELK / Loki)
- [ ] Run Celery workers on dedicated nodes for compute isolation
- [ ] Configure automated backups for PostgreSQL and S3

## License

MIT License
