"""
US Market Configuration

Market-specific parameters for US stock market screening pipeline.
"""

import pytz
from datetime import time

# Market Identification
MARKET_NAME = "US"
MARKET_FULL_NAME = "United States Stock Market"
MARKET_EXCHANGE = "NYSE/NASDAQ"

# Timezone
TIMEZONE = pytz.timezone('America/New_York')  # Eastern Time (ET)

# Market Hours (Eastern Time)
MARKET_OPEN = time(9, 30)   # 9:30 AM ET
MARKET_CLOSE = time(16, 0)  # 4:00 PM ET
PRE_MARKET_OPEN = time(4, 0)  # 4:00 AM ET
AFTER_HOURS_CLOSE = time(20, 0)  # 8:00 PM ET

# Market Indices
PRIMARY_INDEX = "^GSPC"  # S&P 500
PRIMARY_INDEX_NAME = "S&P 500"

SECONDARY_INDICES = {
    "^DJI": "Dow Jones Industrial Average",
    "^IXIC": "NASDAQ Composite",
    "^RUT": "Russell 2000",
    "^VIX": "CBOE Volatility Index"
}

# Market Sentiment Indicators
SENTIMENT_INDICES = {
    "^VIX": "Fear/Greed Index (VIX)",
    "^GSPC": "S&P 500 Trend",
    "DXY": "US Dollar Index",
    "^TNX": "10-Year Treasury Yield"
}

# Sector Configuration
SECTORS_FILE = "us_sectors.json"
TOTAL_STOCKS = 240
STOCKS_PER_SECTOR = 30
NUM_SECTORS = 8

# Selection Criteria (US Market Specific)
SELECTION_CRITERIA = {
    "min_market_cap": 2_000_000_000,  # $2B minimum (mid/large cap focus)
    "min_avg_volume": 1_000_000,       # 1M shares daily minimum
    "min_price": 5.00,                 # $5 minimum (avoid penny stocks)
    "max_price": 1000.00,              # $1000 maximum
    "beta_min": 0.5,                   # Minimum beta
    "beta_max": 2.5,                   # Maximum beta
    "max_volatility": 0.5              # 50% max annual volatility
}

# Risk-Free Rate (US Treasury)
RISK_FREE_RATE = 0.045  # 4.5% (10-year Treasury yield approximation)

# Currency
CURRENCY = "USD"
CURRENCY_SYMBOL = "$"

# Data Sources
DATA_SOURCE = "yahooquery"  # Primary data source
FALLBACK_SOURCE = None      # No fallback (yahooquery only)

# Batch Processing
BATCH_SIZE = 50              # Stocks per batch
MAX_RETRIES = 3              # Retry attempts per stock
RETRY_DELAY = 2              # Seconds between retries

# Logging
LOG_DIR = "logs/screening/us"
REPORT_DIR = "reports/us"
DATA_DIR = "data/us"

# Report Generation
REPORT_TITLE = "US Market Screening Report"
REPORT_SUBTITLE = "Daily Stock Opportunities - NYSE/NASDAQ"

# Event Risk Guard Settings (US Market)
EVENT_RISK_SETTINGS = {
    "earnings_lookback_days": 90,
    "earnings_blackout_days": 7,     # Days before earnings to skip
    "sec_filings_check": True,
    "fomc_blackout": True,           # Skip trading around Fed meetings
    "major_indices_crash_threshold": -2.5  # % drop to trigger crash risk
}

# Market Regime Settings (US Market)
REGIME_SETTINGS = {
    "index_symbol": "^GSPC",         # S&P 500 for regime detection
    "vix_symbol": "^VIX",            # VIX for volatility regime
    "lookback_days": 252,            # 1 year of trading days
    "regime_states": 3,              # low_vol, medium_vol, high_vol
    "crash_threshold": 0.30          # 30% crash risk threshold
}

# Performance Thresholds
PERFORMANCE_THRESHOLDS = {
    "excellent": 0.15,   # 15%+ expected return
    "good": 0.10,        # 10-15% expected return
    "moderate": 0.05,    # 5-10% expected return
    "poor": 0.0          # Below 5% expected return
}

# Technical Indicators Configuration
TECHNICAL_CONFIG = {
    "rsi_period": 14,
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "ma_short": 20,      # 20-day MA
    "ma_long": 50,       # 50-day MA
    "volume_ma": 20,     # 20-day volume MA
    "bb_period": 20,     # Bollinger Bands period
    "bb_std": 2          # Bollinger Bands standard deviation
}

# LSTM Model Configuration (US Market)
LSTM_CONFIG = {
    "sequence_length": 60,      # 60 trading days
    "prediction_days": 5,       # Predict 5 days ahead
    "hidden_units": 128,
    "dropout": 0.2,
    "epochs": 50,
    "batch_size": 32,
    "learning_rate": 0.001
}

# Email Notification Settings (US Market)
EMAIL_SETTINGS = {
    "subject_prefix": "[US Market]",
    "send_time": "07:00",  # 7 AM ET (before market open)
    "include_charts": True,
    "include_regime_analysis": True,
    "max_opportunities": 20
}

# API Rate Limiting
RATE_LIMIT_CONFIG = {
    "requests_per_minute": 100,
    "requests_per_hour": 2000,
    "backoff_multiplier": 1.5,
    "max_backoff_seconds": 60
}

# Feature Flags
FEATURES = {
    "market_regime_engine": True,
    "event_risk_guard": True,
    "lstm_predictions": True,
    "sentiment_analysis": True,
    "technical_analysis": True,
    "fundamental_analysis": True,
    "csv_export": True,
    "email_notifications": False,  # Disabled by default
    "web_dashboard": True
}

# Version
CONFIG_VERSION = "1.0.0"
LAST_UPDATED = "2025-11-21"

def get_config() -> dict:
    """Return complete configuration as dictionary"""
    return {
        "market": {
            "name": MARKET_NAME,
            "full_name": MARKET_FULL_NAME,
            "exchange": MARKET_EXCHANGE,
            "timezone": str(TIMEZONE),
            "currency": CURRENCY
        },
        "indices": {
            "primary": PRIMARY_INDEX,
            "secondary": SECONDARY_INDICES,
            "sentiment": SENTIMENT_INDICES
        },
        "criteria": SELECTION_CRITERIA,
        "thresholds": PERFORMANCE_THRESHOLDS,
        "technical": TECHNICAL_CONFIG,
        "lstm": LSTM_CONFIG,
        "event_risk": EVENT_RISK_SETTINGS,
        "regime": REGIME_SETTINGS,
        "features": FEATURES,
        "version": CONFIG_VERSION
    }


if __name__ == "__main__":
    # Print configuration summary
    print(f"US Market Configuration v{CONFIG_VERSION}")
    print(f"Last Updated: {LAST_UPDATED}")
    print(f"\nMarket: {MARKET_FULL_NAME}")
    print(f"Primary Index: {PRIMARY_INDEX_NAME} ({PRIMARY_INDEX})")
    print(f"Trading Hours: {MARKET_OPEN} - {MARKET_CLOSE} {TIMEZONE}")
    print(f"Total Stocks: {TOTAL_STOCKS} across {NUM_SECTORS} sectors")
    print(f"Data Source: {DATA_SOURCE}")
    print("\nFeatures Enabled:")
    for feature, enabled in FEATURES.items():
        status = "✓" if enabled else "✗"
        print(f"  {status} {feature}")
