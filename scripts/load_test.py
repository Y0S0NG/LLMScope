#!/usr/bin/env python3
"""Load testing script for LLMScope"""

import asyncio
import aiohttp
import time
import random
from datetime import datetime
from typing import List

API_URL = "http://localhost:8000"
API_KEY = "test-api-key"
NUM_REQUESTS = 10000
CONCURRENT_REQUESTS = 100

MODELS = ["gpt-4", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet"]
PROVIDERS = ["openai", "anthropic"]


async def send_event(session: aiohttp.ClientSession, event_id: int):
    """Send a single event"""
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "model": random.choice(MODELS),
        "provider": random.choice(PROVIDERS),
        "prompt_tokens": random.randint(50, 500),
        "completion_tokens": random.randint(50, 500),
        "total_tokens": 0,  # Will be calculated
        "latency_ms": random.uniform(500, 3000),
        "metadata": {"test_id": event_id}
    }
    event["total_tokens"] = event["prompt_tokens"] + event["completion_tokens"]

    headers = {"X-API-Key": API_KEY}

    try:
        async with session.post(
            f"{API_URL}/events/ingest",
            json=event,
            headers=headers
        ) as response:
            return response.status == 200
    except Exception as e:
        print(f"Error sending event {event_id}: {e}")
        return False


async def run_load_test():
    """Run load test"""
    print(f"Starting load test: {NUM_REQUESTS} requests with {CONCURRENT_REQUESTS} concurrent")
    print("-" * 60)

    start_time = time.time()
    successes = 0
    failures = 0

    async with aiohttp.ClientSession() as session:
        # Create batches of concurrent requests
        for batch_start in range(0, NUM_REQUESTS, CONCURRENT_REQUESTS):
            batch_end = min(batch_start + CONCURRENT_REQUESTS, NUM_REQUESTS)
            batch_size = batch_end - batch_start

            # Send batch concurrently
            tasks = [
                send_event(session, event_id)
                for event_id in range(batch_start, batch_end)
            ]
            results = await asyncio.gather(*tasks)

            # Count successes/failures
            successes += sum(1 for r in results if r)
            failures += sum(1 for r in results if not r)

            # Progress update
            if batch_end % 1000 == 0:
                elapsed = time.time() - start_time
                rps = batch_end / elapsed
                print(f"Processed {batch_end}/{NUM_REQUESTS} events ({rps:.1f} req/s)")

    # Final stats
    elapsed = time.time() - start_time
    rps = NUM_REQUESTS / elapsed

    print("-" * 60)
    print(f"Load test complete!")
    print(f"Total time: {elapsed:.2f}s")
    print(f"Requests per second: {rps:.1f}")
    print(f"Successes: {successes}")
    print(f"Failures: {failures}")
    print(f"Success rate: {(successes/NUM_REQUESTS)*100:.1f}%")


if __name__ == "__main__":
    asyncio.run(run_load_test())
