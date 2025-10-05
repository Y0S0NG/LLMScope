"""Dependency injection"""
from fastapi import Depends, HTTPException, Header
from typing import Optional
from sqlalchemy.orm import Session
from .config import settings
from .db.base import get_db as get_db_session
from .db.models import Tenant, Project


# Cache for default tenant/project to avoid repeated DB queries
_default_tenant_cache: Optional[Tenant] = None
_default_project_cache: Optional[Project] = None


async def get_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Validate API key from header"""
    # In single-tenant mode with auth enabled
    if settings.single_tenant_mode and settings.require_auth:
        if not x_api_key:
            raise HTTPException(status_code=401, detail="API key required")
        if x_api_key != settings.api_key:
            raise HTTPException(status_code=401, detail="Invalid API key")
        return x_api_key

    # In single-tenant mode without auth
    if settings.single_tenant_mode and not settings.require_auth:
        return settings.api_key

    # Multi-tenant mode (TODO: implement later)
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    # TODO: Validate against database and get tenant
    return x_api_key


def get_db():
    """Get database session"""
    db = next(get_db_session())
    try:
        yield db
    finally:
        db.close()


async def get_current_tenant(
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
) -> Tenant:
    """Get current tenant (default tenant in single-tenant mode)"""
    global _default_tenant_cache

    if settings.single_tenant_mode:
        # Use cached tenant if available
        if _default_tenant_cache is not None:
            return _default_tenant_cache

        # Query default tenant
        tenant = db.query(Tenant).filter(Tenant.id == settings.default_tenant_id).first()
        if not tenant:
            raise HTTPException(
                status_code=500,
                detail="Default tenant not found. Run database migrations."
            )

        _default_tenant_cache = tenant
        return tenant

    # Multi-tenant mode (TODO: implement later)
    # Look up tenant from api_key
    raise HTTPException(status_code=501, detail="Multi-tenant mode not implemented yet")


async def get_current_project(
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
) -> Project:
    """Get current project (default project in single-tenant mode)"""
    global _default_project_cache

    if settings.single_tenant_mode:
        # Use cached project if available
        if _default_project_cache is not None:
            return _default_project_cache

        # Query default project
        project = db.query(Project).filter(
            Project.id == settings.default_project_id,
            Project.tenant_id == tenant.id
        ).first()

        if not project:
            raise HTTPException(
                status_code=500,
                detail="Default project not found. Run database migrations."
            )

        _default_project_cache = project
        return project

    # Multi-tenant mode (TODO: implement later)
    # Look up project from tenant and request context
    raise HTTPException(status_code=501, detail="Multi-tenant mode not implemented yet")
