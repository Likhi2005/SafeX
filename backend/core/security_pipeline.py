import logging
from typing import Dict, Any, Optional
from datetime import datetime

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
        self.pipeline_version = "1.0.0"
    
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
                return self._create_error_result("Invalid input", prompt)
            
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
            
            # Stage 5: Combine all filter results
            filter_results = {
                "obfuscation_detector": obfuscation_result,
                "regex_filter": regex_result,
                "ml_classifier": ml_result
            }
            
            # Stage 6: Policy evaluation and decision
            policy_decision = evaluate_prompt_security(decoded_prompt, filter_results)
            
            self.logger.info(f"Policy decision: {policy_decision.get('decision')} (risk: {policy_decision.get('risk_score')})")
            
            # Stage 7: Apply sanitization if needed
            final_prompt = decoded_prompt
            sanitization_result = None
            
            if policy_decision.get('decision') == Decision.SANITIZE.value:
                sanitization_result = sanitize_prompt(decoded_prompt, filter_results)
                final_prompt = sanitization_result.get('sanitized_prompt', decoded_prompt)
                
                self.logger.info(f"Sanitization applied: {len(sanitization_result.get('applied_rules', []))} rules")
            
            # Create comprehensive result
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
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
            return self._create_error_result(f"Pipeline error: {str(e)}", prompt)
    
    def _validate_input(self, prompt: str) -> bool:
        """Validate input prompt."""
        if not prompt or not isinstance(prompt, str):
            return False
        
        if len(prompt) > 10000:  # Max prompt length
            self.logger.warning("Prompt exceeds maximum length")
            return False
        
        return True
    
    def _create_success_result(self, original_prompt: str, processed_prompt: str,
                             policy_decision: Dict, filter_results: Dict,
                             sanitization_result: Optional[Dict], processing_time: float,
                             user_id: str = None) -> Dict[str, Any]:
        """Create successful analysis result."""
        
        return {
            "status": "success",
            "decision": policy_decision.get('decision'),
            "risk_score": policy_decision.get('risk_score'),
            "risk_level": policy_decision.get('risk_level'),
            "explanation": policy_decision.get('explanation'),
            
            # Prompt data
            "original_prompt": original_prompt,
            "processed_prompt": processed_prompt,
            "prompt_modified": original_prompt != processed_prompt,
            
            # Analysis details
            "filter_results": filter_results,
            "policy_decision": policy_decision,
            "sanitization_result": sanitization_result,
            
            # Metadata
            "processing_time_seconds": processing_time,
            "pipeline_version": self.pipeline_version,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_id": user_id
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
            "original_prompt": prompt,
            "processed_prompt": None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "pipeline_version": self.pipeline_version
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