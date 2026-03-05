from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
from datetime import datetime, timezone

# Import blueprints
from backend.routes import health_bp
from backend.core.security_pipeline import analyze_prompt_security, get_pipeline_stats

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
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # App startup
    # @app.before_first_request
    # def initialize_security_system():
    """Initialize the security system on first request."""
    try:
            logger.info("🚀 Initializing SafeX Security System with ONNX optimizations...")
            
            # Set development mode flags
            if app.debug:
                os.environ['SKIP_ML_MODELS'] = 'true'
                logger.info("Development mode: Using Lightweight models")
            else:
                logger.info("Production mode: Loading full ONNX models")
                
            # Initialize ML models (if not in dev mode)
            from backend.ml.model_loader import initialize_models
            success = initialize_models()
            
            if success:
                logger.info("✅ Security system initialized successfully")
            else:
                logger.warning("⚠️ Security system initialized with limited features")
    except Exception as e:
            logger.error(f"Failed to initialize security system: {e}")
            
            
            
    # Import health blueprint
    try:
        from backend.routes.health import health_bp
        app.register_blueprint(health_bp)
    except ImportError:
        logger.warning("Health blueprint not found, creating basic health endpoint")
        
        @app.route('/health', methods=['GET'])
        def health_check():
            """Basic health check endpoint."""
            return jsonify({
                "status": "healthy",
                "service": "SafeX Security Gateway",
                "version": "2.0.0-onnx",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
    
    
    # Main security endpoint (placeholder for now)
    @app.route('/analyze', methods=['POST'])
    def analyze_prompt():
        """
        Main endpoint for prompt security analysis.
        
        Request Body:
        {
            "prompt": "User input to analyze",
            "user_id": "optional_user_id"
        }
        """
        try:
            # Parse request data
            data = request.get_json()
            
            if not data or 'prompt' not in data:
                return jsonify({
                    "error": "Missing 'prompt' in request body",
                    "status": "error",
                    "code": "MISSING_PROMPT"
                }), 400
            
            prompt = data['prompt']
            user_id = data.get('user_id', 'anonymous')
            
            # Input validation
            if not prompt or len(prompt.strip()) == 0:
                return jsonify({
                    "error": "empty prompt provided",
                    "status": "error",
                    "code": "EMPTY_PROMPT"
                }), 400
                
            if len(prompt) > 10000:
                return jsonify({
                    "error": "Prompt too long (max 10,000 characters)",
                    "status": "error",
                    "code": "PROMPT_TOO_LONG"
                }), 400
                
            # Run optimized security analysis
            result = analyze_prompt_security(prompt, user_id)
            
            # Add request metadata
            result["request_id"] = f"{user_id}_{int(datetime.now(timezone.utc).timestamp())}"
            result["api_version"] = "2.0.0-onnx"
            
            # Returning the result
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Analysis endpoints error: {e}")
            return jsonify({
                "status": "error",
                "decision": "BLOCK",
                "error": "Internal security analysis error",
                "risk_score": 1.0,
                "code": "ANALYSIS_ERROR",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": str(e)
            }), 500
            
            
    # Quick analysis endpoint for high-throughput applications
    @app.route('/analyze/quick', methods=['POST'])
    def quick_analyze():
        """
        High-performance quick analysis endpont.
        Return minimal response for high-throughput applications.
        """
        try:
            data = request.get_json()
            prompt = data['prompt']
            user_id = data.get('user_id', 'anonymous')
            
            # Run analysis
            result = analyze_prompt_security(prompt, user_id)
            
            # Return minimal response for speed
            return jsonify({
                "decision": result['decision'],
                "risk_score": result['risk_score'],
                "safe": result['decision'] == 'ALLOW',
                "processed_prompt": result.get('processed_prompt', prompt),
                "processing_time": result['processing_time_seconds'],
                "timestamp": result['timestamp']
            })
        except Exception as e:
            logger.error(f"Quick analysis error: {e}")
            return jsonify({
                "decision": "BLOCK",
                "safe": False,
                "error": "Quick analysis failed",
                "processing_time": 0.0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": str(e)
            }), 500
            
            
    # Stats endpoint
    @app.route('/stats', methods=['GET'])
    def get_stats():
        """Get performance statistics and system health."""
        try:
            stats = get_pipeline_stats()
            
            return jsonify({
                "system": "SafeX Security Gateway",
                "version": "2.0.0-onnx",
                "performance": stats,
                "optimization": "ONNX Runtime",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "operational"
            })
        except Exception as e:
            logger.error(f"Stats endpoint error: {e}")
            return jsonify({
                "error": "Failed to retrieve statistics",
                "status": "error"
            }), 500
            
    @app.route('/analyze/batch', methods=['POST'])
    def batch_analyze():
        """
        Batch analysis endpoint for processing multiple prompts efficiently.
        
        Request Body:
        {
            "prompts": ["prompt1", "prompt2", ...]
            "user_id": "optional_user_id"
        }
        """
        try:
            data = request.get_json()
            
            if not data or 'prompts' not in data:
                return jsonify({
                    "error": "Missing 'prompts' array in request body",
                    "status": "error"
                }), 400
            
            prompts = data['prompts']
            user_id = data.get('user_id', 'batch_user')
            
            # Input validation
            if not isinstance(prompts, list) or len(prompts) == 0:
                return jsonify({
                    "error": "Invalid prompts array",
                    "status": "error",
                }), 400
                
            if len(prompts) > 100: # Limit batch size
                return jsonify({
                    "error": "Batch size too large (max 100 prompts)",
                    "status": "error",
                    "code": "BATCH_TOO_LARGE"
                }), 400
                
            # Process batch
            results = []
            total_processing_time =0.0
            
            
            for i, prompt in enumerate(prompts):
                try:
                    result = analyze_prompt_security(prompt, f"{user_id}_batch_{i}")
                    results.append({
                        "index": i,
                        "decision": result['decision'],
                        "risk_score": result['risk_score'],
                        "safe": result['decision'] == 'ALLOW',
                        "processing_time": result['processing_time_seconds']
                    })
                    total_processing_time += result['processing_time_seconds']
                    
                except Exception as e:
                    results.append({
                        "index": i,
                        "decision": "BLOCK",
                        "risk_score": 1.0,
                        "safe": False,
                        "error": str(e)
                    })
            
            return jsonify({
                "status": "success",
                "results": results,
                "batch_stats": {
                    "total_prompts": len(prompts),
                    "total_processing_time": total_processing_time,
                    "avg_processing_time": total_processing_time / len(prompts),
                    "blocked_count": sum(1 for r in results if r.get('decision') == 'BLOCK'),
                    "sanitized_count": sum(1 for r in results if r.get('decision') == 'SANITIZE'),
                    "allowed_count": sum(1 for r in results if r.get('decision') == 'ALLOW')
                    
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        except Exception as e:
            logger.error(f"Batch analysis error: {e}")
            return jsonify({
                "status": "error",
                "error": "Batch processing failed"
            }), 500
        
        
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Endpoint not found",
            "service": "SafeX Security Gateway",
            "available_endpoints": ["/analyze", "/analyze/quick","/analyze/batch", "/stats", "/health"],
            "documentation": "https://github.com/Likhi2005/SafeX"
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "Internal server error",
            "service": "SafeX Security Gateway",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500
    
    return app

if __name__ == '__main__':
    print("🚀 Starting SafeX Security Gateway v2.0.0 with ONNX optimization...")
    app = create_app()
    
    # Production settings
    port =int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() =='true'
    print("Starting SafeX Security Gateway...")
    
    
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True # Enable threading for better performance
        )














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
    
    
    
    
    
    
    