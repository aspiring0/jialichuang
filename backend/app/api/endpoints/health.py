"""
Health Check Endpoints
"""

from datetime import datetime
from typing import Dict

import redis
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str
    timestamp: str
    version: str
    services: Dict[str, str]


class ServiceHealth(BaseModel):
    """Individual service health model"""

    status: str
    message: str = ""


@router.get("", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check endpoint.
    Checks all connected services status.
    """
    services = {}

    # Check PostgreSQL
    try:
        result = await db.execute(text("SELECT 1"))
        result.fetchone()
        services["postgresql"] = "healthy"
    except Exception as e:
        services["postgresql"] = f"unhealthy: {str(e)[:50]}"

    # Check Redis
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        services["redis"] = "healthy"
        redis_client.close()
    except Exception as e:
        services["redis"] = f"unhealthy: {str(e)[:50]}"

    # Check RabbitMQ (basic check via HTTP)
    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://{settings.RABBITMQ_HOST}:15672/api/overview",
                auth=(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD),
                timeout=5.0,
            )
            if response.status_code == 200:
                services["rabbitmq"] = "healthy"
            else:
                services["rabbitmq"] = f"unhealthy: status {response.status_code}"
    except Exception as e:
        services["rabbitmq"] = f"unhealthy: {str(e)[:50]}"

    # Check MinIO
    try:
        from minio import Minio

        minio_client = Minio(
            f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        minio_client.list_buckets()
        services["minio"] = "healthy"
    except Exception as e:
        services["minio"] = f"unhealthy: {str(e)[:50]}"

    # Determine overall status
    all_healthy = all(v == "healthy" for v in services.values())
    overall_status = "healthy" if all_healthy else "degraded"

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version="0.1.0",
        services=services,
    )


@router.get("/live")
async def liveness():
    """Kubernetes liveness probe endpoint"""
    return {"status": "alive"}


@router.get("/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    """Kubernetes readiness probe endpoint"""
    try:
        # Check database connection
        await db.execute(text("SELECT 1"))

        # Check Redis
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()
        redis_client.close()

        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}",
        )