"""
Breakout Detector for Phase 3 Auto-Rescan
==========================================

This module detects real-time breakouts and significant market events
for intraday trading opportunities.

Breakout Types:
- Price Breakouts: Support/resistance, day range
- Volume Breakouts: Unusual volume spikes
- Momentum Breakouts: Strong directional moves

Author: FinBERT Enhanced Stock Screener
Version: 1.0.0 (Phase 3 Auto-Rescan)
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class BreakoutType(Enum):
    """Types of breakouts detected"""
    PRICE_BREAKOUT_UP = "price_breakout_up"
    PRICE_BREAKOUT_DOWN = "price_breakout_down"
    VOLUME_SPIKE = "volume_spike"
    MOMENTUM_SURGE = "momentum_surge"
    MOMENTUM_REVERSAL = "momentum_reversal"
    DAY_HIGH_BREAK = "day_high_break"
    DAY_LOW_BREAK = "day_low_break"


@dataclass
class BreakoutSignal:
    """Represents a detected breakout signal"""
    symbol: str
    breakout_type: BreakoutType
    strength: float  # 0-100 score
    timestamp: datetime
    price: float
    volume: int
    details: Dict  # Additional context
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['breakout_type'] = self.breakout_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


class BreakoutDetector:
    """
    Detects breakouts and significant market events for day trading.
    
    Uses multiple detection strategies:
    - Price action (support/resistance, day range)
    - Volume analysis (unusual activity)
    - Momentum (directional strength)
    """
    
    def __init__(
        self,
        price_breakout_threshold: float = 2.0,  # % move
        volume_spike_multiplier: float = 2.0,  # Multiple of avg
        momentum_threshold: float = 3.0,  # % change in period
        min_signal_strength: float = 60.0  # Min strength to report
    ):
        """
        Initialize breakout detector.
        
        Args:
            price_breakout_threshold: Min % price move for breakout
            volume_spike_multiplier: Min volume multiple for spike
            momentum_threshold: Min % momentum for surge detection
            min_signal_strength: Minimum signal strength to report
        """
        self.price_breakout_threshold = price_breakout_threshold
        self.volume_spike_multiplier = volume_spike_multiplier
        self.momentum_threshold = momentum_threshold
        self.min_signal_strength = min_signal_strength
        
        self.detected_signals: List[BreakoutSignal] = []
        
        logger.info(f"BreakoutDetector initialized:")
        logger.info(f"  Price threshold: {price_breakout_threshold}%")
        logger.info(f"  Volume multiplier: {volume_spike_multiplier}x")
        logger.info(f"  Momentum threshold: {momentum_threshold}%")
        logger.info(f"  Min signal strength: {min_signal_strength}")
    
    def detect_price_breakout(
        self,
        symbol: str,
        current_price: float,
        day_open: float,
        day_high: float,
        day_low: float,
        prev_close: float
    ) -> Optional[BreakoutSignal]:
        """
        Detect price breakouts (support/resistance, day range).
        
        Args:
            symbol: Stock symbol
            current_price: Current price
            day_open: Today's open price
            day_high: Today's high price
            day_low: Today's low price
            prev_close: Previous day's close
            
        Returns:
            BreakoutSignal if breakout detected, None otherwise
        """
        # Calculate price changes
        change_from_open_pct = ((current_price - day_open) / day_open * 100)
        change_from_prev_pct = ((current_price - prev_close) / prev_close * 100)
        
        # Check day high/low breaks
        if current_price >= day_high * 0.999:  # At or near day high
            if abs(change_from_open_pct) >= self.price_breakout_threshold:
                strength = min(abs(change_from_open_pct) * 20, 100)
                
                return BreakoutSignal(
                    symbol=symbol,
                    breakout_type=BreakoutType.DAY_HIGH_BREAK,
                    strength=strength,
                    timestamp=datetime.now(),
                    price=current_price,
                    volume=0,  # Volume filled later
                    details={
                        'day_high': day_high,
                        'change_from_open': change_from_open_pct,
                        'change_from_prev': change_from_prev_pct
                    }
                )
        
        elif current_price <= day_low * 1.001:  # At or near day low
            if abs(change_from_open_pct) >= self.price_breakout_threshold:
                strength = min(abs(change_from_open_pct) * 20, 100)
                
                return BreakoutSignal(
                    symbol=symbol,
                    breakout_type=BreakoutType.DAY_LOW_BREAK,
                    strength=strength,
                    timestamp=datetime.now(),
                    price=current_price,
                    volume=0,
                    details={
                        'day_low': day_low,
                        'change_from_open': change_from_open_pct,
                        'change_from_prev': change_from_prev_pct
                    }
                )
        
        # Check general price breakout
        if abs(change_from_prev_pct) >= self.price_breakout_threshold:
            breakout_type = (
                BreakoutType.PRICE_BREAKOUT_UP if change_from_prev_pct > 0
                else BreakoutType.PRICE_BREAKOUT_DOWN
            )
            strength = min(abs(change_from_prev_pct) * 15, 100)
            
            return BreakoutSignal(
                symbol=symbol,
                breakout_type=breakout_type,
                strength=strength,
                timestamp=datetime.now(),
                price=current_price,
                volume=0,
                details={
                    'change_from_prev': change_from_prev_pct,
                    'prev_close': prev_close
                }
            )
        
        return None
    
    def detect_volume_spike(
        self,
        symbol: str,
        current_volume: int,
        avg_volume: int,
        current_price: float
    ) -> Optional[BreakoutSignal]:
        """
        Detect unusual volume spikes.
        
        Args:
            symbol: Stock symbol
            current_volume: Current volume
            avg_volume: Average daily volume
            current_price: Current price
            
        Returns:
            BreakoutSignal if volume spike detected, None otherwise
        """
        if avg_volume == 0:
            return None
        
        volume_multiple = current_volume / avg_volume
        
        if volume_multiple >= self.volume_spike_multiplier:
            # Calculate strength based on volume multiple
            strength = min((volume_multiple - 1) * 30, 100)
            
            return BreakoutSignal(
                symbol=symbol,
                breakout_type=BreakoutType.VOLUME_SPIKE,
                strength=strength,
                timestamp=datetime.now(),
                price=current_price,
                volume=current_volume,
                details={
                    'volume_multiple': volume_multiple,
                    'avg_volume': avg_volume,
                    'current_volume': current_volume
                }
            )
        
        return None
    
    def detect_momentum_breakout(
        self,
        symbol: str,
        current_price: float,
        momentum_15m: Optional[float],
        momentum_60m: Optional[float],
        volume: int
    ) -> Optional[BreakoutSignal]:
        """
        Detect momentum surges or reversals.
        
        Args:
            symbol: Stock symbol
            current_price: Current price
            momentum_15m: 15-minute momentum %
            momentum_60m: 60-minute momentum %
            volume: Current volume
            
        Returns:
            BreakoutSignal if momentum breakout detected, None otherwise
        """
        # Check 15-minute momentum surge
        if momentum_15m and abs(momentum_15m) >= self.momentum_threshold:
            strength = min(abs(momentum_15m) * 15, 100)
            
            return BreakoutSignal(
                symbol=symbol,
                breakout_type=BreakoutType.MOMENTUM_SURGE,
                strength=strength,
                timestamp=datetime.now(),
                price=current_price,
                volume=volume,
                details={
                    'momentum_15m': momentum_15m,
                    'momentum_60m': momentum_60m,
                    'timeframe': '15m'
                }
            )
        
        # Check 60-minute momentum
        if momentum_60m and abs(momentum_60m) >= self.momentum_threshold:
            strength = min(abs(momentum_60m) * 12, 100)
            
            return BreakoutSignal(
                symbol=symbol,
                breakout_type=BreakoutType.MOMENTUM_SURGE,
                strength=strength,
                timestamp=datetime.now(),
                price=current_price,
                volume=volume,
                details={
                    'momentum_15m': momentum_15m,
                    'momentum_60m': momentum_60m,
                    'timeframe': '60m'
                }
            )
        
        # Check momentum reversal (15m vs 60m divergence)
        if momentum_15m and momentum_60m:
            if (momentum_15m > 0 and momentum_60m < -self.momentum_threshold) or \
               (momentum_15m < 0 and momentum_60m > self.momentum_threshold):
                strength = min(abs(momentum_15m - momentum_60m) * 10, 100)
                
                return BreakoutSignal(
                    symbol=symbol,
                    breakout_type=BreakoutType.MOMENTUM_REVERSAL,
                    strength=strength,
                    timestamp=datetime.now(),
                    price=current_price,
                    volume=volume,
                    details={
                        'momentum_15m': momentum_15m,
                        'momentum_60m': momentum_60m,
                        'divergence': momentum_15m - momentum_60m
                    }
                )
        
        return None
    
    def scan_for_breakouts(
        self,
        stock_data: Dict
    ) -> List[BreakoutSignal]:
        """
        Scan a single stock for all breakout types.
        
        Args:
            stock_data: Dictionary with stock data including price, volume, etc.
            
        Returns:
            List of detected breakout signals
        """
        signals = []
        
        symbol = stock_data.get('symbol')
        if not symbol:
            return signals
        
        # Extract data
        current_price = stock_data.get('price', stock_data.get('regularMarketPrice', 0))
        day_open = stock_data.get('open', stock_data.get('regularMarketOpen', current_price))
        day_high = stock_data.get('dayHigh', stock_data.get('regularMarketDayHigh', current_price))
        day_low = stock_data.get('dayLow', stock_data.get('regularMarketDayLow', current_price))
        prev_close = stock_data.get('previousClose', stock_data.get('regularMarketPreviousClose', current_price))
        current_volume = stock_data.get('volume', stock_data.get('regularMarketVolume', 0))
        avg_volume = stock_data.get('avg_volume', stock_data.get('averageDailyVolume10Day', 0))
        
        # Intraday momentum (if available)
        intraday_data = stock_data.get('intraday_data', {})
        momentum_15m = intraday_data.get('momentum_15m')
        momentum_60m = intraday_data.get('momentum_60m')
        
        # Detect price breakouts
        if current_price > 0:
            price_signal = self.detect_price_breakout(
                symbol, current_price, day_open, day_high, day_low, prev_close
            )
            if price_signal and price_signal.strength >= self.min_signal_strength:
                signals.append(price_signal)
        
        # Detect volume spikes
        if current_volume > 0 and avg_volume > 0:
            volume_signal = self.detect_volume_spike(
                symbol, current_volume, avg_volume, current_price
            )
            if volume_signal and volume_signal.strength >= self.min_signal_strength:
                signals.append(volume_signal)
        
        # Detect momentum breakouts
        if momentum_15m or momentum_60m:
            momentum_signal = self.detect_momentum_breakout(
                symbol, current_price, momentum_15m, momentum_60m, current_volume
            )
            if momentum_signal and momentum_signal.strength >= self.min_signal_strength:
                signals.append(momentum_signal)
        
        return signals
    
    def scan_multiple_stocks(
        self,
        stocks_data: List[Dict]
    ) -> List[BreakoutSignal]:
        """
        Scan multiple stocks for breakouts.
        
        Args:
            stocks_data: List of stock data dictionaries
            
        Returns:
            List of all detected breakout signals, sorted by strength
        """
        all_signals = []
        
        for stock_data in stocks_data:
            signals = self.scan_for_breakouts(stock_data)
            all_signals.extend(signals)
        
        # Sort by strength (strongest first)
        all_signals.sort(key=lambda s: s.strength, reverse=True)
        
        # Store for later reference
        self.detected_signals = all_signals
        
        if all_signals:
            logger.info(f"Detected {len(all_signals)} breakout signals")
            for signal in all_signals[:5]:  # Log top 5
                logger.info(f"  {signal.symbol}: {signal.breakout_type.value} "
                          f"(strength: {signal.strength:.1f})")
        
        return all_signals
    
    def get_top_breakouts(
        self,
        max_count: int = 10,
        min_strength: Optional[float] = None
    ) -> List[BreakoutSignal]:
        """
        Get top breakout signals.
        
        Args:
            max_count: Maximum number of signals to return
            min_strength: Optional minimum strength filter
            
        Returns:
            List of top breakout signals
        """
        signals = self.detected_signals
        
        if min_strength:
            signals = [s for s in signals if s.strength >= min_strength]
        
        return signals[:max_count]
    
    def reset(self) -> None:
        """Reset detected signals"""
        self.detected_signals.clear()


def test_breakout_detector():
    """Test breakout detector functionality"""
    print("\n" + "="*80)
    print("TESTING BREAKOUT DETECTOR")
    print("="*80)
    
    detector = BreakoutDetector(
        price_breakout_threshold=2.0,
        volume_spike_multiplier=2.0,
        momentum_threshold=3.0,
        min_signal_strength=60.0
    )
    
    # Simulate stock data with various breakout scenarios
    test_stocks = [
        {
            'symbol': 'AAPL',
            'price': 180.00,
            'open': 175.50,
            'dayHigh': 180.00,
            'dayLow': 174.00,
            'previousClose': 175.00,
            'volume': 80_000_000,
            'avg_volume': 60_000_000,
            'intraday_data': {
                'momentum_15m': 2.8,
                'momentum_60m': 1.5
            }
        },
        {
            'symbol': 'MSFT',
            'price': 392.50,
            'open': 385.00,
            'dayHigh': 392.50,
            'dayLow': 384.00,
            'previousClose': 380.00,
            'volume': 90_000_000,
            'avg_volume': 30_000_000,  # 3x volume spike!
            'intraday_data': {
                'momentum_15m': 4.2,  # Strong momentum!
                'momentum_60m': 3.1
            }
        },
        {
            'symbol': 'GOOGL',
            'price': 139.00,
            'open': 141.00,
            'dayHigh': 142.00,
            'dayLow': 139.00,
            'previousClose': 141.50,
            'volume': 22_000_000,
            'avg_volume': 25_000_000,
            'intraday_data': {
                'momentum_15m': -1.8,
                'momentum_60m': -0.5
            }
        },
    ]
    
    print("\n--- Scanning for Breakouts ---")
    signals = detector.scan_multiple_stocks(test_stocks)
    
    print(f"\nTotal Signals Detected: {len(signals)}")
    print("\n--- Top Signals ---")
    for i, signal in enumerate(signals, 1):
        print(f"\n{i}. {signal.symbol}")
        print(f"   Type: {signal.breakout_type.value}")
        print(f"   Strength: {signal.strength:.1f}/100")
        print(f"   Price: ${signal.price:.2f}")
        print(f"   Details: {signal.details}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Run test
    test_breakout_detector()
