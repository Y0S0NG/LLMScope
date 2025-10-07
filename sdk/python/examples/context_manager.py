"""
Example: Manual tracking with context manager

This example shows how to use the context manager for manual tracking
with more control over what gets tracked.
"""
from llmscope import LLMScope
import openai
import os

# Initialize LLMScope tracker
tracker = LLMScope(
    api_key=os.getenv("LLMSCOPE_API_KEY", "your-api-key"),
    base_url=os.getenv("LLMSCOPE_URL", "http://localhost:8000"),
    project="production",
    debug=True
)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")


def example_1_basic_context_manager():
    """Basic usage of context manager"""
    print("Example 1: Basic context manager")

    with tracker.track("openai_completion") as span:
        # Make your LLM call
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "What is Python?"}]
        )

        # Track the response
        span.track_response(response)

    print("✓ Tracked successfully!\n")


def example_2_with_metadata():
    """Add custom metadata to tracked events"""
    print("Example 2: Context manager with metadata")

    with tracker.track("user_query") as span:
        # Set custom metadata
        span.set_metadata("user_id", "user_12345")
        span.set_metadata("session_id", "sess_abc123")
        span.set_metadata("environment", "production")

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Explain machine learning"}]
        )

        # Track with metadata
        span.track_response(response)

    print("✓ Tracked with metadata!\n")


def example_3_multiple_calls():
    """Track multiple LLM calls in a single span"""
    print("Example 3: Multiple calls in one span")

    with tracker.track("multi_step_workflow") as span:
        span.set_metadata("workflow_type", "multi_step")

        # First call
        response1 = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Generate a topic"}]
        )
        span.track_response(response1)

        topic = response1.choices[0].message.content

        # Second call using output from first
        response2 = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": f"Write about: {topic}"}
            ]
        )
        span.track_response(response2)

    print("✓ Tracked multiple calls!\n")


def example_4_anthropic():
    """Track Anthropic Claude API calls"""
    print("Example 4: Anthropic Claude tracking")

    try:
        import anthropic

        client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

        with tracker.track("claude_completion") as span:
            span.set_metadata("provider", "anthropic")

            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": "What is AI?"}
                ]
            )

            span.track_response(response)

        print("✓ Tracked Anthropic call!\n")

    except ImportError:
        print("⚠ Anthropic not installed (pip install anthropic)\n")
    except Exception as e:
        print(f"⚠ Anthropic error: {e}\n")


def example_5_error_handling():
    """Error handling with context manager"""
    print("Example 5: Error handling")

    try:
        with tracker.track("failing_call") as span:
            span.set_metadata("expected_to_fail", True)

            # This will fail
            response = openai.chat.completions.create(
                model="invalid-model",
                messages=[{"role": "user", "content": "test"}]
            )
            span.track_response(response)

    except Exception as e:
        print(f"✓ Error tracked: {type(e).__name__}\n")
        # Error is automatically tracked by the context manager


def example_6_no_auto_track():
    """Context manager without tracking response"""
    print("Example 6: Manual span without auto-tracking")

    # Sometimes you just want to time something
    with tracker.track("custom_operation") as span:
        span.set_metadata("operation", "custom")

        # Do your work here
        result = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hi"}]
        )

        # Don't call span.track_response()
        # Only timing and metadata will be tracked if error occurs

    print("✓ Span completed (no explicit tracking)\n")


if __name__ == "__main__":
    print("=== LLMScope Context Manager Examples ===\n")

    example_1_basic_context_manager()
    example_2_with_metadata()
    example_3_multiple_calls()
    example_4_anthropic()
    example_5_error_handling()
    example_6_no_auto_track()

    print("=== All examples completed ===")
    print("Check your LLMScope dashboard for tracked events!")
