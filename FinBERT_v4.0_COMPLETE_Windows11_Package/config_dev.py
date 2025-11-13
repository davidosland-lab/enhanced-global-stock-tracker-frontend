"""
FinBERT v4.0 Development Configuration
"""

import os
from datetime import timedelta

class DevelopmentConfig:
    """Development environment configuration"""
    
    # Flask settings
    DEBUG = True
    TESTING = False
    SECRET_KEY = 'dev-secret-key-change-in-production'
    
    # Server settings - Windows 11 Localhost Configuration
    HOST = '127.0.0.1'  # Localhost for Windows 11 deployment
    PORT = 5001  # Default port (can be changed if needed)
    THREADED = True
    
    # CORS settings
    CORS_ORIGINS = ['http://localhost:*', 'http://127.0.0.1:*']
    
    # Database settings (for v4.0)
    DATABASE_URI = 'sqlite:///finbert_dev.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cache settings
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # ML Model settings
    MODEL_CACHE_DIR = 'models/cache'
    USE_GPU = False  # Set to True if CUDA available
    
    # API Rate limits
    RATE_LIMIT = '100/hour'
    
    # WebSocket settings
    SOCKETIO_ASYNC_MODE = 'eventlet'
    SOCKETIO_CORS_ALLOWED_ORIGINS = '*'
    
    # External API Keys (add your own)
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', '')
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
    
    # Feature flags for v4.0
    FEATURES = {
        'USE_REAL_FINBERT': False,  # Toggle when model is ready
        'USE_LSTM': True,  # ✅ ENABLED - LSTM predictions active
        'USE_XGBOOST': False,  # Toggle when implemented
        'ENABLE_WEBSOCKET': False,  # Toggle when ready
        'ENABLE_DATABASE': False,  # Toggle when schema ready
        'ENABLE_SOCIAL_SENTIMENT': False,  # Toggle when APIs configured
        'ENABLE_DARK_MODE': False,  # Toggle when UI ready
        'ENABLE_PORTFOLIO': False,  # Toggle when feature complete
    }
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = 'logs/finbert_dev.log'
    
    # Performance
    ENABLE_PROFILING = True
    PROFILE_DIR = 'profiles'
    
    # Testing
    TEST_MODE = False
    TEST_DATABASE_URI = 'sqlite:///test.db'

class ProductionConfig:
    """Production environment configuration"""
    
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.urandom(32)
    
    # Add production settings here
    
    FEATURES = {
        'USE_REAL_FINBERT': False,
        'USE_LSTM': True,  # ✅ ENABLED - LSTM predictions active
        'USE_XGBOOST': False,
        'ENABLE_WEBSOCKET': False,
        'ENABLE_DATABASE': False,
        'ENABLE_SOCIAL_SENTIMENT': False,
        'ENABLE_DARK_MODE': False,
        'ENABLE_PORTFOLIO': False,
    }

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])