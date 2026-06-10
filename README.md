# Kaggle-like Data Science Platform

A full-stack data science competition and collaboration platform.

## Features

- **User & Portfolio Management**: Authentication, profiles, skills, social links
- **Dataset Management**: Upload, version, and share datasets
- **Notebooks & Compute**: Jupyter-like notebooks with sandboxed Docker containers (CPU/GPU/TPU)
- **Competitions**: Create contests, submit predictions, live leaderboards via WebSockets
- **E-Learning (LMS)**: Courses, lessons, and progress tracking
- **Community**: Discussion forums with upvoting
- **Job Board**: Company postings with tier requirements

## Tech Stack

### Backend
- **FastAPI** — ASGI web framework with auto-generated OpenAPI docs
- **SQLAlchemy 2.0** — ORM with PostgreSQL/SQLite support
- **Redis** — Caching, session store, and Pub/Sub for real-time features
- **Celery** — Background task queue for competition evaluation and compute provisioning
- **Boto3/MinIO** — Object storage for datasets and notebook files
- **Docker SDK** — Sandbox container orchestration for user code execution
- **WebSockets** — Real-time leaderboard updates

### Frontend
- **React 18 + TypeScript** — Component-based SPA
- **Vite** — Build tooling with HMR
- **Tailwind CSS** — Utility-first styling
- **React Router** — Client-side routing
- **Axios** — API client with JWT interceptors

## Quick Start

### Backend
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Background Worker (Celery)
```bash
celery -A app.core.celery_app worker --loglevel=info
```

### Required Services
- **PostgreSQL** (or SQLite for dev)
- **Redis** — `redis-server`
- **MinIO** (or AWS S3) — `docker run -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ':9001'`
- **Docker** — for notebook sandboxing

## Architecture

```
[ User Browser (React) ]
       |
       v (REST API / WebSockets)
[ API Layer (FastAPI) ] <--> [ Database (PostgreSQL) ]
       |
       |--> [ File Storage (MinIO / S3) ]
       |
       |--> [ Cache & Pub/Sub (Redis) ]
       |
       v (Background tasks)
[ Celery Workers ] <--> [ Docker Sandbox ]
```

## Project Structure

```
app/
  core/          # Config, database, security, redis, s3, celery, docker
  models/        # SQLAlchemy ORM models
  schemas/       # Pydantic request/response models
  crud/          # Database operations per entity
  api/           # FastAPI routers, WebSockets, dependencies
  tasks/         # Celery background tasks
  main.py        # Application entry point
frontend/
  src/
    api/         # Axios client
    components/  # Shared UI components
    context/     # React contexts (Auth)
    pages/       # Route-level pages
```
