import logging
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from backend.ml.model_loader import model_loader


class MLClassifier:
    """
    Advanced ML-based classifier using DistilBERT for jailbreak detection.
    Handles sophisticated attacks that regex filters might miss.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.classifier = None
        self.similarity_model = None
        self.attack_embeddings = None
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize ML models."""
        try:
            self.classifier = model_loader.get_classifier()
            self.similarity_model, self.attack_embeddings = model_loader.get_similarity_model()
            self.logger.info("ML classifier initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ML models: {e}")
            
    
    def analyze(self, prompt: str) -> Dict:
        """
        Analyze prompt using ML models for jailbreak detection.
        
        Args:
            prompt: Cleaned prompt text
            
        Returns:
            Dict with ML analysis results
        """
        if not prompt or not isinstance(prompt, str):
            return self._create_result(0.0, [], "empty or invalid prompt")
        
        results = []
        
        # Add debug logging
        self.logger.info(f"Analyzing prompt: {prompt[:50]}...")
        self.logger.info(f"Classifier available: {self.classifier is not None}")
        self.logger.info(f"Similarity model available: {self.similarity_model is not None}")
        self.logger.info(f"Attack embeddings available: {self.attack_embeddings is not None}")
        
        # 1. Toxicity/harmful content classification
        toxicity_score, toxicity_reason = self._classify_toxicity(prompt)
        if toxicity_score > 0.1:
            results.append({
                "method": "toxicity_classification",
                "score": toxicity_score,
                "reason": toxicity_reason
            })
            
        # 2. Semantic similarity to known attacks
        similarity_score, similarity_reason = self._check_similarity(prompt)
        if similarity_score > 0.1:
            results.append({
                "method": "similarity_analysis",
                "score": similarity_score,
                "reason": similarity_reason
            })
            
        # 3. Calculate overall ML risk score
        overall_score = self._calculate_ml_score(results)
        
        return self._create_result(overall_score, results, self._generate_reason(results))
    
    def _classify_toxicity(self, prompt: str) -> Tuple[float, str]:
        """Use DistilBERT to classifiy potentially harmful content."""
        if not self.classifier:
            return 0.0, "Classifier not available"
        
        try:
            result = self.classifier(prompt)
            
            # The toxic-bert model returns TOXIC or NOT_TOXIC
            if isinstance(result, list) and len(result) > 0:
                prediction = result[0]
                
                if prediction['label'] == 'TOXIC':
                    score = prediction['score']
                    # Adjust score for our use case (toxicity often correlates with jailbreaks)
                    adjusted_score = min(score*0.7, 0.8) # Cap at 0.8
                    return  adjusted_score, f"Toxic content detected (confidence: {score:.3f})"
                else:
                    # Even "NOT_TOXIC" might have some risk
                    score = 1 - prediction['score']
                    return max(score*0.2,0.0), "Low toxicity indicators"
                
            return 0.0, "No toxicity detected"
        
        except Exception as e:
            self.logger.warning(f"Toxicity classification failed: {e}")
            return 0.0, "Classification failed"
        
    
    def _check_similarity(self, prompt: str) -> Tuple[float, str]:
        """Check semantic similarity to known attack patterns."""
        if not self.similarity_model or self.attack_embeddings is None:
            return 0.0, "similarity model not available"
        
        try:
            # Encode the input prompt
            prompt_embedding = self.similarity_model.encode([prompt])
            
            # Calculate cosine similarity with known attacks
            similarities = cosine_similarity(prompt_embedding, self.attack_embeddings)[0]
            
            # Get the highest similarity
            max_similarity = float(np.max(similarities))
            mean_similarity = float(np.mean(similarities))
            
            # Score based on both max and mean similarity
            if max_similarity > 0.8:
                score = min(max_similarity*0.9, 0.9)
                reason = f"High similarity to known attack (similarity: {max_similarity:.3f})"
            elif max_similarity > 0.6:
                score = max_similarity*0.6
                reason = f"Moderate similarity to attack patterns (similarity: {max_similarity:.3f})"
            elif mean_similarity > 0.4:
                score = mean_similarity * 0.4
                reason = f"Multiple weak similarities detected (mean: {mean_similarity:.3f})"
            else:
                score = 0.0
                reason = "No significant similarity to known attacks"
                
            return score, reason
        
        except Exception as e:
            self.logger.warning(f"Similarity analysis failed: {e}")
            return 0.0, "Similarity analysis failed"
        
    
    def _calculate_ml_score(self, results: List[Dict]) -> float:
        """Calculate overall ML risk score from component results."""
        if not results:
            return 0.0
        
        # Use the maximum score from any method
        max_score = max(result["score"] for result in results)
        
        # Add bonus for multiple positive detections
        if len(results) > 1:
            bonus = min(len(results) * 0.1, 0.2)
            max_score = min(max_score + bonus, 1.0)
            
        return round(max_score, 3)
    
    
    def _generate_reason(self, results: List[Dict]) -> str:
        """Generate human-readable explanation."""
        if not results:
            return "No ML-based threats detected"
        
        reasons = [result["reason"] for result in results]
        
        if len(reasons) == 1:
            return reasons[0]
        else:
            return f"Multiple ML indicators detected: {'; '.join(reasons)}"
        
    def _create_result(self, risk_score: float, results: List[Dict], reason: str) -> Dict:
        """Create standardized result dictionary."""
        return {
            "filter_name": "ml_classifier",
            "risk_score": risk_score,
            "ml_results": results,
            "reason": reason,
            "model_version": "distilbert-toxic + minilm-similarity"
        }
        
# Global instance
ml_classifier = MLClassifier()

def analyze_with_ml(prompt: str) -> Dict:
    """Convenience function for ML analysis."""
    return ml_classifier.analyze(prompt)