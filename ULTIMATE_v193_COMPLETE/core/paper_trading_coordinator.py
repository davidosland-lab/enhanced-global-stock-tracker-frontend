"""
Paper Trading Coordinator - Phase 3 Intraday Integration
=========================================================
VERSION: v1.3.15.193.10 - Macro Risk Gates Integration (Mar 4, 2026)

CHANGELOG v193.10:
- NEW: Macro Risk Gatekeeper fully integrated into trading decisions
  * World Risk >=80 blocks trades, >=60 reduces position 50%
  * US market <=-1.5% blocks, <=-0.75% reduces 25%
  * VIX >=30 requires 70%+ confidence and reduces 25%
  * Financial sector stricter: Block if World Risk >=60 or US <=-1.0%
- NEW: FinBERT sentiment fallback to macro sentiment when neutral
- NEW: Confidence penalty system for missing data
  * LSTM missing: -20% confidence penalty
  * Sentiment missing: -15% confidence penalty
  * Volume missing: -10% confidence penalty
- FIXED: March 4, 2026 incident (USD556 loss) - macro gates now active
  * Would have blocked BP.L, BOQ.AX, NAB.AX on high risk day
  * World Risk 100/100, US -2.5%, VIX 59.3 -> All blocked
- Position multipliers now combine macro risk AND sentiment
  * Example: Macro 0.5x * Sentiment 0.75x = 0.375x final position
- Applies to ALL markets: AU, US, UK with same gates

Previous v184:
- NEW: ML-based SELL signals using same 5-component system as BUY signals
  (FinBERT + LSTM + Technical + Momentum + Volume = 70-75% accuracy)
- Intelligent exit timing: ML detects momentum shifts, sentiment changes, technical breakdowns
- Mechanical exits as fallback: Stop loss, trailing stops still active for safety
- Configurable confidence threshold: Default 60% for ML exits (vs 52% for entries)
- Addresses: "Can't the same ML be used to identify sells?"

Previous v183:
- Extended holding period: 5 -> 15 days to let winners run
- Widened trailing stops: 3% -> 5% for trending stocks  
- Profit protection - won't exit positions above +5% profit on time/trailing stop
- Addresses premature exits (e.g., NVDA +2.76% sold due to 5-day expiry)

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
    # FIX: Use absolute import instead of relative import to avoid "No module named 'sentiment_integration'"
    # The module exists at core/sentiment_integration.py but needs core. prefix
    from core.sentiment_integration import IntegratedSentimentAnalyzer, get_sentiment_analyzer
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

# Import Enhanced Pipeline Signal Adapter V3 (75-85% win rate)
try:
    sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
    from pipeline_signal_adapter_v3 import EnhancedPipelineSignalAdapter
    ENHANCED_ADAPTER_AVAILABLE = True
    logger.info("[ADAPTER] Enhanced Pipeline Signal Adapter V3 available (75-85% win rate target)")
except ImportError as e:
    logger.warning(f"Enhanced adapter not available: {e}")
    ENHANCED_ADAPTER_AVAILABLE = False
    EnhancedPipelineSignalAdapter = None

# Import Macro Risk Gatekeeper (v193.10)
try:
    from core.macro_risk_gates import MacroRiskGatekeeper, create_risk_gatekeeper
    MACRO_RISK_GATES_AVAILABLE = True
    logger.info("[RISK] Macro Risk Gatekeeper available (v193.10)")
except ImportError as e:
    logger.warning(f"Macro Risk Gates not available: {e}")
    MACRO_RISK_GATES_AVAILABLE = False
    MacroRiskGatekeeper = None

# Import Market Entry Strategy (v1.3.15.163)
try:
    from core.market_entry_strategy import MarketEntryStrategy, create_entry_timing_report
    MARKET_ENTRY_STRATEGY_AVAILABLE = True
    logger.info("[ENTRY] Market Entry Strategy available (avoid buying at tops)")
except ImportError as e:
    logger.warning(f"Market entry strategy not available: {e}")
    MARKET_ENTRY_STRATEGY_AVAILABLE = False
    MarketEntryStrategy = None

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
        use_real_swing_signals: bool = True,
        use_enhanced_adapter: bool = True,  # NEW: Enable 75-85% two-stage system
        min_confidence: float = None,       # FIX v1.3.15.160: UI confidence slider
        default_stop_loss: float = None     # FIX v1.3.15.160: UI stop-loss input
    ):
        """
        Initialize paper trading coordinator
        
        Args:
            symbols: List of symbols to trade
            initial_capital: Starting capital
            config_file: Path to configuration
            use_real_swing_signals: Use SwingSignalGenerator (True) or simplified (False)
            use_enhanced_adapter: Use EnhancedPipelineSignalAdapter for 75-85% win rate (True)
        """
        self.symbols = symbols
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.use_real_swing_signals = use_real_swing_signals and ML_INTEGRATION_AVAILABLE
        self.use_enhanced_adapter = use_enhanced_adapter and ENHANCED_ADAPTER_AVAILABLE
        
        # FIX v1.3.15.160: Store UI overrides for confidence and stop-loss
        self.ui_min_confidence = min_confidence
        self.ui_default_stop_loss = default_stop_loss
        
        # Load config
        self.config = self._load_config(config_file)
        
        # Initialize Enhanced Pipeline Signal Adapter (75-85% win rate two-stage system)
        if self.use_enhanced_adapter:
            logger.info("[TARGET] Initializing Enhanced Pipeline Signal Adapter (75-85% win rate)")
            logger.info("[SYSTEM] Two-stage: Overnight (60-80%) + Live ML (70-75%) = 75-85%")
            self.signal_adapter = EnhancedPipelineSignalAdapter(
                pipeline_base_path=Path(__file__).parent.parent / 'reports',
                use_ml_signals=True,
                ml_weight=0.60,        # 60% ML signals
                sentiment_weight=0.40   # 40% overnight sentiment
            )
            logger.info("[OK] Adapter initialized: ML(60%) + Overnight(40%)")
        else:
            self.signal_adapter = None
        
        # Initialize swing signal generator (REAL 70-75% win rate signals)
        # NOTE: If enhanced adapter is enabled, this is used WITHIN the adapter
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
        
        # v193.11.6.21: Gap reality checker for prediction validation
        try:
            from core.gap_reality_checker import GapRealityChecker
            self.gap_reality_checker = GapRealityChecker(state_dir="state")
            logger.info("[OK] Gap reality checker initialized")
        except Exception as e:
            logger.warning(f"[WARN] Gap reality checker unavailable: {e}")
            self.gap_reality_checker = None
        
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
        
        # Initialize Macro Risk Gatekeeper (v193.10)
        if MACRO_RISK_GATES_AVAILABLE:
            self.macro_risk_gates = create_risk_gatekeeper()
            logger.info("[RISK] Macro Risk Gatekeeper enabled (World Risk, US Market, VIX, Sector rules)")
        else:
            self.macro_risk_gates = None
            logger.warning("[RISK] Macro Risk Gates disabled - trades may execute during extreme risk events")
        
        # Initialize Market Entry Strategy (v1.3.15.163) - Avoid buying at tops
        if MARKET_ENTRY_STRATEGY_AVAILABLE:
            self.entry_strategy = MarketEntryStrategy(config=self.config.get('entry_timing', {}))
            logger.info("[ENTRY] Market Entry Strategy enabled (avoid buying at tops)")
        else:
            self.entry_strategy = None
            logger.warning("[ENTRY] Entry timing disabled - may buy at tops")
        
        # Initialize Pre-Market Strategy (v193.11.6.10) - Gap prediction trading
        try:
            from core.pre_market_strategy import PreMarketStrategy
            self.pre_market_strategy = PreMarketStrategy(config=self.config.get('pre_market', {}))
            logger.info("[PRE-MARKET] Gap prediction strategy enabled (AU SPI, UK FTSE futures)")
        except ImportError as e:
            self.pre_market_strategy = None
            logger.warning(f"[PRE-MARKET] Gap prediction strategy not available: {e}")
        
        # Load overnight reports on startup
        logger.info("[STARTUP] Loading overnight pipeline reports...")
        self._overnight_reports_cache = self._load_overnight_reports()
        self._reports_last_check = datetime.now()
        self._reports_check_interval = timedelta(minutes=30)  # Check every 30 minutes
        self._processed_recommendations = set()  # Track which recommendations we've acted on
        
        logger.info("=" * 80)
        logger.info("PAPER TRADING COORDINATOR - INTEGRATED VERSION")
        logger.info("=" * 80)
        logger.info(f"  Initial Capital: USD{initial_capital:,.2f}")
        logger.info(f"  Symbols: {', '.join(symbols)}")
        logger.info(f"  Real Swing Signals: {self.use_real_swing_signals}")
        if self.use_enhanced_adapter:
            logger.info(f"  Enhanced Adapter: ENABLED (75-85% win rate target)")
            logger.info(f"    - Overnight Pipeline: 40% weight (60-80% accuracy)")
            logger.info(f"    - Live ML Signals: 60% weight (70-75% accuracy)")
        else:
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
                'holding_period_days': 15,  # v1.3.15.183: Extended from 5 to 15 days to let winners run
                'stop_loss_percent': 5.0,   # v1.3.15.183: Widened from 3% to 5% for trending stocks
                'confidence_threshold': 52.0,
                'max_position_size': 0.25,
                'use_trailing_stop': True,
                'use_profit_targets': True,
                'disable_time_exit_for_winners': True,  # v1.3.15.183: NEW - Don't exit profitable positions on time
                'min_profit_to_hold': 5.0,   # v1.3.15.183: NEW - Hold positions above +5% profit longer
                # v1.3.15.184: ML-based intelligent exits
                'use_ml_exits': True,                    # v1.3.15.184: NEW - Use ML to identify optimal exits
                'ml_exit_confidence_threshold': 0.60,    # v1.3.15.184: NEW - Require 60%+ confidence for ML exits
                'ml_exit_weight': 0.70                   # v1.3.15.184: NEW - Weight ML exits 70% vs mechanical 30%
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
    
    def _load_overnight_reports(self) -> Dict:
        """
        Load morning reports from overnight pipeline
        
        Returns dict with structure:
        {
            'au': {...report data...},
            'us': {...report data...},
            'uk': {...report data...}
        }
        """
        reports = {}
        report_base = Path(__file__).parent.parent / 'reports' / 'screening'
        
        for market in ['au', 'us', 'uk']:
            report_path = report_base / f'{market}_morning_report.json'
            if report_path.exists():
                try:
                    with open(report_path, 'r') as f:
                        report = json.load(f)
                        reports[market] = report
                        
                        # Calculate report age
                        if 'timestamp' in report:
                            report_time = datetime.fromisoformat(report['timestamp'])
                            age_hours = (datetime.now() - report_time).total_seconds() / 3600
                            report['age_hours'] = age_hours
                        
                        top_count = len(report.get('top_stocks', []))
                        
                        # Extract gap prediction if available
                        market_sentiment = report.get('market_sentiment', {})
                        gap_prediction = market_sentiment.get('gap_prediction', {})
                        
                        if gap_prediction and 'predicted_gap_pct' in gap_prediction:
                            gap_pct = gap_prediction['predicted_gap_pct']
                            gap_conf = gap_prediction.get('confidence', 0)
                            gap_dir = gap_prediction.get('direction', 'NEUTRAL')
                            logger.info(
                                f"[OK] Loaded {market.upper()} morning report - "
                                f"{top_count} opportunities, "
                                f"sentiment {report.get('overall_sentiment', 0):.1f}, "
                                f"gap {gap_pct:+.2f}% ({gap_dir}, {gap_conf:.0%} conf), "
                                f"age {report.get('age_hours', 0):.1f}h"
                            )
                        else:
                            logger.info(
                                f"[OK] Loaded {market.upper()} morning report - "
                                f"{top_count} opportunities, "
                                f"sentiment {report.get('overall_sentiment', 0):.1f}, "
                                f"age {report.get('age_hours', 0):.1f}h"
                            )
                except Exception as e:
                    logger.warning(f"[WARN] Error loading {market.upper()} report: {e}")
            else:
                logger.debug(f"[INFO] No {market.upper()} morning report found at {report_path}")
        
        if not reports:
            logger.warning("[WARN] No overnight reports found - running without pipeline data")
        else:
            total_opportunities = sum(len(r.get('top_stocks', [])) for r in reports.values())
            logger.info(f"[OK] Loaded {len(reports)} markets, {total_opportunities} total opportunities")
        
        return reports
    
    def _check_for_updated_reports(self) -> bool:
        """
        Check if pipeline reports have been updated since last check
        
        Returns:
            True if reports were updated and reloaded, False otherwise
        """
        now = datetime.now()
        
        # Only check every 30 minutes
        if now - self._reports_last_check < self._reports_check_interval:
            return False
        
        self._reports_last_check = now
        
        report_base = Path(__file__).parent.parent / 'reports' / 'screening'
        updated = False
        
        for market in ['au', 'us', 'uk']:
            report_path = report_base / f'{market}_morning_report.json'
            if report_path.exists():
                # Check file modification time
                file_mtime = datetime.fromtimestamp(report_path.stat().st_mtime)
                
                # If report exists in cache, check if file is newer
                if market in self._overnight_reports_cache:
                    cached_report = self._overnight_reports_cache[market]
                    if 'timestamp' in cached_report:
                        cached_time = datetime.fromisoformat(cached_report['timestamp'])
                        if file_mtime > cached_time:
                            logger.info(f"[PIPELINE] Detected updated {market.upper()} morning report")
                            updated = True
                else:
                    # New report that wasn't there before
                    logger.info(f"[PIPELINE] Detected new {market.upper()} morning report")
                    updated = True
        
        if updated:
            logger.info("[PIPELINE] Reloading morning reports...")
            self._overnight_reports_cache = self._load_overnight_reports()
            return True
        
        return False
    
    def _get_pipeline_recommendations(self, market: str = None, max_recommendations: int = 5) -> List[Dict]:
        """
        Get top stock recommendations from pipeline reports
        
        Args:
            market: Specific market ('au', 'us', 'uk') or None for all markets
            max_recommendations: Maximum number of recommendations per market
            
        Returns:
            List of recommendation dicts with keys: symbol, signal, score, sentiment, market
        """
        recommendations = []
        
        markets_to_check = [market] if market else ['au', 'us', 'uk']
        
        for mkt in markets_to_check:
            if mkt not in self._overnight_reports_cache:
                continue
            
            report = self._overnight_reports_cache[mkt]
            top_stocks = report.get('top_stocks', [])
            
            # Get top N stocks from this market
            for stock in top_stocks[:max_recommendations]:
                symbol = stock.get('symbol')
                if not symbol:
                    continue
                
                # Create unique key to track if we've already processed this recommendation
                recommendation_key = f"{symbol}_{report.get('timestamp', '')}"
                
                # Skip if we've already acted on this recommendation
                if recommendation_key in self._processed_recommendations:
                    continue
                
                # Extract recommendation details
                rec = {
                    'symbol': symbol,
                    'signal': stock.get('signal', 'UNKNOWN'),
                    'opportunity_score': stock.get('opportunity_score', stock.get('score', 0)),
                    'sentiment': stock.get('sentiment', 50.0),
                    'market': mkt.upper(),
                    'technical_signal': stock.get('technical_signal', ''),
                    'recommendation_key': recommendation_key,
                    'report_age_hours': report.get('age_hours', 0)
                }
                
                recommendations.append(rec)
        
        return recommendations
    
    def _evaluate_pipeline_recommendation(self, recommendation: Dict) -> Tuple[bool, float, str]:
        """
        Evaluate if a pipeline recommendation meets trading signal parameters
        
        FIX v193.11.6.16: Added hybrid trade_mode to allow confidence-based HOLD signal overrides
        
        Two modes:
        - 'strict': Only trade explicit BUY/SELL signals (default, conservative)
        - 'confidence_based': Allow high-confidence HOLD signals with strong scores to trade
        
        Args:
            recommendation: Recommendation dict from _get_pipeline_recommendations
            
        Returns:
            Tuple of (should_trade, confidence, reason)
        """
        symbol = recommendation['symbol']
        signal = recommendation['signal']
        score = recommendation['opportunity_score']
        sentiment = recommendation['sentiment']
        
        # FIX v193.11.6.16: Get trade mode from config (default to 'strict' for safety)
        trade_mode = self.config.get('paper_trading', {}).get('trade_mode', 'strict')
        
        # Calculate confidence (used in both modes)
        confidence = (score * 0.7 + sentiment * 0.3)
        
        # Common checks for report age
        if recommendation['report_age_hours'] > 12:
            return False, 0, f"Report too old: {recommendation['report_age_hours']:.1f}h > 12h"
        
        # ===== MODE 1: STRICT (Original Behavior) =====
        if trade_mode == 'strict':
            # BUY signals
            if signal in ['BUY', 'STRONG_BUY']:
                if score < 60.0:
                    return False, 0, f"Score too low: {score:.1f} < 60.0"
                if sentiment < 45.0:
                    return False, 0, f"Sentiment too bearish: {sentiment:.1f} < 45.0"
                
                return True, confidence, f"Pipeline BUY: score={score:.1f}, sentiment={sentiment:.1f}"
            
            # SELL signals
            elif signal in ['SELL', 'STRONG_SELL']:
                if symbol not in self.positions:
                    return False, 0, "No open position to sell"
                if score > 40.0:
                    return False, 0, f"Score too high for sell: {score:.1f} > 40.0"
                
                return True, confidence, f"Pipeline SELL: score={score:.1f}, sentiment={sentiment:.1f}"
            
            # HOLD or other signals - blocked in strict mode
            return False, 0, f"Signal {signal} not actionable (strict mode)"
        
        # ===== MODE 2: CONFIDENCE_BASED (New Behavior) =====
        elif trade_mode == 'confidence_based':
            # Get configurable thresholds
            min_confidence = self.config.get('paper_trading', {}).get('min_confidence', 53.0)
            hold_buy_threshold = self.config.get('paper_trading', {}).get('hold_override_min_score', 60.0)
            hold_sell_threshold = self.config.get('paper_trading', {}).get('hold_override_max_score', 40.0)
            
            # Check minimum confidence first (applies to all signals)
            if confidence < min_confidence:
                return False, 0, f"Confidence {confidence:.1f}% < {min_confidence}% (confidence_based mode)"
            
            # Explicit BUY signals
            if signal in ['BUY', 'STRONG_BUY']:
                if score < 60.0:
                    return False, 0, f"Score too low: {score:.1f} < 60.0"
                if sentiment < 45.0:
                    return False, 0, f"Sentiment too bearish: {sentiment:.1f} < 45.0"
                
                return True, confidence, f"Pipeline BUY: score={score:.1f}, conf={confidence:.1f}%"
            
            # Explicit SELL signals
            elif signal in ['SELL', 'STRONG_SELL']:
                if symbol not in self.positions:
                    return False, 0, "No open position to sell"
                if score > 40.0:
                    return False, 0, f"Score too high for sell: {score:.1f} > 40.0"
                
                return True, confidence, f"Pipeline SELL: score={score:.1f}, conf={confidence:.1f}%"
            
            # HOLD signals - use score-based directional bias
            elif signal == 'HOLD':
                # High-quality HOLD (score >= 60) -> Treat as BUY if confidence met
                if score >= hold_buy_threshold and sentiment >= 45.0:
                    logger.info(f"[HOLD->BUY] {symbol}: Overriding HOLD signal - score={score:.1f}, conf={confidence:.1f}%")
                    return True, confidence, f"Pipeline BUY (HOLD override): score={score:.1f}, conf={confidence:.1f}%"
                
                # Low-quality HOLD (score <= 40) + open position -> Treat as SELL
                elif score <= hold_sell_threshold and symbol in self.positions:
                    logger.info(f"[HOLD->SELL] {symbol}: Overriding HOLD signal - score={score:.1f}, conf={confidence:.1f}%")
                    return True, confidence, f"Pipeline SELL (HOLD override): score={score:.1f}, conf={confidence:.1f}%"
                
                # Truly neutral HOLD (40 < score < 60) - don't trade
                else:
                    return False, 0, f"Signal HOLD with neutral score {score:.1f} (no strong bias, confidence_based mode)"
            
            # Unknown signal types
            return False, 0, f"Signal {signal} not recognized (confidence_based mode)"
        
        # Invalid trade_mode
        else:
            logger.error(f"Invalid trade_mode '{trade_mode}' - defaulting to strict")
            return False, 0, f"Invalid trade_mode '{trade_mode}'"
    
    def _process_pipeline_recommendations(self):
        """
        Process pipeline recommendations and execute trades that meet criteria
        """
        recommendations = self._get_pipeline_recommendations(max_recommendations=5)
        
        if not recommendations:
            logger.info("[PIPELINE] No new recommendations to process")
            return
        
        logger.info(f"[PIPELINE] Found {len(recommendations)} recommendations across all markets")
        
        actionable_count = 0
        for rec in recommendations:
            symbol = rec['symbol']
            
            # Skip if we already have a position
            if symbol in self.positions:
                logger.debug(f"[PIPELINE] Skipping {symbol} - already have position")
                continue
            
            # Skip if we've reached max positions
            if len(self.positions) >= self.config['risk_management']['max_total_positions']:
                logger.info(f"[PIPELINE] Max positions reached ({len(self.positions)}), stopping")
                break
            
            # Evaluate recommendation
            should_trade, confidence, reason = self._evaluate_pipeline_recommendation(rec)
            
            if should_trade:
                actionable_count += 1
                logger.info(
                    f"[PIPELINE] Actionable: {symbol} ({rec['market']}) - "
                    f"{rec['signal']} @ score={rec['opportunity_score']:.1f}, "
                    f"confidence={confidence:.1f}%"
                )
                logger.info(f"[PIPELINE]   Reason: {reason}")
                
                # Execute trade based on signal
                if rec['signal'] in ['BUY', 'STRONG_BUY']:
                    # Fetch current price
                    price_data = self.fetch_market_data(symbol)
                    if price_data is None or price_data.empty:
                        logger.warning(f"[PIPELINE] Could not fetch data for {symbol}")
                        continue
                    
                    current_price = price_data['Close'].iloc[-1]
                    
                    # Enter position
                    logger.info(f"[PIPELINE] Executing BUY for {symbol} at USD{current_price:.2f}")
                    self.enter_position(
                        symbol=symbol,
                        entry_price=current_price,
                        confidence=confidence,
                        signal_strength=rec['opportunity_score'],
                        entry_reason=f"Pipeline: {reason}"
                    )
                    
                    # Mark this recommendation as processed
                    self._processed_recommendations.add(rec['recommendation_key'])
                
                elif rec['signal'] in ['SELL', 'STRONG_SELL'] and symbol in self.positions:
                    # Exit position
                    logger.info(f"[PIPELINE] Executing SELL for {symbol}")
                    self.exit_position(symbol, f"Pipeline: {reason}")
                    
                    # Mark this recommendation as processed
                    self._processed_recommendations.add(rec['recommendation_key'])
            else:
                logger.debug(f"[PIPELINE] Not actionable: {symbol} - {reason}")
        
        if actionable_count > 0:
            logger.info(f"[PIPELINE] Processed {actionable_count} actionable recommendations")
        else:
            logger.info("[PIPELINE] No recommendations met trading criteria")
    
    def _load_overnight_sentiment(self, symbol: str) -> Optional[float]:
        """
        Load overnight sentiment score for a specific symbol from morning reports
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'HSBA.L', 'BHP.AX')
            
        Returns:
            Sentiment score (0-100) or None if not found
        """
        # Load reports if not already loaded
        if not hasattr(self, '_overnight_reports_cache'):
            self._overnight_reports_cache = self._load_overnight_reports()
        
        reports = self._overnight_reports_cache
        
        # Determine market from symbol
        if symbol.endswith('.AX'):
            market = 'au'
        elif symbol.endswith('.L'):
            market = 'uk'
        else:
            market = 'us'
        
        # Get report for this market
        if market not in reports:
            return None
        
        report = reports[market]
        
        # Look for symbol in top_stocks
        for stock in report.get('top_stocks', []):
            if stock.get('symbol') == symbol:
                sentiment = stock.get('sentiment', stock.get('opportunity_score', 0))
                logger.debug(f"[DATA] {symbol} overnight sentiment: {sentiment:.1f}")
                return sentiment
        
        # Not in top stocks - use market-wide sentiment as fallback
        market_sentiment = report.get('overall_sentiment', 50.0)
        logger.debug(f"[DATA] {symbol} not in top stocks, using market sentiment: {market_sentiment:.1f}")
        return market_sentiment
    
    def get_trading_opportunities(self, min_score: float = 60.0) -> List[Dict]:
        """
        Get pre-screened trading opportunities from overnight pipeline
        
        These are stocks that have already been analyzed overnight with:
        - Opportunity scores (0-100 composite ranking)
        - Technical signals (BREAKOUT, MOMENTUM, VOLUME)
        - FinBERT sentiment analysis
        - LSTM predictions
        
        Args:
            min_score: Minimum opportunity score to include
            
        Returns:
            List of opportunity dicts sorted by score
        """
        # Load reports if not already loaded
        if not hasattr(self, '_overnight_reports_cache'):
            self._overnight_reports_cache = self._load_overnight_reports()
        
        reports = self._overnight_reports_cache
        opportunities = []
        
        for market, report in reports.items():
            for stock in report.get('top_stocks', []):
                score = stock.get('sentiment', stock.get('opportunity_score', 0))
                
                if score >= min_score:
                    opportunities.append({
                        'symbol': stock['symbol'],
                        'opportunity_score': score,
                        'signals': stock.get('signals', []),
                        'market': market,
                        'market_sentiment': report.get('overall_sentiment', 50.0),
                        'recommendation': report.get('recommendation', 'NEUTRAL'),
                        'risk_rating': report.get('risk_rating', 'Unknown'),
                        'pre_screened': True,
                        'source': 'overnight_pipeline'
                    })
        
        # Sort by opportunity score (descending)
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        logger.info(
            f"[OPPORTUNITIES] Found {len(opportunities)} pre-screened stocks "
            f"(min_score={min_score:.1f})"
        )
        
        # v193.11.6.21: Apply gap reality adjustment if available
        if self.gap_reality_checker and len(opportunities) > 0:
            # Group opportunities by market
            market_groups = {}
            for opp in opportunities:
                market = opp.get('market', '').upper()
                if market not in market_groups:
                    market_groups[market] = []
                market_groups[market].append(opp)
            
            # Apply gap adjustment to each market
            for market, stocks in market_groups.items():
                adjusted_stocks = self.gap_reality_checker.apply_multiplier_to_stocks(stocks, market)
                # Note: stocks are modified in place, no need to reassign
            
            # Re-sort after adjustment
            opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
            
            logger.info(
                f"[GAP ADJUST] Applied gap reality adjustments to {len(opportunities)} opportunities"
            )
        
        return opportunities
    
    def validate_gap_predictions(self) -> Dict:
        """
        Validate gap predictions against actual market opens (v193.11.6.21)
        
        Call this method 10-15 minutes after market open to:
        1. Check actual market gap vs prediction
        2. Log prediction accuracy
        3. Enable score adjustments for future opportunities
        
        Returns:
            Dict with validation results for each market
        """
        if not self.gap_reality_checker:
            logger.warning("[GAP VALIDATE] Gap reality checker not available")
            return {}
        
        logger.info("\n" + "="*80)
        logger.info("[GAP VALIDATE] CHECKING PREDICTION ACCURACY")
        logger.info("="*80)
        
        results = {}
        
        # Check each market
        for market in ['AU', 'UK', 'US']:
            validation = self.gap_reality_checker.check_actual_gap(market, minutes_after_open=15)
            
            if validation:
                results[market] = validation
                
                # Log summary
                summary = self.gap_reality_checker.get_validation_summary(market)
                if summary:
                    logger.info(f"\n{summary}")
                
                # Log if large miss
                error_pct = abs(validation.get('error_pct', 0))
                if error_pct > 0.5:
                    logger.warning(
                        f"[GAP VALIDATE] {market}: Large prediction miss "
                        f"(error: {validation.get('error_pct'):+.2f}%)"
                    )
            else:
                logger.debug(f"[GAP VALIDATE] {market}: No validation available yet")
        
        return results
    
    def analyze_pre_market_gaps(self, execute_trades: bool = False) -> Dict:
        """
        Analyze gap predictions from overnight pipelines and determine trading strategy
        
        **NEW in v193.11.6.10**: Pre-market gap prediction trading
        - Loads gap predictions from AU/UK overnight reports
        - Analyzes gap vs sentiment vs world risk
        - Calculates optimal position sizing
        - Optionally executes trades based on gap signals
        
        Args:
            execute_trades: If True, execute trades based on gap analysis
            
        Returns:
            Dict with analysis results for each market
        """
        if not self.pre_market_strategy:
            logger.warning("[PRE-MARKET] Gap prediction strategy not available")
            return {}
        
        logger.info("\n" + "="*80)
        logger.info("[PRE-MARKET] OVERNIGHT GAP ANALYSIS")
        logger.info("="*80)
        
        # Load overnight reports if not already loaded
        if not hasattr(self, '_overnight_reports_cache'):
            self._overnight_reports_cache = self._load_overnight_reports()
        
        reports = self._overnight_reports_cache
        results = {}
        
        # Analyze each market with gap predictions
        for market in ['au', 'uk']:  # AU and UK have gap predictions, US TBD
            if market not in reports:
                logger.info(f"[PRE-MARKET] No {market.upper()} report available")
                continue
            
            report = reports[market]
            market_sentiment_data = report.get('market_sentiment', {})
            
            # Extract gap prediction
            gap_prediction = market_sentiment_data.get('gap_prediction', {})
            if not gap_prediction or 'predicted_gap_pct' not in gap_prediction:
                # Try alternate structure
                if 'predicted_gap_pct' in market_sentiment_data:
                    gap_prediction = {
                        'predicted_gap_pct': market_sentiment_data.get('predicted_gap_pct', 0),
                        'confidence': market_sentiment_data.get('confidence', 0),
                        'direction': market_sentiment_data.get('direction', 'NEUTRAL')
                    }
                else:
                    logger.info(f"[PRE-MARKET] No gap prediction found in {market.upper()} report")
                    continue
            
            # Extract market data
            sentiment_score = market_sentiment_data.get('sentiment_score', 50)
            world_risk_score = report.get('world_risk_score', 50)
            top_stocks = report.get('top_opportunities', report.get('top_stocks', []))
            
            logger.info(f"\n[{market.upper()}] Gap Analysis:")
            logger.info(f"  Gap: {gap_prediction.get('predicted_gap_pct', 0):+.2f}%")
            logger.info(f"  Confidence: {gap_prediction.get('confidence', 0):.0f}%")
            logger.info(f"  Sentiment: {sentiment_score:.1f}/100")
            logger.info(f"  World Risk: {world_risk_score:.1f}/100")
            logger.info(f"  Top Stocks: {len(top_stocks)}")
            
            # v193.11.6.21: Store gap prediction for later validation
            if self.gap_reality_checker:
                self.gap_reality_checker.store_prediction(
                    market=market.upper(),
                    predicted_gap_pct=gap_prediction.get('predicted_gap_pct', 0),
                    confidence=gap_prediction.get('confidence', 0),
                    direction=gap_prediction.get('direction', 'NEUTRAL')
                )
            
            # Analyze gap opportunity
            decision = self.pre_market_strategy.analyze_gap_opportunity(
                market=market,
                gap_prediction=gap_prediction,
                world_risk_score=world_risk_score,
                sentiment_score=sentiment_score,
                top_stocks=top_stocks
            )
            
            results[market] = decision
            
            # Execute trades if requested and decision is to enter
            if execute_trades and decision['should_enter']:
                logger.info(f"\n[{market.upper()}] EXECUTING PRE-MARKET TRADES")
                logger.info(f"  Position Multiplier: {decision['position_multiplier']:.2f}x")
                logger.info(f"  Entry Timing: {decision['timing']}")
                logger.info(f"  Symbols: {', '.join(decision['recommended_symbols'])}")
                
                # Calculate position size with multiplier
                base_position_size = self.config['risk_management']['position_size_pct'] / 100.0
                adjusted_size = base_position_size * decision['position_multiplier']
                
                # Enter positions for recommended symbols
                for symbol in decision['recommended_symbols']:
                    # Check if we already have this position
                    if symbol in self.positions:
                        logger.info(f"  [SKIP] {symbol} - already have position")
                        continue
                    
                    # Check max positions
                    if len(self.positions) >= self.config['risk_management']['max_total_positions']:
                        logger.info(f"  [SKIP] Max positions reached ({len(self.positions)})")
                        break
                    
                    # Fetch current/pre-market price
                    price_data = self.fetch_market_data(symbol, period="5d")
                    if price_data is None or price_data.empty:
                        logger.warning(f"  [ERROR] Could not fetch data for {symbol}")
                        continue
                    
                    current_price = self.fetch_current_price(symbol)
                    if not current_price:
                        current_price = price_data['Close'].iloc[-1]
                    
                    # Calculate shares based on adjusted position size
                    position_value = self.current_capital * adjusted_size
                    shares = int(position_value / current_price)
                    
                    if shares < 1:
                        logger.warning(f"  [SKIP] {symbol} - position too small ({shares} shares)")
                        continue
                    
                    # Find stock data from report for confidence
                    stock_confidence = 60.0  # Default
                    for stock in top_stocks:
                        if stock.get('symbol') == symbol:
                            stock_confidence = stock.get('confidence', 60.0)
                            break
                    
                    # Enter position
                    logger.info(
                        f"  [ENTER] {symbol} @ USD{current_price:.2f} "
                        f"x{shares} shares = USD{shares * current_price:.2f} "
                        f"({adjusted_size*100:.1f}% of capital)"
                    )
                    
                    try:
                        self.enter_position(
                            symbol=symbol,
                            entry_price=current_price,
                            confidence=stock_confidence,
                            signal_strength=decision['gap_data']['confidence'],
                            entry_reason=f"Pre-market gap: {decision['entry_reason']}",
                            position_size_override=adjusted_size  # Pass multiplier
                        )
                        logger.info(f"  [OK] Position entered successfully")
                    except Exception as e:
                        logger.error(f"  [ERROR] Failed to enter position: {e}")
            
            elif decision['should_enter']:
                logger.info(f"\n[{market.upper()}] Gap signal detected but execute_trades=False")
                logger.info(f"  Set execute_trades=True to enter positions")
            else:
                logger.info(f"\n[{market.upper()}] No entry signal - {decision['entry_reason']}")
        
        logger.info("\n" + "="*80)
        logger.info("[PRE-MARKET] Gap analysis complete")
        logger.info("="*80 + "\n")
        
        return results
    
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
        Fetch current price for a symbol (v190: Enhanced after-hours support)
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Current price or None
            
        Enhancement v190:
        - Try regularMarketPrice first (live trading)
        - Fallback to postMarketPrice (after-hours)
        - Fallback to previousClose (market closed)
        - Fallback to yfinance historical data
        """
        try:
            if YAHOOQUERY_AVAILABLE:
                ticker = Ticker(symbol)
                quote = ticker.price
                
                if isinstance(quote, dict) and symbol in quote:
                    stock_data = quote[symbol]
                    
                    # Try regular market price (during trading hours)
                    price = stock_data.get('regularMarketPrice')
                    if price and price > 0:
                        return float(price)
                    
                    # Try post-market price (after-hours trading)
                    price = stock_data.get('postMarketPrice')
                    if price and price > 0:
                        logger.debug(f"{symbol}: Using post-market price USD{price:.2f}")
                        return float(price)
                    
                    # Try pre-market price (before market opens)
                    price = stock_data.get('preMarketPrice')
                    if price and price > 0:
                        logger.debug(f"{symbol}: Using pre-market price USD{price:.2f}")
                        return float(price)
                    
                    # Fallback to previous close (market closed)
                    price = stock_data.get('regularMarketPreviousClose')
                    if price and price > 0:
                        logger.debug(f"{symbol}: Using previous close USD{price:.2f} (market closed)")
                        return float(price)
            
            # Fallback to yfinance
            if YFINANCE_AVAILABLE:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                
                if not hist.empty:
                    price = float(hist['Close'].iloc[-1])
                    logger.debug(f"{symbol}: Using yfinance close USD{price:.2f}")
                    return price
            
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
            
            # Daily momentum (+/-10 points)
            sentiment += daily_change * 3.33
            
            # 5-day trend (+/-15 points)
            sentiment += five_day_change * 3
            
            # MA position (+/-10 points)
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
    
    def should_allow_trade(self, symbol: str, signal: Dict, sentiment_score: float, price_data=None) -> Tuple[bool, float, str]:
        """
        Check if trade should be allowed based on FinBERT v4.4.4 sentiment gates
        
        **FIXED in v193.11.3**: Accept price_data to avoid redundant yfinance calls
        **NEW in v193.10**: Macro Risk Gatekeeper integration (World Risk, US Market, VIX, Sector rules)
        **FIXED in v1.3.15.52**: Now returns position_multiplier for dynamic sizing
        **NEW in v1.3.15.45**: Respects negative sentiment from morning report
        
        Args:
            symbol: Stock symbol
            signal: Trading signal
            sentiment_score: Market sentiment (0-100)
            price_data: Optional pre-fetched price data (avoids redundant yfinance call)
        
        Returns:
            Tuple of (allow_trade, position_multiplier, reason)
            - allow_trade (bool): Whether to proceed with trade
            - position_multiplier (float): 0.0 to 1.5 for position sizing
            - reason (str): Explanation of decision
        """
        # STEP 1: Check Macro Risk Gates (v193.10) - HIGHEST PRIORITY
        # Blocks trades during extreme risk (World Risk >80, US market <-1.5%, VIX >30)
        if self.macro_risk_gates:
            confidence = signal.get('confidence', 0) / 100.0  # Convert to 0.0-1.0
            allow_macro, position_mult, macro_reason = self.macro_risk_gates.should_allow_new_position(
                symbol=symbol,
                signal=signal,
                confidence=confidence
            )
            
            if not allow_macro:
                logger.warning(f"[MACRO BLOCK] {symbol}: {macro_reason}")
                return False, 0.0, f"Macro Risk Gate: {macro_reason}"
            
            # Apply position reduction if macro risk gates suggest it
            if position_mult < 1.0:
                logger.warning(f"[MACRO REDUCE] {symbol}: Position reduced to {position_mult*100:.0f}% - {macro_reason}")
                # Note: Will be combined with sentiment multipliers below
        else:
            # No macro gates available - proceed with full position
            position_mult = 1.0
            logger.debug(f"[RISK] Macro Risk Gates not available for {symbol}, proceeding without macro checks")
        
        # STEP 2: Check if we have sentiment recommendation from morning report
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
                        # Combine macro risk multiplier with sentiment multiplier
                        final_mult = position_mult * 0.5
                        return True, final_mult, reason
        
        # Standard sentiment gates with position multipliers
        block_threshold = self.config.get('cross_timeframe', {}).get('sentiment_block_threshold', 30)
        if sentiment_score < block_threshold:
            reason = f"Sentiment too low ({sentiment_score:.1f} < {block_threshold})"
            logger.warning(f"[BLOCK] {symbol}: {reason}")
            return False, 0.0, reason
        
        # Check signal action (FIX v1.3.15.165: Check 'prediction' field, not 'action')
        # Signal format: {'prediction': 1, 'confidence': 75} or {'action': 'BUY'}
        prediction = signal.get('prediction', 0)
        action = signal.get('action', '')
        
        # Support both formats: prediction==1 OR action in ['BUY', 'STRONG_BUY']
        is_buy_signal = (prediction == 1) or (action in ['BUY', 'STRONG_BUY'])
        
        if not is_buy_signal:
            reason = f"Signal not actionable: {action if action else 'HOLD'} (only BUY/STRONG_BUY allowed)"
            logger.info(f"[BLOCK] {symbol}: {reason}")
            return False, 0.0, reason
        
        # Check confidence (FIX v1.3.15.160: Use UI value if provided)
        min_confidence = self.ui_min_confidence if self.ui_min_confidence is not None else 48.0  # v188: Lowered from 52.0
        confidence = signal.get('confidence', 0)
        if confidence < min_confidence:
            reason = f"Confidence {confidence:.1f}% < {min_confidence}%"
            logger.info(f"[SKIP] {symbol}: {reason}")
            return False, 0.0, reason
        
        # NEW v1.3.15.163: Check entry timing to avoid buying at tops
        # FIX v1.3.15.165: Support both 'prediction' and 'action' signal formats
        prediction = signal.get('prediction', 0)
        action = signal.get('action', '')
        is_buy_signal = (prediction == 1) or (action in ['BUY', 'STRONG_BUY'])
        
        if self.entry_strategy and is_buy_signal:
            try:
                # Get price data for entry timing evaluation
                # FIX v193.11.3: Use passed price_data to avoid redundant yfinance call
                if price_data is None or price_data.empty:
                    import yfinance as yf
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='3mo')
                else:
                    hist = price_data
                
                if not hist.empty and len(hist) >= 20:
                    entry_eval = self.entry_strategy.evaluate_entry_timing(
                        symbol=symbol,
                        price_data=hist,
                        signal=signal
                    )
                    
                    entry_quality = entry_eval.get('entry_quality')
                    entry_score = entry_eval.get('entry_score', 50)
                    
                    # Block on DONT_BUY
                    if entry_quality == 'DONT_BUY':
                        reason = f"Poor entry timing (score {entry_score:.0f}/100): {entry_eval.get('wait_reason', 'Likely at top')}"
                        logger.warning(f"[BLOCK] {symbol}: {reason}")
                        return False, 0.0, reason
                    
                    # Reduce position on WAIT_FOR_DIP
                    elif entry_quality == 'WAIT_FOR_DIP':
                        target = entry_eval.get('entry_price_target', 0)
                        current = entry_eval.get('current_price', 0)
                        reason = f"Entry timing caution (score {entry_score:.0f}/100): Wait for USD{target:.2f} vs current USD{current:.2f}"
                        logger.warning(f"[REDUCE] {symbol}: {reason}")
                        # Apply 50% position reduction for poor timing, combine with macro multiplier
                        sentiment_multiplier = self._get_sentiment_multiplier(sentiment_score)
                        final_mult = position_mult * sentiment_multiplier * 0.5
                        return True, final_mult, reason
                    
                    # Log good/excellent timing
                    elif entry_quality in ['GOOD_ENTRY', 'IMMEDIATE_BUY']:
                        logger.info(f"[OK] {symbol}: Good entry timing (score {entry_score:.0f}/100)")
                
            except Exception as e:
                logger.warning(f"[ENTRY] Could not evaluate entry timing for {symbol}: {e}")
        
        # Calculate position multiplier based on sentiment score
        # This is the key fix: dynamically adjust position size based on market conditions
        # NOTE: Combine with macro risk multiplier from Step 1
        if sentiment_score < 30:
            # Extreme bearish - BLOCK (already handled above)
            return False, 0.0, "Extreme bearish sentiment"
        elif sentiment_score < 45:
            # Bearish - REDUCE to 50%
            reason = f"Bearish sentiment ({sentiment_score:.1f}) - REDUCE position to 50%"
            logger.warning(f"[REDUCE] {symbol}: {reason}")
            final_mult = position_mult * 0.5
            return True, final_mult, reason
        elif sentiment_score < 55:
            # Slightly bearish/neutral - REDUCE to 75%
            reason = f"Neutral sentiment ({sentiment_score:.1f}) - REDUCE position to 75%"
            logger.info(f"[CAUTION] {symbol}: {reason}")
            final_mult = position_mult * 0.75
            return True, final_mult, reason
        elif sentiment_score < 65:
            # Normal bullish - Standard 100%
            reason = f"Normal sentiment ({sentiment_score:.1f}) - Standard position"
            logger.info(f"[ALLOW] {symbol}: {reason}")
            final_mult = position_mult * 1.0
            return True, final_mult, reason
        elif sentiment_score < 75:
            # Bullish - BOOST to 120%
            reason = f"Bullish sentiment ({sentiment_score:.1f}) - BOOST position to 120%"
            logger.info(f"[BOOST] {symbol}: {reason}")
            final_mult = position_mult * 1.2
            return True, final_mult, reason
        else:
            # Strong bullish - MAXIMUM BOOST to 150%
            reason = f"Strong bullish ({sentiment_score:.1f}) - MAXIMUM position 150%"
            logger.info(f"[MAXIMUM] {symbol}: {reason}")
            final_mult = position_mult * 1.5
            return True, final_mult, reason
    
    def _get_sentiment_multiplier(self, sentiment_score: float) -> float:
        """
        Get position size multiplier based on sentiment (extracted for reuse)
        
        Args:
            sentiment_score: Market sentiment 0-100
            
        Returns:
            Position multiplier (0.5 to 1.5)
        """
        if sentiment_score < 45:
            return 0.5
        elif sentiment_score < 55:
            return 0.75
        elif sentiment_score < 65:
            return 1.0
        elif sentiment_score < 75:
            return 1.2
        else:
            return 1.5
    
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
            # Use Enhanced Pipeline Signal Adapter if enabled (75-85% win rate)
            if self.use_enhanced_adapter and self.signal_adapter is not None:
                logger.info(f"[ADAPTER] Generating ENHANCED signal for {symbol} (75-85% target)")
                
                # Try to load overnight sentiment from reports
                overnight_sentiment_score = self._load_overnight_sentiment(symbol)
                
                if overnight_sentiment_score:
                    # FIX v1.3.15.180: Wrap sentiment score in proper dict structure
                    # _load_overnight_sentiment returns a float, but combine_signals expects a dict
                    overnight_sentiment = {
                        'sentiment_score': overnight_sentiment_score,
                        'confidence': 'MEDIUM',  # Default confidence
                        'risk_rating': 'MEDIUM',  # Default risk
                        'volatility_level': 'NORMAL'  # Default volatility
                    }
                    
                    # Get ML signal
                    ml_signal = self.signal_adapter.get_ml_signal(symbol)
                    
                    # Combine signals using adapter
                    combined_signal = self.signal_adapter.combine_signals(
                        symbol=symbol,
                        overnight_sentiment=overnight_sentiment,
                        ml_signal=ml_signal
                    )
                    
                    logger.info(
                        f"[OK] {symbol} Combined Signal: {combined_signal['action']} "
                        f"(score={combined_signal['combined_score']:.2f}, "
                        f"conf={combined_signal['confidence']:.2f}) | "
                        f"ML({combined_signal['ml_prediction']:.2f}) + "
                        f"Overnight({combined_signal['sentiment_score']:.1f})"
                    )
                    
                    # Convert to format expected by rest of code
                    return {
                        'prediction': 1 if combined_signal['action'] in ['BUY', 'STRONG_BUY'] else 0,
                        'confidence': combined_signal['confidence'] * 100,
                        'signal_strength': combined_signal['combined_score'] * 100,
                        'position_size': combined_signal['position_size'],
                        'source': 'Enhanced Adapter (75-85%)',
                        'symbol': symbol
                    }
                else:
                    logger.warning(f"[!] No overnight sentiment for {symbol}, falling back to ML-only")
                    # Fall through to ML-only
            
            # Use REAL swing signal generator if enabled (70-75% win rate)
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
                # FIX v1.3.15.179: Handle both numeric and string predictions
                prediction_value = enhanced_signal.get('prediction', 0)
                if isinstance(prediction_value, str):
                    # Old format: string action
                    prediction_numeric = 1 if prediction_value == 'BUY' else 0
                else:
                    # New format (v1.3.15.178+): numeric prediction
                    # Convert: 1.0 (BUY) -> 1, -1.0 (SELL) -> 0, 0.0 (HOLD) -> 0
                    prediction_numeric = 1 if prediction_value > 0 else 0
                
                return {
                    'prediction': prediction_numeric,
                    'confidence': enhanced_signal['confidence'] * 100,
                    'signal_strength': enhanced_signal['confidence'] * 100,
                    'components': enhanced_signal.get('components', {}),
                    'source': 'ML Swing Generator (70-75%)',
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
            
            # FIX v1.3.15.169: Ensure confidence is a float
            confidence = signal.get('confidence', 0)
            if isinstance(confidence, (list, np.ndarray)):
                confidence = float(confidence[0]) if len(confidence) > 0 else 0.0
            else:
                confidence = float(confidence)
            
            # Check if position should be boosted
            boost_threshold = self.config['cross_timeframe'].get('sentiment_boost_threshold', 70)
            if self.last_market_sentiment > boost_threshold:
                # Boost confidence
                confidence = min(100, confidence + 5)
                signal['confidence'] = confidence
                
                logger.info(
                    f"[=>] BOOSTED entry for {symbol} - "
                    f"Market sentiment {self.last_market_sentiment:.1f} > {boost_threshold}"
                )
            else:
                signal['confidence'] = confidence
            
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
            # SENTIMENT GATE CHECK - Block trades based on FinBERT sentiment
            if not signal.get('type') == 'MANUAL':  # Don't block manual trades
                # FIX v193.11.3: Pass price_data to avoid redundant yfinance call
                price_data = self.fetch_market_data(symbol, period="3mo")
                gate, position_multiplier, reason = self.should_allow_trade(symbol, signal, self.last_market_sentiment, price_data)
                
                # gate is boolean: True = allow, False = block
                if not gate:
                    logger.warning(f"{symbol}: TRADE BLOCKED - {reason}")
                    logger.warning(f"  -> Market Sentiment: {self.last_market_sentiment:.1f}/100")
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
                
                # FIX v193.11.3: Use position_multiplier already calculated above (avoid redundant call)
                # The should_allow_trade was already called at the gate check
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
                logger.info(f"{symbol}: Using manual stop_loss=USD{stop_loss:.2f}, take_profit=USD{profit_target:.2f if profit_target else 'None'}")
            else:
                # Calculate automatically (FIX v1.3.15.160: Use UI value if provided)
                stop_loss_pct = abs(self.ui_default_stop_loss) if self.ui_default_stop_loss is not None else self.config['swing_trading']['stop_loss_percent']
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
            logger.info(f"  Shares: {shares} @ USD{current_price:.2f}")
            logger.info(f"  Position Size: {position_size:.1%} (USD{cost:,.2f})")
            logger.info(f"  Stop Loss: USD{stop_loss:.2f} (-{stop_loss_pct}%)")
            logger.info(f"  Profit Target: USD{profit_target:.2f} (+8%)" if profit_target else "  No Profit Target")
            logger.info(f"  Target Exit: {holding_days} days")
            logger.info(f"  Regime: {regime}")
            logger.info(f"  Capital Remaining: USD{self.current_capital:,.2f}")
            
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
        """Update all open positions with current prices (v191: Enhanced logging)"""
        for symbol, position in list(self.positions.items()):
            logger.debug(f"[UPDATE] Fetching price for {symbol}...")
            current_price = self.fetch_current_price(symbol)
            
            if current_price:
                old_price = position.current_price
                position.current_price = current_price
                position.unrealized_pnl = (current_price - position.entry_price) * position.shares
                position.unrealized_pnl_pct = ((current_price - position.entry_price) / position.entry_price) * 100
                
                # Log price update
                if abs(current_price - old_price) > 0.01:  # Only log if price changed
                    logger.info(f"[UPDATE] {symbol}: USD{old_price:.2f} -> USD{current_price:.2f} ({position.unrealized_pnl_pct:+.2f}%)")
                
                # Update trailing stop
                if self.config['swing_trading']['use_trailing_stop']:
                    self._update_trailing_stop(position, current_price)
            else:
                logger.warning(f"[UPDATE] {symbol}: Could not fetch current price - position unchanged at USD{position.current_price:.2f}")
    
    def _update_trailing_stop(self, position: Position, current_price: float):
        """Update trailing stop"""
        # FIX v1.3.15.160: Use UI stop-loss if provided
        stop_loss_pct = abs(self.ui_default_stop_loss) if self.ui_default_stop_loss is not None else self.config['swing_trading']['stop_loss_percent']
        
        if current_price > position.entry_price:
            new_trailing = current_price * (1 - stop_loss_pct / 100)
            
            if new_trailing > position.trailing_stop:
                logger.info(f"{position.symbol}: Trailing stop USD{position.trailing_stop:.2f} -> USD{new_trailing:.2f}")
                position.trailing_stop = new_trailing
    
    def _get_ml_exit_signal(self, symbol: str, position: Position) -> Optional[Dict]:
        """
        Get ML-based exit signal for an open position (v1.3.15.184)
        
        Uses the same 5-component ML system (FinBERT + LSTM + Technical + Momentum + Volume)
        that identifies BUY signals, but now for intelligent SELL detection.
        
        Returns:
            ML signal dict with prediction, confidence, and component scores
            None if ML check fails or insufficient data
        """
        try:
            # Get historical price data (need 60+ days for LSTM)
            from yahooquery import Ticker
            
            ticker = Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)  # Extra buffer for weekends/holidays
            
            history = ticker.history(start=start_date, end=end_date, interval='1d')
            
            if history.empty or len(history) < 60:
                logger.debug(f"{symbol}: Insufficient data for ML exit check ({len(history)} days)")
                return None
            
            # Clean and prepare data
            if isinstance(history.index, pd.MultiIndex):
                history = history.reset_index(level=0, drop=True)
            
            price_data = history[['open', 'high', 'low', 'close', 'volume']].copy()
            price_data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            # Generate ML signal using the same system used for entries
            signal = self.swing_signal_generator.generate_signal(
                symbol=symbol,
                price_data=price_data,
                news_data=None,  # Could add news sentiment here
                current_date=None
            )
            
            return signal
            
        except Exception as e:
            logger.warning(f"{symbol}: ML exit signal generation failed: {e}")
            return None
    
    def check_exits(self) -> List[Tuple[str, str]]:
        """Check all positions for exit conditions (v1.3.15.184: ML-first, then mechanical)"""
        exits = []
        
        for symbol, position in self.positions.items():
            exit_reason = self._check_exit_conditions(position)
            
            if exit_reason:
                exits.append((symbol, exit_reason))
        
        return exits
    
    def _check_exit_conditions(self, position: Position) -> Optional[str]:
        """Check if position should be exited (v1.3.15.184: ML-based exits with mechanical fallbacks)"""
        price = position.current_price
        current_profit_pct = position.unrealized_pnl_pct
        symbol = position.symbol
        
        # v1.3.15.184: PRIMARY CHECK - ML-based SELL signal
        use_ml_exits = self.config['swing_trading'].get('use_ml_exits', True)
        ml_exit_confidence_threshold = self.config['swing_trading'].get('ml_exit_confidence_threshold', 0.60)
        
        if use_ml_exits and self.swing_signal_generator:
            try:
                # Get fresh price data for ML analysis
                ml_signal = self._get_ml_exit_signal(symbol, position)
                
                if ml_signal and ml_signal['prediction'] == 'SELL':
                    confidence = ml_signal['confidence']
                    combined_score = ml_signal['combined_score']
                    
                    # Only exit if ML confidence is high enough
                    if confidence >= ml_exit_confidence_threshold:
                        logger.info(
                            f"[ML_EXIT] {symbol}: SELL signal detected | "
                            f"Confidence: {confidence:.1%} | Score: {combined_score:.3f} | "
                            f"Sentiment: {ml_signal['components'].get('sentiment', 0):.2f} | "
                            f"LSTM: {ml_signal['components'].get('lstm', 0):.2f} | "
                            f"Technical: {ml_signal['components'].get('technical', 0):.2f}"
                        )
                        return f"ML_SELL_{int(confidence*100)}%"
                    else:
                        logger.debug(
                            f"{symbol}: ML SELL signal but confidence {confidence:.1%} < {ml_exit_confidence_threshold:.1%}, using mechanical rules"
                        )
            except Exception as e:
                logger.warning(f"{symbol}: ML exit check failed: {e}, using mechanical rules")
        
        # SECONDARY CHECKS - Mechanical safety exits (always enforced)
        # FIX v193.11.6.21: Dynamic stop-loss respects current UI setting
        # Calculate stop-loss based on CURRENT UI setting, not just entry-time static value
        stop_loss_pct = abs(self.ui_default_stop_loss) if self.ui_default_stop_loss is not None else self.config['swing_trading']['stop_loss_percent']
        dynamic_stop_loss = position.entry_price * (1 - stop_loss_pct / 100)
        
        # Use the TIGHTER of: entry stop_loss OR current UI setting
        # This ensures: tightening stop-loss after entry works, loosening doesn't override (safer)
        effective_stop_loss = max(position.stop_loss, dynamic_stop_loss)
        
        if price <= effective_stop_loss:
            # Calculate actual loss percentage
            loss_pct = ((price - position.entry_price) / position.entry_price) * 100
            
            # Log which stop triggered for diagnostics
            if effective_stop_loss == dynamic_stop_loss:
                logger.info(f"[STOP-LOSS] {symbol}: Dynamic stop triggered at USD{price:.2f} (loss: {abs(loss_pct):.2f}%, UI setting: {stop_loss_pct}%)")
                return f"STOP_LOSS_DYNAMIC_{abs(int(loss_pct))}%"
            else:
                entry_stop_pct = (1 - position.stop_loss/position.entry_price)*100
                logger.info(f"[STOP-LOSS] {symbol}: Entry stop triggered at USD{price:.2f} (loss: {abs(loss_pct):.2f}%, entry setting: {entry_stop_pct:.1f}%)")
                return f"STOP_LOSS_STATIC_{abs(int(loss_pct))}%"
        
        # v1.3.15.183: Relax trailing stop for profitable trending positions
        disable_time_exit = self.config['swing_trading'].get('disable_time_exit_for_winners', True)
        min_profit_threshold = self.config['swing_trading'].get('min_profit_to_hold', 5.0)
        
        # Trailing stop - but allow wider tolerance for winners
        if price <= position.trailing_stop:
            # v1.3.15.183: If position is profitable above threshold, ignore trailing stop
            if disable_time_exit and current_profit_pct >= min_profit_threshold:
                logger.debug(f"{position.symbol}: Trailing stop hit but profit {current_profit_pct:.1f}% >= {min_profit_threshold}%, holding")
            else:
                return "TRAILING_STOP"
        
        # Profit target
        if position.profit_target and price >= position.profit_target:
            holding_days = (datetime.now() - datetime.fromisoformat(position.entry_date)).days
            if holding_days >= 2:
                return "PROFIT_TARGET_8%"
            elif price >= position.entry_price * 1.12:
                return "QUICK_PROFIT_12%"
        
        # Target exit date - v1.3.15.183: Skip if position is profitable
        if position.target_exit_date:
            if datetime.now() >= datetime.fromisoformat(position.target_exit_date):
                # v1.3.15.183: Don't exit profitable positions on time alone
                if disable_time_exit and current_profit_pct >= min_profit_threshold:
                    logger.info(f"{position.symbol}: Holding period expired but profit {current_profit_pct:.1f}% >= {min_profit_threshold}%, extending hold")
                    # Extend target exit by another period
                    new_exit = datetime.now() + timedelta(days=self.config['swing_trading']['holding_period_days'])
                    position.target_exit_date = new_exit.isoformat()
                    return None
                else:
                    holding_days = (datetime.now() - datetime.fromisoformat(position.entry_date)).days
                    return f"TARGET_EXIT_{holding_days}d"
        
        # Intraday breakdown early exit - v1.3.15.183: Only exit if profit is below threshold
        if self.config['cross_timeframe']['use_intraday_for_exits']:
            if self.last_market_sentiment < 20:
                # v1.3.15.183: More aggressive exit logic - only if sentiment crashes
                if current_profit_pct < min_profit_threshold:
                    return "INTRADAY_BREAKDOWN"
                else:
                    logger.debug(f"{position.symbol}: Sentiment low but profit {current_profit_pct:.1f}% >= {min_profit_threshold}%, holding")
        
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
            logger.info(f"  Entry: USD{position.entry_price:.2f} -> Exit: USD{exit_price:.2f}")
            logger.info(f"  P&L: USD{pnl:+,.2f} ({pnl_pct:+.2f}%)")
            logger.info(f"  Capital: USD{self.current_capital:,.2f}")
            
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
            
                # Check market hours for all symbols
            if MARKET_CALENDAR_AVAILABLE and market_calendar:
                closed_symbols = []
                for symbol in self.symbols:
                    can_trade, reason = market_calendar.can_trade_symbol(symbol)
                    if not can_trade:
                        closed_symbols.append(f"{symbol} ({reason})")
                
                if closed_symbols:
                    logger.warning(f"[CALENDAR] Some markets are closed:")
                    for msg in closed_symbols:
                        logger.warning(f"   {msg}")
                    # Continue with open markets only
            
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
                    logger.info("[SCAN] Running intraday scan...")
                    alerts = self.intraday_scanner.scan_for_opportunities(
                        symbols=self.symbols,
                        price_data_provider=self.fetch_market_data
                    )
                    self.last_intraday_scan = datetime.now()
                    
                    if alerts:
                        logger.info(f"   Found {len(alerts)} intraday alerts")
                        for alert in alerts:
                            logger.info(f"   [!] {alert.symbol}: {alert.alert_type} (strength={alert.signal_strength:.1f})")
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
            
                # 6. Check for updated pipeline reports and process recommendations
            if self._check_for_updated_reports():
                logger.info("[PIPELINE] Processing fresh pipeline recommendations...")
                self._process_pipeline_recommendations()
            
                # 7. Look for new entries
            if len(self.positions) < self.config['risk_management']['max_total_positions']:
                logger.info("[SCAN] Scanning for new entry opportunities...")
                
                for symbol in self.symbols:
                    if symbol in self.positions:
                        continue
                    
                    should_enter, confidence, signal = self.evaluate_entry(symbol)
                    
                    if should_enter:
                        logger.info(f"[OK] Entry signal for {symbol} - confidence {confidence:.2f}")
                        self.enter_position(symbol, signal)
            
            # 8. Print status
            self.print_status()
            
        except Exception as e:
            logger.error(f"[ERROR] Exception in trading cycle: {e}")
            logger.error(f"[ERROR] Traceback: ", exc_info=True)
            logger.warning(f"[WARN]  Trading cycle failed but loop will continue")
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
        logger.info(f"Total Capital: USD{total_capital:,.2f} ({total_return:+.2f}%)")
        logger.info(f"  Cash: USD{self.current_capital:,.2f}")
        logger.info(f"  Invested: USD{total_value:,.2f}")
        logger.info(f"  Unrealized P&L: USD{total_unrealized_pnl:+,.2f}")
        logger.info(f"")
        logger.info(f"Open Positions: {len(self.positions)}")
        for symbol, pos in self.positions.items():
            logger.info(f"  {symbol}: {pos.shares} shares @ USD{pos.entry_price:.2f} | "
                       f"Current: USD{pos.current_price:.2f} | P&L: {pos.unrealized_pnl_pct:+.2f}%")
        logger.info(f"")
        logger.info(f"Performance:")
        logger.info(f"  Total Trades: {self.metrics['total_trades']}")
        logger.info(f"  Win Rate: {win_rate:.1f}%")
        logger.info(f"  Realized P&L: USD{self.metrics['total_pnl']:+,.2f}")
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
        logger.info(f"Initial Capital: USD{self.initial_capital:,.2f}")
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
