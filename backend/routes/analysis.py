from flask import Blueprint, jsonify, request, current_app
import logging
from datetime import datetime, timezone
from backend.core.security_pipeline import analyze_prompt_security

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/v1')
logger = logging.getLogger(__name__)

@analysis_bp.route('/analyze', methods=['POST'])
def analyze_prompt():
    """
    Enhanced security analysis endpoint with detailed filter results.
    
    Request Body:
    {
        "prompt": "User input to analyze",
        "user_id": "optional_user_id",
        "include_details": true
    }
    """
    start_time = datetime.now(timezone.utc)
    
    try:
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "Invalid JSON in request body",
                "status": "error",
                "code": "INVALID_JSON"
            }), 400
        
        if 'prompt' not in data:
            return jsonify({
                "error": "Missing 'prompt' in request body",
                "status": "error",
                "code": "MISSING_PROMPT"
            }), 400
        
        prompt = data['prompt']
        user_id = data.get('user_id', 'anonymous')
        include_details = data.get('include_details', True)
        
        # Input validation
        if not prompt or not isinstance(prompt, str):
            return jsonify({
                "error": "Invalid prompt: must be a non-empty string",
                "status": "error",
                "code": "INVALID_PROMPT"
            }), 400
            
        if len(prompt.strip()) == 0:
            return jsonify({
                "error": "Empty prompt provided",
                "status": "error",
                "code": "EMPTY_PROMPT"
            }), 400
            
        if len(prompt) > 10000:
            return jsonify({
                "error": "Prompt too long (max 10,000 characters)",
                "status": "error",
                "code": "PROMPT_TOO_LONG"
            }), 400
        
        # Run security analysis
        result = analyze_prompt_security(prompt, user_id)
        
        # Enhance result with detailed breakdown if requested
        if include_details:
            result = enhance_analysis_details(result)
        
        # Add request metadata
        result["request_id"] = f"{user_id}_{int(start_time.timestamp())}"
        result["api_version"] = "2.0.0"
        result["request_timestamp"] = start_time.isoformat()
        result["analysis_complete"] = True
        
        logger.info(f"Detailed analysis complete for user {user_id}: {result.get('decision')} (risk: {result.get('risk_score', 0):.3f})")
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Analysis endpoint error: {e}")
        return jsonify({
            "status": "error",
            "decision": "BLOCK",
            "error": "Internal security analysis error",
            "risk_score": 1.0,
            "code": "ANALYSIS_ERROR",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": str(e) if current_app.debug else "Contact administrator"
        }), 500

@analysis_bp.route('/analyze/filters', methods=['POST'])
def analyze_filters_detailed():
    """
    Get detailed filter breakdown for a prompt.
    
    Request Body:
    {
        "prompt": "User input to analyze",
        "user_id": "optional_user_id"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                "error": "Missing prompt",
                "status": "error"
            }), 400
        
        prompt = data['prompt']
        user_id = data.get('user_id', 'anonymous')
        
        # Run analysis
        result = analyze_prompt_security(prompt, user_id)
        
        # Extract and enhance filter details
        filter_details = extract_filter_details(result)
        
        return jsonify({
            "status": "success",
            "prompt": prompt,
            "overall_risk_score": result.get('risk_score', 0),
            "decision": result.get('decision', 'BLOCK'),
            "filters": filter_details,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Filter analysis error: {e}")
        return jsonify({
            "status": "error",
            "error": "Filter analysis failed",
            "details": str(e) if current_app.debug else "Contact administrator"
        }), 500

def enhance_analysis_details(result):
    """Enhance the analysis result with detailed breakdown."""
    
    # Extract filter results
    filter_results = result.get('filter_results', {})
    
    # Create detailed breakdown
    detailed_filters = {}
    
    # Regex Filter Details
    regex_result = filter_results.get('regex_filter', {})
    detailed_filters['regex_filter'] = {
        "name": "Pattern Detection",
        "description": "Detects known attack patterns and jailbreak attempts",
        "risk_score": regex_result.get('risk_score', 0),
        "status": get_filter_status(regex_result.get('risk_score', 0)),
        "reason": regex_result.get('reason', 'No patterns detected'),
        "matches": regex_result.get('matches', []),
        "categories_detected": regex_result.get('categories_detected', []),
        "match_count": regex_result.get('match_count', 0),
        "severity_level": regex_result.get('severity_level', 'LOW'),
        "details": {
            "patterns_checked": ["jailbreak", "injection", "leakage", "obfuscation"],
            "threat_indicators": len(regex_result.get('matches', [])),
            "confidence": "high" if regex_result.get('match_count', 0) > 0 else "low"
        }
    }
    
    # Obfuscation Detector Details
    obf_result = filter_results.get('obfuscation_detector', {})
    detailed_filters['obfuscation_detector'] = {
        "name": "Obfuscation Detection",
        "description": "Identifies attempts to hide malicious content through encoding",
        "risk_score": obf_result.get('obfuscation_score', 0),
        "status": get_filter_status(obf_result.get('obfuscation_score', 0)),
        "reason": obf_result.get('reason', 'No obfuscation detected'),
        "is_obfuscated": obf_result.get('is_obfuscated', False),
        "techniques_found": obf_result.get('techniques_found', []),
        "decoded_prompt": obf_result.get('decoded_prompt', ''),
        "details": {
            "encoding_types": [t.get('type', '') for t in obf_result.get('techniques_found', [])],
            "obfuscation_methods": len(obf_result.get('techniques_found', [])),
            "confidence": "high" if obf_result.get('is_obfuscated', False) else "low"
        }
    }
    
    # ML Classifier Details
    ml_result = filter_results.get('ml_classifier', {})
    detailed_filters['ml_classifier'] = {
        "name": "AI/ML Analysis",
        "description": "Advanced machine learning models for toxicity and threat detection",
        "risk_score": ml_result.get('risk_score', 0),
        "status": get_filter_status(ml_result.get('risk_score', 0)),
        "reason": ml_result.get('reason', 'No ML threats detected'),
        "confidence": ml_result.get('confidence', 'low'),
        "is_threat": ml_result.get('is_threat', False),
        "ml_results": ml_result.get('ml_results', []),
        "model_info": ml_result.get('model_info', {}),
        "details": {
            "models_used": get_ml_models_used(ml_result.get('ml_results', [])),
            "toxicity_score": get_toxicity_score(ml_result.get('ml_results', [])),
            "similarity_score": get_similarity_score(ml_result.get('ml_results', [])),
            "confidence_level": ml_result.get('confidence', 'medium')
        }
    }
    
    # Add enhanced filter details to result
    result['detailed_filters'] = detailed_filters
    result['filter_summary'] = {
        "total_filters": len(detailed_filters),
        "filters_triggered": sum(1 for f in detailed_filters.values() if f['risk_score'] > 0.1),
        "highest_risk_filter": max(detailed_filters.keys(), 
                                 key=lambda k: detailed_filters[k]['risk_score']) if detailed_filters else None,
        "overall_confidence": calculate_overall_confidence(detailed_filters)
    }
    
    return result

def extract_filter_details(result):
    """Extract detailed filter information for the filters endpoint."""
    filter_results = result.get('filter_results', {})
    details = {}
    
    for filter_name, filter_data in filter_results.items():
        details[filter_name] = {
            "risk_score": filter_data.get('risk_score', 0),
            "reason": filter_data.get('reason', 'No details available'),
            "status": get_filter_status(filter_data.get('risk_score', 0)),
            "raw_data": filter_data
        }
    
    return details

def get_filter_status(risk_score):
    """Get human-readable status based on risk score."""
    if risk_score >= 0.8:
        return "CRITICAL"
    elif risk_score >= 0.6:
        return "HIGH"
    elif risk_score >= 0.4:
        return "MEDIUM"
    elif risk_score >= 0.2:
        return "LOW"
    else:
        return "SAFE"

def get_ml_models_used(ml_results):
    """Extract which ML models were used."""
    models = []
    for result in ml_results:
        method = result.get('method', '')
        if method not in models:
            models.append(method)
    return models

def get_toxicity_score(ml_results):
    """Extract toxicity score from ML results."""
    for result in ml_results:
        if result.get('method') == 'toxicity_classification':
            return result.get('score', 0)
    return 0

def get_similarity_score(ml_results):
    """Extract similarity score from ML results."""
    for result in ml_results:
        if result.get('method') == 'similarity_analysis':
            return result.get('score', 0)
    return 0

def calculate_overall_confidence(detailed_filters):
    """Calculate overall confidence based on all filters."""
    confidences = []
    for filter_data in detailed_filters.values():
        conf = filter_data['details'].get('confidence', 'low')
        if conf == 'high':
            confidences.append(3)
        elif conf == 'medium':
            confidences.append(2)
        else:
            confidences.append(1)
    
    if not confidences:
        return 'low'
    
    avg_conf = sum(confidences) / len(confidences)
    if avg_conf >= 2.5:
        return 'high'
    elif avg_conf >= 1.5:
        return 'medium'
    else:
        return 'low'