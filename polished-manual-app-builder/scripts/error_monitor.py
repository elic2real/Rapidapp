#!/usr/bin/env python3
"""
Polished Manual App Builder - Automated Error Monitor
Comprehensive error detection, logging, and alerting system
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import aiohttp
import psutil
import docker
import argparse
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('error_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"

@dataclass
class ErrorLog:
    timestamp: str
    error_id: str
    service: str
    severity: ErrorSeverity
    error_type: str
    message: str
    details: Dict[str, Any]
    resolution_steps: List[str]
    resolved: bool = False
    resolution_time: Optional[str] = None

@dataclass
class ServiceHealth:
    service: str
    status: ServiceStatus
    url: str
    response_time: Optional[float]
    error_message: Optional[str]
    last_check: str

class ErrorMonitor:
    def __init__(self, config_path: str = "error_monitor_config.json"):
        self.config = self.load_config(config_path)
        self.docker_client = docker.from_env()
        self.error_log: List[ErrorLog] = []
        self.service_health: Dict[str, ServiceHealth] = {}
        self.running = False
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "services": {
                "event-store": {
                    "url": "http://localhost:8080/health",
                    "container_name": "polished-manual-app-builder-event-store-1",
                    "critical": True
                },
                "orchestrator": {
                    "url": "http://localhost:8001/health", 
                    "container_name": "polished-manual-app-builder-orchestrator-1",
                    "critical": True
                },
                "collab-engine": {
                    "url": "http://localhost:8003/health",
                    "container_name": "polished-manual-app-builder-collab-engine-1", 
                    "critical": True
                },
                "postgres": {
                    "container_name": "polished-manual-app-builder-postgres-1",
                    "critical": True
                },
                "redis": {
                    "container_name": "polished-manual-app-builder-redis-1",
                    "critical": False
                }
            },
            "monitoring": {
                "check_interval": 30,
                "response_timeout": 10,
                "max_response_time": 5.0,
                "memory_threshold": 80,
                "cpu_threshold": 80,
                "disk_threshold": 90
            },
            "alerting": {
                "enabled": True,
                "webhook_url": None,
                "email_enabled": False,
                "email_smtp": None
            }
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config

    async def check_service_health(self, service_name: str, service_config: Dict[str, Any]) -> ServiceHealth:
        """Check health of a specific service"""
        health = ServiceHealth(
            service=service_name,
            status=ServiceStatus.UNKNOWN,
            url=service_config.get("url", ""),
            response_time=None,
            error_message=None,
            last_check=datetime.utcnow().isoformat()
        )
        
        # Check container status first
        container_name = service_config.get("container_name")
        if container_name:
            try:
                container = self.docker_client.containers.get(container_name)
                if container.status != "running":
                    health.status = ServiceStatus.DOWN
                    health.error_message = f"Container status: {container.status}"
                    return health
            except docker.errors.NotFound:
                health.status = ServiceStatus.DOWN
                health.error_message = "Container not found"
                return health
            except Exception as e:
                health.error_message = f"Docker check failed: {str(e)}"
        
        # Check HTTP health endpoint if available
        if service_config.get("url"):
            try:
                timeout = aiohttp.ClientTimeout(total=self.config["monitoring"]["response_timeout"])
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    start_time = time.time()
                    async with session.get(service_config["url"]) as response:
                        health.response_time = time.time() - start_time
                        
                        if response.status == 200:
                            if health.response_time > self.config["monitoring"]["max_response_time"]:
                                health.status = ServiceStatus.DEGRADED
                                health.error_message = f"Slow response: {health.response_time:.2f}s"
                            else:
                                health.status = ServiceStatus.HEALTHY
                        else:
                            health.status = ServiceStatus.DEGRADED
                            health.error_message = f"HTTP {response.status}"
                            
            except asyncio.TimeoutError:
                health.status = ServiceStatus.DOWN
                health.error_message = "Request timeout"
            except Exception as e:
                health.status = ServiceStatus.DOWN
                health.error_message = f"Connection failed: {str(e)}"
        else:
            # No HTTP endpoint, just check container
            health.status = ServiceStatus.HEALTHY if container.status == "running" else ServiceStatus.DOWN
            
        return health

    def check_system_resources(self) -> List[ErrorLog]:
        """Check system resource usage"""
        errors = []
        
        # Check memory usage
        memory = psutil.virtual_memory()
        if memory.percent > self.config["monitoring"]["memory_threshold"]:
            errors.append(ErrorLog(
                timestamp=datetime.utcnow().isoformat(),
                error_id=f"SYS-MEM-{int(time.time())}",
                service="system",
                severity=ErrorSeverity.HIGH if memory.percent > 90 else ErrorSeverity.MEDIUM,
                error_type="high_memory_usage",
                message=f"High memory usage: {memory.percent:.1f}%",
                details={
                    "memory_percent": memory.percent,
                    "available_gb": memory.available / (1024**3),
                    "total_gb": memory.total / (1024**3)
                },
                resolution_steps=[
                    "docker system prune -f",
                    "Restart memory-intensive services",
                    "Check for memory leaks in applications"
                ]
            ))
        
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > self.config["monitoring"]["cpu_threshold"]:
            errors.append(ErrorLog(
                timestamp=datetime.utcnow().isoformat(),
                error_id=f"SYS-CPU-{int(time.time())}",
                service="system",
                severity=ErrorSeverity.HIGH if cpu_percent > 95 else ErrorSeverity.MEDIUM,
                error_type="high_cpu_usage",
                message=f"High CPU usage: {cpu_percent:.1f}%",
                details={
                    "cpu_percent": cpu_percent,
                    "cpu_count": psutil.cpu_count()
                },
                resolution_steps=[
                    "Identify CPU-intensive processes with 'top' or 'htop'",
                    "Scale services horizontally",
                    "Optimize algorithms in hot paths"
                ]
            ))
        
        # Check disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        if disk_percent > self.config["monitoring"]["disk_threshold"]:
            errors.append(ErrorLog(
                timestamp=datetime.utcnow().isoformat(),
                error_id=f"SYS-DISK-{int(time.time())}",
                service="system",
                severity=ErrorSeverity.CRITICAL if disk_percent > 95 else ErrorSeverity.HIGH,
                error_type="high_disk_usage",
                message=f"High disk usage: {disk_percent:.1f}%",
                details={
                    "disk_percent": disk_percent,
                    "free_gb": disk.free / (1024**3),
                    "total_gb": disk.total / (1024**3)
                },
                resolution_steps=[
                    "docker system prune -a --volumes",
                    "Clean application logs",
                    "Remove unused Docker images and containers"
                ]
            ))
        
        return errors

    def check_docker_containers(self) -> List[ErrorLog]:
        """Check Docker container status and resource usage"""
        errors = []
        
        try:
            containers = self.docker_client.containers.list(all=True)
            
            for container in containers:
                if not container.name.startswith("polished-manual-app-builder"):
                    continue
                    
                # Check container status
                if container.status != "running":
                    errors.append(ErrorLog(
                        timestamp=datetime.utcnow().isoformat(),
                        error_id=f"DOCKER-STATUS-{container.short_id}",
                        service=container.name,
                        severity=ErrorSeverity.CRITICAL,
                        error_type="container_down",
                        message=f"Container {container.name} is {container.status}",
                        details={
                            "container_id": container.short_id,
                            "status": container.status,
                            "image": container.image.tags[0] if container.image.tags else "unknown"
                        },
                        resolution_steps=[
                            "docker compose up -d",
                            f"docker logs {container.name}",
                            "Check service dependencies"
                        ]
                    ))
                    continue
                
                # Check container resource usage
                try:
                    stats = container.stats(stream=False)
                    
                    # Memory usage
                    memory_usage = stats['memory_stats']['usage']
                    memory_limit = stats['memory_stats']['limit']
                    memory_percent = (memory_usage / memory_limit) * 100
                    
                    if memory_percent > 90:
                        errors.append(ErrorLog(
                            timestamp=datetime.utcnow().isoformat(),
                            error_id=f"DOCKER-MEM-{container.short_id}",
                            service=container.name,
                            severity=ErrorSeverity.HIGH,
                            error_type="high_container_memory",
                            message=f"Container {container.name} high memory: {memory_percent:.1f}%",
                            details={
                                "container_id": container.short_id,
                                "memory_percent": memory_percent,
                                "memory_usage_mb": memory_usage / (1024**2),
                                "memory_limit_mb": memory_limit / (1024**2)
                            },
                            resolution_steps=[
                                f"docker restart {container.name}",
                                "Check for memory leaks",
                                "Increase memory limits in docker-compose.yml"
                            ]
                        ))
                        
                except Exception as e:
                    logger.warning(f"Failed to get stats for {container.name}: {e}")
                    
        except Exception as e:
            errors.append(ErrorLog(
                timestamp=datetime.utcnow().isoformat(),
                error_id=f"DOCKER-API-{int(time.time())}",
                service="docker",
                severity=ErrorSeverity.CRITICAL,
                error_type="docker_api_error",
                message=f"Docker API error: {str(e)}",
                details={"error": str(e)},
                resolution_steps=[
                    "Restart Docker Desktop",
                    "Check Docker daemon status",
                    "Verify Docker permissions"
                ]
            ))
        
        return errors

    async def send_alert(self, error: ErrorLog):
        """Send alert for critical errors"""
        if not self.config["alerting"]["enabled"]:
            return
            
        # Webhook alert
        webhook_url = self.config["alerting"]["webhook_url"]
        if webhook_url:
            try:
                alert_data = {
                    "text": f"🚨 {error.service.upper()} ERROR",
                    "attachments": [{
                        "color": "danger" if error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] else "warning",
                        "fields": [
                            {"title": "Service", "value": error.service, "short": True},
                            {"title": "Error Type", "value": error.error_type, "short": True},
                            {"title": "Severity", "value": error.severity.value, "short": True},
                            {"title": "Time", "value": error.timestamp, "short": True},
                            {"title": "Message", "value": error.message, "short": False}
                        ]
                    }]
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(webhook_url, json=alert_data) as response:
                        if response.status == 200:
                            logger.info(f"Alert sent for error {error.error_id}")
                        else:
                            logger.error(f"Failed to send alert: {response.status}")
                            
            except Exception as e:
                logger.error(f"Failed to send webhook alert: {e}")

    def save_error_log(self):
        """Save error log to file"""
        log_file = Path("error_log.json")
        
        # Load existing log
        existing_errors = []
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    existing_errors = [ErrorLog(**item) for item in json.load(f)]
            except Exception as e:
                logger.warning(f"Failed to load existing error log: {e}")
        
        # Merge with current errors
        all_errors = existing_errors + self.error_log
        
        # Keep only last 1000 errors
        if len(all_errors) > 1000:
            all_errors = all_errors[-1000:]
        
        # Save to file
        try:
            with open(log_file, 'w') as f:
                json.dump([asdict(error) for error in all_errors], f, indent=2)
            logger.info(f"Saved {len(all_errors)} errors to {log_file}")
        except Exception as e:
            logger.error(f"Failed to save error log: {e}")

    def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "services": {},
            "system_resources": {},
            "recent_errors": [],
            "recommendations": []
        }
        
        # Service health
        critical_down = 0
        for service_name, health in self.service_health.items():
            report["services"][service_name] = {
                "status": health.status.value,
                "response_time": health.response_time,
                "error_message": health.error_message,
                "last_check": health.last_check
            }
            
            if health.status == ServiceStatus.DOWN and self.config["services"][service_name].get("critical"):
                critical_down += 1
        
        # Overall status
        if critical_down > 0:
            report["overall_status"] = "critical"
        elif any(h.status == ServiceStatus.DEGRADED for h in self.service_health.values()):
            report["overall_status"] = "degraded"
        
        # System resources
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        report["system_resources"] = {
            "memory_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3),
            "cpu_percent": psutil.cpu_percent(),
            "disk_percent": (disk.used / disk.total) * 100,
            "disk_free_gb": disk.free / (1024**3)
        }
        
        # Recent errors (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        recent_errors = [
            error for error in self.error_log
            if datetime.fromisoformat(error.timestamp.replace('Z', '+00:00')) > cutoff_time
        ]
        report["recent_errors"] = [asdict(error) for error in recent_errors[-10:]]
        
        # Recommendations
        if memory.percent > 80:
            report["recommendations"].append("High memory usage detected. Consider scaling or optimizing services.")
        if disk.used / disk.total > 0.85:
            report["recommendations"].append("Disk space running low. Clean up Docker resources.")
        if critical_down > 0:
            report["recommendations"].append(f"{critical_down} critical services are down. Immediate attention required.")
        
        return report

    async def monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Starting error monitoring loop")
        
        while self.running:
            try:
                # Check service health
                for service_name, service_config in self.config["services"].items():
                    health = await self.check_service_health(service_name, service_config)
                    self.service_health[service_name] = health
                    
                    # Create error log for unhealthy services
                    if health.status in [ServiceStatus.DOWN, ServiceStatus.DEGRADED]:
                        severity = ErrorSeverity.CRITICAL if health.status == ServiceStatus.DOWN else ErrorSeverity.HIGH
                        error = ErrorLog(
                            timestamp=datetime.utcnow().isoformat(),
                            error_id=f"HEALTH-{service_name}-{int(time.time())}",
                            service=service_name,
                            severity=severity,
                            error_type="service_unhealthy",
                            message=f"{service_name} is {health.status.value}: {health.error_message}",
                            details={
                                "status": health.status.value,
                                "response_time": health.response_time,
                                "error_message": health.error_message
                            },
                            resolution_steps=[
                                f"Check {service_name} logs: docker logs polished-manual-app-builder-{service_name}-1",
                                "Restart service: docker compose restart " + service_name,
                                "Check service dependencies"
                            ]
                        )
                        self.error_log.append(error)
                        
                        # Send alert for critical issues
                        if severity == ErrorSeverity.CRITICAL:
                            await self.send_alert(error)
                
                # Check system resources
                resource_errors = self.check_system_resources()
                self.error_log.extend(resource_errors)
                
                # Check Docker containers
                docker_errors = self.check_docker_containers()
                self.error_log.extend(docker_errors)
                
                # Send alerts for new critical errors
                for error in resource_errors + docker_errors:
                    if error.severity == ErrorSeverity.CRITICAL:
                        await self.send_alert(error)
                
                # Save error log periodically
                if len(self.error_log) > 0:
                    self.save_error_log()
                    self.error_log.clear()  # Clear after saving
                
                # Generate and save health report
                health_report = self.generate_health_report()
                with open("health_report.json", "w") as f:
                    json.dump(health_report, f, indent=2)
                
                logger.info(f"Health check completed. Overall status: {health_report['overall_status']}")
                
                # Wait for next check
                await asyncio.sleep(self.config["monitoring"]["check_interval"])
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)

    async def start(self):
        """Start the error monitor"""
        self.running = True
        await self.monitoring_loop()

    def stop(self):
        """Stop the error monitor"""
        self.running = False
        logger.info("Error monitor stopped")

async def main():
    parser = argparse.ArgumentParser(description="Polished Manual App Builder Error Monitor")
    parser.add_argument("--config", default="error_monitor_config.json", help="Configuration file path")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--report", action="store_true", help="Generate health report and exit")
    
    args = parser.parse_args()
    
    monitor = ErrorMonitor(args.config)
    
    if args.report:
        # Generate health report only
        for service_name, service_config in monitor.config["services"].items():
            health = await monitor.check_service_health(service_name, service_config)
            monitor.service_health[service_name] = health
        
        report = monitor.generate_health_report()
        print(json.dumps(report, indent=2))
        return
    
    if args.once:
        # Run once and exit
        monitor.running = True
        for service_name, service_config in monitor.config["services"].items():
            health = await monitor.check_service_health(service_name, service_config)
            monitor.service_health[service_name] = health
            
            if health.status != ServiceStatus.HEALTHY:
                print(f"❌ {service_name}: {health.status.value} - {health.error_message}")
            else:
                print(f"✅ {service_name}: {health.status.value}")
        
        # Check system resources
        resource_errors = monitor.check_system_resources()
        for error in resource_errors:
            print(f"⚠️  {error.service}: {error.message}")
        
        return
    
    # Continuous monitoring
    try:
        await monitor.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        monitor.stop()

if __name__ == "__main__":
    asyncio.run(main())
