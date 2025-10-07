# Testing Guide for LLMScope SDK

This guide explains how to test the LLMScope Python SDK.

**⚠️ Important:** Currently only the **Events API** is fully implemented. Analytics, Alerts, and Auth endpoints return placeholder/TODO responses and are skipped in integration tests.

## Test Types

### 1. Unit Tests (Mocked)
Unit tests don't require a running API server. They use mocks to test SDK logic.

**Run unit tests:**
```bash
cd sdk/python
pip install -e ".[dev]"
pytest tests/test_events.py tests/test_analytics.py -v
```

### 2. Integration Tests (Live API)
Integration tests require a running LLMScope API server.

**Setup:**
```bash
# Set environment variables
export LLMSCOPE_API_KEY="your-api-key"
export LLMSCOPE_BASE_URL="http://localhost:8000"  # optional

# Install SDK with dev dependencies
pip install -e ".[dev]"
```

**Run integration tests:**
```bash
pytest tests/test_integration.py -v
```

### 3. Quick Manual Test
The fastest way to test if the SDK works:

```bash
cd sdk/python

# Option 1: Install the SDK first
pip install -e .
python examples/quick_test.py

# Option 2: Run directly
PYTHONPATH=. python examples/quick_test.py
```

## Running All Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all unit tests
pytest tests/test_*.py -v -k "not integration"

# Run all tests (including integration)
export LLMSCOPE_API_KEY="your-api-key"
pytest tests/ -v
```

## Test Coverage

```bash
# Install with coverage support
pip install -e ".[dev]"

# Run tests with coverage
pytest --cov=llmscope --cov-report=term-missing --cov-report=html tests/

# View HTML coverage report
open htmlcov/index.html
```

## Testing Against Local API

1. **Start your LLMScope API server:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Create an API key** (if needed):
   ```bash
   # Use your API or create via database
   ```

3. **Run quick test:**
   ```bash
   cd sdk/python
   export LLMSCOPE_API_KEY="your-key"
   python examples/quick_test.py
   ```

4. **Run full example:**
   ```bash
   python examples/basic_usage.py
   ```

## Manual Testing with Python REPL

```python
# Start Python REPL
python

# Import SDK
from llmscope import LLMScopeClient

# Initialize client
client = LLMScopeClient(
    api_key="your-api-key",
    base_url="http://localhost:8000"
)

# Test event ingestion
response = client.events.ingest({
    "model": "gpt-4",
    "provider": "openai",
    "tokens_prompt": 100,
    "tokens_completion": 50,
    "latency_ms": 1200
})
print(response)

# Test getting recent events
events = client.events.get_recent(limit=5)
print(events)

# Test analytics
from datetime import datetime, timedelta
metrics = client.analytics.get_metrics(
    start_time=datetime.utcnow() - timedelta(days=1),
    end_time=datetime.utcnow()
)
print(metrics)
```

## Common Issues

### API Connection Errors
```
requests.exceptions.ConnectionError: Failed to establish connection
```
**Solution:** Make sure your API server is running at the specified base_url.

### Authentication Errors
```
HTTPError: 401 Unauthorized
```
**Solution:** Check that your API key is valid and set correctly.

### Import Errors
```
ModuleNotFoundError: No module named 'llmscope'
```
**Solution:** Install the SDK first: `pip install -e .`

### Pydantic Validation Errors
```
ValidationError: X validation errors for EventRequest
```
**Solution:** Check that required fields (model, provider, tokens_prompt, tokens_completion, latency_ms) are provided.

## CI/CD Testing

For automated testing in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Install dependencies
  run: |
    pip install -e ".[dev]"

- name: Run unit tests
  run: |
    pytest tests/ -v -k "not integration"

- name: Run integration tests
  env:
    LLMSCOPE_API_KEY: ${{ secrets.LLMSCOPE_API_KEY }}
    LLMSCOPE_BASE_URL: ${{ secrets.LLMSCOPE_BASE_URL }}
  run: |
    pytest tests/test_integration.py -v
```

## Performance Testing

Test batch ingestion performance:

```python
import time
from llmscope import LLMScopeClient

client = LLMScopeClient(api_key="your-key")

# Generate 100 events
events = [
    {
        "model": "gpt-4",
        "provider": "openai",
        "tokens_prompt": 100,
        "tokens_completion": 50,
        "latency_ms": 1200
    }
    for _ in range(100)
]

# Time the batch ingestion
start = time.time()
response = client.events.ingest_batch(events)
elapsed = time.time() - start

print(f"Ingested {response.count} events in {elapsed:.2f}s")
print(f"Rate: {response.count/elapsed:.2f} events/sec")
```