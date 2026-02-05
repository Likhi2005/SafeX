import time
import psutil
import logging
from typing import Dict, Any
from datetime import datetime

class HealthChecker:
    """
    System health monitoring for SafeX security gateway.
    Checks CPU, memory, disk, and service availability.
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.logger = logging.getLogger(__name__)
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system resource usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory.percent,
                "memory_available_mb": memory.available // (1024 * 1024),
                "disk_usage_percent": disk.percent,
                "disk_free_gb": disk.free // (1024 ** 3)
            }
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return {}
        
    def check_redis_connection(self) -> Dict[str, Any]:
        """Check Redis connectivity for caching/rate limiting."""
        try:
            # Import here to avoid circular dependency
            from backend.core.redis_client import get_redis_client
            
            redis_client = get_redis_client()
            redis_client.ping()
            
            return {
                "status": "healthy",
                "latency_ms": self._measure_redis_latency(redis_client)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
            
    def _measure_redis_latency(self, redis_client) -> float:
        """Measure Redis response time."""
        start = time.time()
        redis_client.ping()
        return round((time.time() - start) * 1000, 2)
    
    def check_ml_models(self) -> Dict[str, Any]:
        """Verify ML models are loaded and functional."""
        try:
            # Import here to avoid loading models during healthcheck init
            from backend.ml.model_loader import ModelLoader
            
            model_loader = ModelLoader()
            models_status = {}
            
            # Check DistilBERT classifier
            try:
                classifier = model_loader.load_classifier()
                models_status["distilbert_classifier"] = "loaded"
            except Exception as e:
                models_status["distilbert_classifier"] = f"error: {str(e)}"
                
            # Check MiniLM similarity detector
            try:
                similarity_model = model_loader.load_similarity_model()
                models_status["minilm_similarity"] = "loaded"
            except Exception as e:
                models_status["minilm_similarity"] = f"error: {str(e)}"
                
            # return {"models": models_status}
            return models_status
        
        except Exception as e:
            return {"models": f"failed_to_check: {str(e)}"}
        
    
    def get_uptime_seconds(self) -> float:
        """Get service uptime in seconds."""
        return round(time.time() - self.start_time, 2)
    
    def comprehensive_health_check(self) -> Dict[str, Any]:
        """
        Full system Health report.
        Returns status suitable for monitoring systems.
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Get all health metrics
        system_metrics = self.get_system_metrics()
        redis_status = self.check_redis_connection()
        ml_models_status = self.check_ml_models()
        uptime = self.get_uptime_seconds()
        
        # Determine overall health
        overall_status = self._determine_overall_status(
            system_metrics, redis_status, ml_models_status
        )
        return {
            "status": overall_status,
            "timestamp": timestamp,
            "uptime_seconds": uptime,
            "system": system_metrics,
            "redis": redis_status,
            "models": ml_models_status,
            "version": "1.0.0",
            "service": "SafeX Security Gateway"
        }
        
    def _determine_overall_status(self, systme: Dict, redis: Dict, models: Dict) -> str:
        """
        Determine overall service health based on components.
        Returns: 'healthy', 'degraded', or 'unhealthy'
        """
        
        # Critical failures
        if redis.get("status") == "unhealthy":
            return "unhealthy"
        
        # Check for model failures
        model_errors = [v for v in models.values() if "error" in str(v)]
        if len(model_errors) >= 2:
            return "unhealthy"
        
        # Check system resources
        cpu_usage = system.get("cpu_usage_percent", 0)
        memory_usage = system.get("memory_usage_percent", 0)
        
        if cpu_usage > 90 or memory_usage > 95:
            return "unhealthy"
        elif cpu_usage > 75 or memory_usage > 85 or len(model_errors) == 1:
            return "degraded"
        
        return "healthy"
    
    
    # Global health checker instance
health_checker = HealthChecker()

def get_health_status() -> Dict[str, Any]:
    """Get current health status (used by Flask routes)."""
    return health_checker.comprehensive_health_check()

def get_basic_health() -> Dict[str, str]:
    """Quick health check for load balancer probes."""
    try:
        # Just check if service is running
        return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }