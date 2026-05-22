# Event Ledger

Two microservices that ingest financial transaction events, enforce idempotency, handle out-of-order delivery, and propagate trace IDs across service boundaries.

## Architecture

- **Gateway Service** (`:8080`) — public REST API for event ingestion and queries
- **Account Service** (`:8081`) — internal service for balances and transaction application

Each service runs as an independent process with its own SQLite database.

## Prerequisites

- Python 3.11+
- pip
- Docker Engine (optional, for Compose)

## Setup

```bash
cd event-ledger
python3 -m venv .venv
source .venv/bin/activate
pip install -e account-service/ -e gateway-service/ -e ".[dev]"
```

## Run with Docker Compose (preferred)

```bash
docker compose up --build
```

Or use the helper script:

```bash
./scripts/docker-up.sh
```

Swagger UI after startup:

- Gateway: http://localhost:8080/docs
- Account: http://localhost:8081/docs

Stop containers:

```bash
./scripts/docker-down.sh
```

View logs:

```bash
docker compose logs -f
```

## Run locally without Docker

```bash
# Terminal 1 — Account Service
cd account-service
uvicorn account_service.main:app --port 8081

# Terminal 2 — Gateway
cd gateway-service
ACCOUNT_SERVICE_URL=http://localhost:8081 uvicorn gateway_service.main:app --port 8080
```

## Run tests

```bash
pytest -v
```

Tests include per-service integration tests and cross-service e2e tests.

## Example requests

```bash
# Submit event
curl -X POST http://localhost:8080/events \
  -H "Content-Type: application/json" \
  -d '{"eventId":"evt-001","accountId":"acct-123","type":"CREDIT","amount":150.00,"currency":"USD","eventTimestamp":"2026-05-15T14:02:11Z"}'

# Duplicate (returns 200)
curl -X POST http://localhost:8080/events -H "Content-Type: application/json" -d '...'

# List events for account
curl "http://localhost:8080/events?account=acct-123"

# Get balance
curl http://localhost:8081/accounts/acct-123/balance

# Health
curl http://localhost:8080/health
curl http://localhost:8081/health

# Metrics
curl http://localhost:8080/metrics
```

## Design decisions

### Idempotency
Unique `eventId` at Gateway and Account layers. Duplicates return HTTP 200 with the original event.

### Out-of-order events
Event listings sorted by `eventTimestamp`. Balance is a commutative sum (CREDIT − DEBIT), so arrival order does not affect correctness.

### Resiliency
Gateway uses **timeout + retry with exponential backoff and jitter** (tenacity) when calling Account Service. After retries exhaust, `POST /events` returns **503**. `GET /events` continues to work from Gateway local storage.

### Observability
- JSON structured logs via structlog (`trace_id`, `service`, timestamp, level)
- `X-Trace-Id` propagated Gateway → Account
- `GET /health` with database connectivity check
- `GET /metrics` with request counters

## What is intentionally not included

- Kafka / message queues (REST only per spec)
- Kubernetes (Docker Compose for local run)
- OpenTelemetry/Jaeger (custom trace ID meets minimum requirement)
