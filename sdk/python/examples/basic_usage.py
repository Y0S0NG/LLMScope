"""Basic usage example for LLMScope SDK"""
from llmscope import LLMScopeClient, EventRequest
from datetime import datetime, timedelta


def main():
    """Demonstrate basic SDK usage"""

    # Initialize client
    # For production, use environment variable: os.getenv("LLMSCOPE_API_KEY")
    client = LLMScopeClient(
        api_key="your-api-key-here",
        base_url="http://localhost:8000"
    )

    print("=" * 60)
    print("LLMScope SDK Basic Usage Example")
    print("=" * 60)

    # 1. Ingest a single event
    print("\n1. Ingesting single event...")
    event = EventRequest(
        model="gpt-4",
        provider="openai",
        tokens_prompt=100,
        tokens_completion=50,
        latency_ms=1200,
        user_id="user-123",
        session_id="session-456",
        temperature=0.7,
        metadata={"environment": "development", "feature": "chat"}
    )

    response = client.events.ingest(event)
    print(f"   ✅ Event ID: {response.event_id}")
    print(f"   Status: {response.status}")

    # 2. Batch ingest multiple events
    print("\n2. Batch ingesting events...")
    events = [
        {
            "model": "gpt-4",
            "provider": "openai",
            "tokens_prompt": 200,
            "tokens_completion": 100,
            "latency_ms": 1500,
            "cost_usd": 0.015
        },
        {
            "model": "claude-3-opus",
            "provider": "anthropic",
            "tokens_prompt": 150,
            "tokens_completion": 75,
            "latency_ms": 1300,
            "cost_usd": 0.012
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
    print(f"   Event IDs: {', '.join(batch_response.event_ids[:3])}...")

    # 3. Get recent events
    print("\n3. Retrieving recent events...")
    recent_events = client.events.get_recent(limit=5)
    print(f"   ✅ Retrieved {len(recent_events)} recent events")
    if recent_events:
        print(f"   Latest: {recent_events[0].get('model', 'N/A')}")

    # 4. Get processing stats
    print("\n4. Getting processing statistics...")
    stats = client.events.get_stats()
    print(f"   ✅ Stats: {stats}")

    # 5. Get analytics metrics
    print("\n5. Getting analytics metrics...")
    end = datetime.utcnow()
    start = end - timedelta(days=1)

    metrics = client.analytics.get_metrics(
        start_time=start,
        end_time=end,
        model="gpt-4"
    )
    print(f"   ✅ Metrics for last 24h: {metrics}")

    # 6. Get cost breakdown
    print("\n6. Getting cost breakdown...")
    costs = client.analytics.get_costs(
        start_time=start,
        end_time=end
    )
    print(f"   ✅ Cost data: {costs}")

    # 7. List alert rules
    print("\n7. Listing alert rules...")
    rules = client.alerts.list_rules()
    print(f"   ✅ Found {len(rules)} alert rules")
    for rule in rules[:3]:
        print(f"      - {rule.get('name', 'N/A')}: {rule.get('condition', 'N/A')} > {rule.get('threshold', 'N/A')}")

    # 8. Create an alert rule
    print("\n8. Creating alert rule...")
    from llmscope import AlertRule

    new_rule = AlertRule(
        name="High Latency Warning",
        condition="avg_latency_ms",
        threshold=2000.0,
        enabled=True
    )

    try:
        created_rule = client.alerts.create_rule(new_rule)
        print(f"   ✅ Created rule: {created_rule.get('name', 'N/A')}")
    except Exception as e:
        print(f"   ⚠️  Error creating rule: {e}")

    # 9. List API keys
    print("\n9. Listing API keys...")
    keys = client.auth.list_api_keys()
    print(f"   ✅ Found {len(keys)} API keys")
    for key in keys[:3]:
        print(f"      - {key.get('name', 'N/A')}: {key.get('key_masked', 'N/A')}")

    print("\n" + "=" * 60)
    print("✅ Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()