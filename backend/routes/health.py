from flask import Blueprint,jsonify
import logging
from typing import Dict, Any

# Import health checking functions
from backend.healthcheck.healthcheck import get_health_status, get_basic_health

# Create Blueprint
health_bp = Blueprint('health', __name__, url_prefix='/health')

# Configure logging
logger = logging.getLogger(__name__)

@health_bp.route('', methods=['GET'])
def basic_health():
    """
    Basic health check for load balancers.
    Returns 200 if service is running.
    """
    try:
        health_data = get_basic_health()
        return jsonify(health_data), 200
    except Exception as e:
        logger.error(f"Basic healh check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": "service unavailable"
        }), 503
        
@health_bp.route('/detailed', methods=['GET'])
def detailed_health():
    """
    Comprehensive health check with system metrics.
    Returns detailed status of all components.
    """
    try:
        health_data = get_health_status()
        
        # Return appropriate HTTP status based on health
        status_code = {
            "healthy": 200,
            "degraded": 200, # Still functional
            "unhealthy": 503
        }.get(health_data.get("status"), 503)
        
        return jsonify(health_data), status_code
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": f"Health check failed: {str(e)}",
            "service": "SafeX Security Gateway"
        }), 503
        

@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """
    Kubernetes readiness probe.
    Checks if service is ready to accept traffic.
    """
    try:
        health_data = get_health_status()
        
        # Service is ready if healthy or degraded
        if health_data.get("status") in ["healthy","degraded"]:
            return jsonify({
                "status": "ready",
                "timestamp": health_data.get("timestamp")
            }), 200
        else:
            return jsonify({
                "status": "not_ready",
                "reason": "service unhealthy"
            }), 503
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({
            "status": "not_ready",
            "error": str(e)
        }), 503
        
        
@health_bp.route('/live', methods=['GET'])
def liveness_check():
    """
    Kubernetes liveness probe.
    Simple check if the application is alive.
    """
    return jsonify({
        "status": "alive",
        "service": "SafeX Security Gateway"
    }), 200
        















# from flask import Blueprint, jsonify
# import logging
# from typing import Dict, Any

# # Import health checking functions
# from backend.healthcheck.healthcheck import get_health_status, get_basic_health

# # Create Blueprint
# health_bp = Blueprint('health', __name__, url_prefix='/health')

# # Configure logging
# logger = logging.getLogger(__name__)

# @health_bp.route('', methods=['GET'])
# def basic_health():
#     """
#     Basic health check for load balancers.
#     Returns 200 if service is running.
#     """
#     try:
#         health_data = get_basic_health()
#         return jsonify(health_data), 200
#     except Exception as e:
#         logger.error(f"Basic health check failed: {e}")
#         return jsonify({
#             "status": "unhealthy",
#             "error": "Service unavailable"
#         }), 503

# @health_bp.route('/detailed', methods=['GET'])
# def detailed_health():
#     """
#     Comprehensive health check with system metrics.
#     Returns detailed status of all components.
#     """
#     try:
#         health_data = get_health_status()
        
#         # Return appropriate HTTP status based on health
#         status_code = {
#             "healthy": 200,
#             "degraded": 200,  # Still functional
#             "unhealthy": 503
#         }.get(health_data.get("status"), 503)
        
#         return jsonify(health_data), status_code
        
#     except Exception as e:
#         logger.error(f"Detailed health check failed: {e}")
#         return jsonify({
#             "status": "unhealthy",
#             "error": f"Health check failed: {str(e)}",
#             "service": "SafeX Security Gateway"
#         }), 503

# @health_bp.route('/ready', methods=['GET'])
# def readiness_check():
#     """
#     Kubernetes readiness probe.
#     Checks if service is ready to accept traffic.
#     """
#     try:
#         health_data = get_health_status()
        
#         # Service is ready if healthy or degraded
#         if health_data.get("status") in ["healthy", "degraded"]:
#             return jsonify({
#                 "status": "ready",
#                 "timestamp": health_data.get("timestamp")
#             }), 200
#         else:
#             return jsonify({
#                 "status": "not_ready",
#                 "reason": "Service unhealthy"
#             }), 503
            
#     except Exception as e:
#         logger.error(f"Readiness check failed: {e}")
#         return jsonify({
#             "status": "not_ready",
#             "error": str(e)
#         }), 503

# @health_bp.route('/live', methods=['GET'])
# def liveness_check():
#     """
#     Kubernetes liveness probe.
#     Simple check if the application is alive.
#     """
#     return jsonify({
#         "status": "alive",
#         "service": "SafeX Security Gateway"
#     }), 200