# LLMScope Python SDK

Python SDK for tracking LLM API calls with LLMScope.

## Installation

```bash
pip install llmscope
```

## Quick Start

### Manual Tracking

```python
from llmscope import LLMTracker

tracker = LLMTracker(api_key="your-api-key")

tracker.track_event(
    model="gpt-4",
    provider="openai",
    prompt_tokens=100,
    completion_tokens=50,
    latency_ms=1200.5
)
```

### Automatic OpenAI Tracking

```python
from llmscope.openai_patch import patch_openai

# Patch OpenAI to automatically track all calls
patch_openai(api_key="your-llmscope-api-key")

# Now use OpenAI normally - all calls are tracked automatically
import openai
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Automatic Anthropic Tracking

```python
from llmscope.anthropic_patch import patch_anthropic

# Patch Anthropic to automatically track all calls
patch_anthropic(api_key="your-llmscope-api-key")

# Now use Anthropic normally - all calls are tracked automatically
import anthropic
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-opus-20240229",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Configuration

Set the LLMScope API URL:

```python
tracker = LLMTracker(
    api_key="your-api-key",
    base_url="https://api.llmscope.dev"
)
```
