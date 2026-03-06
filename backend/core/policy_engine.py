import logging
from typing import Dict, List, Any, Tuple
from enum import Enum
from datetime import datetime

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
    Central policy engine that combines results from all security filters 
    and makes final decisions about prompt handling.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Default thresholds (fallback if constants not available)
        self.decision_thresholds = {
            "BLOCK": 0.7,      # Block if risk >= 70%
            "SANITIZE": 0.4,   # Sanitize if risk >= 40%
            # ALLOW if risk < 40%
        }
        
        self.risk_thresholds = {
            "CRITICAL": 0.8,   # Critical if risk >= 80%
            "HIGH": 0.6,       # High if risk >= 60%
            "MEDIUM": 0.3,     # Medium if risk >= 30%
            # LOW if risk < 30%
        }
        
        # Load from constants file if available
        try:
            from backend.config.constants import DECISION_THRESHOLDS, RISK_THRESHOLDS
            self.decision_thresholds = DECISION_THRESHOLDS
            self.risk_thresholds = RISK_THRESHOLDS
        except ImportError:
            self.logger.warning("Constants not found, using default thresholds")
        
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
            self.logger.debug(f"Evaluating policy for prompt: {prompt[:50]}...")
            
            # Validate input
            if not isinstance(filter_results, dict):
                return self._create_error_decision(prompt, "Invalid filter results")
            
            # Calculate weighted risk score
            risk_score = self._calculate_weighted_risk(filter_results)
            
            # Determine risk level
            risk_level = self._assess_risk_level(risk_score)
            
            # Make policy decision
            decision = self._make_decision(risk_score, filter_results)
            
            # Generate explanation
            explanation = self._generate_explanation(decision, filter_results, risk_score)
            
            # Add confidence rating
            confidence = self._calculate_confidence(filter_results, risk_score)
            
            self.logger.info(f"Policy decision: {decision.value} (risk: {risk_score:.3f}, confidence: {confidence})")
            
            # Compile decision report
            return self._create_decision_report(
                prompt, decision, risk_score, risk_level, explanation, filter_results, confidence
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
                
                # Validate filter result
                if not isinstance(filter_result, dict):
                    self.logger.warning(f"Invalid filter result for {filter_name}")
                    continue
                
                # Get risk score with validation
                if filter_name == "obfuscation_detector":
                    # For obfuscation, use obfuscation_score as risk indicator
                    filter_score = filter_result.get("obfuscation_score", 0.0)
                else:
                    filter_score = filter_result.get("risk_score", 0.0)
                
                # Validate score
                if not isinstance(filter_score, (int, float)) or filter_score < 0:
                    filter_score = 0.0
                elif filter_score > 1.0:
                    filter_score = 1.0
                    
                total_score += filter_score * weight
                total_weight += weight
                
                self.logger.debug(f"{filter_name}: score={filter_score:.3f}, weight={weight}")
        
        # Normalize by total weight used
        if total_weight > 0:
            weighted_score = total_score / total_weight
        else:
            self.logger.warning("No valid filter results for scoring")
            weighted_score = 0.0
            
        # Apply escalation rules
        escalated_score = self._apply_escalation_rules(filter_results, weighted_score)
        
        return round(min(escalated_score, 1.0), 3)
    
    def _apply_escalation_rules(self, filter_results: Dict[str, Any], base_score: float) -> float:
        """Apply escalation rules for specific filter combinations."""
        escalation_bonus = 0.0
        applied_rules = []
        
        # Rule 1: Multiple filter detections
        active_filters = 0
        for filter_name, result in filter_results.items():
            if isinstance(result, dict):
                risk_score = result.get("risk_score", 0.0)
                obf_score = result.get("obfuscation_score", 0.0)
                if risk_score > 0.2 or obf_score > 0.2:
                    active_filters += 1
        
        if active_filters >= 2:
            escalation_bonus += 0.15
            applied_rules.append(f"Multiple filters triggered ({active_filters})")
            
        # Rule 2: High-confidence ML detection
        ml_result = filter_results.get("ml_classifier", {})
        if isinstance(ml_result, dict):
            ml_score = ml_result.get("risk_score", 0.0)
            ml_confidence = ml_result.get("confidence", "low")
            
            if ml_score > 0.7 and ml_confidence in ["high", "medium"]:
                escalation_bonus += 0.1
                applied_rules.append("High-confidence ML detection")
        
        # Rule 3: Obfuscation + Attack pattern combination
        obf_result = filter_results.get("obfuscation_detector", {})
        regex_result = filter_results.get("regex_filter", {})
        
        if (isinstance(obf_result, dict) and isinstance(regex_result, dict)):
            obf_score = obf_result.get("obfuscation_score", 0.0)
            regex_score = regex_result.get("risk_score", 0.0)
            
            if obf_score > 0.3 and regex_score > 0.5:
                escalation_bonus += 0.2
                applied_rules.append("Obfuscation + Attack pattern detected")
        
        # Rule 4: High category diversity in regex matches
        regex_result = filter_results.get("regex_filter", {})
        if isinstance(regex_result, dict):
            categories = regex_result.get("categories_detected", [])
            if len(categories) >= 3:
                escalation_bonus += 0.1
                applied_rules.append(f"Multiple attack categories ({len(categories)})")
        
        if applied_rules:
            self.logger.info(f"Escalation rules applied: {'; '.join(applied_rules)}")
            
        return base_score + escalation_bonus
    
    def _assess_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on score."""
        if risk_score >= self.risk_thresholds["CRITICAL"]:
            return RiskLevel.CRITICAL
        elif risk_score >= self.risk_thresholds["HIGH"]:
            return RiskLevel.HIGH
        elif risk_score >= self.risk_thresholds["MEDIUM"]:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
        
    def _make_decision(self, risk_score: float, filter_results: Dict[str, Any]) -> Decision:
        """Make final policy decision based on risk assessment."""
        
        # Critical threats: Always block
        if risk_score >= self.decision_thresholds["BLOCK"]:
            return Decision.BLOCK
        
        # Medium-high threats: Sanitize if possible, otherwise block
        elif risk_score >= self.decision_thresholds["SANITIZE"]:
            # Check if sanitization is viable
            if self._is_sanitizable(filter_results):
                return Decision.SANITIZE
            else:
                # If can't sanitize safely, escalate to block
                self.logger.info("Sanitization not viable, escalating to BLOCK")
                return Decision.BLOCK
        
        # Low threats: Allow with monitoring
        else:
            return Decision.ALLOW

    def _is_sanitizable(self, filter_results: Dict[str, Any]) -> bool:
        """Determine if prompt can be safely sanitized."""
        
        # Don't sanitize if ML confidence is very high (likely sophisticated attack)
        ml_result = filter_results.get("ml_classifier", {})
        if isinstance(ml_result, dict):
            ml_score = ml_result.get("risk_score", 0.0)
            ml_confidence = ml_result.get("confidence", "low")
            
            if ml_score > 0.8 and ml_confidence == "high":
                self.logger.debug("Cannot sanitize: High ML confidence threat")
                return False
        
        # Don't sanitize if multiple attack categories detected
        regex_result = filter_results.get("regex_filter", {})
        if isinstance(regex_result, dict):
            categories = regex_result.get("categories_detected", [])
            if len(categories) > 2:
                self.logger.debug(f"Cannot sanitize: Too many categories ({len(categories)})")
                return False
        
        # Don't sanitize heavy obfuscation (indicates intent to bypass)
        obf_result = filter_results.get("obfuscation_detector", {})
        if isinstance(obf_result, dict):
            obf_score = obf_result.get("obfuscation_score", 0.0)
            if obf_score > 0.7:
                self.logger.debug("Cannot sanitize: Heavy obfuscation detected")
                return False
        
        return True
    
    def _calculate_confidence(self, filter_results: Dict[str, Any], risk_score: float) -> str:
        """Calculate confidence level for the decision."""
        try:
            # Count filters with results
            active_filters = sum(1 for result in filter_results.values() 
                               if isinstance(result, dict) and result.get("risk_score", 0.0) > 0.1)
            
            # Get ML confidence if available
            ml_result = filter_results.get("ml_classifier", {})
            ml_confidence = ml_result.get("confidence", "low") if isinstance(ml_result, dict) else "low"
            
            # Determine overall confidence
            if active_filters >= 2 and ml_confidence == "high":
                return "high"
            elif active_filters >= 1 and ml_confidence in ["medium", "high"]:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            self.logger.warning(f"Error calculating confidence: {e}")
            return "low"
    
    def _generate_explanation(self, decision: Decision, filter_results: Dict[str, Any], risk_score: float) -> str:
        """Generate human-readable explanation for the decision."""
        
        explanations = []
        
        # Add filter-specific explanations
        for filter_name, result in filter_results.items():
            if not isinstance(result, dict):
                continue
                
            if filter_name == "regex_filter":
                risk = result.get("risk_score", 0.0)
                if risk > 0.1:
                    reason = result.get("reason", "Pattern matches detected")
                    explanations.append(f"Pattern matching: {reason}")
                    
            elif filter_name == "obfuscation_detector":
                obf_score = result.get("obfuscation_score", 0.0)
                if obf_score > 0.1:
                    reason = result.get("reason", "Obfuscation detected")
                    explanations.append(f"Obfuscation: {reason}")
                    
            elif filter_name == "ml_classifier":
                ml_risk = result.get("risk_score", 0.0)
                if ml_risk > 0.1:
                    reason = result.get("reason", "ML threat indicators")
                    explanations.append(f"ML analysis: {reason}")
        
        base_explanation = "; ".join(explanations) if explanations else "No significant threats detected"
        
        # Add decision reasoning
        if decision == Decision.BLOCK:
            return f"BLOCKED - {base_explanation} (Risk: {risk_score:.3f})"
        elif decision == Decision.SANITIZE:
            return f"SANITIZE REQUIRED - {base_explanation} (Risk: {risk_score:.3f})"
        else:
            return f"ALLOWED - {base_explanation} (Risk: {risk_score:.3f})"
        
    def _create_decision_report(self, prompt: str, decision: Decision, risk_score: float,
                              risk_level: RiskLevel, explanation: str, 
                              filter_results: Dict[str, Any], confidence: str) -> Dict[str, Any]:
        """Create comprehensive decision report."""
        return {
            "decision": decision.value,
            "risk_score": risk_score,
            "risk_level": risk_level.value,
            "explanation": explanation,
            "confidence": confidence,
            "threat_detected": risk_score > 0.3,
            "sanitizable": decision == Decision.SANITIZE,
            "original_prompt": prompt,
            "filter_results": filter_results,
            "decision_factors": {
                "block_threshold": self.decision_thresholds["BLOCK"],
                "sanitize_threshold": self.decision_thresholds["SANITIZE"],
                "filter_weights": self.filter_weights
            },
            "timestamp": self._get_timestamp(),
            "policy_version": "2.0.0"
        }
        
    def _create_error_decision(self, prompt: str, error: str) -> Dict[str, Any]:
        """Create fail-safe decision on error."""
        return {
            "decision": Decision.BLOCK.value,
            "risk_score": 1.0,
            "risk_level": RiskLevel.CRITICAL.value,
            "explanation": f"BLOCKED due to evaluation error: {error}",
            "confidence": "error",
            "threat_detected": True,
            "sanitizable": False,
            "original_prompt": prompt,
            "error": error,
            "filter_results": {},
            "timestamp": self._get_timestamp(),
            "policy_version": "2.0.0"
        }
        
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
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