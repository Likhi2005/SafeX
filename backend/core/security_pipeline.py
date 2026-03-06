import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

# Import all security components
from backend.filters.regex_filter import analyze_prompt as regex_analyze
from backend.filters.obfuscation_detector import analyze_obfuscation
from backend.ml.ml_classifier import analyze_with_ml
from backend.core.policy_engine import evaluate_prompt_security, Decision
from backend.core.sanitizer import sanitize_prompt

class SecurityPipeline:
    """
    Unified security pipeline that orchestrates all security filters
    and provides a single interface for prompt analysis.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pipeline_version = "2.0.0-onnx"
        self._performance_stats = {
            "total_requests": 0,
            "avg_processing_time": 0.0,
            "blocked_requests": 0,
            "sanitized_requests": 0,
            "allowed_requests": 0,
            "error_requests": 0
        }
    
    def analyze(self, prompt: str, user_id: str = None) -> Dict[str, Any]:
        """
        Complete security analysis of a user prompt.
        
        Args:
            prompt: User input to analyze
            user_id: Optional user identifier for logging
            
        Returns:
            Complete security analysis and decision
        """
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Starting security analysis for user: {user_id}")
            self.logger.debug(f"Prompt preview: {prompt[:100]}...")
            
            # Stage 1: Input validation
            if not self._validate_input(prompt):
                return self._create_error_result("Invalid input prompt", prompt)
            
            # Stage 2: Obfuscation detection and decoding
            obfuscation_result = analyze_obfuscation(prompt)
            decoded_prompt = obfuscation_result.get("decoded_prompt", prompt)
            
            self.logger.debug(f"Obfuscation check complete: score={obfuscation_result.get('obfuscation_score', 0)}")
            
            # Stage 3: Regex-based pattern matching (fast)
            regex_result = regex_analyze(decoded_prompt)
            
            self.logger.debug(f"Regex check complete: score={regex_result.get('risk_score', 0)}")
            
            # Stage 4: ML-based analysis (slower but more accurate)
            ml_result = analyze_with_ml(decoded_prompt)
            
            self.logger.debug(f"ML check complete: score={ml_result.get('risk_score', 0)}")
            
            # Stage 5: Combine all filter results with validation
            filter_results = self._validate_filter_results({
                "obfuscation_detector": obfuscation_result,
                "regex_filter": regex_result,
                "ml_classifier": ml_result
            })
            
            # Stage 6: Policy evaluation and decision
            policy_decision = evaluate_prompt_security(decoded_prompt, filter_results)
            
            self.logger.info(f"Policy decision: {policy_decision.get('decision')} (risk: {policy_decision.get('risk_score')})")
            
            # Stage 7: Apply sanitization if needed
            final_prompt = decoded_prompt
            sanitization_result = None
            
            if policy_decision.get('decision') == Decision.SANITIZE.value:
                try:
                    sanitization_result = sanitize_prompt(decoded_prompt, filter_results)
                    final_prompt = sanitization_result.get('sanitized_prompt', decoded_prompt)
                    self.logger.info(f"Sanitization applied: {len(sanitization_result.get('applied_rules', []))} rules")
                except Exception as e:
                    self.logger.error(f"Sanitization failed: {e}")
                    # Fall back to blocking if sanitization fails
                    policy_decision['decision'] = Decision.BLOCK.value
                    policy_decision['risk_score'] = 1.0
            
            # Create comprehensive result
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            # Update stats
            self._update_performance_stats(processing_time, policy_decision.get('decision'))
            
            # Log performance
            self.logger.info(f"Analysis complete: {policy_decision.get('decision')} "
                           f"(risk: {policy_decision.get('risk_score'):.3f}) "
                           f"in {processing_time:.3f}s - user: {user_id}")
            
            return self._create_success_result(
                original_prompt=prompt,
                processed_prompt=final_prompt,
                policy_decision=policy_decision,
                filter_results=filter_results,
                sanitization_result=sanitization_result,
                processing_time=processing_time,
                user_id=user_id
            )
            
        except Exception as e:
            self.logger.error(f"Security pipeline failed: {e}")
            self._performance_stats["error_requests"] += 1
            return self._create_error_result(f"Pipeline error: {str(e)}", prompt)
    
    def _validate_input(self, prompt: str) -> bool:
        """Validate input prompt."""
        if not prompt or not isinstance(prompt, str):
            self.logger.warning("Invalid prompt: empty or not string")
            return False
        
        if len(prompt.strip()) == 0:
            self.logger.warning("Invalid prompt: empty after stripping")
            return False
        
        if len(prompt) > 10000:  # Max prompt length
            self.logger.warning("Prompt exceeds maximum length")
            return False
        
        return True
    
    def _validate_filter_results(self, filter_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize filter results."""
        validated_results = {}
        
        for filter_name, result in filter_results.items():
            if not isinstance(result, dict):
                self.logger.error(f"Invalid result from {filter_name}: not a dictionary")
                # Create fallback result
                validated_results[filter_name] = {
                    "filter_name": filter_name,
                    "risk_score": 0.0,
                    "reason": "Filter error - invalid result format",
                    "error": True
                }
                continue
            
            # Validate risk score
            risk_score = result.get("risk_score", 0.0)
            if not isinstance(risk_score, (int, float)) or risk_score < 0:
                risk_score = 0.0
            elif risk_score > 1.0:
                risk_score = 1.0
            
            # Ensure required fields exist
            validated_result = {
                "filter_name": filter_name,
                "risk_score": round(risk_score, 3),
                "reason": result.get("reason", "No reason provided"),
                **result  # Keep all other original fields
            }
            
            # Add specific validation for each filter type
            if filter_name == "obfuscation_detector":
                validated_result["obfuscation_score"] = validated_result.get("obfuscation_score", risk_score)
                validated_result["is_obfuscated"] = validated_result.get("is_obfuscated", risk_score > 0.2)
                
            elif filter_name == "regex_filter":
                validated_result["matches"] = validated_result.get("matches", [])
                validated_result["categories_detected"] = validated_result.get("categories_detected", [])
                validated_result["is_threat"] = validated_result.get("is_threat", risk_score > 0.3)
                
            elif filter_name == "ml_classifier":
                validated_result["ml_results"] = validated_result.get("ml_results", [])
                validated_result["is_threat"] = validated_result.get("is_threat", risk_score > 0.3)
                validated_result["confidence"] = validated_result.get("confidence", "low")
            
            validated_results[filter_name] = validated_result
        
        return validated_results
    
    def _update_performance_stats(self, processing_time: float, decision: str):
        """Update performance statistics."""
        self._performance_stats["total_requests"] += 1
        
        # Update average processing time using exponential moving average
        alpha = 0.1
        self._performance_stats["avg_processing_time"] = (
            alpha * processing_time + 
            (1 - alpha) * self._performance_stats["avg_processing_time"]
        )
        
        if decision == "BLOCK":
            self._performance_stats["blocked_requests"] += 1
        elif decision == "SANITIZE":
            self._performance_stats["sanitized_requests"] += 1
        elif decision == "ALLOW":
            self._performance_stats["allowed_requests"] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        total = self._performance_stats["total_requests"]
        stats = self._performance_stats.copy()
        
        if total > 0:
            stats["block_rate"] = round(stats["blocked_requests"] / total * 100, 2)
            stats["sanitize_rate"] = round(stats["sanitized_requests"] / total * 100, 2)
            stats["allow_rate"] = round(stats["allowed_requests"] / total * 100, 2)
            stats["error_rate"] = round(stats["error_requests"] / total * 100, 2)
        else:
            stats["block_rate"] = 0.0
            stats["sanitize_rate"] = 0.0  
            stats["allow_rate"] = 0.0
            stats["error_rate"] = 0.0
        
        return stats
    
    def _create_success_result(self, 
        original_prompt: str,
        processed_prompt: str,
        policy_decision: Dict,
        filter_results: Dict,
        sanitization_result: Optional[Dict],
        processing_time: float,
        user_id: str = None) -> Dict[str, Any]:
        """Create successful analysis result."""
        
        return {
            "status": "success",
            "decision": policy_decision.get('decision'),
            "risk_score": policy_decision.get('risk_score'),
            "risk_level": policy_decision.get('risk_level'),
            "explanation": policy_decision.get('explanation'),
            "confidence": policy_decision.get('confidence', 'medium'),
            "threat_detected": policy_decision.get('risk_score', 0.0) > 0.3,
            "original_prompt": original_prompt,
            "processed_prompt": processed_prompt,
            "prompt_modified": original_prompt != processed_prompt,
            "filter_results": filter_results,
            "policy_decision": policy_decision,
            "sanitization_result": sanitization_result,
            "processing_time_seconds": round(processing_time, 4),
            "pipeline_version": self.pipeline_version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "optimization": "onnx-enabled"
        }
    
    def _create_error_result(self, error: str, prompt: str = None) -> Dict[str, Any]:
        """Create error result (fail-safe to block)."""
        return {
            "status": "error",
            "decision": Decision.BLOCK.value,
            "risk_score": 1.0,
            "risk_level": "CRITICAL",
            "explanation": f"Security analysis failed: {error}",
            "error": error,
            "threat_detected": True,
            "original_prompt": prompt,
            "processed_prompt": None,
            "filter_results": {},
            "policy_decision": {
                "decision": Decision.BLOCK.value,
                "risk_score": 1.0,
                "explanation": "Error in security analysis - blocked as precaution"
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pipeline_version": self.pipeline_version,
            "processing_time_seconds": 0.0
        }

# Global pipeline instance
security_pipeline = SecurityPipeline()

def analyze_prompt_security(prompt: str, user_id: str = None) -> Dict[str, Any]:
    """
    Main entry point for prompt security analysis.
    
    Args:
        prompt: User prompt to analyze
        user_id: Optional user identifier
        
    Returns:
        Complete security analysis result
    """
    return security_pipeline.analyze(prompt, user_id)

def get_pipeline_stats() -> Dict[str, Any]:
    """Get pipeline performance statistics."""
    return security_pipeline.get_pipeline_stats()