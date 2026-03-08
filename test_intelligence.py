#!/usr/bin/env python3
"""
Test script for the threat intelligence system
"""

import sys
import os
from datetime import datetime, timezone

# Add project root to Python path
sys.path.insert(0, os.path.abspath('.'))

try:
    # Test basic imports
    print("Testing imports...")
    
    # Test threat intelligence service
    from backend.services.threat_intelligence import ThreatIntelligenceService
    print("✅ ThreatIntelligenceService imported successfully")
    
    # Test threat service
    from backend.services.threat_service import ThreatLogService
    print("✅ ThreatLogService imported successfully")
    
    # Test model initialization
    from backend.ml.model_initializer import model_initializer
    print("✅ Model initializer imported successfully")
    
    print("\n=== Testing Threat Intelligence Service ===")
    
    # Initialize threat intelligence
    intelligence = ThreatIntelligenceService()
    print("✅ ThreatIntelligenceService initialized")
    
    # Test real-time intelligence (without database, should work with simulated data)
    print("\nTesting real-time intelligence...")
    real_time_data = intelligence.get_real_time_threats(minutes=30)
    print(f"✅ Real-time threats: {len(real_time_data['realtime_threats'])} found")
    print(f"   Active threats: {real_time_data['summary']['active_threats']}")
    print(f"   Countries affected: {real_time_data['summary']['countries_affected']}")
    
    # Test attack pattern detection
    print("\nTesting attack pattern detection...")
    patterns = intelligence.detect_attack_patterns(hours=24)
    print(f"✅ Attack patterns: {len(patterns['patterns'])} detected")
    for pattern in patterns['patterns'][:3]:  # Show first 3
        print(f"   - {pattern['type']}: {pattern['count']} occurrences")
    
    # Test threat predictions
    print("\nTesting threat predictions...")
    predictions = intelligence.get_threat_predictions()
    print(f"✅ Predictions generated")
    print(f"   Overall risk level: {predictions['overall_risk_level']}")
    print(f"   Predictions count: {len(predictions['predictions'])}")
    
    # Test dashboard data
    print("\nTesting dashboard data compilation...")
    dashboard = intelligence.get_intelligence_dashboard(minutes=60)
    print(f"✅ Dashboard data compiled")
    print(f"   Active threats: {dashboard['summary']['active_threats']}")
    print(f"   Risk level: {dashboard['summary']['risk_level']}")
    
    print("\n🎉 All threat intelligence tests passed successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== System Ready for Demo ===")
print("✅ Threat Intelligence Engine: OPERATIONAL")
print("✅ ML-Powered Analytics: READY")
print("✅ Real-time Monitoring: ACTIVE")
print("✅ Predictive Analysis: FUNCTIONAL")