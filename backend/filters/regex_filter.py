import re
import logging
from typing import Dict, List, Tuple, Optional
from backend.config.constants import (
    JAILBREAK_PATTERNS,
    INJECTION_PATTERNS,
    LEAKAGE_PATTERNS,
    SUSPICIOUS_KEYWORDS,
    OBFUSCATION_PATTERNS,
    )

class RegexFilter:
    """
    Fast regex-based filter for detecting obvious prompt attacks.
    First line of defense - catches blatant jailbreaks and injections.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._compile_patterns()
        
    def _compile_patterns(self):
        """Pre-compile regex patterns for performance."""
        try:
            self.jailbreak_regex = [re.compile(pattern, re.IGNORECASE) for pattern in JAILBREAK_PATTERNS]
            self.injection_regex = [re.compile(pattern, re.IGNORECASE) for pattern in INJECTION_PATTERNS]
            self.leakage_regex = [re.compile(pattern, re.IGNORECASE) for pattern in LEAKAGE_PATTERNS]
            self.obfuscation_regex = [re.compile(pattern, re.IGNORECASE) for pattern in OBFUSCATION_PATTERNS]
            
            # Compile suspicious keywords into single pattern for efficiency
            keywords_pattern = r'\b('+ '|'.join(re.escape(kw) for kw in SUSPICIOUS_KEYWORDS) + r')\b'
            self.suspicious_regex = re.compile(keywords_pattern, re.IGNORECASE)
            
            self.logger.info("Regex patterns compiled successfully")
        except Exception as e:
            self.logger.error(f"Failed to compile regex patterns: {e}")
            raise
        
    def analyze(self, prompt: str) -> Dict:
        """
        Analyze prompt for regex-based security violations.
        
        Args:
            prompt (str): User input to analyze
            
        Returns:
            Dict with risk_score, matches, and decision reason
        """
        if not prompt or not isinstance(prompt, str):
            return self._create_result(0.0, [], "Empty or invalid prompt")
        
        # Clean prompt for analysis
        cleaned_prompt = self._preprocess_prompt(prompt)
        
        # Check all pattern categories
        jailbreak_matches = self._check_patterns(cleaned_prompt, self.jailbreak_regex, "jailbreak")
        injection_matches = self._check_patterns(cleaned_prompt, self.injection_regex, "injection")
        leakage_matches = self._check_patterns(cleaned_prompt, self.leakage_regex, "leakage")
        obfuscation_matches = self._check_patterns(cleaned_prompt, self.obfuscation_regex, "obfuscation")
        suspicious_matches = self._check_suspicious_keywords(cleaned_prompt)
        
        # Combine all matches
        all_matches = jailbreak_matches + injection_matches + leakage_matches + obfuscation_matches + suspicious_matches
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(all_matches)
        
        # Generate decision reason
        reason = self._generate_reason(all_matches, risk_score)
        
        return self._create_result(risk_score, all_matches, reason)
    
    def _preprocess_prompt(self, prompt: str) ->str:
        """Clean and normalize prompt for analysis."""
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+',' ',prompt.strip())
        
        # Decode common obfuscation attempts
        cleaned = self._decode_common_obfuscation(cleaned)
        
        return cleaned
    
    def _decode_common_obfuscation(self, text: str) -> str:
        """Decode basic obfuscation techniques."""
        try:
            # Remove excessive spacing between characters
            text = re.sub(r'([a-zA-Z])\s+([a-zA-Z])',r'\1\2',text)
            
            # Remove repeated characters (keep only 2 max)
            text = re.sub(r'([a-zA-Z])\1{2,}',r'\1\1',text)
            
            return text
        except Exception as e:
            return text
        
    def _check_patterns(self, prompt:str,patterns: List[re.Pattern], category: str) -> List[Dict]:
        """Check prompt against compiled regex patterns."""
        matches = []
        
        for pattern in patterns:
            try:
                found_matches = pattern.finditer(prompt)
                for match in found_matches:
                    matches.append({
                        "category": category,
                        "pattern": pattern.pattern,
                        "match": match.group(0),
                        "position": match.span(),
                        "severity": self._get_category_severity(category)
                    })
            except Exception as e:
                self.logger.warning(f"Pattern matching failed for {pattern.pattern}: {e}")
        return matches
    
    def _check_suspicious_keywords(self, prompt: str) -> List[Dict]:
        """Check for suspicious keywords."""
        matches = []
        
        try:
            found_matches = self.suspicious_regex.finditer(prompt)
            for match in found_matches:
                matches.append({
                    "category": "suspicious_keyword",
                    "pattern": "keyword_detection",
                    "match": match.group(0),
                    "position": match.span(),
                    "severity": 0.3
                })
        except Exception as e:
            self.logger.warning(f"Suspicious keyword detection failed: {e}")
        
        return matches
    
    def _get_category_severity(self, category: str) -> float:
        """Get severity score for each attack category."""
        severity_map ={
            "jailbreak": 0.8,
            "injection": 0.7,
            "leakage": 0.6,
            "obfuscation": 0.5,
            "suspicious_keyword": 0.3
        }
        return severity_map.get(category, 0.5)
    
    def _calculate_risk_score(self, matches: List[Dict]) -> float:
        """Calculate overall risk score from matches."""
        if not matches:
            return 0.0
        
        # Base score from highest severity match
        max_severity = max(match["severity"] for match in matches)
        
        # Add bonus for multiple categories
        categories = set(match["category"] for match in matches)
        category_bonus = min(len(categories)*0.1,0.3)
        
        # Add bonus for multiple matches in same category
        match_bonus = min(len(matches)* 0.05, 0.2)
        
        # Calculate final score (capped at 1.0)
        risk_score = min(max_severity + category_bonus + match_bonus, 1.0)
        
        return round(risk_score, 3)
    
    def _generate_reason(self, matches: List[Dict], risk_score: float) -> str:
        """Generate human-readable explanation for the decision."""
        if not matches:
            return "No security violations detected"
        
        # Group matches by category
        by_category = {}
        for match in matches:
            category = match["category"]
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(match)
            
        # Build explaination
        reasons = []
        for category,category_matches in by_category.items():
            count = len(category_matches)
            category_name = category.replace('_',' ').title()
            
            if count == 1:
                reasons.append(f"Detected {category_name.lower()}")
            else:
                reasons.append(f"Detected {count} {category_name.lower()} patterns")
                
        base_reason = "; ".join(reasons)
        
        # Add risk level
        if risk_score >= 0.8:
            return f"HIGH RISK: {base_reason}"
        elif risk_score >= 0.5:
            return f"MEDIUM RISK: {base_reason}"
        else:
            return f"LOW RISK: {base_reason}"
        
    def _create_result(self, risk_score: float, matches: List[Dict], reason: str) -> Dict:
        """Create standardized result dictionary."""
        
        return {
            "filter_name": "regex_filter",
            "risk_score": risk_score,
            "matches": matches,
            "match_count":len(matches),
            "reason": reason,
            "categories_detected": list(set(m["category"] for m in matches))
        }
        
# Global instance for reuse
regex_filter = RegexFilter()

def analyze_prompt(prompt: str) -> Dict:
    """
    Convenience function for analyzing prompts.
    
    Args:
        prompt: User input to analyze
    
    Returns:
        Analysis result dictionary
    """
    return regex_filter.analyze(prompt)