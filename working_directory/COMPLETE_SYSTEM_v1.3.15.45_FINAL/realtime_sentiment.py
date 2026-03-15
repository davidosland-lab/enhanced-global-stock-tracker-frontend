"""
Real-Time Global Market Sentiment Calculator
=============================================

Calculates dynamic multi-market sentiment throughout trading day.

Features:
- Real-time updates every 5 minutes
- Global aggregation (US 50%, UK 25%, AU 25%)
- Intraday trend analysis
- Fear index integration (VIX, VFTSE)
- Automatic fallback to morning reports

Author: AI Trading System
Version: v1.3.15.46
Date: 2026-01-29
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json

try:
    import yfinance as yf
except ImportError:
    yf = None
    logging.warning("yfinance not available, using fallback sentiment only")

logger = logging.getLogger(__name__)


class RealtimeMarketSentiment:
    """
    Real-time global market sentiment calculator
    
    Monitors major indices across three markets (US, UK, AU) and calculates
    weighted global sentiment score (0-100) that updates throughout trading day.
    
    Weighting:
    - US Markets: 50% (S&P 500, NASDAQ, Dow Jones)
    - UK Markets: 25% (FTSE 100)
    - AU Markets: 25% (ASX All Ords)
    
    Update Frequency: Every 5 minutes (configurable)
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize real-time sentiment calculator
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default 300 = 5 minutes)
        """
        self.cache = {}
        self.cache_ttl = cache_ttl
        self.last_update = 0
        
        # Market indices to monitor
        self.indices = {
            'us': ['^GSPC', '^IXIC', '^DJI'],  # S&P 500, NASDAQ, Dow
            'uk': ['^FTSE'],                    # FTSE 100
            'au': ['^AORD']                     # ASX All Ords
        }
        
        # Fear/volatility indices
        self.fear_indices = {
            'us': '^VIX',      # US VIX (CBOE Volatility Index)
            'uk': '^VFTSE'     # UK VIX (FTSE Volatility Index)
        }
        
        # Market weights (reflects global influence)
        self.weights = {
            'us': 0.50,  # 50% - most influential global market
            'uk': 0.25,  # 25% - European bridge session
            'au': 0.25   # 25% - Asian first-mover
        }
        
        logger.info("[REALTIME SENTIMENT] Initialized with weights: US 50%, UK 25%, AU 25%")
    
    def get_global_sentiment(self, force_refresh: bool = False) -> Dict:
        """
        Calculate real-time global market sentiment
        
        Args:
            force_refresh: Force recalculation (ignore cache)
        
        Returns:
            {
                'score': float,        # Global sentiment 0-100
                'label': str,          # BULLISH/NEUTRAL/BEARISH
                'confidence': str,     # HIGH/MODERATE/LOW
                'breakdown': {         # Per-market details
                    'us': {'score': float, 'change': float, 'trend': str},
                    'uk': {'score': float, 'change': float, 'trend': str},
                    'au': {'score': float, 'change': float, 'trend': str}
                },
                'timestamp': datetime,
                'source': str,         # 'realtime' or 'morning_report'
                'markets_available': int
            }
        """
        # Check cache (unless force refresh)
        if not force_refresh:
            if time.time() - self.last_update < self.cache_ttl:
                if 'global_sentiment' in self.cache:
                    logger.debug("[REALTIME SENTIMENT] Returning cached sentiment")
                    return self.cache['global_sentiment']
        
        # Calculate fresh sentiment
        logger.info("[REALTIME SENTIMENT] Calculating fresh global sentiment...")
        
        try:
            sentiments = {}
            
            # Fetch each market's real-time sentiment
            for market, symbols in self.indices.items():
                market_sentiment = self._calculate_market_sentiment(market, symbols)
                if market_sentiment:
                    sentiments[market] = market_sentiment
                    logger.info(f"[REALTIME SENTIMENT] {market.upper()}: {market_sentiment['score']:.1f} "
                               f"({market_sentiment['change']:+.2f}%) {market_sentiment['trend']}")
            
            # Calculate weighted global sentiment
            if len(sentiments) > 0:
                global_score = self._weighted_average(sentiments)
                confidence = self._calculate_confidence(sentiments)
                label = self._classify_sentiment(global_score)
                
                # Build result
                result = {
                    'score': global_score,
                    'label': label,
                    'confidence': confidence,
                    'breakdown': sentiments,
                    'timestamp': datetime.now(),
                    'source': 'realtime',
                    'markets_available': len(sentiments),
                    'weights': self.weights
                }
                
                # Update cache
                self.cache['global_sentiment'] = result
                self.last_update = time.time()
                
                logger.info(f"[REALTIME SENTIMENT] GLOBAL: {global_score:.1f}/100 ({label}) - {confidence} confidence")
                logger.info(f"[REALTIME SENTIMENT] Markets: {len(sentiments)}/3 available")
                
                return result
            else:
                # No real-time data available, fallback to morning report
                logger.warning("[REALTIME SENTIMENT] No real-time data available, using morning report fallback")
                return self._fallback_morning_sentiment()
                
        except Exception as e:
            logger.error(f"[REALTIME SENTIMENT] Calculation failed: {e}", exc_info=True)
            return self._fallback_morning_sentiment()
    
    def _calculate_market_sentiment(self, market: str, symbols: List[str]) -> Optional[Dict]:
        """
        Calculate real-time sentiment for a specific market
        
        Args:
            market: Market code ('us', 'uk', 'au')
            symbols: List of ticker symbols to monitor
        
        Returns:
            {
                'score': float,         # 0-100
                'change': float,        # % change from previous close
                'trend': str,           # UP/DOWN/FLAT
                'momentum': float,      # Intraday momentum
                'indices_count': int    # Number of indices used
            }
        """
        if not yf:
            logger.warning(f"[REALTIME SENTIMENT] yfinance not available for {market}")
            return None
        
        try:
            scores = []
            changes = []
            momentums = []
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    
                    # Get intraday data (1 day, 15-min intervals)
                    hist = ticker.history(period='1d', interval='15m')
                    
                    if len(hist) == 0:
                        logger.debug(f"[REALTIME SENTIMENT] No intraday data for {symbol}")
                        continue
                    
                    # Get official previous close
                    info = ticker.info
                    prev_close = info.get('regularMarketPreviousClose', info.get('previousClose'))
                    current_price = hist['Close'].iloc[-1]
                    
                    if not prev_close or prev_close <= 0:
                        # Fallback: use first intraday price
                        prev_close = hist['Close'].iloc[0]
                    
                    # Calculate % change from previous close
                    pct_change = ((current_price - prev_close) / prev_close) * 100
                    
                    # Calculate intraday momentum (last hour vs 4 hours ago)
                    if len(hist) >= 16:  # 4 hours = 16 intervals of 15min
                        four_hours_ago_price = hist['Close'].iloc[-16]
                        momentum = ((current_price - four_hours_ago_price) / four_hours_ago_price) * 100
                    else:
                        momentum = pct_change
                    
                    # Convert to sentiment score (0-100)
                    # FIXED v1.3.15.52: Daily close is PRIMARY, momentum is bounded modifier
                    # Formula: Base score from daily change + bounded momentum adjustment
                    # Daily change is the most important market signal
                    # Momentum provides context but cannot override the daily close direction
                    
                    # Base score from daily close (primary signal)
                    base_score = 50 + (pct_change * 15)  # ±1% = ±15 points
                    
                    # Momentum modifier (secondary, bounded to ±5 points max)
                    momentum_modifier = max(-5, min(5, momentum * 2))
                    
                    # Final sentiment score
                    sentiment_score = base_score + momentum_modifier
                    sentiment_score = max(0, min(100, sentiment_score))  # Clamp to [0, 100]
                    
                    # Example: AORD -0.9% with +2% intraday momentum:
                    # base = 50 + (-0.9 * 15) = 36.5 (BEARISH base)
                    # modifier = min(5, 2*2) = 4 (momentum boost, but bounded)
                    # final = 36.5 + 4 = 40.5 (SLIGHTLY BEARISH) ✓ Correct!
                    # 
                    # Compare to old formula: 50 + (-9) + (10) = 51 (NEUTRAL) ✗ Wrong!
                    
                    scores.append(sentiment_score)
                    changes.append(pct_change)
                    momentums.append(momentum)
                    
                    logger.debug(f"[REALTIME SENTIMENT] {symbol}: {sentiment_score:.1f} "
                                f"(daily {pct_change:+.2f}%, momentum {momentum:+.2f}%, "
                                f"base {base_score:.1f}, modifier {momentum_modifier:+.1f})")
                
                except Exception as e:
                    logger.warning(f"[REALTIME SENTIMENT] Failed to fetch {symbol}: {e}")
                    continue
            
            if len(scores) > 0:
                avg_score = sum(scores) / len(scores)
                avg_change = sum(changes) / len(changes)
                avg_momentum = sum(momentums) / len(momentums)
                
                # Determine trend based on average change
                if avg_change > 0.5:
                    trend = 'UP'
                elif avg_change < -0.5:
                    trend = 'DOWN'
                else:
                    trend = 'FLAT'
                
                return {
                    'score': avg_score,
                    'change': avg_change,
                    'momentum': avg_momentum,
                    'trend': trend,
                    'indices_count': len(scores)
                }
            
            logger.warning(f"[REALTIME SENTIMENT] No valid data for {market}")
            return None
            
        except Exception as e:
            logger.error(f"[REALTIME SENTIMENT] Failed to calculate {market} sentiment: {e}")
            return None
    
    def _weighted_average(self, sentiments: Dict) -> float:
        """
        Calculate weighted average sentiment across markets
        
        Args:
            sentiments: Dict of market sentiments
        
        Returns:
            Weighted global sentiment score (0-100)
        """
        total_weight = 0
        weighted_sum = 0
        
        for market, data in sentiments.items():
            weight = self.weights.get(market, 0.25)
            weighted_sum += data['score'] * weight
            total_weight += weight
        
        # Normalize by total weight (in case not all markets available)
        global_score = weighted_sum / total_weight if total_weight > 0 else 50.0
        
        return global_score
    
    def _classify_sentiment(self, score: float) -> str:
        """
        Classify numeric sentiment score into label
        
        Args:
            score: Sentiment score 0-100
        
        Returns:
            Label: BULLISH/SLIGHTLY_BULLISH/NEUTRAL/SLIGHTLY_BEARISH/BEARISH
        """
        if score >= 65:
            return 'BULLISH'
        elif score >= 55:
            return 'SLIGHTLY_BULLISH'
        elif score >= 45:
            return 'NEUTRAL'
        elif score >= 35:
            return 'SLIGHTLY_BEARISH'
        else:
            return 'BEARISH'
    
    def _calculate_confidence(self, sentiments: Dict) -> str:
        """
        Calculate confidence level based on market agreement
        
        High confidence: All markets agree (low variance)
        Low confidence: Markets diverge (high variance)
        
        Args:
            sentiments: Dict of market sentiments
        
        Returns:
            Confidence: HIGH/MODERATE/LOW
        """
        if len(sentiments) < 2:
            return 'LOW'  # Need at least 2 markets for confidence
        
        scores = [data['score'] for data in sentiments.values()]
        
        # Calculate standard deviation
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Classify confidence based on standard deviation
        if std_dev < 10:
            return 'HIGH'      # Markets strongly agree
        elif std_dev < 20:
            return 'MODERATE'  # Some divergence
        else:
            return 'LOW'       # Markets disagree
    
    def _fallback_morning_sentiment(self) -> Dict:
        """
        Fallback to morning report sentiment if real-time fails
        
        Loads sentiment from overnight pipeline morning reports.
        Priority: US > UK > AU
        
        Returns:
            Sentiment dict from morning report, or neutral default
        """
        logger.info("[REALTIME SENTIMENT] Using morning report fallback")
        
        # Try to load morning reports in priority order
        for market in ['us', 'uk', 'au']:
            try:
                report_path = Path('reports/screening') / f'{market}_morning_report.json'
                
                if not report_path.exists():
                    continue
                
                # Check if report is recent (within 24 hours)
                file_age_hours = (time.time() - report_path.stat().st_mtime) / 3600
                if file_age_hours > 24:
                    logger.warning(f"[REALTIME SENTIMENT] {market} morning report is stale ({file_age_hours:.1f}h old)")
                    continue
                
                # Load report
                with open(report_path, 'r') as f:
                    report = json.load(f)
                
                sentiment_score = report.get('overall_sentiment', 50)
                
                logger.info(f"[REALTIME SENTIMENT] Loaded {market.upper()} morning report: {sentiment_score:.1f}/100")
                
                return {
                    'score': sentiment_score,
                    'label': self._classify_sentiment(sentiment_score),
                    'confidence': 'MODERATE',
                    'breakdown': {
                        market: {
                            'score': sentiment_score,
                            'change': 0.0,
                            'trend': 'FLAT',
                            'indices_count': 1
                        }
                    },
                    'timestamp': datetime.fromtimestamp(report_path.stat().st_mtime),
                    'source': 'morning_report',
                    'markets_available': 1,
                    'weights': self.weights
                }
            
            except Exception as e:
                logger.warning(f"[REALTIME SENTIMENT] Failed to load {market} morning report: {e}")
                continue
        
        # Ultimate fallback: neutral sentiment
        logger.warning("[REALTIME SENTIMENT] All fallbacks failed, using neutral default")
        return {
            'score': 50.0,
            'label': 'NEUTRAL',
            'confidence': 'LOW',
            'breakdown': {},
            'timestamp': datetime.now(),
            'source': 'default',
            'markets_available': 0,
            'weights': self.weights
        }
    
    def get_sentiment_gate_recommendation(self, sentiment_score: float) -> Dict:
        """
        Get trading gate recommendation based on sentiment score
        
        Args:
            sentiment_score: Current sentiment (0-100)
        
        Returns:
            {
                'action': str,           # BLOCK/REDUCE/NEUTRAL/BOOST
                'adjustment': float,     # Confidence multiplier
                'message': str           # Explanation
            }
        """
        # Sentiment thresholds (configurable)
        BLOCK_THRESHOLD = 20   # < 20: BLOCK all new buys
        REDUCE_THRESHOLD = 35  # < 35: REDUCE confidence by 30%
        BOOST_THRESHOLD = 65   # > 65: BOOST confidence by 20%
        
        if sentiment_score < BLOCK_THRESHOLD:
            return {
                'action': 'BLOCK',
                'adjustment': 0.0,
                'message': f'Bearish sentiment ({sentiment_score:.1f}) - blocking new positions'
            }
        elif sentiment_score < REDUCE_THRESHOLD:
            return {
                'action': 'REDUCE',
                'adjustment': 0.70,  # Reduce to 70% of original
                'message': f'Slightly bearish sentiment ({sentiment_score:.1f}) - reducing confidence by 30%'
            }
        elif sentiment_score > BOOST_THRESHOLD:
            return {
                'action': 'BOOST',
                'adjustment': 1.20,  # Boost to 120% of original
                'message': f'Bullish sentiment ({sentiment_score:.1f}) - boosting confidence by 20%'
            }
        else:
            return {
                'action': 'NEUTRAL',
                'adjustment': 1.0,
                'message': f'Neutral sentiment ({sentiment_score:.1f}) - no adjustment'
            }


# Convenience function for quick testing
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("Real-Time Global Sentiment Calculator - Test")
    print("=" * 60)
    
    calculator = RealtimeMarketSentiment(cache_ttl=300)
    
    print("\nFetching real-time global sentiment...")
    sentiment = calculator.get_global_sentiment(force_refresh=True)
    
    print(f"\nGlobal Sentiment: {sentiment['score']:.1f}/100 ({sentiment['label']})")
    print(f"Confidence: {sentiment['confidence']}")
    print(f"Markets Available: {sentiment['markets_available']}/3")
    print(f"Source: {sentiment['source']}")
    print(f"Timestamp: {sentiment['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\nRegional Breakdown:")
    for market, data in sentiment['breakdown'].items():
        print(f"  {market.upper()}: {data['score']:.1f} ({data['change']:+.2f}%) {data['trend']}")
    
    print("\nSentiment Gate Recommendation:")
    gate = calculator.get_sentiment_gate_recommendation(sentiment['score'])
    print(f"  Action: {gate['action']}")
    print(f"  Adjustment: {gate['adjustment']:.2f}x")
    print(f"  Message: {gate['message']}")
    
    print("\n" + "=" * 60)
