# Clean FastAPI

A FastAPI project structured around a simple “clean architecture”-style layering (controllers → services → models/entities) with:

- **Auth** (register + login with JWT access tokens)
- **Users** CRUD + password change
- **Jobs** CRUD + complete job workflow
- **PostgreSQL** (Docker) + **SQLAlchemy** + **Alembic** migrations
- **Rate limiting** with `slowapi`
- **Pytest** unit/e2e test setup


---

## Tech stack

- **FastAPI**
- **SQLAlchemy 2.x**
- **Alembic**
- **PostgreSQL** (via `docker-compose`)
- **JWT Auth** (`pyjwt`)
- **Password hashing** (`bcrypt` + `passlib`)
- **Rate limiting** (`slowapi`)
- Tooling: **ruff**, **black**, **mypy**, **pre-commit**, **pytest**

---

## Project structure

High-level layout:

- `main.py` — FastAPI app + router registration + SlowAPI middleware
- `src/`
  - `auth/` — auth controller + service + request models
  - `users/` — user controller + service + request/response models
  - `jobs/` — job controller + service + request/response models
  - `entities/` — SQLAlchemy entities (`User`, `Job`, `Priority`, etc.)
  - `db/` — DB setup and session dependency
  - `security/` — JWT + password utilities
  - `errors/` — custom domain errors
  - `rate_limiting.py` — shared limiter + exception handler
- `alembic/` + `alembic.ini` — migrations
- `tests/` — pytest setup + unit/e2e tests
- `.env.example` — environment variables template
- `docker-compose.yml` — local Postgres

---

## Requirements

- Python **3.14+**
- Docker for local Postgres

---

## Configuration

Create a `.env` file based on `.env.example`:

```dotenv
DB_URL=
SECRET_KEY=
ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=
```

Example values:

```dotenv
DB_URL=postgresql+psycopg://postgres:postgres@localhost:5432/app_db
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Notes:
- The app **requires** `DB_URL`. If it’s missing, startup fails.
- `SECRET_KEY` and `ALGORITHM` are used for JWT signing/verification.

---

## Running PostgreSQL (Docker)

Start Postgres:

```bash
docker compose up -d
```

Default database settings from `docker-compose.yml`:

- user: `postgres`
- password: `postgres`
- db: `app_db`
- port: `5432`

---

## Install & run (local)

This repo includes a `uv.lock`, so `uv` is a good fit:

```bash
uv sync
uv run fastapi dev main.py
```

Alternatively (pip/venv workflow):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
fastapi dev main.py
```

App will be available at:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

---

## Database migrations (Alembic)

This repo includes Alembic configuration (`alembic/`, `alembic.ini`). Typical commands:

```bash
alembic upgrade head
```

To create new migrations (example):

```bash
alembic revision -m "create tables"
```

> Make sure `DB_URL` points to the database you want to migrate.

---

## API overview

### Auth (`/auth`)

- `POST /auth/register`  
  Registers a new user.

- `POST /auth/login`  
  OAuth2 password flow (`application/x-www-form-urlencoded`) returning an access token.

### Users (`/users`)

- `GET /users` — list users (requires auth)
- `GET /users/{id}` — get user by id (requires auth)
- `PATCH /users/{id}` — update first/last name (requires auth)
- `PATCH /users/{id}/change-password` — change password
- `DELETE /users/{id}` — delete user (requires auth)

### Jobs (`/jobs`)

- `GET /jobs` — list jobs (requires auth)
- `POST /jobs` — create job (requires auth)
- `PUT /jobs/{id}` — update job (requires auth)
- `PATCH /jobs/{id}/complete` — mark job complete (requires auth)
- `DELETE /jobs/{id}` — delete job (requires auth)

Rate limit: set to `5/hour` on endpoints.

---

## Authentication

Protected endpoints are JWT-based. Typical usage:

1. Register: `POST /auth/register`
    - json body: `{"first_name": str, "last_name": str, "email": str, "password": str}`
2. Login: `POST /auth/login` to get an access token
    - form-data: `username` (email), `password`
3. Call protected endpoints with:

```http
Authorization: Bearer <access_token>
```

---

## Rate limiting

Rate limiting is implemented using `slowapi`:

- A global middleware is added in `main.py`
- Each endpoint is decorated with `@limiter.limit("5/hour")`
- A custom handler is registered for `RateLimitExceeded`

---

## Testing

Tests use `pytest` + FastAPI `TestClient`.

The test setup:
- Disables rate limiting (`limiter.enabled = False`)
- Overrides the DB dependency to use a local SQLite database (`sqlite:///./test.db`)
- Provides fixtures for auth headers and seeded data

Run tests:

```bash
pytest
```

---

## Linting / formatting (optional)

Configured tools include: `ruff`, `black`, `mypy`, and `pre-commit`.

Examples:

```bash
ruff check .
black .
mypy .
pre-commit run --all-files
```
