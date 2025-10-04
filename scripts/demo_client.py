#!/usr/bin/env python3
"""Demo client for LLMScope"""

import time
from llmscope import LLMTracker

# Initialize tracker
tracker = LLMTracker(
    api_key="demo-api-key",
    base_url="http://localhost:8000"
)

print("LLMScope Demo Client")
print("-" * 40)

# Simulate some LLM calls
events = [
    {
        "model": "gpt-4",
        "provider": "openai",
        "prompt_tokens": 150,
        "completion_tokens": 75,
        "latency_ms": 1250.5,
        "metadata": {"feature": "chatbot", "user": "demo_user"}
    },
    {
        "model": "claude-3-opus",
        "provider": "anthropic",
        "prompt_tokens": 200,
        "completion_tokens": 100,
        "latency_ms": 1500.0,
        "metadata": {"feature": "summarization", "user": "demo_user"}
    },
    {
        "model": "gpt-3.5-turbo",
        "provider": "openai",
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "latency_ms": 800.0,
        "metadata": {"feature": "completion", "user": "demo_user"}
    }
]

for i, event in enumerate(events, 1):
    print(f"\nSending event {i}/{len(events)}...")
    print(f"  Model: {event['model']}")
    print(f"  Tokens: {event['prompt_tokens']} + {event['completion_tokens']}")
    print(f"  Latency: {event['latency_ms']}ms")

    tracker.track_event(**event)
    time.sleep(1)

print("\n" + "-" * 40)
print("Demo complete! Check the dashboard at http://localhost:3000")
