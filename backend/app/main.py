"""FastAPI app entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text

from .config import settings
from .db.base import engine, SessionLocal
from .db.models import Tenant, Project
from .api import events, analytics, alerts, auth, websocket


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
