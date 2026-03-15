"""
Market Entry Strategy Module (v1.3.15.163)

Implements sophisticated market entry timing to avoid buying at tops.
Designed to address the problem: "If you buy at the top and then it falls, that's not a good strategy."

Entry Timing Strategies:
1. Pullback Entry: Wait for 1-3% pullback in uptrend before entering
2. RSI Oversold: Enter when RSI < 40 (short-term oversold) in strong uptrend
3. Support Test: Enter when price tests key support (MA20, MA50, prior swing low)
4. Volatility Compression: Enter after volatility squeeze before breakout
5. Volume Confirmation: Enter on breakout with volume > 1.5x average

Scoring System:
- IMMEDIATE BUY (Score 80-100): Strong timing signals, enter now
- GOOD ENTRY (Score 60-79): Decent timing, acceptable to enter
- WAIT FOR DIP (Score 40-59): Signal valid but wait for better entry
- DON'T BUY (Score 0-39): Poor timing, likely buying near top

Author: GenSpark AI Developer
Date: 2026-02-18
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np

# Setup logging
logger = logging.getLogger(__name__)


class MarketEntryStrategy:
    """
    Sophisticated market entry timing strategy.
    
    Prevents buying at tops by analyzing:
    - Price position relative to moving averages
    - RSI levels and divergence
    - Recent pullback depth
    - Volume patterns
    - Volatility compression/expansion
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize Market Entry Strategy
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Entry timing thresholds
        self.pullback_min = self.config.get('pullback_min_pct', 0.5)  # Min 0.5% pullback
        self.pullback_max = self.config.get('pullback_max_pct', 5.0)  # Max 5% pullback
        self.rsi_oversold = self.config.get('rsi_oversold', 40)
        self.rsi_overbought = self.config.get('rsi_overbought', 70)
        self.volume_multiplier = self.config.get('volume_multiplier', 1.5)
        
        logger.info("MarketEntryStrategy initialized")
        logger.info(f"  Pullback Range: {self.pullback_min}% - {self.pullback_max}%")
        logger.info(f"  RSI Oversold: < {self.rsi_oversold}")
        logger.info(f"  RSI Overbought: > {self.rsi_overbought}")
    
    def evaluate_entry_timing(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        signal: Dict
    ) -> Dict:
        """
        Evaluate whether now is a good time to enter a trade.
        
        Args:
            symbol: Stock symbol
            price_data: Historical price data (OHLCV)
            signal: Trading signal with 'action' and 'confidence'
            
        Returns:
            Dictionary with:
                - entry_score (0-100): Overall timing score
                - entry_quality: 'IMMEDIATE_BUY', 'GOOD_ENTRY', 'WAIT_FOR_DIP', 'DONT_BUY'
                - timing_factors: Breakdown of timing signals
                - wait_reason: Why to wait (if score < 60)
                - entry_price_target: Suggested entry price if waiting
        """
        try:
            # Skip if not a BUY signal (FIX v1.3.15.177: Support both signal formats)
            # Standard format: {'prediction': 1} OR Enhanced format: {'action': 'BUY'}
            prediction = signal.get('prediction', 0)
            action = signal.get('action', '')
            is_buy_signal = (prediction == 1) or (action in ['BUY', 'STRONG_BUY'])
            
            if not is_buy_signal:
                return {
                    'entry_score': 0,
                    'entry_quality': 'NOT_BUY_SIGNAL',
                    'timing_factors': {},
                    'wait_reason': 'Signal is not a BUY',
                    'entry_price_target': None
                }
            
            # Calculate technical indicators
            current_price = float(price_data['Close'].iloc[-1])
            ma_20 = float(price_data['Close'].rolling(20).mean().iloc[-1])
            ma_50 = float(price_data['Close'].rolling(50).mean().iloc[-1]) if len(price_data) >= 50 else ma_20
            rsi = self._calculate_rsi(price_data['Close'])
            
            # Calculate entry timing factors
            timing_factors = {}
            entry_score = 0
            
            # Factor 1: Pullback Detection (0-30 points)
            pullback_score, pullback_info = self._score_pullback(
                current_price, price_data, ma_20, ma_50
            )
            entry_score += pullback_score
            timing_factors['pullback'] = pullback_info
            
            # Factor 2: RSI Position (0-25 points)
            rsi_score, rsi_info = self._score_rsi(rsi, current_price, ma_20)
            entry_score += rsi_score
            timing_factors['rsi'] = rsi_info
            
            # Factor 3: Support Test (0-25 points)
            support_score, support_info = self._score_support_test(
                current_price, ma_20, ma_50, price_data
            )
            entry_score += support_score
            timing_factors['support'] = support_info
            
            # Factor 4: Volume Confirmation (0-20 points)
            volume_score, volume_info = self._score_volume(price_data)
            entry_score += volume_score
            timing_factors['volume'] = volume_info
            
            # Determine entry quality (FIX v1.3.15.177: Lower thresholds)
            if entry_score >= 70:
                entry_quality = 'IMMEDIATE_BUY'
                wait_reason = None
            elif entry_score >= 50:
                entry_quality = 'GOOD_ENTRY'
                wait_reason = None
            elif entry_score >= 35:
                entry_quality = 'WAIT_FOR_DIP'
                wait_reason = self._generate_wait_reason(timing_factors)
            else:
                entry_quality = 'DONT_BUY'
                wait_reason = "Likely buying at top - poor entry timing"
            
            # Calculate suggested entry price
            entry_price_target = self._calculate_entry_target(
                current_price, ma_20, ma_50, timing_factors
            ) if entry_quality in ['WAIT_FOR_DIP', 'DONT_BUY'] else None
            
            logger.info(f"[ENTRY] {symbol} - Score: {entry_score:.0f}/100, Quality: {entry_quality}")
            logger.info(f"        Pullback: {pullback_score:.0f}, RSI: {rsi_score:.0f}, "
                       f"Support: {support_score:.0f}, Volume: {volume_score:.0f}")
            
            return {
                'entry_score': entry_score,
                'entry_quality': entry_quality,
                'timing_factors': timing_factors,
                'wait_reason': wait_reason,
                'entry_price_target': entry_price_target,
                'current_price': current_price
            }
            
        except Exception as e:
            logger.error(f"Entry timing evaluation error for {symbol}: {e}")
            return {
                'entry_score': 50,  # Neutral score on error
                'entry_quality': 'UNKNOWN',
                'timing_factors': {},
                'wait_reason': f"Error: {e}",
                'entry_price_target': None
            }
    
    def _score_pullback(
        self,
        current_price: float,
        price_data: pd.DataFrame,
        ma_20: float,
        ma_50: float
    ) -> Tuple[float, Dict]:
        """
        Score pullback quality (0-30 points)
        
        Best Entry: 1-3% pullback from recent high in uptrend
        Poor Entry: At or near recent high (no pullback)
        """
        # Find recent high (20-day high)
        recent_high = float(price_data['Close'].rolling(20).max().iloc[-1])
        
        # Calculate pullback percentage
        pullback_pct = ((recent_high - current_price) / recent_high) * 100
        
        # Distance from MA20
        dist_from_ma20_pct = ((current_price - ma_20) / ma_20) * 100
        
        score = 0
        quality = ""
        
        # FIX v1.3.15.177: Relax pullback requirements for momentum trades
        if pullback_pct < 0.5:
            # At/near recent high - ACCEPTABLE for momentum
            score = 15
            quality = "RECENT_HIGH"
        elif 0.5 <= pullback_pct < 2.0:
            # Small-medium pullback (0.5-2%) - GOOD
            score = 25
            quality = "GOOD_PULLBACK"
        elif 2.0 <= pullback_pct <= 4.0:
            # Ideal pullback (2-4%) - EXCELLENT
            score = 30
            quality = "IDEAL_PULLBACK"
        elif 4.0 < pullback_pct <= 6.0:
            # Larger pullback (4-6%) - GOOD
            score = 25
            quality = "LARGE_PULLBACK"
        else:
            # Very large pullback (>5%) - may signal trend change
            score = 10
            quality = "LARGE_PULLBACK"
        
        return score, {
            'score': score,
            'quality': quality,
            'pullback_pct': pullback_pct,
            'recent_high': recent_high,
            'dist_from_ma20_pct': dist_from_ma20_pct
        }
    
    def _score_rsi(
        self,
        rsi: float,
        current_price: float,
        ma_20: float
    ) -> Tuple[float, Dict]:
        """
        Score RSI positioning (0-25 points)
        
        Best: RSI 35-45 (short-term oversold) in uptrend
        Poor: RSI > 70 (overbought)
        """
        score = 0
        quality = ""
        
        # Check if in uptrend
        in_uptrend = current_price > ma_20
        
        if rsi < 30:
            # Deeply oversold
            score = 20 if in_uptrend else 10
            quality = "DEEPLY_OVERSOLD"
        elif 30 <= rsi < 40:
            # Oversold - EXCELLENT entry in uptrend
            score = 25 if in_uptrend else 15
            quality = "OVERSOLD"
        elif 40 <= rsi < 50:
            # Slightly oversold - GOOD
            score = 20 if in_uptrend else 15
            quality = "SLIGHTLY_OVERSOLD"
        elif 50 <= rsi < 60:
            # Neutral - ACCEPTABLE
            score = 15
            quality = "NEUTRAL"
        # FIX v1.3.15.177: Allow higher RSI for momentum trades
        elif 55 <= rsi < 65:
            # Momentum zone - ACCEPTABLE for trending stocks
            score = 18
            quality = "MOMENTUM_ZONE"
        elif 65 <= rsi < 75:
            # Strong momentum - CAUTION but not blocking
            score = 15
            quality = "STRONG_MOMENTUM"
        else:
            # Extreme overbought - POOR timing
            score = 8
            quality = "OVERBOUGHT"
        
        return score, {
            'score': score,
            'quality': quality,
            'rsi': rsi,
            'in_uptrend': in_uptrend
        }
    
    def _score_support_test(
        self,
        current_price: float,
        ma_20: float,
        ma_50: float,
        price_data: pd.DataFrame
    ) -> Tuple[float, Dict]:
        """
        Score support level test (0-25 points)
        
        Best: Price testing MA20 or MA50 support in uptrend
        Poor: Price far above all support levels
        """
        # Calculate distances
        dist_to_ma20_pct = ((current_price - ma_20) / ma_20) * 100
        dist_to_ma50_pct = ((current_price - ma_50) / ma_50) * 100
        
        score = 0
        quality = ""
        support_level = None
        
        if abs(dist_to_ma20_pct) <= 1.0:
            # At MA20 - EXCELLENT support test
            score = 25
            quality = "AT_MA20"
            support_level = ma_20
        elif abs(dist_to_ma50_pct) <= 2.0:
            # At MA50 - GOOD support test
            score = 20
            quality = "AT_MA50"
            support_level = ma_50
        elif 1.0 < dist_to_ma20_pct <= 3.0:
            # Slightly above MA20 - ACCEPTABLE
            score = 15
            quality = "NEAR_MA20"
            support_level = ma_20
        elif dist_to_ma20_pct > 5.0:
            # Far above support - POOR (extended)
            score = 5
            quality = "EXTENDED"
            support_level = None
        else:
            # Between support levels - NEUTRAL
            score = 10
            quality = "BETWEEN_SUPPORT"
            support_level = None
        
        return score, {
            'score': score,
            'quality': quality,
            'dist_to_ma20_pct': dist_to_ma20_pct,
            'dist_to_ma50_pct': dist_to_ma50_pct,
            'support_level': support_level
        }
    
    def _score_volume(
        self,
        price_data: pd.DataFrame
    ) -> Tuple[float, Dict]:
        """
        Score volume confirmation (0-20 points)
        
        Best: Recent volume spike (>1.5x average) on down day (capitulation)
        Poor: Low volume
        """
        # Calculate volume metrics
        current_volume = float(price_data['Volume'].iloc[-1])
        avg_volume_20 = float(price_data['Volume'].rolling(20).mean().iloc[-1])
        volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1.0
        
        # Check if today was down day
        close_today = float(price_data['Close'].iloc[-1])
        close_yesterday = float(price_data['Close'].iloc[-2]) if len(price_data) > 1 else close_today
        down_day = close_today < close_yesterday
        
        score = 0
        quality = ""
        
        if volume_ratio > 2.0 and down_day:
            # High volume down day - CAPITULATION (best entry)
            score = 20
            quality = "CAPITULATION"
        elif volume_ratio > 1.5:
            # Above average volume - GOOD
            score = 15
            quality = "HIGH_VOLUME"
        elif volume_ratio > 1.0:
            # Normal volume - ACCEPTABLE
            score = 10
            quality = "NORMAL_VOLUME"
        else:
            # Low volume - POOR
            score = 5
            quality = "LOW_VOLUME"
        
        return score, {
            'score': score,
            'quality': quality,
            'volume_ratio': volume_ratio,
            'down_day': down_day
        }
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1])
        except:
            return 50.0  # Neutral RSI on error
    
    def _generate_wait_reason(self, timing_factors: Dict) -> str:
        """Generate human-readable reason to wait"""
        reasons = []
        
        pullback = timing_factors.get('pullback', {})
        if pullback.get('quality') == 'AT_TOP':
            reasons.append(f"Price at recent high (pullback only {pullback.get('pullback_pct', 0):.1f}%)")
        
        rsi = timing_factors.get('rsi', {})
        if rsi.get('quality') in ['OVERBOUGHT', 'OVERBOUGHT_TERRITORY']:
            reasons.append(f"RSI overbought ({rsi.get('rsi', 0):.0f})")
        
        support = timing_factors.get('support', {})
        if support.get('quality') == 'EXTENDED':
            reasons.append(f"Price extended {support.get('dist_to_ma20_pct', 0):.1f}% above MA20")
        
        if not reasons:
            reasons.append("Entry timing is not optimal")
        
        return "; ".join(reasons)
    
    def _calculate_entry_target(
        self,
        current_price: float,
        ma_20: float,
        ma_50: float,
        timing_factors: Dict
    ) -> float:
        """Calculate suggested entry price if waiting"""
        # Default: 2% below current price
        target = current_price * 0.98
        
        # Better target: MA20 level
        pullback = timing_factors.get('pullback', {})
        if pullback.get('quality') == 'AT_TOP':
            # Wait for pullback to MA20
            target = min(target, ma_20)
        
        # If already below MA20, use MA50
        if current_price < ma_20:
            target = ma_50
        
        return round(target, 2)


def create_entry_timing_report(
    symbol: str,
    entry_evaluation: Dict,
    signal: Dict
) -> str:
    """
    Create human-readable entry timing report
    
    Args:
        symbol: Stock symbol
        entry_evaluation: Result from evaluate_entry_timing()
        signal: Original trading signal
        
    Returns:
        Formatted report string
    """
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append(f"ENTRY TIMING ANALYSIS: {symbol}")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # Overall assessment
    entry_score = entry_evaluation['entry_score']
    entry_quality = entry_evaluation['entry_quality']
    current_price = entry_evaluation.get('current_price', 0)
    
    report_lines.append(f"Current Price: USD{current_price:.2f}")
    report_lines.append(f"Entry Score: {entry_score:.0f}/100")
    report_lines.append(f"Entry Quality: {entry_quality}")
    report_lines.append("")
    
    # Recommendation
    if entry_quality == 'IMMEDIATE_BUY':
        report_lines.append("[OK] RECOMMENDATION: BUY NOW - Excellent entry timing")
    elif entry_quality == 'GOOD_ENTRY':
        report_lines.append("[OK] RECOMMENDATION: BUY - Good entry timing")
    elif entry_quality == 'WAIT_FOR_DIP':
        wait_reason = entry_evaluation.get('wait_reason', 'Unknown')
        target = entry_evaluation.get('entry_price_target', 0)
        report_lines.append(f"[WARN] RECOMMENDATION: WAIT FOR BETTER ENTRY")
        report_lines.append(f"   Reason: {wait_reason}")
        report_lines.append(f"   Target Entry: USD{target:.2f} ({((target/current_price - 1) * 100):.1f}%)")
    else:
        report_lines.append("[ALERT] RECOMMENDATION: DON'T BUY - Poor entry timing (likely at top)")
    
    report_lines.append("")
    report_lines.append("-" * 80)
    report_lines.append("TIMING FACTOR BREAKDOWN")
    report_lines.append("-" * 80)
    
    # Timing factors
    timing_factors = entry_evaluation.get('timing_factors', {})
    
    # Pullback
    pullback = timing_factors.get('pullback', {})
    report_lines.append(f"Pullback: {pullback.get('score', 0):.0f}/30 - {pullback.get('quality', 'N/A')}")
    report_lines.append(f"  - Pullback from High: {pullback.get('pullback_pct', 0):.1f}%")
    report_lines.append(f"  - Distance from MA20: {pullback.get('dist_from_ma20_pct', 0):.1f}%")
    report_lines.append("")
    
    # RSI
    rsi = timing_factors.get('rsi', {})
    report_lines.append(f"RSI: {rsi.get('score', 0):.0f}/25 - {rsi.get('quality', 'N/A')}")
    report_lines.append(f"  - RSI Value: {rsi.get('rsi', 0):.1f}")
    report_lines.append(f"  - In Uptrend: {rsi.get('in_uptrend', False)}")
    report_lines.append("")
    
    # Support
    support = timing_factors.get('support', {})
    report_lines.append(f"Support Test: {support.get('score', 0):.0f}/25 - {support.get('quality', 'N/A')}")
    report_lines.append(f"  - Distance to MA20: {support.get('dist_to_ma20_pct', 0):.1f}%")
    report_lines.append(f"  - Distance to MA50: {support.get('dist_to_ma50_pct', 0):.1f}%")
    report_lines.append("")
    
    # Volume
    volume = timing_factors.get('volume', {})
    report_lines.append(f"Volume: {volume.get('score', 0):.0f}/20 - {volume.get('quality', 'N/A')}")
    report_lines.append(f"  - Volume Ratio: {volume.get('volume_ratio', 0):.2f}x avg")
    report_lines.append(f"  - Down Day: {volume.get('down_day', False)}")
    report_lines.append("")
    
    report_lines.append("=" * 80)
    
    return "\n".join(report_lines)
