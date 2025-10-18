#!/usr/bin/env python3
"""
ML System Configuration File
Edit this file to customize system behavior
"""

# ========== FEATURE FLAGS ==========

# Sentiment Analysis - DISABLED by default to ensure Yahoo Finance stability
# When enabled, adds market sentiment as the 36th feature
# WARNING: Original sentiment makes 20+ API calls and may cause issues
USE_SENTIMENT_ANALYSIS = False

# ========== SERVER SETTINGS ==========

# Server port
PORT = 8000

# Server host
HOST = "127.0.0.1"

# ========== DATA SETTINGS ==========

# Cache duration in seconds (5 minutes default)
CACHE_DURATION = 300

# Default data period for training
DEFAULT_PERIOD = "2y"

# Default data interval
DEFAULT_INTERVAL = "1d"

# ========== MODEL SETTINGS ==========

# Minimum samples needed for training
MIN_TRAINING_SAMPLES = 100

# Test data split ratio
TEST_SPLIT = 0.2

# Random seed for reproducibility
RANDOM_SEED = 42

# ========== FEATURE ENGINEERING ==========

# Number of periods for moving averages
SMA_SHORT = 20
SMA_LONG = 50
EMA_SHORT = 12
EMA_LONG = 26

# RSI period
RSI_PERIOD = 14

# Bollinger Bands period
BB_PERIOD = 20

# ATR period  
ATR_PERIOD = 14

# ========== LOGGING ==========

# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = "INFO"

# Log to file
LOG_TO_FILE = False
LOG_FILE = "ml_system.log"