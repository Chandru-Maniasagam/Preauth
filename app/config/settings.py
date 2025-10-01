"""
Environment-specific settings for RCM SaaS Application
"""

import os
from typing import Dict, Any


class DevelopmentConfig:
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5173', 'http://127.0.0.1:5173']
    RATELIMIT_DEFAULT = "2000 per hour"


class ProductionConfig:
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
    RATELIMIT_DEFAULT = "1000 per hour"


class TestingConfig:
    """Testing environment configuration"""
    DEBUG = False
    TESTING = True
    LOG_LEVEL = 'DEBUG'
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5173']
    RATELIMIT_DEFAULT = "5000 per hour"


def get_config() -> Dict[str, Any]:
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig.__dict__
    elif env == 'testing':
        return TestingConfig.__dict__
    else:
        return DevelopmentConfig.__dict__


# Environment-specific configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
