# LLMScope SDK Integration Guide

## Installation

### Python

```bash
pip install llmscope
```

### TypeScript/JavaScript

```bash
npm install @llmscope/sdk
```

## Python SDK

### Basic Usage

```python
from llmscope import LLMTracker

tracker = LLMTracker(api_key="your-api-key")

# Track an event
tracker.track_event(
    model="gpt-4",
    provider="openai",
    prompt_tokens=100,
    completion_tokens=50,
    latency_ms=1200.5,
    metadata={"user_id": "123", "environment": "production"}
)
```

### OpenAI Integration

```python
from llmscope.openai_patch import patch_openai

# Automatically track all OpenAI calls
patch_openai(api_key="your-llmscope-api-key")

# Use OpenAI normally
import openai
openai.api_key = "your-openai-api-key"

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
# Event automatically tracked!
```

### Anthropic Integration

```python
from llmscope.anthropic_patch import patch_anthropic

# Automatically track all Anthropic calls
patch_anthropic(api_key="your-llmscope-api-key")

# Use Anthropic normally
import anthropic
client = anthropic.Anthropic(api_key="your-anthropic-api-key")

message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)
# Event automatically tracked!
```

### Custom Metadata

```python
tracker.track_event(
    model="gpt-4",
    provider="openai",
    prompt_tokens=100,
    completion_tokens=50,
    latency_ms=1200.5,
    metadata={
        "user_id": "user_123",
        "session_id": "sess_456",
        "environment": "production",
        "feature": "chatbot",
        "version": "1.0.0"
    }
)
```

## TypeScript SDK

### Basic Usage

```typescript
import { LLMTracker } from '@llmscope/sdk';

const tracker = new LLMTracker('your-api-key');

await tracker.trackEvent({
  model: 'gpt-4',
  provider: 'openai',
  promptTokens: 100,
  completionTokens: 50,
  latencyMs: 1200.5,
  metadata: {
    userId: '123',
    environment: 'production'
  }
});
```

### Express Middleware

```typescript
import express from 'express';
import { LLMTracker } from '@llmscope/sdk';

const app = express();
const tracker = new LLMTracker('your-api-key');

app.use(async (req, res, next) => {
  // Track LLM usage in your routes
  res.locals.tracker = tracker;
  next();
});

app.post('/chat', async (req, res) => {
  const start = Date.now();

  // Make LLM call
  const response = await openai.chat.completions.create({
    model: 'gpt-4',
    messages: req.body.messages
  });

  // Track event
  await res.locals.tracker.trackEvent({
    model: 'gpt-4',
    provider: 'openai',
    promptTokens: response.usage.prompt_tokens,
    completionTokens: response.usage.completion_tokens,
    latencyMs: Date.now() - start
  });

  res.json(response);
});
```

## Best Practices

### 1. Error Handling

The SDK is designed to never fail your application. Tracking errors are logged but don't throw exceptions.

### 2. Batching (Coming Soon)

For high-volume applications, batch events:

```python
tracker.enable_batching(max_batch_size=100, flush_interval=5)
```

### 3. Custom Cost Tracking

Override default cost calculation:

```python
tracker.track_event(
    model="custom-model",
    provider="custom",
    prompt_tokens=100,
    completion_tokens=50,
    latency_ms=1200.5,
    cost=0.025  # Custom cost
)
```

### 4. Metadata Standards

Recommended metadata fields:

- `user_id`: User identifier
- `session_id`: Session identifier
- `environment`: prod, staging, dev
- `feature`: Feature/component name
- `version`: Application version

## Troubleshooting

### Events Not Appearing

1. Check API key is correct
2. Verify LLMScope API is reachable
3. Check application logs for errors

### High Latency

The SDK sends events asynchronously and shouldn't impact performance. If you notice issues:

1. Check network connectivity
2. Verify LLMScope API response times
3. Consider implementing batching

## Advanced Features

### Custom Event Enrichment

```python
class CustomTracker(LLMTracker):
    def track_event(self, **kwargs):
        # Add custom fields
        kwargs['metadata']['app_version'] = '1.0.0'
        kwargs['metadata']['region'] = 'us-west-2'
        super().track_event(**kwargs)
```

### Sampling

Track only a percentage of events:

```python
import random

if random.random() < 0.1:  # 10% sampling
    tracker.track_event(...)
```
