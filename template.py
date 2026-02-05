import os
from pathlib import Path
import logging

# logging string
logging.basicConfig(level=logging.INFO,format='[%(asctime)s]: %(message)s')

project_name = "SafeX"

# Project structures

list_of_files = [
    
    # Backend
    "backend/__init__.py",
    "backend/app.py",
    "backend/requirements.txt",
    
    "backend/config/__init__.py",
    "backend/config/constants.py",
    "backend/config/settings.py",
    
    # Security filters
    "backend/filters/__init__.py",
    "backend/filters/regex_filter.py",
    "backend/filters/obfuscation_detector.py",
    # "backend/filters/sanitization_filter.py",
    # "backend/filters/input_validation.py",
    # "backend/filters/security_middleware.py",
    
    
    # ML Models
    "backend/ml/__init__.py",
    # "backend/ml/ml_classifier.py",
    # "backend/ml/similarity_detector.py",
    # "backend/ml/model_loader.py",
    
    # Core logic
    "backend/core/__init__.py",
    # "backend/core/policy_engine.py",
    # "backend/core/sanitizer.py",
    # "backend/core/redis_client.py",
    
    # Utils
    "backend/utils/__init__.py",
    # "backend/utils/logger.py",
    # "backend/utils/helpers.py",
    
    # Models directory
    "models/.gitkeep",
    "models/README.md",
    
    
    # Tests
    "tests/__init__.py",
    "tests/test_regex_filter.py",
    "tests/test_ml_classifier.py",
    "tests/test_policy_engine.py",
    
    
    # Scripts
    "scripts/download_models.py",
    "scripts/convert_to_onnx.py",
    "scripts/setup.sh",
    
]

# Create project structure
for filepath in list_of_files:
    filepath = Path(filepath)
    # older
    # filedir,filename = os.path.split(filepath)
    filedir = filepath.parent
    filename = filepath.name
    
    if filedir != "":
        os.makedirs(filedir,exist_ok=True)
        logging.info(f"Creating directory: {filedir} for file: {filename}")
    
    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath,"w") as f:
            pass
        logging.info(f"Creating empty file: {filepath}")
    else:
        logging.info(f"File already exists: {filepath}")
    


















# import os
# from pathlib import Path
# import logging

# # Logging configuration
# logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s')

# project_name = "ShieldGPT"

# # Project structure
# list_of_files = [
#     # Backend core structure
#     "backend/__init__.py",
#     "backend/app.py",
#     "backend/config/__init__.py",
#     "backend/config/constants.py",
#     "backend/config/settings.py",
    
#     # Security filters
#     "backend/filters/__init__.py",
#     "backend/filters/regex_filter.py",
#     "backend/filters/obfuscation_detector.py",
    
#     # ML models
#     "backend/ml/__init__.py",
#     "backend/ml/ml_classifier.py",
#     "backend/ml/similarity_detector.py",
#     "backend/ml/model_loader.py",
    
#     # Core logic
#     "backend/core/__init__.py",
#     "backend/core/policy_engine.py",
#     "backend/core/sanitizer.py",
#     "backend/core/redis_client.py",
    
#     # Utils
#     "backend/utils/__init__.py",
#     "backend/utils/logger.py",
#     "backend/utils/helpers.py",
    
#     # Models directory
#     "models/.gitkeep",
#     "models/README.md",
    
#     # Frontend
#     "frontend/package.json",
#     "frontend/public/index.html",
#     "frontend/src/App.jsx",
#     "frontend/src/index.jsx",
#     "frontend/src/components/PromptTester.jsx",
#     "frontend/src/components/RiskDisplay.jsx",
#     "frontend/tailwind.config.js",
    
#     # Docker
#     "docker/Dockerfile.backend",
#     "docker/Dockerfile.frontend",
#     "docker-compose.yml",
    
#     # Deployment configs
#     ".env.example",
#     ".gitignore",
#     "requirements.txt",
#     "README.md",
    
#     # Tests
#     "tests/__init__.py",
#     "tests/test_regex_filter.py",
#     "tests/test_ml_classifier.py",
#     "tests/test_policy_engine.py",
    
#     # Scripts
#     "scripts/download_models.py",
#     "scripts/convert_to_onnx.py",
#     "scripts/setup.sh",
# ]

# # Create directory structure
# for filepath in list_of_files:
#     filepath = Path(filepath)
#     filedir, filename = os.path.split(filepath)
    
#     if filedir != "":
#         os.makedirs(filedir, exist_ok=True)
#         logging.info(f"Creating directory: {filedir} for file: {filename}")
    
#     if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
#         with open(filepath, "w") as f:
#             pass
#         logging.info(f"Creating empty file: {filepath}")
#     else:
#         logging.info(f"File already exists: {filepath}")