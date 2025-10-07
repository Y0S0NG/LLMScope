"""
Example: Automatic tracking with monkey-patching

This example shows how to use monkey-patching to automatically
track ALL OpenAI/Anthropic API calls in your application without
any code changes to your existing functions.
"""
from llmscope import LLMScope
from llmscope.integrations import patch_openai, unpatch_openai
from llmscope.integrations import patch_anthropic, unpatch_anthropic
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


def example_1_basic_patching():
    """Basic monkey-patching - track all OpenAI calls automatically"""
    print("Example 1: Basic monkey-patching")
    print("Applying OpenAI patch...")

    # Patch OpenAI - now ALL calls are automatically tracked!
    patch_openai(tracker)

    # Make regular OpenAI calls - no decorator needed!
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "What is 2+2?"}]
    )

    print(f"Response: {response.choices[0].message.content}")
    print("✓ Automatically tracked!\n")

    # Clean up
    unpatch_openai()


def example_2_multiple_calls():
    """All calls in a function are automatically tracked"""
    print("Example 2: Multiple calls auto-tracked")

    patch_openai(tracker)

    def my_existing_function(questions):
        """Your existing code - no changes needed!"""
        results = []
        for question in questions:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": question}]
            )
            results.append(response.choices[0].message.content)
        return results

    # Call your function - all LLM calls tracked automatically
    questions = [
        "What is Python?",
        "What is JavaScript?",
    ]
    answers = my_existing_function(questions)

    print(f"✓ Tracked {len(answers)} calls automatically!\n")

    unpatch_openai()


def example_3_anthropic_patching():
    """Patch Anthropic Claude API"""
    print("Example 3: Anthropic patching")

    try:
        import anthropic

        # Patch Anthropic
        patch_anthropic(tracker)

        client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

        # Regular Anthropic call - automatically tracked!
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[{"role": "user", "content": "Hello!"}]
        )

        print(f"Response: {response.content[0].text[:50]}...")
        print("✓ Anthropic call auto-tracked!\n")

        unpatch_anthropic()

    except ImportError:
        print("⚠ Anthropic not installed\n")
    except Exception as e:
        print(f"⚠ Anthropic error: {e}\n")


def example_4_both_providers():
    """Patch multiple providers at once"""
    print("Example 4: Multi-provider patching")

    # Patch both OpenAI and Anthropic
    patch_openai(tracker)

    try:
        patch_anthropic(tracker)
    except ImportError:
        pass

    # Now ALL calls to both providers are tracked
    response1 = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "OpenAI test"}]
    )
    print("✓ OpenAI call tracked")

    try:
        import anthropic
        client = anthropic.Anthropic()
        response2 = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=100,
            messages=[{"role": "user", "content": "Anthropic test"}]
        )
        print("✓ Anthropic call tracked")
    except:
        pass

    print()

    # Clean up both
    unpatch_openai()
    unpatch_anthropic()


def example_5_async_patching():
    """Patching works with async functions too"""
    print("Example 5: Async patching")

    import asyncio

    async def async_example():
        patch_openai(tracker)

        client = openai.AsyncOpenAI()

        # Async call - also tracked!
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Async test"}]
        )

        print(f"Response: {response.choices[0].message.content}")
        print("✓ Async call tracked!\n")

        unpatch_openai()

    asyncio.run(async_example())


def example_6_selective_patching():
    """Patch only when needed"""
    print("Example 6: Selective patching")

    # Before patching - not tracked
    print("Before patch: Making untracked call")
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Not tracked"}]
    )
    print("  (not tracked)")

    # Apply patch
    patch_openai(tracker)
    print("After patch: Making tracked call")
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Tracked!"}]
    )
    print("  ✓ Tracked!")

    # Remove patch
    unpatch_openai()
    print("After unpatch: Making untracked call")
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Not tracked again"}]
    )
    print("  (not tracked)\n")


if __name__ == "__main__":
    print("=== LLMScope Monkey-Patching Examples ===\n")
    print("This shows how to track ALL LLM calls automatically")
    print("without modifying your existing code!\n")

    example_1_basic_patching()
    example_2_multiple_calls()
    example_3_anthropic_patching()
    example_4_both_providers()
    example_5_async_patching()
    example_6_selective_patching()

    print("=== All examples completed ===")
    print("\nKey takeaway: Use monkey-patching when you want")
    print("to track ALL calls without modifying existing code!")
    print("\nCheck your LLMScope dashboard for all tracked events!")
