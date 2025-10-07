#!/usr/bin/env python3
"""
Simple chatbot demo using Anthropic's API with LLMScope tracking.
"""
import os
from dotenv import load_dotenv
from anthropic import Anthropic
from llmscope import LLMScope

# Load environment variables
load_dotenv()

# Initialize Anthropic client
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY not found in environment variables.")
    print("Please create a .env file with your API key.")
    exit(1)

client = Anthropic(api_key=api_key)

# Initialize LLMScope tracker
llmscope_api_key = os.getenv("LLMSCOPE_API_KEY")
llmscope_endpoint = os.getenv("LLMSCOPE_ENDPOINT", "http://localhost:8000")

tracker = LLMScope(
    api_key=llmscope_api_key,
    base_url=llmscope_endpoint,
    project="chatbot_demo",
    debug=True  # Enable debug logging
)


@tracker.trace(name="anthropic_chat")
def get_chat_response(messages):
    """
    Get a response from Claude using Anthropic's API.
    This function is automatically tracked by LLMScope.
    """
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=messages
    )
    return response


def main():
    """Run the chatbot application."""

    print("=" * 60)
    print("Anthropic Chatbot Demo with LLMScope Tracking")
    print("=" * 60)
    print("Type 'quit', 'exit', or 'q' to end the conversation.")
    print()

    conversation_history = []

    while True:
        # Get user input
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break

        # Add user message to conversation history
        conversation_history.append({
            "role": "user",
            "content": user_input
        })

        try:
            # Call Anthropic API with automatic LLMScope tracking via decorator
            response = get_chat_response(conversation_history)

            # Extract assistant's response
            assistant_message = response.content[0].text

            # Add assistant message to conversation history
            conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            # Display response
            print(f"\nAssistant: {assistant_message}\n")

        except Exception as e:
            print(f"\nError: {str(e)}\n")
            # Remove the last user message if there was an error
            conversation_history.pop()

if __name__ == "__main__":
    main()
