"""Add TimescaleDB hypertable and aggregates

Revision ID: 67aa717b7457
Revises: ebb440b41de1
Create Date: 2025-10-04 16:25:09.721893

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67aa717b7457'
down_revision: Union[str, None] = 'ebb440b41de1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert llm_events to hypertable
    op.execute("""
        SELECT create_hypertable('llm_events', 'time', 
            chunk_time_interval => INTERVAL '1 day',
            if_not_exists => TRUE
        );
    """)
    
    # Create indexes
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_tenant_project_time 
        ON llm_events (tenant_id, project_id, time DESC);
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_model_provider 
        ON llm_events (model, provider, time DESC);
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_session 
        ON llm_events (user_id, session_id, time DESC);
    """)
    
     # ⬇️ NEW: Create materialized views OUTSIDE transaction
    connection = op.get_bind()
    
    # Commit the transaction before creating materialized views
    connection.execute(sa.text("COMMIT;"))
    
    # Now create the materialized views outside transaction
    connection.execution_options(isolation_level="AUTOCOMMIT").execute(sa.text("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS hourly_stats
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
    """))
    
    connection.execution_options(isolation_level="AUTOCOMMIT").execute(sa.text("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS daily_stats
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
    """))

def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS daily_stats;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS hourly_stats;")
    op.execute("DROP INDEX IF EXISTS idx_user_session;")
    op.execute("DROP INDEX IF EXISTS idx_model_provider;")
    op.execute("DROP INDEX IF EXISTS idx_tenant_project_time;")
    # Note: Can't easily revert hypertable conversion
