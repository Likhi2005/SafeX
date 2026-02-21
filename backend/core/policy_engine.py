import logging
from typing import Dict, List, Any, Tuple
from enum import Enum
from backend.config.constants import DECISION_THRESHOLDS, RISK_THRESHOLDS


class Decision(Enum):
    """Security decision types."""
    ALLOW = "ALLOW"
    SANITIZE = "SANITIZE"
    BLOCK = "BLOCK"
    
    
class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    
    
class PolicyEngine:
    """
    Central policy engine that combines results from all security filters and makes final decisions about prompt handling.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        
        # Decision weights for each filter
        self.filter_weights = {
            "regex_filter": 0.4,
            "obfuscation_detector": 0.2,
            "ml_classifier": 0.4
        }
    
    
    def evaluate(self, prompt: str, filter_results: Dict[str, Any]) -> Dict[str, Any]:
        
        """
        Evaluate all filter results and make final security decision.
        
        Args:
            prompt: Original user prompt
            filter_results: Combined results from all security filters
            
        Returns:
            Final policy decision with risk assessment
        """
        try:
            # Calculate weighted risk score
            risk_score = self._calculate_weighted_risk(filter_results)
            
            # Determine risk level
            risk_level = self._assess_risk_level(risk_score)
            
            # Make policy decision
            decision = self._make_decision(risk_score, filter_results)
            
            # Generate explanation
            explanation = self._generate_explanation(decision, filter_results, risk_score)
            
            # Compile decision report
            return self._create_decision_report(
                prompt, decision, risk_score, risk_level, explanation, filter_results
            )
            
        except Exception as e:
            self.logger.error(f"Policy evaluation failed: {e}")
            # Fail-safe: block on error
            return self._create_error_decision(prompt, str(e))
        
    def _calculate_weighted_risk(self, filter_results: Dict[str, Any]) -> float:
        """Calculate weighted risk score from all filters."""
        total_score = 0.0
        total_weight = 0.0
        
        for filter_name, weight in self.filter_weights.items():
            if filter_name in filter_results:
                filter_result = filter_results[filter_name]
                filter_score = filter_result.get("risk_score", 0.0)
                
                
                # Handle obfuscation detector special case
                if filter_name == "obfuscation_detector":
                    filter_score = filter_result.get("obfuscation_score", 0.0)
                    
                total_score += filter_score * weight
                total_weight += weight
                
                self.logger.debug(f"{filter_name}: score={filter_score}, weight={weight}")
                
        
        # Normalize by total weight used
        if total_weight > 0:
            weighted_score = total_score / total_weight
        else:
            weighted_score = 0.0
            
        # Apply escalation rules
        escalated_score = self._apply_escalation_rules(filter_results, weighted_score)
        
        return round(min(escalated_score,1.0), 3)
    
    
    def _apply_escalation_rules(self, filter_results: Dict[str, Any], base_score: float) -> float:
        """Apply escalation rules for specific filter combinations."""
        escalation_bonus = 0.0
        
        # Rule 1: Multiple filter detections
        active_filters = sum(1 for result in filter_results.values()
                             if result.get("risk_score", 0.0) > 0.2 or
                             result.get("obfuscation_score", 0.0) > 0.2)
        
        if active_filters >= 2:
            escalation_bonus += 0.15
            self.logger.info(f"Escalation: Multiple filters triggered ({active_filters})")
            
        # Rule 2: High-confidence ML detection
        ml_result = filter_results.get("ml_classifier", {})
        if ml_result.get("risk_score", 0.0) > 0.7:
            escalation_bonus += 0.1
            self.logger.info("Escalation: High-confidence ML detection")
            
        
        # Rule 3: obfuscation + Attack pattern
        obf_result = filter_results.get("obfuscation_detector", {})
        regex_result = filter_results.get("regex_filter", {})
        
        if (obf_result.get("obfuscation_score",0.0) > 0.3 and
            regex_result.get("risk_score", 0.0) > 0.5):
            escalation_bonus += 0.2
            self.logger.info("Escalation: Obfuscation + Attack pattern detected")
            
        return base_score + escalation_bonus
    
    def _assess_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on score."""
        if risk_score >= RISK_THRESHOLDS["CRITICAL"]:
            return RiskLevel.CRITICAL
        elif risk_score >= RISK_THRESHOLDS["HIGH"]:
            return RiskLevel.HIGH
        elif risk_score >= RISK_THRESHOLDS["MEDIUM"]:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
        
    def _make_decision(self, risk_score: float, filter_results: Dict[str, Any]) -> Decision:
        """Make final policy decision based on risk assessment."""
        
        # Critical threats: Always block
        if risk_score >= DECISION_THRESHOLDS["BLOCK"]:
            return Decision.BLOCK
        
        # Medium-high threats: Sanitize if possible, otherwise block
        elif risk_score >= DECISION_THRESHOLDS["SANITIZE"]:
            # Check if sanitization is viable
            if self._is_sanitizable(filter_results):
                return Decision.SANITIZE
            else:
                return Decision.BLOCK
        
        # Low threats: Allow with monitoring
        else:
            return Decision.ALLOW
        
    
    def _is_sanitizable(self, filter_results: Dict[str, Any]) -> bool:
        """Determine if prompt can be safely sanitized."""
        
        # Don't sanitize if ML confidence is very high (likely sophisticated attack)
        ml_result = filter_results.get("ml_classifier", {})
        if ml_result.get("risk_score", 0.0) > 0.8:
            return False
        
        # Don't sanitize if multiple attack categories detected
        regex_result = filter_results.get("regex_filter", {})
        categories = regex_result.get("categories_detected", [])
        if len(categories) > 2:
            return False
        
        # Don't sanitize heavy obfuscation (indicates intent to bypass)
        obf_result = filter_results.get("obfuscation_detector", {})
        if obf_result.get("obfuscation_score", 0.0) > 0.7:
            return False
        
        return True
    
    def _generate_explanation(self, decision: Decision, filter_results: Dict[str, Any], risk_score: float) -> str:
        """Generate human-readable explanation for the decision."""
        
        explanations = []
        
        # Add filter-specific explanations
        for filter_name, result in filter_results.items():
            if filter_name == "regex_filter" and result.get("risk_score", 0.0) > 0.1:
                explanations.append(f"Pattern matching: {result.get('reason', 'Unknown')}")
                
            elif filter_name == "obfuscation_detector" and result.get("obfuscation_score", 0.0) > 0.1:
                explanations.append(f"Obfuscation: {result.get('reason', 'Unknown')}")
                
            elif filter_name == "ml_classifier" and result.get("risk_score", 0.0) > 0.1:
                explanations.append(f"ML analysis: {result.get('reason', 'Unknown')}")
        
        base_explanation = "; ".join(explanations) if explanations else "No threats detected"
        
        # Add decision reasoning
        if decision == Decision.BLOCK:
            return f"BLOCKED - {base_explanation} (Risk: {risk_score:.3f})"
        elif decision == Decision.SANITIZE:
            return f"SANITIZE - {base_explanation} (Risk: {risk_score:.3f})"
        else:
            return f"ALLOWED - {base_explanation} (Risk: {risk_score:.3f})"
      
      
        
    def _create_decision_report(self, prompt: str, decision: Decision, risk_score: float,
                              risk_level: RiskLevel, explanation: str, 
                              filter_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive decision report."""
        return {
            "decision": decision.value,
            "risk_score": risk_score,
            "risk_level": risk_level.value,
            "explanation": explanation,
            "original_prompt": prompt,
            "filter_results": filter_results,
            "timestamp": self._get_timestamp(),
            "policy_version": "1.0.0"
        }
       
       
        
    def _create_error_decision(self, prompt: str, error: str) -> Dict[str, Any]:
        """Create fail-safe decision on error."""
        return {
            "decision": Decision.BLOCK.value,
            "risk_score": 1.0,
            "risk_level": RiskLevel.CRITICAL.value,
            "explanation": f"BLOCKED due to evaluation error: {error}",
            "original_prompt": prompt,
            "error": error,
            "timestamp": self._get_timestamp(),
            "policy_version": "1.0.0"
        }
        
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    
# Global policy engine instance
policy_engine = PolicyEngine()

def evaluate_prompt_security(prompt: str, filter_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function for policy evaluation.
    Args:
        prompt: Original user prompt
        filter_results: Results from all security filters
        
    Returns:
        Policy decision report
    """
    return policy_engine.evaluate(prompt, filter_results)
    