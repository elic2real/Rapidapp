import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.config import settings
from app.database import engine, create_tables
from app.cache import redis_client
from app.telemetry import setup_telemetry
from app.routes import health, orchestration, cache, admin
from app.middleware import (
    LoggingMiddleware,
    MetricsMiddleware,
    ErrorHandlerMiddleware,
)

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Starting AI Orchestrator service")
    
    # Initialize telemetry
    setup_telemetry()
    
    # Create database tables
    await create_tables()
    
    # Test Redis connection
    try:
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error("Failed to connect to Redis", error=str(e))
        raise
    
    # Initialize semantic cache
    from app.services.semantic_cache import semantic_cache
    await semantic_cache.initialize()
    
    # Load models if configured
    from app.services.model_manager import model_manager
    await model_manager.initialize()
    
    logger.info("AI Orchestrator service started successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down AI Orchestrator service")
    await redis_client.close()
    await engine.dispose()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AI Orchestrator",
        description="AI orchestration service with semantic caching and model routing",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.development else None,
        redoc_url="/redoc" if settings.development else None,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add custom middleware
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(LoggingMiddleware)

    # Include routers
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(orchestration.router, prefix="/v1", tags=["orchestration"])
    app.include_router(cache.router, prefix="/cache", tags=["cache"])
    app.include_router(admin.router, prefix="/admin", tags=["admin"])

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        log_level="info",
        reload=settings.development,
    )
