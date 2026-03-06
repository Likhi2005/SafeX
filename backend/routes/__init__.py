from flask import Blueprint

# Import blueprints
from .health import health_bp
from .analysis import analysis_bp

# You can register these in app.py
__all__ = ['health_bp', 'analysis_bp']

"""
SafeX Backend - LLM Security Gateway
Production-grade prompt injection detection and sanitization.
"""

__version__ = "1.0.0"
__author__ = "SafeX Team"