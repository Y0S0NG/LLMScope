-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Tenants table (B2B multi-tenancy)
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    plan VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    settings JSONB DEFAULT '{}',
    usage_limits JSONB DEFAULT '{"requests": 10000, "cost": 100}'
);

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    settings JSONB DEFAULT '{}'
);

-- Main events table (hypertable)
CREATE TABLE llm_events (
    time TIMESTAMPTZ NOT NULL,
    id UUID DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL,
    project_id UUID NOT NULL,
    
    -- Request metadata
    model VARCHAR(50),
    provider VARCHAR(50),
    endpoint VARCHAR(255),
    
    -- User tracking
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    
    -- Token usage
    tokens_prompt INTEGER,
    tokens_completion INTEGER,
    tokens_total INTEGER,
    
    -- Performance metrics
    latency_ms INTEGER,
    time_to_first_token_ms INTEGER,
    
    -- Cost tracking
    cost_usd DECIMAL(10, 6),
    
    -- Content (compressed)
    messages JSONB,
    response TEXT,
    
    -- Model parameters
    temperature DECIMAL(3, 2),
    max_tokens INTEGER,
    top_p DECIMAL(3, 2),
    
    -- Status and flags
    status VARCHAR(20),
    error_message TEXT,
    has_error BOOLEAN DEFAULT FALSE,
    pii_detected BOOLEAN DEFAULT FALSE,
    
    -- Indexes for common queries
    PRIMARY KEY (id, time)
);

-- Convert to hypertable
SELECT create_hypertable('llm_events', 'time');

-- Create indexes
CREATE INDEX idx_tenant_project_time ON llm_events (tenant_id, project_id, time DESC);
CREATE INDEX idx_model_provider ON llm_events (model, provider, time DESC);
CREATE INDEX idx_user_session ON llm_events (user_id, session_id, time DESC);

-- Continuous aggregates for fast analytics
CREATE MATERIALIZED VIEW hourly_stats
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', time) AS hour,
    tenant_id,
    project_id,
    model,
    COUNT(*) as request_count,
    SUM(cost_usd) as total_cost,
    AVG(latency_ms) as avg_latency,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms) as p50_latency,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_latency,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99_latency,
    SUM(tokens_total) as total_tokens,
    COUNT(*) FILTER (WHERE has_error = true) as error_count
FROM llm_events
GROUP BY hour, tenant_id, project_id, model;

-- Daily aggregates
CREATE MATERIALIZED VIEW daily_stats
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', time) AS day,
    tenant_id,
    project_id,
    SUM(cost_usd) as daily_cost,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(*) as total_requests
FROM llm_events
GROUP BY day, tenant_id, project_id;

-- Alerts configuration
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255),
    condition JSONB NOT NULL,
    actions JSONB NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Alert history
CREATE TABLE alert_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
    triggered_at TIMESTAMPTZ DEFAULT NOW(),
    event_data JSONB,
    status VARCHAR(50)
);