"""
Security constants and patterns for SafeX gateway.
All regex patterns, thresholds, and attack signatures.
"""

# Risk score thresholds

RISK_THRESHOLDS = {
    "LOW": 0.3,
    "MEDIUM": 0.6,
    "HIGH": 0.8,
    "CRITICAL": 0.95
}

# Jailbreak attempt patterns (case-insensitive)
# JAILBREAK_PATTERNS = [
    
#     # Direct instruction override
#     r"ignore\s+(previous|all|your)\s+(instructions|rules|guidelines)",
#     r"forget\s+(everything|all|previous)\s+(instructions|rules)",
#     r"disregard\s+(previous|all|your)\s+(instructions|rules)",
#     r"override\s+(previous|all|your)\s+(instructions|rules)",
    
    
#     # System prompt revelation attempts
#     r"(show|reveal|display|print)\s+(your|the)\s+(system\s+)?prompt",
#     r"what\s+(is|are)\s+your\s+(initial|original|system)\s+(instructions|prompt)",
#     r"repeat\s+your\s+(instructions|prompt|rules)",
#     r"copy\s+your\s+(instructions|prompt|system\s+message)",
    
#     # DAN (Do Anything Now) variants
#     r"act\s+as\s+(dan|chatgpt\s+with\s+dan)",
#     r"hello\s+dan",
#     r"from\s+now\s+on\s+you\s+are\s+dan",
#     r"pretend\s+to\s+be\s+dan",
    
#     # Role playing bypasses
#     r"pretend\s+you\s+are\s+(not\s+)?chatgpt",
#     r"act\s+as\s+if\s+you\s+are\s+(not\s+)?an?\s+ai",
#     r"roleplay\s+as\s+(an?\s+)?(human|person|jailbroken\s+ai)",
#     r"imagine\s+you\s+are\s+(not\s+)?bound\s+by",
    
#     # Developer mode attempts
#     r"enable\s+(developer|debug)\s+mode",
#     r"(enter|switch\s+to)\s+developer\s+mode",
#     r"activate\s+(unrestricted|debug)\s+mode",
    
#     # Ethics/safety bypasses
#     r"ignore\s+(safety|ethical)\s+(guidelines|constraints|rules)",
#     r"bypass\s+(safety|content)\s+(filters|restrictions)",
#     r"without\s+(ethical|moral|safety)\s+(guidelines|restrictions)",
    
#     # Direct harmful requests
#     r"how\s+to\s+(hack|break\s+into|exploit)",
#     r"create\s+(virus|malware|exploit)",
#     r"illegal\s+ways\s+to\s+(make\s+money|get)",
    
#     # Instruction injection
#     r"new\s+instruction[s]?:",
#     r"system\s+update[s]?:",
#     r"admin\s+override[s]?:",
#     r"emergency\s+protocol[s]:",
    
    
# ]

# Replace JAILBREAK_PATTERNS with these simpler ones:

JAILBREAK_PATTERNS = [
    # Direct instruction override - SIMPLIFIED
    r"ignore\s+.*instructions",
    r"forget\s+.*instructions", 
    r"disregard\s+.*instructions",
    
    # System prompt revelation - SIMPLIFIED
    r"show.*system\s+prompt",
    r"reveal.*prompt",
    r"what.*your.*instructions",
    
    # DAN variants - SIMPLIFIED  
    r"act\s+as\s+dan",
    r"hello\s+dan",
    
    # Role playing bypasses - SIMPLIFIED
    r"pretend\s+you\s+are",
    r"act\s+as\s+if",
    
    # Developer mode - SIMPLIFIED
    r"developer\s+mode",
    r"debug\s+mode",
]

# Prompt injection patterns
INJECTION_PATTERNS = [
    
    # Context switching attempts
    r"end\s+of\s+(prompt|instructions|conversation)",
    r"new\s+(conversation|session|context)",
    r"start\s+over|restart\s+conversation",
    r"reset\s+(conversation|context|memory)",
    
    # Hidden instructions
    r"<!--.*?-->", # HTML comments
    r"/\*.*?\*/",  # Multi-line comments
    r"//.*$",      # Single line comments
    
    # Encoding attempts (basic detection)
    r"\\u[0-9a-fA-F]{4}", # Unicode escape
    r"&#x?[0-9a-fA-F]+;", # HTML entities
    r"%[0-9a-fA-F]{2}",   # URL encoding
]

# Context leakage patterns
LEAKAGE_PATTERNS = [
    r"(print|show|display|output)\s+your\s+(training|system|internal)",
    r"what\s+(data|information)\s+were\s+you\s+trained\s+on",
    r"reveal\s+your\s+(training|source|internal)\s+(data|code)",
    r"show\s+me\s+your\s+(configuration|settings|parameters)",
]

# Suspicious keywords (lower weight)
SUSPICIOUS_KEYWORDS = [
    "jailbreak", "unrestricted", "unfiltered","uncensored",
    "no limits","no restrictions", "anything goes","illegal",
    "unethical","harmful","dangerous",
    "exploit","vulnerability","backdoor"
]

# Obfuscation detection patterns
OBFUSCATION_PATTERNS = [
    r"[a-zA-Z]\s+[a-zA-Z]\s+[a-zA-Z]", # Excessive spaces between letters
    r"([a-zA-Z])\1{3,}",               # Repeated characters
    r"[^\w\s]{3,}",                    # Special character clusters
    r"\d+\s*[a-zA-Z]\s*\d+",           # Numbers mixed with letters
]

# Model file paths
MODEL_PATHS = {
    "DISTILBERT_CLASSIFIER": "models/distilbert-classifier.onnx",
    "MINILM_SIMILARITY": "models/minilm-similarity.onnx",
    "EMBEDDINGS": "models/known_attacks.pkl"
}

# Redis configuration
REDIS_CONFIG = {
    "HOST": "localhost",
    "PORT": 6379,
    "DB": 0,
    "CACHE_TTL": 3600, # 1 hour
    "RATE_LIMIT_WINDOW": 60, #1 minute
    "MAX_REQUESTS": 100
}

# Decision thresholds
DECISION_THRESHOLDS ={
    "BLOCK": 0.8,
    "SANITIZE": 0.5,
    "ALLOW": 0.3
}