"""
Enhanced Opportunity Monitor - Continuous Watchlist Scanning
============================================================

**Purpose**: Monitor 720-stock universe for trading opportunities throughout the day

**Features**:
- Continuous monitoring (5-minute updates)
- Multi-factor opportunity detection
- News-driven alerts
- Volume anomaly detection
- Sector rotation signals
- Missed opportunity tracking
- **Market-aware scanning**: Only scans stocks when their market is open

**Author**: Enhanced Global Stock Tracker
**Version**: 1.1
**Date**: 2026-02-07
**Updated**: 2026-02-07 - Added market hours filtering
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import sys
from pathlib import Path

# Import MarketCalendar for market hours checking
try:
    sys.path.insert(0, str(Path(__file__).parent.parent / 'ml_pipeline'))
    from market_calendar import MarketCalendar, Exchange, MarketStatus
    MARKET_CALENDAR_AVAILABLE = True
except ImportError:
    MARKET_CALENDAR_AVAILABLE = False
    logger.warning("[OpportunityMonitor] MarketCalendar not available - will scan all symbols")

logger = logging.getLogger(__name__)


class OpportunityType(Enum):
    """Types of trading opportunities"""
    BUY_SETUP = "BUY_SETUP"
    SELL_WARNING = "SELL_WARNING"
    POSITION_ADJUST = "POSITION_ADJUST"
    NEWS_DRIVEN = "NEWS_DRIVEN"
    TECHNICAL_BREAKOUT = "TECHNICAL_BREAKOUT"
    VOLUME_SURGE = "VOLUME_SURGE"
    SECTOR_MOMENTUM = "SECTOR_MOMENTUM"


class Urgency(Enum):
    """Urgency levels for opportunities"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class OpportunityAlert:
    """Opportunity alert data structure"""
    symbol: str
    opportunity_type: OpportunityType
    urgency: Urgency
    confidence: float  # 0-100
    reason: str
    timestamp: datetime
    price: float
    expected_move_pct: float  # Expected % price movement
    timeframe: str  # "immediate", "intraday", "swing"
    
    # Supporting data
    technical_score: float = 0.0
    sentiment_score: float = 0.0
    volume_ratio: float = 1.0
    sector_momentum: float = 0.0
    
    # Actionable info
    suggested_action: str = ""  # "BUY", "SELL", "WATCH"
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    target_price: Optional[float] = None


class OpportunityMonitor:
    """
    Continuous opportunity monitoring across entire watchlist
    
    **Purpose**: Don't miss opportunities like STAN.L (+1.87%)
    
    **Strategy**:
    1. Monitor all symbols every 5 minutes
    2. Detect emerging opportunities early
    3. Alert for immediate action
    4. Track missed opportunities for analysis
    """
    
    def __init__(
        self,
        symbols: List[str],
        update_interval_minutes: int = 5,
        confidence_threshold: float = 48.0,  # v188: Lowered from 65.0
        enable_news_monitoring: bool = True,
        enable_technical_monitoring: bool = True,
        enable_volume_monitoring: bool = True,
        enable_market_hours_filter: bool = True
    ):
        """
        Initialize opportunity monitor
        
        Args:
            symbols: List of symbols to monitor
            update_interval_minutes: How often to scan (default 5 minutes)
            confidence_threshold: Minimum confidence for alert (default 65%)
            enable_news_monitoring: Monitor news for sentiment spikes
            enable_technical_monitoring: Monitor technical breakouts
            enable_volume_monitoring: Monitor volume anomalies
            enable_market_hours_filter: Only scan stocks when market is open (default True)
        """
        self.symbols = symbols
        self.update_interval = update_interval_minutes
        self.confidence_threshold = confidence_threshold
        
        # Feature flags
        self.enable_news = enable_news_monitoring
        self.enable_technical = enable_technical_monitoring
        self.enable_volume = enable_volume_monitoring
        self.enable_market_hours_filter = enable_market_hours_filter and MARKET_CALENDAR_AVAILABLE
        
        # State tracking
        self.last_scan = {}  # symbol -> timestamp
        self.last_prices = {}  # symbol -> price
        self.last_alerts = {}  # symbol -> OpportunityAlert
        self.missed_opportunities = []  # Track opportunities not acted upon
        
        # Alert history
        self.alert_history = []
        self.max_history_size = 1000
        
        # Market calendar (if available)
        self.market_calendar = None
        if MARKET_CALENDAR_AVAILABLE:
            self.market_calendar = MarketCalendar()
        
        # Statistics
        self.scan_stats = {
            'total_scans': 0,
            'symbols_scanned': 0,
            'symbols_skipped_closed': 0,
            'symbols_skipped_interval': 0,
            'opportunities_found': 0
        }
        
        logger.info(f"[OpportunityMonitor] Initialized with {len(symbols)} symbols")
        logger.info(f"[OpportunityMonitor] Update interval: {update_interval_minutes} minutes")
        logger.info(f"[OpportunityMonitor] Confidence threshold: {confidence_threshold}%")
        logger.info(f"[OpportunityMonitor] Market hours filter: {'ENABLED' if self.enable_market_hours_filter else 'DISABLED'}")
        if not MARKET_CALENDAR_AVAILABLE:
            logger.warning("[OpportunityMonitor] MarketCalendar unavailable - all symbols will be scanned")
    
    def scan_for_opportunities(
        self,
        fetch_price_func,
        fetch_news_func=None,
        market_sentiment: float = 50.0,
        existing_positions: List[str] = None
    ) -> List[OpportunityAlert]:
        """
        Scan all symbols for trading opportunities
        **Market-aware**: Only scans stocks when their market is open
        
        Args:
            fetch_price_func: Function to fetch current price data
            fetch_news_func: Function to fetch news data (optional)
            market_sentiment: Current market sentiment 0-100
            existing_positions: List of symbols already held
            
        Returns:
            List of OpportunityAlert objects
        """
        opportunities = []
        existing_positions = existing_positions or []
        
        # Track statistics for this scan
        self.scan_stats['total_scans'] += 1
        scanned_count = 0
        skipped_closed = 0
        skipped_interval = 0
        opportunity_count = 0
        
        # Group symbols by market for logging
        market_groups = self._group_symbols_by_market(self.symbols)
        
        logger.info(f"[OpportunityMonitor] Scan #{self.scan_stats['total_scans']} starting...")
        logger.info(f"[OpportunityMonitor] Total symbols: {len(self.symbols)}")
        logger.info(f"[OpportunityMonitor] Market breakdown: US={len(market_groups['US'])}, "
                   f"UK={len(market_groups['UK'])}, AU={len(market_groups['AU'])}")
        logger.info(f"[OpportunityMonitor] Market Sentiment: {market_sentiment:.1f}/100")
        logger.info(f"[OpportunityMonitor] Existing Positions: {len(existing_positions)}")
        
        # Check market status for each market
        if self.enable_market_hours_filter:
            market_status = self._get_all_market_status()
            logger.info(f"[OpportunityMonitor] Market Status:")
            for market, status_info in market_status.items():
                logger.info(f"  {market}: {status_info['status'].value.upper()} "
                          f"({status_info['symbols_count']} symbols)")
        
        for symbol in self.symbols:
            try:
                # CHECK 1: Market hours filter (if enabled)
                if self.enable_market_hours_filter:
                    can_trade, reason = self._can_scan_symbol(symbol)
                    if not can_trade:
                        skipped_closed += 1
                        continue
                
                # CHECK 2: Scan interval
                if not self._should_scan(symbol):
                    skipped_interval += 1
                    continue
                
                scanned_count += 1
                
                # Skip if already holding (unless looking for exit signals)
                if symbol in existing_positions:
                    # Still monitor for exit signals
                    exit_signal = self._check_exit_opportunity(
                        symbol, fetch_price_func, market_sentiment
                    )
                    if exit_signal:
                        opportunities.append(exit_signal)
                        opportunity_count += 1
                    continue
                
                # Fetch current data
                price_data = fetch_price_func(symbol)
                if price_data is None or len(price_data) < 20:
                    continue
                
                current_price = price_data['Close'].iloc[-1]
                self.last_prices[symbol] = current_price
                
                # Evaluate opportunity
                opportunity = self._evaluate_opportunity(
                    symbol=symbol,
                    price_data=price_data,
                    news_data=fetch_news_func(symbol) if fetch_news_func else None,
                    market_sentiment=market_sentiment,
                    current_price=current_price
                )
                
                if opportunity:
                    # Check confidence threshold
                    if opportunity.confidence >= self.confidence_threshold:
                        opportunities.append(opportunity)
                        opportunity_count += 1
                        
                        # Store in alert history
                        self.last_alerts[symbol] = opportunity
                        self.alert_history.append(opportunity)
                        
                        # Trim history
                        if len(self.alert_history) > self.max_history_size:
                            self.alert_history = self.alert_history[-self.max_history_size:]
                        
                        logger.info(
                            f"[OPPORTUNITY] {symbol}: {opportunity.opportunity_type.value} "
                            f"(conf={opportunity.confidence:.1f}%, urgency={opportunity.urgency.value})"
                        )
                        logger.info(f"  -> {opportunity.reason}")
                
                # Update last scan time
                self.last_scan[symbol] = datetime.now()
                
            except Exception as e:
                logger.error(f"[OpportunityMonitor] Error scanning {symbol}: {e}")
                continue
        
        # Update statistics
        self.scan_stats['symbols_scanned'] += scanned_count
        self.scan_stats['symbols_skipped_closed'] += skipped_closed
        self.scan_stats['symbols_skipped_interval'] += skipped_interval
        self.scan_stats['opportunities_found'] += opportunity_count
        
        logger.info(
            f"[OpportunityMonitor] Scan complete: "
            f"{scanned_count} scanned, {skipped_closed} skipped (closed markets), "
            f"{skipped_interval} skipped (interval), {opportunity_count} opportunities found"
        )
        
        # Log efficiency metrics
        if self.enable_market_hours_filter:
            efficiency_pct = (skipped_closed / len(self.symbols) * 100) if len(self.symbols) > 0 else 0
            logger.info(f"[OpportunityMonitor] Efficiency: Saved {efficiency_pct:.1f}% of scans by filtering closed markets")
        
        # Sort by urgency and confidence
        opportunities.sort(
            key=lambda x: (
                3 if x.urgency == Urgency.CRITICAL else
                2 if x.urgency == Urgency.HIGH else
                1 if x.urgency == Urgency.MEDIUM else 0,
                x.confidence
            ),
            reverse=True
        )
        
        return opportunities
    
    def _should_scan(self, symbol: str) -> bool:
        """Check if symbol should be scanned now based on interval"""
        if symbol not in self.last_scan:
            return True
        
        time_since_last = (datetime.now() - self.last_scan[symbol]).total_seconds() / 60.0
        return time_since_last >= self.update_interval
    
    def _can_scan_symbol(self, symbol: str) -> Tuple[bool, str]:
        """
        Check if symbol can be scanned based on market hours
        
        Args:
            symbol: Stock symbol to check
            
        Returns:
            Tuple of (can_scan: bool, reason: str)
        """
        if not self.market_calendar:
            return (True, "Market calendar unavailable")
        
        # Use MarketCalendar's can_trade_symbol method
        can_trade, reason = self.market_calendar.can_trade_symbol(symbol)
        
        return (can_trade, reason)
    
    def _group_symbols_by_market(self, symbols: List[str]) -> Dict[str, List[str]]:
        """
        Group symbols by their market/exchange
        
        Args:
            symbols: List of symbols
            
        Returns:
            Dictionary mapping market name to list of symbols
        """
        markets = {
            'US': [],
            'UK': [],
            'AU': [],
            'OTHER': []
        }
        
        for symbol in symbols:
            if symbol.endswith('.AX'):
                markets['AU'].append(symbol)
            elif symbol.endswith('.L'):
                markets['UK'].append(symbol)
            elif symbol.endswith('.TO') or symbol.endswith('.V'):
                markets['OTHER'].append(symbol)
            else:
                markets['US'].append(symbol)
        
        return markets
    
    def _get_all_market_status(self) -> Dict[str, Dict]:
        """
        Get status for all markets (US, UK, AU)
        
        Returns:
            Dictionary with market status information
        """
        if not MARKET_CALENDAR_AVAILABLE:
            return {}
        
        market_groups = self._group_symbols_by_market(self.symbols)
        
        status_info = {}
        
        # Check US markets (NYSE/NASDAQ)
        if market_groups['US']:
            us_calendar = MarketCalendar(Exchange.NYSE)
            us_status = us_calendar.get_market_status()
            status_info['US'] = {
                'exchange': Exchange.NYSE,
                'status': us_status.status,
                'symbols_count': len(market_groups['US']),
                'time_to_open': us_status.time_to_open,
                'time_to_close': us_status.time_to_close
            }
        
        # Check UK market (LSE)
        if market_groups['UK']:
            uk_calendar = MarketCalendar(Exchange.LSE)
            uk_status = uk_calendar.get_market_status()
            status_info['UK'] = {
                'exchange': Exchange.LSE,
                'status': uk_status.status,
                'symbols_count': len(market_groups['UK']),
                'time_to_open': uk_status.time_to_open,
                'time_to_close': uk_status.time_to_close
            }
        
        # Check AU market (ASX)
        if market_groups['AU']:
            au_calendar = MarketCalendar(Exchange.ASX)
            au_status = au_calendar.get_market_status()
            status_info['AU'] = {
                'exchange': Exchange.ASX,
                'status': au_status.status,
                'symbols_count': len(market_groups['AU']),
                'time_to_open': au_status.time_to_open,
                'time_to_close': au_status.time_to_close
            }
        
        return status_info
    
    def _evaluate_opportunity(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        news_data: Optional[Dict],
        market_sentiment: float,
        current_price: float
    ) -> Optional[OpportunityAlert]:
        """
        Multi-factor opportunity evaluation
        
        Checks:
        1. Technical breakout
        2. News sentiment spike
        3. Volume surge
        4. Sector momentum
        5. Price action patterns
        """
        signals = []
        scores = {
            'technical': 0.0,
            'sentiment': 0.0,
            'volume': 0.0,
            'sector': 0.0
        }
        
        # 1. Technical Analysis
        if self.enable_technical:
            technical_signal, technical_score = self._check_technical_breakout(price_data)
            if technical_signal:
                signals.append(technical_signal)
                scores['technical'] = technical_score
        
        # 2. News Sentiment (if available)
        if self.enable_news and news_data:
            sentiment_signal, sentiment_score = self._check_sentiment_spike(news_data)
            if sentiment_signal:
                signals.append(sentiment_signal)
                scores['sentiment'] = sentiment_score
        
        # 3. Volume Anomaly
        if self.enable_volume:
            volume_signal, volume_score, volume_ratio = self._check_volume_anomaly(price_data)
            if volume_signal:
                signals.append(volume_signal)
                scores['volume'] = volume_score
        else:
            volume_ratio = 1.0
        
        # 4. Price Action Patterns
        pattern_signal = self._check_price_patterns(price_data)
        if pattern_signal:
            signals.append(pattern_signal)
        
        # No signals = no opportunity
        if not signals:
            return None
        
        # Combine signals
        opportunity = self._combine_signals(
            symbol=symbol,
            signals=signals,
            scores=scores,
            current_price=current_price,
            market_sentiment=market_sentiment,
            volume_ratio=volume_ratio
        )
        
        return opportunity
    
    def _check_technical_breakout(
        self, price_data: pd.DataFrame
    ) -> Tuple[Optional[str], float]:
        """
        Check for technical breakouts
        
        Patterns:
        - Resistance breakout
        - Moving average crossover
        - Bollinger Band squeeze breakout
        """
        if len(price_data) < 50:
            return None, 0.0
        
        close = price_data['Close']
        high = price_data['High']
        
        # Calculate indicators
        ma_20 = close.rolling(20).mean()
        ma_50 = close.rolling(50).mean()
        
        # 20-day high
        high_20 = high.rolling(20).max()
        
        current_price = close.iloc[-1]
        prev_price = close.iloc[-2]
        
        signals = []
        score = 50.0
        
        # 1. Breakout above 20-day high
        if current_price > high_20.iloc[-2] and prev_price <= high_20.iloc[-3]:
            signals.append("20-day high breakout")
            score += 20
        
        # 2. Golden cross (MA 20 crosses above MA 50)
        if ma_20.iloc[-1] > ma_50.iloc[-1] and ma_20.iloc[-2] <= ma_50.iloc[-2]:
            signals.append("Golden cross (MA 20 > MA 50)")
            score += 25
        
        # 3. Price above both MAs (trending)
        if current_price > ma_20.iloc[-1] > ma_50.iloc[-1]:
            signals.append("Strong uptrend (above MAs)")
            score += 15
        
        # 4. Recent pullback to MA (buy the dip)
        if len(close) >= 5:
            # Price was below MA 20, now crossing above
            if current_price > ma_20.iloc[-1] and close.iloc[-3] < ma_20.iloc[-3]:
                signals.append("Pullback to MA 20 - Bounce")
                score += 15
        
        if signals:
            return " + ".join(signals), min(score, 100.0)
        
        return None, 0.0
    
    def _check_sentiment_spike(
        self, news_data: Dict
    ) -> Tuple[Optional[str], float]:
        """
        Check for positive news sentiment spike
        
        Requires recent news with strong positive sentiment
        """
        if not news_data or 'sentiment' not in news_data:
            return None, 0.0
        
        sentiment = news_data.get('sentiment', 0.5)
        confidence = news_data.get('confidence', 0.0)
        article_count = news_data.get('article_count', 0)
        
        # Need strong positive sentiment with multiple articles
        if sentiment > 0.7 and confidence > 0.8 and article_count >= 3:
            signal = f"Strong positive news ({article_count} articles, sentiment {sentiment:.2f})"
            score = 70 + (sentiment - 0.7) * 100
            return signal, min(score, 100.0)
        
        return None, 0.0
    
    def _check_volume_anomaly(
        self, price_data: pd.DataFrame
    ) -> Tuple[Optional[str], float, float]:
        """
        Check for volume surge (accumulation signal)
        """
        if len(price_data) < 20:
            return None, 0.0, 1.0
        
        volume = price_data['Volume']
        
        # Average volume (20-day)
        avg_volume = volume.rolling(20).mean().iloc[-1]
        current_volume = volume.iloc[-1]
        
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Significant volume surge
        if volume_ratio > 2.0:
            signal = f"Volume surge {volume_ratio:.1f}x average"
            score = 60 + min((volume_ratio - 2.0) * 10, 40)
            return signal, score, volume_ratio
        elif volume_ratio > 1.5:
            signal = f"Elevated volume {volume_ratio:.1f}x average"
            score = 55 + min((volume_ratio - 1.5) * 10, 15)
            return signal, score, volume_ratio
        
        return None, 0.0, volume_ratio
    
    def _check_price_patterns(self, price_data: pd.DataFrame) -> Optional[str]:
        """
        Check for bullish price action patterns
        
        Patterns:
        - Higher highs, higher lows
        - Bullish engulfing
        - Morning star
        """
        if len(price_data) < 10:
            return None
        
        close = price_data['Close'].iloc[-10:]
        high = price_data['High'].iloc[-10:]
        low = price_data['Low'].iloc[-10:]
        
        # Higher highs and higher lows (last 5 days)
        recent_highs = high.iloc[-5:]
        recent_lows = low.iloc[-5:]
        
        if recent_highs.iloc[-1] > recent_highs.iloc[-3] and \
           recent_lows.iloc[-1] > recent_lows.iloc[-3]:
            return "Higher highs & higher lows"
        
        return None
    
    def _combine_signals(
        self,
        symbol: str,
        signals: List[str],
        scores: Dict[str, float],
        current_price: float,
        market_sentiment: float,
        volume_ratio: float
    ) -> OpportunityAlert:
        """
        Combine multiple signals into a single opportunity alert
        """
        # Calculate composite confidence
        weights = {
            'technical': 0.35,
            'sentiment': 0.30,
            'volume': 0.25,
            'sector': 0.10
        }
        
        confidence = sum(scores[k] * weights[k] for k in scores if scores[k] > 0)
        
        # Adjust for market sentiment
        if market_sentiment < 40:
            confidence *= 0.8  # Reduce confidence in bearish market
        elif market_sentiment > 70:
            confidence *= 1.1  # Boost confidence in bullish market
        
        confidence = min(confidence, 100.0)
        
        # Determine urgency
        if confidence >= 85 and volume_ratio > 2.0:
            urgency = Urgency.CRITICAL
            timeframe = "immediate"
            expected_move = 3.0
        elif confidence >= 75 and volume_ratio > 1.5:
            urgency = Urgency.HIGH
            timeframe = "intraday"
            expected_move = 2.0
        elif confidence >= 65:
            urgency = Urgency.MEDIUM
            timeframe = "swing"
            expected_move = 1.5
        else:
            urgency = Urgency.LOW
            timeframe = "swing"
            expected_move = 1.0
        
        # Determine opportunity type
        if scores.get('sentiment', 0) > 70:
            opp_type = OpportunityType.NEWS_DRIVEN
        elif scores.get('volume', 0) > 60:
            opp_type = OpportunityType.VOLUME_SURGE
        elif scores.get('technical', 0) > 70:
            opp_type = OpportunityType.TECHNICAL_BREAKOUT
        else:
            opp_type = OpportunityType.BUY_SETUP
        
        # Build reason string
        reason = " | ".join(signals[:3])  # Top 3 signals
        
        # Calculate suggested entry/stop/target
        entry_price = current_price
        stop_loss = current_price * 0.96  # -4% stop
        target_price = current_price * (1 + expected_move / 100)
        
        return OpportunityAlert(
            symbol=symbol,
            opportunity_type=opp_type,
            urgency=urgency,
            confidence=confidence,
            reason=reason,
            timestamp=datetime.now(),
            price=current_price,
            expected_move_pct=expected_move,
            timeframe=timeframe,
            technical_score=scores.get('technical', 0),
            sentiment_score=scores.get('sentiment', 0),
            volume_ratio=volume_ratio,
            sector_momentum=scores.get('sector', 0),
            suggested_action="BUY",
            entry_price=entry_price,
            stop_loss=stop_loss,
            target_price=target_price
        )
    
    def _check_exit_opportunity(
        self,
        symbol: str,
        fetch_price_func,
        market_sentiment: float
    ) -> Optional[OpportunityAlert]:
        """
        Check if existing position should be exited
        
        Checks:
        - Technical breakdown
        - Negative news
        - Market sentiment collapse
        """
        # This would check for exit signals on held positions
        # For now, return None (not implemented)
        return None
    
    def track_missed_opportunity(
        self,
        symbol: str,
        alert: OpportunityAlert,
        actual_move_pct: float,
        reason_missed: str
    ):
        """
        Track opportunities that were not acted upon
        
        This helps analyze why opportunities like STAN.L were missed
        """
        missed = {
            'symbol': symbol,
            'alert': alert,
            'actual_move_pct': actual_move_pct,
            'expected_move_pct': alert.expected_move_pct,
            'reason_missed': reason_missed,
            'timestamp': datetime.now()
        }
        
        self.missed_opportunities.append(missed)
        
        logger.warning(f"[MISSED OPPORTUNITY] {symbol}: {reason_missed}")
        logger.warning(f"  Expected: {alert.expected_move_pct:+.2f}%")
        logger.warning(f"  Actual: {actual_move_pct:+.2f}%")
        logger.warning(f"  Confidence: {alert.confidence:.1f}%")
    
    def get_missed_opportunities_report(self) -> Dict:
        """
        Generate report of missed opportunities
        
        Returns:
            Summary statistics and list of missed opportunities
        """
        if not self.missed_opportunities:
            return {'count': 0, 'opportunities': []}
        
        total_missed_gain = sum(
            m['actual_move_pct'] for m in self.missed_opportunities
            if m['actual_move_pct'] > 0
        )
        
        return {
            'count': len(self.missed_opportunities),
            'total_missed_gain_pct': total_missed_gain,
            'average_missed_gain_pct': total_missed_gain / len(self.missed_opportunities),
            'opportunities': self.missed_opportunities[-20:]  # Last 20
        }
    
    def get_alert_history(self, symbol: Optional[str] = None, limit: int = 50) -> List[OpportunityAlert]:
        """
        Get alert history for analysis
        
        Args:
            symbol: Filter by symbol (optional)
            limit: Maximum number of alerts to return
            
        Returns:
            List of recent alerts
        """
        if symbol:
            alerts = [a for a in self.alert_history if a.symbol == symbol]
        else:
            alerts = self.alert_history
        
        return alerts[-limit:]
    
    def get_scan_statistics(self) -> Dict:
        """
        Get scanning statistics
        
        Returns:
            Dictionary with scan statistics including efficiency metrics
        """
        total_scans = self.scan_stats['total_scans']
        symbols_scanned = self.scan_stats['symbols_scanned']
        symbols_skipped_closed = self.scan_stats['symbols_skipped_closed']
        symbols_skipped_interval = self.scan_stats['symbols_skipped_interval']
        opportunities_found = self.scan_stats['opportunities_found']
        
        # Calculate efficiency
        total_symbols_checked = symbols_scanned + symbols_skipped_closed + symbols_skipped_interval
        efficiency_pct = (symbols_skipped_closed / total_symbols_checked * 100) if total_symbols_checked > 0 else 0
        
        # Calculate opportunity rate
        opportunity_rate = (opportunities_found / symbols_scanned * 100) if symbols_scanned > 0 else 0
        
        return {
            'total_scans': total_scans,
            'symbols_scanned': symbols_scanned,
            'symbols_skipped_closed_markets': symbols_skipped_closed,
            'symbols_skipped_scan_interval': symbols_skipped_interval,
            'opportunities_found': opportunities_found,
            'efficiency_pct': round(efficiency_pct, 2),
            'opportunity_rate_pct': round(opportunity_rate, 2),
            'market_hours_filter_enabled': self.enable_market_hours_filter,
            'average_scans_per_cycle': round(symbols_scanned / total_scans, 2) if total_scans > 0 else 0
        }
