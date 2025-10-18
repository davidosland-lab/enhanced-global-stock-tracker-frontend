#!/usr/bin/env python3
"""
ML System Configuration
Central configuration for enabling/disabling features
"""

# ==================== FEATURE FLAGS ====================

# Sentiment Analysis
# DISABLED: The sentiment analyzer makes 20+ Yahoo Finance API calls causing rate limiting
# Set to True only after implementing the fixed batch version
USE_SENTIMENT_ANALYSIS = False

# Yahoo Finance Settings
YAHOO_BATCH_MODE = True  # Use batch downloading when possible
YAHOO_CACHE_DURATION = 300  # Cache data for 5 minutes
YAHOO_MAX_RETRIES = 3
YAHOO_RETRY_DELAY = 2  # Seconds between retries

# ML Model Settings
USE_XGBOOST = True  # Use XGBoost if available
USE_TALIB = True    # Use TA-Lib if available
USE_ENSEMBLE = True # Use ensemble models

# Server Settings
PORT = 8000
HOST = "127.0.0.1"

# Data Settings
DEFAULT_PERIOD = "2y"
DEFAULT_INTERVAL = "1d"
MIN_TRAINING_SAMPLES = 252  # Minimum 1 year of trading days

# Feature Engineering
FEATURE_COUNT_WITHOUT_SENTIMENT = 35
FEATURE_COUNT_WITH_SENTIMENT = 36

# Model Caching
CACHE_MODELS = True
MODEL_CACHE_DIR = "./models"

# Logging
LOG_LEVEL = "INFO"
LOG_TO_FILE = False
LOG_FILE = "ml_system.log"