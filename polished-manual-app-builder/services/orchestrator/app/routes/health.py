from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.database import get_db
from app.models import HealthStatus, ModelInfo
from app.services.model_manager import model_manager
from app.services.semantic_cache import semantic_cache
from app.cache import redis_client

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=HealthStatus)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check."""
    services = {}
    
    # Check database
    try:
        await db.execute("SELECT 1")
        services["database"] = True
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        services["database"] = False
    
    # Check Redis
    try:
        await redis_client.ping()
        services["redis"] = True
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        services["redis"] = False
    
    # Check semantic cache
    try:
        services["semantic_cache"] = semantic_cache.initialized
    except Exception:
        services["semantic_cache"] = False
    
    # Get available models
    models = []
    try:
        models = await model_manager.get_all_models()
        services["model_manager"] = True
    except Exception as e:
        logger.error("Model manager health check failed", error=str(e))
        services["model_manager"] = False
    
    # Determine overall status
    overall_status = "healthy" if all(services.values()) else "degraded"
    
    return HealthStatus(
        status=overall_status,
        version="1.0.0",
        services=services,
        models=models
    )


@router.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe."""
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}
