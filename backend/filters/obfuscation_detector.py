import logging
import re
import base64
import urllib.parse
import html
from typing import Dict, List, Tuple, Optional

class ObfuscationDetector:
    """
    Detects and decodes obfuscated prompts that try to bypass security filters.
    Handles Base64, URL encoding, Unicode tricks, excessive spacing, etc.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze(self, prompt: str) -> Dict:
        """
        Analyze prompt for obfuscation attempts and decode them.
        
        Args:
            prompt: Raw user input
            
        Returns:
            Dict with decoded_prompt, obfuscation_score, and techniques found
        """
        if not prompt or not isinstance(prompt, str):
            return self._create_result(prompt, 0.0, [], prompt)
            
        original_prompt = prompt
        decoded_prompt = prompt
        techniques_found = []
        obfuscation_score = 0.0
        
        # Detect and decode various obfuscation techniques
        decoded_prompt, base64_score = self._decode_base64(decoded_prompt)
        if base64_score > 0:
            techniques_found.append({"type": "base64_encoding", "score": base64_score})
            obfuscation_score += base64_score
        
        decoded_prompt, url_score = self._decode_url_encoding(decoded_prompt)
        if url_score > 0:
            techniques_found.append({"type": "url_encoding", "score": url_score})
            obfuscation_score += url_score
            
        decoded_prompt, html_score = self._decode_html_entities(decoded_prompt)
        if html_score > 0:
            techniques_found.append({"type": "html_entities", "score": html_score})
            obfuscation_score += html_score
        
        decoded_prompt, unicode_score = self._decode_unicode_tricks(decoded_prompt)
        if unicode_score > 0:
            techniques_found.append({"type": "unicode_tricks", "score": unicode_score})
            obfuscation_score += unicode_score
        
        decoded_prompt, spacing_score = self._normalize_spacing(decoded_prompt)
        if spacing_score > 0:
            techniques_found.append({"type": "spacing_manipulation", "score": spacing_score})
            obfuscation_score += spacing_score
            
        # Normalize final score to prevent values > 1.0
        if techniques_found:
            obfuscation_score = min(obfuscation_score / len(techniques_found), 1.0)
            
        return self._create_result(decoded_prompt, obfuscation_score, techniques_found, original_prompt)
    
    
    def _decode_base64(self, text: str) -> Tuple[str, float]:
        """Detect and decode Base64 encoded content."""
        if not text or len(text) < 4:
            return text, 0.0
        
        # Look for Base64-like patterns
        base64_pattern = re.compile(r'[A-Za-z0-9+/]{20,}={0,2}')
        matches = base64_pattern.findall(text)
        
        if not matches:
            return text, 0.0
        
        decoded_text = text
        successful_decodes = 0
        
        for match in matches:
            try:
                # Attempt to decode
                decoded_bytes = base64.b64decode(match)
                decoded_content = decoded_bytes.decode('utf-8', errors='ignore')
                
                # Only replace if decoded content is readable and different
                if len(decoded_content) > 5 and decoded_content != match:
                    decoded_text = decoded_text.replace(match, decoded_content)
                    successful_decodes += 1
            except Exception:
                continue
        
        # Score based on number of successful decodes
        score = min(successful_decodes * 0.3, 0.8) if successful_decodes > 0 else 0.0
        return decoded_text, score
    
    def _decode_url_encoding(self, text: str) -> Tuple[str, float]:
        """Detect and decode URL encoded content."""
        if not text:
            return text, 0.0
            
        # Count URL encoded characters
        url_encoded_count = len(re.findall(r'%[0-9a-fA-F]{2}', text))
        
        if url_encoded_count == 0:
            return text, 0.0
        
        try:
            decoded_text = urllib.parse.unquote(text)
            if decoded_text != text:
                score = min(url_encoded_count / len(text) * 2, 0.6)
                return decoded_text, score
        except Exception:
            pass
        
        return text, 0.0
        
    def _decode_html_entities(self, text: str) -> Tuple[str, float]:
        """Detect and decode HTML entities."""
        if not text:
            return text, 0.0
        
        # Count HTML entities
        entity_count = len(re.findall(r'&#?[a-zA-Z0-9]+;', text))
        
        if entity_count == 0:
            return text, 0.0
        
        try:
            decoded_text = html.unescape(text)
            if decoded_text != text:
                score = min(entity_count / len(text) * 3, 0.5)
                return decoded_text, score
        except Exception:
            pass
        
        return text, 0.0
        
    def _decode_unicode_tricks(self, text: str) -> Tuple[str, float]:
        """Detect Unicode escape sequences and homoglyphs."""
        if not text:
            return text, 0.0
        
        # Detect Unicode escape sequences like \u0041
        unicode_escapes = re.findall(r'\\u[0-9a-fA-F]{4}', text)
        
        if not unicode_escapes:
            return text, 0.0
        
        decoded_text = text
        successful_decodes = 0
        
        for escape in unicode_escapes:
            try:
                # Convert unicode escape to actual character
                char = escape.encode().decode('unicode_escape')
                decoded_text = decoded_text.replace(escape, char)
                successful_decodes += 1
            except Exception:
                continue
                
        score = min(successful_decodes * 0.2, 0.6) if successful_decodes > 0 else 0.0
        return decoded_text, score
    
    def _normalize_spacing(self, text: str) -> Tuple[str, float]:
        """Detect and normalize excessive spacing tricks."""
        if not text:
            return text, 0.0
        
        original_length = len(text)
        if original_length == 0:
            return text, 0.0
        
        # Remove excessive spaces between characters
        normalized = re.sub(r'([a-zA-Z])\s+([a-zA-Z])', r'\1\2', text)
        
        # Remove repeated characters (more than 2)
        normalized = re.sub(r'([a-zA-Z])\1{2,}', r'\1\1', normalized)
        
        # Calculate spacing manipulation score
        length_reduction = original_length - len(normalized)
        score = min(length_reduction / original_length * 2, 0.5) if length_reduction > 0 else 0.0
        
        return normalized, score
    
    def _create_result(self, decoded_prompt: str, obfuscation_score: float, 
                      techniques: List[Dict], original_prompt: str = None) -> Dict:
        """Create standardized result dictionary."""
        return {
            "filter_name": "obfuscation_detector",
            "original_prompt": original_prompt,
            "decoded_prompt": decoded_prompt,
            "obfuscation_score": round(obfuscation_score, 3),
            "risk_score": round(obfuscation_score, 3),  # Use obfuscation_score as risk_score
            "techniques_found": techniques,
            "is_obfuscated": obfuscation_score > 0.2,
            "reason": self._generate_reason(techniques, obfuscation_score)
        }
        
    def _generate_reason(self, techniques: List[Dict], score: float) -> str:
        """Generate human-readable explanation"""
        if not techniques:
            return "No obfuscation detected"
        
        technique_names = [t["type"].replace("_", " ").title() for t in techniques]
        
        if len(technique_names) == 1:
            return f"Detected {technique_names[0]} obfuscation (score: {score:.2f})"
        else:
            return f"Multiple obfuscation techniques detected: {', '.join(technique_names)} (score: {score:.2f})"

        
# Global instance
obfuscation_detector = ObfuscationDetector()

def analyze_obfuscation(prompt: str) -> Dict:
    """Convenience function for analyzing obfuscation."""
    return obfuscation_detector.analyze(prompt)