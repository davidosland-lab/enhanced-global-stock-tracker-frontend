"""
ML Swing Signal Generator - v1.3.15.188
Generates swing trading signals using machine learning models.
v188 patch: Confidence threshold lowered from 0.52 to 0.48
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

# v188 confidence threshold (lowered from 0.52 to enable 48-65% trades)
CONFIDENCE_THRESHOLD = 0.48  # v186: lowered from 0.52

logger = logging.getLogger(__name__)


class SwingSignalGenerator:
    """
    Generates swing trading signals with machine learning.
    """
    
    def __init__(
        self,
        confidence_threshold: float = 0.48,  # v188 default
        min_holding_period: int = 3,
        max_holding_period: int = 21,
        target_win_rate: float = 0.75
    ):
        """
        Initialize the swing signal generator.
        
        Args:
            confidence_threshold: Minimum confidence for trade signals (default 0.48)
            min_holding_period: Minimum days to hold position
            max_holding_period: Maximum days to hold position
            target_win_rate: Target win rate for signals (75-85%)
        """
        self.confidence_threshold = confidence_threshold
        self.min_holding_period = min_holding_period
        self.max_holding_period = max_holding_period
        self.target_win_rate = target_win_rate
        
        logger.info(
            f"SwingSignalGenerator initialized: "
            f"confidence_threshold={self.confidence_threshold}, "
            f"target_win_rate={self.target_win_rate*100:.1f}%"
        )
    
    def generate_signal(
        self,
        symbol: str,
        market_data: pd.DataFrame,
        ml_prediction: Optional[Dict] = None
    ) -> Dict:
        """
        Generate a swing trading signal for a symbol.
        
        Args:
            symbol: Stock symbol
            market_data: Historical price data
            ml_prediction: Optional ML model prediction
            
        Returns:
            Signal dictionary with action, confidence, and metadata
        """
        if market_data is None or len(market_data) < 50:
            return {
                'symbol': symbol,
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': 'Insufficient data'
            }
        
        # Calculate technical indicators
        signals = self._calculate_technical_signals(market_data)
        
        # Incorporate ML prediction if available
        if ml_prediction:
            ml_confidence = ml_prediction.get('confidence', 0.5)
            ml_signal = ml_prediction.get('signal', 'HOLD')
            
            # Combine technical and ML signals
            combined_confidence = (signals['confidence'] * 0.4) + (ml_confidence * 0.6)
            
            if ml_signal == 'BUY' and combined_confidence >= self.confidence_threshold:
                action = 'BUY'
            elif ml_signal == 'SELL' and combined_confidence >= self.confidence_threshold:
                action = 'SELL'
            else:
                action = 'HOLD'
                
            confidence = combined_confidence
        else:
            # Use technical signals only
            action = signals['action']
            confidence = signals['confidence']
        
        # Apply confidence threshold
        if confidence < self.confidence_threshold:
            action = 'HOLD'
        
        return {
            'symbol': symbol,
            'action': action,
            'confidence': round(confidence, 4),
            'timestamp': datetime.now().isoformat(),
            'holding_period': self._estimate_holding_period(confidence),
            'technical_score': signals.get('score', 0.0)
        }
    
    def _calculate_technical_signals(self, df: pd.DataFrame) -> Dict:
        """Calculate technical indicator signals."""
        if len(df) < 20:
            return {'action': 'HOLD', 'confidence': 0.0, 'score': 0.0}
        
        # Simple moving averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean() if len(df) >= 50 else df['SMA_20']
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Get latest values
        current = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Signal logic
        score = 0.0
        
        # Trend: SMA crossover
        if current['Close'] > current['SMA_20']:
            score += 0.3
        if current['SMA_20'] > current['SMA_50']:
            score += 0.2
        
        # Momentum: RSI
        rsi = current['RSI']
        if 30 <= rsi <= 70:  # Neutral zone
            score += 0.2
        elif rsi < 30:  # Oversold (bullish)
            score += 0.3
        elif rsi > 70:  # Overbought (bearish)
            score -= 0.3
        
        # Volume
        if 'Volume' in df.columns:
            avg_volume = df['Volume'].rolling(window=20).mean().iloc[-1]
            if current['Volume'] > avg_volume * 1.5:
                score += 0.2
        
        # Determine action
        if score >= 0.5:
            action = 'BUY'
        elif score <= -0.3:
            action = 'SELL'
        else:
            action = 'HOLD'
        
        # Convert score to confidence
        confidence = min(abs(score), 1.0)
        
        return {
            'action': action,
            'confidence': confidence,
            'score': score
        }
    
    def _estimate_holding_period(self, confidence: float) -> int:
        """Estimate optimal holding period based on confidence."""
        if confidence >= 0.85:
            return self.max_holding_period
        elif confidence >= 0.70:
            return int(self.max_holding_period * 0.7)
        elif confidence >= 0.55:
            return int(self.max_holding_period * 0.5)
        else:
            return self.min_holding_period


class EnhancedPipelineSignalAdapter:
    """
    Adapter to convert pipeline signals to trading format.
    v188 compatible with 48% confidence threshold.
    """
    
    def __init__(self, target_win_rate: float = 0.75):
        self.target_win_rate = target_win_rate
        self.signal_generator = SwingSignalGenerator(
            confidence_threshold=0.48,  # v188
            target_win_rate=target_win_rate
        )
        logger.info(
            f"EnhancedPipelineSignalAdapter V3 initialized "
            f"(target win-rate: {target_win_rate*100:.0f}%-85%)"
        )
    
    def convert_pipeline_signal(self, pipeline_data: Dict) -> Dict:
        """Convert pipeline output to trading signal."""
        symbol = pipeline_data.get('symbol', 'UNKNOWN')
        confidence = pipeline_data.get('confidence', 0.0)
        signal = pipeline_data.get('signal', 'HOLD')
        
        return {
            'symbol': symbol,
            'action': signal,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'source': 'pipeline'
        }


if __name__ == '__main__':
    # Test the signal generator
    print("SwingSignalGenerator v1.3.15.188")
    print(f"Confidence threshold: {CONFIDENCE_THRESHOLD}")
    
    generator = SwingSignalGenerator()
    print(f"Initialized with threshold: {generator.confidence_threshold}")
    print("v188 patch applied: 48% confidence threshold active")
