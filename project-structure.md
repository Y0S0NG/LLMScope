llmscope/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Configuration management
│   │   ├── dependencies.py      # Dependency injection
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── events.py        # Event ingestion endpoints
│   │   │   ├── analytics.py     # Analytics query endpoints
│   │   │   ├── alerts.py        # Alert management
│   │   │   ├── websocket.py     # WebSocket handler
│   │   │   └── auth.py          # Authentication
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py      # API key validation
│   │   │   ├── rate_limit.py    # Rate limiting logic
│   │   │   ├── metrics.py       # Metrics calculation
│   │   │   └── detection.py     # PII/injection detection
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # Database connection
│   │   │   ├── models.py        # SQLAlchemy models
│   │   │   ├── queries.py       # Complex queries
│   │   │   └── migrations/      # Alembic migrations
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── event_service.py
│   │   │   ├── analytics_service.py
│   │   │   ├── alert_service.py
│   │   │   └── cache_service.py
│   │   │
│   │   └── workers/
│   │       ├── __init__.py
│   │       ├── event_processor.py  # Process event queue
│   │       ├── aggregator.py       # Update aggregates
│   │       └── alert_checker.py    # Check alert conditions
│   │
│   ├── tests/
│   │   ├── test_ingestion.py
│   │   ├── test_analytics.py
│   │   └── test_load.py           # Load testing
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── sdk/
│   ├── python/
│   │   ├── llmscope/
│   │   │   ├── __init__.py
│   │   │   ├── tracker.py         # Main SDK class
│   │   │   ├── openai_patch.py    # OpenAI integration
│   │   │   └── anthropic_patch.py # Anthropic integration
│   │   ├── setup.py
│   │   └── README.md
│   │
│   └── typescript/
│       ├── src/
│       └── package.json
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── MetricsChart.tsx
│   │   │   ├── LiveFeed.tsx
│   │   │   ├── CostBreakdown.tsx
│   │   │   └── AlertConfig.tsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   └── useAnalytics.ts
│   │   ├── api/
│   │   │   └── client.ts
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
│
├── infrastructure/
│   ├── terraform/           # IaC for AWS deployment
│   ├── kubernetes/          # K8s manifests
│   ├── nginx/              # Nginx config
│   └── monitoring/         # Prometheus/Grafana
│
├── docs/
│   ├── API.md             # API documentation
│   ├── SETUP.md           # Setup instructions
│   ├── ARCHITECTURE.md    # Architecture details
│   └── SDK_GUIDE.md       # SDK integration guide
│
├── scripts/
│   ├── init_db.sh         # Database initialization
│   ├── load_test.py       # Performance testing
│   └── demo_client.py     # Demo client
│
├── .github/
│   └── workflows/
│       ├── ci.yml         # CI pipeline
│       └── deploy.yml     # CD pipeline
│
├── .env.example
├── README.md
└── LICENSE