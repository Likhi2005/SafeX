from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

# Import blueprints
from backend.routes import health_bp

def create_app():
    """Application factory pattern for Flask app."""
    app = Flask(__name__)
    CORS(app)
    
#     CORS(
#     app,
#     origins=["https://myfrontend.com"],
#     methods=["GET", "POST", "PUT", "DELETE"],
#     allow_headers=["Content-Type", "Authorization"],
#     supports_credentials=True
# )

    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Register blueprints
    app.register_blueprint(health_bp)
    
    # Main security endpoint (placeholder for now)
    @app.route('/analyze', methods=['POST'])
    def analyze_prompt():
        """
        Main endpoint for prompt security analysis.
        Will integrate with security pipeline once filters are built.
        """
        try:
            data = request.get_json()
            prompt = data.get('prompt', '')
            
            if not prompt:
                return jsonify({
                    "error": "No prompt provided"
                }), 400
            
            # Placeholder response until we implement the security pipeline
            return jsonify({
                "prompt": prompt,
                "risk_score": 0.1,
                "decision": "ALLOW",
                "reason": "Pipeline not yet implemented",
                "service": "SafeX Security Gateway"
            }), 200
            
        except Exception as e:
            logger.error(f"Prompt analysis failed: {e}")
            return jsonify({
                "error": "Analysis failed",
                "details": str(e)
            }), 500
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Endpoint not found",
            "service": "SafeX Security Gateway"
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "Internal server error",
            "service": "SafeX Security Gateway"
        }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting SafeX Security Gateway...")
    app.run(host='0.0.0.0', port=5000, debug=True)














# from flask import Flask, jsonify, request
# from flask_cors import CORS
# import logging
# from typing import Dict, Any

# # Import health checking functions
# from healthcheck.healthcheck import get_health_status, get_basic_health

# app = Flask(__name__)
# CORS(app)

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Health endpoints
# # @app.route('/health', methods=['GET'])
# # def basic_health():
# #     """
# #     Basic health check for load balancers.
# #     Returns 200 if service is running.
# #     """
# #     try:
# #         health_data = get_basic_health()
# #         return jsonify(health_data), 200
# #     except Exception as e:
# #         logger.error(f"Basic health check failed: {str(e)}")
# #         return jsonify({
# #             "status": "unhealthy",
# #             "error": "Service unavailable"
# #             # "error": str(e)
# #         }), 503
        
        
# @app.route('/health/live', methods=['GET'])
# def liveness_check():
#     """
#     Kubernetes liveness probe.
#     Simple check if the application is alive.
#     """
#     return jsonify({
#         "status": "alive",
#         "service": "SafeX Security Gateway"
#     }), 200
    
    
# if __name__ == '__main__':
#     logger.info("Starting SafeX Security Gateway...")
#     app.run(host='0.0.0.0', port=3000, debug=True)
    
    
    
    
    
    
    