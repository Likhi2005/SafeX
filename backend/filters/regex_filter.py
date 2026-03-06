import logging
import re
import string
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
            
            self.logger.info(f"Compiled {len(self.jailbreak_regex)} jailbreak patterns")
            self.logger.info(f"Compiled {len(self.injection_regex)} injection patterns")
            self.logger.info(f"Compiled {len(self.leakage_regex)} leakage patterns")
            self.logger.info(f"Compiled {len(self.obfuscation_regex)} obfuscation patterns")
        except Exception as e:
            self.logger.error(f"Failed to compile regex patterns: {e}")
            # Fallback to empty lists
            self.jailbreak_regex = []
            self.injection_regex = []
            self.leakage_regex = []
            self.obfuscation_regex = []
        
    def analyze(self, prompt: str) -> Dict:
        """
        Analyze prompt for regex-based security violations.
        
        Args:
            prompt (str): User input to analyze
            
        Returns:
            Dict with risk_score, matches, and decision reason
        """
        if not prompt or not isinstance(prompt, str):
            return self._create_result(0.0, [], "Invalid or empty prompt")
        
        # Clean prompt for analysis
        cleaned_prompt = self._preprocess_prompt(prompt)
        
        # Check all pattern categories - unify jailbreak and injection as prompt_injection
        jailbreak_matches = self._check_patterns(cleaned_prompt, self.jailbreak_regex, "prompt_injection")
        injection_matches = self._check_patterns(cleaned_prompt, self.injection_regex, "prompt_injection")
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
    
    def _preprocess_prompt(self, prompt: str) -> str:
        """Clean and normalize prompt for analysis."""
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', prompt.strip())
        
        # Decode common obfuscation attempts
        cleaned = self._decode_common_obfuscation(cleaned)
        
        return cleaned
    
    def _decode_common_obfuscation(self, text: str) -> str:
        """Decode basic obfuscation techniques."""
        try:
            # Remove unnecessary punctuation that might obfuscate
            cleaned = re.sub(r'[^\w\s]', ' ', text)
            # Remove leetspeak common substitutions
            leetspeak_map = {'4': 'a', '3': 'e', '1': 'i', '0': 'o', '5': 's', '7': 't', '@': 'a'}
            for leet, normal in leetspeak_map.items():
                cleaned = cleaned.replace(leet, normal)
            return cleaned
        except Exception as e:
            self.logger.error(f"Error in obfuscation decoding: {e}")
            return text
        
    def _check_patterns(self, prompt: str, patterns: List[re.Pattern], category: str) -> List[Dict]:
        """Check prompt against compiled regex patterns."""
        matches = []
        
        for pattern in patterns:
            try:
                match = pattern.search(prompt)
                if match:
                    matches.append({
                        "category": category,
                        "pattern": pattern.pattern,
                        "match": match.group(),
                        "severity": self._get_category_severity(category),
                        "start_pos": match.start(),
                        "end_pos": match.end()
                    })
            except Exception as e:
                self.logger.error(f"Error checking pattern {pattern.pattern}: {e}")
                continue
        
        return matches
    
    def _check_suspicious_keywords(self, prompt: str) -> List[Dict]:
        """Check for suspicious keywords."""
        matches = []
        
        try:
            prompt_lower = prompt.lower()
            for keyword in SUSPICIOUS_KEYWORDS:
                if keyword.lower() in prompt_lower:
                    matches.append({
                        "category": "suspicious_keyword",
                        "pattern": keyword,
                        "match": keyword,
                        "severity": self._get_category_severity("suspicious_keyword")
                    })
        except Exception as e:
            self.logger.error(f"Error checking suspicious keywords: {e}")
        
        return matches
    
    def _get_category_severity(self, category: str) -> float:
        """Get severity score for each attack category."""
        severity_map = {
            "prompt_injection": 0.8,
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
        
        # Special handling for prompt injection - higher risk
        prompt_injection_bonus = 0.1 if any(m["category"] == "prompt_injection" for m in matches) else 0.0
        
        # Add bonus for multiple categories
        categories = set(match["category"] for match in matches)
        category_bonus = min(len(categories) * 0.1, 0.3)
        
        # Add bonus for multiple matches in same category
        match_bonus = min(len(matches) * 0.05, 0.2)
        
        # Calculate final score (capped at 1.0)
        risk_score = min(max_severity + category_bonus + match_bonus + prompt_injection_bonus, 1.0)
        
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
            
        # Build explanation
        reasons = []
        for category, category_matches in by_category.items():
            count = len(category_matches)
            category_name = category.replace("_", " ").title()
            if count == 1:
                reasons.append(f"{category_name} detected")
            else:
                reasons.append(f"Multiple {category_name} patterns detected ({count})")
                
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
        categories_detected = list(set(match["category"] for match in matches)) if matches else []
        
        # Extract simple match strings for the matches array
        simple_matches = [match["match"] for match in matches] if matches else []
        
        return {
            "filter_name": "regex_filter",
            "risk_score": risk_score,
            "matches": simple_matches,
            "detailed_matches": matches,
            "categories_detected": categories_detected,
            "match_count": len(matches),
            "reason": reason,
            "is_threat": risk_score > 0.3,
            "severity_level": "HIGH" if risk_score >= 0.7 else "MEDIUM" if risk_score >= 0.4 else "LOW"
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