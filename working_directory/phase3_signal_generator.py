"""
Phase 3 Signal Generator - Recommendation Engine + ML Integration
=================================================================

Generates buy/sell recommendations using Phase 3 swing trading methodology.
Used by manual_trading_phase3.py to provide automatic signal generation.

This implements the same signal generation logic as the original Phase 3 backtest.

**NEW**: Integrated ML Pipeline (LSTM, Transformer, Ensemble, GNN, RL)
**NEW**: Adaptive FinBERT sentiment (local when available, archive pipeline otherwise)

Version: 2.0 - ML Enhanced
Date: December 24, 2024
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Tuple
from datetime import datetime
import logging
import asyncio

# Import adaptive ML integration
try:
    from ml_pipeline.adaptive_ml_integration import adaptive_ml, MLSignal, get_ml_status
    ML_AVAILABLE = True
except Exception as e:
    ML_AVAILABLE = False
    adaptive_ml = None
    print(f"⚠️ ML Pipeline not available: {e}")

logger = logging.getLogger(__name__)

if ML_AVAILABLE:
    ml_info = get_ml_status()
    logger.info(f"✅ ML Pipeline: {ml_info['ml_source']}")
else:
    logger.warning("⚠️ ML Pipeline not available - using technical analysis only")


class Phase3SignalGenerator:
    """
    Generates trading signals using Phase 3 methodology:
    - Momentum analysis (RSI, MACD)
    - Trend analysis (MA crossovers)
    - Volume analysis
    - Volatility analysis (ATR)
    - Regime detection
    """
    
    def __init__(self, config: Dict, use_ml: bool = True):
        """
        Initialize signal generator
        
        Args:
            config: Phase 3 configuration dictionary
            use_ml: Whether to use ML models (default: True)
        """
        self.config = config
        self.confidence_threshold = config['swing_trading']['confidence_threshold']
        self.use_ml = use_ml and ML_AVAILABLE
        
        if self.use_ml:
            ml_info = get_ml_status()
            logger.info(f"✅ ML-Enhanced Signal Generator initialized: {ml_info['ml_source']}")
        else:
            logger.info("📊 Technical Analysis Signal Generator initialized (ML disabled)")
    
    def generate_swing_signal(self, symbol: str, price_data: pd.DataFrame) -> Dict:
        """
        Generate swing trading signal for a symbol
        
        Args:
            symbol: Stock symbol
            price_data: Historical price data (OHLCV)
            
        Returns:
            Signal dictionary with prediction, confidence, components
        """
        try:
            if price_data is None or len(price_data) < 50:
                return {'prediction': 0, 'confidence': 0, 'signal_strength': 0}
            
            close = price_data['Close']
            high = price_data['High']
            low = price_data['Low']
            volume = price_data['Volume']
            
            components = {}
            
            # ============================================================
            # 1. MOMENTUM ANALYSIS (RSI + Price Change)
            # ============================================================
            
            # RSI calculation
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_current = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            
            # 10-day momentum
            momentum = ((close.iloc[-1] - close.iloc[-10]) / close.iloc[-10]) * 100 if len(close) >= 10 else 0
            
            # Momentum score
            if 40 < rsi_current < 60 and momentum > 2:
                components['momentum'] = 0.75  # Strong uptrend, not overbought
            elif 30 < rsi_current < 70 and momentum > 0:
                components['momentum'] = 0.60  # Moderate uptrend
            elif rsi_current < 30:
                components['momentum'] = 0.70  # Oversold bounce potential
            elif rsi_current > 70:
                components['momentum'] = 0.40  # Overbought risk
            else:
                components['momentum'] = 0.50  # Neutral
            
            # ============================================================
            # 2. TREND ANALYSIS (Moving Averages)
            # ============================================================
            
            ma_10 = close.rolling(window=10).mean().iloc[-1]
            ma_20 = close.rolling(window=20).mean().iloc[-1]
            ma_50 = close.rolling(window=50).mean().iloc[-1]
            current_price = close.iloc[-1]
            
            # Trend score (Phase 3 original logic)
            if current_price > ma_10 > ma_20 > ma_50:
                components['trend'] = 0.80  # Strong uptrend (all MAs aligned)
            elif current_price > ma_10 > ma_20:
                components['trend'] = 0.65  # Moderate uptrend
            elif current_price > ma_20:
                components['trend'] = 0.55  # Weak uptrend
            else:
                components['trend'] = 0.35  # Downtrend or consolidation
            
            # ============================================================
            # 3. VOLUME ANALYSIS
            # ============================================================
            
            avg_volume = volume.rolling(window=20).mean().iloc[-1]
            current_volume = volume.iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Volume score (Phase 3 original logic)
            if volume_ratio > 2.0:
                components['volume'] = 0.75  # Very strong volume
            elif volume_ratio > 1.5:
                components['volume'] = 0.65  # Strong volume
            elif volume_ratio > 1.0:
                components['volume'] = 0.55  # Above average volume
            else:
                components['volume'] = 0.45  # Below average volume
            
            # ============================================================
            # 4. VOLATILITY ANALYSIS (ATR)
            # ============================================================
            
            # True Range calculation
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=14).mean().iloc[-1]
            atr_pct = (atr / current_price) * 100 if current_price > 0 else 0
            
            # Volatility score (lower is better for swing trading)
            if atr_pct < 2.0:
                components['volatility'] = 0.70  # Low volatility (stable)
            elif atr_pct < 3.0:
                components['volatility'] = 0.60  # Moderate volatility
            elif atr_pct < 4.0:
                components['volatility'] = 0.50  # Higher volatility
            else:
                components['volatility'] = 0.40  # Very high volatility
            
            # ============================================================
            # 5. WEIGHTED COMBINATION (Phase 3 Methodology)
            # ============================================================
            
            weights = {
                'momentum': 0.30,
                'trend': 0.35,
                'volume': 0.20,
                'volatility': 0.15
            }
            
            confidence = sum(components[k] * weights[k] for k in components) * 100
            
            # Prediction based on confidence threshold
            prediction = 1 if confidence >= 50 else 0
            
            # ============================================================
            # 6. REGIME DETECTION
            # ============================================================
            
            regime = self._detect_regime(close, ma_20)
            
            # ============================================================
            # RETURN SIGNAL
            # ============================================================
            
            signal = {
                'symbol': symbol,
                'prediction': prediction,
                'confidence': confidence,
                'signal_strength': confidence,
                'regime': regime,
                'components': components,
                'metrics': {
                    'rsi': rsi_current,
                    'momentum_pct': momentum,
                    'volume_ratio': volume_ratio,
                    'atr_pct': atr_pct,
                    'price': current_price,
                    'ma_10': ma_10,
                    'ma_20': ma_20,
                    'ma_50': ma_50
                },
                'recommendation': 'BUY' if prediction == 1 and confidence >= self.confidence_threshold else 'HOLD'
            }
            
            logger.info(f"{symbol}: Confidence {confidence:.1f}% | {signal['recommendation']} | Regime: {regime}")
            
            return signal
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return {'prediction': 0, 'confidence': 0, 'signal_strength': 0}
    
    async def generate_ml_enhanced_signal(self, symbol: str, price_data: pd.DataFrame) -> Dict:
        """
        Generate ML-enhanced trading signal combining technical analysis + ML models
        
        Args:
            symbol: Stock symbol
            price_data: Historical price data (OHLCV)
            
        Returns:
            Enhanced signal dictionary with ML predictions
        """
        try:
            # Start with Phase 3 technical signal
            tech_signal = self.generate_swing_signal(symbol, price_data)
            
            if not self.use_ml or not ML_AVAILABLE:
                return tech_signal
            
            # Get current price
            current_price = float(price_data['Close'].iloc[-1])
            
            # Generate ML signal
            ml_signal: MLSignal = await adaptive_ml.generate_trading_signal(
                symbol=symbol,
                current_price=current_price,
                historical_data=price_data,
                config=self.config
            )
            
            # Combine technical and ML signals
            # Weight: 50% technical, 50% ML
            combined_confidence = (tech_signal['confidence'] * 0.5 + ml_signal.confidence * 0.5)
            
            # Use ML position sizing if available
            position_size_pct = ml_signal.position_size_pct
            
            # Enhanced signal
            enhanced_signal = {
                'symbol': symbol,
                'prediction': 1 if combined_confidence >= self.confidence_threshold else 0,
                'confidence': combined_confidence,
                'signal_strength': combined_confidence,
                'regime': ml_signal.regime,
                'components': tech_signal['components'],
                'ml_components': ml_signal.components,
                'ml_sentiment': ml_signal.sentiment_score,
                'ml_source': ml_signal.ml_source,
                'metrics': tech_signal['metrics'],
                'ml_predicted_price': ml_signal.predicted_price,
                'ml_stop_loss': ml_signal.stop_loss,
                'ml_take_profit': ml_signal.take_profit,
                'ml_position_size_pct': position_size_pct,
                'recommendation': ml_signal.action,
                'technical_confidence': tech_signal['confidence'],
                'ml_confidence': ml_signal.confidence
            }
            
            logger.info(
                f"{symbol}: ML-Enhanced Signal | "
                f"Tech: {tech_signal['confidence']:.1f}% | "
                f"ML: {ml_signal.confidence:.1f}% | "
                f"Combined: {combined_confidence:.1f}% | "
                f"{enhanced_signal['recommendation']} | "
                f"Source: {ml_signal.ml_source}"
            )
            
            return enhanced_signal
            
        except Exception as e:
            logger.error(f"Error generating ML-enhanced signal for {symbol}: {e}")
            # Fallback to technical signal
            return self.generate_swing_signal(symbol, price_data)
    
    def _detect_regime(self, close: pd.Series, ma_20: float) -> str:
        """Detect market regime"""
        current_price = close.iloc[-1]
        
        if current_price > ma_20 * 1.02:
            return "bullish"
        elif current_price < ma_20 * 0.98:
            return "bearish"
        else:
            return "neutral"
    
    def calculate_position_size(
        self, 
        symbol: str, 
        confidence: float, 
        price: float, 
        available_capital: float,
        volatility_pct: float
    ) -> int:
        """
        Calculate position size using Phase 3 methodology
        
        Args:
            symbol: Stock symbol
            confidence: Signal confidence (0-100)
            price: Current price
            available_capital: Available capital
            volatility_pct: ATR as % of price
            
        Returns:
            Number of shares to buy
        """
        try:
            # Base position size from config
            max_position_pct = self.config['swing_trading']['max_position_size']
            
            # Adjust for confidence (scale 52-100 to 0.5-1.0)
            confidence_adj = 0.5 + ((confidence - 52) / 48) * 0.5 if confidence >= 52 else 0.5
            confidence_adj = max(0.5, min(1.0, confidence_adj))
            
            # Adjust for volatility if enabled
            volatility_adj = 1.0
            if self.config['swing_trading'].get('use_volatility_sizing', False):
                if volatility_pct < 2.0:
                    volatility_adj = 1.2  # Lower volatility = larger position
                elif volatility_pct < 3.0:
                    volatility_adj = 1.0  # Normal
                elif volatility_pct < 4.0:
                    volatility_adj = 0.8  # Higher volatility = smaller position
                else:
                    volatility_adj = 0.6  # Very high volatility = much smaller
            
            # Calculate final position size
            position_pct = max_position_pct * confidence_adj * volatility_adj
            position_value = available_capital * position_pct
            
            # Calculate shares
            shares = int(position_value / price)
            
            logger.info(f"{symbol}: Position size = {shares} shares (${position_value:,.0f})")
            logger.info(f"  Confidence adj: {confidence_adj:.2f} | Volatility adj: {volatility_adj:.2f}")
            
            return max(1, shares)  # At least 1 share
            
        except Exception as e:
            logger.error(f"Error calculating position size for {symbol}: {e}")
            return 0
    
    def evaluate_exit(
        self, 
        symbol: str, 
        entry_price: float, 
        current_price: float,
        entry_date: datetime,
        current_data: pd.DataFrame
    ) -> Tuple[bool, str]:
        """
        Evaluate if position should be exited using Phase 3 methodology
        
        Args:
            symbol: Stock symbol
            entry_price: Entry price
            current_price: Current price
            entry_date: Entry date
            current_data: Current price data
            
        Returns:
            (should_exit, reason)
        """
        try:
            # Calculate P&L
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
            
            # Days held
            days_held = (datetime.now() - entry_date).days
            
            # Get config
            holding_period = self.config['swing_trading']['holding_period_days']
            stop_loss_pct = self.config['swing_trading']['stop_loss_percent']
            profit_target_pct = self.config['swing_trading']['profit_target_pct']
            quick_profit_pct = self.config['swing_trading'].get('quick_profit_target_pct', 12.0)
            
            # Exit conditions (Phase 3 original logic)
            
            # 1. Stop loss hit
            if pnl_pct <= -stop_loss_pct:
                return True, f"Stop loss triggered ({pnl_pct:.2f}%)"
            
            # 2. Quick profit target (early exit)
            if pnl_pct >= quick_profit_pct and days_held >= 1:
                return True, f"Quick profit target hit ({pnl_pct:.2f}%)"
            
            # 3. Standard profit target
            if pnl_pct >= profit_target_pct and days_held >= 2:
                return True, f"Profit target reached ({pnl_pct:.2f}%)"
            
            # 4. Holding period exceeded with profit
            if days_held >= holding_period and pnl_pct > 0:
                return True, f"Holding period complete with profit ({pnl_pct:.2f}%)"
            
            # 5. Holding period exceeded with loss (cut losses)
            if days_held >= holding_period * 1.5 and pnl_pct < -2.0:
                return True, f"Extended hold with loss ({pnl_pct:.2f}%)"
            
            # 6. Generate new signal to check if still bullish
            signal = self.generate_swing_signal(symbol, current_data)
            
            # Exit if signal turns bearish and in loss
            if signal['confidence'] < 45 and pnl_pct < 0:
                return True, f"Signal deteriorated (confidence: {signal['confidence']:.1f}%)"
            
            return False, "Hold"
            
        except Exception as e:
            logger.error(f"Error evaluating exit for {symbol}: {e}")
            return False, "Error"
