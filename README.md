# URL Shortener

A FastAPI-based URL shortener service backed by PostgreSQL and Redis.

This project lets you:

- Create a short code for a long URL
- Redirect short codes back to the original URL
- Delete previously created short URLs
- Inspect simple cache metrics
- Run the app locally or with Docker Compose

## Quick Start

If you already have PostgreSQL and Redis running locally:

```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open:

- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
- Shorten endpoint: `http://localhost:8000/shorten`

## Overview

The application stores every shortened URL in PostgreSQL and uses Redis as a cache for redirect lookups. A short code is generated randomly and mapped to the original URL. When a user opens the short code, the app checks Redis first, then falls back to PostgreSQL if the value is not cached.

## Architecture

![URL Shortener architecture](assets/architecture.svg)

```mermaid
flowchart LR
    U[Client / Browser] --> N[Nginx]
    N --> A1[FastAPI instance 1]
    N --> A2[FastAPI instance 2]
    A1 --> R[(Redis cache)]
    A2 --> R
    A1 --> P[(PostgreSQL)]
    A2 --> P
```

### Request Flow

1. The client calls the API through Nginx or directly against FastAPI.
2. The router sends the request to the service layer.
3. The service layer generates a short code or resolves an existing one.
4. The repository layer reads or writes the `urls` table in PostgreSQL.
5. Redis stores recently used redirects to speed up repeated lookups.

### Code Structure

- `app/main.py` - FastAPI app entry point and health/metrics routes
- `app/routers/urls.py` - HTTP endpoints for shorten, redirect, and delete
- `app/services/url_service.py` - business logic, short code generation, cache handling
- `app/repositories/url_repository.py` - database access layer
- `app/models.py` - SQLAlchemy model for the URL table
- `app/schemas.py` - Pydantic request/response models
- `app/database.py` - database engine and session management
- `app/redis_client.py` - Redis client configuration
- `app/cache_metrics.py` - in-memory cache hit/miss counters
- `alembic/` - database migration files
- `tests/` - automated tests

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- Redis
- Alembic
- Uvicorn
- Pytest
- Nginx for containerized load balancing

## API Endpoints

### `GET /`

Returns a simple application message.

Example:

```bash
curl http://localhost:8000/
```

Response:

```json
{
  "message": "URL Shortener API"
}
```

### `GET /health`

Health check endpoint.

Example:

```bash
curl http://localhost:8000/health
```

Response:

```json
{
  "status": "ok"
}
```

### `GET /instance`

Returns the instance name from the `INSTANCE_NAME` environment variable.

This is most useful in Docker mode where multiple app instances run behind Nginx.

Example:

```bash
curl http://localhost:8000/instance
```

Response:

```json
{
  "instance": "api1"
}
```

### `GET /metrics/cache`

Returns in-memory cache statistics:

Example:

```bash
curl http://localhost:8000/metrics/cache
```

```json
{
  "hits": 10,
  "misses": 4,
  "hit_rate": 0.7142857142857143
}
```

### `POST /shorten`

Creates a short URL.

Example:

```bash
curl -X POST "http://localhost:8000/shorten" -H "Content-Type: application/json" -d '{"url":"https://github.com"}'
```

Request body:

```json
{
  "url": "https://github.com"
}
```

Response:

```json
{
  "short_code": "a1B2c3",
  "short_url": "http://localhost:8000/a1B2c3"
}
```

### `GET /{short_code}`

Redirects to the original URL with HTTP `302`.

Example:

```bash
curl -i "http://localhost:8000/a1B2c3"
```

Typical response:

```http
HTTP/1.1 302 Found
location: https://github.com/
```

### `DELETE /{short_code}`

Deletes the short URL and removes the cached value.

Example:

```bash
curl -X DELETE "http://localhost:8000/a1B2c3"
```

Response:

```json
{
  "message": "URL deleted"
}
```

## Project Structure

```text
app/
  main.py
  database.py
  redis_client.py
  cache_metrics.py
  models.py
  schemas.py
  routers/
  services/
  repositories/
alembic/
tests/
docker-compose.yml
Dockerfile
nginx/
```

## Prerequisites

For local development, install:

- Python 3.12 or later
- PostgreSQL
- Redis

If you use Docker, you only need:

- Docker
- Docker Compose

## Environment Variables

The app uses these variables:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `INSTANCE_NAME` - optional label returned by `GET /instance`

Example `.env`:

```env
DATABASE_URL="postgresql+psycopg2://urluser:urlpassword@localhost:5434/urlshortener"
REDIS_URL="redis://localhost:6379/0"
```

## Run Locally Step by Step

### 1. Clone the repository

```bash
git clone <repository-url>
cd url_shortner
```

### 2. Create and activate a virtual environment

```bash
python -m venv myenv
myenv\Scripts\activate
```

On macOS/Linux:

```bash
python3 -m venv myenv
source myenv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start PostgreSQL and Redis

Make sure PostgreSQL is running and reachable on port `5434`, and Redis is reachable on port `6379`.

This project expects the local database name `urlshortener`.

### 5. Configure environment variables

Create or update `.env` with:

```env
DATABASE_URL="postgresql+psycopg2://urluser:urlpassword@localhost:5434/urlshortener"
REDIS_URL="redis://localhost:6379/0"
```

### 6. Run database migrations

Apply the schema migration with Alembic:

```bash
alembic upgrade head
```

This creates the `urls` table used by the service.

### 7. Start the API server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Open the app

- API root: `http://localhost:8000/`
- Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## Run With Docker Step by Step

This is the easiest way to run the full stack.

### 1. Build and start the containers

```bash
docker compose up --build
```

### 2. What starts

- `postgres` - PostgreSQL database
- `redis` - Redis cache
- `api1` - first FastAPI container
- `api2` - second FastAPI container
- `nginx` - reverse proxy and load balancer

### 3. Access the app

Open:

```text
http://localhost:8000
```

Nginx listens on port `8000` and distributes requests between the two FastAPI containers.

### 4. Stop the stack

```bash
docker compose down
```

To remove the database volume as well:

```bash
docker compose down -v
```

## Example Usage

### Create a short URL

```bash
curl -X POST "http://localhost:8000/shorten" -H "Content-Type: application/json" -d '{"url":"https://github.com"}'
```

If you prefer PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/shorten" -ContentType "application/json" -Body '{"url":"https://github.com"}'
```

### Open the short URL

Visit the `short_url` returned by the API in your browser, or use:

```bash
curl -i "http://localhost:8000/a1B2c3"
```

### Delete a short URL

```bash
curl -X DELETE "http://localhost:8000/a1B2c3"
```

## Testing

Run the test suite with:

```bash
pytest
```

### Test database note

The tests use a separate PostgreSQL database named `urlshortener_test` on `localhost:5434`.

Before running tests, make sure that database exists and is empty.

Example SQL:

```sql
CREATE DATABASE urlshortener_test;
```

The test fixture creates and drops tables automatically.

## Database Migrations

The repository includes an initial Alembic migration that creates the `urls` table.

Useful commands:

```bash
alembic revision --autogenerate -m "message"
alembic upgrade head
alembic downgrade -1
```

## How It Works Internally

### Shortening

1. The client sends a long URL to `POST /shorten`.
2. The service generates a random 6-character short code.
3. The repository stores the mapping in PostgreSQL.
4. The API returns the short code and a short URL.

### Redirecting

1. The client requests `GET /{short_code}`.
2. The service checks Redis for a cached original URL.
3. If Redis misses, the service queries PostgreSQL.
4. The result is cached in Redis for future requests.
5. The API sends a `302` redirect to the original URL.

### Deleting

1. The client calls `DELETE /{short_code}`.
2. The service removes the database record.
3. The cached entry is removed from Redis.

## Troubleshooting

- If the app cannot connect to PostgreSQL, verify `DATABASE_URL`, the database name, and the port.
- If redirects are not being cached, verify Redis is running and reachable through `REDIS_URL`.
- If `pytest` fails immediately, check that the `urlshortener_test` database exists.
- If Docker Compose fails on startup, confirm ports `8000`, `5434`, and `6379` are free.

## Notes

- The short URL shown in responses is currently built using `http://localhost:8000`.
- Cache hit/miss counters are stored in memory, so they reset when the app process restarts.
