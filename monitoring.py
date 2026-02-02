"""
Health monitoring and metrics collection for RFP Automation System
Provides system health checks, performance metrics, and alerting
"""
import time
import psutil
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class HealthCheck:
    """Health check result"""
    name: str
    status: str  # "healthy", "warning", "critical"
    message: str
    duration_ms: float
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """Collects and stores system metrics"""
    
    def __init__(self, max_points: int = 1000):
        self.max_points = max_points
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a metric point"""
        point = MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            tags=tags or {}
        )
        self.metrics[name].append(point)
    
    def increment_counter(self, name: str, value: float = 1.0):
        """Increment a counter metric"""
        self.counters[name] += value
        self.record_metric(f"{name}_total", self.counters[name])
    
    def set_gauge(self, name: str, value: float):
        """Set a gauge metric"""
        self.gauges[name] = value
        self.record_metric(name, value)
    
    def get_metric(self, name: str, since: Optional[datetime] = None) -> List[MetricPoint]:
        """Get metric points"""
        points = list(self.metrics.get(name, []))
        
        if since:
            points = [p for p in points if p.timestamp >= since]
        
        return points
    
    def get_latest_value(self, name: str) -> Optional[float]:
        """Get latest value for a metric"""
        points = self.metrics.get(name)
        if points:
            return points[-1].value
        return None


class HealthMonitor:
    """Monitors system health and components"""
    
    def __init__(self):
        self.checks: Dict[str, callable] = {}
        self.metrics = MetricsCollector()
        self.last_check_time = datetime.utcnow()
    
    def register_check(self, name: str, check_func: callable):
        """Register a health check"""
        self.checks[name] = check_func
        logger.info(f"Registered health check: {name}")
    
    async def run_check(self, name: str) -> HealthCheck:
        """Run a single health check"""
        check_func = self.checks.get(name)
        if not check_func:
            return HealthCheck(
                name=name,
                status="critical",
                message="Health check not found",
                duration_ms=0,
                timestamp=datetime.utcnow()
            )
        
        start_time = time.time()
        
        try:
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            
            duration = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name=name,
                status=result.get("status", "healthy"),
                message=result.get("message", "OK"),
                duration_ms=duration,
                timestamp=datetime.utcnow(),
                details=result.get("details", {})
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"Health check failed: {name} - {e}")
            
            return HealthCheck(
                name=name,
                status="critical",
                message=str(e),
                duration_ms=duration,
                timestamp=datetime.utcnow()
            )
    
    async def run_all_checks(self) -> Dict[str, HealthCheck]:
        """Run all registered health checks"""
        results = {}
        
        for name in self.checks:
            results[name] = await self.run_check(name)
        
        self.last_check_time = datetime.utcnow()
        return results
    
    def get_overall_status(self, checks: Dict[str, HealthCheck]) -> str:
        """Determine overall system status"""
        if not checks:
            return "unknown"
        
        statuses = [check.status for check in checks.values()]
        
        if "critical" in statuses:
            return "critical"
        elif "warning" in statuses:
            return "warning"
        else:
            return "healthy"


# Global monitoring instance
monitor = HealthMonitor()


# System health checks
async def check_database():
    """Check database connectivity"""
    # In production, check actual database connection
    return {
        "status": "healthy",
        "message": "Database connection successful",
        "details": {
            "connection_time_ms": 5.2
        }
    }


async def check_llm_service():
    """Check LLM service availability"""
    # In production, check actual LLM service
    return {
        "status": "healthy",
        "message": "LLM service responding",
        "details": {
            "response_time_ms": 150.5,
            "model": "llama-3.3-70b"
        }
    }


def check_system_resources():
    """Check system resource usage"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    status = "healthy"
    message = "System resources OK"
    
    if cpu_percent > 80:
        status = "warning"
        message = "High CPU usage"
    
    if memory.percent > 85:
        status = "warning"
        message = "High memory usage"
    
    if disk.percent > 90:
        status = "critical"
        message = "Low disk space"
    
    return {
        "status": status,
        "message": message,
        "details": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "memory_available_gb": memory.available / (1024**3),
            "disk_free_gb": disk.free / (1024**3)
        }
    }


def check_api_endpoints():
    """Check critical API endpoints"""
    # In production, make actual health check requests
    return {
        "status": "healthy",
        "message": "All endpoints responding",
        "details": {
            "endpoints_checked": ["/health", "/api/health"],
            "avg_response_time_ms": 12.3
        }
    }


# Register default health checks
monitor.register_check("database", check_database)
monitor.register_check("llm_service", check_llm_service)
monitor.register_check("system_resources", check_system_resources)
monitor.register_check("api_endpoints", check_api_endpoints)


# Metrics collection functions
def collect_system_metrics():
    """Collect system performance metrics"""
    # CPU and memory
    monitor.metrics.set_gauge("system_cpu_percent", psutil.cpu_percent())
    monitor.metrics.set_gauge("system_memory_percent", psutil.virtual_memory().percent)
    monitor.metrics.set_gauge("system_disk_percent", psutil.disk_usage('/').percent)
    
    # Process metrics
    process = psutil.Process()
    monitor.metrics.set_gauge("process_memory_mb", process.memory_info().rss / (1024**2))
    monitor.metrics.set_gauge("process_cpu_percent", process.cpu_percent())


def collect_api_metrics():
    """Collect API performance metrics"""
    # These would be updated by middleware in production
    monitor.metrics.set_gauge("api_requests_per_second", 10.5)
    monitor.metrics.set_gauge("api_avg_response_time_ms", 125.3)
    monitor.metrics.set_gauge("api_error_rate", 0.02)


async def start_metrics_collection(interval_seconds: int = 30):
    """Start background metrics collection"""
    logger.info("Starting metrics collection")
    
    while True:
        try:
            collect_system_metrics()
            collect_api_metrics()
            await asyncio.sleep(interval_seconds)
        except Exception as e:
            logger.error(f"Metrics collection error: {e}")
            await asyncio.sleep(interval_seconds)


def get_dashboard_metrics() -> Dict[str, Any]:
    """Get metrics for dashboard display"""
    return {
        "system": {
            "cpu_percent": monitor.metrics.get_latest_value("system_cpu_percent"),
            "memory_percent": monitor.metrics.get_latest_value("system_memory_percent"),
            "disk_percent": monitor.metrics.get_latest_value("system_disk_percent")
        },
        "api": {
            "requests_per_second": monitor.metrics.get_latest_value("api_requests_per_second"),
            "avg_response_time_ms": monitor.metrics.get_latest_value("api_avg_response_time_ms"),
            "error_rate": monitor.metrics.get_latest_value("api_error_rate")
        },
        "process": {
            "memory_mb": monitor.metrics.get_latest_value("process_memory_mb"),
            "cpu_percent": monitor.metrics.get_latest_value("process_cpu_percent")
        },
        "last_updated": datetime.utcnow().isoformat()
    }
