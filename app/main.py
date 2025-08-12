"""
Elevate Team Formation App - FastAPI Main Application
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import engine
from app.shared.infrastructure.database import Base
from app.shared.presentation.middleware.tenant_middleware import TenantMiddleware

# Import all domain routers
from app.tenancy.presentation.api import router as tenancy_router
from app.users.presentation.api import router as users_router
from app.courses.presentation.api import router as courses_router
from app.questionnaires.presentation.api import router as questionnaires_router
from app.team_formation.presentation.api import router as team_formation_router
from app.analytics.presentation.api import router as analytics_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management."""
    # Startup
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title="Elevate - Team Formation App",
    description="AI-powered team formation system for educational institutions",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add tenant isolation middleware
app.add_middleware(TenantMiddleware)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "elevate-api",
            "version": "1.0.0"
        }
    )

# Include routers
app.include_router(tenancy_router, prefix="/api/v1/tenancy", tags=["tenancy"])
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(courses_router, prefix="/api/v1", tags=["courses"])  # Courses router includes /courses prefix
app.include_router(questionnaires_router, prefix="/api/v1/questionnaires", tags=["questionnaires"])
app.include_router(team_formation_router, prefix="/api/v1/teams", tags=["team-formation"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Elevate - Team Formation App",
        "docs": "/docs",
        "health": "/health"
    }
