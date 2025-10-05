# LLMScope Setup Guide

## Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for SDK)
- Node.js 18+ (for frontend)

## Quick Start with Docker (Single-Tenant Mode)

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/llmscope.git
cd llmscope
```

### 2. Create environment file

```bash
cp .env.example backend/.env
```

**Default configuration (.env):**
```bash
# Single-Tenant Mode
SINGLE_TENANT_MODE=true
REQUIRE_AUTH=true
API_KEY=llmscope-local-key

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/llmscope

# Default IDs
DEFAULT_TENANT_ID=default
DEFAULT_PROJECT_ID=main
```

### 3. Start services

```bash
cd backend
docker-compose up -d
```

This starts:
- **PostgreSQL** with TimescaleDB (port 5433)
- **Redis** (port 6379)
- **API Server** (port 8000)

### 4. Initialize database

```bash
# Run migrations to create tables and seed default tenant
docker-compose exec api alembic upgrade head
```

You should see output like:
```
INFO  [alembic.runtime.migration] Running upgrade  -> ebb440b41de1, Initial schema
INFO  [alembic.runtime.migration] Running upgrade ebb440b41de1 -> 67aa717b7457, Add TimescaleDB hypertable
INFO  [alembic.runtime.migration] Running upgrade 67aa717b7457 -> 003_seed_default, Seed default tenant
✅ Default tenant created with API key: llmscope-local-key
```

### 5. Verify installation

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","mode":"single-tenant"}
```

### 6. Access the dashboard

Open http://localhost:3000 to see the LLMScope dashboard

---

## Single-Tenant Mode Details

In single-tenant mode:
- ✅ No tenant signup or management needed
- ✅ One static API key for all requests
- ✅ All events automatically associated with default tenant/project
- ✅ Perfect for self-hosted deployment
- ✅ Database schema ready for multi-tenant upgrade later

**API Key:** `llmscope-local-key` (change in `.env` if needed)

**Usage Example:**
```python
from llmscope import LLMTracker

tracker = LLMTracker(api_key="llmscope-local-key", base_url="http://localhost:8000")
```

## Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

### SDK Installation

#### Python

```bash
pip install llmscope
```

#### TypeScript/JavaScript

```bash
npm install @llmscope/sdk
```

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: Secret key for API key hashing
- `API_KEY_HEADER`: Header name for API key (default: X-API-Key)

### Database

LLMScope uses PostgreSQL for data storage. The schema is managed with Alembic migrations.

### Redis

Redis is used for caching and rate limiting.

## Running Tests

```bash
cd backend
pytest
```

## Production Deployment

See [ARCHITECTURE.md](ARCHITECTURE.md) for deployment architecture details.

### Kubernetes

```bash
kubectl apply -f infrastructure/kubernetes/
```

### Terraform (AWS)

```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```
