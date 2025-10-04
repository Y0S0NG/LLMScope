# LLMScope API Documentation

## Authentication

All API requests require an API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" https://api.llmscope.dev/events/ingest
```

## Endpoints

### Event Ingestion

#### POST /events/ingest

Ingest a new LLM event.

**Request Body:**

```json
{
  "timestamp": "2025-10-04T12:00:00Z",
  "model": "gpt-4",
  "provider": "openai",
  "prompt_tokens": 100,
  "completion_tokens": 50,
  "total_tokens": 150,
  "latency_ms": 1200.5,
  "metadata": {}
}
```

**Response:**

```json
{
  "status": "accepted",
  "event_id": "evt_123456"
}
```

### Analytics

#### GET /analytics/metrics

Get aggregated metrics.

**Query Parameters:**
- `start_time` (optional): ISO 8601 timestamp
- `end_time` (optional): ISO 8601 timestamp
- `model` (optional): Filter by model name

**Response:**

```json
{
  "total_requests": 1000,
  "total_tokens": 150000,
  "total_cost": 45.50,
  "avg_latency_ms": 1250.0
}
```

#### GET /analytics/costs

Get cost breakdown by model and provider.

**Query Parameters:**
- `start_time` (optional): ISO 8601 timestamp
- `end_time` (optional): ISO 8601 timestamp

**Response:**

```json
{
  "breakdown": [
    {
      "model": "gpt-4",
      "provider": "openai",
      "requests": 500,
      "total_cost": 30.00
    }
  ]
}
```

### Alerts

#### GET /alerts/rules

List all alert rules.

**Response:**

```json
{
  "rules": [
    {
      "id": "rule_123",
      "name": "High cost alert",
      "condition": "cost_per_hour",
      "threshold": 10.0,
      "enabled": true
    }
  ]
}
```

#### POST /alerts/rules

Create a new alert rule.

**Request Body:**

```json
{
  "name": "High latency alert",
  "condition": "avg_latency",
  "threshold": 2000,
  "enabled": true
}
```

### WebSocket

#### WS /ws

Connect to real-time event stream.

Events are streamed as JSON objects:

```json
{
  "id": "evt_123",
  "timestamp": "2025-10-04T12:00:00Z",
  "model": "gpt-4",
  "total_tokens": 150,
  "latency_ms": 1200,
  "cost": 0.045
}
```
