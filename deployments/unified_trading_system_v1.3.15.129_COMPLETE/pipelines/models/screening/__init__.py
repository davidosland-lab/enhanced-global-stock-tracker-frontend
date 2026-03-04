"""
Overnight Screening Pipeline Modules

Core Components:
- overnight_pipeline: Australian market overnight screening
- us_overnight_pipeline: US market overnight screening  
- uk_overnight_pipeline: UK market overnight screening
- batch_predictor: FinBERT + LSTM batch predictions
- opportunity_scorer: Multi-factor opportunity scoring
- report_generator: Morning report generation
- spi_monitor: Australian market sentiment (SPI futures)
- stock_scanner: Multi-market stock scanner
- finbert_bridge: FinBERT v4.4.4 sentiment analysis
- lstm_trainer: LSTM model training
- event_risk_guard: Event risk assessment (earnings, Basel III, etc.)
- csv_exporter: CSV report exporter
- macro_news_monitor: Macro news sentiment analysis
"""

__version__ = '1.3.15.87'
