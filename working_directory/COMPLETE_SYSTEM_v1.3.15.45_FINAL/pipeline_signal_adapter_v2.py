"""
Pipeline Signal Adapter V2 - Updated for New Pipeline Structure
================================================================

Integrates the NEW complete overnight pipelines (run_us_full_pipeline.py, 
run_uk_full_pipeline.py, run_au_pipeline_v1.3.13.py) with the existing
live trading system.

Changes from V1:
- Reads from pipeline JSON reports instead of live monitors
- Supports new pipeline output format (FinBERT, LSTM, Event Risk, Regime)
- Extracts richer sentiment data
- Compatible with existing trading coordinator

Usage:
    from pipeline_signal_adapter_v2 import PipelineSignalAdapterV2
    
    adapter = PipelineSignalAdapterV2()
    signals = adapter.get_morning_signals()
"""

import logging
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import pytz

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class PipelineSentiment:
    """Pipeline sentiment data from new pipeline structure"""
    market: str
    timestamp: datetime
    sentiment_score: float  # 0-100
    recommendation: str
    confidence: str
    predicted_gap: float
    volatility_level: str
    risk_rating: str
    top_opportunities: List[Dict]  # NEW: From pipeline results
    regime_data: Dict  # NEW: Market regime information
    overnight_data: Dict


@dataclass
class TradingSignal:
    """Trading signal generated from pipeline sentiment"""
    action: str
    symbol: str
    market: str
    base_position_size: float
    adjusted_position_size: float
    confidence: float
    entry_reason: str
    risk_level: str
    stop_loss_pct: float
    take_profit_pct: float
    sentiment_score: float
    pipeline_recommendation: str
    metadata: Dict


class PipelineSignalAdapterV2:
    """
    Adapter V2 that reads NEW overnight pipeline JSON reports and converts
    them to trading signals for the automated trading system.
    """
    
    def __init__(
        self,
        reports_base_path: Optional[Path] = None,
        config_path: Optional[str] = None
    ):
        """
        Initialize pipeline signal adapter V2
        
        Args:
            reports_base_path: Path to pipeline reports directory
            config_path: Path to signal configuration file
        """
        self.reports_base_path = reports_base_path or Path('reports/screening')
        self.reports_base_path.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Market presets
        self.market_presets = self._load_market_presets()
        
        # Cache
        self.cached_sentiments = {}
        self.cache_timestamp = None
        self.cache_ttl = timedelta(hours=12)  # Cache for 12 hours (morning reports valid all day)
        
        logger.info("[OK] Pipeline Signal Adapter V2 initialized")
        logger.info(f"  Reports path: {self.reports_base_path}")
        logger.info(f"  Markets tracked: {', '.join(self.market_presets.keys())}")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load signal adapter configuration"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration (same as V1)
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
                "strong_buy": 1.5,
                "buy": 1.0,
                "neutral": 0.5,
                "sell": 0.0,
                "strong_sell": 0.0
            },
            "confidence_multipliers": {
                "HIGH": 1.2,
                "MODERATE": 1.0,
                "LOW": 0.7
            },
            "risk_adjustments": {
                "Low": 1.1,
                "Moderate": 1.0,
                "Elevated": 0.8,
                "High": 0.5
            },
            "volatility_adjustments": {
                "Very Low": 1.1,
                "Normal": 1.0,
                "Elevated": 0.85,
                "High": 0.6
            },
            "stop_loss_scaling": {
                "Very Low": 0.02,
                "Normal": 0.03,
                "Elevated": 0.04,
                "High": 0.06
            },
            "take_profit_scaling": {
                "strong_buy": 0.08,
                "buy": 0.05,
                "neutral": 0.03
            },
            "max_position_size": 0.30,
            "min_position_size": 0.05,
            "enable_opportunity_mode": True,
            "enable_risk_override": True
        }
    
    def _load_market_presets(self) -> Dict:
        """Load market-specific stock presets"""
        presets = {}
        
        presets['AU'] = {
            'timezone': 'Australia/Sydney',
            'symbols': [
                'CBA.AX', 'BHP.AX', 'CSL.AX', 'NAB.AX', 'WBC.AX',
                'ANZ.AX', 'WES.AX', 'MQG.AX', 'WOW.AX', 'FMG.AX'
            ],
            'sectors': ['Financials', 'Materials', 'Healthcare']
        }
        
        presets['US'] = {
            'timezone': 'America/New_York',
            'symbols': [
                'SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL',
                'AMZN', 'NVDA', 'META', 'TSLA', 'JPM'
            ],
            'sectors': ['Technology', 'Financials', 'Healthcare']
        }
        
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
        Get overnight sentiment from NEW pipeline JSON reports
        
        Args:
            market: Market code ('AU', 'US', 'UK')
            
        Returns:
            PipelineSentiment or None if unavailable
        """
        # Check cache
        if self._is_cache_valid() and market in self.cached_sentiments:
            logger.debug(f"Using cached sentiment for {market}")
            return self.cached_sentiments[market]
        
        # Look for morning report
        report_path = self.reports_base_path / f'{market.lower()}_morning_report.json'
        
        if not report_path.exists():
            logger.warning(f"No morning report found for {market}: {report_path}")
            logger.info(f"  Pipeline may not have run yet")
            logger.info(f"  Expected path: {report_path.absolute()}")
            return None
        
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)
            
            logger.info(f"[OK] Found morning report for {market}")
            logger.debug(f"  Report timestamp: {data.get('timestamp')}")
            
            # Extract sentiment from NEW pipeline format
            market_sentiment = data.get('market_sentiment', {})
            volatility = data.get('volatility', {})
            risk = data.get('risk', {})
            
            sentiment = PipelineSentiment(
                market=market,
                timestamp=datetime.fromisoformat(data['timestamp']),
                sentiment_score=market_sentiment.get('score', 50),
                recommendation=market_sentiment.get('recommendation', 'NEUTRAL'),
                confidence=market_sentiment.get('confidence', 'MODERATE'),
                predicted_gap=market_sentiment.get('predicted_gap_pct', 0.0),
                volatility_level=volatility.get('level', 'Normal'),
                risk_rating=risk.get('rating', 'Moderate'),
                top_opportunities=data.get('top_opportunities', []),
                regime_data=data.get('regime_data', {}),
                overnight_data=data
            )
            
            # Cache the result
            self.cached_sentiments[market] = sentiment
            self.cache_timestamp = datetime.now()
            
            logger.info(f"  Sentiment: {sentiment.sentiment_score:.1f}/100")
            logger.info(f"  Recommendation: {sentiment.recommendation}")
            logger.info(f"  Top opportunities: {len(sentiment.top_opportunities)}")
            
            return sentiment
            
        except Exception as e:
            logger.error(f"Error reading {market} morning report: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _is_cache_valid(self) -> bool:
        """Check if cached sentiments are still valid"""
        if not self.cache_timestamp:
            return False
        return datetime.now() - self.cache_timestamp < self.cache_ttl
    
    def generate_trading_signals(
        self,
        market: str,
        max_signals: int = 5,
        use_pipeline_opportunities: bool = True
    ) -> List[TradingSignal]:
        """
        Generate trading signals based on morning sentiment
        
        Args:
            market: Market code ('AU', 'US', 'UK')
            max_signals: Maximum number of signals to generate
            use_pipeline_opportunities: Use top opportunities from pipeline instead of presets
            
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
        
        # Determine action
        action = self._sentiment_to_action(sentiment.sentiment_score)
        
        # Skip if no action warranted
        if action in ['HOLD', 'REDUCE'] and sentiment.recommendation not in ['STRONG_BUY', 'STRONG_SELL']:
            logger.info(f"No strong signals for {market} - Action: {action}")
            return signals
        
        # Get symbols - prefer pipeline top opportunities
        if use_pipeline_opportunities and sentiment.top_opportunities:
            logger.info(f"Using pipeline top opportunities ({len(sentiment.top_opportunities)} stocks)")
            symbols = [opp['symbol'] for opp in sentiment.top_opportunities[:max_signals]]
        else:
            logger.info(f"Using market presets")
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
            return 'BUY'
        elif sentiment_score >= thresholds['buy']:
            return 'BUY'
        elif sentiment_score <= thresholds['strong_sell']:
            return 'SELL'
        elif sentiment_score <= thresholds['sell']:
            return 'REDUCE'
        else:
            return 'HOLD'
    
    def _create_trading_signal(
        self,
        symbol: str,
        market: str,
        sentiment: PipelineSentiment,
        action: str
    ) -> Optional[TradingSignal]:
        """Create a trading signal for a specific symbol"""
        # Calculate base position size
        base_size = self._calculate_base_position_size(sentiment)
        
        # Apply multipliers
        confidence_mult = self.config['confidence_multipliers'].get(sentiment.confidence, 1.0)
        risk_mult = self.config['risk_adjustments'].get(sentiment.risk_rating, 1.0)
        vol_mult = self.config['volatility_adjustments'].get(sentiment.volatility_level, 1.0)
        
        # Calculate adjusted position size
        adjusted_size = base_size * confidence_mult * risk_mult * vol_mult
        
        # Apply limits
        adjusted_size = max(
            self.config['min_position_size'],
            min(adjusted_size, self.config['max_position_size'])
        )
        
        # Skip if too small and not a sell signal
        if adjusted_size < self.config['min_position_size'] and action != 'SELL':
            return None
        
        # Calculate stop loss and take profit
        stop_loss_pct = self.config['stop_loss_scaling'].get(sentiment.volatility_level, 0.03)
        
        if sentiment.sentiment_score >= self.config['sentiment_thresholds']['strong_buy']:
            take_profit_pct = self.config['take_profit_scaling']['strong_buy']
        elif sentiment.sentiment_score >= self.config['sentiment_thresholds']['buy']:
            take_profit_pct = self.config['take_profit_scaling']['buy']
        else:
            take_profit_pct = self.config['take_profit_scaling']['neutral']
        
        # Build entry reason with regime info
        regime_label = sentiment.regime_data.get('primary_regime', 'Unknown')
        entry_reason = f"{market} Morning: {sentiment.recommendation} " \
                      f"(Score {sentiment.sentiment_score:.0f}, " \
                      f"Regime: {regime_label})"
        
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
                'regime': regime_label,
                'report_timestamp': sentiment.timestamp.isoformat()
            }
        )
        
        return signal
    
    def _calculate_base_position_size(self, sentiment: PipelineSentiment) -> float:
        """Calculate base position size from sentiment"""
        score = sentiment.sentiment_score
        thresholds = self.config['sentiment_thresholds']
        sizing = self.config['position_sizing']
        
        if score >= thresholds['strong_buy']:
            base_size = sizing['strong_buy'] * 0.20
        elif score >= thresholds['buy']:
            base_size = sizing['buy'] * 0.20
        elif score >= thresholds['neutral_high'] or score <= thresholds['neutral_low']:
            base_size = sizing['neutral'] * 0.20
        else:
            base_size = 0.10
        
        return base_size
    
    def get_all_market_signals(
        self,
        markets: Optional[List[str]] = None,
        max_signals_per_market: int = 5
    ) -> Dict[str, List[TradingSignal]]:
        """Get trading signals for all markets"""
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
        """Format signals for paper_trading_coordinator compatibility"""
        formatted = []
        
        for signal in signals:
            formatted_signal = {
                'symbol': signal.symbol,
                'action': signal.action,
                'signal': 'BUY' if signal.action == 'BUY' else 'SELL',
                'confidence': signal.confidence / 100.0,
                'position_size': signal.adjusted_position_size,
                'stop_loss': signal.stop_loss_pct,
                'take_profit': signal.take_profit_pct,
                'reason': signal.entry_reason,
                'source': 'pipeline_adapter_v2',
                'market': signal.market,
                'sentiment_score': signal.sentiment_score,
                'risk_level': signal.risk_level,
                'pipeline_recommendation': signal.pipeline_recommendation,
                'metadata': signal.metadata
            }
            formatted.append(formatted_signal)
        
        return formatted


# Test harness
def test_adapter_v2():
    """Test the adapter V2 with new pipeline structure"""
    print("\n" + "="*80)
    print("PIPELINE SIGNAL ADAPTER V2 TEST")
    print("="*80 + "\n")
    
    adapter = PipelineSignalAdapterV2()
    
    for market in ['AU', 'US', 'UK']:
        print(f"\n{'-'*80}")
        print(f"Testing {market} Market")
        print('-'*80)
        
        try:
            sentiment = adapter.get_morning_sentiment(market)
            if sentiment:
                print(f"[OK] Sentiment: {sentiment.sentiment_score:.1f}/100")
                print(f"  Recommendation: {sentiment.recommendation}")
                print(f"  Top Opportunities: {len(sentiment.top_opportunities)}")
                
                signals = adapter.generate_trading_signals(market, max_signals=3)
                print(f"\n[OK] Generated {len(signals)} signals")
                
                for i, signal in enumerate(signals, 1):
                    print(f"\n  {i}. {signal.symbol}")
                    print(f"     Position: {signal.adjusted_position_size:.1%}")
                    print(f"     Stop/Target: {signal.stop_loss_pct:.1%} / {signal.take_profit_pct:.1%}")
            else:
                print(f"[X] No report available - pipeline needs to run first")
                
        except Exception as e:
            print(f"[X] Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("Test complete")
    print("="*80)


if __name__ == "__main__":
    test_adapter_v2()
