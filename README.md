# URL Shortener API

A FastAPI-based URL shortener service backed by PostgreSQL and Redis.

This project lets you:

- Create a short code for a long URL
- Redirect short codes back to the original URL
- Delete previously created short URLs
- Inspect simple cache metrics
- Run the application locally on your machine
- Run the complete stack with Docker Compose
- Run automated tests and generate coverage reports

## Overview

The application stores shortened URLs in PostgreSQL and uses Redis as a cache for redirect lookups. When a short code is requested, the service checks Redis first and falls back to PostgreSQL if the value is not already cached.

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

1. The client sends a request to the API.
2. In Docker mode, Nginx receives the request first.
3. Nginx distributes requests between the FastAPI instances.
4. The FastAPI router receives the request.
5. The service layer handles the business logic.
6. PostgreSQL stores the URL mappings.
7. Redis caches frequently accessed redirect mappings.
8. Redirect requests check Redis first and PostgreSQL second.

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL 16
- Redis 7
- Alembic
- Uvicorn
- Pytest
- pytest-cov
- Nginx
- Docker
- Docker Compose
- GitHub Actions

## Project Structure

```text
url_shortener_api/
|-- app/
|   |-- main.py
|   |-- database.py
|   |-- redis_client.py
|   |-- cache_metrics.py
|   |-- models.py
|   |-- schemas.py
|   |-- routers/
|   |   `-- urls.py
|   |-- services/
|   |   `-- url_service.py
|   `-- repositories/
|       `-- url_repository.py
|-- alembic/
|-- tests/
|-- nginx/
|-- assets/
|-- .github/workflows/ci.yml
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
|-- requirements-dev.txt
|-- pytest.ini
`-- README.md
```

## Prerequisites

### Local Development

Install:

- Python 3.12 or later
- PostgreSQL 16 or later
- Redis 7 or later

### Docker Development

Install:

- Docker Desktop
- Docker Compose

Docker Compose will run:

- PostgreSQL
- Redis
- Two FastAPI application containers
- Nginx reverse proxy

## Environment Variables

The application uses these environment variables:

- `DATABASE_URL`
- `REDIS_URL`
- `INSTANCE_NAME`
- `TEST_DATABASE_URL`

### Local Example

Create a `.env` file with:

```env
DATABASE_URL="postgresql+psycopg2://urluser:urlpassword@localhost:5434/urlshortener"
REDIS_URL="redis://localhost:6379/0"
INSTANCE_NAME="local"
```

### Docker Example

Inside Docker, the services talk to each other by service name, not by `localhost`:

```env
DATABASE_URL="postgresql+psycopg2://urluser:urlpassword@postgres:5432/urlshortener"
REDIS_URL="redis://redis:6379/0"
INSTANCE_NAME="api1"
```

### Important Port Notes

- Local PostgreSQL: `localhost:5434`
- Docker PostgreSQL service: `postgres:5432`
- Local Redis: `localhost:6379`
- Docker Redis service: `redis:6379`
- Docker Nginx entry point: `http://localhost:8000`

## Run Locally

This mode runs FastAPI directly on your machine while PostgreSQL and Redis run separately. You can use either locally installed services or services started through Docker.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd url_shortener_api
```

### 2. Create a Virtual Environment

#### Windows PowerShell

```powershell
python -m venv myenv
myenv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv myenv
source myenv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

For development and testing:

```bash
pip install -r requirements-dev.txt
```

### 4. Start PostgreSQL and Redis

Make sure these services are reachable before starting the API:

- PostgreSQL on `localhost:5434`
- Redis on `localhost:6379`

The default local database name is `urlshortener`.

### 5. Configure Environment Variables

Create or update `.env`:

```env
DATABASE_URL="postgresql+psycopg2://urluser:urlpassword@localhost:5434/urlshortener"
REDIS_URL="redis://localhost:6379/0"
INSTANCE_NAME="local"
```

### 6. Run Database Migrations

Apply the schema migration:

```bash
alembic upgrade head
```

This creates the tables required by the application, including `urls`.

### 7. Start the API Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Open the Application

- API root: `http://localhost:8000/`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

If you are running the API on the same device, `localhost` will open it directly in your browser.

## Run With Docker Compose

This is the easiest way to run the full stack.

### 1. Build and Start the Containers

```bash
docker compose up -d --build
```

### 2. Check the Running Services

```bash
docker compose ps
```

Expected services:

- `postgres`
- `redis`
- `api1`
- `api2`
- `nginx`

### 3. Run Database Migrations

After the containers are up, apply the schema migration:

```bash
docker compose run --rm api1 alembic upgrade head
```

You can also verify the migration state with:

```bash
docker compose run --rm api1 alembic current
```

### 4. Open the Application

Open:

```text
http://localhost:8000
```

Nginx listens on port `8000` and distributes requests between the two FastAPI containers.

Useful endpoints:

- `http://localhost:8000/docs`
- `http://localhost:8000/health`

### 5. Stop the Stack

```bash
docker compose down
```

To remove the database volume as well:

```bash
docker compose down -v
```

## Database Migrations

This project uses Alembic to manage schema changes.

Common commands:

```bash
alembic current
alembic heads
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "describe your change"
```

Important note:

- Starting FastAPI with `uvicorn` does not automatically create database tables.
- For a fresh database, always run `alembic upgrade head` first.

## Testing

Run the test suite with:

```bash
pytest
```

For verbose output:

```bash
pytest -v
```

Run a specific test file:

```bash
pytest tests/test_urls.py
```

### Test Database

Tests use a separate PostgreSQL database:

- `urlshortener_test`

The default local test connection string is:

```text
postgresql+psycopg2://urluser:urlpassword@localhost:5434/urlshortener_test
```

If needed, set it explicitly before running tests:

```powershell
$env:TEST_DATABASE_URL="postgresql+psycopg2://urluser:urlpassword@localhost:5434/urlshortener_test"
pytest
```

The test fixture creates and drops tables automatically for each test run.

### Test Coverage

Generate an HTML coverage report with:

```bash
pytest --cov=app --cov-report=term-missing --cov-report=html
```

The report is written to:

```text
htmlcov/index.html
```

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

Returns cache statistics.

Example:

```bash
curl http://localhost:8000/metrics/cache
```

Response:

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

## Example Usage

### Create a Short URL

Windows PowerShell:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/shorten" `
  -ContentType "application/json" `
  -Body '{"url":"https://github.com"}'
```

Linux / macOS:

```bash
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://github.com"}'
```

### Open the Short URL

If the API returns:

```json
{
  "short_code": "a1B2c3",
  "short_url": "http://localhost:8000/a1B2c3"
}
```

Open that URL in your browser or use:

```bash
curl -i "http://localhost:8000/a1B2c3"
```

### Delete the Short URL

```bash
curl -X DELETE "http://localhost:8000/a1B2c3"
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

### PostgreSQL Connection Failed

If the app cannot connect to PostgreSQL, verify:

- `DATABASE_URL`
- The database name
- The port
- That PostgreSQL is running

Local PostgreSQL should use `localhost:5434`.
Docker containers should use `postgres:5432`.

### Redis Connection Failed

If redirects are not being cached, verify:

- `REDIS_URL`
- That Redis is running
- That Redis is reachable on the expected port

Local Redis should use `localhost:6379`.
Docker containers should use `redis:6379`.

### `relation "urls" does not exist`

This means the database is reachable, but migrations have not been applied yet.

Run:

```bash
alembic upgrade head
```

Or, in Docker:

```bash
docker compose run --rm api1 alembic upgrade head
```

### Tests Cannot Connect to PostgreSQL

Make sure the test database exists:

- `urlshortener_test`

If needed, create it manually:

```sql
CREATE DATABASE urlshortener_test;
```

### The App Does Not Open in the Browser

If `http://localhost:8000` does not load:

- Check that the API server is running locally
- Check `docker compose ps` if using Docker
- Check Nginx logs with `docker compose logs nginx`

### Docker Containers Are Running but Tables Are Missing

Running the containers does not automatically apply migrations.

Apply them explicitly:

```bash
docker compose run --rm api1 alembic upgrade head
```

## Notes

- The short URL returned by the API is currently built using `http://localhost:8000`.
- Cache hit and miss counters are stored in memory, so they reset when the application restarts.
- PostgreSQL data persists in the Docker volume unless the volume is removed with `docker compose down -v`.
- The `.env` file should not be committed to Git.
