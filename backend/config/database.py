import os
from urllib.parse import urlparse

class DatabaseConfig:
    """Database configuration settings."""
    
    # PostgreSQL connection
    DATABASE_URL = os.environ.get('DATABASE_URL', 
                                 'postgresql://admin:password@localhost:5432/safex_db')
    
    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 120,
        'pool_pre_ping': True,
        'connect_args': {'connect_timeout': 10}
    }
    
    @staticmethod
    def validate_database_url(url: str) -> bool:
        """Validate database URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc, result.path])
        except:
            return False