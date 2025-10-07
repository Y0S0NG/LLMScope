"""
Example: Auto-tracking with @trace decorator

This example shows how to use the @tracker.trace() decorator
to automatically track LLM API calls.
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


# Decorate your function to automatically track all LLM calls
@tracker.trace()
def get_completion(prompt: str) -> str:
    """
    Get completion from OpenAI - automatically tracked!

    The decorator will:
    - Measure request latency
    - Extract model, tokens, cost
    - Send metrics to LLMScope
    - Return the original response
    """
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


@tracker.trace(name="summarize_text")
def summarize(text: str) -> str:
    """Custom name for tracked function"""
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Summarize the following text concisely."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content


# Example with async function
@tracker.trace()
async def async_completion(prompt: str) -> str:
    """Async functions are also supported"""
    client = openai.AsyncOpenAI()
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    # Example 1: Basic usage
    print("Example 1: Basic auto-tracking")
    result = get_completion("What is the capital of France?")
    print(f"Result: {result}\n")
    # Metrics automatically sent to LLMScope!

    # Example 2: Custom name
    print("Example 2: Custom function name")
    summary = summarize("Python is a high-level programming language...")
    print(f"Summary: {summary}\n")

    # Example 3: Async usage
    print("Example 3: Async auto-tracking")
    import asyncio
    async_result = asyncio.run(async_completion("Tell me a joke"))
    print(f"Joke: {async_result}\n")

    # Example 4: Error tracking
    print("Example 4: Error tracking")
    try:
        @tracker.trace()
        def failing_function():
            # This will be tracked as an error
            raise ValueError("Something went wrong!")

        failing_function()
    except ValueError as e:
        print(f"Error caught: {e}")
        # Error metrics sent to LLMScope!

    print("\nAll calls have been automatically tracked!")
    print("Check your LLMScope dashboard for metrics.")
