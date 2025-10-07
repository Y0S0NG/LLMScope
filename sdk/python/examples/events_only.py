"""Events-only usage example for LLMScope SDK

This example demonstrates the Events API - the only fully implemented feature.
Analytics, Alerts, and Auth endpoints return placeholder responses.

Usage: python examples/events_only.py

For single-tenant mode (default):
  Uses api_key="llmscope-local-key" (default from backend config)
"""
from llmscope import LLMScopeClient, EventRequest
import os


def main():
    """Demonstrate Events API usage"""

    # Initialize client - uses single-tenant default API key
    api_key = os.getenv("LLMSCOPE_API_KEY", "llmscope-local-key")
    base_url = os.getenv("LLMSCOPE_BASE_URL", "http://localhost:8000")

    client = LLMScopeClient(api_key=api_key, base_url=base_url)

    print("=" * 60)
    print("LLMScope SDK - Events API Examples")
    print("=" * 60)

    # 1. Ingest a single event with minimal data
    print("\n1. Ingest event (minimal)...")
    event = {
        "model": "gpt-4",
        "provider": "openai",
        "tokens_prompt": 100,
        "tokens_completion": 50,
        "latency_ms": 1200
    }

    response = client.events.ingest(event)
    print(f"   ✅ Event ID: {response.event_id}")
    print(f"   Status: {response.status}")

    # 2. Ingest event with full metadata using EventRequest model
    print("\n2. Ingest event (full metadata)...")
    event_full = EventRequest(
        model="gpt-4",
        provider="openai",
        tokens_prompt=200,
        tokens_completion=100,
        latency_ms=1500,
        time_to_first_token_ms=300,
        user_id="user-123",
        session_id="session-abc",
        temperature=0.7,
        max_tokens=1000,
        cost_usd=0.015,
        messages=[
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "The capital of France is Paris."}
        ],
        response="The capital of France is Paris.",
        metadata={
            "environment": "production",
            "feature": "chat",
            "user_tier": "premium"
        }
    )

    response = client.events.ingest(event_full)
    print(f"   ✅ Event ID: {response.event_id}")

    # 3. Batch ingest multiple events
    print("\n3. Batch ingest events...")
    events = [
        {
            "model": "gpt-4",
            "provider": "openai",
            "tokens_prompt": 150,
            "tokens_completion": 75,
            "latency_ms": 1300,
            "cost_usd": 0.012
        },
        {
            "model": "claude-3-opus",
            "provider": "anthropic",
            "tokens_prompt": 120,
            "tokens_completion": 60,
            "latency_ms": 1100,
            "cost_usd": 0.010
        },
        {
            "model": "gpt-3.5-turbo",
            "provider": "openai",
            "tokens_prompt": 80,
            "tokens_completion": 40,
            "latency_ms": 800,
            "cost_usd": 0.002
        }
    ]

    batch_response = client.events.ingest_batch(events)
    print(f"   ✅ Ingested {batch_response.count} events")
    print(f"   Event IDs: {', '.join(batch_response.event_ids)}")

    # 4. Get recent events
    print("\n4. Retrieve recent events...")
    recent = client.events.get_recent(limit=10)
    events_count = recent.get('count', len(recent.get('events', [])))
    print(f"   ✅ Retrieved {events_count} recent events")

    if recent.get('events'):
        latest = recent['events'][0]
        print(f"   Latest event: {latest.get('model', 'N/A')} - {latest.get('latency_ms', 'N/A')}ms")

    # 5. Get processing statistics
    print("\n5. Get processing statistics...")
    stats = client.events.get_stats()
    print(f"   ✅ Processing stats:")
    print(f"      Total events stored: {stats.get('total_events_stored', 'N/A')}")
    print(f"      Queue length: {stats.get('queue_length', 'N/A')}")
    print(f"      Dead letter queue: {stats.get('dlq_length', 'N/A')}")
    print(f"      Processing lag: {stats.get('processing_lag', 'N/A')}")

    # 6. Get queue statistics
    print("\n6. Get queue statistics...")
    queue_stats = client.events.get_queue_stats()
    print(f"   ✅ Queue stats:")
    print(f"      Queue name: {queue_stats.get('queue_name', 'N/A')}")
    print(f"      Queue length: {queue_stats.get('queue_length', 'N/A')}")
    print(f"      DLQ name: {queue_stats.get('dlq_name', 'N/A')}")
    print(f"      DLQ length: {queue_stats.get('dlq_length', 'N/A')}")

    # 7. Example: Track an error event
    print("\n7. Ingest error event...")
    error_event = EventRequest(
        model="gpt-4",
        provider="openai",
        tokens_prompt=50,
        tokens_completion=0,
        latency_ms=200,
        status="error",
        has_error=True,
        error_message="Rate limit exceeded",
        metadata={"error_code": "rate_limit"}
    )

    response = client.events.ingest(error_event)
    print(f"   ✅ Error event tracked: {response.event_id}")

    print("\n" + "=" * 60)
    print("✅ Examples completed!")
    print("=" * 60)
    print("\nℹ️  Note: Only Events API is fully implemented.")
    print("   Analytics, Alerts, and Auth return placeholder data.")


if __name__ == "__main__":
    main()
