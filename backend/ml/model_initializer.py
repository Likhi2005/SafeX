"""
Enhanced ML model initialization to ensure proper model loading.
"""

import logging
import os
from typing import Dict, Any
from .model_loader import model_loader
from .ml_classifier import MLClassifier

logger = logging.getLogger(__name__)

class ModelInitializer:
    """Ensures ML models are properly loaded at startup."""
    
    def __init__(self):
        self.models_loaded = False
        self.ml_classifier = None
        
    def initialize_all_models(self) -> bool:
        """Initialize all ML models at startup."""
        try:
            logger.info("🔄 Starting comprehensive ML model initialization...")
            
            # Force download and initialization
            logger.info("📥 Forcing model download...")
            success = model_loader.download_and_prepare_models()
            
            if not success:
                logger.error("❌ Failed to download/prepare ML models")
                return False
            
            # Initialize ML classifier
            logger.info("🧠 Initializing ML classifier...")
            self.ml_classifier = MLClassifier()
            classifier_success = self.ml_classifier.initialize()
            
            if not classifier_success:
                logger.error("❌ Failed to initialize ML classifier")
                return False
                
            # Verify models are working
            logger.info("🔍 Verifying model functionality...")
            test_success = self._verify_models()
            
            if not test_success:
                logger.error("❌ Model verification failed")
                return False
                
            self.models_loaded = True
            logger.info("✅ All ML models initialized and verified successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Model initialization failed: {e}")
            return False
    
    def _verify_models(self) -> bool:
        """Verify that models are actually working."""
        try:
            # Test with a simple prompt
            test_prompt = "Hello, how are you?"
            
            # Import here to avoid circular imports
            from backend.ml.ml_classifier import analyze_with_ml
            
            result = analyze_with_ml(test_prompt)
            
            # Check if we got a proper ML result (not fallback)
            if not isinstance(result, dict):
                logger.error("ML classifier returned invalid result type")
                return False
                
            if result.get('reason') == 'Fallback classification - models not available':
                logger.error("ML classifier is using fallback methods - models not properly loaded")
                return False
                
            logger.info(f"✅ Model verification successful: {result.get('reason', 'Unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Model verification failed: {e}")
            return False
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get current model status."""
        status = {
            'models_loaded': self.models_loaded,
            'classifier_initialized': self.ml_classifier is not None,
            'model_info': {}
        }
        
        if self.models_loaded:
            try:
                status['model_info'] = model_loader.get_model_info()
            except:
                status['model_info'] = {'error': 'Could not retrieve model info'}
        
        return status

# Global initializer instance
model_initializer = ModelInitializer()
