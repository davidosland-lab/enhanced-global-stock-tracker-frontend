"""
Adaptive ML Integration - Works in Local AND Remote Environments
==================================================================

This module provides adaptive ML integration that:
1. Detects environment (local finbert_v4.4.4 vs. remote GitHub)
2. Uses best available ML models
3. Provides consistent interface regardless of environment

Features:
- Full FinBERT + LSTM when running locally
- Complete archive ML pipeline when running remotely
- Seamless fallback between environments
- Consistent API for signal generation

Author: Enhanced Global Stock Tracker
Version: 1.0
Date: December 24, 2024
"""

import os
import sys
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MLSignal:
    """Unified ML signal structure"""
    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float  # 0-100
    predicted_price: float
    current_price: float
    position_size_pct: float  # Recommended position size
    stop_loss: float
    take_profit: float
    components: Dict[str, float]  # Individual model scores
    sentiment_score: float
    regime: str  # bullish, bearish, neutral
    ml_source: str  # finbert_local or archive_pipeline


class AdaptiveMLIntegration:
    """
    Adaptive ML integration that works in both environments
    """
    
    def __init__(self):
        self.finbert_available = False
        self.local_models_path = None
        self.ml_source = "archive_pipeline"
        
        # Try to find local finbert_v4.4.4 directory
        self._detect_environment()
        
        # Load appropriate ML modules
        self._load_ml_modules()
        
        logger.info(f"[ML] ML Integration initialized: {self.ml_source}")
    
    def _detect_environment(self):
        """Detect if running in local environment with finbert_v4.4.4"""
        possible_paths = [
            Path("C:/Users/david/AATelS/finbert_v4.4.4"),  # Windows
            Path("C:\\Users\\david\\AATelS\\finbert_v4.4.4"),  # Windows alt
            Path.home() / "AATelS" / "finbert_v4.4.4",  # Home directory
            Path.cwd().parent / "finbert_v4.4.4",  # Parent of current
            Path.cwd().parent.parent / "finbert_v4.4.4",  # Two levels up
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_dir():
                models_path = path / "models"
                if models_path.exists():
                    self.local_models_path = path
                    self.finbert_available = True
                    self.ml_source = "finbert_local"
                    logger.info(f"[OK] Found local FinBERT models at: {path}")
                    sys.path.insert(0, str(path))
                    break
        
        if not self.finbert_available:
            logger.info("[INFO] Using archive ML pipeline (FinBERT models not found locally)")
    
    def _load_ml_modules(self):
        """Load appropriate ML modules based on environment"""
        if self.finbert_available:
            # Load LOCAL finbert_v4.4.4 models
            try:
                # These imports will work when running locally
                from models.backtesting import swing_trader_engine
                from models.sentiment import finbert_analyzer
                
                self.swing_engine = swing_trader_engine.SwingTraderEngine()
                self.sentiment_analyzer = finbert_analyzer.FinBERTAnalyzer()
                logger.info("[OK] Loaded local FinBERT + LSTM models")
            except Exception as e:
                logger.warning(f"[WARN] Failed to load local models: {e}")
                logger.info("[INFO] Falling back to archive ML pipeline")
                self.finbert_available = False
                self._load_archive_models()
        else:
            # Load ARCHIVE ML pipeline
            self._load_archive_models()
    
    def _load_archive_models(self):
        """Load archive ML pipeline models"""
        try:
            # Import from ml_pipeline directory (copied from archive)
            ml_path = Path(__file__).parent
            if str(ml_path) not in sys.path:
                sys.path.insert(0, str(ml_path))
            
            from prediction_engine import PredictionEngine, prediction_engine
            from cba_enhanced_prediction_system import CBAEnhancedPredictionSystem
            
            self.prediction_engine = prediction_engine  # Use global instance
            self.sentiment_system = CBAEnhancedPredictionSystem()
            logger.info("[OK] Loaded archive ML pipeline (LSTM, Transformer, GNN, Ensemble)")
        except Exception as e:
            logger.error(f"[ERROR] Failed to load archive ML models: {e}")
            raise
    
    async def generate_trading_signal(
        self,
        symbol: str,
        current_price: float,
        historical_data: pd.DataFrame,
        config: Optional[Dict] = None
    ) -> MLSignal:
        """
        Generate trading signal using available ML models
        
        Args:
            symbol: Stock symbol
            current_price: Current stock price
            historical_data: Historical price data (OHLCV)
            config: Optional configuration dict
            
        Returns:
            MLSignal with action, confidence, position size, etc.
        """
        if self.finbert_available:
            return await self._generate_finbert_signal(symbol, current_price, historical_data, config)
        else:
            return await self._generate_archive_signal(symbol, current_price, historical_data, config)
    
    async def _generate_finbert_signal(
        self,
        symbol: str,
        current_price: float,
        historical_data: pd.DataFrame,
        config: Optional[Dict]
    ) -> MLSignal:
        """Generate signal using local FinBERT + LSTM pipeline"""
        logger.info(f"🔬 Generating FinBERT signal for {symbol}")
        
        try:
            # Use full swing_trader_engine with FinBERT
            signal = self.swing_engine.generate_signal(
                symbol=symbol,
                data=historical_data,
                config=config
            )
            
            # Use FinBERT sentiment analyzer
            sentiment = await self.sentiment_analyzer.analyze_sentiment(symbol)
            
            # Calculate weighted confidence
            confidence = self._calculate_confidence(signal, sentiment)
            
            # Determine action
            action = "BUY" if confidence >= 52.0 else "HOLD"
            
            # Calculate position size (Phase 3 methodology)
            position_size_pct = self._calculate_position_size(
                confidence=confidence,
                volatility=signal.get('volatility', 0.02),
                regime=signal.get('regime', 'neutral')
            )
            
            # Calculate stop loss and take profit
            stop_loss = current_price * 0.97  # 3% stop loss
            take_profit = current_price * 1.08  # 8% profit target
            
            return MLSignal(
                symbol=symbol,
                action=action,
                confidence=confidence,
                predicted_price=signal.get('predicted_price', current_price * 1.05),
                current_price=current_price,
                position_size_pct=position_size_pct,
                stop_loss=stop_loss,
                take_profit=take_profit,
                components={
                    'momentum': signal.get('momentum_score', 0),
                    'trend': signal.get('trend_score', 0),
                    'volume': signal.get('volume_score', 0),
                    'volatility': signal.get('volatility_score', 0),
                    'finbert_sentiment': sentiment.get('score', 0)
                },
                sentiment_score=sentiment.get('score', 0),
                regime=signal.get('regime', 'neutral'),
                ml_source="finbert_local"
            )
            
        except Exception as e:
            logger.error(f"[ERROR] FinBERT signal generation failed: {e}")
            # Fallback to archive pipeline
            return await self._generate_archive_signal(symbol, current_price, historical_data, config)
    
    async def _generate_archive_signal(
        self,
        symbol: str,
        current_price: float,
        historical_data: pd.DataFrame,
        config: Optional[Dict]
    ) -> MLSignal:
        """Generate signal using archive ML pipeline"""
        logger.info(f"[STATS] Generating archive ML signal for {symbol}")
        
        try:
            # Use archive prediction engine (LSTM, Transformer, Ensemble, GNN, RL)
            prediction = await self.prediction_engine.predict(
                symbol=symbol,
                timeframe="1d",
                include_ensemble=True,
                include_lstm=True,
                include_gnn=True,
                include_rl=False
            )
            
            # Get sentiment analysis
            sentiment_result = await self.sentiment_system.analyze_cba_comprehensive(symbol)
            sentiment_score = sentiment_result.overall_sentiment if hasattr(sentiment_result, 'overall_sentiment') else 0.0
            
            # Calculate technical indicators for component scores
            components = self._calculate_technical_components(historical_data)
            
            # Calculate weighted confidence (Phase 3 methodology)
            confidence = self._calculate_phase3_confidence(components, sentiment_score)
            
            # Determine action
            action = "BUY" if confidence >= 52.0 else "HOLD"
            
            # Get regime from prediction trend
            regime = prediction.get('trend', 'NEUTRAL').lower()
            if regime == 'bullish':
                regime = 'bullish'
            elif regime == 'bearish':
                regime = 'bearish'
            else:
                regime = 'neutral'
            
            # Calculate position size (Phase 3 methodology)
            volatility = components.get('volatility', 0.02)
            position_size_pct = self._calculate_position_size(
                confidence=confidence,
                volatility=volatility,
                regime=regime
            )
            
            # Calculate stop loss and take profit
            stop_loss = current_price * 0.97  # 3% stop loss
            take_profit = current_price * 1.08  # 8% profit target
            
            # Get predicted price
            predicted_price = prediction.get('final_prediction', current_price * 1.05)
            
            return MLSignal(
                symbol=symbol,
                action=action,
                confidence=confidence,
                predicted_price=predicted_price,
                current_price=current_price,
                position_size_pct=position_size_pct,
                stop_loss=stop_loss,
                take_profit=take_profit,
                components=components,
                sentiment_score=sentiment_score,
                regime=regime,
                ml_source="archive_pipeline"
            )
            
        except Exception as e:
            logger.error(f"[ERROR] Archive ML signal generation failed: {e}")
            # Return conservative HOLD signal
            return self._generate_fallback_signal(symbol, current_price)
    
    def _calculate_technical_components(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate technical indicator components (Phase 3 methodology)"""
        try:
            if data.empty or len(data) < 50:
                return {
                    'momentum': 50.0,
                    'trend': 50.0,
                    'volume': 50.0,
                    'volatility': 50.0
                }
            
            close = data['Close'].values
            volume = data['Volume'].values
            
            # Momentum Score (30% weight)
            rsi = self._calculate_rsi(close)
            momentum_score = 100 - rsi if rsi > 70 else (rsi if rsi > 30 else 50)
            
            # Trend Score (35% weight)
            sma_20 = np.mean(close[-20:])
            sma_50 = np.mean(close[-50:]) if len(close) >= 50 else sma_20
            price_vs_sma20 = ((close[-1] - sma_20) / sma_20) * 100
            price_vs_sma50 = ((close[-1] - sma_50) / sma_50) * 100
            trend_score = 50 + (price_vs_sma20 + price_vs_sma50) / 2
            trend_score = max(0, min(100, trend_score))
            
            # Volume Score (20% weight)
            avg_volume = np.mean(volume[-20:])
            current_volume = volume[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            volume_score = min(100, 50 * volume_ratio)
            
            # Volatility Score (15% weight)
            returns = np.diff(close) / close[:-1]
            volatility = np.std(returns[-20:]) if len(returns) >= 20 else 0.02
            volatility_score = max(0, min(100, 100 - (volatility * 1000)))
            
            return {
                'momentum': float(momentum_score),
                'trend': float(trend_score),
                'volume': float(volume_score),
                'volatility': float(volatility_score),
                'volatility_value': float(volatility)
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical components: {e}")
            return {
                'momentum': 50.0,
                'trend': 50.0,
                'volume': 50.0,
                'volatility': 50.0,
                'volatility_value': 0.02
            }
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate RSI indicator"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)
    
    def _calculate_phase3_confidence(self, components: Dict[str, float], sentiment: float) -> float:
        """
        Calculate confidence using Phase 3 methodology:
        - Momentum: 30%
        - Trend: 35%
        - Volume: 20%
        - Volatility: 15%
        """
        weighted_score = (
            components['momentum'] * 0.30 +
            components['trend'] * 0.35 +
            components['volume'] * 0.20 +
            components['volatility'] * 0.15
        )
        
        # Add sentiment boost (normalize sentiment from -1..1 to 0..100)
        sentiment_normalized = (sentiment + 1) * 50  # -1 -> 0, 0 -> 50, 1 -> 100
        sentiment_boost = (sentiment_normalized - 50) * 0.1  # Max ±5 points
        
        confidence = weighted_score + sentiment_boost
        return max(0, min(100, confidence))
    
    def _calculate_confidence(self, signal: Dict, sentiment: Dict) -> float:
        """Calculate overall confidence from signal and sentiment"""
        base_confidence = signal.get('confidence', 50.0)
        sentiment_score = sentiment.get('score', 0.0)
        
        # Sentiment ranges from -1 to 1, convert to 0-100 scale
        sentiment_normalized = (sentiment_score + 1) * 50
        
        # Weight: 70% signal, 30% sentiment
        confidence = base_confidence * 0.7 + sentiment_normalized * 0.3
        return max(0, min(100, confidence))
    
    def _calculate_position_size(
        self,
        confidence: float,
        volatility: float,
        regime: str
    ) -> float:
        """
        Calculate position size using Phase 3 methodology:
        - Base: 25% of capital (0.25)
        - Confidence multiplier: 0.5 - 1.0
        - Volatility multiplier: 0.6 - 1.2
        """
        # Base position size
        base_size = 0.25
        
        # Confidence multiplier (52-100 maps to 0.5-1.0)
        confidence_mult = 0.5 + ((confidence - 52) / 48) * 0.5 if confidence >= 52 else 0
        confidence_mult = max(0.5, min(1.0, confidence_mult))
        
        # Volatility multiplier (lower volatility = larger position)
        vol_mult = 1.2 - (volatility * 30)  # 2% vol -> 1.2x, 5% vol -> 0.6x
        vol_mult = max(0.6, min(1.2, vol_mult))
        
        # Regime boost
        regime_mult = 1.1 if regime == 'bullish' else 1.0
        
        position_size = base_size * confidence_mult * vol_mult * regime_mult
        
        # Cap at 40% of capital
        return min(0.40, position_size)
    
    def _generate_fallback_signal(self, symbol: str, current_price: float) -> MLSignal:
        """Generate conservative fallback signal when ML fails"""
        return MLSignal(
            symbol=symbol,
            action="HOLD",
            confidence=50.0,
            predicted_price=current_price,
            current_price=current_price,
            position_size_pct=0.1,
            stop_loss=current_price * 0.97,
            take_profit=current_price * 1.08,
            components={
                'momentum': 50.0,
                'trend': 50.0,
                'volume': 50.0,
                'volatility': 50.0
            },
            sentiment_score=0.0,
            regime='neutral',
            ml_source='fallback'
        )
    
    def get_ml_info(self) -> Dict[str, Any]:
        """Get information about current ML configuration"""
        return {
            'ml_source': self.ml_source,
            'finbert_available': self.finbert_available,
            'local_models_path': str(self.local_models_path) if self.local_models_path else None,
            'capabilities': {
                'finbert_sentiment': self.finbert_available,
                'lstm_prediction': True,
                'transformer_models': True,
                'ensemble_models': True,
                'gnn_models': not self.finbert_available,  # Archive has GNN
                'rl_trader': not self.finbert_available  # Archive has RL
            }
        }


# Global instance
adaptive_ml = AdaptiveMLIntegration()


# Convenience functions
async def generate_ml_signal(symbol: str, current_price: float, historical_data: pd.DataFrame) -> MLSignal:
    """Convenience function to generate ML signal"""
    return await adaptive_ml.generate_trading_signal(symbol, current_price, historical_data)


def get_ml_status() -> Dict[str, Any]:
    """Get ML integration status"""
    return adaptive_ml.get_ml_info()
