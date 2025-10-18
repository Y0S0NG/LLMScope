// API Response Types

export interface SessionInfo {
  session_id: string;
  created_at: string;
  last_activity: string;
  is_active: boolean;
  metadata: Record<string, any>;
  event_count: number;
  total_tokens: number;
  total_cost: number;
}

export interface SessionMetrics {
  session_id: string;
  event_count: number;
  total_tokens: number;
  total_cost: number;
  models_used: string[];
}

export interface CreateSessionResponse {
  session_id: string;
  message: string;
}

export interface ResetSessionResponse {
  success: boolean;
  message: string;
  session_id: string;
}

export interface HealthResponse {
  status: string;
  database: string;
  sessions: number;
  events: number;
}

// Local Storage Types
export interface StoredSession {
  sessionId: string;
  createdAt: string;
  lastActivity: string;
}

// Chat Types
export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  response: string;
  event_id: string;
}

// Event Types
export interface EventResponse {
  id: string;
  time: string;
  model: string;
  provider: string;
  tokens_total: number;
  tokens_prompt: number;
  tokens_completion: number;
  cost_usd: number;
  latency_ms: number | null;
  status: string;
  has_error: boolean;
  error?: string | null;
}
