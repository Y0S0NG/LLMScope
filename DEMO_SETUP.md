# LLMScope Demo Setup Guide

This guide will help you quickly set up and run the LLMScope interactive demo.

## Quick Start

### Step 1: Get Your Anthropic API Key

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key and copy it

### Step 2: Configure Backend

```bash
cd backend
cp .env.example .env
```

Edit `.env` and add your API key:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

### Step 3: Start the Backend

```bash
# Make sure you're in the backend directory
docker-compose up --build
```

Wait for all services to start. You should see:
- ✅ Database migrations complete
- ✅ API server running on port 8000
- ✅ Worker processing events
- ✅ Redis ready

### Step 4: Open the Demo

Open your browser and navigate to:
```
http://localhost:8000/demo
```

You should see:
- **Left panel**: Chat interface with Claude
- **Right panel**: Live events monitoring table

### Step 5: Start Chatting!

1. Type a message in the chat input
2. Press Enter or click Send
3. Watch the response appear in the chat
4. See the event tracked in real-time on the right panel

## What You'll See

### Chat Interface (Left Panel)
- Clean, modern chat UI
- Message history
- Typing indicator while processing

### Events Monitor (Right Panel)
- **Real-time table**: Shows all API calls as they happen
- **Live statistics**:
  - Total events count
  - Total tokens used
  - Total cost in USD
- **Event details**: Model, tokens, cost, latency, status

## Architecture Overview

```
┌─────────────┐
│   Browser   │
│             │
│  /demo UI   │
└──────┬──────┘
       │
       │ HTTP POST /api/v1/chat
       ▼
┌─────────────────────┐
│   FastAPI Backend   │
│                     │
│  1. Call Anthropic  │
│  2. Track Event     │
│  3. Notify WS       │
└─────────┬───────────┘
          │
          ├─→ Anthropic API
          │
          ├─→ Redis Queue
          │   (Event Ingestion)
          │
          └─→ WebSocket
              (Real-time Updates)
                  │
                  ▼
          ┌───────────────┐
          │  Event Worker │
          │               │
          │  PostgreSQL   │
          │  (TimescaleDB)│
          └───────────────┘
```

## Troubleshooting

### Port Already in Use
If port 8000 is already in use:
```bash
# Find and stop the process
lsof -ti:8000 | xargs kill -9

# Or change the port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Module Not Found: anthropic
```bash
# Rebuild containers
cd backend
docker-compose down
docker-compose up --build
```

### WebSocket Connection Failed
- Check that backend is running: `docker-compose ps`
- Verify no firewall blocking port 8000
- Check browser console for specific errors

### Events Not Appearing
```bash
# Check worker logs
docker-compose logs worker

# Check Redis connection
docker-compose logs redis

# Verify database
docker-compose exec db psql -U postgres -d llmscope -c "SELECT COUNT(*) FROM llm_events;"
```

## Next Steps

### Explore the API
- **Events API**: `GET http://localhost:8000/api/v1/events/recent`
- **Stats API**: `GET http://localhost:8000/api/v1/events/stats`
- **Health Check**: `GET http://localhost:8000/health`

### View All Events
- **Full Events Table**: http://localhost:8000/events/table
  - Includes bulk delete functionality
  - Shows complete event history

### Console Demo
Try the command-line chatbot:
```bash
cd demo
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
pip install -r requirements.txt
python chatbot.py
```

## Features to Try

1. **Send Multiple Messages**: Watch events accumulate in real-time
2. **Check Statistics**: See total tokens and costs update live
3. **Open Multiple Browser Tabs**: All stay synchronized via WebSocket
4. **Monitor Latency**: Compare response times across messages
5. **Error Handling**: Try disconnecting internet to see error tracking

## Stopping the Demo

```bash
# Stop containers (keeps data)
docker-compose down

# Stop and remove all data
docker-compose down -v
```

## Need Help?

- **Documentation**: See [demo/README.md](demo/README.md)
- **API Docs**: http://localhost:8000/docs (when running)
- **Issues**: Check logs with `docker-compose logs`
