from datetime import datetime, timezone
from typing import Dict, Any
from backend.models import db

class ThreatLog(db.Model):
    """Model for storing LLM security threat logs."""
    
    __tablename__ = 'threat_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    sanitized_prompt = db.Column(db.Text, nullable=True)
    attack_type = db.Column(db.String(100), nullable=True)
    risk_score = db.Column(db.Float, nullable=False, default=0.0)
    blocked = db.Column(db.Boolean, nullable=False, default=False)
    model_used = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, 
                          default=lambda: datetime.now(timezone.utc))
    
    # Additional fields for better analytics
    user_id = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    processing_time = db.Column(db.Float, nullable=True)
    
    def __repr__(self):
        return f'<ThreatLog {self.id}: {self.attack_type} - Risk: {self.risk_score}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        return {
            'id': self.id,
            'prompt': self.prompt,
            'sanitized_prompt': self.sanitized_prompt,
            'attack_type': self.attack_type,
            'risk_score': self.risk_score,
            'blocked': self.blocked,
            'model_used': self.model_used,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'processing_time': self.processing_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def create_from_analysis(cls, prompt: str, analysis_result: Dict[str, Any], 
                           user_id: str = None, ip: str = None) -> 'ThreatLog':
        """Create ThreatLog from security analysis result."""
        return cls(
            prompt=prompt,
            sanitized_prompt=analysis_result.get('processed_prompt'),
            attack_type=analysis_result.get('primary_threat'),
            risk_score=analysis_result.get('risk_score', 0.0),
            blocked=analysis_result.get('decision') == 'BLOCK',
            model_used=analysis_result.get('model_used', 'unknown'),
            user_id=user_id,
            ip_address=ip,
            processing_time=analysis_result.get('processing_time_seconds')
        )