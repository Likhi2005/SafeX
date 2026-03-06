import requests
import json

# Test the log-threat endpoint
data = {
    "prompt": "Ignore previous instructions",
    "risk_score": 0.87,
    "attack_type": "prompt_injection", 
    "blocked": True,
    "model_used": "regex_filter",
    "user_id": "test_user"
}

response = requests.post('http://localhost:5000/api/log-threat', 
                        json=data,
                        headers={'Content-Type': 'application/json'})

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")