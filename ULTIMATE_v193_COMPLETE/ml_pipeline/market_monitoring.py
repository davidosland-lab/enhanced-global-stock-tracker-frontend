"""
Market Monitoring Module - Intraday Sentiment & Scanning
========================================================

Monitoring components for real-time market sentiment tracking
and intraday opportunity scanning.

Components:
- MarketSentimentMonitor: Track SPY, VIX, market breadth
- IntradayScanner: 15-minute breakout detection
- CrossTimeframeCoordinator: Enhance swing signals with intraday context

Author: Enhanced Global Stock Tracker
Version: 1.0
Date: December 25, 2024
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class MarketSentiment(Enum):
    """Market sentiment classification"""
    VERY_BULLISH = "VERY_BULLISH"      # >80
    BULLISH = "BULLISH"                 # 70-80
    NEUTRAL = "NEUTRAL"                 # 40-70
    BEARISH = "BEARISH"                 # 20-40
    VERY_BEARISH = "VERY_BEARISH"       # <20


@dataclass
class SentimentReading:
    """Market sentiment reading"""
    timestamp: datetime
    sentiment_score: float  # 0-100
    sentiment_class: MarketSentiment
    spy_momentum: float
    vix_level: float
    breadth_ratio: Optional[float] = None
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['sentiment_class'] = self.sentiment_class.value
        return d


@dataclass
class IntradayAlert:
    """Intraday breakout/breakdown alert"""
    timestamp: datetime
    symbol: str
    alert_type: str  # 'BULLISH_BREAKOUT', 'BEARISH_BREAKDOWN'
    price_change_pct: float
    volume_ratio: float
    signal_strength: float  # 0-100
    recommended_action: str  # 'ENTER', 'EXIT', 'WATCH'
    
    def to_dict(self) -> Dict:
        return asdict(self)


class MarketSentimentMonitor:
    """
    Real-time market sentiment monitor
    
    Tracks SPY, VIX, and market breadth to provide
    overall market sentiment score (0-100)
    """
    
    def __init__(
        self,
        spy_weight: float = 0.6,
        vix_weight: float = 0.4,
        update_interval_minutes: int = 5
    ):
        """
        Initialize market sentiment monitor
        
        Args:
            spy_weight: Weight for SPY momentum (60%)
            vix_weight: Weight for VIX level (40%)
            update_interval_minutes: How often to update (5 min)
        """
        self.spy_weight = spy_weight
        self.vix_weight = vix_weight
        self.update_interval_minutes = update_interval_minutes
        
        # State
        self.last_sentiment = None
        self.last_update = None
        self.sentiment_history = []
        
        logger.info("[CHART] MarketSentimentMonitor initialized")
        logger.info(f"   Weights: SPY({spy_weight}), VIX({vix_weight})")
    
    def get_current_sentiment(
        self,
        spy_data: Optional[pd.DataFrame] = None,
        vix_data: Optional[pd.DataFrame] = None
    ) -> SentimentReading:
        """
        Get current market sentiment
        
        Args:
            spy_data: Recent SPY price data
            vix_data: Recent VIX data
        
        Returns:
            SentimentReading with score 0-100
        """
        try:
            # Fetch data if not provided
            if spy_data is None:
                spy_data = self._fetch_spy_data()
            if vix_data is None:
                vix_data = self._fetch_vix_data()
            
            # Calculate SPY momentum (0-100)
            spy_momentum = self._calculate_spy_momentum(spy_data)
            
            # Calculate VIX level (0-100, inverted)
            vix_level = self._calculate_vix_level(vix_data)
            
            # Combined sentiment
            sentiment_score = (
                spy_momentum * self.spy_weight +
                vix_level * self.vix_weight
            )
            
            # Classify sentiment
            if sentiment_score > 80:
                sentiment_class = MarketSentiment.VERY_BULLISH
            elif sentiment_score > 70:
                sentiment_class = MarketSentiment.BULLISH
            elif sentiment_score > 40:
                sentiment_class = MarketSentiment.NEUTRAL
            elif sentiment_score > 20:
                sentiment_class = MarketSentiment.BEARISH
            else:
                sentiment_class = MarketSentiment.VERY_BEARISH
            
            # Create reading
            reading = SentimentReading(
                timestamp=datetime.now(),
                sentiment_score=sentiment_score,
                sentiment_class=sentiment_class,
                spy_momentum=spy_momentum,
                vix_level=vix_level
            )
            
            # Update state
            self.last_sentiment = reading
            self.last_update = datetime.now()
            self.sentiment_history.append(reading)
            
            # Keep only last 100 readings
            if len(self.sentiment_history) > 100:
                self.sentiment_history = self.sentiment_history[-100:]
            
            logger.info(
                f"[CHART] Market Sentiment: {sentiment_score:.1f} ({sentiment_class.value}) | "
                f"SPY={spy_momentum:.1f}, VIX={vix_level:.1f}"
            )
            
            return reading
            
        except Exception as e:
            logger.error(f"Error calculating market sentiment: {e}")
            return self._get_neutral_sentiment()
    
    def _calculate_spy_momentum(self, spy_data: pd.DataFrame) -> float:
        """
        Calculate SPY momentum score (0-100)
        
        Higher score = bullish momentum
        """
        try:
            if len(spy_data) < 20:
                return 50.0  # Neutral
            
            prices = spy_data['Close'].values
            
            # Recent return (today vs 5 days ago)
            recent_return = (prices[-1] / prices[-6] - 1) if len(prices) >= 6 else 0
            
            # Trend strength (price vs 20-day MA)
            ma_20 = prices[-20:].mean()
            distance_from_ma = (prices[-1] / ma_20 - 1)
            
            # ROC (rate of change)
            roc = (prices[-1] / prices[-21] - 1) if len(prices) >= 21 else 0
            
            # Combine into 0-100 score
            momentum = (
                (recent_return + 0.05) / 0.10 * 40 +  # Recent: -5% to +5% -> 0-40
                (distance_from_ma + 0.05) / 0.10 * 30 +  # Trend: -5% to +5% -> 0-30
                (roc + 0.10) / 0.20 * 30  # ROC: -10% to +10% -> 0-30
            )
            
            return np.clip(momentum, 0, 100)
            
        except Exception as e:
            logger.error(f"Error calculating SPY momentum: {e}")
            return 50.0
    
    def _calculate_vix_level(self, vix_data: pd.DataFrame) -> float:
        """
        Calculate VIX level score (0-100, INVERTED)
        
        Lower VIX = higher score (more bullish)
        Higher VIX = lower score (more bearish)
        """
        try:
            if len(vix_data) == 0:
                return 50.0  # Neutral
            
            current_vix = vix_data['Close'].iloc[-1]
            
            # VIX interpretation:
            # <15 = Very bullish (low fear) → 90-100
            # 15-20 = Bullish → 70-90
            # 20-30 = Neutral → 40-70
            # 30-40 = Bearish → 20-40
            # >40 = Very bearish (high fear) → 0-20
            
            if current_vix < 15:
                score = 90 + (15 - current_vix) * 2
            elif current_vix < 20:
                score = 70 + (20 - current_vix) * 4
            elif current_vix < 30:
                score = 40 + (30 - current_vix) * 3
            elif current_vix < 40:
                score = 20 + (40 - current_vix) * 2
            else:
                score = max(0, 20 - (current_vix - 40))
            
            return np.clip(score, 0, 100)
            
        except Exception as e:
            logger.error(f"Error calculating VIX level: {e}")
            return 50.0
    
    def _fetch_spy_data(self) -> pd.DataFrame:
        """Fetch recent SPY data"""
        try:
            import yfinance as yf
            spy = yf.Ticker("SPY")
            data = spy.history(period="1mo")
            return data
        except Exception as e:
            logger.error(f"Error fetching SPY data: {e}")
            return pd.DataFrame()
    
    def _fetch_vix_data(self) -> pd.DataFrame:
        """Fetch recent VIX data"""
        try:
            import yfinance as yf
            vix = yf.Ticker("^VIX")
            data = vix.history(period="1mo")
            return data
        except Exception as e:
            logger.error(f"Error fetching VIX data: {e}")
            return pd.DataFrame()
    
    def _get_neutral_sentiment(self) -> SentimentReading:
        """Return neutral sentiment on error"""
        return SentimentReading(
            timestamp=datetime.now(),
            sentiment_score=50.0,
            sentiment_class=MarketSentiment.NEUTRAL,
            spy_momentum=50.0,
            vix_level=50.0
        )


class IntradayScanner:
    """
    Real-time intraday scanner for breakouts and breakdowns
    
    Scans every 15 minutes for:
    - Bullish breakouts (price + volume surge)
    - Bearish breakdowns (price drop + volume surge)
    """
    
    def __init__(
        self,
        scan_interval_minutes: int = 15,
        breakout_threshold: float = 70.0,
        price_change_threshold: float = 2.0,
        volume_multiplier: float = 1.5,
        momentum_threshold: float = 3.0
    ):
        """
        Initialize intraday scanner
        
        Args:
            scan_interval_minutes: Scan frequency (15 min)
            breakout_threshold: Min signal strength (70)
            price_change_threshold: Min price change % (2%)
            volume_multiplier: Min volume ratio (1.5x)
            momentum_threshold: Min momentum score (3)
        """
        self.scan_interval_minutes = scan_interval_minutes
        self.breakout_threshold = breakout_threshold
        self.price_change_threshold = price_change_threshold
        self.volume_multiplier = volume_multiplier
        self.momentum_threshold = momentum_threshold
        
        # State
        self.last_scan = None
        self.scan_count = 0
        self.alerts = []
        
        logger.info("[SCAN] IntradayScanner initialized")
        logger.info(f"   Interval: {scan_interval_minutes} min, Threshold: {breakout_threshold}")
    
    def scan_for_opportunities(
        self,
        symbols: List[str],
        price_data_provider: callable
    ) -> List[IntradayAlert]:
        """
        Scan symbols for intraday breakouts/breakdowns
        
        Args:
            symbols: List of symbols to scan
            price_data_provider: Function to fetch price data for a symbol
        
        Returns:
            List of IntradayAlert objects
        """
        alerts = []
        
        try:
            self.scan_count += 1
            logger.info(f"[SCAN] Intraday Scan #{self.scan_count} - {len(symbols)} symbols")
            
            for symbol in symbols:
                try:
                    # Get recent price data
                    price_data = price_data_provider(symbol)
                    
                    if price_data is None or len(price_data) < 20:
                        continue
                    
                    # Check for breakout or breakdown
                    alert = self._check_breakout(symbol, price_data)
                    
                    if alert and alert.signal_strength >= self.breakout_threshold:
                        alerts.append(alert)
                        logger.info(
                            f"[ALERT] {alert.alert_type}: {symbol} | "
                            f"Price={alert.price_change_pct:+.2f}%, "
                            f"Volume={alert.volume_ratio:.2f}x, "
                            f"Strength={alert.signal_strength:.1f}"
                        )
                
                except Exception as e:
                    logger.error(f"Error scanning {symbol}: {e}")
                    continue
            
            # Update state
            self.last_scan = datetime.now()
            self.alerts.extend(alerts)
            
            # Keep only recent alerts (last 50)
            if len(self.alerts) > 50:
                self.alerts = self.alerts[-50:]
            
            logger.info(f"[OK] Scan complete: {len(alerts)} alerts generated")
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error in intraday scan: {e}")
            return []
    
    def _check_breakout(self, symbol: str, price_data: pd.DataFrame) -> Optional[IntradayAlert]:
        """
        Check if symbol has breakout or breakdown
        
        Returns:
            IntradayAlert if breakout detected, None otherwise
        """
        try:
            if len(price_data) < 20:
                return None
            
            # Calculate metrics
            current_price = price_data['Close'].iloc[-1]
            prev_price = price_data['Close'].iloc[-2]
            price_change_pct = (current_price / prev_price - 1) * 100
            
            # Volume ratio
            current_volume = price_data['Volume'].iloc[-1]
            avg_volume = price_data['Volume'].tail(20).mean()
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Momentum
            prices = price_data['Close'].values
            momentum = (prices[-1] / prices[-6] - 1) * 100 if len(prices) >= 6 else 0
            
            # Check for breakout conditions
            is_bullish_breakout = (
                price_change_pct > self.price_change_threshold and
                volume_ratio > self.volume_multiplier and
                momentum > 0
            )
            
            is_bearish_breakdown = (
                price_change_pct < -self.price_change_threshold and
                volume_ratio > self.volume_multiplier and
                momentum < 0
            )
            
            if not is_bullish_breakout and not is_bearish_breakdown:
                return None
            
            # Calculate signal strength
            signal_strength = (
                abs(price_change_pct) * 15 +  # Price component
                (volume_ratio - 1) * 20 +     # Volume component
                abs(momentum) * 5              # Momentum component
            )
            signal_strength = min(signal_strength, 100)
            
            # Determine alert type and action
            if is_bullish_breakout:
                alert_type = 'BULLISH_BREAKOUT'
                recommended_action = 'ENTER' if signal_strength > 80 else 'WATCH'
            else:
                alert_type = 'BEARISH_BREAKDOWN'
                recommended_action = 'EXIT' if signal_strength > 80 else 'WATCH'
            
            return IntradayAlert(
                timestamp=datetime.now(),
                symbol=symbol,
                alert_type=alert_type,
                price_change_pct=price_change_pct,
                volume_ratio=volume_ratio,
                signal_strength=signal_strength,
                recommended_action=recommended_action
            )
            
        except Exception as e:
            logger.error(f"Error checking breakout for {symbol}: {e}")
            return None


class CrossTimeframeCoordinator:
    """
    Coordinates swing signals with intraday context
    
    Enhances swing trading signals using real-time intraday sentiment:
    - Block entries when market sentiment < 30
    - Boost positions when market sentiment > 70
    - Early exit on intraday breakdowns
    """
    
    def __init__(
        self,
        sentiment_monitor: MarketSentimentMonitor,
        intraday_scanner: IntradayScanner,
        sentiment_boost_threshold: float = 70.0,
        sentiment_block_threshold: float = 30.0,
        early_exit_threshold: float = 80.0
    ):
        """
        Initialize cross-timeframe coordinator
        
        Args:
            sentiment_monitor: MarketSentimentMonitor instance
            intraday_scanner: IntradayScanner instance
            sentiment_boost_threshold: Sentiment level to boost (70)
            sentiment_block_threshold: Sentiment level to block (30)
            early_exit_threshold: Breakdown strength to exit (80)
        """
        self.sentiment_monitor = sentiment_monitor
        self.intraday_scanner = intraday_scanner
        self.sentiment_boost_threshold = sentiment_boost_threshold
        self.sentiment_block_threshold = sentiment_block_threshold
        self.early_exit_threshold = early_exit_threshold
        
        logger.info("[COORD] CrossTimeframeCoordinator initialized")
        logger.info(f"   Boost: >{sentiment_boost_threshold}, Block: <{sentiment_block_threshold}")
    
    def enhance_signal(self, symbol: str, base_signal: Dict) -> Dict:
        """
        Enhance swing signal with intraday context
        
        Args:
            symbol: Stock symbol
            base_signal: Base signal from SwingSignalGenerator
        
        Returns:
            Enhanced signal with intraday adjustments
        """
        try:
            # Get current market sentiment
            sentiment = self.sentiment_monitor.get_current_sentiment()
            
            # Start with base signal
            enhanced_signal = base_signal.copy()
            enhanced_signal['intraday_enhancement'] = {
                'market_sentiment': sentiment.sentiment_score,
                'sentiment_class': sentiment.sentiment_class.value,
                'adjustments': []
            }
            
            # Check for entry blocks
            if base_signal['prediction'] == 'BUY':
                if sentiment.sentiment_score < self.sentiment_block_threshold:
                    enhanced_signal['prediction'] = 'HOLD'
                    enhanced_signal['confidence'] = 0.0
                    enhanced_signal['intraday_enhancement']['adjustments'].append(
                        f"BLOCKED: Market sentiment {sentiment.sentiment_score:.1f} < {self.sentiment_block_threshold}"
                    )
                    logger.info(f"[ERROR] BLOCKED {symbol} entry - weak market sentiment: {sentiment.sentiment_score:.1f}")
                    return enhanced_signal
            
            # Check for position boost
            if base_signal['prediction'] == 'BUY' and sentiment.sentiment_score > self.sentiment_boost_threshold:
                # Boost confidence
                boost_amount = min(10, (sentiment.sentiment_score - self.sentiment_boost_threshold) / 2)
                enhanced_signal['confidence'] = min(0.95, enhanced_signal['confidence'] + boost_amount / 100)
                
                # Boost position size
                if 'phase3' in enhanced_signal:
                    current_size = enhanced_signal['phase3'].get('recommended_position_size', 0.25)
                    enhanced_signal['phase3']['recommended_position_size'] = min(0.30, current_size * 1.2)
                
                enhanced_signal['intraday_enhancement']['adjustments'].append(
                    f"BOOSTED: Market sentiment {sentiment.sentiment_score:.1f} > {self.sentiment_boost_threshold} "
                    f"(+{boost_amount:.1f}% confidence)"
                )
                logger.info(f"[BOOST] BOOSTED {symbol} - strong market sentiment: {sentiment.sentiment_score:.1f}")
            
            return enhanced_signal
            
        except Exception as e:
            logger.error(f"Error enhancing signal: {e}")
            return base_signal
    
    def check_early_exit(self, symbol: str, current_position: Dict) -> Optional[str]:
        """
        Check if position should exit early due to intraday breakdown
        
        Args:
            symbol: Stock symbol
            current_position: Current position dict
        
        Returns:
            Exit reason if should exit, None otherwise
        """
        try:
            # Check recent intraday alerts for this symbol
            recent_alerts = [
                alert for alert in self.intraday_scanner.alerts
                if alert.symbol == symbol and
                   alert.alert_type == 'BEARISH_BREAKDOWN' and
                   (datetime.now() - alert.timestamp).total_seconds() < 3600  # Last hour
            ]
            
            # If strong breakdown detected, recommend early exit
            for alert in recent_alerts:
                if alert.signal_strength >= self.early_exit_threshold:
                    reason = (
                        f"INTRADAY_BREAKDOWN: {alert.alert_type} "
                        f"(strength={alert.signal_strength:.1f}, "
                        f"price={alert.price_change_pct:+.2f}%, "
                        f"volume={alert.volume_ratio:.2f}x)"
                    )
                    logger.warning(f"[WARN] Early exit recommended for {symbol}: {reason}")
                    return reason
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking early exit: {e}")
            return None


# Convenience function
def create_monitoring_system(
    scan_interval_minutes: int = 15,
    breakout_threshold: float = 70.0
) -> Tuple[MarketSentimentMonitor, IntradayScanner, CrossTimeframeCoordinator]:
    """
    Create complete monitoring system
    
    Returns:
        (sentiment_monitor, intraday_scanner, coordinator)
    """
    sentiment_monitor = MarketSentimentMonitor()
    intraday_scanner = IntradayScanner(
        scan_interval_minutes=scan_interval_minutes,
        breakout_threshold=breakout_threshold
    )
    coordinator = CrossTimeframeCoordinator(sentiment_monitor, intraday_scanner)
    
    logger.info("[OK] Complete monitoring system created")
    
    return (sentiment_monitor, intraday_scanner, coordinator)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    print("Market Monitoring Module")
    print("=" * 70)
    print("\nComponents:")
    print("  [CHART] MarketSentimentMonitor - Track SPY, VIX, market breadth")
    print("  🔍 IntradayScanner - 15-minute breakout detection")
    print("  🔗 CrossTimeframeCoordinator - Enhance swing signals")
    print("\nUsage:")
    print("  from ml_pipeline.market_monitoring import create_monitoring_system")
    print("  sentiment, scanner, coordinator = create_monitoring_system()")
    print("  ")
    print("  # Get market sentiment")
    print("  reading = sentiment.get_current_sentiment()")
    print("  ")
    print("  # Scan for opportunities")
    print("  alerts = scanner.scan_for_opportunities(symbols, data_provider)")
    print("  ")
    print("  # Enhance swing signal")
    print("  enhanced_signal = coordinator.enhance_signal(symbol, base_signal)")
