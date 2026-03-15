"""
ML Pipeline Integration Package
================================

Adaptive ML integration that works in both environments:
- Local: Uses finbert_v4.4.4 models when available
- Remote: Uses archive ML pipeline (LSTM, Transformer, Ensemble, GNN)

NEW: Integrated Swing Trading & Monitoring
- SwingSignalGenerator: Real-time signal generation (70-75% win rate)
- Market Monitoring: Sentiment tracking, intraday scanning
- Cross-timeframe coordination: Enhance swing signals with intraday context

Author: Enhanced Global Stock Tracker
Version: 2.0
Date: December 25, 2024
"""

__version__ = "2.0.0"

# Import main classes
from .adaptive_ml_integration import AdaptiveMLIntegration
from .prediction_engine import PredictionEngine
from .cba_enhanced_prediction_system import CBAEnhancedPredictionSystem

# Try to import torch-dependent models
try:
    from .deep_learning_ensemble import DeepEnsemblePredictor
    from .neural_network_models import NeuralNetworkPredictor
    DEEP_LEARNING_AVAILABLE = True
except ImportError:
    DeepEnsemblePredictor = None
    NeuralNetworkPredictor = None
    DEEP_LEARNING_AVAILABLE = False

# NEW: Swing trading & monitoring components
from .swing_signal_generator import SwingSignalGenerator, generate_swing_signal
from .market_monitoring import (
    MarketSentimentMonitor,
    IntradayScanner,
    CrossTimeframeCoordinator,
    create_monitoring_system,
    MarketSentiment,
    SentimentReading,
    IntradayAlert
)

__all__ = [
    # Prediction models
    "AdaptiveMLIntegration",
    "PredictionEngine",
    "CBAEnhancedPredictionSystem",
    "DeepEnsemblePredictor",
    "NeuralNetworkPredictor",
    # Swing trading
    "SwingSignalGenerator",
    "generate_swing_signal",
    # Monitoring
    "MarketSentimentMonitor",
    "IntradayScanner",
    "CrossTimeframeCoordinator",
    "create_monitoring_system",
    "MarketSentiment",
    "SentimentReading",
    "IntradayAlert"
]
