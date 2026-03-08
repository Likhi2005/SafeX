"""
Advanced Threat Intelligence Service for real-time threat analysis and prediction.
"""

import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
import json
from backend.models import db
from backend.models.threat_log import ThreatLog
from sqlalchemy import func, desc
import hashlib

logger = logging.getLogger(__name__)

class ThreatIntelligenceService:
    """Advanced threat intelligence and analytics service."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_real_time_threats(self, minutes: int = 30) -> Dict[str, Any]:
        """Get real-time threat data for live dashboard."""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
            
            # Get recent threats with geolocation simulation
            recent_threats = db.session.query(ThreatLog).filter(
                ThreatLog.created_at >= cutoff_time
            ).order_by(desc(ThreatLog.created_at)).limit(100).all()
            
            # Process for real-time display
            processed_threats = []
            for threat in recent_threats:
                # Simulate geolocation based on IP (for demo purposes)
                lat, lng = self._simulate_geolocation(threat.ip_address)
                
                processed_threats.append({
                    'id': threat.id,
                    'timestamp': threat.created_at.isoformat(),
                    'risk_score': threat.risk_score,
                    'attack_type': threat.attack_type,
                    'blocked': threat.blocked,
                    'location': {'lat': lat, 'lng': lng},
                    'country': self._get_country_from_ip(threat.ip_address),
                    'severity': self._get_severity_level(threat.risk_score)
                })
            
            # Calculate threat metrics
            threat_stats = self._calculate_real_time_stats(recent_threats)
            
            return {
                'threats': processed_threats,
                'stats': threat_stats,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'period_minutes': minutes
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get real-time threats: {e}")
            return {'threats': [], 'stats': {}, 'error': str(e)}
    
    def detect_attack_patterns(self, hours: int = 24) -> Dict[str, Any]:
        """Detect coordinated attack patterns and campaigns."""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            # Get threats for pattern analysis
            threats = db.session.query(ThreatLog).filter(
                ThreatLog.created_at >= cutoff_time,
                ThreatLog.risk_score > 0.3
            ).all()
            
            # Analyze patterns
            patterns = {
                'attack_campaigns': self._detect_campaigns(threats),
                'threat_clusters': self._cluster_threats(threats),
                'time_patterns': self._analyze_time_patterns(threats),
                'source_analysis': self._analyze_attack_sources(threats)
            }
            
            return {
                'patterns': patterns,
                'analysis_period_hours': hours,
                'threats_analyzed': len(threats),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to detect attack patterns: {e}")
            return {'patterns': {}, 'error': str(e)}
    
    def get_threat_predictions(self) -> Dict[str, Any]:
        """Generate threat predictions based on historical data."""
        try:
            # Analyze historical trends
            historical_data = self._get_historical_trends(days=14)
            
            # Generate predictions
            predictions = {
                'next_hour_risk': self._predict_next_hour_risk(historical_data),
                'trending_attacks': self._predict_trending_attacks(historical_data),
                'risk_hotspots': self._identify_risk_hotspots(historical_data),
                'threat_forecast': self._generate_threat_forecast(historical_data)
            }
            
            return {
                'predictions': predictions,
                'confidence': 'medium',  # This would be calculated based on data quality
                'forecast_horizon': '24_hours',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate predictions: {e}")
            return {'predictions': {}, 'error': str(e)}
    
    def _simulate_geolocation(self, ip_address: str) -> Tuple[float, float]:
        """Simulate geolocation for demo purposes."""
        if not ip_address:
            return 40.7128, -74.0060  # Default to NYC
        
        # Use IP hash to generate consistent coordinates
        hash_val = int(hashlib.md5(ip_address.encode()).hexdigest()[:8], 16)
        
        # Generate realistic coordinates (major cities)
        cities = [
            (40.7128, -74.0060),   # New York
            (34.0522, -118.2437),  # Los Angeles  
            (51.5074, -0.1278),    # London
            (35.6762, 139.6503),   # Tokyo
            (52.5200, 13.4050),    # Berlin
            (48.8566, 2.3522),     # Paris
        ]
        
        return cities[hash_val % len(cities)]
    
    def _get_country_from_ip(self, ip_address: str) -> str:
        """Simulate country detection."""
        if not ip_address:
            return "Unknown"
        
        # Simple simulation based on IP hash
        countries = ["USA", "UK", "Germany", "Japan", "France", "Canada", "Australia"]
        hash_val = int(hashlib.md5(ip_address.encode()).hexdigest()[:2], 16)
        return countries[hash_val % len(countries)]
    
    def _get_severity_level(self, risk_score: float) -> str:
        """Convert risk score to severity level."""
        if risk_score >= 0.8:
            return "critical"
        elif risk_score >= 0.6:
            return "high"
        elif risk_score >= 0.3:
            return "medium"
        else:
            return "low"
    
    def _calculate_real_time_stats(self, threats: List[ThreatLog]) -> Dict[str, Any]:
        """Calculate real-time statistics."""
        if not threats:
            return {}
        
        total_threats = len(threats)
        blocked_count = sum(1 for t in threats if t.blocked)
        avg_risk = sum(t.risk_score for t in threats) / total_threats
        
        # Attack type distribution
        attack_types = Counter(t.attack_type for t in threats if t.attack_type)
        
        return {
            'total_threats': total_threats,
            'blocked_count': blocked_count,
            'allow_count': total_threats - blocked_count,
            'block_rate': (blocked_count / total_threats) * 100,
            'avg_risk_score': round(avg_risk, 3),
            'attack_distribution': dict(attack_types.most_common(5)),
            'critical_threats': sum(1 for t in threats if t.risk_score >= 0.8)
        }
    
    def _detect_campaigns(self, threats: List[ThreatLog]) -> List[Dict[str, Any]]:
        """Detect coordinated attack campaigns."""
        campaigns = []
        
        # Group by attack type and time proximity
        attack_groups = defaultdict(list)
        for threat in threats:
            if threat.attack_type:
                attack_groups[threat.attack_type].append(threat)
        
        # Identify potential campaigns (simplified)
        for attack_type, group_threats in attack_groups.items():
            if len(group_threats) >= 3:  # Minimum for campaign
                campaigns.append({
                    'campaign_id': f"camp_{attack_type}_{len(group_threats)}",
                    'attack_type': attack_type,
                    'threat_count': len(group_threats),
                    'avg_risk': sum(t.risk_score for t in group_threats) / len(group_threats),
                    'time_span': self._get_time_span(group_threats),
                    'severity': 'high' if len(group_threats) > 10 else 'medium'
                })
        
        return campaigns[:5]  # Return top 5 campaigns
    
    def _cluster_threats(self, threats: List[ThreatLog]) -> List[Dict[str, Any]]:
        """Cluster similar threats."""
        clusters = []
        
        # Simple clustering by prompt similarity (for demo)
        prompt_groups = defaultdict(list)
        for threat in threats:
            # Group by first 20 characters as simple clustering
            key = threat.prompt[:20] if threat.prompt else "unknown"
            prompt_groups[key].append(threat)
        
        # Create clusters from groups
        for i, (key, group) in enumerate(prompt_groups.items()):
            if len(group) > 1:
                clusters.append({
                    'cluster_id': f"cluster_{i}",
                    'pattern': key,
                    'size': len(group),
                    'avg_risk': sum(t.risk_score for t in group) / len(group),
                    'attack_types': list(set(t.attack_type for t in group if t.attack_type))
                })
        
        return sorted(clusters, key=lambda x: x['size'], reverse=True)[:5]
    
    def _analyze_time_patterns(self, threats: List[ThreatLog]) -> Dict[str, Any]:
        """Analyze temporal attack patterns."""
        if not threats:
            return {}
        
        # Hourly distribution
        hourly_counts = defaultdict(int)
        for threat in threats:
            hour = threat.created_at.hour
            hourly_counts[hour] += 1
        
        # Find peak hours
        peak_hour = max(hourly_counts, key=hourly_counts.get) if hourly_counts else 0
        
        return {
            'hourly_distribution': dict(hourly_counts),
            'peak_hour': peak_hour,
            'peak_count': hourly_counts[peak_hour],
            'pattern_type': 'concentrated' if max(hourly_counts.values()) > len(threats) * 0.3 else 'distributed'
        }
    
    def _analyze_attack_sources(self, threats: List[ThreatLog]) -> Dict[str, Any]:
        """Analyze attack source patterns."""
        source_analysis = {
            'unique_ips': len(set(t.ip_address for t in threats if t.ip_address)),
            'repeat_attackers': [],
            'top_countries': []
        }
        
        # Count attacks per IP
        ip_counts = Counter(t.ip_address for t in threats if t.ip_address)
        
        # Identify repeat attackers
        for ip, count in ip_counts.most_common(5):
            if count > 2:  # More than 2 attacks
                source_analysis['repeat_attackers'].append({
                    'ip': ip,
                    'attack_count': count,
                    'country': self._get_country_from_ip(ip)
                })
        
        # Country distribution
        country_counts = Counter(self._get_country_from_ip(t.ip_address) for t in threats if t.ip_address)
        source_analysis['top_countries'] = [
            {'country': country, 'count': count} 
            for country, count in country_counts.most_common(5)
        ]
        
        return source_analysis
    
    def _get_historical_trends(self, days: int) -> List[Dict[str, Any]]:
        """Get historical threat trends."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        daily_stats = db.session.query(
            func.date(ThreatLog.created_at).label('date'),
            func.count(ThreatLog.id).label('count'),
            func.avg(ThreatLog.risk_score).label('avg_risk'),
            func.sum(func.cast(ThreatLog.blocked, 'integer')).label('blocked')
        ).filter(
            ThreatLog.created_at >= cutoff_date
        ).group_by(
            func.date(ThreatLog.created_at)
        ).order_by('date').all()
        
        return [
            {
                'date': row.date.strftime('%Y-%m-%d'),
                'count': int(row.count),
                'avg_risk': float(row.avg_risk or 0),
                'blocked': int(row.blocked or 0)
            }
            for row in daily_stats
        ]
    
    def _predict_next_hour_risk(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Predict risk level for next hour."""
        if not historical_data:
            return {'level': 'low', 'confidence': 0.5}
        
        # Simple prediction based on recent trend
        recent_avg_risk = sum(d['avg_risk'] for d in historical_data[-3:]) / min(3, len(historical_data))
        
        if recent_avg_risk >= 0.7:
            level = 'high'
        elif recent_avg_risk >= 0.4:
            level = 'medium'  
        else:
            level = 'low'
        
        return {
            'level': level,
            'risk_score': round(recent_avg_risk, 3),
            'confidence': 0.75,
            'trend': 'increasing' if len(historical_data) > 1 and historical_data[-1]['avg_risk'] > historical_data[-2]['avg_risk'] else 'stable'
        }
    
    def _predict_trending_attacks(self, historical_data: List[Dict]) -> List[str]:
        """Predict which attack types might trend."""
        # This would use more sophisticated ML in production
        trending = ['prompt_injection', 'jailbreak_attempt', 'data_leakage']
        return trending[:3]
    
    def _identify_risk_hotspots(self, historical_data: List[Dict]) -> List[Dict[str, Any]]:
        """Identify geographical risk hotspots."""
        # Simulated hotspots for demo
        return [
            {'location': 'North America', 'risk_level': 0.6, 'threat_count': 45},
            {'location': 'Europe', 'risk_level': 0.4, 'threat_count': 32},
            {'location': 'Asia', 'risk_level': 0.7, 'threat_count': 38}
        ]
    
    def _generate_threat_forecast(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Generate 24-hour threat forecast."""
        if not historical_data:
            return {}
        
        current_trend = historical_data[-1]['count'] if historical_data else 10
        
        return {
            'expected_threats_24h': int(current_trend * 1.2),  # Simple projection
            'confidence_interval': [int(current_trend * 0.8), int(current_trend * 1.5)],
            'key_risks': ['Automated attacks', 'Social engineering', 'Model exploitation']
        }
    
    def _get_time_span(self, threats: List[ThreatLog]) -> str:
        """Calculate time span of threat group."""
        if len(threats) < 2:
            return "instant"
        
        times = [t.created_at for t in threats]
        span = max(times) - min(times)
        
        if span.total_seconds() < 3600:  # Less than 1 hour
            return f"{int(span.total_seconds() / 60)} minutes"
        elif span.total_seconds() < 86400:  # Less than 1 day
            return f"{int(span.total_seconds() / 3600)} hours"
        else:
            return f"{span.days} days"

# Global service instance
threat_intelligence = ThreatIntelligenceService()