# LLMScope Demo Applications

This directory contains demo applications showcasing LLMScope's event tracking capabilities.

## Available Demos

### 1. Console Chatbot (`chatbot.py`)
A simple command-line chatbot powered by Claude with LLMScope tracking.

**Features:**
- Interactive command-line chatbot powered by Claude
- Conversation history maintained throughout the session
- LLMScope integration for tracking requests and responses
- Simple setup with environment variables

### 2. Interactive Web Demo
A modern web interface combining chat and real-time event monitoring on a single page.

**Features:**
- **Split-panel UI**: Chat interface on the left, live events table on the right
- **Real-time updates**: WebSocket connection for instant event table updates
- **Live statistics**: Total events, tokens, and cost displayed in real-time
- **Automatic tracking**: All chat interactions are tracked via LLMScope

**Access the web demo:**
```
http://localhost:8000/demo
```
(requires backend server running)

## Prerequisites

- Python 3.8 or higher
- Anthropic API key
- LLMScope backend running (optional, for tracking)

## Setup

1. **Install dependencies:**

   ```bash
   cd demo
   pip install -r requirements.txt
   ```

   Or install the LLMScope SDK from the local repository:

   ```bash
   cd ../sdk/python
   pip install -e .
   cd ../../demo
   pip install anthropic python-dotenv
   ```

2. **Configure environment variables:**

   Copy the example environment file and add your API keys:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Anthropic API key:

   ```
   ANTHROPIC_API_KEY=your_actual_api_key_here
   LLMSCOPE_API_KEY=your_llmscope_api_key_here  # Optional
   LLMSCOPE_ENDPOINT=http://localhost:8000      # Optional
   ```

## Usage

### Console Chatbot

Run the chatbot:

```bash
python chatbot.py
```

The chatbot will start an interactive session. Type your messages and press Enter to chat with Claude. Type `quit`, `exit`, or `q` to end the conversation.

### Example Session

```
============================================================
Anthropic Chatbot Demo with LLMScope Tracking
============================================================
Type 'quit', 'exit', or 'q' to end the conversation.

You: Hello! What can you help me with?
Assistant: Hello\! I can help you with a wide variety of tasks...

You: What is LLMScope?

Assistant: LLMScope is a monitoring and tracking system for LLM applications...

You: quit

Goodbye\!
```

### Interactive Web Demo

1. Set up the backend environment:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

2. Build and start the LLMScope backend server:
   ```bash
   docker-compose up --build
   ```

3. Open your browser to:
   ```
   http://localhost:8000/demo
   ```

4. Start chatting and watch the events appear in real-time!

**Web Demo Architecture:**
```
User Message → Backend /api/v1/chat endpoint
    ↓
Call Anthropic API
    ↓
Track event with LLMScope (EventService.queue_event)
    ↓
Notify WebSocket clients
    ↓
Frontend refreshes events table
```

## LLMScope Integration

The chatbot automatically tracks:

- Request metadata (user_id, session_id, timestamps)
- Model usage (tokens, model name)
- Conversation context
- Response latency

All tracking data is sent to your LLMScope backend for monitoring and analytics.

## Troubleshooting

### Console Chatbot Issues

**Missing API Key**

If you see `Error: ANTHROPIC_API_KEY not found`, make sure:
1. You have created a `.env` file in the demo directory
2. The file contains your Anthropic API key
3. The key is valid

**LLMScope Connection Issues**

If LLMScope tracking is not working:
1. Ensure the LLMScope backend is running
2. Check that `LLMSCOPE_ENDPOINT` points to the correct URL
3. Verify your `LLMSCOPE_API_KEY` is correct

### Web Demo Issues

**ModuleNotFoundError: No module named 'anthropic'**

If you see this error, rebuild the Docker containers:
```bash
cd backend
docker-compose down
docker-compose up --build
```

**Chat Not Working**

1. Verify `ANTHROPIC_API_KEY` is set in `backend/.env`
2. Rebuild containers after adding the API key: `docker-compose up --build`
3. Check backend logs: `docker-compose logs api`

**WebSocket Connection Issues**

- Ensure backend is running on port 8000
- Check browser console for connection errors
- WebSocket will auto-reconnect every 3 seconds if disconnected

**No Events Showing**

- Verify the event worker is running: `docker-compose ps`
- Check Redis is accessible: `docker-compose logs redis`
- Ensure database migrations are up to date

## Notes

- The `.env` file is gitignored to prevent accidental exposure of API keys
- LLMScope tracking is optional - the chatbot will work without it
- Conversation history is maintained only for the current session
