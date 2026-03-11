"""
Paper Trading Coordinator - Phase 3 Intraday Integration
=========================================================

A complete paper trading system that simulates live trading with:
- Swing trading signals (Phase 1-3 features)
- Intraday monitoring and alerts
- Real market data from yahooquery/yfinance
- No broker API required (simulated execution)

Usage:
    python paper_trading_coordinator.py --symbols AAPL,GOOGL,MSFT --capital 100000
"""

# ============================================================================
# CRITICAL: Set offline mode BEFORE any imports to prevent HuggingFace checks
# ============================================================================
import os
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN'] = '1'

import logging
import json
import time
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum
import sys

# Add parent directory to path to import ml_pipeline
sys.path.insert(0, str(Path(__file__).parent.parent))

# Create required directories if they don't exist
Path('logs').mkdir(exist_ok=True)
Path('state').mkdir(exist_ok=True)
Path('config').mkdir(exist_ok=True)

# Configure logging FIRST (before any imports that might use it)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/paper_trading.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Import sentiment integration (FinBERT v4.4.4)
try:
    from sentiment_integration import IntegratedSentimentAnalyzer, get_sentiment_analyzer
    SENTIMENT_INTEGRATION_AVAILABLE = True
    logger.info("[SENTIMENT] Integrated sentiment analyzer (FinBERT v4.4.4) available")
except ImportError as e:
    SENTIMENT_INTEGRATION_AVAILABLE = False
    logger.warning(f"[SENTIMENT] Integrated sentiment not available: {e}")

# Import swing signal generator and monitoring
try:
    from ml_pipeline.swing_signal_generator import SwingSignalGenerator
    from ml_pipeline.market_monitoring import (
        MarketSentimentMonitor,
        IntradayScanner,
        CrossTimeframeCoordinator,
        create_monitoring_system
    )
    ML_INTEGRATION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ML integration not available: {e}")
    ML_INTEGRATION_AVAILABLE = False

# Import market calendar
try:
    from ml_pipeline.market_calendar import MarketCalendar
    MARKET_CALENDAR_AVAILABLE = True
    market_calendar = MarketCalendar()
    logger.info("[CALENDAR] Market calendar initialized")
except ImportError as e:
    logger.warning(f"Market calendar not available: {e}")
    MARKET_CALENDAR_AVAILABLE = False
    market_calendar = None

# Import tax audit trail
try:
    from ml_pipeline.tax_audit_trail import TaxAuditTrail, TransactionType
    TAX_AUDIT_AVAILABLE = True
    logger.info("[TAX] Tax audit trail module available")
except ImportError as e:
    logger.warning(f"Tax audit trail not available: {e}")
    TAX_AUDIT_AVAILABLE = False

# Data fetching
try:
    from yahooquery import Ticker
    YAHOOQUERY_AVAILABLE = True
except ImportError:
    YAHOOQUERY_AVAILABLE = False

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


class PositionType(Enum):
    """Position type"""
    SWING = "swing"
    INTRADAY = "intraday"


class MarketSentiment(Enum):
    """Market sentiment levels"""
    VERY_BULLISH = "very_bullish"  # >70
    BULLISH = "bullish"            # 60-70
    NEUTRAL = "neutral"            # 40-60
    BEARISH = "bearish"            # 30-40
    VERY_BEARISH = "very_bearish"  # <30


@dataclass
class Position:
    """Trading position"""
    symbol: str
    position_type: str
    entry_date: str
    entry_price: float
    shares: int
    stop_loss: float
    trailing_stop: float
    profit_target: Optional[float]
    target_exit_date: Optional[str]
    current_price: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    entry_confidence: float
    regime: str
    
    def to_dict(self):
        return asdict(self)


class PaperTradingCoordinator:
    """
    Paper trading coordinator with swing + intraday integration
    """
    
    def __init__(
        self,
        symbols: List[str],
        initial_capital: float = 100000.0,
        config_file: str = "config/live_trading_config.json",
        use_real_swing_signals: bool = True
    ):
        """
        Initialize paper trading coordinator
        
        Args:
            symbols: List of symbols to trade
            initial_capital: Starting capital
            config_file: Path to configuration
            use_real_swing_signals: Use SwingSignalGenerator (True) or simplified (False)
        """
        self.symbols = symbols
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.use_real_swing_signals = use_real_swing_signals and ML_INTEGRATION_AVAILABLE
        
        # Load config
        self.config = self._load_config(config_file)
        
        # Initialize swing signal generator (REAL 70-75% win rate signals)
        if self.use_real_swing_signals:
            logger.info("[TARGET] Initializing REAL swing signal generator (70-75% win rate)")
            self.swing_signal_generator = SwingSignalGenerator(
                sentiment_weight=0.25,      # FinBERT
                lstm_weight=0.25,            # LSTM
                technical_weight=0.25,       # Technical
                momentum_weight=0.15,        # Momentum
                volume_weight=0.10,          # Volume
                confidence_threshold=self.config['swing_trading']['confidence_threshold'],
                use_multi_timeframe=self.config['swing_trading'].get('use_multi_timeframe', True),
                use_volatility_sizing=self.config['swing_trading'].get('use_volatility_sizing', True)
            )
        else:
            logger.info("[WARN]  Using simplified signal generation (50-60% win rate)")
            self.swing_signal_generator = None
        
        # Initialize monitoring system
        if ML_INTEGRATION_AVAILABLE:
            logger.info("[CHART] Initializing market monitoring system")
            (
                self.sentiment_monitor,
                self.intraday_scanner,
                self.cross_timeframe_coordinator
            ) = create_monitoring_system(
                scan_interval_minutes=self.config['intraday_monitoring']['scan_interval_minutes'],
                breakout_threshold=self.config['intraday_monitoring']['breakout_threshold']
            )
        else:
            self.sentiment_monitor = None
            self.intraday_scanner = None
            self.cross_timeframe_coordinator = None
        
        # State
        self.positions: Dict[str, Position] = {}
        self.closed_trades: List[Dict] = []
        self.session_start = datetime.now()
        self.last_market_sentiment = 50.0  # Neutral
        self.multi_market_breakdown = {}  # Store AU/US/UK sentiment breakdown
        
        # Performance tracking
        self.metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'max_drawdown': 0.0,
            'peak_capital': initial_capital
        }
        
        # Intraday monitoring state
        self.intraday_alerts = []
        self.last_intraday_scan = None
        
        # ML signals and decision tracking
        self.last_ml_signals = {}
        self.decision_history = []
        
        # Initialize tax audit trail
        if TAX_AUDIT_AVAILABLE:
            self.tax_audit = TaxAuditTrail(base_path="tax_records")
            logger.info("[TAX] Tax audit trail initialized")
        else:
            self.tax_audit = None
        
        # Initialize integrated sentiment analyzer (FinBERT v4.4.4)
        if SENTIMENT_INTEGRATION_AVAILABLE:
            self.sentiment_analyzer = get_sentiment_analyzer(use_finbert=True)
            logger.info("[SENTIMENT] FinBERT v4.4.4 sentiment integration enabled")
        else:
            self.sentiment_analyzer = None
            logger.warning("[SENTIMENT] Using fallback sentiment (SPY-based)")
        
        logger.info("=" * 80)
        logger.info("PAPER TRADING COORDINATOR - INTEGRATED VERSION")
        logger.info("=" * 80)
        logger.info(f"  Initial Capital: ${initial_capital:,.2f}")
        logger.info(f"  Symbols: {', '.join(symbols)}")
        logger.info(f"  Real Swing Signals: {self.use_real_swing_signals}")
        logger.info(f"  Expected Performance: {'70-75% win rate' if self.use_real_swing_signals else '50-60% win rate'}")
        logger.info(f"  Sentiment Integration: {'FinBERT v4.4.4' if SENTIMENT_INTEGRATION_AVAILABLE else 'Fallback (SPY)'}")
        logger.info("=" * 80)
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_file}, using defaults")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'swing_trading': {
                'holding_period_days': 5,
                'stop_loss_percent': 3.0,
                'confidence_threshold': 52.0,
                'max_position_size': 0.25,
                'use_trailing_stop': True,
                'use_profit_targets': True
            },
            'risk_management': {
                'max_total_positions': 3,
                'max_portfolio_heat': 0.06,
                'max_single_trade_risk': 0.02
            },
            'cross_timeframe': {
                'use_intraday_for_entries': True,
                'use_intraday_for_exits': True,
                'sentiment_boost_threshold': 70,
                'sentiment_block_threshold': 30,
                'early_exit_threshold': 80
            },
            'intraday_monitoring': {
                'scan_interval_minutes': 15,
                'breakout_threshold': 70.0
            }
        }
    
    # =========================================================================
    # DATA FETCHING
    # =========================================================================
    
    def fetch_market_data(self, symbol: str, period: str = "3mo") -> Optional[pd.DataFrame]:
        """
        Fetch market data for a symbol
        
        Args:
            symbol: Stock symbol
            period: Data period (1mo, 3mo, 6mo, 1y)
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            if YAHOOQUERY_AVAILABLE:
                ticker = Ticker(symbol)
                hist = ticker.history(period=period)
                
                if isinstance(hist, pd.DataFrame) and not hist.empty:
                    # Normalize columns
                    hist.columns = [col.capitalize() for col in hist.columns]
                    logger.info(f"[OK] Fetched {len(hist)} days of data for {symbol} (yahooquery)")
                    return hist
            
            if YFINANCE_AVAILABLE:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                
                if not hist.empty:
                    # Normalize columns
                    hist.columns = [col.capitalize() for col in hist.columns]
                    logger.info(f"[OK] Fetched {len(hist)} days of data for {symbol} (yfinance)")
                    return hist
            
            logger.warning(f"No data available for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def fetch_current_price(self, symbol: str) -> Optional[float]:
        """
        Fetch current price for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Current price or None
        """
        try:
            if YAHOOQUERY_AVAILABLE:
                ticker = Ticker(symbol)
                quote = ticker.price
                
                if isinstance(quote, dict) and symbol in quote:
                    price = quote[symbol].get('regularMarketPrice')
                    if price:
                        return float(price)
            
            if YFINANCE_AVAILABLE:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                
                if not hist.empty:
                    return float(hist['Close'].iloc[-1])
            
            logger.warning(f"Could not fetch current price for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {e}")
            return None
    
    # =========================================================================
    # MARKET SENTIMENT (Simulated)
    # =========================================================================
    
    def get_market_sentiment(self) -> float:
        """
        Get current GLOBAL market sentiment (0-100)
        
        **Enhanced in v1.3.15.46**: Multi-market aggregation (AU/US/UK)
        
        Weighting:
        - US Markets: 50% (dominant global influence)
        - UK Markets: 25% (bridge session between AU and US)
        - AU Markets: 25% (first to open in trading day)
        
        Priority:
        1. Multi-market sentiment from morning reports (FinBERT v4.4.4)
        2. Fallback to SPY-based sentiment
        
        Returns:
            Global weighted sentiment score (0-100)
        """
        # Try integrated sentiment first (FinBERT v4.4.4) - MULTI-MARKET
        if self.sentiment_analyzer:
            try:
                # Load all available morning reports
                sentiments = {}
                
                for market_code in ['au', 'us', 'uk']:
                    morning_data = self.sentiment_analyzer.load_morning_sentiment(market=market_code)
                    if morning_data:
                        sentiments[market_code] = {
                            'score': morning_data['overall_sentiment'],
                            'recommendation': morning_data['recommendation'],
                            'confidence': morning_data.get('confidence', 'MODERATE'),
                            'finbert': morning_data.get('finbert_sentiment', {})
                        }
                        logger.info(f"[SENTIMENT] {market_code.upper()}: {morning_data['overall_sentiment']:.1f}/100 "
                                   f"({morning_data['recommendation']})")
                
                # Calculate weighted global sentiment if we have multiple markets
                if len(sentiments) > 0:
                    # Define market weights (total = 1.0)
                    weights = {
                        'us': 0.50,  # US markets most influential
                        'uk': 0.25,  # UK/Europe bridge session
                        'au': 0.25   # AU/Asia first to open
                    }
                    
                    # Calculate weighted average
                    total_weight = 0
                    weighted_sentiment = 0
                    
                    for market_code, data in sentiments.items():
                        weight = weights.get(market_code, 0.25)
                        weighted_sentiment += data['score'] * weight
                        total_weight += weight
                    
                    # Normalize if not all markets available
                    if total_weight > 0:
                        global_sentiment = weighted_sentiment / total_weight
                    else:
                        global_sentiment = 50.0  # Neutral default
                    
                    # Store for decision making
                    self.last_market_sentiment = global_sentiment
                    self.multi_market_breakdown = sentiments
                    
                    # Use primary market's recommendation (US if available, else UK, else AU)
                    if 'us' in sentiments:
                        self.sentiment_recommendation = sentiments['us']['recommendation']
                        self.finbert_breakdown = sentiments['us']['finbert']
                    elif 'uk' in sentiments:
                        self.sentiment_recommendation = sentiments['uk']['recommendation']
                        self.finbert_breakdown = sentiments['uk']['finbert']
                    else:
                        self.sentiment_recommendation = sentiments['au']['recommendation']
                        self.finbert_breakdown = sentiments['au']['finbert']
                    
                    logger.info(f"[SENTIMENT] GLOBAL (weighted): {global_sentiment:.1f}/100")
                    logger.info(f"            Markets: {len(sentiments)}/3 available")
                    logger.info(f"            Breakdown: US={sentiments.get('us', {}).get('score', 'N/A')}, "
                               f"UK={sentiments.get('uk', {}).get('score', 'N/A')}, "
                               f"AU={sentiments.get('au', {}).get('score', 'N/A')}")
                    
                    return global_sentiment
                else:
                    logger.info("[SENTIMENT] No morning reports available, using SPY fallback")
                    
            except Exception as e:
                logger.warning(f"[SENTIMENT] Error loading morning reports: {e}, using SPY fallback")
        
        # Fallback to SPY-based sentiment (original logic)
        logger.debug("[SENTIMENT] Using SPY-based sentiment")
        
        try:
            # Fetch SPY (S&P 500) data
            spy_data = self.fetch_market_data('SPY', period='1mo')
            
            if spy_data is None or spy_data.empty:
                return 50.0  # Neutral default
            
            # Calculate sentiment based on price action
            last_close = spy_data['Close'].iloc[-1]
            prev_close = spy_data['Close'].iloc[-2]
            
            # Daily change
            daily_change = ((last_close - prev_close) / prev_close) * 100
            
            # 5-day trend
            if len(spy_data) >= 5:
                five_day_change = ((last_close - spy_data['Close'].iloc[-5]) / spy_data['Close'].iloc[-5]) * 100
            else:
                five_day_change = daily_change
            
            # 20-day MA
            if len(spy_data) >= 20:
                ma_20 = spy_data['Close'].rolling(20).mean().iloc[-1]
                ma_position = ((last_close - ma_20) / ma_20) * 100
            else:
                ma_position = 0
            
            # Calculate sentiment score
            sentiment = 50  # Neutral baseline
            
            # Daily momentum (±10 points)
            sentiment += daily_change * 3.33
            
            # 5-day trend (±15 points)
            sentiment += five_day_change * 3
            
            # MA position (±10 points)
            sentiment += ma_position * 5
            
            # Clamp to 0-100
            sentiment = max(0, min(100, sentiment))
            
            logger.info(f"[SENTIMENT] SPY-based: {sentiment:.1f}/100 (Daily: {daily_change:+.2f}%, 5-day: {five_day_change:+.2f}%)")
            
            self.last_market_sentiment = sentiment
            return sentiment
            
        except Exception as e:
            logger.error(f"Error calculating market sentiment: {e}")
            return 50.0  # Neutral default
    
    def classify_sentiment(self, sentiment: float) -> MarketSentiment:
        """Classify sentiment score"""
        if sentiment >= 70:
            return MarketSentiment.VERY_BULLISH
        elif sentiment >= 60:
            return MarketSentiment.BULLISH
        elif sentiment >= 40:
            return MarketSentiment.NEUTRAL
        elif sentiment >= 30:
            return MarketSentiment.BEARISH
        else:
            return MarketSentiment.VERY_BEARISH
    
    def should_allow_trade(self, symbol: str, signal: Dict, sentiment_score: float) -> Tuple[bool, float, str]:
        """
        Check if trade should be allowed based on FinBERT v4.4.4 sentiment gates
        
        **FIXED in v1.3.15.52**: Now returns position_multiplier for dynamic sizing
        **NEW in v1.3.15.45**: Respects negative sentiment from morning report
        
        Args:
            symbol: Stock symbol
            signal: Trading signal
            sentiment_score: Market sentiment (0-100)
        
        Returns:
            Tuple of (allow_trade, position_multiplier, reason)
            - allow_trade (bool): Whether to proceed with trade
            - position_multiplier (float): 0.0 to 1.5 for position sizing
            - reason (str): Explanation of decision
        """
        # Check if we have sentiment recommendation from morning report
        if hasattr(self, 'sentiment_recommendation'):
            recommendation = self.sentiment_recommendation
            
            # BLOCK on strong negative recommendations
            if recommendation in ['STRONG_SELL', 'AVOID']:
                reason = f"Market recommendation is {recommendation}"
                logger.warning(f"[BLOCK] {symbol}: {reason}")
                return False, 0.0, reason
            
            # BLOCK on SELL with low sentiment
            if recommendation == 'SELL' and sentiment_score < 35:
                reason = f"Bearish market (sentiment: {sentiment_score:.1f}/100, recommendation: {recommendation})"
                logger.warning(f"[BLOCK] {symbol}: {reason}")
                return False, 0.0, reason
            
            # CAUTION on low sentiment with HOLD/CAUTION
            if recommendation in ['CAUTION', 'HOLD'] and sentiment_score < 45:
                # Check FinBERT breakdown if available
                if hasattr(self, 'finbert_breakdown'):
                    scores = self.finbert_breakdown.get('overall_scores', {})
                    negative_pct = scores.get('negative', 0) * 100
                    
                    # Block if negative sentiment is very high (>60%)
                    if negative_pct > 60:
                        reason = f"High negative sentiment ({negative_pct:.1f}% negative)"
                        logger.warning(f"[BLOCK] {symbol}: {reason}")
                        return False, 0.0, reason
                    
                    # Reduce position if moderate negative
                    elif negative_pct > 45:
                        reason = f"Moderate negative sentiment ({negative_pct:.1f}% negative), REDUCE position"
                        logger.warning(f"[CAUTION] {symbol}: {reason}")
                        return True, 0.5, reason
        
        # Standard sentiment gates with position multipliers
        block_threshold = self.config.get('cross_timeframe', {}).get('sentiment_block_threshold', 30)
        if sentiment_score < block_threshold:
            reason = f"Sentiment too low ({sentiment_score:.1f} < {block_threshold})"
            logger.warning(f"[BLOCK] {symbol}: {reason}")
            return False, 0.0, reason
        
        # Check signal action
        if signal.get('action') not in ['BUY', 'STRONG_BUY']:
            return True, 1.0, "Signal not a buy"
        
        # Check confidence
        min_confidence = 52.0  # Default threshold
        confidence = signal.get('confidence', 0)
        if confidence < min_confidence:
            reason = f"Confidence {confidence:.1f}% < {min_confidence}%"
            logger.info(f"[SKIP] {symbol}: {reason}")
            return False, 0.0, reason
        
        # Calculate position multiplier based on sentiment score
        # This is the key fix: dynamically adjust position size based on market conditions
        if sentiment_score < 30:
            # Extreme bearish - BLOCK (already handled above)
            return False, 0.0, "Extreme bearish sentiment"
        elif sentiment_score < 45:
            # Bearish - REDUCE to 50%
            reason = f"Bearish sentiment ({sentiment_score:.1f}) - REDUCE position to 50%"
            logger.warning(f"[REDUCE] {symbol}: {reason}")
            return True, 0.5, reason
        elif sentiment_score < 55:
            # Slightly bearish/neutral - REDUCE to 75%
            reason = f"Neutral sentiment ({sentiment_score:.1f}) - REDUCE position to 75%"
            logger.info(f"[CAUTION] {symbol}: {reason}")
            return True, 0.75, reason
        elif sentiment_score < 65:
            # Normal bullish - Standard 100%
            reason = f"Normal sentiment ({sentiment_score:.1f}) - Standard position"
            logger.info(f"[ALLOW] {symbol}: {reason}")
            return True, 1.0, reason
        elif sentiment_score < 75:
            # Bullish - BOOST to 120%
            reason = f"Bullish sentiment ({sentiment_score:.1f}) - BOOST position to 120%"
            logger.info(f"[BOOST] {symbol}: {reason}")
            return True, 1.2, reason
        else:
            # Strong bullish - MAXIMUM BOOST to 150%
            reason = f"Strong bullish ({sentiment_score:.1f}) - MAXIMUM position 150%"
            logger.info(f"[MAXIMUM] {symbol}: {reason}")
            return True, 1.5, reason
    
    # =========================================================================
    # SIGNAL GENERATION (Simplified Phase 1-3)
    # =========================================================================
    
    def generate_swing_signal(self, symbol: str, price_data: pd.DataFrame) -> Dict:
        """
        Generate swing trading signal - INTEGRATED VERSION
        
        Uses SwingSignalGenerator if available, otherwise falls back to simplified version
        
        Args:
            symbol: Stock symbol
            price_data: Historical price data
            
        Returns:
            Signal dictionary with prediction and confidence
        """
        try:
            # Use REAL swing signal generator if enabled
            if self.use_real_swing_signals and self.swing_signal_generator is not None:
                logger.info(f"[TARGET] Generating REAL swing signal for {symbol}")
                
                # Fetch news data for sentiment analysis
                news_data = self._fetch_news_data(symbol)
                
                # Generate base signal using 5-component system
                base_signal = self.swing_signal_generator.generate_signal(
                    symbol=symbol,
                    price_data=price_data,
                    news_data=news_data
                )
                
                # Enhance with cross-timeframe coordination
                if self.cross_timeframe_coordinator:
                    enhanced_signal = self.cross_timeframe_coordinator.enhance_signal(
                        symbol=symbol,
                        base_signal=base_signal
                    )
                else:
                    enhanced_signal = base_signal
                
                # Extract components safely (handle None values)
                components = enhanced_signal.get('components', {})
                sentiment_val = components.get('sentiment', 0) if components.get('sentiment') is not None else 0
                lstm_val = components.get('lstm', 0) if components.get('lstm') is not None else 0
                technical_val = components.get('technical', 0) if components.get('technical') is not None else 0
                
                logger.info(
                    f"[OK] {symbol} Signal: {enhanced_signal['prediction']} "
                    f"(conf={enhanced_signal['confidence']:.2f}) | "
                    f"Components: Sentiment={sentiment_val:.3f}, "
                    f"LSTM={lstm_val:.3f}, "
                    f"Technical={technical_val:.3f}"
                )
                
                # Convert to format expected by rest of code
                return {
                    'prediction': 1 if enhanced_signal['prediction'] == 'BUY' else 0,
                    'confidence': enhanced_signal['confidence'] * 100,
                    'signal_strength': enhanced_signal['confidence'] * 100,
                    'components': enhanced_signal.get('components', {}),
                    'symbol': symbol
                }
            
            # FALLBACK: Use simplified signal generation
            logger.info(f"[WARN]  Using simplified signal for {symbol}")
            return self._generate_simplified_signal(symbol, price_data)
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return {'prediction': 0, 'confidence': 0, 'signal_strength': 0}
    
    def _generate_simplified_signal(self, symbol: str, price_data: pd.DataFrame) -> Dict:
        """
        Simplified signal generation (FALLBACK)
        
        This is the original simplified method - kept as fallback
        Only uses 4 components (no FinBERT, no LSTM)
        Expected: 50-60% win rate
        """
        try:
            if len(price_data) < 20:
                return {'prediction': 0, 'confidence': 0, 'signal_strength': 0}
            
            # Calculate indicators
            close = price_data['Close']
            volume = price_data['Volume']
            
            # 1. Price momentum (20-day ROC)
            momentum = ((close.iloc[-1] - close.iloc[-20]) / close.iloc[-20]) * 100
            
            # 2. Moving averages
            ma_10 = close.rolling(10).mean().iloc[-1]
            ma_20 = close.rolling(20).mean().iloc[-1]
            ma_50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else ma_20
            
            # 3. Volume surge
            avg_volume = volume.rolling(20).mean().iloc[-1]
            current_volume = volume.iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # 4. Volatility (simplified ATR)
            high = price_data['High']
            low = price_data['Low']
            tr = pd.concat([
                high - low,
                (high - close.shift()).abs(),
                (low - close.shift()).abs()
            ], axis=1).max(axis=1)
            atr = tr.rolling(14).mean().iloc[-1]
            atr_pct = (atr / close.iloc[-1]) * 100
            
            # Calculate signal components
            components = {}
            
            # Momentum score
            if momentum > 5:
                components['momentum'] = 0.75
            elif momentum > 0:
                components['momentum'] = 0.60
            elif momentum > -5:
                components['momentum'] = 0.40
            else:
                components['momentum'] = 0.25
            
            # Trend score
            if close.iloc[-1] > ma_10 > ma_20 > ma_50:
                components['trend'] = 0.80
            elif close.iloc[-1] > ma_10 > ma_20:
                components['trend'] = 0.65
            elif close.iloc[-1] > ma_20:
                components['trend'] = 0.55
            else:
                components['trend'] = 0.35
            
            # Volume score
            if volume_ratio > 2.0:
                components['volume'] = 0.75
            elif volume_ratio > 1.5:
                components['volume'] = 0.65
            elif volume_ratio > 1.0:
                components['volume'] = 0.55
            else:
                components['volume'] = 0.45
            
            # Volatility score (lower is better for swing trading)
            if atr_pct < 2.0:
                components['volatility'] = 0.70
            elif atr_pct < 3.0:
                components['volatility'] = 0.60
            elif atr_pct < 4.0:
                components['volatility'] = 0.50
            else:
                components['volatility'] = 0.40
            
            # Weighted combination (Phase 1-3 style)
            weights = {
                'momentum': 0.30,
                'trend': 0.35,
                'volume': 0.20,
                'volatility': 0.15
            }
            
            confidence = sum(components[k] * weights[k] for k in components) * 100
            
            # Prediction
            prediction = 1 if confidence >= 50 else 0
            
            signal = {
                'symbol': symbol,
                'prediction': prediction,
                'confidence': confidence,
                'signal_strength': confidence,
                'components': components,
                'metrics': {
                    'momentum_pct': momentum,
                    'volume_ratio': volume_ratio,
                    'atr_pct': atr_pct,
                    'price': close.iloc[-1],
                    'ma_10': ma_10,
                    'ma_20': ma_20
                }
            }
            
            logger.info(f"{symbol}: Signal confidence {confidence:.1f}% (Prediction: {'BUY' if prediction == 1 else 'HOLD'})")
            
            return signal
            
        except Exception as e:
            logger.error(f"Error in simplified signal generation for {symbol}: {e}")
            return {'prediction': 0, 'confidence': 0, 'signal_strength': 0}
    
    def _fetch_news_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Fetch recent news data for sentiment analysis
        
        Returns:
            DataFrame with news articles and sentiment, or None
        """
        try:
            # Try to fetch news from available sources
            if YAHOOQUERY_AVAILABLE:
                ticker = Ticker(symbol)
                
                # Check if news is a method or property
                news = ticker.news if callable(ticker.news) == False else None
                
                # Validate news data
                if news is not None and hasattr(news, '__len__') and len(news) > 0:
                    # Convert to DataFrame
                    news_df = pd.DataFrame(news)
                    if 'providerPublishTime' in news_df.columns:
                        news_df['timestamp'] = pd.to_datetime(news_df['providerPublishTime'], unit='s')
                        news_df.set_index('timestamp', inplace=True)
                    return news_df
            
            # Return None (SwingSignalGenerator will use other components)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return None
    
    # =========================================================================
    # POSITION MANAGEMENT
    # =========================================================================
    
    def evaluate_entry(self, symbol: str) -> Tuple[bool, float, Dict]:
        """
        Evaluate if we should enter a position - INTEGRATED VERSION
        
        Args:
            symbol: Stock symbol
            
        Returns:
            (should_enter, confidence, signal)
        """
        # Fetch data
        price_data = self.fetch_market_data(symbol, period="3mo")
        
        if price_data is None or price_data.empty:
            return False, 0, {}
        
        # Generate signal (uses SwingSignalGenerator if enabled)
        signal = self.generate_swing_signal(symbol, price_data)
        
        # Capture ML component signals for dashboard
        if signal and 'components' in signal:
            self.last_ml_signals = {
                'finbert_sentiment': signal['components'].get('sentiment_score', 0),
                'lstm_prediction': signal['components'].get('lstm_score', 0),
                'technical_analysis': signal['components'].get('technical_score', 0),
                'momentum': signal['components'].get('momentum_score', 0),
                'volume_analysis': signal['components'].get('volume_score', 0),
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol
            }
        
        confidence = signal.get('confidence', 0)
        prediction = signal.get('prediction', 0)
        
        # Check base threshold
        threshold = self.config['swing_trading']['confidence_threshold']
        
        if confidence < threshold:
            return False, confidence, signal
        
        # Evaluate entry with intraday context
        signal = self.evaluate_entry_with_intraday(symbol, signal)
        
        if signal is None:
            return False, confidence, {}
        
        # Update confidence from enhanced signal
        confidence = signal.get('confidence', confidence)
        
        # Check if we have room for more positions
        max_positions = self.config['risk_management']['max_total_positions']
        if len(self.positions) >= max_positions:
            logger.warning(f"{symbol}: Max positions ({max_positions}) reached")
            return False, confidence, signal
        
        # Check if already holding
        if symbol in self.positions:
            return False, confidence, signal
        
        should_enter = prediction == 1 and confidence >= threshold
        
        return should_enter, confidence, signal
    
    def evaluate_entry_with_intraday(self, symbol: str, signal: Dict) -> Optional[Dict]:
        """
        Evaluate entry decision with intraday context
        
        This method applies cross-timeframe logic:
        - Block entries when market sentiment < 30
        - Boost positions when market sentiment > 70
        - Adjust position size based on intraday context
        
        Args:
            symbol: Stock symbol
            signal: Base signal from generate_swing_signal()
        
        Returns:
            Modified signal or None if entry blocked
        """
        try:
            # Get current market sentiment
            if self.sentiment_monitor:
                sentiment_reading = self.sentiment_monitor.get_current_sentiment()
                self.last_market_sentiment = sentiment_reading.sentiment_score
            else:
                sentiment_reading = None
                # Update from SPY-based calculation
                self.get_market_sentiment()
            
            # Check if entry should be blocked
            block_threshold = self.config['cross_timeframe'].get('sentiment_block_threshold', 30)
            if self.last_market_sentiment < block_threshold:
                logger.warning(
                    f"[ERROR] BLOCKED entry for {symbol} - "
                    f"Market sentiment {self.last_market_sentiment:.1f} < {block_threshold}"
                )
                return None
            
            # Check if position should be boosted
            boost_threshold = self.config['cross_timeframe'].get('sentiment_boost_threshold', 70)
            if self.last_market_sentiment > boost_threshold:
                # Boost confidence
                signal['confidence'] = min(100, signal['confidence'] + 5)
                
                logger.info(
                    f"[=>] BOOSTED entry for {symbol} - "
                    f"Market sentiment {self.last_market_sentiment:.1f} > {boost_threshold}"
                )
            
            return signal
            
        except Exception as e:
            logger.error(f"Error evaluating entry for {symbol}: {e}")
            return signal
    
    def enter_position(self, symbol: str, signal: Dict) -> bool:
        """
        Enter a new swing position (paper trade)
        
        Args:
            symbol: Stock symbol
            signal: Signal dictionary
            
        Returns:
            True if position entered successfully
        """
        try:
            # MARKET HOURS CHECK - Don't trade on closed markets (unless manual override)
            if not signal.get('type') == 'MANUAL' and MARKET_CALENDAR_AVAILABLE and market_calendar:
                can_trade, reason = market_calendar.can_trade_symbol(symbol)
                if not can_trade:
                    logger.warning(f"{symbol}: TRADE BLOCKED - Market closed ({reason})")
                    return False
            
            # SENTIMENT GATE CHECK - Block trades based on FinBERT sentiment
            if not signal.get('type') == 'MANUAL':  # Don't block manual trades
                gate, position_multiplier, reason = self.should_allow_trade(symbol, signal, self.last_market_sentiment)
                
                # gate is boolean: True = allow, False = block
                if not gate:
                    logger.warning(f"{symbol}: TRADE BLOCKED - {reason}")
                    logger.warning(f"  → Market Sentiment: {self.last_market_sentiment:.1f}/100")
                    return False
                
                # Log position sizing adjustment
                if position_multiplier < 1.0:
                    logger.info(f"{symbol}: Position REDUCED to {position_multiplier*100:.0f}% - {reason}")
                elif position_multiplier > 1.0:
                    logger.info(f"{symbol}: Position BOOSTED to {position_multiplier*100:.0f}% - {reason}")
                else:
                    logger.info(f"{symbol}: Standard position sizing - {reason}")
            
            # Get current price
            current_price = self.fetch_current_price(symbol)
            
            if current_price is None:
                logger.error(f"{symbol}: Could not fetch current price")
                return False
            
            # Determine position size
            # Check if this is a manual trade with custom shares
            if signal.get('type') == 'MANUAL' and 'shares' in signal:
                # Use manual shares
                shares = int(signal['shares'])
                logger.info(f"{symbol}: Manual trade with {shares} shares specified")
            else:
                # Calculate shares automatically
                base_size = self.config['swing_trading']['max_position_size']
                
                # Apply sentiment-based position multiplier
                gate, position_multiplier, reason = self.should_allow_trade(symbol, signal, self.last_market_sentiment)
                position_size = base_size * position_multiplier
                
                if position_multiplier != 1.0:
                    logger.info(f"{symbol}: Position size adjusted to {position_size:.1%} (multiplier: {position_multiplier:.2f})")
                
                # Calculate shares
                position_value = self.current_capital * position_size
                shares = int(position_value / current_price)
            
            if shares < 1:
                logger.warning(f"{symbol}: Insufficient capital for 1 share")
                return False
            
            # Calculate stops and targets
            # Check for manual values first
            if signal.get('type') == 'MANUAL':
                # Use manual stop loss and take profit if provided
                stop_loss = signal.get('stop_loss', current_price * 0.95)
                profit_target = signal.get('take_profit')
                logger.info(f"{symbol}: Using manual stop_loss=${stop_loss:.2f}, take_profit=${profit_target:.2f if profit_target else 'None'}")
            else:
                # Calculate automatically
                stop_loss_pct = self.config['swing_trading']['stop_loss_percent']
                stop_loss = current_price * (1 - stop_loss_pct / 100)
                # Profit target (Phase 1)
                profit_target = current_price * 1.08 if self.config['swing_trading']['use_profit_targets'] else None
            
            trailing_stop = stop_loss
            
            # Target exit date (Phase 2 - adaptive)
            holding_days = self._calculate_holding_period(signal)
            target_exit_date = (datetime.now() + timedelta(days=holding_days)).isoformat()
            
            # Determine regime
            regime = self._determine_regime(signal)
            
            # Calculate cost
            cost = shares * current_price
            commission = cost * 0.001  # 0.1%
            total_cost = cost + commission
            
            # Update capital
            self.current_capital -= total_cost
            
            # Create position
            position = Position(
                symbol=symbol,
                position_type=PositionType.SWING.value,
                entry_date=datetime.now().isoformat(),
                entry_price=current_price,
                shares=shares,
                stop_loss=stop_loss,
                trailing_stop=trailing_stop,
                profit_target=profit_target,
                target_exit_date=target_exit_date,
                current_price=current_price,
                unrealized_pnl=0.0,
                unrealized_pnl_pct=0.0,
                entry_confidence=signal.get('confidence', 0),
                regime=regime
            )
            
            self.positions[symbol] = position
            
            # Record BUY transaction for tax purposes
            if self.tax_audit:
                try:
                    self.tax_audit.record_transaction(
                        symbol=symbol,
                        transaction_type=TransactionType.BUY,
                        quantity=shares,
                        price=current_price,
                        brokerage=commission,
                        transaction_date=datetime.now()
                    )
                    logger.info(f"[TAX] BUY transaction recorded for {symbol}")
                except Exception as e:
                    logger.error(f"[TAX] Failed to record BUY: {e}")
            
            logger.info(f"[OK] POSITION OPENED: {symbol}")
            logger.info(f"  Shares: {shares} @ ${current_price:.2f}")
            logger.info(f"  Position Size: {position_size:.1%} (${cost:,.2f})")
            logger.info(f"  Stop Loss: ${stop_loss:.2f} (-{stop_loss_pct}%)")
            logger.info(f"  Profit Target: ${profit_target:.2f} (+8%)" if profit_target else "  No Profit Target")
            logger.info(f"  Target Exit: {holding_days} days")
            logger.info(f"  Regime: {regime}")
            logger.info(f"  Capital Remaining: ${self.current_capital:,.2f}")
            
            # Log decision for dashboard
            self._log_trading_decision(
                action='BUY',
                symbol=symbol,
                confidence=signal.get('confidence', 0),
                reason=f"ML signal: {signal.get('confidence', 0):.0f}% confidence, Regime: {regime}",
                price=current_price,
                shares=shares
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error entering position for {symbol}: {e}")
            return False
    
    def _calculate_holding_period(self, signal: Dict) -> int:
        """Calculate adaptive holding period (3-15 days)"""
        base_holding = 5
        confidence = signal.get('confidence', 50)
        
        if confidence > 70:
            return min(15, base_holding + 3)
        elif confidence < 55:
            return max(3, base_holding - 2)
        
        return base_holding
    
    def _determine_regime(self, signal: Dict) -> str:
        """Determine market regime"""
        sentiment = self.last_market_sentiment
        
        if sentiment >= 70:
            return "STRONG_UPTREND"
        elif sentiment >= 60:
            return "MILD_UPTREND"
        elif sentiment >= 40:
            return "RANGING"
        else:
            return "DOWNTREND"
    
    def _log_trading_decision(self, action: str, symbol: str, confidence: float, 
                               reason: str, price: float = None, shares: int = None):
        """Log trading decision for dashboard display"""
        decision = {
            'action': action,
            'symbol': symbol,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'price': price,
            'shares': shares
        }
        
        # Keep last 50 decisions
        self.decision_history.append(decision)
        if len(self.decision_history) > 50:
            self.decision_history = self.decision_history[-50:]
    
    def update_positions(self):
        """Update all open positions with current prices"""
        for symbol, position in list(self.positions.items()):
            current_price = self.fetch_current_price(symbol)
            
            if current_price:
                position.current_price = current_price
                position.unrealized_pnl = (current_price - position.entry_price) * position.shares
                position.unrealized_pnl_pct = ((current_price - position.entry_price) / position.entry_price) * 100
                
                # Update trailing stop
                if self.config['swing_trading']['use_trailing_stop']:
                    self._update_trailing_stop(position, current_price)
    
    def _update_trailing_stop(self, position: Position, current_price: float):
        """Update trailing stop"""
        stop_loss_pct = self.config['swing_trading']['stop_loss_percent']
        
        if current_price > position.entry_price:
            new_trailing = current_price * (1 - stop_loss_pct / 100)
            
            if new_trailing > position.trailing_stop:
                logger.info(f"{position.symbol}: Trailing stop ${position.trailing_stop:.2f} → ${new_trailing:.2f}")
                position.trailing_stop = new_trailing
    
    def check_exits(self) -> List[Tuple[str, str]]:
        """Check all positions for exit conditions"""
        exits = []
        
        for symbol, position in self.positions.items():
            exit_reason = self._check_exit_conditions(position)
            
            if exit_reason:
                exits.append((symbol, exit_reason))
        
        return exits
    
    def _check_exit_conditions(self, position: Position) -> Optional[str]:
        """Check if position should be exited"""
        price = position.current_price
        
        # Stop loss
        if price <= position.stop_loss:
            return "STOP_LOSS"
        
        # Trailing stop
        if price <= position.trailing_stop:
            return "TRAILING_STOP"
        
        # Profit target
        if position.profit_target and price >= position.profit_target:
            holding_days = (datetime.now() - datetime.fromisoformat(position.entry_date)).days
            if holding_days >= 2:
                return "PROFIT_TARGET_8%"
            elif price >= position.entry_price * 1.12:
                return "QUICK_PROFIT_12%"
        
        # Target exit date
        if position.target_exit_date:
            if datetime.now() >= datetime.fromisoformat(position.target_exit_date):
                holding_days = (datetime.now() - datetime.fromisoformat(position.entry_date)).days
                return f"TARGET_EXIT_{holding_days}d"
        
        # Intraday breakdown early exit
        if self.config['cross_timeframe']['use_intraday_for_exits']:
            if self.last_market_sentiment < 20 and position.unrealized_pnl_pct > 0:
                return "INTRADAY_BREAKDOWN"
        
        return None
    
    def exit_position(self, symbol: str, exit_reason: str) -> bool:
        """Exit a position (paper trade)"""
        if symbol not in self.positions:
            return False
        
        try:
            position = self.positions[symbol]
            exit_price = position.current_price
            
            # Calculate P&L
            proceeds = position.shares * exit_price
            commission = proceeds * 0.001
            net_proceeds = proceeds - commission
            
            cost = position.shares * position.entry_price
            pnl = net_proceeds - cost
            pnl_pct = (pnl / cost) * 100
            
            # Update capital
            self.current_capital += net_proceeds
            
            # Update metrics
            self.metrics['total_trades'] += 1
            self.metrics['total_pnl'] += pnl
            
            if pnl > 0:
                self.metrics['winning_trades'] += 1
            else:
                self.metrics['losing_trades'] += 1
            
            # Track drawdown
            if self.current_capital > self.metrics['peak_capital']:
                self.metrics['peak_capital'] = self.current_capital
            
            drawdown = (self.metrics['peak_capital'] - self.current_capital) / self.metrics['peak_capital']
            if drawdown > self.metrics['max_drawdown']:
                self.metrics['max_drawdown'] = drawdown
            
            # Record trade
            holding_days = (datetime.now() - datetime.fromisoformat(position.entry_date)).days
            trade_record = {
                'symbol': symbol,
                'entry_date': position.entry_date,
                'exit_date': datetime.now().isoformat(),
                'holding_days': holding_days,
                'entry_price': position.entry_price,
                'exit_price': exit_price,
                'shares': position.shares,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'exit_reason': exit_reason,
                'entry_confidence': position.entry_confidence
            }
            
            self.closed_trades.append(trade_record)
            
            # Record SELL transaction for tax purposes
            if self.tax_audit:
                try:
                    self.tax_audit.record_transaction(
                        symbol=symbol,
                        transaction_type=TransactionType.SELL,
                        quantity=position.shares,
                        price=exit_price,
                        brokerage=commission,
                        transaction_date=datetime.now()
                    )
                    logger.info(f"[TAX] SELL transaction recorded for {symbol}")
                except Exception as e:
                    logger.error(f"[TAX] Failed to record SELL: {e}")
            
            # Remove position
            del self.positions[symbol]
            
            logger.info(f"[OK] POSITION CLOSED: {symbol}")
            logger.info(f"  Reason: {exit_reason}")
            logger.info(f"  Holding: {holding_days} days")
            logger.info(f"  Entry: ${position.entry_price:.2f} → Exit: ${exit_price:.2f}")
            logger.info(f"  P&L: ${pnl:+,.2f} ({pnl_pct:+.2f}%)")
            logger.info(f"  Capital: ${self.current_capital:,.2f}")
            
            # Log decision for dashboard
            self._log_trading_decision(
                action='SELL',
                symbol=symbol,
                confidence=100.0 if pnl > 0 else 0.0,
                reason=f"{exit_reason} - P&L: {pnl_pct:+.2f}%, Held {holding_days} days",
                price=exit_price,
                shares=position.shares
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error exiting position {symbol}: {e}")
            return False
    
    # =========================================================================
    # INTRADAY MONITORING (Simplified)
    # =========================================================================
    
    def run_intraday_scan(self):
        """Run intraday monitoring scan"""
        try:
            self.last_intraday_scan = datetime.now()
            
            # Update market sentiment
            sentiment = self.get_market_sentiment()
            sentiment_class = self.classify_sentiment(sentiment)
            
            logger.info(f"Intraday Scan: Market sentiment = {sentiment:.1f} ({sentiment_class.value})")
            
            # Check for breakout alerts
            for symbol in self.symbols:
                # Fetch recent data
                data = self.fetch_market_data(symbol, period="5d")
                
                if data is None or len(data) < 2:
                    continue
                
                # Simple breakout detection
                current_price = data['Close'].iloc[-1]
                prev_close = data['Close'].iloc[-2]
                change_pct = ((current_price - prev_close) / prev_close) * 100
                
                # Volume surge
                current_volume = data['Volume'].iloc[-1]
                avg_volume = data['Volume'].rolling(5).mean().iloc[-1]
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                
                # Alert on strong moves
                threshold = self.config['intraday_monitoring']['breakout_threshold']
                
                if abs(change_pct) > 2.0 and volume_ratio > 1.5:
                    breakout_strength = min(100, abs(change_pct) * 10 + (volume_ratio - 1) * 20)
                    
                    if breakout_strength > threshold:
                        alert = {
                            'timestamp': datetime.now().isoformat(),
                            'symbol': symbol,
                            'type': 'BULLISH_BREAKOUT' if change_pct > 0 else 'BEARISH_BREAKDOWN',
                            'strength': breakout_strength,
                            'price_change_pct': change_pct,
                            'volume_ratio': volume_ratio,
                            'current_price': current_price
                        }
                        
                        self.intraday_alerts.append(alert)
                        
                        logger.info(f"[WARN]  INTRADAY ALERT: {symbol}")
                        logger.info(f"    Type: {alert['type']}")
                        logger.info(f"    Strength: {breakout_strength:.1f}")
                        logger.info(f"    Price Change: {change_pct:+.2f}%")
                        logger.info(f"    Volume Ratio: {volume_ratio:.2f}x")
            
        except Exception as e:
            logger.error(f"Error in intraday scan: {e}")
    
    # =========================================================================
    # MAIN LOOP
    # =========================================================================
    
    def run_trading_cycle(self):
        """Run one complete trading cycle - INTEGRATED VERSION"""
        try:
            logger.info(f"\n{'='*80}")
            logger.info(f"Trading Cycle: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"{'='*80}")
            
                # Check market hours for all symbols and filter to only open markets
            open_symbols = []
            closed_symbols = []
            
            if MARKET_CALENDAR_AVAILABLE and market_calendar:
                for symbol in self.symbols:
                    can_trade, reason = market_calendar.can_trade_symbol(symbol)
                    if can_trade:
                        open_symbols.append(symbol)
                    else:
                        closed_symbols.append(f"{symbol} ({reason})")
                
                if closed_symbols:
                    logger.warning(f"[CALENDAR] Some markets are closed:")
                    for msg in closed_symbols:
                        logger.warning(f"   {msg}")
                    logger.info(f"[CALENDAR] Trading only on open markets: {len(open_symbols)} of {len(self.symbols)} symbols")
            else:
                # If calendar not available, allow all symbols
                open_symbols = self.symbols.copy()
            
                # 1. Update market sentiment
            if self.sentiment_monitor:
                logger.info("[CHART] Updating market sentiment...")
                sentiment_reading = self.sentiment_monitor.get_current_sentiment()
                self.last_market_sentiment = sentiment_reading.sentiment_score
                logger.info(f"   Market Sentiment: {sentiment_reading.sentiment_score:.1f} ({sentiment_reading.sentiment_class.value})")
            else:
                self.get_market_sentiment()
            
                # 2. Run intraday scan (every 15 minutes)
            if self._should_run_intraday_scan():
                if self.intraday_scanner:
                    logger.info("🔍 Running intraday scan...")
                    alerts = self.intraday_scanner.scan_for_opportunities(
                        symbols=self.symbols,
                        price_data_provider=self.fetch_market_data
                    )
                    self.last_intraday_scan = datetime.now()
                    
                    if alerts:
                        logger.info(f"   Found {len(alerts)} intraday alerts")
                        for alert in alerts:
                            logger.info(f"   🚨 {alert.symbol}: {alert.alert_type} (strength={alert.signal_strength:.1f})")
                else:
                    self.run_intraday_scan()
            
                # 3. Update existing positions
            self.update_positions()
            
                # 4. Check for early exits (intraday breakdowns)
            if self.positions and self.cross_timeframe_coordinator:
                logger.info("[WARN]  Checking for early exits...")
                for symbol in list(self.positions.keys()):
                    position = self.positions[symbol]
                    
                    # Check for intraday breakdown
                    exit_reason = self.cross_timeframe_coordinator.check_early_exit(symbol, position.to_dict())
                    
                    if exit_reason:
                        logger.warning(f"   Early exit triggered for {symbol}: {exit_reason}")
                        current_price = self.fetch_current_price(symbol)
                        if current_price:
                            position.current_price = current_price
                            self.exit_position(symbol, exit_reason)
            
                # 5. Check regular exits
            exits = self.check_exits()
            for symbol, reason in exits:
                self.exit_position(symbol, reason)
            
                # 6. Look for new entries (only on open markets)
            if len(self.positions) < self.config['risk_management']['max_total_positions']:
                logger.info("🔎 Scanning for new entry opportunities...")
                
                for symbol in open_symbols:  # Only check symbols where market is open
                    if symbol in self.positions:
                        continue
                    
                    should_enter, confidence, signal = self.evaluate_entry(symbol)
                    
                    if should_enter:
                        logger.info(f"[OK] Entry signal for {symbol} - confidence {confidence:.2f}")
                        self.enter_position(symbol, signal)
            
            # 7. Print status
            self.print_status()
            
        except Exception as e:
            logger.error(f"[ERROR] Exception in trading cycle: {e}")
            logger.error(f"[ERROR] Traceback: ", exc_info=True)
            logger.warning(f"[WARN] Trading cycle failed but loop will continue")
            # Don't re-raise - let the loop continue
    
    def run_single_cycle(self):
        """Alias for run_trading_cycle() for compatibility"""
        return self.run_trading_cycle()
    
    def _should_run_intraday_scan(self) -> bool:
        """Check if it's time to run intraday scan"""
        if self.last_intraday_scan is None:
            return True
        
        scan_interval = self.config['intraday_monitoring']['scan_interval_minutes']
        elapsed_minutes = (datetime.now() - self.last_intraday_scan).total_seconds() / 60
        
        return elapsed_minutes >= scan_interval
    
    def print_status(self):
        """Print current portfolio status"""
        total_invested = sum(p.shares * p.entry_price for p in self.positions.values())
        total_value = sum(p.shares * p.current_price for p in self.positions.values())
        total_unrealized_pnl = sum(p.unrealized_pnl for p in self.positions.values())
        
        total_capital = self.current_capital + total_value
        total_return = ((total_capital - self.initial_capital) / self.initial_capital) * 100
        
        win_rate = (self.metrics['winning_trades'] / self.metrics['total_trades'] * 100) if self.metrics['total_trades'] > 0 else 0
        
        logger.info(f"\n{'='*80}")
        logger.info(f"PORTFOLIO STATUS")
        logger.info(f"{'='*80}")
        logger.info(f"Total Capital: ${total_capital:,.2f} ({total_return:+.2f}%)")
        logger.info(f"  Cash: ${self.current_capital:,.2f}")
        logger.info(f"  Invested: ${total_value:,.2f}")
        logger.info(f"  Unrealized P&L: ${total_unrealized_pnl:+,.2f}")
        logger.info(f"")
        logger.info(f"Open Positions: {len(self.positions)}")
        for symbol, pos in self.positions.items():
            logger.info(f"  {symbol}: {pos.shares} shares @ ${pos.entry_price:.2f} | "
                       f"Current: ${pos.current_price:.2f} | P&L: {pos.unrealized_pnl_pct:+.2f}%")
        logger.info(f"")
        logger.info(f"Performance:")
        logger.info(f"  Total Trades: {self.metrics['total_trades']}")
        logger.info(f"  Win Rate: {win_rate:.1f}%")
        logger.info(f"  Realized P&L: ${self.metrics['total_pnl']:+,.2f}")
        logger.info(f"  Max Drawdown: {self.metrics['max_drawdown']*100:.2f}%")
        logger.info(f"")
        logger.info(f"Market Sentiment: {self.last_market_sentiment:.1f}/100")
        logger.info(f"Intraday Alerts (last hour): {len([a for a in self.intraday_alerts if (datetime.now() - datetime.fromisoformat(a['timestamp'])).seconds < 3600])}")
        logger.info(f"{'='*80}\n")
    
    def get_status_dict(self) -> Dict:
        """Get status as dictionary for dashboard"""
        total_invested = sum(p.shares * p.entry_price for p in self.positions.values())
        total_value = sum(p.shares * p.current_price for p in self.positions.values())
        total_unrealized_pnl = sum(p.unrealized_pnl for p in self.positions.values())
        total_capital = self.current_capital + total_value
        total_return = ((total_capital - self.initial_capital) / self.initial_capital) * 100
        win_rate = (self.metrics['winning_trades'] / self.metrics['total_trades'] * 100) if self.metrics['total_trades'] > 0 else 0
        
        # Get ML signals if available
        ml_signals = {}
        if hasattr(self, 'last_ml_signals') and self.last_ml_signals:
            ml_signals = self.last_ml_signals
        
        # Get latest decisions
        latest_decisions = []
        if hasattr(self, 'decision_history'):
            latest_decisions = self.decision_history[-10:]  # Last 10 decisions
        
        return {
            'timestamp': datetime.now().isoformat(),
            'symbols': self.symbols,  # Add tracked symbols
            'capital': {
                'total': total_capital,
                'cash': self.current_capital,
                'invested': total_value,
                'initial': self.initial_capital,
                'total_return_pct': total_return
            },
            'positions': {
                'count': len(self.positions),
                'open': [p.to_dict() for p in self.positions.values()],
                'unrealized_pnl': total_unrealized_pnl
            },
            'performance': {
                'total_trades': self.metrics['total_trades'],
                'winning_trades': self.metrics['winning_trades'],
                'losing_trades': self.metrics['losing_trades'],
                'win_rate': win_rate,
                'realized_pnl': self.metrics['total_pnl'],
                'max_drawdown': self.metrics['max_drawdown'] * 100
            },
            'market': {
                'sentiment': self.last_market_sentiment,
                'sentiment_class': self.classify_sentiment(self.last_market_sentiment).value,
                'breakdown': getattr(self, 'multi_market_breakdown', {}),  # Market-specific scores
                'source': 'global' if hasattr(self, 'multi_market_breakdown') and len(getattr(self, 'multi_market_breakdown', {})) > 1 else 'single'
            },
            'ml_signals': ml_signals,
            'latest_decisions': latest_decisions,
            'intraday_alerts': self.intraday_alerts[-10:],  # Last 10 alerts
            'closed_trades': self.closed_trades[-20:]  # Last 20 trades
        }
    
    # =========================================================================
    # TAX REPORTING
    # =========================================================================
    
    def generate_tax_report(self, financial_year: str = None) -> Optional[str]:
        """
        Generate ATO-compliant tax report
        
        Args:
            financial_year: Financial year (e.g., '2026-27'), defaults to current
            
        Returns:
            Path to generated report or None
        """
        if not self.tax_audit:
            logger.warning("[TAX] Tax audit trail not available")
            return None
        
        try:
            report_path = self.tax_audit.generate_ato_report(financial_year)
            logger.info(f"[TAX] Tax report generated: {report_path}")
            return report_path
        except Exception as e:
            logger.error(f"[TAX] Failed to generate tax report: {e}")
            return None
    
    def export_tax_records(self, financial_year: str = None, format: str = 'csv') -> Optional[str]:
        """
        Export tax records to CSV
        
        Args:
            financial_year: Financial year (e.g., '2026-27'), defaults to current
            format: Export format ('csv' or 'json')
            
        Returns:
            Path to exported file or None
        """
        if not self.tax_audit:
            logger.warning("[TAX] Tax audit trail not available")
            return None
        
        try:
            export_path = self.tax_audit.export_transactions(financial_year, format)
            logger.info(f"[TAX] Transactions exported: {export_path}")
            return export_path
        except Exception as e:
            logger.error(f"[TAX] Failed to export transactions: {e}")
            return None
    
    def get_tax_summary(self, financial_year: str = None) -> Optional[Dict]:
        """
        Get tax summary for a financial year
        
        Args:
            financial_year: Financial year (e.g., '2026-27'), defaults to current
            
        Returns:
            Tax summary dictionary or None
        """
        if not self.tax_audit:
            logger.warning("[TAX] Tax audit trail not available")
            return None
        
        try:
            summary = self.tax_audit.get_financial_year_summary(financial_year)
            return summary
        except Exception as e:
            logger.error(f"[TAX] Failed to get tax summary: {e}")
            return None
    
    def save_state(self, filepath: str = "state/paper_trading_state.json"):
        """Save current state with atomic write (ATOMIC_WRITE_v85)"""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            state = self.get_status_dict()
            
            # Add metadata
            state['last_update'] = datetime.now().isoformat()
            state['state_version'] = 2
            
            # Atomic write: temp file + rename
            temp_path = Path(filepath).with_suffix('.tmp')
            
            with open(temp_path, 'w') as f:
                json.dump(state, f, indent=2)
            
            # Verify write
            if temp_path.stat().st_size == 0:
                raise ValueError("Written state file is empty!")
            
            # Atomic rename
            temp_path.replace(filepath)
            
            logger.info(f"State saved to {filepath} ({Path(filepath).stat().st_size} bytes)")
            
        except Exception as e:
            logger.error(f"Error saving state: {e}")
            if temp_path.exists():
                temp_path.unlink()
    
    def run_cycle(self):
        """Run a single trading cycle (for unified dashboard)"""
        self.run_trading_cycle()
    
    def run(self, cycles: int = None, interval: int = 300):
        """
        Run paper trading system
        
        Args:
            cycles: Number of cycles to run (None = infinite)
            interval: Seconds between cycles
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"PAPER TRADING SYSTEM STARTED")
        logger.info(f"{'='*80}")
        logger.info(f"Symbols: {', '.join(self.symbols)}")
        logger.info(f"Initial Capital: ${self.initial_capital:,.2f}")
        logger.info(f"Cycle Interval: {interval}s")
        logger.info(f"{'='*80}\n")
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                
                if cycles and cycle_count > cycles:
                    break
                
                self.run_trading_cycle()
                
                # Save state
                self.save_state()
                
                # Wait for next cycle
                if cycles is None or cycle_count < cycles:
                    logger.info(f"Next cycle in {interval}s...\n")
                    time.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("\nShutting down gracefully...")
            self.save_state()
            self.print_status()
            logger.info("[OK] Paper trading stopped")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Paper Trading System with Intraday Integration')
    parser.add_argument('--symbols', type=str, default='AAPL,GOOGL,MSFT',
                       help='Comma-separated list of symbols to trade')
    parser.add_argument('--capital', type=float, default=100000.0,
                       help='Initial capital')
    parser.add_argument('--config', type=str, default='config/live_trading_config.json',
                       help='Configuration file path')
    parser.add_argument('--cycles', type=int, default=None,
                       help='Number of trading cycles (default: infinite)')
    parser.add_argument('--interval', type=int, default=300,
                       help='Seconds between cycles (default: 300)')
    parser.add_argument('--real-signals', action='store_true',
                       help='Use real SwingSignalGenerator (70-75%% win rate)')
    parser.add_argument('--simplified', action='store_true',
                       help='Use simplified signals (50-60%% win rate)')
    
    args = parser.parse_args()
    
    # Determine signal mode
    use_real_signals = args.real_signals or not args.simplified  # Default to real signals
    
    # Parse symbols
    symbols = [s.strip() for s in args.symbols.split(',')]
    
    # Create logs directory
    Path('logs').mkdir(exist_ok=True)
    Path('state').mkdir(exist_ok=True)
    
    # Initialize coordinator
    coordinator = PaperTradingCoordinator(
        symbols=symbols,
        initial_capital=args.capital,
        config_file=args.config,
        use_real_swing_signals=use_real_signals
    )
    
    # Run
    coordinator.run(cycles=args.cycles, interval=args.interval)


if __name__ == '__main__':
    main()
