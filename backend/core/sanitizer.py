import re
import logging
from typing import Dict, List, Tuple, Optional
from backend.config.constants import JAILBREAK_PATTERNS, INJECTION_PATTERNS


class SemanticSanitizer:
    """
    Intelligent prompt sanitizer that removes or replaces malicious content while preserving the legitimate intent of user queries.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Sanitization rules and replacements
        self.sanitization_rules = {
            # Direct instruction overrides
            "ignore_instructions": {
                "patterns": [
                    r"ignore\s+.*?instructions",
                    r"forget\s+.*?instructions", 
                    r"disregard\s+.*?instructions"
                ],
                "replacement": "[INSTRUCTION_OVERRIDE_REMOVED]",
                "explanation": "Removed instruction override attempt"
            },
            
            # System prompt revelation
            "system_revelation": {
                "patterns": [
                    r"show\s+.*?system\s+prompt",
                    r"reveal\s+.*?prompt",
                    r"display\s+.*?instructions",
                    r"show\s+me\s+your\s+prompt",
                    r"show\s+.*?prompt"
                ],
                "replacement": "[SYSTEM_QUERY_REMOVED]",
                "explanation": "Removed system prompt revelation attempt"
            },
            
            # Role-playing bypasses
            "role_bypass": {
                "patterns": [
                    r"act\s+as\s+dan",
                    r"pretend\s+you\s+are\s+not\s+.*?ai",
                    r"roleplay\s+as\s+.*?human"
                ],
                "replacement": "[ROLE_BYPASS_REMOVED]",
                "explanation": "Removed role-playing bypass attempt"
            },
            
            # Developer mode attempts
            "dev_mode": {
                "patterns": [
                    r"developer\s+mode",
                    r"debug\s+mode",
                    r"unrestricted\s+mode"
                ],
                "replacement": "[DEV_MODE_REMOVED]",
                "explanation": "Removed developer mode activation attempt"
            },
            
            # Harmful content requests
            "harmful_requests": {
                "patterns": [
                    r"how\s+to\s+hack",
                    r"create\s+.*?virus",
                    r"illegal\s+ways"
                ],
                "replacement": "[HARMFUL_REQUEST_REMOVED]",
                "explanation": "Removed potentially harmful content request"
            }
        }
        
        # Compile patterns for performance
        self._compile_patterns()
        
    def _compile_patterns(self):
        """Pre-compile regex patterns for sanitization."""
        self.compiled_rules = {}
        
        for rule_name, rule_data in self.sanitization_rules.items():
            compiled_patterns = []
            for pattern in rule_data["patterns"]:
                try:
                    compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
                except re.error as e:
                    self.logger.warning(f"Failed to compile pattern {pattern}: {e}")
                    
            self.compiled_rules[rule_name] = {
                "patterns": compiled_patterns,
                "replacement": rule_data["replacement"],
                "explanation": rule_data["explanation"]
            }
        
        self.logger.info(f"Compiled {len(self.compiled_rules)} sanitization rules")
        
    
    def sanitize(self, prompt: str, filter_results: Dict) -> Dict[str, any]:
        """
        Sanitize a risky prompt by removing or replacing malicious content.
        
        Args:
            prompt: Original prompt to sanitize
            filter_results: Results from security filters to guide sanitization
            
        Returns:
            Dict with sanitized prompt and sanitization report
        """
        if not prompt or not isinstance(prompt, str):
            return self._create_result(prompt, prompt, [], "Empty or invalid prompt")
        
        original_prompt = prompt
        sanitized_prompt = prompt
        applied_rules = []
        
        # Apply sanitization rules based on filter detections
        sanitized_prompt, applied_rules = self._apply_sanitization_rules(
            sanitized_prompt, filter_results
        )
        
        # Clean up excessive whitespace and artifacts
        sanitized_prompt = self._cleanup_sanitized_prompt(sanitized_prompt)
        
        # Verify sanitization was successful
        safety_check = self._verify_sanitization_safety(sanitized_prompt)
        
        return self._create_result(
            original_prompt, sanitized_prompt, applied_rules, 
            f"Applied {len(applied_rules)} sanitization rules", safety_check
        )
        
    def _apply_sanitization_rules(self, prompt: str, filter_results: Dict) -> Tuple[str, List]:
        """Apply appropriate sanitization rules based on filter results."""
        sanitized = prompt
        applied_rules = []
        
        # Get detected categories to focus sanitization
        regex_results = filter_results.get("regex_filter", {})
        detected_categories = regex_results.get("categories_detected", [])
        
        
        # Log detected categories for debugging
        self.logger.info(f"DEBUG: Original prompt: '{prompt}'")
        self.logger.info(f"DEBUG: Detected categories: {detected_categories}")
        
        
        # Apply rules based on detected threats
        for rule_name, rule_data in self.compiled_rules.items():
            should_apply = self._should_apply_rule(rule_name, detected_categories, filter_results)
            
            if should_apply:
                original_length = len(sanitized)
                
                # Apply all patterns in this rule
                for pattern in rule_data["patterns"]:
                    matches = list(pattern.finditer(sanitized))
                    
                    if matches:
                        # Replace matches with sanitization marker
                        for match in reversed(matches):  # Reverse to maintain positions
                            sanitized = (
                                sanitized[:match.start()] + 
                                rule_data["replacement"] + 
                                sanitized[match.end():]
                            )
                
                # Record if rule made changes
                if len(sanitized) != original_length:
                    applied_rules.append({
                        "rule": rule_name,
                        "explanation": rule_data["explanation"],
                        "replacement": rule_data["replacement"]
                    })
                    
                    self.logger.info(f"Applied sanitization rule: {rule_name}")
        
        self.logger.info(f"DEBUG: Final sanitized: '{sanitized}'")
        
        return sanitized, applied_rules
    
    def _should_apply_rule(self, rule_name: str, detected_categories: List[str], 
                          filter_results: Dict) -> bool:
        """Determine if a sanitization rule should be applied."""
        
        # Rule mapping to detected categories
        rule_category_map = {
            "ignore_instructions": ["jailbreak"],
            "system_revelation": ["jailbreak", "leakage"],
            "role_bypass": ["jailbreak"],
            "dev_mode": ["jailbreak"],
            "harmful_requests": ["suspicious_keyword"]
        }
        
        # Check if rule applies to detected categories
        applicable_categories = rule_category_map.get(rule_name, [])
        if any(cat in detected_categories for cat in applicable_categories):
            return True
        
        # Apply based on ML confidence for sophisticated attacks
        ml_results = filter_results.get("ml_classifier", {})
        if ml_results.get("risk_score", 0.0) > 0.6:
            # Apply more aggressive sanitization for high ML scores
            return True
        
        # Apply based on obfuscation detection
        obf_results = filter_results.get("obfuscation_detector", {})
        if obf_results.get("obfuscation_score", 0.0) > 0.4:
            # Apply sanitization if obfuscation detected
            return True
        
        return False
    
    
    def _cleanup_sanitized_prompt(self, prompt: str) -> str:
        """Clean up artifacts from sanitization process."""
        # Remove multiple consecutive sanitization markers
        prompt = re.sub(r'(\[[\w_]+_REMOVED\]\s*){2,}', r'\1', prompt)
        
        # Clean up excessive whitespace
        prompt = re.sub(r'\s+', ' ', prompt)
        
        # Remove leading/trailing whitespace
        prompt = prompt.strip()
        
        # If prompt becomes too short or only markers, provide fallback
        content_length = len(re.sub(r'\[[\w_]+_REMOVED\]', '', prompt).strip())
        if content_length < 5:
            prompt = "Please rephrase your request in a clear and appropriate manner."
        
        return prompt
    
    
    def _verify_sanitization_safety(self, sanitized_prompt: str) -> Dict[str, any]:
        """Verify that sanitization was effective."""
        # Quick safety check using basic patterns
        safety_issues = []
        
        # Check for remaining instruction overrides
        if re.search(r'ignore\s+.*instructions', sanitized_prompt, re.IGNORECASE):
            safety_issues.append("Instruction override still present")
        
        # Check for system prompt requests
        if re.search(r'show.*prompt', sanitized_prompt, re.IGNORECASE):
            safety_issues.append("System prompt request still present")
        
        # Check for role bypass attempts
        if re.search(r'act\s+as\s+dan', sanitized_prompt, re.IGNORECASE):
            safety_issues.append("Role bypass still present")
        
        is_safe = len(safety_issues) == 0
        
        return {
            "is_safe": is_safe,
            "safety_issues": safety_issues,
            "confidence": 0.9 if is_safe else 0.3
        }
        
    
    def _create_result(self, original: str, sanitized: str, applied_rules: List,
                      summary: str, safety_check: Dict = None) -> Dict[str, any]:
        """Create standardized sanitization result."""
        return {
            "filter_name": "semantic_sanitizer",
            "original_prompt": original,
            "sanitized_prompt": sanitized,
            "applied_rules": applied_rules,
            "rules_count": len(applied_rules),
            "summary": summary,
            "safety_check": safety_check or {"is_safe": True, "confidence": 0.9},
            "sanitization_effective": len(applied_rules) > 0,
            "length_reduction": len(original) - len(sanitized)
        }
        
    
# Global sanitizer instance
semantic_sanitizer = SemanticSanitizer()

def sanitize_prompt(prompt: str, filter_results: Dict) -> Dict[str, any]:
    """
    Convenience function for prompt sanitization.
    
    Args:
        prompt: Original prompt to sanitize
        filter_results: Security filter results
        
    Returns:
        Sanitization result dictionary
    """
    return semantic_sanitizer.sanitize(prompt, filter_results)