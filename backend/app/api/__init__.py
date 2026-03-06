"""
API Routes
"""

from fastapi import APIRouter

from app.api.endpoints import health, sessions, tasks

api_router = APIRouter()

# Include all API endpoints
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])