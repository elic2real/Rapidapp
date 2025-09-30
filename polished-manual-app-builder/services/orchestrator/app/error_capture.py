import json
import traceback
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import aiofiles
import httpx
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger()

class ErrorCapture:
    """Captures and analyzes errors for automatic learning and guide updates"""
    
    def __init__(self):
        self.log_dir = Path("../../logs/errors")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.service_name = "ai-orchestrator"
        
    async def log_error(
        self, 
        error: Exception, 
        context: str, 
        request: Optional[Request] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Log error with full context for analysis and learning"""
        
        error_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "context": context,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "severity": self._determine_severity(error),
            "stack_trace": traceback.format_exc(),
            "additional_data": additional_data or {},
            "environment": self._get_environment(),
            "version": "1.0.0",
        }
        
        # Add request context if available
        if request:
            error_log["request"] = {
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client_ip": request.client.host if request.client else None,
            }
        
        # Log to structured error file
        await self._write_error_log(error_log)
        
        # Send to error monitoring system
        await self._send_to_monitor(error_log)
        
        # Update error guide if this is a new pattern
        await self._update_error_guide(error_log)
        
        # Log to application logger
        logger.error(
            "Error captured",
            error_type=error_log["error_type"],
            context=context,
            severity=error_log["severity"]
        )
    
    def _determine_severity(self, error: Exception) -> str:
        """Determine error severity based on error type"""
        if isinstance(error, (ConnectionError, TimeoutError)):
            return "high"
        elif isinstance(error, HTTPException):
            if error.status_code >= 500:
                return "high"
            elif error.status_code >= 400:
                return "medium"
            else:
                return "low"
        elif isinstance(error, (ValueError, TypeError)):
            return "medium"
        elif isinstance(error, (FileNotFoundError, PermissionError)):
            return "high"
        else:
            return "medium"
    
    def _get_environment(self) -> str:
        """Get current environment"""
        import os
        return os.getenv("ENVIRONMENT", "development")
    
    async def _write_error_log(self, error_log: Dict[str, Any]):
        """Write error to JSONL log file"""
        log_file = self.log_dir / f"{self.service_name}-errors.jsonl"
        
        try:
            async with aiofiles.open(log_file, "a") as f:
                await f.write(json.dumps(error_log) + "\n")
        except Exception as e:
            logger.error(f"Failed to write error log: {e}")
    
    async def _send_to_monitor(self, error_log: Dict[str, Any]):
        """Send error to monitoring system"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    "http://localhost:8090/errors",
                    json=error_log
                )
        except Exception as e:
            logger.warning(f"Failed to send error to monitor: {e}")
    
    async def _update_error_guide(self, error_log: Dict[str, Any]):
        """Update error guide with new error patterns"""
        try:
            # Create error pattern hash for deduplication
            pattern_data = f"{error_log['error_type']}{error_log['error_message']}"
            pattern_hash = hashlib.md5(pattern_data.encode()).hexdigest()
            
            new_error_entry = {
                "pattern_hash": pattern_hash,
                "error_type": error_log["error_type"],
                "service": error_log["service"],
                "context": error_log["context"],
                "message": error_log["error_message"],
                "first_seen": error_log["timestamp"],
                "last_seen": error_log["timestamp"],
                "occurrence_count": 1,
                "resolved": False,
                "solution": None,
                "prevention_tips": [],
                "related_errors": [],
                "severity": error_log["severity"]
            }
            
            # Write to pending errors file for review and integration
            pending_file = self.log_dir / "pending-error-patterns.jsonl"
            async with aiofiles.open(pending_file, "a") as f:
                await f.write(json.dumps(new_error_entry) + "\n")
                
        except Exception as e:
            logger.error(f"Failed to update error guide: {e}")


# Global error capture instance
error_capture = ErrorCapture()


async def error_capture_middleware(request: Request, call_next):
    """FastAPI middleware to capture all errors"""
    try:
        response = await call_next(request)
        return response
    except Exception as error:
        # Capture the error
        await error_capture.log_error(
            error=error,
            context=f"{request.method} {request.url.path}",
            request=request
        )
        
        # Return appropriate error response
        if isinstance(error, HTTPException):
            raise error
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )


class ErrorCaptureHandler:
    """Handler for manual error capture in specific contexts"""
    
    @staticmethod
    async def capture_ollama_error(error: Exception, model: str, prompt: str):
        """Capture Ollama-specific errors with context"""
        await error_capture.log_error(
            error=error,
            context="ollama_inference",
            additional_data={
                "model": model,
                "prompt_length": len(prompt),
                "ollama_endpoint": "http://localhost:11434"
            }
        )
    
    @staticmethod
    async def capture_cache_error(error: Exception, operation: str, key: str):
        """Capture cache-related errors"""
        await error_capture.log_error(
            error=error,
            context=f"cache_{operation}",
            additional_data={
                "cache_key": key,
                "operation": operation
            }
        )
    
    @staticmethod
    async def capture_model_error(error: Exception, model_id: str, operation: str):
        """Capture model management errors"""
        await error_capture.log_error(
            error=error,
            context=f"model_{operation}",
            additional_data={
                "model_id": model_id,
                "operation": operation
            }
        )
