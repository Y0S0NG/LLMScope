"""Seed default tenant and project

Revision ID: 003_seed_default
Revises: 67aa717b7457
Create Date: 2025-10-05 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision: str = '003_seed_default'
down_revision: Union[str, None] = '67aa717b7457'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed default tenant and project for single-tenant mode"""

    # Generate consistent UUIDs for default tenant and project
    default_tenant_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'llmscope.default.tenant'))
    default_project_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'llmscope.default.project'))

    # Insert default tenant (idempotent with ON CONFLICT DO NOTHING)
    op.execute(f"""
        INSERT INTO tenants (id, name, api_key, plan, settings, usage_limits)
        VALUES (
            '{default_tenant_id}'::uuid,
            'Default Tenant',
            'llmscope-local-key',
            'self_hosted',
            '{{}}'::jsonb,
            '{{"requests": -1, "cost": -1}}'::jsonb
        )
        ON CONFLICT (id) DO NOTHING;
    """)

    # Insert default project (idempotent)
    op.execute(f"""
        INSERT INTO projects (id, tenant_id, name, settings)
        VALUES (
            '{default_project_id}'::uuid,
            '{default_tenant_id}'::uuid,
            'Main Project',
            '{{}}'::jsonb
        )
        ON CONFLICT (id) DO NOTHING;
    """)


def downgrade() -> None:
    """Remove default tenant and project"""
    default_tenant_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'llmscope.default.tenant'))
    default_project_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'llmscope.default.project'))

    op.execute(f"DELETE FROM projects WHERE id = '{default_project_id}'::uuid;")
    op.execute(f"DELETE FROM tenants WHERE id = '{default_tenant_id}'::uuid;")
