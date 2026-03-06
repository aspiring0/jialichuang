"""
Multi-Agent Data Analysis Assistant
FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api import api_router
from app.config import settings
from app.database import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print(f"🚀 Starting {settings.APP_NAME}...")
    print(f"📊 Environment: {settings.APP_ENV}")
    
    # Initialize database tables
    await init_db()
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("🔄 Shutting down...")
    await close_db()
    print("👋 Goodbye!")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
## Multi-Agent Data Analysis Assistant

A production-grade, self-driven multi-agent data analysis assistant.

### Features
- 🤖 Natural language interaction
- 📊 Automatic data analysis
- 📈 Visualization generation
- 🔒 Secure sandbox execution

### Architecture
- Coordinator Agent: Task orchestration
- Data Parser Agent: Data parsing and cleaning
- Analysis Agent: Statistical analysis and ML
- Visualization Agent: Chart generation
- Debugger Agent: Error recovery
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Mount Prometheus metrics endpoint
if settings.ENABLE_METRICS:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.APP_NAME,
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )