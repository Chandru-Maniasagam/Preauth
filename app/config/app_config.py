"""
Application configuration for RCM SaaS Application
"""

import os
from typing import Dict, Any


class AppConfig:
    """Application configuration settings"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = os.environ.get('FLASK_TESTING', 'False').lower() == 'true'
    
    # API Configuration
    API_VERSION = "v1"
    API_PREFIX = f"/api/{API_VERSION}"
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Pagination Configuration
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
    
    # Security Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = "1000 per hour"
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')
    
    # Business Configuration
    PREAUTH_EXPIRY_DAYS = 30
    MAX_PATIENT_RECORDS_PER_HOSPITAL = 10000
    MAX_PREAUTH_REQUESTS_PER_DAY = 1000
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get application configuration dictionary"""
        return {
            'SECRET_KEY': cls.SECRET_KEY,
            'DEBUG': cls.DEBUG,
            'TESTING': cls.TESTING,
            'API_VERSION': cls.API_VERSION,
            'API_PREFIX': cls.API_PREFIX,
            'CORS_ORIGINS': cls.CORS_ORIGINS,
            'DEFAULT_PAGE_SIZE': cls.DEFAULT_PAGE_SIZE,
            'MAX_PAGE_SIZE': cls.MAX_PAGE_SIZE,
            'MAX_CONTENT_LENGTH': cls.MAX_CONTENT_LENGTH,
            'ALLOWED_EXTENSIONS': cls.ALLOWED_EXTENSIONS,
            'JWT_SECRET_KEY': cls.JWT_SECRET_KEY,
            'JWT_ACCESS_TOKEN_EXPIRES': cls.JWT_ACCESS_TOKEN_EXPIRES,
            'JWT_REFRESH_TOKEN_EXPIRES': cls.JWT_REFRESH_TOKEN_EXPIRES,
            'RATELIMIT_STORAGE_URL': cls.RATELIMIT_STORAGE_URL,
            'RATELIMIT_DEFAULT': cls.RATELIMIT_DEFAULT,
            'LOG_LEVEL': cls.LOG_LEVEL,
            'LOG_FILE': cls.LOG_FILE,
            'PREAUTH_EXPIRY_DAYS': cls.PREAUTH_EXPIRY_DAYS,
            'MAX_PATIENT_RECORDS_PER_HOSPITAL': cls.MAX_PATIENT_RECORDS_PER_HOSPITAL,
            'MAX_PREAUTH_REQUESTS_PER_DAY': cls.MAX_PREAUTH_REQUESTS_PER_DAY
        }
