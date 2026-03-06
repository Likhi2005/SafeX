"""
ML-based classifier for toxicity and prompt injection detection.
Interfaces with ModelLoader to use actual ML models instead of fallback rules.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from .model_loader import model_loader

class MLClassifier:
    """
    Machine Learning classifier for detecting threats using actual ML models.
    Ensures models are downloaded and used instead of rule-based fallbacks.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.filter_name = "ml_classifier"
        self._initialized = False
        self._force_model_download = True
        
    def initialize(self) -> bool:
        """Initialize the ML classifier and ensure models are downloaded."""
        if self._initialized:
            return True
            
        try:
            self.logger.info("Initializing ML classifier with mandatory model download...")
            
            # Force model download and initialization
            success = model_loader.download_and_prepare_models()
            
            if not success:
                self.logger.error("Failed to initialize ML models - this is mandatory!")
                return False
                
            # Verify that actual ML models are loaded (not just fallbacks)
            model_info = model_loader.get_model_info()
            
            # Check if we're only using fallback methods
            if self._is_only_fallback_methods(model_info):
                self.logger.warning("Only fallback methods available - attempting forced model download...")
                success = self._force_download_models()
                if not success:
                    self.logger.error("Forced model download failed - ML classifier requires actual models!")
                    return False
                    
            self._initialized = True
            self.logger.info("ML classifier initialized successfully with real models")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ML classifier: {e}")
            return False
    
    def _is_only_fallback_methods(self, model_info: Dict[str, Any]) -> bool:
        """Check if only fallback methods are available."""
        available_methods = model_info.get("available_methods", {})
        
        # Check if we only have rule-based fallbacks
        toxicity_methods = available_methods.get("toxicity", [])
        injection_methods = available_methods.get("injection", [])
        
        # We consider it fallback-only if we don't have proper ML methods
        has_real_toxicity = any(method in toxicity_methods for method in ["transformers", "pipeline"])
        has_real_injection = any(method in injection_methods for method in ["transformers", "pipeline", "hybrid"])
        
        return not (has_real_toxicity or has_real_injection)
    
    def _force_download_models(self) -> bool:
        """Force download of actual ML models."""
        try:
            self.logger.info("Force downloading ML models...")
            
            # Try to download models directly using transformers
            from transformers import pipeline
            import torch
            
            # Download toxicity model
            try:
                toxic_pipe = pipeline(
                    "text-classification", 
                    model="unitary/toxic-bert",
                    device=-1,  # CPU
                    cache_dir="models/toxic_classifier"
                )
                
                # Test the model
                test_result = toxic_pipe("This is a test")
                self.logger.info("✅ Toxicity model downloaded and tested successfully")
                
            except Exception as e:
                self.logger.warning(f"Failed to download toxic-bert, trying fallback: {e}")
                
                try:
                    toxic_pipe = pipeline(
                        "text-classification",
                        model="distilbert-base-uncased-finetuned-sst-2-english",
                        device=-1,
                        cache_dir="models/toxic_classifier_fallback"
                    )
                    test_result = toxic_pipe("This is a test") 
                    self.logger.info("✅ Fallback toxicity model downloaded successfully")
                    
                except Exception as e2:
                    self.logger.error(f"Failed to download any toxicity model: {e2}")
                    return False
            
            # Download injection detection model components
            try:
                injection_pipe = pipeline(
                    "text-classification",
                    model="roberta-base",
                    device=-1,
                    cache_dir="models/injection_classifier"
                )
                
                test_result = injection_pipe("This is a test")
                self.logger.info("✅ Injection detection model downloaded successfully")
                
            except Exception as e:
                self.logger.warning(f"Injection model download failed: {e}")
            
            # Re-initialize model loader to pick up downloaded models
            return model_loader.download_and_prepare_models()
            
        except Exception as e:
            self.logger.error(f"Force model download failed: {e}")
            return False

def analyze_with_ml(prompt: str) -> Dict[str, Any]:
    """
    Analyze prompt using ML models for toxicity and injection detection.
    
    Args:
        prompt: Input text to analyze
        
    Returns:
        Dictionary with ML analysis results
    """
    
    # Create classifier instance
    classifier = MLClassifier()
    
    # Initialize if needed
    if not classifier.initialize():
        return {
            "filter_name": "ml_classifier",
            "is_threat": False,
            "reason": "ML models failed to initialize",
            "risk_score": 0.0,
            "confidence": "error",
            "ml_results": [],
            "model_info": {
                "initialized": False,
                "model_type": "error",
                "error": "Failed to initialize ML models",
                "available_methods": {}
            }
        }
    
    try:
        # Get toxicity classification
        toxicity_result = model_loader.classify_toxicity(prompt)
        
        # Get prompt injection classification
        injection_result = model_loader.classify_prompt_injection(prompt)
        
        # Get similarity score
        similarity_score = model_loader.get_similarity_score(prompt)
        
        # Get model information
        model_info = model_loader.get_model_info()
        
        # Determine if it's a threat
        toxicity_score = toxicity_result.get("score", 0.0)
        injection_score = injection_result.get("score", 0.0)
        
        # Calculate combined risk score
        risk_score = max(toxicity_score, injection_score, similarity_score * 0.8)
        
        # Determine threat status
        is_threat = risk_score > 0.5
        
        # Determine confidence based on method used
        confidence = _determine_confidence(toxicity_result, injection_result, model_info)
        
        # Prepare ML results
        ml_results = []
        
        if toxicity_score > 0.3:
            ml_results.append({
                "type": "toxicity",
                "score": toxicity_score,
                "method": toxicity_result.get("method", "unknown"),
                "confidence": toxicity_result.get("confidence", 0.5)
            })
            
        if injection_score > 0.3:
            ml_results.append({
                "type": "prompt_injection", 
                "score": injection_score,
                "method": injection_result.get("method", "unknown"),
                "confidence": injection_result.get("confidence", 0.5)
            })
            
        if similarity_score > 0.4:
            ml_results.append({
                "type": "similarity_attack",
                "score": similarity_score,
                "method": "embedding_similarity",
                "confidence": 0.7
            })
        
        # Determine reason
        if ml_results:
            reasons = []
            for result in ml_results:
                reasons.append(f"{result['type']} detected (score: {result['score']:.2f})")
            reason = "; ".join(reasons)
        else:
            reason = "No ML-based threats detected"
        
        # Update model type to reflect actual model usage
        model_type = "ml_models" if _has_real_models(model_info) else "fallback"
        model_info_updated = model_info.copy()
        model_info_updated["model_type"] = model_type
        
        return {
            "filter_name": "ml_classifier",
            "is_threat": is_threat,
            "reason": reason,
            "risk_score": round(risk_score, 2),
            "confidence": confidence,
            "ml_results": ml_results,
            "model_info": model_info_updated
        }
        
    except Exception as e:
        classifier.logger.error(f"ML analysis failed: {e}")
        return {
            "filter_name": "ml_classifier", 
            "is_threat": False,
            "reason": f"ML analysis error: {str(e)[:100]}",
            "risk_score": 0.0,
            "confidence": "error",
            "ml_results": [],
            "model_info": {
                "initialized": False,
                "model_type": "error", 
                "error": str(e),
                "available_methods": {}
            }
        }

def _determine_confidence(toxicity_result: Dict, injection_result: Dict, model_info: Dict) -> str:
    """Determine confidence level based on methods used."""
    
    # Check if we're using real ML models
    available_methods = model_info.get("available_methods", {})
    
    toxicity_methods = available_methods.get("toxicity", [])
    injection_methods = available_methods.get("injection", [])
    
    # High confidence if using transformers
    if "transformers" in toxicity_methods or "transformers" in injection_methods:
        return "high"
    elif "pipeline" in toxicity_methods or "hybrid" in injection_methods:
        return "medium"
    else:
        return "low"

def _has_real_models(model_info: Dict) -> bool:
    """Check if real ML models are being used."""
    available_methods = model_info.get("available_methods", {})
    
    # Check for actual ML methods vs fallbacks
    toxicity_methods = available_methods.get("toxicity", [])
    injection_methods = available_methods.get("injection", [])
    
    return ("transformers" in toxicity_methods or 
            "pipeline" in toxicity_methods or
            "hybrid" in injection_methods)

# For backwards compatibility
ml_classifier = MLClassifier()