"""
Pipeline Signal Adapter - Integrate Morning Reports into Trading System
========================================================================

Connects the overnight pipeline morning reports (AU/US/UK) to the automated
trading system, converting sentiment scores into actionable buy/sell signals
with flexible position sizing based on opportunity/risk levels.

Features:
- Reads morning report sentiment scores from pipeline_trading
- Converts sentiment to trading signals (BUY/SELL/NEUTRAL)
- Adjusts position sizing based on confidence levels
- Provides risk override mechanisms for significant opportunities/threats
- Integrates with paper_trading_coordinator for execution

Usage:
    from pipeline_signal_adapter import PipelineSignalAdapter
    
    adapter = PipelineSignalAdapter()
    signals = adapter.get_morning_signals()
    
    for signal in signals:
        if signal['action'] == 'BUY':
            coordinator.enter_position(signal['symbol'], signal)
"""

import logging
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import pandas as pd
import pytz

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add pipeline_trading to path
PIPELINE_TRADING_PATH = Path(__file__).parent.parent / 'pipeline_trading'
sys.path.insert(0, str(PIPELINE_TRADING_PATH))
sys.path.insert(0, str(PIPELINE_TRADING_PATH / 'models'))


@dataclass
class PipelineSentiment:
    """Pipeline sentiment data"""
    market: str  # 'AU', 'US', 'UK'
    timestamp: datetime
    sentiment_score: float  # 0-100
    recommendation: str  # 'STRONG_BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG_SELL'
    confidence: str  # 'HIGH', 'MODERATE', 'LOW'
    predicted_gap: float  # Predicted opening gap percentage
    volatility_level: str  # 'Very Low', 'Normal', 'Elevated', 'High'
    risk_rating: str  # 'Low', 'Moderate', 'Elevated', 'High'
    overnight_data: Dict  # Raw overnight indicator data


@dataclass
class TradingSignal:
    """Trading signal generated from pipeline sentiment"""
    action: str  # 'BUY', 'SELL', 'HOLD', 'REDUCE'
    symbol: str
    market: str
    base_position_size: float  # 0.0-1.0 (fraction of normal position)
    adjusted_position_size: float  # After confidence/risk adjustments
    confidence: float  # 0-100
    entry_reason: str
    risk_level: str
    stop_loss_pct: float
    take_profit_pct: float
    sentiment_score: float
    pipeline_recommendation: str
    metadata: Dict


class PipelineSignalAdapter:
    """
    Adapter that reads overnight pipeline sentiment and converts it to
    trading signals for the automated trading system.
    """
    
    def __init__(
        self,
        pipeline_base_path: Optional[Path] = None,
        config_path: Optional[str] = None
    ):
        """
        Initialize pipeline signal adapter
        
        Args:
            pipeline_base_path: Path to pipeline_trading directory
            config_path: Path to signal configuration file
        """
        self.pipeline_base_path = pipeline_base_path or PIPELINE_TRADING_PATH
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Market presets from pipeline
        self.market_presets = self._load_market_presets()
        
        # Cache for morning reports
        self.cached_sentiments = {}
        self.cache_timestamp = None
        self.cache_ttl = timedelta(minutes=30)  # Cache for 30 minutes
        
        logger.info("[OK] Pipeline Signal Adapter initialized")
        logger.info(f"  Pipeline path: {self.pipeline_base_path}")
        logger.info(f"  Markets tracked: {', '.join(self.market_presets.keys())}")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load signal adapter configuration"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            "sentiment_thresholds": {
                "strong_buy": 70,
                "buy": 60,
                "neutral_high": 55,
                "neutral_low": 45,
                "sell": 40,
                "strong_sell": 30
            },
            "position_sizing": {
                "strong_buy": 1.5,  # 150% of normal (opportunity mode)
                "buy": 1.0,  # 100% of normal
                "neutral": 0.5,  # 50% of normal (cautious)
                "sell": 0.0,  # No new positions
                "strong_sell": 0.0  # No new positions, consider exits
            },
            "confidence_multipliers": {
                "HIGH": 1.2,  # 20% boost for high confidence
                "MODERATE": 1.0,  # No adjustment
                "LOW": 0.7  # 30% reduction for low confidence
            },
            "risk_adjustments": {
                "Low": 1.1,  # Slightly more aggressive in low risk
                "Moderate": 1.0,  # Normal sizing
                "Elevated": 0.8,  # More cautious
                "High": 0.5  # Very defensive
            },
            "volatility_adjustments": {
                "Very Low": 1.1,  # Can be more aggressive
                "Normal": 1.0,
                "Elevated": 0.85,
                "High": 0.6  # Very cautious in high volatility
            },
            "stop_loss_scaling": {
                "Very Low": 0.02,  # 2% in calm markets
                "Normal": 0.03,  # 3% normal
                "Elevated": 0.04,  # 4% in volatile markets
                "High": 0.06  # 6% wide stops in high vol
            },
            "take_profit_scaling": {
                "strong_buy": 0.08,  # 8% target for strong conviction
                "buy": 0.05,  # 5% normal target
                "neutral": 0.03  # 3% quick profit in uncertainty
            },
            "max_position_size": 0.30,  # 30% max of portfolio per position
            "min_position_size": 0.05,  # 5% minimum position size
            "enable_opportunity_mode": True,  # Allow oversized positions for strong signals
            "enable_risk_override": True  # Allow defensive overrides
        }
    
    def _load_market_presets(self) -> Dict:
        """Load market-specific stock presets"""
        presets = {}
        
        # AU Market Presets
        presets['AU'] = {
            'timezone': 'Australia/Sydney',
            'symbols': [
                'CBA.AX', 'BHP.AX', 'CSL.AX', 'NAB.AX', 'WBC.AX',
                'ANZ.AX', 'WES.AX', 'MQG.AX', 'WOW.AX', 'FMG.AX'
            ],
            'sectors': ['Financials', 'Materials', 'Healthcare']
        }
        
        # US Market Presets
        presets['US'] = {
            'timezone': 'America/New_York',
            'symbols': [
                'SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL',
                'AMZN', 'NVDA', 'META', 'TSLA', 'JPM'
            ],
            'sectors': ['Technology', 'Financials', 'Healthcare']
        }
        
        # UK Market Presets
        presets['UK'] = {
            'timezone': 'Europe/London',
            'symbols': [
                'HSBA.L', 'BP.L', 'SHEL.L', 'AZN.L', 'GSK.L',
                'ULVR.L', 'RIO.L', 'LSEG.L', 'DGE.L', 'NG.L'
            ],
            'sectors': ['Financials', 'Energy', 'Healthcare']
        }
        
        return presets
    
    def get_morning_sentiment(self, market: str) -> Optional[PipelineSentiment]:
        """
        Get overnight sentiment for a specific market
        
        Args:
            market: Market code ('AU', 'US', 'UK')
            
        Returns:
            PipelineSentiment or None if unavailable
        """
        # Check cache
        if self._is_cache_valid() and market in self.cached_sentiments:
            logger.debug(f"Using cached sentiment for {market}")
            return self.cached_sentiments[market]
        
        # Import market monitor based on market
        try:
            if market == 'AU':
                sys.path.insert(0, str(self.pipeline_base_path / "models" / "screening")); from spi_monitor import SPIMonitor
                monitor = SPIMonitor()
                data = monitor.get_overnight_summary()
                
                sentiment = PipelineSentiment(
                    market='AU',
                    timestamp=datetime.now(pytz.timezone('Australia/Sydney')),
                    sentiment_score=data['sentiment_score'],
                    recommendation=data['recommendation']['stance'],
                    confidence=data['recommendation'].get('confidence', 'MODERATE'),
                    predicted_gap=data['gap_prediction']['predicted_gap_pct'],
                    volatility_level='Normal',  # SPI doesn't have direct vol measure
                    risk_rating=data['recommendation']['risk_level'],
                    overnight_data=data
                )
                
            elif market == 'US':
                sys.path.insert(0, str(self.pipeline_base_path / "models" / "screening")); from us_market_monitor import USMarketMonitor
                monitor = USMarketMonitor()
                data = monitor.get_market_overview()
                
                sentiment = PipelineSentiment(
                    market='US',
                    timestamp=datetime.now(pytz.timezone('America/New_York')),
                    sentiment_score=data['overall_sentiment'],
                    recommendation=data['recommendation']['stance'],
                    confidence=data['recommendation'].get('confidence', 'MODERATE'),
                    predicted_gap=0.0,  # US doesn't predict gap, it's live market
                    volatility_level=data['vix']['level'],
                    risk_rating=data['vix']['risk_rating'],
                    overnight_data=data
                )
                
            elif market == 'UK':
                # Import directly to avoid circular imports
                sys.path.insert(0, str(self.pipeline_base_path / 'models' / 'screening'))
                from uk_market_monitor import UKMarketMonitor
                monitor = UKMarketMonitor()
                data = monitor.get_market_overview()
                
                sentiment = PipelineSentiment(
                    market='UK',
                    timestamp=datetime.now(pytz.timezone('Europe/London')),
                    sentiment_score=data['overall_sentiment'],
                    recommendation=data['recommendation']['stance'],
                    confidence=data['recommendation'].get('confidence', 'MODERATE'),
                    predicted_gap=data['us_overnight_impact'].get('predicted_ftse_impact_pct', 0.0),
                    volatility_level=data['volatility']['level'],
                    risk_rating=data['volatility']['risk_rating'],
                    overnight_data=data
                )
            else:
                logger.error(f"Unknown market: {market}")
                return None
            
            # Cache the result
            self.cached_sentiments[market] = sentiment
            self.cache_timestamp = datetime.now()
            
            return sentiment
            
        except Exception as e:
            logger.error(f"Error fetching {market} sentiment: {e}")
            return None
    
    def _is_cache_valid(self) -> bool:
        """Check if cached sentiments are still valid"""
        if not self.cache_timestamp:
            return False
        return datetime.now() - self.cache_timestamp < self.cache_ttl
    
    def generate_trading_signals(
        self,
        market: str,
        max_signals: int = 5
    ) -> List[TradingSignal]:
        """
        Generate trading signals based on morning sentiment
        
        Args:
            market: Market code ('AU', 'US', 'UK')
            max_signals: Maximum number of signals to generate
            
        Returns:
            List of TradingSignal objects
        """
        sentiment = self.get_morning_sentiment(market)
        if not sentiment:
            logger.warning(f"No sentiment available for {market}")
            return []
        
        logger.info("="*60)
        logger.info(f"GENERATING TRADING SIGNALS - {market} Market")
        logger.info("="*60)
        logger.info(f"Sentiment Score: {sentiment.sentiment_score:.1f}/100")
        logger.info(f"Recommendation: {sentiment.recommendation}")
        logger.info(f"Confidence: {sentiment.confidence}")
        logger.info(f"Risk Rating: {sentiment.risk_rating}")
        logger.info(f"Volatility: {sentiment.volatility_level}")
        
        signals = []
        
        # Determine action based on sentiment score
        action = self._sentiment_to_action(sentiment.sentiment_score)
        
        # Skip if no action warranted
        if action in ['HOLD', 'REDUCE'] and sentiment.recommendation not in ['STRONG_BUY', 'STRONG_SELL']:
            logger.info(f"No strong signals for {market} - Action: {action}")
            return signals
        
        # Get symbols for this market
        symbols = self.market_presets[market]['symbols'][:max_signals]
        
        for symbol in symbols:
            signal = self._create_trading_signal(
                symbol=symbol,
                market=market,
                sentiment=sentiment,
                action=action
            )
            
            if signal:
                signals.append(signal)
        
        logger.info(f"Generated {len(signals)} signals for {market}")
        return signals
    
    def _sentiment_to_action(self, sentiment_score: float) -> str:
        """Convert sentiment score to trading action"""
        thresholds = self.config['sentiment_thresholds']
        
        if sentiment_score >= thresholds['strong_buy']:
            return 'BUY'  # Strong opportunity
        elif sentiment_score >= thresholds['buy']:
            return 'BUY'  # Normal buy
        elif sentiment_score <= thresholds['strong_sell']:
            return 'SELL'  # Strong risk - exit positions
        elif sentiment_score <= thresholds['sell']:
            return 'REDUCE'  # Reduce exposure
        else:
            return 'HOLD'  # No clear direction
    
    def _create_trading_signal(
        self,
        symbol: str,
        market: str,
        sentiment: PipelineSentiment,
        action: str
    ) -> Optional[TradingSignal]:
        """
        Create a trading signal for a specific symbol
        
        Args:
            symbol: Stock symbol
            market: Market code
            sentiment: Pipeline sentiment data
            action: Trading action ('BUY', 'SELL', 'REDUCE', 'HOLD')
            
        Returns:
            TradingSignal or None
        """
        # Calculate base position size
        base_size = self._calculate_base_position_size(sentiment)
        
        # Apply confidence multiplier
        confidence_mult = self.config['confidence_multipliers'].get(sentiment.confidence, 1.0)
        
        # Apply risk adjustment
        risk_mult = self.config['risk_adjustments'].get(sentiment.risk_rating, 1.0)
        
        # Apply volatility adjustment
        vol_mult = self.config['volatility_adjustments'].get(sentiment.volatility_level, 1.0)
        
        # Calculate adjusted position size
        adjusted_size = base_size * confidence_mult * risk_mult * vol_mult
        
        # Apply limits
        adjusted_size = max(
            self.config['min_position_size'],
            min(adjusted_size, self.config['max_position_size'])
        )
        
        # Skip if adjusted size is too small and not a sell signal
        if adjusted_size < self.config['min_position_size'] and action != 'SELL':
            logger.debug(f"Skipping {symbol} - position size too small ({adjusted_size:.2%})")
            return None
        
        # Calculate stop loss based on volatility
        stop_loss_pct = self.config['stop_loss_scaling'].get(sentiment.volatility_level, 0.03)
        
        # Calculate take profit based on conviction
        if sentiment.sentiment_score >= self.config['sentiment_thresholds']['strong_buy']:
            take_profit_pct = self.config['take_profit_scaling']['strong_buy']
        elif sentiment.sentiment_score >= self.config['sentiment_thresholds']['buy']:
            take_profit_pct = self.config['take_profit_scaling']['buy']
        else:
            take_profit_pct = self.config['take_profit_scaling']['neutral']
        
        # Build entry reason
        entry_reason = f"{market} Morning Signal: {sentiment.recommendation} " \
                      f"(Sentiment {sentiment.sentiment_score:.0f}, " \
                      f"Gap {sentiment.predicted_gap:+.2f}%)"
        
        signal = TradingSignal(
            action=action,
            symbol=symbol,
            market=market,
            base_position_size=base_size,
            adjusted_position_size=adjusted_size,
            confidence=sentiment.sentiment_score,
            entry_reason=entry_reason,
            risk_level=sentiment.risk_rating,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
            sentiment_score=sentiment.sentiment_score,
            pipeline_recommendation=sentiment.recommendation,
            metadata={
                'volatility_level': sentiment.volatility_level,
                'predicted_gap': sentiment.predicted_gap,
                'confidence_level': sentiment.confidence,
                'overnight_data_timestamp': sentiment.timestamp.isoformat()
            }
        )
        
        return signal
    
    def _calculate_base_position_size(self, sentiment: PipelineSentiment) -> float:
        """Calculate base position size from sentiment"""
        score = sentiment.sentiment_score
        thresholds = self.config['sentiment_thresholds']
        sizing = self.config['position_sizing']
        
        if score >= thresholds['strong_buy']:
            base_size = sizing['strong_buy'] * 0.20  # 20% * 1.5 = 30% max
        elif score >= thresholds['buy']:
            base_size = sizing['buy'] * 0.20  # 20% * 1.0 = 20%
        elif score >= thresholds['neutral_high'] or score <= thresholds['neutral_low']:
            base_size = sizing['neutral'] * 0.20  # 20% * 0.5 = 10%
        else:
            base_size = 0.10  # 10% for weak signals
        
        return base_size
    
    def get_all_market_signals(
        self,
        markets: Optional[List[str]] = None,
        max_signals_per_market: int = 3
    ) -> Dict[str, List[TradingSignal]]:
        """
        Get trading signals for all markets
        
        Args:
            markets: List of markets ('AU', 'US', 'UK'), None = all
            max_signals_per_market: Max signals per market
            
        Returns:
            Dictionary of {market: [signals]}
        """
        if markets is None:
            markets = ['AU', 'US', 'UK']
        
        all_signals = {}
        
        for market in markets:
            try:
                signals = self.generate_trading_signals(market, max_signals_per_market)
                if signals:
                    all_signals[market] = signals
            except Exception as e:
                logger.error(f"Error generating signals for {market}: {e}")
                continue
        
        return all_signals
    
    def format_signals_for_coordinator(
        self,
        signals: List[TradingSignal]
    ) -> List[Dict]:
        """
        Format signals for paper_trading_coordinator compatibility
        
        Args:
            signals: List of TradingSignal objects
            
        Returns:
            List of signal dictionaries compatible with coordinator
        """
        formatted = []
        
        for signal in signals:
            formatted_signal = {
                'symbol': signal.symbol,
                'action': signal.action,
                'signal': 'BUY' if signal.action == 'BUY' else 'SELL',
                'confidence': signal.confidence / 100.0,  # Convert to 0-1
                'position_size': signal.adjusted_position_size,
                'stop_loss': signal.stop_loss_pct,
                'take_profit': signal.take_profit_pct,
                'reason': signal.entry_reason,
                'source': 'pipeline_adapter',
                'market': signal.market,
                'sentiment_score': signal.sentiment_score,
                'risk_level': signal.risk_level,
                'pipeline_recommendation': signal.pipeline_recommendation,
                'metadata': signal.metadata
            }
            formatted.append(formatted_signal)
        
        return formatted


# ============================================================================
# TEST HARNESS
# ============================================================================

def test_pipeline_signal_adapter():
    """Test the pipeline signal adapter"""
    print("\n" + "="*80)
    print("PIPELINE SIGNAL ADAPTER TEST")
    print("="*80 + "\n")
    
    # Initialize adapter
    adapter = PipelineSignalAdapter()
    
    # Test each market
    for market in ['AU', 'US', 'UK']:
        print(f"\n{'-'*80}")
        print(f"Testing {market} Market")
        print('-'*80)
        
        try:
            # Get sentiment
            sentiment = adapter.get_morning_sentiment(market)
            if sentiment:
                print(f"[OK] Sentiment fetched: {sentiment.sentiment_score:.1f}/100")
                print(f"  Recommendation: {sentiment.recommendation}")
                print(f"  Confidence: {sentiment.confidence}")
                print(f"  Risk: {sentiment.risk_rating}")
                print(f"  Volatility: {sentiment.volatility_level}")
                
                # Generate signals
                signals = adapter.generate_trading_signals(market, max_signals=3)
                print(f"\n[OK] Generated {len(signals)} trading signals")
                
                for i, signal in enumerate(signals, 1):
                    print(f"\n  Signal {i}: {signal.symbol}")
                    print(f"    Action: {signal.action}")
                    print(f"    Position Size: {signal.adjusted_position_size:.1%}")
                    print(f"    Stop Loss: {signal.stop_loss_pct:.1%}")
                    print(f"    Take Profit: {signal.take_profit_pct:.1%}")
                    print(f"    Reason: {signal.entry_reason[:60]}...")
            else:
                print(f"[X] No sentiment available for {market}")
                
        except Exception as e:
            print(f"[X] Error testing {market}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("Test complete")
    print("="*80)


if __name__ == "__main__":
    test_pipeline_signal_adapter()
