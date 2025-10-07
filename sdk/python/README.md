# LLMScope Python SDK

Python SDK for tracking LLM API calls with LLMScope.

## Installation

```bash
pip install llmscope
```

## Quick Start

### Auto-Tracking (Recommended)

The easiest way to track your LLM calls is with the auto-tracking features:

#### Method 1: Decorator

```python
from llmscope import LLMScope
import openai

# Initialize tracker
tracker = LLMScope(
    api_key="your-api-key",
    project="production"
)

# Decorate your functions - automatic tracking!
@tracker.trace()
def get_completion(prompt):
    return openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

# Use normally - metrics automatically sent to LLMScope
result = get_completion("What is Python?")
```

#### Method 2: Context Manager

```python
from llmscope import LLMScope
import openai

tracker = LLMScope(api_key="your-api-key", project="production")

# Track with context manager
with tracker.track() as span:
    span.set_metadata("user_id", "user123")
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    span.track_response(response)
```

#### Method 3: Monkey-Patching (Track ALL Calls)

```python
from llmscope import LLMScope
from llmscope.integrations import patch_openai
import openai

tracker = LLMScope(api_key="your-api-key")
patch_openai(tracker)  # ALL OpenAI calls now tracked automatically!

# Use OpenAI normally - everything is tracked
response = openai.chat.completions.create(...)
```

## Manual Event Tracking

For more control, use the full-featured client to manually track events:

### Using the Full-Featured Client

```python
from llmscope import LLMScopeClient

# Initialize client
client = LLMScopeClient(
    api_key="your-api-key",
    base_url="http://localhost:8000"  # Optional, defaults to localhost
)

# Ingest a single event
response = client.events.ingest({
    "model": "gpt-4",
    "provider": "openai",
    "tokens_prompt": 100,
    "tokens_completion": 50,
    "latency_ms": 1200
})
print(f"Event ID: {response.event_id}")

# Batch ingest events
events = [
    {
        "model": "gpt-4",
        "provider": "openai",
        "tokens_prompt": 100,
        "tokens_completion": 50,
        "latency_ms": 1200
    },
    {
        "model": "claude-3-opus",
        "provider": "anthropic",
        "tokens_prompt": 150,
        "tokens_completion": 75,
        "latency_ms": 1500
    }
]
batch_response = client.events.ingest_batch(events)
print(f"Ingested {batch_response.count} events")
```

### Using Type-Safe Models

```python
from llmscope import LLMScopeClient, EventRequest
from datetime import datetime

client = LLMScopeClient(api_key="your-api-key")

# Create event with type hints
event = EventRequest(
    model="gpt-4",
    provider="openai",
    tokens_prompt=100,
    tokens_completion=50,
    latency_ms=1200,
    user_id="user-123",
    session_id="session-456",
    temperature=0.7,
    metadata={"environment": "production"}
)

response = client.events.ingest(event)
```

## API Modules

### Events

```python
# Get recent events
recent = client.events.get_recent(limit=50)

# Get processing stats
stats = client.events.get_stats()
print(f"Total events: {stats['total_events']}")
print(f"Queue length: {stats['queue_length']}")

# Get queue stats
queue_stats = client.events.get_queue_stats()
```

### Analytics

```python
from datetime import datetime, timedelta

# Get metrics for the last 24 hours
end = datetime.utcnow()
start = end - timedelta(days=1)

metrics = client.analytics.get_metrics(
    start_time=start,
    end_time=end,
    model="gpt-4"  # Optional: filter by model
)
print(f"Total requests: {metrics['total_requests']}")
print(f"Avg latency: {metrics['avg_latency_ms']}ms")

# Get cost breakdown
costs = client.analytics.get_costs(start_time=start, end_time=end)
print(f"Total cost: ${costs['total_cost_usd']}")
```

### Alerts

```python
from llmscope import AlertRule

# Create alert rule
rule = AlertRule(
    name="High Latency Alert",
    condition="avg_latency_ms",
    threshold=2000.0,
    enabled=True
)
created_rule = client.alerts.create_rule(rule)

# List all alert rules
rules = client.alerts.list_rules()
for rule in rules:
    print(f"{rule['name']}: {rule['condition']} > {rule['threshold']}")
```

### Auth

```python
from llmscope import APIKeyCreate

# Create new API key
key = APIKeyCreate(
    name="Production Key",
    description="API key for production environment"
)
created_key = client.auth.create_api_key(key)
print(f"API Key: {created_key['key']}")
print("Save this - it won't be shown again!")

# List API keys (masked)
keys = client.auth.list_api_keys()
for key in keys:
    print(f"{key['name']}: {key['key_masked']}")
```

## Advanced Features

### Supported Providers

- **OpenAI** (GPT-4, GPT-3.5, etc.)
- **Anthropic** (Claude 3 models)
- More coming soon!

### Auto-Tracking Features

All tracking methods automatically capture:
- Model name and provider
- Token usage (prompt, completion, total)
- Request latency
- Response content (optional)
- Error tracking
- Custom metadata

### Async Support

All tracking methods work with async functions:

```python
@tracker.trace()
async def async_completion(prompt):
    client = openai.AsyncOpenAI()
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

### Provider Integration

Track multiple providers simultaneously:

```python
from llmscope.integrations import patch_openai, patch_anthropic

# Track both providers
patch_openai(tracker)
patch_anthropic(tracker)

# All calls to both providers are now tracked
import openai
import anthropic

openai_response = openai.chat.completions.create(...)  # Tracked
anthropic_response = anthropic_client.messages.create(...)  # Tracked
```

## Configuration

### LLMScope Tracker Options

```python
tracker = LLMScope(
    api_key="your-api-key",
    base_url="https://api.llmscope.dev",  # Custom API URL
    project="production",  # Auto-set project for all events
    debug=True  # Enable debug logging
)
```

### LLMScopeClient Options

```python
client = LLMScopeClient(
    api_key="your-api-key",
    base_url="https://api.llmscope.dev"
)
```

## Error Handling

### Auto-Tracking Errors

Auto-tracking is fail-safe - if tracking fails, your application continues:

```python
@tracker.trace()
def my_function():
    # Even if LLMScope tracking fails, this function will complete normally
    return openai.chat.completions.create(...)

# Errors are tracked too!
@tracker.trace()
def might_fail():
    raise ValueError("Oops!")  # This error is automatically tracked
```

### Manual Error Handling

```python
from requests.exceptions import HTTPError

try:
    response = client.events.ingest(event)
except HTTPError as e:
    print(f"API error: {e.response.status_code} - {e.response.text}")
```

## Examples

See the [examples/](examples/) directory for complete examples:

- [auto_tracking.py](examples/auto_tracking.py) - Using @trace decorator
- [context_manager.py](examples/context_manager.py) - Using context managers
- [monkey_patch.py](examples/monkey_patch.py) - Using monkey-patching
- [quick_test.py](examples/quick_test.py) - Manual event tracking

## When to Use Each Method

| Method | Use Case |
|--------|----------|
| **@trace decorator** | Best for tracking specific functions you control |
| **Context manager** | Best for fine-grained control with metadata |
| **Monkey-patching** | Best for tracking ALL calls in existing code without changes |
| **Manual events** | Best for custom tracking or non-standard LLM providers |

## License

MIT
