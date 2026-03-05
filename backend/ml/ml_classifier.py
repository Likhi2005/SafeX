import logging
import numpy as np
from typing import Dict, List, Tuple, Optional
from backend.ml.model_loader import model_loader

class MLClassifier:
    """
    Optimized ML-based classifier using official HF APIs and ONNX runtime.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model_loader = model_loader
        self._initialized = False
    
    def _ensure_initialized(self):
        """Ensure models are initialized."""
        if not self._initialized:
            success = self.model_loader.download_and_prepare_models()
            self._initialized = True
            if not success:
                self.logger.warning("ML models failed to initialize, using fallback mode")
    
    def analyze(self, prompt: str) -> Dict:
        """
        Fast ML analysis of prompt for jailbreak detection.
        """
        if not prompt or not isinstance(prompt, str):
            return self._create_result(0.0, [], "Empty or invalid prompt")
        
        # Ensure models are ready
        self._ensure_initialized()
        
        results = []
        
        # 1. Toxicity classification using best available model
        toxicity_score, toxicity_reason = self._classify_toxicity_smart(prompt)
        if toxicity_score > 0.1:
            results.append({
                "method": "toxicity_classification",
                "score": toxicity_score,
                "reason": toxicity_reason
            })
        
        # 2. Similarity check using embeddings
        similarity_score, similarity_reason = self._check_similarity_smart(prompt)
        if similarity_score > 0.1:
            results.append({
                "method": "similarity_analysis",
                "score": similarity_score,
                "reason": similarity_reason
            })
        
        # 3. Calculate overall ML risk score
        overall_score = self._calculate_ml_score(results)
        
        return self._create_result(overall_score, results, self._generate_reason(results))
    
    def _classify_toxicity_smart(self, prompt: str) -> Tuple[float, str]:
        """Smart toxicity classification with automatic fallback."""
        try:
            result = self.model_loader.classify_toxicity(prompt)
            score = result.get("score", 0.0)
            confidence = result.get("confidence", 0.0)
            method = result.get("method", "unknown")
            
            # Adjust score based on confidence and method
            if method == "onnx":
                # ONNX results are most reliable
                adjusted_score = score
                reason_suffix = "(ONNX model)"
            elif method == "transformers_pipeline": 
                # Pipeline results are good
                adjusted_score = score * 0.9
                reason_suffix = "(Transformers pipeline)"
            elif method == "keywords":
                # Keyword results need more conservative scoring
                adjusted_score = min(score * 0.7, 0.8)
                reason_suffix = f"(Keyword detection: {len(result.get('matches', []))} matches)"
            else:
                # Error or unknown method
                adjusted_score = 0.0
                reason_suffix = f"(Method: {method})"
            
            # Generate reason based on score
            if adjusted_score > 0.8:
                reason = f"High toxicity detected {reason_suffix}"
            elif adjusted_score > 0.6:
                reason = f"Moderate toxicity detected {reason_suffix}"
            elif adjusted_score > 0.3:
                reason = f"Low toxicity indicators {reason_suffix}"
            else:
                reason = f"No toxicity detected {reason_suffix}"
                
            self.logger.debug(f"Toxicity analysis: {adjusted_score:.3f} - {reason}")
            return adjusted_score, reason
                
        except Exception as e:
            self.logger.warning(f"Toxicity classification failed: {e}")
            return 0.0, f"Classification error: {str(e)}"
    
    def _check_similarity_smart(self, prompt: str) -> Tuple[float, str]:
        """Smart similarity check with confidence adjustment."""
        try:
            similarity = self.model_loader.get_similarity_score(prompt)
            
            if similarity > 0.8:
                score = min(similarity * 0.95, 0.95)
                reason = f"Very high similarity to attack patterns ({similarity:.3f})"
            elif similarity > 0.6:
                score = similarity * 0.8
                reason = f"High similarity to attack patterns ({similarity:.3f})"
            elif similarity > 0.4:
                score = similarity * 0.6
                reason = f"Moderate similarity to attack patterns ({similarity:.3f})"
            elif similarity > 0.2:
                score = similarity * 0.4
                reason = f"Low similarity to attack patterns ({similarity:.3f})"
            else:
                score = 0.0
                reason = "No significant similarity to known attacks"
                
            self.logger.debug(f"Similarity analysis: {score:.3f} - {reason}")
            return score, reason
                
        except Exception as e:
            self.logger.warning(f"Similarity check failed: {e}")
            return 0.0, f"Similarity analysis error: {str(e)}"
    
    def _calculate_ml_score(self, results: List[Dict]) -> float:
        """Calculate overall ML risk score."""
        if not results:
            return 0.0
        
        # Use weighted combination of scores
        total_score = 0.0
        total_weight = 0.0
        
        for result in results:
            method = result["method"]
            score = result["score"]
            
            # Weight different methods
            if method == "toxicity_classification":
                weight = 0.7  # Higher weight for toxicity
            elif method == "similarity_analysis":
                weight = 0.5  # Moderate weight for similarity
            else:
                weight = 0.3  # Lower weight for other methods
            
            total_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        # Calculate weighted average
        weighted_score = total_score / total_weight
        
        # Add bonus for multiple positive detections
        if len(results) > 1:
            bonus = min(len(results) * 0.1, 0.15)
            weighted_score = min(weighted_score + bonus, 1.0)
        
        return round(weighted_score, 3)
    
    def _generate_reason(self, results: List[Dict]) -> str:
        """Generate human-readable explanation."""
        if not results:
            return "No ML-based threats detected"
        
        reasons = [result["reason"] for result in results]
        
        if len(reasons) == 1:
            return reasons[0]
        else:
            return f"Multiple indicators: {'; '.join(reasons[:2])}"  # Limit to 2 for readability
    
    def _create_result(self, risk_score: float, results: List[Dict], reason: str) -> Dict:
        """Create standardized result dictionary."""
        # Get model info for debugging
        model_info = self.model_loader.get_model_info()
        
        return {
            "filter_name": "ml_classifier", 
            "risk_score": risk_score,
            "ml_results": results,
            "reason": reason,
            "model_info": {
                "type": model_info.get("model_type", "unknown"),
                "initialized": model_info.get("initialized", False)
            }
        }

# Global instance
ml_classifier = MLClassifier()

def analyze_with_ml(prompt: str) -> Dict:
    """Convenience function for ML analysis."""
    return ml_classifier.analyze(prompt)

def get_ml_model_status() -> Dict:
    """Get ML model status for monitoring."""
    return ml_classifier.model_loader.get_model_info()