# LLMScope

> **High-performance observability platform for LLM applications**

LLMScope provides real-time monitoring, cost tracking, and analytics for your LLM API usage across OpenAI, Anthropic, and other providers.

## Features

- 🚀 **High Performance**: Handle millions of events per day with sub-second query performance
- 📊 **Real-time Analytics**: Live dashboards with WebSocket streaming
- 💰 **Cost Tracking**: Automatic cost calculation and breakdown by model/provider
- 🔔 **Smart Alerts**: Configurable alerts for cost, latency, and usage thresholds
- 🛡️ **Security**: PII detection and prompt injection monitoring
- 📦 **Easy Integration**: SDKs for Python and TypeScript with automatic tracking
- 🎯 **Provider Support**: OpenAI, Anthropic, and custom providers

## Quick Start (Self-Hosted Single-Tenant Mode)

### 1. Clone and setup

```bash
git clone https://github.com/yourusername/llmscope.git
cd llmscope
cp .env.example backend/.env
```

### 2. Start the platform with Docker

```bash
cd backend
docker-compose up -d
```

### 3. Run database migrations

```bash
# This will create tables and seed the default tenant
docker-compose exec api alembic upgrade head
```

You should see:
```
✅ Default tenant created: ID=default, API_KEY=llmscope-local-key
✅ Default project created: ID=main
```

### 4. Install SDK

**Python:**
```bash
pip install llmscope
```

**TypeScript:**
```bash
npm install @llmscope/sdk
```

### 5. Track your LLM calls

**Python:**
```python
from llmscope.openai_patch import patch_openai

# Use the default API key from .env (llmscope-local-key)
patch_openai(api_key="llmscope-local-key", base_url="http://localhost:8000")

# Use OpenAI normally - all calls are tracked!
import openai
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**TypeScript:**
```typescript
import { LLMTracker } from '@llmscope/sdk';

const tracker = new LLMTracker('llmscope-local-key', 'http://localhost:8000');

await tracker.trackEvent({
  model: 'gpt-4',
  provider: 'openai',
  promptTokens: 100,
  completionTokens: 50,
  latencyMs: 1200
});
```

### 6. View your dashboard

Open http://localhost:3000 to see real-time metrics, cost breakdown, and live event feed.

---

## Deployment Modes

### 🏠 Single-Tenant (Default - Self-Hosted)
Perfect for individual developers and teams. No tenant management needed - just deploy and use with a single static API key.

**Configuration:**
```bash
SINGLE_TENANT_MODE=true
REQUIRE_AUTH=true
API_KEY=llmscope-local-key
```

### 🏢 Multi-Tenant (Coming Soon)
For SaaS deployments with multiple organizations. Requires tenant signup, API key management, and usage isolation.

**To enable (future):**
```bash
SINGLE_TENANT_MODE=false
# Implement tenant signup/management
```

## Architecture

```
Client App → SDK → API Server → Database (PostgreSQL)
                        ↓
                    Redis Cache
                        ↓
                  Background Workers
```

## Documentation

- [Setup Guide](docs/SETUP.md)
- [API Documentation](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [SDK Integration Guide](docs/SDK_GUIDE.md)

## Components

### Backend (FastAPI)
- Event ingestion with high throughput
- Real-time WebSocket streaming
- Complex analytics queries
- Rate limiting and authentication

### Frontend (React + TypeScript)
- Real-time dashboard
- Cost breakdown visualizations
- Alert configuration
- Live event feed

### SDKs
- **Python**: Automatic tracking for OpenAI and Anthropic
- **TypeScript**: Integration with Node.js applications

### Infrastructure
- Kubernetes manifests
- Terraform for AWS deployment
- Prometheus + Grafana monitoring
- Nginx reverse proxy

## Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

### Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## Deployment

### Docker Compose (Development)
```bash
docker-compose up -d
```

### Kubernetes (Production)
```bash
kubectl apply -f infrastructure/kubernetes/
```

### AWS (Terraform)
```bash
cd infrastructure/terraform
terraform init
terraform apply
```

## Performance

- **Throughput**: 10,000+ events/second per API server
- **Query Latency**: <100ms for most analytics queries
- **Storage**: Efficient time-series partitioning for billions of events

## Security

- API key authentication with SHA-256 hashing
- Rate limiting per API key
- PII detection in prompts/responses
- Prompt injection detection
- Encryption at rest and in transit

## Roadmap

- [ ] Additional LLM provider integrations (Cohere, AI21, etc.)
- [ ] Advanced anomaly detection with ML
- [ ] Cost optimization recommendations
- [ ] Team collaboration features
- [ ] Custom dashboards and reports
- [ ] Webhook integrations

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details

## Support

- GitHub Issues: [Report bugs or request features](https://github.com/yourusername/llmscope/issues)
- Documentation: [Read the docs](docs/)
- Email: support@llmscope.dev

---

Built with ❤️ by the LLMScope team
