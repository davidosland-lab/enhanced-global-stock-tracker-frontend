"""
Configuration file for ML Stock Prediction System
Adjust these settings as needed for your environment
"""

# Server Configuration
PORT = 8000  # Change if port 8000 is already in use

# Feature Configuration  
USE_SENTIMENT = False  # Set to True only if you have 4GB+ RAM and Python 3.10/3.11

# Data Configuration
DEFAULT_TRAINING_DAYS = 180  # Number of days of historical data for training
MIN_TRAINING_DAYS = 90  # Minimum days required for reliable predictions

# Model Configuration
ENSEMBLE_TYPE = "voting"  # Options: "voting" or "stacking"
MODEL_WEIGHTS = [0.30, 0.25, 0.15, 0.25, 0.05]  # Weights for ensemble models

# Cache Configuration
ENABLE_CACHE = True  # SQLite caching for 50x faster data retrieval
CACHE_DB = "market_data.db"  # Database file name

# Backtesting Configuration
COMMISSION_RATE = 0.001  # 0.1% commission
SLIPPAGE_RATE = 0.0005  # 0.05% slippage

# API Configuration
REQUEST_TIMEOUT = 10  # Seconds before API requests timeout
TRAINING_TIMEOUT = 60  # Seconds before training requests timeout