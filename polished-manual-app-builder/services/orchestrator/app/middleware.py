import time
import uuid
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import structlog
from prometheus_client import Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = structlog.get_logger(__name__)

# Prometheus metrics
request_count = Counter(
    'orchestrator_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

request_duration = Histogram(
    'orchestrator_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

model_requests = Counter(
    'orchestrator_model_requests_total',
    'Total number of model requests',
    ['model', 'provider', 'status']
)

cache_operations = Counter(
    'orchestrator_cache_operations_total',
    'Total number of cache operations',
    ['operation', 'result']
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Add request ID to context
        request.state.request_id = request_id

        # Log request
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            user_agent=request.headers.get("user-agent"),
            client_ip=request.client.host if request.client else None,
        )

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Log response
            logger.info(
                "Request completed",
                request_id=request_id,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
            )

            return response

        except Exception as exc:
            duration = time.time() - start_time
            logger.error(
                "Request failed",
                request_id=request_id,
                error=str(exc),
                duration_ms=round(duration * 1000, 2),
            )
            raise


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for Prometheus metrics collection."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        method = request.method
        endpoint = self._get_endpoint(request)

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Record metrics
            request_count.labels(
                method=method,
                endpoint=endpoint,
                status_code=response.status_code
            ).inc()

            request_duration.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            return response

        except Exception as exc:
            duration = time.time() - start_time
            
            request_count.labels(
                method=method,
                endpoint=endpoint,
                status_code=500
            ).inc()

            request_duration.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            raise

    def _get_endpoint(self, request: Request) -> str:
        """Extract endpoint pattern from request."""
        if hasattr(request, 'route') and request.route:
            return request.route.path
        return request.url.path


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for global error handling."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except ValueError as exc:
            logger.error("Validation error", error=str(exc))
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Bad Request",
                    "message": str(exc),
                    "request_id": getattr(request.state, "request_id", None),
                }
            )
        except TimeoutError as exc:
            logger.error("Timeout error", error=str(exc))
            return JSONResponse(
                status_code=408,
                content={
                    "error": "Request Timeout",
                    "message": "The request took too long to process",
                    "request_id": getattr(request.state, "request_id", None),
                }
            )
        except Exception as exc:
            logger.error("Unexpected error", error=str(exc), exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                    "request_id": getattr(request.state, "request_id", None),
                }
            )


def get_metrics() -> str:
    """Get Prometheus metrics in text format."""
    return generate_latest().decode('utf-8')
