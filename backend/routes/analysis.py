from flask import Blueprint, jsonify, request, current_app
import logging
from datetime import datetime, timezone, timedelta
from backend.core.security_pipeline import analyze_prompt_security

from backend.models.threat_log import ThreatLog
from backend.services.threat_service import ThreatLogService

# Add SQLAlchemy imports for the trends endpoint
from backend.models import db
from sqlalchemy import func, cast, Date

# analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/v1')
analysis_bp = Blueprint('analysis', __name__)
logger = logging.getLogger(__name__)




@analysis_bp.route('/api/threat-trends', methods=['GET'])  # Keep /api/ in route
def get_threat_trends():
    """Get threat trends over time for charts using real database data."""
    try:
        days = int(request.args.get('days', 7))
        
        # Input validation
        if days < 1 or days > 365:
            return jsonify({
                'status': 'error',
                'message': 'Days parameter must be between 1 and 365'
            }), 400
        
        # Calculate date range
        end_date = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
        start_date = (end_date - timedelta(days=days-1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        logger.info(f"Fetching threat trends from {start_date} to {end_date} ({days} days)")
        
        # PostgreSQL-compatible query to group by date
        daily_query = db.session.query(
            cast(ThreatLog.created_at, Date).label('date'),
            func.count(ThreatLog.id).label('total'),
            func.sum(cast(ThreatLog.blocked, 'integer')).label('blocked'),
            func.count(ThreatLog.id) - func.sum(cast(ThreatLog.blocked, 'integer')).label('allowed')
        ).filter(
            ThreatLog.created_at >= start_date,
            ThreatLog.created_at <= end_date
        ).group_by(
            cast(ThreatLog.created_at, Date)
        ).order_by(
            cast(ThreatLog.created_at, Date)
        ).all()
        
        # Get total period statistics
        period_totals = db.session.query(
            func.count(ThreatLog.id).label('total_requests'),
            func.sum(cast(ThreatLog.blocked, 'integer')).label('total_blocked'),
            func.count(ThreatLog.id) - func.sum(cast(ThreatLog.blocked, 'integer')).label('total_allowed'),
            func.avg(ThreatLog.risk_score).label('avg_risk_score'),
            func.avg(ThreatLog.processing_time).label('avg_processing_time')
        ).filter(
            ThreatLog.created_at >= start_date,
            ThreatLog.created_at <= end_date
        ).first()
        
        # Get top attack types for the period
        top_attack_types = db.session.query(
            ThreatLog.attack_type,
            func.count(ThreatLog.id).label('count'),
            func.avg(ThreatLog.risk_score).label('avg_risk')
        ).filter(
            ThreatLog.created_at >= start_date,
            ThreatLog.created_at <= end_date,
            ThreatLog.attack_type.isnot(None),
            ThreatLog.attack_type != ''
        ).group_by(
            ThreatLog.attack_type
        ).order_by(
            func.count(ThreatLog.id).desc()
        ).limit(10).all()
        
        # Create complete daily data (fill in missing days with zeros)
        daily_data = {}
        for row in daily_query:
            date_str = row.date.strftime('%Y-%m-%d')
            daily_data[date_str] = {
                'date': date_str,
                'total': int(row.total or 0),
                'blocked': int(row.blocked or 0),
                'allowed': int(row.allowed or 0),
                'block_rate': round((row.blocked or 0) / max(row.total or 1, 1) * 100, 2)
            }
        
        # Fill in missing days with zeros
        complete_daily_counts = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            if date_str in daily_data:
                complete_daily_counts.append(daily_data[date_str])
            else:
                complete_daily_counts.append({
                    'date': date_str,
                    'total': 0,
                    'blocked': 0,
                    'allowed': 0,
                    'block_rate': 0.0
                })
            current_date += timedelta(days=1)
        
        # Prepare period statistics
        total_requests = int(period_totals.total_requests or 0)
        total_blocked = int(period_totals.total_blocked or 0)
        total_allowed = int(period_totals.total_allowed or 0)
        
        period_stats = {
            'requests': total_requests,
            'blocked': total_blocked,
            'allowed': total_allowed,
            'block_rate': round(total_blocked / max(total_requests, 1) * 100, 2) if total_requests > 0 else 0.0,
            'avg_risk_score': round(float(period_totals.avg_risk_score or 0), 3),
            'avg_processing_time': round(float(period_totals.avg_processing_time or 0) * 1000, 2)  # Convert to ms
        }
        
        # Prepare attack types data
        attack_types_data = [
            {
                'type': row.attack_type,
                'count': int(row.count),
                'avg_risk': round(float(row.avg_risk or 0), 3),
                'percentage': round(row.count / max(total_requests, 1) * 100, 2) if total_requests > 0 else 0.0
            }
            for row in top_attack_types
        ]
        
        trends_response = {
            'daily_counts': complete_daily_counts,
            'total_period': period_stats,
            'top_attack_types': attack_types_data,
            'date_range': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d'),
                'days': days
            }
        }
        
        logger.info(f"Threat trends retrieved: {total_requests} total requests over {days} days")
        
        return jsonify({
            'status': 'success',
            'trends': trends_response,
            'period_days': days,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except ValueError as ve:
        logger.warning(f"Invalid parameter in threat trends: {ve}")
        return jsonify({
            'status': 'error',
            'message': 'Invalid parameters provided'
        }), 400
        
    except Exception as e:
        logger.error(f"Failed to get threat trends: {e}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch threat trends',
            'details': str(e) if current_app.debug else 'Contact administrator'
        }), 500
        
        

@analysis_bp.route('/api/analyze', methods=['POST'])
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

@analysis_bp.route('/api//analyze/filters', methods=['POST'])
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
    
@analysis_bp.route('/api/threats', methods=['GET'])  
def get_threats():
    """Get recent threat logs - this endpoint was missing!"""
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

@analysis_bp.route('/api/threat-stats', methods=['GET'])
def get_threat_statistics():
    """Get threat analysis statistics - this endpoint was missing!"""
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