"""Metric extractors for different LLM providers"""
from typing import Dict, Any, Optional


def extract_openai_metrics(response: Any, duration_ms: int) -> Optional[Dict[str, Any]]:
    """
    Extract metrics from OpenAI API response

    Supports both sync and async OpenAI client responses.

    Args:
        response: OpenAI API response object
        duration_ms: Request duration in milliseconds

    Returns:
        Event dictionary or None if extraction fails
    """
    try:
        # Handle ChatCompletion response
        if hasattr(response, 'model') and hasattr(response, 'usage'):
            event = {
                "model": response.model,
                "provider": "openai",
                "tokens_prompt": response.usage.prompt_tokens,
                "tokens_completion": response.usage.completion_tokens,
                "tokens_total": response.usage.total_tokens,
                "latency_ms": duration_ms,
                "status": "success",
                "has_error": False
            }

            # Extract response content if available
            if hasattr(response, 'choices') and len(response.choices) > 0:
                choice = response.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    event['response'] = choice.message.content

                # Extract finish reason
                if hasattr(choice, 'finish_reason'):
                    if 'metadata' not in event:
                        event['metadata'] = {}
                    event['metadata']['finish_reason'] = choice.finish_reason

            # Extract system fingerprint if available
            if hasattr(response, 'system_fingerprint'):
                if 'metadata' not in event:
                    event['metadata'] = {}
                event['metadata']['system_fingerprint'] = response.system_fingerprint

            return event

        # Handle streaming response (not fully supported yet)
        # For now, return None for streaming responses
        return None

    except Exception as e:
        # If extraction fails, return None
        return None


def extract_anthropic_metrics(response: Any, duration_ms: int) -> Optional[Dict[str, Any]]:
    """
    Extract metrics from Anthropic API response

    Supports Anthropic Claude API responses.

    Args:
        response: Anthropic API response object
        duration_ms: Request duration in milliseconds

    Returns:
        Event dictionary or None if extraction fails
    """
    try:
        # Handle Anthropic Message response
        if hasattr(response, 'model') and hasattr(response, 'usage'):
            event = {
                "model": response.model,
                "provider": "anthropic",
                "tokens_prompt": response.usage.input_tokens,
                "tokens_completion": response.usage.output_tokens,
                "tokens_total": response.usage.input_tokens + response.usage.output_tokens,
                "latency_ms": duration_ms,
                "status": "success",
                "has_error": False
            }

            # Extract response content if available
            if hasattr(response, 'content') and len(response.content) > 0:
                # Anthropic returns content as list of content blocks
                text_parts = []
                for content_block in response.content:
                    if hasattr(content_block, 'text'):
                        text_parts.append(content_block.text)

                if text_parts:
                    event['response'] = '\n'.join(text_parts)

            # Extract stop reason
            if hasattr(response, 'stop_reason'):
                if 'metadata' not in event:
                    event['metadata'] = {}
                event['metadata']['stop_reason'] = response.stop_reason

            # Extract role
            if hasattr(response, 'role'):
                if 'metadata' not in event:
                    event['metadata'] = {}
                event['metadata']['role'] = response.role

            return event

        return None

    except Exception as e:
        return None


def extract_generic_metrics(
    model: str,
    provider: str,
    prompt_tokens: int,
    completion_tokens: int,
    duration_ms: int,
    **kwargs
) -> Dict[str, Any]:
    """
    Create event from generic metrics

    Use this for custom tracking or when provider-specific extraction fails.

    Args:
        model: Model name
        provider: Provider name
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        duration_ms: Request duration in milliseconds
        **kwargs: Additional optional fields (response, metadata, etc.)

    Returns:
        Event dictionary
    """
    event = {
        "model": model,
        "provider": provider,
        "tokens_prompt": prompt_tokens,
        "tokens_completion": completion_tokens,
        "tokens_total": prompt_tokens + completion_tokens,
        "latency_ms": duration_ms,
        "status": "success",
        "has_error": False
    }

    # Add any additional fields
    for key, value in kwargs.items():
        if value is not None:
            event[key] = value

    return event
