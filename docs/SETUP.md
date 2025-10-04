# LLMScope Setup Guide

## Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for SDK)
- Node.js 18+ (for frontend)

## Quick Start with Docker

1. Clone the repository:

```bash
git clone https://github.com/yourusername/llmscope.git
cd llmscope
```

2. Create environment file:

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start services:

```bash
cd backend
docker-compose up -d
```

4. Initialize database:

```bash
docker-compose exec api alembic upgrade head
```

5. Access the dashboard at `http://localhost:3000`

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
