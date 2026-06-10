# API Documentation — Kaggle-like Data Science Platform

**Base URL:** `http://localhost:8000/api/v1`  
**Interactive Docs:** `http://localhost:8000/docs` (Swagger UI) · `http://localhost:8000/redoc` (ReDoc)  
**Authentication:** Bearer token (JWT) — obtain via `/api/v1/auth/login`

---

## Table of Contents

- [Authentication](#authentication)
- [Users](#users)
- [Datasets](#datasets)
- [Notebooks](#notebooks)
- [Competitions](#competitions)
- [Courses & Lessons](#courses--lessons)
- [Community (Posts & Upvotes)](#community-posts--upvotes)
- [Jobs](#jobs)
- [WebSockets](#websockets)
- [Data Models](#data-models)
- [Error Responses](#error-responses)

---

## Authentication

All protected endpoints require the following HTTP header:

```
Authorization: Bearer <access_token>
```

### POST `/auth/register`

Register a new user account.

**Request body:**

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secret123"
}
```

**Response `200`:**

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "global_tier": "Novice",
  "created_at": "2024-01-01T00:00:00"
}
```

**Errors:**
- `400` — Email already registered
- `400` — Username already taken

---

### POST `/auth/login`

Authenticate and receive a JWT token.

**Request body** (`application/x-www-form-urlencoded`):

```
username=john_doe&password=secret123
```

**Response `200`:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `400` — Incorrect username or password

---

## Users

### GET `/users/me` 🔒

Get the currently authenticated user's details.

**Response `200`:** [User](#user)

---

### PUT `/users/me` 🔒

Update the currently authenticated user's account fields.

**Request body:**

```json
{
  "username": "new_username",
  "email": "new@example.com",
  "password": "new_password"
}
```

All fields are optional. **Response `200`:** [User](#user)

---

### GET `/users/{username}`

Get a user's public profile by username.

**Path parameter:** `username` — the target user's username

**Response `200`:**

```json
{
  "id": 1,
  "username": "john_doe",
  "global_tier": "Expert",
  "created_at": "2024-01-01T00:00:00",
  "profile": {
    "id": 1,
    "user_id": 1,
    "full_name": "John Doe",
    "bio": "Data scientist",
    "github_url": "https://github.com/johndoe",
    "linkedin_url": null,
    "is_seeking_job": true,
    "total_upvotes": 73
  }
}
```

**Errors:**
- `404` — User not found

---

### PUT `/users/profile/update` 🔒

Update the current user's profile information.

**Request body:**

```json
{
  "full_name": "John Doe",
  "bio": "ML engineer and Kaggle enthusiast",
  "github_url": "https://github.com/johndoe",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "is_seeking_job": false
}
```

All fields are optional. **Response `200`:** [UserProfile](#userprofile)

**Errors:**
- `404` — Profile not found

---

## Datasets

### GET `/datasets/`

List public, active datasets.

**Query parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | `0` | Pagination offset |
| `limit` | int | `100` | Max records returned |
| `search` | string | — | Filter by title (case-insensitive) |
| `sort` | string | `newest` | Sort order: `newest` or `downloads` |

**Response `200`:** Array of [Dataset](#dataset)

---

### POST `/datasets/` 🔒

Create a new dataset and get a presigned S3 upload URL.

**Request body:**

```json
{
  "title": "Titanic Survivors",
  "slug": "titanic-survivors",
  "description": "Classic Titanic dataset",
  "is_public": true
}
```

**Response `200`:**

```json
{
  "dataset": { ...Dataset },
  "upload_url": "http://minio:9000/kaggle-platform/datasets/1/titanic-survivors?..."
}
```

---

### GET `/datasets/{dataset_id}`

Get a dataset by ID.

**Response `200`:** [Dataset](#dataset) | `404` — Dataset not found

---

### GET `/datasets/slug/{slug}`

Get a dataset by its slug.

**Response `200`:** [Dataset](#dataset) | `404` — Dataset not found

---

### PUT `/datasets/{dataset_id}` 🔒

Update a dataset. Only the owner can update.

**Request body:**

```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "is_public": false
}
```

All fields optional. **Response `200`:** [Dataset](#dataset)

**Errors:**
- `403` — Not authorized (not the owner)
- `404` — Dataset not found

---

### DELETE `/datasets/{dataset_id}` 🔒

Delete a dataset. Only the owner can delete.

**Response `200`:**

```json
{ "message": "Dataset deleted" }
```

**Errors:**
- `403` — Not authorized
- `404` — Dataset not found

---

### GET `/datasets/{dataset_id}/download`

Get a presigned download URL for a public dataset. Increments `downloads_count`.

**Response `200`:**

```json
{ "download_url": "http://..." }
```

**Errors:**
- `403` — Dataset is private
- `404` — Dataset not found

---

### GET `/datasets/{dataset_id}/files`

List all files in a dataset.

**Response `200`:** Array of [DatasetFile](#datasetfile)

---

### POST `/datasets/{dataset_id}/files` 🔒

Add a file record to a dataset. Only the owner can add files.

**Request body:**

```json
{
  "file_name": "train.csv",
  "storage_path_url": "http://minio:9000/kaggle-platform/datasets/1/train.csv",
  "file_size_bytes": 102400,
  "file_type": "text/csv"
}
```

**Response `200`:** [DatasetFile](#datasetfile)

**Errors:**
- `403` — Not authorized
- `404` — Dataset not found

---

## Notebooks

### GET `/notebooks/`

List all notebooks.

**Query parameters:** `skip` (int, default `0`), `limit` (int, default `100`)

**Response `200`:** Array of [Notebook](#notebook)

---

### POST `/notebooks/` 🔒

Create a new notebook.

**Request body:**

```json
{
  "title": "My EDA Notebook",
  "description": "Exploratory data analysis",
  "language": "python",
  "storage_path_url": null
}
```

**Response `200`:** [Notebook](#notebook)

---

### GET `/notebooks/{notebook_id}`

Get a notebook by ID.

**Response `200`:** [Notebook](#notebook) | `404` — Notebook not found

---

### PUT `/notebooks/{notebook_id}` 🔒

Update a notebook. Only the creator can update.

**Request body:**

```json
{
  "title": "Updated Title",
  "description": "New description",
  "language": "r",
  "storage_path_url": "http://..."
}
```

All fields optional. **Response `200`:** [Notebook](#notebook)

**Errors:**
- `403` — Not authorized
- `404` — Notebook not found

---

### DELETE `/notebooks/{notebook_id}` 🔒

Delete a notebook. Only the creator can delete.

**Response `200`:**

```json
{ "message": "Notebook deleted" }
```

---

### POST `/notebooks/{notebook_id}/fork` 🔒

Fork a notebook. Creates a copy attributed to the current user.

**Response `200`:** [Notebook](#notebook) (new forked notebook)

**Errors:**
- `404` — Notebook not found

---

### POST `/notebooks/{notebook_id}/attach-dataset` 🔒

Link a dataset to a notebook for use in compute sessions.

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | int | ID of the dataset to attach |

**Response `200`:**

```json
{ "message": "Dataset attached to notebook" }
```

---

### POST `/notebooks/{notebook_id}/session/start` 🔒

Start a compute session (Docker container) for notebook execution. Triggers an async Celery task.

**Request body:**

```json
{
  "hardware_target": "CPU",
  "user_id": 1
}
```

`hardware_target` can be `CPU` or `GPU`.

**Response `200`:**

```json
{
  "session": { ...ComputeSession },
  "task_id": "celery-task-uuid"
}
```

**Errors:**
- `403` — Not authorized
- `404` — Notebook not found

---

## Competitions

### GET `/competitions/`

List all competitions.

**Query parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | `0` | Pagination offset |
| `limit` | int | `100` | Max records |
| `status` | string | — | Filter by status (e.g. `Active`, `Completed`) |

**Response `200`:** Array of [Competition](#competition)

---

### POST `/competitions/` 🔒

Create a new competition.

**Request body:**

```json
{
  "title": "House Price Prediction",
  "description_markdown": "## Overview\nPredict house prices...",
  "evaluation_metric": "RMSE",
  "ground_truth_file_path": "s3://kaggle-platform/competitions/1/ground_truth.csv",
  "prize_pool": "10000.00",
  "start_date": "2024-06-01T00:00:00",
  "end_date": "2024-09-01T00:00:00"
}
```

**Response `200`:** [Competition](#competition)

---

### GET `/competitions/{competition_id}`

Get a competition by ID.

**Response `200`:** [Competition](#competition) | `404` — Competition not found

---

### PUT `/competitions/{competition_id}` 🔒

Update a competition. Only the creator can update.

**Request body:**

```json
{
  "title": "New Title",
  "status": "Completed"
}
```

All fields optional. **Response `200`:** [Competition](#competition)

**Errors:**
- `403` — Not authorized
- `404` — Competition not found

---

### DELETE `/competitions/{competition_id}` 🔒

Delete a competition. Only the creator can delete.

**Response `200`:**

```json
{ "message": "Competition deleted" }
```

---

### GET `/competitions/{competition_id}/submissions`

List all submissions for a competition.

**Query parameters:** `skip` (int), `limit` (int)

**Response `200`:** Array of [Submission](#submission)

---

### POST `/competitions/{competition_id}/submissions` 🔒

Submit a solution to a competition. Triggers async evaluation via Celery.

**Request body:**

```json
{
  "submitted_file_url": "http://minio:9000/kaggle-platform/submissions/my_submission.csv"
}
```

**Response `200`:** [Submission](#submission)

**Errors:**
- `400` — Competition deadline has passed
- `404` — Competition not found

---

### GET `/competitions/{competition_id}/leaderboard`

Get the leaderboard for a competition. Returns cached data when available.

**Response `200`:**

```json
{
  "source": "cache",
  "data": [
    {
      "id": 1,
      "competition_id": 1,
      "user_id": 3,
      "best_score": 0.9823,
      "rank_position": 1,
      "last_submission_time": "2024-08-15T12:00:00"
    }
  ]
}
```

`source` is either `"cache"` (Redis) or `"database"`.

---

## Courses & Lessons

### GET `/courses/`

List all courses.

**Query parameters:** `skip` (int), `limit` (int)

**Response `200`:** Array of [Course](#course)

---

### POST `/courses/` 🔒

Create a new course.

**Request body:**

```json
{
  "title": "Intro to Pandas",
  "summary": "Learn data manipulation with Pandas",
  "difficulty": "Beginner"
}
```

`difficulty` options: `Beginner`, `Intermediate`, `Advanced`

**Response `200`:** [Course](#course)

---

### GET `/courses/{course_id}`

Get a course by ID (includes lessons list).

**Response `200`:** [Course](#course) | `404` — Course not found

---

### PUT `/courses/{course_id}` 🔒

Update a course.

**Request body:**

```json
{
  "title": "Advanced Pandas",
  "difficulty": "Advanced"
}
```

All fields optional. **Response `200`:** [Course](#course)

---

### DELETE `/courses/{course_id}` 🔒

Delete a course.

**Response `200`:**

```json
{ "message": "Course deleted" }
```

---

### GET `/courses/{course_id}/lessons`

List all lessons for a course.

**Response `200`:** Array of [Lesson](#lesson)

---

### POST `/courses/{course_id}/lessons` 🔒

Add a lesson to a course.

**Request body:**

```json
{
  "course_id": 1,
  "order_index": 1,
  "title": "DataFrames 101",
  "text_content": "In this lesson we cover...",
  "tutorial_notebook_id": 5,
  "exercise_notebook_id": 6
}
```

**Response `200`:** [Lesson](#lesson)

**Errors:**
- `404` — Course not found

---

### GET `/lessons/{lesson_id}`

Get a lesson by ID.

**Response `200`:** [Lesson](#lesson) | `404` — Lesson not found

---

### PUT `/lessons/{lesson_id}` 🔒

Update a lesson.

**Request body:**

```json
{
  "title": "Updated Lesson Title",
  "text_content": "Updated content..."
}
```

All fields optional. **Response `200`:** [Lesson](#lesson)

---

### POST `/lessons/{lesson_id}/complete` 🔒

Mark a lesson as completed for the current user.

**Response `200`:** [UserCourseProgress](#usercourseprogress)

**Errors:**
- `400` — Lesson already completed

---

## Community (Posts & Upvotes)

### GET `/posts/`

List all discussion posts.

**Query parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | `0` | Pagination offset |
| `limit` | int | `100` | Max records |
| `category` | string | — | Filter by category |

**Response `200`:** Array of [DiscussionPost](#discussionpost)

---

### POST `/posts/` 🔒

Create a new discussion post.

**Request body:**

```json
{
  "title": "How to handle missing values?",
  "content_body": "I have a dataset with 30% missing values...",
  "category": "GENERAL"
}
```

**Response `200`:** [DiscussionPost](#discussionpost)

---

### GET `/posts/{post_id}`

Get a post by ID.

**Response `200`:** [DiscussionPost](#discussionpost) | `404` — Post not found

---

### PUT `/posts/{post_id}` 🔒

Update a post. Only the author can update.

**Request body:**

```json
{
  "title": "Updated Title",
  "content_body": "Updated content",
  "category": "TUTORIAL"
}
```

All fields optional. **Response `200`:** [DiscussionPost](#discussionpost)

**Errors:**
- `403` — Not authorized
- `404` — Post not found

---

### DELETE `/posts/{post_id}` 🔒

Delete a post. Only the author can delete.

**Response `200`:**

```json
{ "message": "Post deleted" }
```

---

### POST `/upvote/` 🔒

Upvote a resource. Automatically updates owner's tier when thresholds are reached.

**Request body:**

```json
{
  "target_type": "Dataset",
  "target_id": 3
}
```

`target_type` options: `Dataset`, `Notebook`, `Post`

**Response `200`:** [Upvote](#upvote)

**Errors:**
- `400` — Already upvoted

**Tier thresholds:**

| Tier | Upvotes Required |
|------|-----------------|
| Novice | 0 |
| Contributor | 10 |
| Expert | 50 |
| Master | 100 |
| Grandmaster | 500 |

When a tier upgrade occurs, a real-time notification is published to the Redis channel `notifications:{user_id}`.

---

## Jobs

### GET `/jobs/`

List job postings.

**Query parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | `0` | Pagination offset |
| `limit` | int | `100` | Max records |
| `tier` | string | — | Filter by `minimum_tier_required` |
| `keyword` | string | — | Search in job title or company name |

**Response `200`:** Array of [JobPosting](#jobposting)

---

### POST `/jobs/` 🔒

Create a new job posting.

**Request body:**

```json
{
  "company_name": "DataCorp Inc.",
  "job_title": "Senior Data Scientist",
  "description": "We are looking for an experienced data scientist...",
  "minimum_tier_required": "Expert"
}
```

**Response `200`:** [JobPosting](#jobposting)

---

### GET `/jobs/{job_id}`

Get a job posting by ID.

**Response `200`:** [JobPosting](#jobposting) | `404` — Job posting not found

---

### PUT `/jobs/{job_id}` 🔒

Update a job posting.

**Request body:**

```json
{
  "job_title": "Lead Data Scientist",
  "minimum_tier_required": "Master"
}
```

All fields optional. **Response `200`:** [JobPosting](#jobposting)

---

### DELETE `/jobs/{job_id}` 🔒

Delete a job posting.

**Response `200`:**

```json
{ "message": "Job posting deleted" }
```

---

## WebSockets

WebSocket endpoints do not use the standard REST `/api/v1` prefix — they are mounted directly under `/api/v1/ws`.

### WS `/ws/leaderboard/{competition_id}`

Subscribe to real-time leaderboard updates for a competition.

**Connection URL:**
```
ws://localhost:8000/api/v1/ws/leaderboard/1
```

**Messages received** (JSON):

```json
{
  "user_id": 3,
  "rank": 1,
  "score": 0.9823,
  "updated_at": "2024-08-15T12:00:00"
}
```

Messages are pushed whenever a new leaderboard event is published to the Redis pub/sub channel `leaderboard:{competition_id}`.

---

### WS `/ws/notebooks/{notebook_id}/execute`

Execute code inside an active compute session container.

**Connection URL:**
```
ws://localhost:8000/api/v1/ws/notebooks/5/execute
```

**Send a message (JSON):**

```json
{ "action": "run", "code": "import pandas as pd\nprint(pd.__version__)" }
```

**Received on success:**

```json
{ "type": "output", "output": "2.2.1\n" }
```

**Received on error:**

```json
{ "type": "error", "message": "No active compute session. Start a session first." }
```

**Ping / Pong heartbeat:**

Send:
```json
{ "action": "ping" }
```
Receive:
```json
{ "type": "pong" }
```

> A compute session must be started via `POST /notebooks/{notebook_id}/session/start` before code execution is possible.

---

## Data Models

### User

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "global_tier": "Novice",
  "created_at": "2024-01-01T00:00:00"
}
```

`global_tier` values: `Novice`, `Contributor`, `Expert`, `Master`, `Grandmaster`

---

### UserProfile

```json
{
  "id": 1,
  "user_id": 1,
  "full_name": "John Doe",
  "bio": "Data scientist",
  "github_url": "https://github.com/johndoe",
  "linkedin_url": null,
  "is_seeking_job": true,
  "total_upvotes": 73
}
```

---

### Dataset

```json
{
  "id": 1,
  "title": "Titanic Survivors",
  "slug": "titanic-survivors",
  "description": "Classic Titanic dataset",
  "status": "Active",
  "is_public": true,
  "owner_id": 1,
  "views_count": 150,
  "downloads_count": 42,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-02T00:00:00",
  "files": []
}
```

`status` values: `PENDING`, `Active`, `Archived`

---

### DatasetFile

```json
{
  "id": 1,
  "dataset_id": 1,
  "file_name": "train.csv",
  "storage_path_url": "http://minio:9000/kaggle-platform/datasets/1/train.csv",
  "file_size_bytes": 102400,
  "file_type": "text/csv"
}
```

---

### Notebook

```json
{
  "id": 1,
  "title": "My EDA Notebook",
  "description": "Exploratory data analysis",
  "language": "python",
  "storage_path_url": null,
  "creator_id": 1,
  "forked_from_id": null,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

---

### ComputeSession

```json
{
  "id": 1,
  "notebook_id": 1,
  "user_id": 1,
  "hardware_target": "CPU",
  "container_id": "abc123def456",
  "session_status": "Active",
  "start_time": "2024-01-01T10:00:00",
  "end_time": null,
  "allowed_quota_remaining_minutes": 480
}
```

`session_status` values: `Pending`, `Active`, `Stopped`, `Failed`

---

### Competition

```json
{
  "id": 1,
  "title": "House Price Prediction",
  "description_markdown": "## Overview\n...",
  "evaluation_metric": "RMSE",
  "ground_truth_file_path": "s3://...",
  "prize_pool": "10000.00",
  "start_date": "2024-06-01T00:00:00",
  "end_date": "2024-09-01T00:00:00",
  "status": "Active",
  "creator_id": 1,
  "created_at": "2024-05-01T00:00:00"
}
```

`status` values: `Active`, `Completed`, `Upcoming`

---

### Submission

```json
{
  "id": 1,
  "competition_id": 1,
  "user_id": 2,
  "submitted_file_url": "http://minio:9000/...",
  "score": 0.9345,
  "status": "Scored",
  "submitted_at": "2024-07-15T14:30:00"
}
```

`status` values: `Pending`, `Scoring`, `Scored`, `Failed`

---

### Course

```json
{
  "id": 1,
  "title": "Intro to Pandas",
  "summary": "Learn data manipulation",
  "difficulty": "Beginner",
  "created_at": "2024-01-01T00:00:00",
  "lessons": []
}
```

---

### Lesson

```json
{
  "id": 1,
  "course_id": 1,
  "order_index": 1,
  "title": "DataFrames 101",
  "text_content": "In this lesson...",
  "tutorial_notebook_id": 5,
  "exercise_notebook_id": 6
}
```

---

### UserCourseProgress

```json
{
  "user_id": 1,
  "lesson_id": 3,
  "is_completed": true,
  "completed_at": "2024-03-10T09:00:00"
}
```

---

### DiscussionPost

```json
{
  "id": 1,
  "title": "How to handle missing values?",
  "content_body": "I have a dataset...",
  "category": "GENERAL",
  "author_id": 1,
  "created_at": "2024-01-05T11:00:00",
  "updated_at": "2024-01-05T11:00:00"
}
```

---

### Upvote

```json
{
  "id": 1,
  "target_type": "Dataset",
  "target_id": 3,
  "user_id": 2,
  "created_at": "2024-02-01T08:00:00"
}
```

---

### JobPosting

```json
{
  "id": 1,
  "company_name": "DataCorp Inc.",
  "job_title": "Senior Data Scientist",
  "description": "We are looking for...",
  "minimum_tier_required": "Expert",
  "posted_at": "2024-05-01T00:00:00"
}
```

---

## Error Responses

All errors follow a consistent JSON format:

```json
{
  "detail": "Human-readable error message"
}
```

| HTTP Status | Meaning |
|-------------|---------|
| `400` | Bad request — invalid input or business rule violation |
| `401` | Unauthorized — missing or invalid Bearer token |
| `403` | Forbidden — authenticated but not permitted |
| `404` | Not found — resource does not exist |
| `422` | Unprocessable Entity — request body validation failed |
| `500` | Internal Server Error — unexpected server-side error |

### Example `422` Validation Error

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "title"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

---

## Quick Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | — | Register new user |
| POST | `/auth/login` | — | Login, get JWT |
| GET | `/users/me` | 🔒 | Get current user |
| PUT | `/users/me` | 🔒 | Update current user |
| GET | `/users/{username}` | — | Get public profile |
| PUT | `/users/profile/update` | 🔒 | Update profile |
| GET | `/datasets/` | — | List datasets |
| POST | `/datasets/` | 🔒 | Create dataset |
| GET | `/datasets/{id}` | — | Get dataset |
| PUT | `/datasets/{id}` | 🔒 | Update dataset |
| DELETE | `/datasets/{id}` | 🔒 | Delete dataset |
| GET | `/datasets/{id}/download` | — | Download dataset |
| GET | `/datasets/{id}/files` | — | List dataset files |
| POST | `/datasets/{id}/files` | 🔒 | Add dataset file |
| GET | `/notebooks/` | — | List notebooks |
| POST | `/notebooks/` | 🔒 | Create notebook |
| GET | `/notebooks/{id}` | — | Get notebook |
| PUT | `/notebooks/{id}` | 🔒 | Update notebook |
| DELETE | `/notebooks/{id}` | 🔒 | Delete notebook |
| POST | `/notebooks/{id}/fork` | 🔒 | Fork notebook |
| POST | `/notebooks/{id}/attach-dataset` | 🔒 | Attach dataset |
| POST | `/notebooks/{id}/session/start` | 🔒 | Start compute session |
| GET | `/competitions/` | — | List competitions |
| POST | `/competitions/` | 🔒 | Create competition |
| GET | `/competitions/{id}` | — | Get competition |
| PUT | `/competitions/{id}` | 🔒 | Update competition |
| DELETE | `/competitions/{id}` | 🔒 | Delete competition |
| GET | `/competitions/{id}/submissions` | — | List submissions |
| POST | `/competitions/{id}/submissions` | 🔒 | Submit solution |
| GET | `/competitions/{id}/leaderboard` | — | Get leaderboard |
| GET | `/courses/` | — | List courses |
| POST | `/courses/` | 🔒 | Create course |
| GET | `/courses/{id}` | — | Get course |
| PUT | `/courses/{id}` | 🔒 | Update course |
| DELETE | `/courses/{id}` | 🔒 | Delete course |
| GET | `/courses/{id}/lessons` | — | List lessons |
| POST | `/courses/{id}/lessons` | 🔒 | Add lesson |
| GET | `/lessons/{id}` | — | Get lesson |
| PUT | `/lessons/{id}` | 🔒 | Update lesson |
| POST | `/lessons/{id}/complete` | 🔒 | Mark lesson complete |
| GET | `/posts/` | — | List posts |
| POST | `/posts/` | 🔒 | Create post |
| GET | `/posts/{id}` | — | Get post |
| PUT | `/posts/{id}` | 🔒 | Update post |
| DELETE | `/posts/{id}` | 🔒 | Delete post |
| POST | `/upvote/` | 🔒 | Upvote resource |
| GET | `/jobs/` | — | List jobs |
| POST | `/jobs/` | 🔒 | Create job posting |
| GET | `/jobs/{id}` | — | Get job posting |
| PUT | `/jobs/{id}` | 🔒 | Update job posting |
| DELETE | `/jobs/{id}` | 🔒 | Delete job posting |
| WS | `/ws/leaderboard/{competition_id}` | — | Real-time leaderboard |
| WS | `/ws/notebooks/{notebook_id}/execute` | — | Notebook code execution |
