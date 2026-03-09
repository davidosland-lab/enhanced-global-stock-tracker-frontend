"""
Pre-Market Trading Strategy Module
===================================
VERSION: v1.3.15.193.11.6.10 - Gap Prediction Integration (Mar 9, 2026)

Integrates gap predictions from overnight pipelines (AU SPI, UK FTSE futures)
into paper trading decisions for pre-market entry timing.

FEATURES:
- Gap prediction analysis (predicted gap vs. actual gap at open)
- Confidence-based position sizing
- Risk-adjusted entry decisions
- Market regime correlation (world risk, macro events)
- Multi-market support (AU, UK, US)

GAP PREDICTION LOGIC:
1. Load gap prediction from overnight pipeline report
2. Compare predicted direction vs. market sentiment
3. Apply confidence threshold (default 60%)
4. Calculate position size multiplier based on:
   - Gap magnitude (larger gaps = higher conviction)
   - Confidence level (higher confidence = larger positions)
   - World risk score (high risk = smaller positions)
5. Generate entry recommendations

USAGE:
    strategy = PreMarketStrategy(config)
    decision = strategy.analyze_gap_opportunity(
        market='uk',
        gap_prediction={'predicted_gap_pct': -0.57, 'confidence': 70},
        world_risk_score=87.6,
        sentiment_score=29.2
    )
    
    if decision['should_enter']:
        position_size = capital * decision['position_multiplier']
        # Execute trades on decision['recommended_symbols']

Author: Trading System v1.3.15
Date: March 9, 2026
"""

import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class PreMarketStrategy:
    """
    Pre-market trading strategy using gap predictions
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize pre-market strategy
        
        Args:
            config: Optional configuration dict
        """
        self.config = config or self._default_config()
        logger.info("[PRE-MARKET] Strategy initialized")
    
    def _default_config(self) -> Dict:
        """Default configuration for pre-market strategy"""
        return {
            'min_gap_confidence': 60,           # Minimum confidence to act on gap (%)
            'min_gap_magnitude': 0.3,           # Minimum gap size to act on (%)
            'max_position_multiplier': 1.5,     # Maximum position size multiplier
            'min_position_multiplier': 0.25,    # Minimum position size multiplier
            'world_risk_threshold': 80,         # World risk above which to reduce positions
            'sentiment_threshold': 35,          # Sentiment below which to avoid entry
            'enable_gap_trading': True,         # Master switch for gap-based trading
            'markets': {
                'au': {'enabled': True, 'correlation': 0.85},  # AU SPI correlation
                'uk': {'enabled': True, 'correlation': 0.75},  # UK FTSE correlation
                'us': {'enabled': False, 'correlation': 0.90}  # US pre-market (future)
            }
        }
    
    def analyze_gap_opportunity(
        self,
        market: str,
        gap_prediction: Dict,
        world_risk_score: float,
        sentiment_score: float,
        top_stocks: List[Dict] = None
    ) -> Dict:
        """
        Analyze gap prediction and determine if/how to enter trades
        
        Args:
            market: 'au', 'uk', or 'us'
            gap_prediction: Dict with 'predicted_gap_pct', 'confidence', 'direction'
            world_risk_score: World risk score (0-100)
            sentiment_score: Market sentiment score (0-100)
            top_stocks: Optional list of top opportunity stocks from overnight pipeline
            
        Returns:
            Dict with:
                - should_enter: bool - Whether to enter trades
                - position_multiplier: float - Position size adjustment (0.0-1.5)
                - recommended_symbols: List[str] - Symbols to trade
                - entry_reason: str - Explanation
                - risk_level: str - LOW/MODERATE/HIGH/EXTREME
                - timing: str - NOW/WAIT_5MIN/WAIT_10MIN/AT_OPEN
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"[PRE-MARKET] Analyzing {market.upper()} gap opportunity")
        logger.info(f"{'='*80}")
        
        # Extract gap prediction data
        predicted_gap = gap_prediction.get('predicted_gap_pct', 0)
        confidence = gap_prediction.get('confidence', 0)
        direction = gap_prediction.get('direction', 'NEUTRAL')
        
        logger.info(f"  Predicted Gap: {predicted_gap:+.2f}%")
        logger.info(f"  Confidence: {confidence:.0f}%")
        logger.info(f"  Direction: {direction}")
        logger.info(f"  Sentiment Score: {sentiment_score:.1f}/100")
        logger.info(f"  World Risk: {world_risk_score:.1f}/100")
        
        # Check if gap trading is enabled for this market
        if not self.config.get('enable_gap_trading', True):
            logger.info("[PRE-MARKET] Gap trading disabled in config")
            return self._no_entry_decision("Gap trading disabled")
        
        if not self.config['markets'].get(market, {}).get('enabled', False):
            logger.info(f"[PRE-MARKET] {market.upper()} market disabled in config")
            return self._no_entry_decision(f"{market.upper()} market disabled")
        
        # GATE 1: Confidence threshold
        min_confidence = self.config['min_gap_confidence']
        if confidence < min_confidence:
            logger.warning(f"[BLOCK] Confidence too low ({confidence:.0f}% < {min_confidence}%)")
            return self._no_entry_decision(f"Confidence below threshold ({confidence:.0f}% < {min_confidence}%)")
        
        # GATE 2: Gap magnitude threshold
        min_gap = self.config['min_gap_magnitude']
        gap_magnitude = abs(predicted_gap)
        if gap_magnitude < min_gap:
            logger.info(f"[SKIP] Gap too small ({gap_magnitude:.2f}% < {min_gap}%)")
            return self._no_entry_decision(f"Gap magnitude too small ({gap_magnitude:.2f}% < {min_gap}%)")
        
        # GATE 3: World risk check
        world_risk_threshold = self.config['world_risk_threshold']
        risk_multiplier = 1.0
        
        if world_risk_score >= 85:
            risk_multiplier = 0.5
            logger.warning(f"[RISK] Extreme world risk ({world_risk_score:.1f}) - position reduced 50%")
        elif world_risk_score >= world_risk_threshold:
            risk_multiplier = 0.75
            logger.warning(f"[RISK] High world risk ({world_risk_score:.1f}) - position reduced 25%")
        
        # GATE 4: Sentiment check
        sentiment_threshold = self.config['sentiment_threshold']
        if sentiment_score < sentiment_threshold and predicted_gap < 0:
            # Double bearish signal - very cautious or avoid
            if sentiment_score < 20:
                logger.warning(f"[BLOCK] Extreme bearish sentiment ({sentiment_score:.1f}) with negative gap")
                return self._no_entry_decision(f"Extreme bearish conditions (sentiment {sentiment_score:.1f})")
            else:
                risk_multiplier *= 0.75  # Further reduce position
                logger.warning(f"[CAUTION] Bearish sentiment ({sentiment_score:.1f}) - position reduced")
        
        # GATE 5: Direction consistency check
        # If sentiment and gap disagree significantly, reduce conviction
        sentiment_bullish = sentiment_score > 50
        gap_bullish = predicted_gap > 0
        
        if sentiment_bullish != gap_bullish:
            risk_multiplier *= 0.85
            logger.info(f"[CAUTION] Sentiment ({sentiment_score:.1f}) and gap ({predicted_gap:+.2f}%) disagree - position reduced 15%")
        
        # Calculate position multiplier based on conviction
        # Formula: base_mult * confidence_factor * gap_factor * risk_multiplier
        
        # Confidence factor: 60% conf = 0.6x, 70% = 0.85x, 80% = 1.0x, 90% = 1.2x
        confidence_factor = min(1.2, (confidence - 50) / 50 * 0.8 + 0.6)
        
        # Gap factor: Larger gaps = higher conviction (0.3% = 0.7x, 1.0% = 1.0x, 2.0% = 1.3x)
        gap_factor = min(1.3, 0.7 + (gap_magnitude * 0.3))
        
        # Base multiplier from market correlation
        market_correlation = self.config['markets'][market].get('correlation', 0.75)
        base_mult = 0.5 + (market_correlation * 0.5)  # 0.5 to 1.0 based on correlation
        
        # Calculate final position multiplier
        position_mult = base_mult * confidence_factor * gap_factor * risk_multiplier
        
        # Clamp to min/max bounds
        min_mult = self.config['min_position_multiplier']
        max_mult = self.config['max_position_multiplier']
        position_mult = max(min_mult, min(max_mult, position_mult))
        
        logger.info(f"\n[POSITION CALC]")
        logger.info(f"  Base: {base_mult:.2f}x (market correlation {market_correlation:.2f})")
        logger.info(f"  Confidence: {confidence_factor:.2f}x (conf {confidence:.0f}%)")
        logger.info(f"  Gap: {gap_factor:.2f}x (magnitude {gap_magnitude:.2f}%)")
        logger.info(f"  Risk: {risk_multiplier:.2f}x (world risk {world_risk_score:.1f})")
        logger.info(f"  FINAL: {position_mult:.2f}x (clamped {min_mult:.2f}x - {max_mult:.2f}x)")
        
        # Determine risk level
        if world_risk_score >= 85 or sentiment_score < 25:
            risk_level = "EXTREME"
        elif world_risk_score >= 75 or sentiment_score < 35:
            risk_level = "HIGH"
        elif world_risk_score >= 60 or sentiment_score < 45:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"
        
        # Determine entry timing based on gap size and confidence
        if gap_magnitude >= 1.5 and confidence >= 75:
            timing = "NOW"  # Strong conviction - enter immediately
        elif gap_magnitude >= 1.0 and confidence >= 70:
            timing = "WAIT_2MIN"  # Good signal - wait for initial volatility
        elif gap_magnitude >= 0.5 or confidence >= 65:
            timing = "WAIT_5MIN"  # Moderate signal - wait for market to settle
        else:
            timing = "AT_OPEN"  # Weak signal - wait for official open
        
        # Select recommended symbols
        recommended_symbols = self._select_symbols_for_gap(
            market=market,
            gap_direction=direction,
            top_stocks=top_stocks,
            max_symbols=5
        )
        
        # Build entry reason
        entry_reason = self._build_entry_reason(
            market=market,
            predicted_gap=predicted_gap,
            confidence=confidence,
            sentiment_score=sentiment_score,
            world_risk_score=world_risk_score,
            position_mult=position_mult
        )
        
        logger.info(f"\n[DECISION]")
        logger.info(f"  Should Enter: YES")
        logger.info(f"  Position Size: {position_mult:.2f}x normal")
        logger.info(f"  Risk Level: {risk_level}")
        logger.info(f"  Entry Timing: {timing}")
        logger.info(f"  Symbols: {', '.join(recommended_symbols)}")
        logger.info(f"  Reason: {entry_reason}")
        logger.info(f"{'='*80}\n")
        
        return {
            'should_enter': True,
            'position_multiplier': position_mult,
            'recommended_symbols': recommended_symbols,
            'entry_reason': entry_reason,
            'risk_level': risk_level,
            'timing': timing,
            'gap_data': {
                'predicted_gap_pct': predicted_gap,
                'confidence': confidence,
                'direction': direction,
                'magnitude': gap_magnitude
            },
            'analysis': {
                'base_multiplier': base_mult,
                'confidence_factor': confidence_factor,
                'gap_factor': gap_factor,
                'risk_multiplier': risk_multiplier,
                'world_risk_score': world_risk_score,
                'sentiment_score': sentiment_score,
                'market_correlation': market_correlation
            }
        }
    
    def _no_entry_decision(self, reason: str) -> Dict:
        """Return a no-entry decision"""
        logger.info(f"[NO ENTRY] {reason}\n{'='*80}\n")
        return {
            'should_enter': False,
            'position_multiplier': 0.0,
            'recommended_symbols': [],
            'entry_reason': reason,
            'risk_level': 'N/A',
            'timing': 'SKIP'
        }
    
    def _select_symbols_for_gap(
        self,
        market: str,
        gap_direction: str,
        top_stocks: List[Dict] = None,
        max_symbols: int = 5
    ) -> List[str]:
        """
        Select symbols to trade based on gap direction and top opportunities
        
        Args:
            market: 'au', 'uk', or 'us'
            gap_direction: 'BULLISH', 'BEARISH', or 'NEUTRAL'
            top_stocks: List of top opportunity stocks from overnight pipeline
            max_symbols: Maximum number of symbols to return
            
        Returns:
            List of symbol strings
        """
        if not top_stocks:
            logger.warning("[PRE-MARKET] No top stocks provided, cannot select symbols")
            return []
        
        # Filter stocks based on gap direction
        filtered_stocks = []
        
        for stock in top_stocks:
            prediction = stock.get('prediction', '').upper()
            confidence = stock.get('confidence', 0)
            
            # Match stock prediction with gap direction
            if gap_direction == 'BULLISH':
                if prediction in ['BUY', 'STRONG_BUY'] and confidence >= 50:
                    filtered_stocks.append(stock)
            elif gap_direction == 'BEARISH':
                # For bearish gaps, we might want to avoid longs or look for shorts
                # For now, skip entry on bearish gaps unless stock is very strong
                if prediction in ['BUY', 'STRONG_BUY'] and confidence >= 70:
                    filtered_stocks.append(stock)
            else:  # NEUTRAL
                if prediction in ['BUY', 'HOLD'] and confidence >= 55:
                    filtered_stocks.append(stock)
        
        # Sort by opportunity score (highest first)
        filtered_stocks.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
        
        # Extract symbols
        symbols = [stock['symbol'] for stock in filtered_stocks[:max_symbols]]
        
        logger.info(f"[SYMBOLS] Selected {len(symbols)}/{len(top_stocks)} symbols for {gap_direction} gap")
        
        return symbols
    
    def _build_entry_reason(
        self,
        market: str,
        predicted_gap: float,
        confidence: float,
        sentiment_score: float,
        world_risk_score: float,
        position_mult: float
    ) -> str:
        """Build human-readable entry reason"""
        
        direction = "bullish" if predicted_gap > 0 else "bearish"
        gap_size = "large" if abs(predicted_gap) >= 1.0 else "moderate" if abs(predicted_gap) >= 0.5 else "small"
        conf_level = "high" if confidence >= 75 else "moderate" if confidence >= 65 else "acceptable"
        
        reason = f"{market.upper()} {gap_size} {direction} gap ({predicted_gap:+.2f}%) with {conf_level} confidence ({confidence:.0f}%)"
        
        # Add sentiment context
        if sentiment_score >= 65:
            reason += f", strong bullish sentiment ({sentiment_score:.0f})"
        elif sentiment_score >= 50:
            reason += f", neutral-bullish sentiment ({sentiment_score:.0f})"
        elif sentiment_score >= 35:
            reason += f", cautious sentiment ({sentiment_score:.0f})"
        else:
            reason += f", bearish sentiment ({sentiment_score:.0f})"
        
        # Add risk context
        if world_risk_score >= 85:
            reason += f", EXTREME world risk ({world_risk_score:.0f}) - small position ({position_mult:.2f}x)"
        elif world_risk_score >= 75:
            reason += f", HIGH world risk ({world_risk_score:.0f}) - reduced position ({position_mult:.2f}x)"
        elif world_risk_score >= 60:
            reason += f", moderate world risk ({world_risk_score:.0f})"
        
        return reason
    
    def load_gap_prediction_from_report(self, market: str, report_path: Path = None) -> Optional[Dict]:
        """
        Load gap prediction from overnight pipeline report
        
        Args:
            market: 'au', 'uk', or 'us'
            report_path: Optional path to report file (defaults to standard location)
            
        Returns:
            Dict with gap prediction data or None if not available
        """
        if not report_path:
            # Default report location
            base_path = Path(__file__).parent.parent / 'reports' / 'screening'
            report_path = base_path / f'{market}_morning_report.json'
        
        if not report_path.exists():
            logger.warning(f"[PRE-MARKET] No report found at {report_path}")
            return None
        
        try:
            with open(report_path, 'r') as f:
                report = json.load(f)
            
            # Extract gap prediction from market_sentiment section
            market_sentiment = report.get('market_sentiment', {})
            
            # Check for gap prediction fields
            gap_prediction = market_sentiment.get('gap_prediction', {})
            if gap_prediction and 'predicted_gap_pct' in gap_prediction:
                logger.info(f"[PRE-MARKET] Loaded gap prediction for {market.upper()}: {gap_prediction.get('predicted_gap_pct'):+.2f}%")
                return gap_prediction
            
            # Fallback: check if gap data is directly in market_sentiment
            if 'predicted_gap_pct' in market_sentiment:
                gap_data = {
                    'predicted_gap_pct': market_sentiment.get('predicted_gap_pct', 0),
                    'confidence': market_sentiment.get('confidence', 0),
                    'direction': market_sentiment.get('direction', 'NEUTRAL')
                }
                logger.info(f"[PRE-MARKET] Loaded gap data for {market.upper()}: {gap_data['predicted_gap_pct']:+.2f}%")
                return gap_data
            
            logger.warning(f"[PRE-MARKET] No gap prediction found in {market.upper()} report")
            return None
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to load gap prediction from {report_path}: {e}")
            return None
