# Quick Testing Guide

**⚠️ Only Events API is fully implemented. Analytics/Alerts/Auth return placeholder data.**

## Single-Tenant Mode (Default Configuration)

Your backend is configured in **single-tenant mode** with a static API key: `llmscope-local-key`

The test scripts are pre-configured with this key, so they work **out of the box**!

## Fastest Way to Test (Events API Only)

### 1. Quick Test Script (Recommended)
```bash
cd sdk/python

# Just run it - no API key setup needed!
python examples/quick_test.py
```

The script automatically uses `llmscope-local-key` which matches your backend config.

Expected output:
```
🧪 Testing LLMScope SDK (Events API)
✅ Client initialized
📤 Test 1: Ingest single event...
   ✅ Event ingested successfully!
   Event ID: evt_xxx
📤 Test 2: Batch ingest events...
   ✅ Batch ingested successfully!
   Count: 2 events
📥 Test 3: Get recent events...
   ✅ Retrieved recent events
📊 Test 4: Get processing stats...
   ✅ Stats retrieved successfully!
📊 Test 5: Get queue stats...
   ✅ Queue stats retrieved!
✅ All tests passed!
```

### 2. Full Events Example
```bash
python examples/events_only.py
```

### 3. Unit Tests (No API needed)
```bash
pip install -e ".[dev]"
pytest tests/test_events.py -v
```

### 4. Integration Tests (Requires running API)
```bash
# Make sure your API server is running first!
# No need to set API key - uses llmscope-local-key by default
pytest tests/test_integration.py::TestEventsIntegration -v

# Or set it explicitly:
# export LLMSCOPE_API_KEY="llmscope-local-key"
```

## What's Implemented

✅ **Events API** (Fully Working):
- `client.events.ingest()` - Ingest single event
- `client.events.ingest_batch()` - Batch ingest
- `client.events.get_recent()` - Get recent events
- `client.events.get_stats()` - Processing statistics
- `client.events.get_queue_stats()` - Queue stats

⚠️ **Not Yet Implemented** (Return placeholder data):
- Analytics API
- Alerts API
- Auth API

## Troubleshooting

**Connection Error:**
```
Failed to establish connection to http://localhost:8000
```
→ Make sure your API server is running

**401 Unauthorized:**
```
HTTPError: 401 Unauthorized
```
→ Make sure you're using the correct API key: `llmscope-local-key` (from backend/app/config.py)

**Import Error:**
```
ModuleNotFoundError: No module named 'llmscope'
```
→ Install SDK: `pip install -e .`

## Manual Testing

```python
from llmscope import LLMScopeClient

# For single-tenant mode, use the default API key
client = LLMScopeClient(api_key="llmscope-local-key")

# Test event ingestion
response = client.events.ingest({
    "model": "gpt-4",
    "provider": "openai",
    "tokens_prompt": 100,
    "tokens_completion": 50,
    "latency_ms": 1200
})

print(f"Event ID: {response.event_id}")
```

## Backend Configuration

Your backend is configured in `backend/app/config.py`:
- `single_tenant_mode: True`
- `require_auth: True`
- `api_key: "llmscope-local-key"`

To disable authentication (optional):
Set `require_auth: False` in config.py or create `.env` file:
```
require_auth=False
```

For full testing documentation, see [TESTING.md](TESTING.md)
