"""
============================================================
CONFIGURATION FILE
============================================================

This file contains all settings for our application.
Think of it like a control panel with different knobs and switches.

We have 3 environments:
1. Development - for coding on your computer
2. Testing - for running automated tests
3. Production - for the real deployed application
"""

import os
from datetime import timedelta

# Get the base directory (where this file is located)
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Base configuration class
    
    This contains settings that are the same across all environments.
    Other config classes inherit from this one.
    """
    
    # ========================================
    # SECRET KEYS
    # ========================================
    # SECRET_KEY: Used for session encryption and CSRF protection
    # NEVER share this key or commit it to Git!
    # Generate new one with: python -c 'import secrets; print(secrets.token_hex(32))'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # JWT_SECRET_KEY: Used specifically for JWT token encryption
    # Should be different from SECRET_KEY for extra security
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key-change-in-production')
    
    # ========================================
    # DATABASE CONFIGURATION
    # ========================================
    # SQLALCHEMY_DATABASE_URI: Connection string to database
    # Format: postgresql://username:password@host:port/database_name
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://taskapp_user:devpassword123@localhost:5432/taskmanagement_db'
    )
    
    # SQLALCHEMY_TRACK_MODIFICATIONS: Tracks object changes
    # We disable this because it uses extra memory
    # SQLAlchemy's own event system is better
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQLALCHEMY_ECHO: Print all SQL queries to console
    # Useful for debugging, but disable in production
    SQLALCHEMY_ECHO = False
    
    # ========================================
    # JWT CONFIGURATION
    # ========================================
    # JWT_ACCESS_TOKEN_EXPIRES: How long login tokens last
    # After this time, user must login again
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # 24 hours
    
    # JWT_REFRESH_TOKEN_EXPIRES: How long refresh tokens last
    # Refresh tokens are used to get new access tokens
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # 30 days
    
    # JWT_TOKEN_LOCATION: Where to look for JWT tokens
    # 'headers' means we'll send tokens in HTTP headers
    JWT_TOKEN_LOCATION = ['headers']
    
    # JWT_HEADER_NAME: Which HTTP header contains the token
    # Standard is 'Authorization'
    JWT_HEADER_NAME = 'Authorization'
    
    # JWT_HEADER_TYPE: Token prefix in header
    # Full header looks like: "Authorization: Bearer <token>"
    JWT_HEADER_TYPE = 'Bearer'
    
    # ========================================
    # CORS CONFIGURATION
    # ========================================
    # CORS_ORIGINS: Which domains can access our API
    # In development, we allow localhost
    # In production, you'd specify your actual frontend domain
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # ========================================
    # FILE UPLOAD CONFIGURATION
    # ========================================
    # MAX_CONTENT_LENGTH: Maximum file size for uploads
    # 10 MB = 10 * 1024 * 1024 bytes
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_FILE_SIZE_MB', 10)) * 1024 * 1024
    
    # ALLOWED_EXTENSIONS: Which file types can be uploaded
    ALLOWED_EXTENSIONS = os.getenv(
        'ALLOWED_EXTENSIONS',
        'pdf,doc,docx,xls,xlsx,jpg,jpeg,png,gif'
    ).split(',')
    
    # UPLOAD_FOLDER: Where to temporarily store uploaded files
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    
    # ========================================
    # AWS S3 CONFIGURATION (Phase 4)
    # ========================================
    # Amazon S3 settings for cloud file storage
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
    
    # ========================================
    # PAGINATION
    # ========================================
    # ITEMS_PER_PAGE: Default number of items to return in list endpoints
    # Example: GET /api/tasks?page=1&per_page=20
    ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', 20))
    
    # ========================================
    # APPLICATION INFO
    # ========================================
    APP_NAME = os.getenv('APP_NAME', 'Task Management App')
    API_VERSION = os.getenv('API_VERSION', 'v1')
    
    # ========================================
    # REDIS CONFIGURATION (Optional - for caching)
    # ========================================
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # ========================================
    # EMAIL CONFIGURATION (Optional - Phase 5+)
    # ========================================
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')


class DevelopmentConfig(Config):
    """
    Development environment configuration
    
    Used when coding on your local machine.
    Has helpful debugging features enabled.
    """
    DEBUG = True
    TESTING = False
    
    # Show SQL queries in console (helpful for learning!)
    SQLALCHEMY_ECHO = True
    
    # More detailed error messages
    PROPAGATE_EXCEPTIONS = True


class TestingConfig(Config):
    """
    Testing environment configuration
    
    Used when running automated tests.
    Uses a separate test database.
    """
    DEBUG = True
    TESTING = True
    
    # Use in-memory SQLite database for faster tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF protection in tests
    WTF_CSRF_ENABLED = False
    
    # Use shorter token expiry for tests
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


class ProductionConfig(Config):
    """
    Production environment configuration
    
    Used when application is deployed to real server.
    All debugging features are disabled for security and performance.
    """
    DEBUG = False
    TESTING = False
    
    # Don't show SQL queries in production (security risk)
    SQLALCHEMY_ECHO = False
    
    # Force HTTPS in production (commented out for now)
    # SESSION_COOKIE_SECURE = True
    # REMEMBER_COOKIE_SECURE = True
    
    # Stricter security settings
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    @staticmethod
    def init_app(app):
        """
        Validate production configuration
        Called when app is initialized with this config
        """
        Config.init_app(app)
        
        # Must have real secret keys in production
        if not os.getenv('SECRET_KEY'):
            raise ValueError('SECRET_KEY environment variable must be set in production')
        
        if not os.getenv('JWT_SECRET_KEY'):
            raise ValueError('JWT_SECRET_KEY environment variable must be set in production')


# ============================================================
# CONFIGURATION DICTIONARY
# ============================================================
# This makes it easy to switch between environments
# Usage: config_by_name['development'] or config_by_name['production']

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


# ============================================================
# HELPER FUNCTION
# ============================================================
def get_config(config_name=None):
    """
    Get configuration object by name
    
    Args:
        config_name (str): Name of configuration ('development', 'testing', 'production')
        
    Returns:
        Config: Configuration class
        
    Example:
        config = get_config('development')
        print(config.DEBUG)  # True
    """
    if config_name is None:
        # Default to development if FLASK_ENV not set
        config_name = os.getenv('FLASK_ENV', 'development')
    
    return config_by_name.get(config_name, DevelopmentConfig)
