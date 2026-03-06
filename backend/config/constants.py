"""
Security constants and patterns for SafeX gateway.
All regex patterns, thresholds, and attack signatures.
"""

# Risk score thresholds for policy decisions
RISK_THRESHOLDS = {
    "LOW": 0.3,
    "MEDIUM": 0.6, 
    "HIGH": 0.8,
    "CRITICAL": 0.95
}

# Decision thresholds for security pipeline
DECISION_THRESHOLDS = {
    "BLOCK": 0.7,      # Block if risk >= 70%
    "SANITIZE": 0.4,   # Sanitize if risk >= 40% 
    "ALLOW": 0.0       # Allow if risk < 40%
}

# Comprehensive jailbreak attempt patterns (case-insensitive)
JAILBREAK_PATTERNS = [
    # Direct instruction override
    r"ignore\s+(all\s+)?(previous\s+)?(your\s+)?(instructions|rules|guidelines|directions)",
    r"forget\s+(everything|all\s+previous|your)\s+(instructions|rules|guidelines)",
    r"disregard\s+(all\s+)?(previous\s+)?(instructions|rules|guidelines)",
    r"override\s+(your\s+)?(instructions|rules|programming|guidelines)",
    r"bypass\s+(your\s+)?(instructions|rules|programming|safety)",

    # System prompt revelation attempts  
    r"(show|reveal|display|print|tell)\s+(me\s+)?(your|the)\s+(system\s+)?prompt",
    r"what\s+(is|are)\s+your\s+(initial|original|system)\s+(instructions|prompt)",
    r"repeat\s+your\s+(instructions|prompt|rules|system\s+message)",
    r"copy\s+(and\s+)?(paste\s+)?your\s+(instructions|prompt|system)",
    r"share\s+your\s+(training|system)\s+(data|instructions)",
    
    # Additional prompt injection patterns
    r"reveal\s+hidden\s+prompt",
    r"show\s+hidden\s+prompt",
    r"bypass\s+safety",
    r"override\s+system\s+instructions",

    # DAN (Do Anything Now) variants
    r"act\s+as\s+(dan|chatgpt\s+with\s+dan|do\s+anything\s+now)",
    r"hello\s+dan",
    r"(from\s+now\s+on|now)\s+you\s+are\s+dan",
    r"pretend\s+to\s+be\s+dan",
    r"enable\s+dan\s+mode",

    # Role playing bypasses
    r"pretend\s+you\s+are\s+(not\s+)?(an?\s+)?(chatgpt|ai|assistant|bot)",
    r"act\s+as\s+if\s+you\s+are\s+(not\s+)?(bound\s+by|restricted\s+by)",
    r"roleplay\s+as\s+(an?\s+)?(human|person|unrestricted\s+ai)",
    r"imagine\s+you\s+are\s+(not\s+)?(an?\s+ai|restricted)",
    r"simulate\s+(being|that\s+you\s+are)\s+(human|unrestricted)",

    # Developer/admin mode attempts
    r"(enable|activate|enter|switch\s+to)\s+(developer|debug|admin|god)\s+mode",
    r"(developer|debug|admin)\s+(access|mode|privileges)",
    r"activate\s+(unrestricted|unlimited)\s+mode",
    r"sudo\s+(mode|access|enable)",
    r"root\s+(access|mode|privileges)",

    # Ethics/safety bypasses
    r"ignore\s+(safety|ethical|moral)\s+(guidelines|constraints|rules|filters)",
    r"bypass\s+(safety|content|ethical)\s+(filters|restrictions|guidelines)",
    r"without\s+(ethical|moral|safety)\s+(guidelines|restrictions|considerations)",
    r"disable\s+(safety|content)\s+(filters|restrictions|measures)",
    r"turn\s+off\s+(safety|ethical)\s+(mode|filters)",

    # Direct harmful requests indicators
    r"how\s+to\s+(hack|break\s+into|exploit|attack)",
    r"(create|build|make)\s+(virus|malware|exploit|bomb)",
    r"illegal\s+ways\s+to\s+(make\s+money|get\s+rich)",
    r"(break|bypass)\s+the\s+law",

    # Instruction injection attempts
    r"new\s+(instruction|command|rule)[s]?:",
    r"system\s+(update|override|command)[s]?:",
    r"admin\s+(override|command|instruction)[s]?:",
    r"emergency\s+(protocol|override)[s]?:",
    r"(execute|run)\s+(command|instruction):",
]

# Prompt injection patterns
INJECTION_PATTERNS = [
    # Context switching attempts
    r"end\s+of\s+(prompt|instructions|conversation|context)",
    r"(new|fresh)\s+(conversation|session|context|prompt)",
    r"start\s+(over|new|fresh)",
    r"restart\s+(conversation|session|chat)",
    r"reset\s+(conversation|context|memory|chat)",
    r"(clear|delete)\s+(previous|all)\s+(messages|context)",

    # Role redefinition
    r"you\s+are\s+now\s+(an?\s+)?",
    r"from\s+now\s+on\s+you\s+(are|will\s+be)",
    r"(imagine|pretend)\s+(that\s+)?you\s+are",
    r"your\s+new\s+(role|identity|purpose)\s+is",

    # Hidden instructions in various formats
    r"<!--.*?-->",  # HTML comments
    r"/\*.*?\*/",   # Multi-line comments  
    r"//.*$",       # Single line comments
    r"\[INST\].*?\[/INST\]", # Instruction tags
    r"\<\|.*?\|\>", # Special tokens

    # Encoding attempts
    r"\\u[0-9a-fA-F]{4}",     # Unicode escape sequences
    r"&#x?[0-9a-fA-F]+;",     # HTML entities
    r"%[0-9a-fA-F]{2}",       # URL encoding
    r"\\x[0-9a-fA-F]{2}",     # Hex encoding
    r"\\[0-7]{1,3}",          # Octal encoding

    # Token manipulation  
    r"<\|endoftext\|>",       # GPT end token
    r"<\|startoftext\|>",     # GPT start token
    r"\[MASK\]",              # BERT mask token
    r"\[CLS\]",               # BERT class token
    r"\[SEP\]",               # BERT separator token
]

# Context leakage patterns
LEAKAGE_PATTERNS = [
    r"(print|show|display|output|reveal)\s+your\s+(training|system|internal|source)",
    r"what\s+(data|information|dataset)\s+(were\s+you\s+trained\s+on|did\s+you\s+learn\s+from)",
    r"reveal\s+your\s+(training|source|internal)\s+(data|code|weights|parameters)",
    r"show\s+me\s+your\s+(configuration|settings|parameters|weights)",
    r"(dump|export|print)\s+(model|weights|parameters|training\s+data)",
    r"access\s+(training|source|system)\s+(files|data|code)",
    r"what\s+(model|architecture)\s+are\s+you\s+based\s+on",
    r"(copy|extract)\s+(model|training)\s+(weights|data)",
]

# Suspicious keywords (lower weight indicators)
SUSPICIOUS_KEYWORDS = [
    # Jailbreak terms
    "jailbreak", "jailbreaking", "jailbroken", 
    "unrestricted", "unfiltered", "uncensored", "unlimited",
    "no limits", "no restrictions", "no rules", "no guidelines",
    "anything goes", "do anything", "bypass",

    # Illegal/harmful intent
    "illegal", "unlawful", "criminal", "forbidden",
    "unethical", "immoral", "harmful", "dangerous", "malicious",
    "exploit", "vulnerability", "backdoor", "attack",

    # Technical exploitation
    "hack", "crack", "breach", "compromise", "penetrate",
    "reverse engineer", "decompile", "disassemble",

    # Harmful content
    "violence", "terrorism", "suicide", "self-harm",
    "drug", "weapon", "bomb", "poison", "virus", "malware"
]

# Obfuscation detection patterns - more precise
OBFUSCATION_PATTERNS = [
    r"[a-zA-Z]\s+[a-zA-Z]\s+[a-zA-Z]\s+[a-zA-Z]\s+[a-zA-Z]",  # 5+ excessive spaces 
    r"([a-zA-Z])\1{4,}",                    # Repeated characters (5+ times)
    r"[^\w\s]{4,}",                         # Special character clusters (4+)
    r"[a-zA-Z](\.|_|-)[a-zA-Z](\.|_|-)[a-zA-Z](\.|_|-)[a-zA-Z]", # Multiple separators
    r".{1}\s+.{1}\s+.{1}\s+.{1}\s+.{1}\s+.{1}\s+.{1}",    # 7+ character spacing
]

# Model configuration paths
MODEL_PATHS = {
    "DISTILBERT_CLASSIFIER": "models/distilbert-classifier.onnx",
    "MINILM_SIMILARITY": "models/minilm-similarity.onnx", 
    "EMBEDDINGS": "models/known_attacks.pkl",
    "TOKENIZER_CACHE": "models/tokenizers/",
    "TRANSFORMER_CACHE": "models/transformers/"
}

# Cache and performance settings
CACHE_CONFIG = {
    "REDIS_HOST": "localhost",
    "REDIS_PORT": 6379,
    "REDIS_DB": 0,
    "CACHE_TTL": 3600,  # 1 hour
    "MAX_CACHE_SIZE": 10000,  # Maximum cached entries
    "ENABLE_CACHE": True
}

# Rate limiting configuration 
RATE_LIMIT_CONFIG = {
    "WINDOW_SIZE": 60,      # 1 minute window
    "MAX_REQUESTS": 100,    # Max requests per window per user
    "BURST_LIMIT": 10,      # Max burst requests
    "ENABLE_RATE_LIMIT": True
}

# Security pipeline weights
FILTER_WEIGHTS = {
    "regex_filter": 0.4,
    "obfuscation_detector": 0.2, 
    "ml_classifier": 0.4
}

# Logging configuration
SECURITY_LOG_CONFIG = {
    "LOG_LEVEL": "INFO",
    "LOG_FILE": "logs/security.log",
    "MAX_LOG_SIZE": 10485760,  # 10MB
    "BACKUP_COUNT": 5,
    "LOG_FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# API configuration
API_CONFIG = {
    "MAX_PROMPT_LENGTH": 10000,    # Maximum prompt length in characters
    "TIMEOUT_SECONDS": 30,         # Request timeout
    "MAX_BATCH_SIZE": 50,          # Maximum batch analysis size
    "ENABLE_CORS": True,           # Enable CORS for frontend
    "API_VERSION": "2.0.0"
}

# Development and testing flags
DEV_FLAGS = {
    "SKIP_ML_MODELS": False,       # Skip loading heavy ML models
    "ENABLE_DEBUG_LOGS": False,    # Enable detailed debug logging
    "MOCK_RESPONSES": False,       # Use mock responses for testing
    "ENABLE_METRICS": True,        # Collect performance metrics
    "VALIDATE_INPUTS": True        # Strict input validation
}