from flask import current_app
from typing import Dict, Any, List, Optional
from backend.models import db
from backend.models.threat_log import ThreatLog
import logging

logger = logging.getLogger(__name__)

class ThreatLogService:
    """Service for managing threat logs."""
    
    @staticmethod
    def log_threat(prompt: str, analysis_result: Dict[str, Any], 
                  user_id: str = None, ip_address: str = None) -> Optional[ThreatLog]:
        """Log a threat analysis result to the database."""
        try:
            threat_log = ThreatLog.create_from_analysis(
                prompt=prompt,
                analysis_result=analysis_result,
                user_id=user_id,
                ip=ip_address
            )
            
            db.session.add(threat_log)
            db.session.commit()
            
            logger.info(f"Logged threat: {threat_log.id} - {threat_log.attack_type}")
            return threat_log
            
        except Exception as e:
            logger.error(f"Failed to log threat: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_recent_threats(limit: int = 100) -> List[ThreatLog]:
        """Get recent threat logs."""
        try:
            return ThreatLog.query.order_by(
                ThreatLog.created_at.desc()
            ).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to fetch recent threats: {e}")
            return []
    
    @staticmethod
    def get_threat_stats() -> Dict[str, Any]:
        """Get threat statistics."""
        try:
            total = ThreatLog.query.count()
            blocked = ThreatLog.query.filter_by(blocked=True).count()
            
            # Get most common attack types
            attack_types = db.session.query(
                ThreatLog.attack_type,
                db.func.count(ThreatLog.id).label('count')
            ).group_by(ThreatLog.attack_type).all()
            
            return {
                'total_threats': total,
                'blocked_threats': blocked,
                'allowed_threats': total - blocked,
                'block_rate': (blocked / total * 100) if total > 0 else 0,
                'attack_types': [
                    {'type': at[0], 'count': at[1]} 
                    for at in attack_types
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get threat stats: {e}")
            return {}