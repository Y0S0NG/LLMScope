"""Metrics calculation"""
from typing import Dict, Any, List
from datetime import datetime


def calculate_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int
) -> float:
    """Calculate cost based on model and token usage"""
    # Pricing per 1K tokens (approximate)
    pricing = {
        "gpt-4": {"prompt": 0.03, "completion": 0.06},
        "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
        "claude-3-opus": {"prompt": 0.015, "completion": 0.075},
        "claude-3-sonnet": {"prompt": 0.003, "completion": 0.015},
    }

    model_pricing = pricing.get(model, {"prompt": 0, "completion": 0})
    prompt_cost = (prompt_tokens / 1000) * model_pricing["prompt"]
    completion_cost = (completion_tokens / 1000) * model_pricing["completion"]

    return prompt_cost + completion_cost


def aggregate_metrics(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate metrics from events"""
    if not events:
        return {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "avg_latency_ms": 0.0
        }

    total_requests = len(events)
    total_tokens = sum(e.get("total_tokens", 0) for e in events)
    total_cost = sum(e.get("cost", 0) for e in events)
    avg_latency = sum(e.get("latency_ms", 0) for e in events) / total_requests

    return {
        "total_requests": total_requests,
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 4),
        "avg_latency_ms": round(avg_latency, 2)
    }
