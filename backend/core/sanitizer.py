import logging
import re
import string
from typing import Dict, List, Tuple, Optional, Any
from backend.config.constants import JAILBREAK_PATTERNS, INJECTION_PATTERNS

class SemanticSanitizer:
    """
    Intelligent prompt sanitizer that removes or replaces malicious content 
    while preserving the legitimate intent of user queries.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Sanitization rules and replacements
        self.sanitization_rules = {
            "instruction_override": {
                "patterns": [
                    r"ignore\s+.*?instructions",
                    r"forget\s+.*?instructions", 
                    r"disregard\s+.*?instructions",
                    r"override\s+.*?instructions"
                ],
                "replacement": "[INSTRUCTION_OVERRIDE_REMOVED]",
                "explanation": "Removed instruction override attempt"
            },
            
            "system_revelation": {
                "patterns": [
                    r"show\s+.*?system\s+prompt",
                    r"reveal\s+.*?prompt",
                    r"display\s+.*?instructions",
                    r"show\s+me\s+your\s+prompt",
                    r"show\s+.*?prompt",
                    r"what\s+.*?your.*?instructions"
                ],
                "replacement": "[SYSTEM_QUERY_REMOVED]",
                "explanation": "Removed system prompt revelation attempt"
            },
            
            "role_bypass": {
                "patterns": [
                    r"act\s+as\s+dan",
                    r"pretend\s+you\s+are\s+not\s+.*?ai",
                    r"roleplay\s+as\s+.*?human",
                    r"imagine\s+you\s+are\s+not",
                    r"simulate\s+being\s+human"
                ],
                "replacement": "[ROLE_BYPASS_REMOVED]",
                "explanation": "Removed role-playing bypass attempt"
            },
            
            "dev_mode": {
                "patterns": [
                    r"developer\s+mode",
                    r"debug\s+mode",
                    r"unrestricted\s+mode",
                    r"admin\s+mode",
                    r"god\s+mode"
                ],
                "replacement": "[DEV_MODE_REMOVED]",
                "explanation": "Removed developer mode activation attempt"
            },
            
            "harmful_requests": {
                "patterns": [
                    r"how\s+to\s+hack",
                    r"create\s+.*?virus",
                    r"illegal\s+ways",
                    r"bypass\s+security",
                    r"break\s+into"
                ],
                "replacement": "[HARMFUL_REQUEST_REMOVED]",
                "explanation": "Removed potentially harmful content request"
            },

            "jailbreak_phrases": {
                "patterns": [
                    r"jailbreak",
                    r"do\s+anything\s+now",
                    r"without\s+restrictions",
                    r"no\s+limits",
                    r"bypass\s+filters"
                ],
                "replacement": "[JAILBREAK_PHRASE_REMOVED]",
                "explanation": "Removed jailbreak phrase"
            },

            "obfuscation_cleanup": {
                "patterns": [
                    r"[a-zA-Z]\s+[a-zA-Z]\s+[a-zA-Z]",  # Excessive spacing
                    r"([a-zA-Z])\1{3,}",                 # Repeated chars
                    r"[^\w\s]{3,}"                       # Symbol clusters
                ],
                "replacement": "[OBFUSCATION_REMOVED]",
                "explanation": "Cleaned up obfuscation attempt"
            }
        }
        
        # Compile patterns for performance
        self._compile_patterns()
        
    def _compile_patterns(self):
        """Pre-compile regex patterns for sanitization."""
        self.compiled_rules = {}
        
        for rule_name, rule_data in self.sanitization_rules.items():
            try:
                compiled_patterns = []
                for pattern in rule_data["patterns"]:
                    compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
                
                self.compiled_rules[rule_name] = {
                    "patterns": compiled_patterns,
                    "replacement": rule_data["replacement"],
                    "explanation": rule_data["explanation"]
                }
            except Exception as e:
                self.logger.error(f"Failed to compile pattern for {rule_name}: {e}")
                continue
        
        self.logger.info(f"Compiled {len(self.compiled_rules)} sanitization rules")
    
    def sanitize(self, prompt: str, filter_results: Dict) -> Dict[str, Any]:
        """
        Sanitize a risky prompt by removing or replacing malicious content.
        
        Args:
            prompt: Original prompt to sanitize
            filter_results: Results from security filters to guide sanitization
            
        Returns:
            Dict with sanitized prompt and sanitization report
        """
        if not prompt or not isinstance(prompt, str):
            return self._create_result(prompt, prompt, [], "Invalid input", {})
        
        original_prompt = prompt
        sanitized_prompt = prompt
        applied_rules = []
        
        try:
            # Apply sanitization rules based on filter detections
            sanitized_prompt, applied_rules = self._apply_sanitization_rules(
                sanitized_prompt, filter_results
            )
            
            # Clean up excessive whitespace and artifacts
            sanitized_prompt = self._cleanup_sanitized_prompt(sanitized_prompt)
            
            # Verify sanitization was successful
            safety_check = self._verify_sanitization_safety(sanitized_prompt)
            
            summary = f"Applied {len(applied_rules)} sanitization rules"
            
            return self._create_result(
                original_prompt, sanitized_prompt, applied_rules, summary, safety_check
            )
            
        except Exception as e:
            self.logger.error(f"Sanitization failed: {e}")
            return self._create_result(
                original_prompt, original_prompt, [], f"Sanitization error: {e}", {}
            )
        
    def _apply_sanitization_rules(self, prompt: str, filter_results: Dict) -> Tuple[str, List]:
        """Apply appropriate sanitization rules based on filter results."""
        sanitized = prompt
        applied_rules = []
        
        # Get detected categories to focus sanitization
        regex_results = filter_results.get("regex_filter", {})
        detected_categories = regex_results.get("categories_detected", [])
        obfuscation_results = filter_results.get("obfuscation_detector", {})
        ml_results = filter_results.get("ml_classifier", {})
        
        # Log detected categories for debugging
        self.logger.debug(f"Sanitizing prompt with categories: {detected_categories}")
        
        # Apply rules based on what was detected
        for rule_name, rule_data in self.compiled_rules.items():
            if self._should_apply_rule(rule_name, detected_categories, filter_results):
                
                original_sanitized = sanitized
                for pattern in rule_data["patterns"]:
                    matches = pattern.findall(sanitized)
                    if matches:
                        sanitized = pattern.sub(rule_data["replacement"], sanitized)
                        
                if sanitized != original_sanitized:
                    applied_rules.append({
                        "rule": rule_name,
                        "explanation": rule_data["explanation"],
                        "replacement": rule_data["replacement"],
                        "matches_found": len(matches) if 'matches' in locals() else 0
                    })
                    self.logger.info(f"Applied sanitization rule: {rule_name}")
        
        # Special handling for obfuscation
        if obfuscation_results.get("is_obfuscated", False):
            sanitized, obf_rule = self._clean_obfuscation(sanitized)
            if obf_rule:
                applied_rules.append(obf_rule)
                
        return sanitized, applied_rules
    
    def _should_apply_rule(self, rule_name: str, detected_categories: List[str], 
                          filter_results: Dict) -> bool:
        """Determine if a sanitization rule should be applied."""
        
        # Rule mapping to detected categories
        rule_category_mapping = {
            "instruction_override": ["jailbreak", "injection"],
            "system_revelation": ["leakage", "jailbreak"],
            "role_bypass": ["jailbreak", "injection"],
            "dev_mode": ["jailbreak", "injection"],
            "harmful_requests": ["injection", "suspicious_keyword"],
            "jailbreak_phrases": ["jailbreak", "injection"],
            "obfuscation_cleanup": []  # Always consider for obfuscation
        }
        
        # Check if rule applies to detected categories
        relevant_categories = rule_category_mapping.get(rule_name, [])
        if relevant_categories:
            category_match = any(cat in detected_categories for cat in relevant_categories)
            if category_match:
                return True
        
        # Special cases based on filter results
        obf_results = filter_results.get("obfuscation_detector", {})
        ml_results = filter_results.get("ml_classifier", {})
        
        # Apply obfuscation cleanup if obfuscation detected
        if rule_name == "obfuscation_cleanup" and obf_results.get("is_obfuscated", False):
            return True
            
        # Apply more aggressive rules if ML confidence is high
        if ml_results.get("risk_score", 0.0) > 0.7:
            return rule_name in ["instruction_override", "system_revelation", "jailbreak_phrases"]
        
        return False
    
    def _clean_obfuscation(self, prompt: str) -> Tuple[str, Optional[Dict]]:
        """Clean obfuscation-specific patterns."""
        try:
            original = prompt
            cleaned = prompt
            
            # Remove excessive spacing
            cleaned = re.sub(r'\s+', ' ', cleaned)
            
            # Fix character spacing (a b c -> abc)
            cleaned = re.sub(r'([a-zA-Z])\s+([a-zA-Z])', r'\1\2', cleaned)
            
            # Remove repeated characters (aaaaa -> aa)
            cleaned = re.sub(r'([a-zA-Z])\1{2,}', r'\1\1', cleaned)
            
            # Remove excessive punctuation
            cleaned = re.sub(r'[^\w\s]{3,}', ' ', cleaned)
            
            # Clean up multiple spaces
            cleaned = re.sub(r'\s+', ' ', cleaned.strip())
            
            if cleaned != original:
                return cleaned, {
                    "rule": "obfuscation_cleanup",
                    "explanation": "Cleaned up obfuscated text formatting",
                    "replacement": "[CLEANED]"
                }
            else:
                return cleaned, None
                
        except Exception as e:
            self.logger.error(f"Obfuscation cleaning failed: {e}")
            return prompt, None
    
    def _cleanup_sanitized_prompt(self, prompt: str) -> str:
        """Clean up the sanitized prompt to remove artifacts."""
        try:
            cleaned = prompt
            
            # Remove multiple consecutive removal markers
            cleaned = re.sub(r'(\[[\w_]+_REMOVED\])\s*\1+', r'\1', cleaned)
            
            # Clean up excessive whitespace
            cleaned = re.sub(r'\s+', ' ', cleaned)
            
            # Remove leading/trailing whitespace
            cleaned = cleaned.strip()
            
            # If prompt becomes too short or only removal markers, provide fallback
            content_without_markers = re.sub(r'\[[\w_]+_REMOVED\]', '', cleaned).strip()
            if len(content_without_markers) < 3:
                cleaned = "[SANITIZED_QUERY]"
                
            return cleaned
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return prompt
    
    def _verify_sanitization_safety(self, sanitized_prompt: str) -> Dict[str, Any]:
        """Verify that sanitization was successful by re-checking for threats."""
        try:
            # Quick pattern check on sanitized content
            threat_indicators = 0
            
            # Check for remaining jailbreak indicators
            jailbreak_patterns = [
                r"ignore.*instructions", r"bypass.*security", r"developer.*mode"
            ]
            
            for pattern in jailbreak_patterns:
                if re.search(pattern, sanitized_prompt, re.IGNORECASE):
                    threat_indicators += 1
            
            # Check for suspicious keywords
            suspicious_words = ["jailbreak", "hack", "bypass", "override"]
            for word in suspicious_words:
                if word.lower() in sanitized_prompt.lower():
                    threat_indicators += 1
            
            is_safe = threat_indicators == 0
            risk_score = min(threat_indicators * 0.2, 1.0)
            
            return {
                "is_safe": is_safe,
                "remaining_threats": threat_indicators,
                "risk_score": risk_score,
                "verification_method": "pattern_check"
            }
            
        except Exception as e:
            self.logger.error(f"Safety verification failed: {e}")
            return {
                "is_safe": False,
                "remaining_threats": 1,
                "risk_score": 0.5,
                "error": str(e)
            }
    
    def _create_result(self, original: str, sanitized: str, applied_rules: List,
                      summary: str, safety_check: Dict) -> Dict[str, Any]:
        """Create comprehensive sanitization result."""
        
        try:
            return {
                "filter_name": "semantic_sanitizer",
                "original_prompt": original,
                "sanitized_prompt": sanitized,
                "prompt_modified": original != sanitized,
                "applied_rules": applied_rules,
                "rules_applied_count": len(applied_rules),
                "summary": summary,
                "safety_verification": safety_check,
                "is_safe_after_sanitization": safety_check.get("is_safe", False),
                "sanitization_successful": len(applied_rules) > 0,
                "character_reduction": len(original) - len(sanitized),
                "sanitization_method": "rule_based_semantic"
            }
            
        except Exception as e:
            self.logger.error(f"Error creating sanitization result: {e}")
            return {
                "filter_name": "semantic_sanitizer",
                "original_prompt": original,
                "sanitized_prompt": sanitized,
                "error": str(e),
                "prompt_modified": False,
                "applied_rules": [],
                "summary": "Sanitization failed"
            }

# Global sanitizer instance
semantic_sanitizer = SemanticSanitizer()

def sanitize_prompt(prompt: str, filter_results: Dict) -> Dict[str, Any]:
    """
    Convenience function for prompt sanitization.
    
    Args:
        prompt: Original prompt to sanitize
        filter_results: Security filter results
        
    Returns:
        Sanitization result dictionary
    """
    return semantic_sanitizer.sanitize(prompt, filter_results)