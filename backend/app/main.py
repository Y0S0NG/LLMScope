"""FastAPI app entry point"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from sqlalchemy import text
from pydantic import BaseModel
from typing import List
import uuid
import os
from anthropic import Anthropic

from .config import settings
from .db.base import engine, SessionLocal
from .db.models import Tenant, Project, LLMEvent
from .api import events, analytics, alerts, auth, websocket
from .dependencies import get_current_tenant, get_current_project


class DeleteEventsRequest(BaseModel):
    event_ids: List[str]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup: Verify default tenant exists in single-tenant mode
    if settings.single_tenant_mode:
        db = SessionLocal()
        try:
            tenant = db.query(Tenant).filter(Tenant.id == settings.default_tenant_id).first()
            if not tenant:
                print(f"⚠️  WARNING: Default tenant '{settings.default_tenant_id}' not found!")
                print("   Run: alembic upgrade head")
            else:
                print(f"✅ Single-tenant mode: Using tenant '{tenant.name}' (ID: {tenant.id})")

                project = db.query(Project).filter(Project.id == settings.default_project_id).first()
                if project:
                    print(f"✅ Default project: '{project.name}' (ID: {project.id})")
                else:
                    print(f"⚠️  WARNING: Default project '{settings.default_project_id}' not found!")
        finally:
            db.close()

    yield

    # Shutdown
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure from settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers with /api/v1 prefix
app.include_router(events.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(websocket.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LLMScope API",
        "version": settings.api_version,
        "mode": "single-tenant" if settings.single_tenant_mode else "multi-tenant"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    db = SessionLocal()
    try:
        # Check database connection
        db.execute(text("SELECT 1"))

        # In single-tenant mode, verify default tenant exists
        if settings.single_tenant_mode:
            tenant = db.query(Tenant).filter(Tenant.id == settings.default_tenant_id).first()
            if not tenant:
                return {
                    "status": "unhealthy",
                    "error": "Default tenant not found. Run database migrations."
                }

        return {
            "status": "healthy",
            "mode": "single-tenant" if settings.single_tenant_mode else "multi-tenant"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
    finally:
        db.close()


@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """Interactive demo page with chat and live events table"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LLMScope Interactive Demo</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                background-color: #f5f5f5;
                height: 100vh;
                overflow: hidden;
            }
            .container {
                display: flex;
                height: 100vh;
                gap: 20px;
                padding: 20px;
            }
            .panel {
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                overflow: hidden;
                display: flex;
                flex-direction: column;
            }
            .left-panel {
                flex: 1;
                min-width: 400px;
            }
            .right-panel {
                flex: 1;
                min-width: 600px;
            }
            .panel-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                font-size: 20px;
                font-weight: bold;
            }
            .chat-container {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            .message {
                padding: 12px 16px;
                border-radius: 8px;
                max-width: 85%;
                word-wrap: break-word;
                animation: fadeIn 0.3s ease-in;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .user-message {
                background: #667eea;
                color: white;
                align-self: flex-end;
                margin-left: auto;
            }
            .assistant-message {
                background: #f0f0f0;
                color: #333;
                align-self: flex-start;
            }
            .system-message {
                background: #fff3cd;
                color: #856404;
                align-self: center;
                font-size: 14px;
                font-style: italic;
            }
            .input-container {
                padding: 20px;
                border-top: 1px solid #e0e0e0;
                display: flex;
                gap: 10px;
            }
            #messageInput {
                flex: 1;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 15px;
                font-family: inherit;
                outline: none;
            }
            #messageInput:focus {
                border-color: #667eea;
            }
            .btn {
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
                font-size: 15px;
            }
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .btn-primary:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }
            .btn:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
            }
            .events-container {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
            }
            .stats {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .stat-item {
                text-align: center;
            }
            .stat-label {
                font-size: 12px;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .stat-value {
                font-size: 24px;
                font-weight: bold;
                color: #667eea;
                margin-top: 5px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                font-size: 14px;
            }
            th {
                background: #667eea;
                color: white;
                padding: 12px 8px;
                text-align: left;
                position: sticky;
                top: 0;
                font-weight: 600;
            }
            td {
                padding: 10px 8px;
                border-bottom: 1px solid #e0e0e0;
            }
            tr:hover {
                background: #f8f9fa;
            }
            .badge {
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            .badge-success {
                background: #d4edda;
                color: #155724;
            }
            .badge-error {
                background: #f8d7da;
                color: #721c24;
            }
            .loading {
                text-align: center;
                padding: 40px;
                color: #666;
            }
            .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 15px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="panel left-panel">
                <div class="panel-header">💬 Chat with Claude</div>
                <div class="chat-container" id="chatContainer">
                    <div class="message system-message">
                        Welcome! Ask me anything. Your interactions are being tracked by LLMScope.
                    </div>
                </div>
                <div class="input-container">
                    <input
                        type="text"
                        id="messageInput"
                        placeholder="Type your message..."
                        onkeypress="if(event.key==='Enter') sendMessage()"
                    />
                    <button class="btn btn-primary" onclick="sendMessage()" id="sendBtn">Send</button>
                </div>
            </div>

            <div class="panel right-panel">
                <div class="panel-header">📊 Live Events Monitor</div>
                <div class="events-container">
                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-label">Total Events</div>
                            <div class="stat-value" id="totalEvents">0</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Total Tokens</div>
                            <div class="stat-value" id="totalTokens">0</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Total Cost</div>
                            <div class="stat-value" id="totalCost">$0.00</div>
                        </div>
                    </div>
                    <div id="eventsTableContainer">
                        <div class="loading">
                            <div class="spinner"></div>
                            Loading events...
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let ws = null;
            let reconnectInterval = null;

            // Connect to WebSocket for real-time events
            function connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                ws = new WebSocket(`${protocol}//${window.location.host}/api/v1/ws/events`);

                ws.onopen = () => {
                    console.log('WebSocket connected');
                    clearInterval(reconnectInterval);
                };

                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    if (data.type === 'event_update') {
                        loadEvents();
                    }
                };

                ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                };

                ws.onclose = () => {
                    console.log('WebSocket closed, reconnecting...');
                    reconnectInterval = setInterval(() => {
                        connectWebSocket();
                    }, 3000);
                };
            }

            // Load events from API
            async function loadEvents() {
                try {
                    const response = await fetch('/api/v1/events/recent?limit=50', {
                        headers: {
                            'X-API-Key': 'llmscope-local-key'
                        }
                    });
                    const data = await response.json();
                    displayEvents(data.events);
                } catch (error) {
                    console.error('Error loading events:', error);
                }
            }

            // Display events in table
            function displayEvents(events) {
                let totalTokens = 0;
                let totalCost = 0;

                let html = `
                    <table>
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Model</th>
                                <th>Tokens</th>
                                <th>Cost</th>
                                <th>Latency</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                events.forEach(event => {
                    const time = new Date(event.time).toLocaleTimeString();
                    const tokens = event.tokens_total || 0;
                    const cost = event.cost_usd || 0;
                    const latency = event.latency_ms || 'N/A';
                    const status = event.has_error ? 'Error' : 'OK';
                    const statusClass = event.has_error ? 'badge-error' : 'badge-success';

                    totalTokens += tokens;
                    totalCost += cost;

                    html += `
                        <tr>
                            <td>${time}</td>
                            <td>${event.model || 'N/A'}</td>
                            <td>${tokens.toLocaleString()}</td>
                            <td>$${cost.toFixed(6)}</td>
                            <td>${latency}ms</td>
                            <td><span class="badge ${statusClass}">${status}</span></td>
                        </tr>
                    `;
                });

                html += '</tbody></table>';
                document.getElementById('eventsTableContainer').innerHTML = html;
                document.getElementById('totalEvents').textContent = events.length;
                document.getElementById('totalTokens').textContent = totalTokens.toLocaleString();
                document.getElementById('totalCost').textContent = `$${totalCost.toFixed(4)}`;
            }

            // Send chat message
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();

                if (!message) return;

                // Disable input
                input.disabled = true;
                document.getElementById('sendBtn').disabled = true;

                // Add user message to chat
                addMessage(message, 'user');
                input.value = '';

                try {
                    // Call backend chat API
                    const response = await fetch('/api/v1/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-API-Key': 'llmscope-local-key'
                        },
                        body: JSON.stringify({ message })
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const data = await response.json();
                    addMessage(data.response, 'assistant');

                } catch (error) {
                    console.error('Error:', error);
                    addMessage('Sorry, there was an error processing your message.', 'system');
                } finally {
                    // Re-enable input
                    input.disabled = false;
                    document.getElementById('sendBtn').disabled = false;
                    input.focus();
                }
            }

            // Add message to chat
            function addMessage(text, role) {
                const chatContainer = document.getElementById('chatContainer');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${role}-message`;
                messageDiv.textContent = text;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }

            // Initialize
            connectWebSocket();
            loadEvents();
            setInterval(loadEvents, 5000); // Refresh every 5 seconds as fallback
        </script>
    </body>
    </html>
    """


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


# Initialize Anthropic client
anthropic_client = None


def get_anthropic_client():
    """Get or create Anthropic client"""
    global anthropic_client
    if anthropic_client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")
        anthropic_client = Anthropic(api_key=api_key)
    return anthropic_client


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    tenant: Tenant = Depends(get_current_tenant),
    project: Project = Depends(get_current_project)
):
    """
    Chat endpoint that uses Anthropic's API and tracks with LLMScope.
    This simulates the demo chatbot but in the web interface.
    """
    try:
        client = get_anthropic_client()

        # Call Anthropic API
        import time
        start_time = time.time()

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": request.message}]
        )

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        # Extract response text
        first_block = response.content[0]
        assistant_message = first_block.text if hasattr(first_block, 'text') else str(first_block)

        # Track event with LLMScope
        from .services.event_service import EventService

        event_data = {
            "tenant_id": str(tenant.id),
            "project_id": str(project.id),
            "model": "claude-3-5-sonnet-20241022",
            "provider": "anthropic",
            "endpoint": "/api/v1/chat",
            "tokens_prompt": response.usage.input_tokens,
            "tokens_completion": response.usage.output_tokens,
            "tokens_total": response.usage.input_tokens + response.usage.output_tokens,
            "latency_ms": latency_ms,
            "status": "success",
            "has_error": False,
        }

        # Queue the event
        await EventService.queue_event(event_data)

        # Notify WebSocket clients
        from .api.websocket import notify_event_update
        await notify_event_update()

        return ChatResponse(response=assistant_message)

    except Exception as e:
        # Track error event
        try:
            from .services.event_service import EventService
            error_event = {
                "tenant_id": str(tenant.id),
                "project_id": str(project.id),
                "model": "claude-3-5-sonnet-20241022",
                "provider": "anthropic",
                "endpoint": "/api/v1/chat",
                "tokens_prompt": 0,
                "tokens_completion": 0,
                "tokens_total": 0,
                "latency_ms": 0,
                "status": "error",
                "has_error": True,
                "error_message": str(e),
            }
            await EventService.queue_event(error_event)
        except:
            pass

        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.get("/events/table", response_class=HTMLResponse)
async def events_table():
    """Display all events in a table format"""
    db = SessionLocal()
    try:
        # Query all events ordered by time descending
        events = db.query(LLMEvent).order_by(LLMEvent.time.desc()).limit(1000).all()

        # Build HTML table
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>LLMScope Events</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }
                h1 { color: #333; }
                .info {
                    background-color: #e3f2fd;
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .actions {
                    display: flex;
                    gap: 10px;
                }
                .btn {
                    padding: 8px 16px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-weight: bold;
                    transition: background-color 0.3s;
                }
                .btn-danger {
                    background-color: #d32f2f;
                    color: white;
                }
                .btn-danger:hover {
                    background-color: #b71c1c;
                }
                .btn-secondary {
                    background-color: #757575;
                    color: white;
                }
                .btn-secondary:hover {
                    background-color: #616161;
                }
                .btn:disabled {
                    background-color: #e0e0e0;
                    color: #9e9e9e;
                    cursor: not-allowed;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    background-color: white;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                th {
                    background-color: #1976d2;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    position: sticky;
                    top: 0;
                }
                td {
                    padding: 10px;
                    border-bottom: 1px solid #ddd;
                }
                tr:hover { background-color: #f5f5f5; }
                .error { color: #d32f2f; font-weight: bold; }
                .success { color: #388e3c; }
                .truncate {
                    max-width: 300px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }
                .cost { text-align: right; }
                .tokens { text-align: right; }
                .checkbox-cell { text-align: center; width: 40px; }
            </style>
        </head>
        <body>
            <h1>LLMScope Events Dashboard</h1>
            <div class="info">
                <div>
                    <strong>Total Events:</strong> """ + str(len(events)) + """ (showing latest 1000) |
                    <strong>Selected:</strong> <span id="selectedCount">0</span>
                </div>
                <div class="actions">
                    <button class="btn btn-secondary" onclick="selectAll()">Select All</button>
                    <button class="btn btn-secondary" onclick="deselectAll()">Deselect All</button>
                    <button class="btn btn-danger" onclick="deleteSelected()" id="deleteBtn" disabled>Delete Selected</button>
                </div>
            </div>
            <table>
                <thead>
                    <tr>
                        <th class="checkbox-cell"><input type="checkbox" id="selectAllCheckbox" onclick="toggleAll(this)"></th>
                        <th>Time</th>
                        <th>Model</th>
                        <th>Provider</th>
                        <th>User ID</th>
                        <th>Session ID</th>
                        <th>Tokens</th>
                        <th>Cost (USD)</th>
                        <th>Latency (ms)</th>
                        <th>Status</th>
                        <th>Error</th>
                    </tr>
                </thead>
                <tbody>
        """

        for event in events:
            has_error = getattr(event, 'has_error', False)
            status_class = "error" if has_error else "success"
            status_text = "Error" if has_error else "OK"

            time_val = getattr(event, 'time', None)
            time_str = time_val.strftime('%Y-%m-%d %H:%M:%S') if time_val else 'N/A'
            model = getattr(event, 'model', None) or 'N/A'
            provider = getattr(event, 'provider', None) or 'N/A'
            user_id = getattr(event, 'user_id', None) or 'N/A'
            session_id = getattr(event, 'session_id', None) or 'N/A'
            tokens = getattr(event, 'tokens_total', None) or 0
            cost_val = getattr(event, 'cost_usd', None)
            cost = float(cost_val) if cost_val is not None else 0.0
            latency = getattr(event, 'latency_ms', None) or 'N/A'
            error_msg = getattr(event, 'error_message', None) or ''
            event_id = str(getattr(event, 'id', ''))

            html += f"""
                    <tr>
                        <td class="checkbox-cell"><input type="checkbox" class="event-checkbox" value="{event_id}" onchange="updateSelection()"></td>
                        <td>{time_str}</td>
                        <td>{model}</td>
                        <td>{provider}</td>
                        <td>{user_id}</td>
                        <td>{session_id}</td>
                        <td class="tokens">{tokens}</td>
                        <td class="cost">${cost:.6f}</td>
                        <td class="tokens">{latency}</td>
                        <td class="{status_class}">{status_text}</td>
                        <td class="truncate">{error_msg}</td>
                    </tr>
            """

        html += """
                </tbody>
            </table>
            <script>
                function updateSelection() {
                    const checkboxes = document.querySelectorAll('.event-checkbox');
                    const checkedCount = document.querySelectorAll('.event-checkbox:checked').length;
                    document.getElementById('selectedCount').textContent = checkedCount;
                    document.getElementById('deleteBtn').disabled = checkedCount === 0;

                    const allChecked = checkedCount === checkboxes.length;
                    document.getElementById('selectAllCheckbox').checked = allChecked;
                }

                function toggleAll(checkbox) {
                    const checkboxes = document.querySelectorAll('.event-checkbox');
                    checkboxes.forEach(cb => cb.checked = checkbox.checked);
                    updateSelection();
                }

                function selectAll() {
                    const checkboxes = document.querySelectorAll('.event-checkbox');
                    checkboxes.forEach(cb => cb.checked = true);
                    updateSelection();
                }

                function deselectAll() {
                    const checkboxes = document.querySelectorAll('.event-checkbox');
                    checkboxes.forEach(cb => cb.checked = false);
                    updateSelection();
                }

                async function deleteSelected() {
                    const checkboxes = document.querySelectorAll('.event-checkbox:checked');
                    const ids = Array.from(checkboxes).map(cb => cb.value);

                    if (ids.length === 0) {
                        alert('No events selected');
                        return;
                    }

                    if (!confirm(`Are you sure you want to delete ${ids.length} event(s)?`)) {
                        return;
                    }

                    try {
                        const response = await fetch('/events/delete', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ event_ids: ids })
                        });

                        if (response.ok) {
                            alert('Events deleted successfully');
                            window.location.reload();
                        } else {
                            const error = await response.json();
                            alert('Error deleting events: ' + (error.detail || 'Unknown error'));
                        }
                    } catch (error) {
                        alert('Error deleting events: ' + error.message);
                    }
                }
            </script>
        </body>
        </html>
        """

        return html

    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body>
            <h1>Error loading events</h1>
            <p style="color: red;">{str(e)}</p>
        </body>
        </html>
        """
    finally:
        db.close()


@app.post("/events/delete")
async def delete_events(request: DeleteEventsRequest):
    """Delete selected events by their IDs"""
    db = SessionLocal()
    try:
        # Convert string IDs to UUIDs
        event_uuids = []
        for event_id in request.event_ids:
            try:
                event_uuids.append(uuid.UUID(event_id))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid UUID format: {event_id}")

        # Delete events
        deleted_count = db.query(LLMEvent).filter(LLMEvent.id.in_(event_uuids)).delete(synchronize_session=False)
        db.commit()

        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"Successfully deleted {deleted_count} event(s)"
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting events: {str(e)}")
    finally:
        db.close()
