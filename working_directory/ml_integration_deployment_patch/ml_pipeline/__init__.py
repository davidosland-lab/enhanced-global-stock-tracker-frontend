"""
ML Pipeline Integration Package
================================

Adaptive ML integration that works in both environments:
- Local: Uses finbert_v4.4.4 models when available
- Remote: Uses archive ML pipeline (LSTM, Transformer, Ensemble, GNN)

Author: Enhanced Global Stock Tracker
Version: 1.0
Date: December 24, 2024
"""

__version__ = "1.0.0"
__all__ = [
    "AdaptiveMLIntegration",
    "PredictionEngine",
    "CBAEnhancedPredictionSystem",
    "DeepEnsemblePredictor",
    "NeuralNetworkPredictor"
]
