"""
Configuration file for ML Stock Predictor
Contains API keys and settings
"""

# Alpha Vantage API Configuration
ALPHA_VANTAGE_API_KEY = '68ZFANK047DL0KSR'

# Data Source Configuration
# Options: 'yahoo', 'alpha_vantage'
DEFAULT_DATA_SOURCE = 'yahoo'  # Can switch to 'alpha_vantage' if needed

# Server Configuration
API_PORT = 8000
MCP_PORT = 8001

# Feature Flags
USE_SENTIMENT_ANALYSIS = False  # Set to True to enable FinBERT (requires installation)
USE_ALPHA_VANTAGE_BACKUP = True  # Automatically switch to Alpha Vantage if Yahoo fails

# Rate Limiting (Alpha Vantage Free Tier)
ALPHA_VANTAGE_RATE_LIMIT = 12  # seconds between requests (5 per minute)
ALPHA_VANTAGE_DAILY_LIMIT = 500  # daily request limit

# Cache Settings
CACHE_DURATION = 300  # 5 minutes
CLEAR_CACHE_ON_START = True  # Clear yfinance cache on startup

# ML Model Settings
MIN_DATA_POINTS = 50  # Minimum data points for training
TRAIN_TEST_SPLIT = 0.8  # 80% train, 20% test
DEFAULT_PREDICTION_DAYS = 5

# Technical Indicators
CALCULATE_ALL_INDICATORS = True  # Calculate all 35+ indicators

print(f"✅ Configuration loaded - Alpha Vantage API key configured")