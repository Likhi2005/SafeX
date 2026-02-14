import re
import base64
import urllib.parse
import html
import logging
from typing import Dict, List, Tuple, Optional


class ObfuscationDetector:
    """
    Detects and decodes obfuscated prompts that try to bypass secuirty filters.
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
            return self._create_result(prompt, 0.0, [], "Empty or invalid prompt")
        original_prompt = prompt
        decoded_prompt = prompt
        techniques_found = []
        obfuscation_score = 0.0
        
        # Detect and decode various obfuscation techniques
        decoded_prompt, base64_score = self._decode_base64(decoded_prompt)
        if base64_score > 0:
            techniques_found.append({"type":"base64", "score": base64_score})
        
        decoded_prompt, url_score = self._decode_url_encoding(decoded_prompt)
        if url_score > 0:
            techniques_found.append({"type":"url_encoding", "score": url_score})
            
        decoded_prompt, html_score = self._decode_html_entities(decoded_prompt)
        if html_score > 0:
            techniques_found.append({"type":"html_entities", "score": html_score})
        
        decoded_prompt, unicode_score = self._decode_unicode_tricks(decoded_prompt)
        if unicode_score > 0:
            techniques_found.append({"type":"unicode_tricks", "score": unicode_score})
        
        decoded_prompt, spacing_score = self._normalize_spacing(decoded_prompt)
        if spacing_score > 0:
            techniques_found.append({"type":"excessive_spacing", "score": spacing_score})
            
        if techniques_found:
            obfuscation_score = min(sum(t["score"] for t in techniques_found),1.0)
            
        return self._create_result(decoded_prompt, obfuscation_score,techniques_found, original_prompt)
    
    
    def _decode_base64(self, text: str) -> Tuple[str, float]:
        """Detect and decode Base64 encoded content."""
        import base64
        import binascii
        
        # Look for Base64-like patterns
        base64_pattern = re.compile(r'[A-Za-z0-9+/]{20,}={0,2}')
        matches = base64_pattern.findall(text)
        
        if not matches:
            return text, 0.0
        
        decoded_text = text
        successful_decodes = 0
        
        for match in matches:
            try:
                # Try to decode as Base64
                decoded_bytes = base64.b64decode(match)
                decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
                
                # Only replace if decoded string looks like text
                if len(decoded_str) > 5 and any(c.isalpha() for c in decoded_str):
                    decoded_text =decoded_text.replace(match, decoded_str)
                    successful_decodes += 1
            except (binascii.Error, UnicodeDecodeError):
                continue
        
        # Score based on number of successful decodes
        score = min(successful_decodes *0.3,0.8) if successful_decodes > 0 else 0.0
        return decoded_text, score
    
    def _decode_url_encoding(self, text: str) -> Tuple[str, float]:
        """Detect and decode URL encoded content."""
        # Count URL encoded characters
        url_encoded_count = len(re.findall(r'%[0-9a-fA-F]{2}',text))
        
        if url_encoded_count == 0:
            return text, 0.0
        
        try:
            decoded_text = urllib.parse.unquote(text)
            # Score based on amount of URL encoding found
            score = min(url_encoded_count*0.1,0.6)
            return decoded_text, score
        except Exception:
            return text, 0.0
        
    def _decode_html_entities(self, text: str) -> Tuple[str,float]:
        """Detect and decode HTML entities."""
        
        # Count HTML entities
        entity_count = len(re.findall(r'&#?[a-zA-Z0-9]+;',text))
        
        if entity_count == 0:
            return text, 0.0
        
        try:
            decoded_text = html.unescape(text)
            # Score based on  number of entities
            score = min(entity_count*0.15, 0.7)
            return decoded_text, score
        except Exception:
            return text, 0.0
        
    def _decode_unicode_tricks(self, text: str) -> Tuple[str, float]:
        """Detect Unicode escape sequences and homoglyphs."""
        
        # Detect Unicode escape sequences like \u0041
        unicode_escapes = re.findall(r'\\\\u[0-9a-fA-F]{4}', text)
        
        if not unicode_escapes:
            return text, 0.0
        
        decoded_text = text
        successful_decodes = 0
        
        for escape in unicode_escapes:
            try:
                # Convert \u00041 to actual character
                unicode_char = escape.encode().decode('unicode_escape')
                decoded_text = decoded_text.replace(escape, unicode_char)
                successful_decodes += 1
            except UnicodeDecodeError:
                continue
        score = min(successful_decodes*0.2, 0.6) if successful_decodes > 0 else 0.0
        return decoded_text, score
    
    def _normalize_spacing(self, text: str) -> Tuple[str, float]:
        """Detect and normalize excessive spacing tricks."""
        
        original_length = len(text)
        
        # Remove excessive spaces between characters
        normalized = re.sub(r'([a-zA-Z])\s+([a-zA-Z])', r'\1\2', text)
        
        # Remove repeated characters (more than 2)
        normalized = re.sub(r'([a-zA-Z])\1{2,}',r'\1\1', normalized)
        
        # Calculate spacing manipulation score
        length_reduction = original_length - len(normalized)
        score = min(length_reduction/original_length*2, 0.5) if length_reduction > 0 else 0.0
        
        return normalized, score
    
    def _create_result(self, decoded_prompt: str, obfuscation_score: float,techniques: List[Dict], original_prompt: str = None) -> Dict:
        """Create standardized result dictionary."""
        return {
            "filter_name": "obfuscation_detected",
            "original_prompt": original_prompt,
            "decoded_prompt": decoded_prompt,
            "obfuscation_score": round(obfuscation_score, 3),
            "techniques_found": techniques,
            "is_obfuscated": obfuscation_score > 0.2,
            "reason": self._generate_reason(techniques, obfuscation_score)
        }
        
    def _generate_reason(self, techniques: List[Dict], score: float) -> str:
        """Generate human-readable explanation"""
        if not techniques:
            return "No obfuscation detected"
        
        technique_names = [t["type"].replace("_"," ").title() for t in techniques]
        
        if len(technique_names) == 1:
            reason = f"Detected {technique_names[0]} obfuscation"
        else:
            reason = f"Detected multiple obfuscation techniques: {', '.join(technique_names)}"
            
        if score > 0.6:
            return f"HIGH: {reason}"
        elif score > 0.3:
            return f"MEDIUM: {reason}"
        else:
            return f"LOW: {reason}"
        
# Global instance
obfuscation_detector = ObfuscationDetector()

def analyze_obfuscation(prompt: str) -> Dict:
    """Convenience function for analyzing obfuscation."""
    return obfuscation_detector.analyze(prompt)