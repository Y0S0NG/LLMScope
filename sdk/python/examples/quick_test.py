"""Quick test script for LLMScope SDK

A simple script to quickly verify the SDK is working.
Only tests the Events API (the only fully implemented feature).

Usage: python examples/quick_test.py

For single-tenant mode (default):
  Uses api_key="llmscope-local-key" (default from backend config)

Set environment variables to override:
  LLMSCOPE_API_KEY=your-api-key
  LLMSCOPE_BASE_URL=http://localhost:8000 (optional)
"""
import os
import sys
from llmscope import LLMScopeClient


def quick_test():
    """Quick smoke test for SDK - Events API only"""

    # Get API key from environment or use single-tenant default
    api_key = os.getenv("LLMSCOPE_API_KEY", "llmscope-local-key")
    base_url = os.getenv("LLMSCOPE_BASE_URL", "http://localhost:8000")

    print(f"🧪 Testing LLMScope SDK (Events API)")
    print(f"   API URL: {base_url}")
    print(f"   API Key: {api_key[:8]}..." if len(api_key) > 8 else f"   API Key: {api_key}")
    print()

    try:    
        # Initialize client
        client = LLMScopeClient(api_key=api_key, base_url=base_url)
        print("✅ Client initialized")

        # Test 1: Ingest a simple event
        print("\n📤 Test 1: Ingest single event...")
        event = {
            "model": "gpt-4",
            "provider": "openai",
            "tokens_prompt": 100,
            "tokens_completion": 50,
            "latency_ms": 1200
        }

        response = client.events.ingest(event)
        print(f"✅ Event ingested successfully!")
        print(f"   Event ID: {response.event_id}")
        print(f"   Status: {response.status}")

        # Test 2: Batch ingest events
        print("\n📤 Test 2: Batch ingest events...")
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
        print(f"✅ Batch ingested successfully!")
        print(f"   Count: {batch_response.count} events")
        print(f"   Event IDs: {', '.join(batch_response.event_ids)}")

        # Test 3: Get recent events
        print("\n📥 Test 3: Get recent events...")
        recent = client.events.get_recent(limit=5)
        print(f"✅ Retrieved recent events")
        print(f"   Count: {recent.get('count', len(recent))} events")

        # Test 4: Get processing stats
        print("\n📊 Test 4: Get processing stats...")
        stats = client.events.get_stats()
        print(f"✅ Stats retrieved successfully!")
        print(f"   Total events stored: {stats.get('total_events_stored', 'N/A')}")
        print(f"   Queue length: {stats.get('queue_length', 'N/A')}")

        # Test 5: Get queue stats
        print("\n📊 Test 5: Get queue stats...")
        queue_stats = client.events.get_queue_stats()
        print(f"✅ Queue stats retrieved!")
        print(f"   Queue: {queue_stats.get('queue_name', 'N/A')}")
        print(f"   Pending: {queue_stats.get('queue_length', 'N/A')}")

        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("=" * 50)
        print("\nNote: Analytics, Alerts, and Auth APIs are not yet")
        print("implemented and will return placeholder responses.")
        return 0

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(quick_test())