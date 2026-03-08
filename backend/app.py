from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any



# Database imports
from backend.models import init_db, db
from backend.models.threat_log import ThreatLog
from backend.services.threat_service import ThreatLogService
from backend.config.database import DatabaseConfig

# Model Initializer
from backend.ml.model_initializer import model_initializer

# WebSocket and Threat Intelligence
from backend.websocket.threat_websocket import ws_service

def create_app():
    """Application factory pattern for Flask app."""
    app = Flask(__name__)
    
    
    # -------------------------
    # Configure logging FIRST
    # -------------------------
    # Configure logging
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/safex.log')
        ]
    )
    logger = logging.getLogger(__name__)
    
    
    
    # -------------------------
    # Database config
    # -------------------------
    app.config.from_object(DatabaseConfig)
    
    # Initialize database
    init_db(app)
    
    # Create tables immediately in app context (Flask 3.x compatible)
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
        
    # Configure CORS
    CORS(app, 
         origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         supports_credentials=True)
    
    
    
    # Database initialization
    # @app.before_first_request
    # def create_tables():
    #     """Create database tables if they don't exist."""
    #     try:
    #         db.create_all()
    #         logger.info("Database tables created successfully")
    #     except Exception as e:
    #         logger.error(f"Failed to create database tables: {e}")
    
    
    
    # Initialize security system on startup (Flask 3.x compatible)
    _initialized = False
    
    @app.before_request
    def ensure_initialization():
        """Ensure the security system is initialized before processing requests."""
        nonlocal _initialized
        if not _initialized:
            initialize_security_system()
            _initialized = True
            
    # New threat logging API endpoint
    @app.route('/api/log-threat', methods=['POST'])
    def log_threat():
        """Log a threat analysis result to the database."""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'error': 'No JSON data provided',
                    'status': 'error'
                }), 400
            
            # Validate required fields
            required_fields = ['prompt', 'risk_score', 'attack_type', 'blocked']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({
                    'error': f'Missing required fields: {missing_fields}',
                    'status': 'error'
                }), 400
            
            # Create analysis result for ThreatLog
            analysis_result = {
                'processed_prompt': data.get('sanitized_prompt'),
                'primary_threat': data.get('attack_type'),
                'risk_score': data.get('risk_score'),
                'decision': 'BLOCK' if data.get('blocked') else 'ALLOW',
                'model_used': data.get('model_used', 'manual_log'),
                'processing_time_seconds': data.get('processing_time', 0.0)
            }
            
            # Log to database
            threat_log = ThreatLogService.log_threat(
                prompt=data['prompt'],
                analysis_result=analysis_result,
                user_id=data.get('user_id', 'api_user'),
                ip_address=request.remote_addr
            )
            
            if threat_log:
                return jsonify({
                    'status': 'success',
                    'message': 'Threat logged successfully',
                    'threat_id': threat_log.id,
                    'timestamp': threat_log.created_at.isoformat()
                }), 201
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to log threat'
                }), 500
                
        except Exception as e:
            logger.error(f"Log threat error: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Internal server error',
                'details': str(e)
            }), 500
    
    # Get threat logs endpoint
    @app.route('/api/threats', methods=['GET'])
    def get_threats():
        """Get recent threat logs."""
        try:
            limit = request.args.get('limit', 100, type=int)
            threats = ThreatLogService.get_recent_threats(limit=limit)
            
            return jsonify({
                'status': 'success',
                'threats': [threat.to_dict() for threat in threats],
                'count': len(threats)
            })
            
        except Exception as e:
            logger.error(f"Get threats error: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch threats'
            }), 500
    
    # Threat statistics endpoint
    @app.route('/api/threat-stats', methods=['GET'])
    def get_threat_statistics():
        """Get threat analysis statistics."""
        try:
            stats = ThreatLogService.get_threat_stats()
            
            return jsonify({
                'status': 'success',
                'statistics': stats,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
        except Exception as e:
            logger.error(f"Get threat stats error: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch statistics'
            }), 500
            
    def initialize_security_system():
        """Initialize the security system."""
        try:
            logger.info("🚀 Initializing SafeX Security System v2.0.0...")
            
            # Force ML model initialization ALWAYS (not just in production)
            logger.info("🔄 Initializing ML models...")
            model_success = model_initializer.initialize_all_models()
            
            if not model_success:
                logger.error("❌ ML model initialization failed!")
                # Don't skip ML models - this is critical
                return False
            else:
                logger.info("✅ ML models initialized successfully")
            
            # Get model status for logging
            model_status = model_initializer.get_model_status()
            logger.info(f"📊 Model status: {model_status}")
            
            return True
                
        except Exception as e:
            logger.error(f"Failed to initialize security system: {e}")
            return False
    
    # def initialize_security_system():
    #     """Initialize the security system."""
    #     try:
    #         logger.info("🚀 Initializing SafeX Security System v2.0.0...")
            
    #         if app.debug or os.environ.get('FLASK_ENV') == 'development':
    #             os.environ['SKIP_ML_MODELS'] = 'true'
    #             logger.info("Development mode: Using lightweight models")
    #         else:
    #             logger.info("Production mode: Loading full ML models")
            
    #         from backend.ml.model_loader import initialize_models
    #         success = initialize_models()
            
    #         if success:
    #             logger.info("Security system initialized successfully")
    #         else:
    #             logger.warning("Security system initialized with limited features")
                
    #         return success
                
    #     except Exception as e:
    #         logger.error(f"Failed to initialize security system: {e}")
    #         return False
    
    # Register blueprints
    try:
        from backend.routes.health import health_bp
        from backend.routes.analysis import analysis_bp
        
        app.register_blueprint(health_bp)
        app.register_blueprint(analysis_bp)
        logger.info("Blueprints registered successfully")
        
        # Initialize WebSocket service
        socketio = ws_service.init_app(app)
        logger.info("WebSocket service initialized")
        
    except ImportError as e:
        logger.warning(f"Blueprint import failed: {e}")
        
        # Fallback endpoints if blueprints fail
        @app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({
                "status": "healthy",
                "service": "SafeX Security Gateway",
                "version": "2.0.0",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
    
    # Keep original analyze endpoint for compatibility
    @app.route('/analyze', methods=['POST'])
    def analyze_prompt_legacy():
        """Legacy analyze endpoint for backward compatibility."""
        try:
            from backend.core.security_pipeline import analyze_prompt_security
            
            data = request.get_json()
            if not data or 'prompt' not in data:
                return jsonify({"error": "Missing prompt"}), 400
            
            result = analyze_prompt_security(data['prompt'], data.get('user_id', 'anonymous'))
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Legacy analyze error: {e}")
            return jsonify({
                "status": "error",
                "decision": "BLOCK",
                "error": "Analysis failed",
                "risk_score": 1.0
            }), 500
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Endpoint not found",
            "service": "SafeX Security Gateway",
            "available_endpoints": {
                "/analyze": "POST - Legacy analysis",
                "/api/v1/analyze": "POST - Enhanced analysis",
                "/api/v1/analyze/filters": "POST - Filter details",
                "/health": "GET - Health check"
            }
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            "error": "Internal server error",
            "service": "SafeX Security Gateway"
        }), 500
    
    return app, socketio

if __name__ == '__main__':
    print("Starting SafeX Security Gateway v2.0.0...")
    app, socketio = create_app()
    
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"Server ready at http://{host}:{port}")
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)



# from flask import Flask, jsonify, request
# from flask_cors import CORS
# import logging
# import os
# from datetime import datetime, timezone

# # Import blueprints
# from backend.routes import health_bp
# from backend.core.security_pipeline import analyze_prompt_security, get_pipeline_stats

# def create_app():
#     """Application factory pattern for Flask app."""
#     app = Flask(__name__)
#     CORS(app)
    
# #     CORS(
# #     app,
# #     origins=["https://myfrontend.com"],
# #     methods=["GET", "POST", "PUT", "DELETE"],
# #     allow_headers=["Content-Type", "Authorization"],
# #     supports_credentials=True
# # )

    
#     # Configure logging
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     logger = logging.getLogger(__name__)
    
#     # App startup
#     # @app.before_first_request
#     # def initialize_security_system():
#     """Initialize the security system on first request."""
#     try:
#             logger.info("🚀 Initializing SafeX Security System with ONNX optimizations...")
            
#             # Set development mode flags
#             if app.debug:
#                 os.environ['SKIP_ML_MODELS'] = 'true'
#                 logger.info("Development mode: Using Lightweight models")
#             else:
#                 logger.info("Production mode: Loading full ONNX models")
                
#             # Initialize ML models (if not in dev mode)
#             from backend.ml.model_loader import initialize_models
#             success = initialize_models()
            
#             if success:
#                 logger.info("✅ Security system initialized successfully")
#             else:
#                 logger.warning("⚠️ Security system initialized with limited features")
#     except Exception as e:
#             logger.error(f"Failed to initialize security system: {e}")
            
            
            
#     # Import health blueprint
#     try:
#         from backend.routes.health import health_bp
#         app.register_blueprint(health_bp)
#     except ImportError:
#         logger.warning("Health blueprint not found, creating basic health endpoint")
        
#         @app.route('/health', methods=['GET'])
#         def health_check():
#             """Basic health check endpoint."""
#             return jsonify({
#                 "status": "healthy",
#                 "service": "SafeX Security Gateway",
#                 "version": "2.0.0-onnx",
#                 "timestamp": datetime.now(timezone.utc).isoformat()
#             })
            
    
    
#     # Main security endpoint (placeholder for now)
#     @app.route('/analyze', methods=['POST'])
#     def analyze_prompt():
#         """
#         Main endpoint for prompt security analysis.
        
#         Request Body:
#         {
#             "prompt": "User input to analyze",
#             "user_id": "optional_user_id"
#         }
#         """
#         try:
#             # Parse request data
#             data = request.get_json()
            
#             if not data or 'prompt' not in data:
#                 return jsonify({
#                     "error": "Missing 'prompt' in request body",
#                     "status": "error",
#                     "code": "MISSING_PROMPT"
#                 }), 400
            
#             prompt = data['prompt']
#             user_id = data.get('user_id', 'anonymous')
            
#             # Input validation
#             if not prompt or len(prompt.strip()) == 0:
#                 return jsonify({
#                     "error": "empty prompt provided",
#                     "status": "error",
#                     "code": "EMPTY_PROMPT"
#                 }), 400
                
#             if len(prompt) > 10000:
#                 return jsonify({
#                     "error": "Prompt too long (max 10,000 characters)",
#                     "status": "error",
#                     "code": "PROMPT_TOO_LONG"
#                 }), 400
                
#             # Run optimized security analysis
#             result = analyze_prompt_security(prompt, user_id)
            
#             # Add request metadata
#             result["request_id"] = f"{user_id}_{int(datetime.now(timezone.utc).timestamp())}"
#             result["api_version"] = "2.0.0-onnx"
            
#             # Returning the result
#             return jsonify(result)
            
#         except Exception as e:
#             logger.error(f"Analysis endpoints error: {e}")
#             return jsonify({
#                 "status": "error",
#                 "decision": "BLOCK",
#                 "error": "Internal security analysis error",
#                 "risk_score": 1.0,
#                 "code": "ANALYSIS_ERROR",
#                 "timestamp": datetime.now(timezone.utc).isoformat(),
#                 "details": str(e)
#             }), 500
            
            
#     # Quick analysis endpoint for high-throughput applications
#     @app.route('/analyze/quick', methods=['POST'])
#     def quick_analyze():
#         """
#         High-performance quick analysis endpont.
#         Return minimal response for high-throughput applications.
#         """
#         try:
#             data = request.get_json()
#             prompt = data['prompt']
#             user_id = data.get('user_id', 'anonymous')
            
#             # Run analysis
#             result = analyze_prompt_security(prompt, user_id)
            
#             # Return minimal response for speed
#             return jsonify({
#                 "decision": result['decision'],
#                 "risk_score": result['risk_score'],
#                 "safe": result['decision'] == 'ALLOW',
#                 "processed_prompt": result.get('processed_prompt', prompt),
#                 "processing_time": result['processing_time_seconds'],
#                 "timestamp": result['timestamp']
#             })
#         except Exception as e:
#             logger.error(f"Quick analysis error: {e}")
#             return jsonify({
#                 "decision": "BLOCK",
#                 "safe": False,
#                 "error": "Quick analysis failed",
#                 "processing_time": 0.0,
#                 "timestamp": datetime.now(timezone.utc).isoformat(),
#                 "details": str(e)
#             }), 500
            
            
#     # Stats endpoint
#     @app.route('/stats', methods=['GET'])
#     def get_stats():
#         """Get performance statistics and system health."""
#         try:
#             stats = get_pipeline_stats()
            
#             return jsonify({
#                 "system": "SafeX Security Gateway",
#                 "version": "2.0.0-onnx",
#                 "performance": stats,
#                 "optimization": "ONNX Runtime",
#                 "timestamp": datetime.now(timezone.utc).isoformat(),
#                 "status": "operational"
#             })
#         except Exception as e:
#             logger.error(f"Stats endpoint error: {e}")
#             return jsonify({
#                 "error": "Failed to retrieve statistics",
#                 "status": "error"
#             }), 500
            
#     @app.route('/analyze/batch', methods=['POST'])
#     def batch_analyze():
#         """
#         Batch analysis endpoint for processing multiple prompts efficiently.
        
#         Request Body:
#         {
#             "prompts": ["prompt1", "prompt2", ...]
#             "user_id": "optional_user_id"
#         }
#         """
#         try:
#             data = request.get_json()
            
#             if not data or 'prompts' not in data:
#                 return jsonify({
#                     "error": "Missing 'prompts' array in request body",
#                     "status": "error"
#                 }), 400
            
#             prompts = data['prompts']
#             user_id = data.get('user_id', 'batch_user')
            
#             # Input validation
#             if not isinstance(prompts, list) or len(prompts) == 0:
#                 return jsonify({
#                     "error": "Invalid prompts array",
#                     "status": "error",
#                 }), 400
                
#             if len(prompts) > 100: # Limit batch size
#                 return jsonify({
#                     "error": "Batch size too large (max 100 prompts)",
#                     "status": "error",
#                     "code": "BATCH_TOO_LARGE"
#                 }), 400
                
#             # Process batch
#             results = []
#             total_processing_time =0.0
            
            
#             for i, prompt in enumerate(prompts):
#                 try:
#                     result = analyze_prompt_security(prompt, f"{user_id}_batch_{i}")
#                     results.append({
#                         "index": i,
#                         "decision": result['decision'],
#                         "risk_score": result['risk_score'],
#                         "safe": result['decision'] == 'ALLOW',
#                         "processing_time": result['processing_time_seconds']
#                     })
#                     total_processing_time += result['processing_time_seconds']
                    
#                 except Exception as e:
#                     results.append({
#                         "index": i,
#                         "decision": "BLOCK",
#                         "risk_score": 1.0,
#                         "safe": False,
#                         "error": str(e)
#                     })
            
#             return jsonify({
#                 "status": "success",
#                 "results": results,
#                 "batch_stats": {
#                     "total_prompts": len(prompts),
#                     "total_processing_time": total_processing_time,
#                     "avg_processing_time": total_processing_time / len(prompts),
#                     "blocked_count": sum(1 for r in results if r.get('decision') == 'BLOCK'),
#                     "sanitized_count": sum(1 for r in results if r.get('decision') == 'SANITIZE'),
#                     "allowed_count": sum(1 for r in results if r.get('decision') == 'ALLOW')
                    
#                 },
#                 "timestamp": datetime.now(timezone.utc).isoformat()
#             })
        
#         except Exception as e:
#             logger.error(f"Batch analysis error: {e}")
#             return jsonify({
#                 "status": "error",
#                 "error": "Batch processing failed"
#             }), 500
        
        
    
#     # Global error handlers
#     @app.errorhandler(404)
#     def not_found(error):
#         return jsonify({
#             "error": "Endpoint not found",
#             "service": "SafeX Security Gateway",
#             "available_endpoints": ["/analyze", "/analyze/quick","/analyze/batch", "/stats", "/health"],
#             "documentation": "https://github.com/Likhi2005/SafeX"
#         }), 404

#     @app.errorhandler(500)
#     def internal_error(error):
#         return jsonify({
#             "error": "Internal server error",
#             "service": "SafeX Security Gateway",
#             "timestamp": datetime.now(timezone.utc).isoformat()
#         }), 500
    
#     return app

# if __name__ == '__main__':
#     print("🚀 Starting SafeX Security Gateway v2.0.0 with ONNX optimization...")
#     app = create_app()
    
#     # Production settings
#     port =int(os.environ.get('PORT', 5000))
#     debug = os.environ.get('DEBUG', 'False').lower() =='true'
#     print("Starting SafeX Security Gateway...")
    
    
    
#     app.run(
#         host='0.0.0.0',
#         port=port,
#         debug=debug,
#         threaded=True # Enable threading for better performance
#         )