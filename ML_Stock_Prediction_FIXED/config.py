"""
ML Stock Prediction Configuration
REAL DATA ONLY - NO FALLBACK
"""

# Server Configuration
PORT = 8000  # Change if port in use

# Data Configuration
USE_SENTIMENT = False  # Sentiment analysis disabled for stability
CACHE_ENABLED = True   # SQLite caching for faster data retrieval

# Model Configuration  
ENSEMBLE_TYPE = "voting"  # or "stacking"
MODEL_WEIGHTS = [0.30, 0.25, 0.25, 0.15, 0.05]  # Weights for 5 models

# Training Configuration
DEFAULT_TRAINING_DAYS = 180  # 6 months of data
MIN_TRAINING_SAMPLES = 60    # Minimum samples required

# Backtesting Configuration
COMMISSION_RATE = 0.001  # 0.1% commission
SLIPPAGE_RATE = 0.0005  # 0.05% slippage

# API Configuration
REQUEST_TIMEOUT = 30  # seconds
TRAINING_TIMEOUT = 120  # seconds