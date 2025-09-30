#!/usr/bin/env python3
"""
Enhanced Error Monitoring HTTP Server
Receives errors from all services and triggers learning system
"""

import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass
import aiohttp
from aiohttp import web, ClientSession
import aiofiles
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ErrorEvent:
    timestamp: str
    service: str
    context: str
    error_type: str
    error_message: str
    severity: str
    stack_trace: str = None
    additional_data: Dict[str, Any] = None

class ErrorMonitorServer:
    """HTTP server to receive and process errors from all services"""
    
    def __init__(self):
        self.logs_dir = Path("logs/errors")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.error_queue = asyncio.Queue()
        self.learning_engine_path = Path("scripts/error_learning_engine.py")
        
        # Error processing statistics
        self.stats = {
            "total_errors_received": 0,
            "errors_by_service": {},
            "errors_by_severity": {},
            "learning_runs": 0,
            "last_learning_run": None
        }
    
    async def start_server(self, host="0.0.0.0", port=8090):
        """Start the error monitoring HTTP server"""
        app = web.Application()
        
        # Error ingestion endpoints
        app.router.add_post('/errors', self.receive_error)
        app.router.add_post('/errors/batch', self.receive_batch_errors)
        
        # Status and analytics endpoints
        app.router.add_get('/status', self.get_status)
        app.router.add_get('/stats', self.get_stats)
        app.router.add_get('/analytics', self.get_analytics)
        
        # Control endpoints
        app.router.add_post('/trigger-learning', self.trigger_learning)
        app.router.add_post('/reset-stats', self.reset_stats)
        
        # Health check
        app.router.add_get('/health', self.health_check)
        
        # Start background tasks
        asyncio.create_task(self.error_processor())
        asyncio.create_task(self.periodic_learning())
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"Error monitoring server started on {host}:{port}")
        return runner
    
    async def receive_error(self, request):
        """Receive a single error event"""
        try:
            data = await request.json()
            
            # Validate required fields
            required_fields = ['service', 'context', 'error_type', 'error_message', 'severity']
            for field in required_fields:
                if field not in data:
                    return web.json_response(
                        {"error": f"Missing required field: {field}"}, 
                        status=400
                    )
            
            # Create error event
            error_event = ErrorEvent(
                timestamp=data.get('timestamp', datetime.utcnow().isoformat()),
                service=data['service'],
                context=data['context'],
                error_type=data['error_type'],
                error_message=data['error_message'],
                severity=data['severity'],
                stack_trace=data.get('stack_trace'),
                additional_data=data.get('additional_data', {})
            )
            
            # Queue for processing
            await self.error_queue.put(error_event)
            
            # Update statistics
            self.stats["total_errors_received"] += 1
            self.stats["errors_by_service"][error_event.service] = \
                self.stats["errors_by_service"].get(error_event.service, 0) + 1
            self.stats["errors_by_severity"][error_event.severity] = \
                self.stats["errors_by_severity"].get(error_event.severity, 0) + 1
            
            logger.info(f"Received error from {error_event.service}: {error_event.error_type}")
            
            return web.json_response({
                "status": "received",
                "timestamp": error_event.timestamp
            })
            
        except Exception as e:
            logger.error(f"Error receiving error event: {e}")
            return web.json_response(
                {"error": "Failed to process error event"}, 
                status=500
            )
    
    async def receive_batch_errors(self, request):
        """Receive multiple error events in batch"""
        try:
            data = await request.json()
            errors = data.get('errors', [])
            
            received_count = 0
            for error_data in errors:
                try:
                    error_event = ErrorEvent(
                        timestamp=error_data.get('timestamp', datetime.utcnow().isoformat()),
                        service=error_data['service'],
                        context=error_data['context'],
                        error_type=error_data['error_type'],
                        error_message=error_data['error_message'],
                        severity=error_data['severity'],
                        stack_trace=error_data.get('stack_trace'),
                        additional_data=error_data.get('additional_data', {})
                    )
                    
                    await self.error_queue.put(error_event)
                    received_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing batch item: {e}")
            
            self.stats["total_errors_received"] += received_count
            
            return web.json_response({
                "status": "received",
                "processed_count": received_count,
                "total_count": len(errors)
            })
            
        except Exception as e:
            logger.error(f"Error receiving batch errors: {e}")
            return web.json_response(
                {"error": "Failed to process batch errors"}, 
                status=500
            )
    
    async def error_processor(self):
        """Background task to process queued errors"""
        while True:
            try:
                # Wait for error events
                error_event = await self.error_queue.get()
                
                # Save to log file
                await self.save_error_log(error_event)
                
                # Add to pending patterns for learning
                await self.add_to_pending_patterns(error_event)
                
                # Mark task as done
                self.error_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing error event: {e}")
    
    async def save_error_log(self, error_event: ErrorEvent):
        """Save error to structured log file"""
        log_file = self.logs_dir / f"{error_event.service}-errors.jsonl"
        
        error_dict = {
            "timestamp": error_event.timestamp,
            "service": error_event.service,
            "context": error_event.context,
            "error_type": error_event.error_type,
            "error_message": error_event.error_message,
            "severity": error_event.severity,
            "stack_trace": error_event.stack_trace,
            "additional_data": error_event.additional_data
        }
        
        async with aiofiles.open(log_file, "a") as f:
            await f.write(json.dumps(error_dict) + "\n")
    
    async def add_to_pending_patterns(self, error_event: ErrorEvent):
        """Add error to pending patterns for learning system"""
        import hashlib
        
        pattern_data = f"{error_event.error_type}{error_event.error_message}"
        pattern_hash = hashlib.md5(pattern_data.encode()).hexdigest()
        
        error_pattern = {
            "pattern_hash": pattern_hash,
            "error_type": error_event.error_type,
            "service": error_event.service,
            "context": error_event.context,
            "message": error_event.error_message,
            "first_seen": error_event.timestamp,
            "last_seen": error_event.timestamp,
            "occurrence_count": 1,
            "resolved": False,
            "solution": None,
            "prevention_tips": [],
            "related_errors": [],
            "severity": error_event.severity
        }
        
        pending_file = self.logs_dir / "pending-error-patterns.jsonl"
        async with aiofiles.open(pending_file, "a") as f:
            await f.write(json.dumps(error_pattern) + "\n")
    
    async def periodic_learning(self):
        """Periodically trigger the learning engine"""
        while True:
            try:
                # Wait 5 minutes between learning runs
                await asyncio.sleep(300)
                
                # Check if there are pending patterns to process
                pending_file = self.logs_dir / "pending-error-patterns.jsonl"
                if pending_file.exists() and pending_file.stat().st_size > 0:
                    await self.run_learning_engine()
                
            except Exception as e:
                logger.error(f"Error in periodic learning: {e}")
    
    async def run_learning_engine(self):
        """Run the error learning engine"""
        try:
            logger.info("Running error learning engine...")
            
            process = await asyncio.create_subprocess_exec(
                "python", str(self.learning_engine_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info("Learning engine completed successfully")
                self.stats["learning_runs"] += 1
                self.stats["last_learning_run"] = datetime.utcnow().isoformat()
            else:
                logger.error(f"Learning engine failed: {stderr.decode()}")
                
        except Exception as e:
            logger.error(f"Error running learning engine: {e}")
    
    async def get_status(self, request):
        """Get server status"""
        return web.json_response({
            "status": "running",
            "timestamp": datetime.utcnow().isoformat(),
            "queue_size": self.error_queue.qsize(),
            "logs_directory": str(self.logs_dir)
        })
    
    async def get_stats(self, request):
        """Get error processing statistics"""
        return web.json_response(self.stats)
    
    async def get_analytics(self, request):
        """Get analytics from the learning engine"""
        try:
            analytics_file = self.logs_dir / "analytics_report.json"
            if analytics_file.exists():
                async with aiofiles.open(analytics_file, 'r') as f:
                    analytics_data = json.loads(await f.read())
                return web.json_response(analytics_data)
            else:
                return web.json_response({"error": "Analytics not available"}, status=404)
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return web.json_response({"error": "Failed to get analytics"}, status=500)
    
    async def trigger_learning(self, request):
        """Manually trigger learning engine"""
        try:
            await self.run_learning_engine()
            return web.json_response({"status": "learning_triggered"})
        except Exception as e:
            logger.error(f"Error triggering learning: {e}")
            return web.json_response({"error": "Failed to trigger learning"}, status=500)
    
    async def reset_stats(self, request):
        """Reset statistics"""
        self.stats = {
            "total_errors_received": 0,
            "errors_by_service": {},
            "errors_by_severity": {},
            "learning_runs": 0,
            "last_learning_run": None
        }
        return web.json_response({"status": "stats_reset"})
    
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        })


async def main():
    """Main function to start the error monitoring server"""
    server = ErrorMonitorServer()
    runner = await server.start_server()
    
    try:
        # Keep the server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down error monitoring server...")
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
