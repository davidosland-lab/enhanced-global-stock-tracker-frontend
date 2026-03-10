"""
Gap Reality Checker Module v193.11.6.21
========================================

Validates gap predictions against actual market opens and adjusts opportunity scores.

PROBLEM:
System predicted ASX opening gap of +0.38%, actual SPI 200 opened +1.3%
Error: 0.92 percentage points (242% prediction error)
This causes misallocation - stocks scored assuming small gap, but large gap occurred.

SOLUTION:
At market open (first 5-15 minutes), compare predicted vs actual gap:
- Large positive surprise (+0.5%+ miss): BOOST stock scores (market stronger than expected)
- Large negative surprise (-0.5%+ miss): REDUCE stock scores (market weaker than expected)
- Small miss (<0.5%): No adjustment (within expected variance)

INTEGRATION:
Called by paper_trading_coordinator.py during:
1. Pre-market analysis (stores prediction)
2. Post-open validation (15 min after open, checks actual)
3. Score adjustment (applies multiplier to opportunity scores)

Author: AI Trading System
Date: 2026-03-10
Version: v193.11.6.21
"""

import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import pytz
from yahooquery import Ticker
import json
import os

logger = logging.getLogger(__name__)


class GapRealityChecker:
    """
    Validates gap predictions against actual market opens.
    
    Stores predictions, checks actual gaps at open, and provides
    score adjustment multipliers based on prediction accuracy.
    """
    
    def __init__(self, state_dir: str = "state"):
        """
        Initialize the gap reality checker.
        
        Args:
            state_dir: Directory to store prediction state files
        """
        self.state_dir = state_dir
        os.makedirs(state_dir, exist_ok=True)
        
        # Market symbols for gap checking
        self.market_symbols = {
            'AU': '^AXJO',   # ASX 200
            'UK': '^FTSE',   # FTSE 100
            'US': '^GSPC'    # S&P 500
        }
        
        # Timezones
        self.timezones = {
            'AU': pytz.timezone('Australia/Sydney'),
            'UK': pytz.timezone('Europe/London'),
            'US': pytz.timezone('US/Eastern')
        }
        
        # Gap accuracy thresholds (percentage points)
        self.accuracy_thresholds = {
            'excellent': 0.2,   # Within 0.2% = no adjustment
            'good': 0.5,        # Within 0.5% = minor adjustment
            'poor': 1.0,        # Within 1.0% = moderate adjustment
            'terrible': 2.0     # > 2.0% = major adjustment
        }
        
        # Score adjustment multipliers
        self.score_multipliers = {
            # Positive surprise (market stronger than predicted)
            'positive_small': 1.05,    # +0.2% to +0.5% miss -> boost 5%
            'positive_medium': 1.10,   # +0.5% to +1.0% miss -> boost 10%
            'positive_large': 1.15,    # +1.0% to +2.0% miss -> boost 15%
            'positive_huge': 1.20,     # > +2.0% miss -> boost 20%
            
            # Negative surprise (market weaker than predicted)
            'negative_small': 0.95,    # -0.2% to -0.5% miss -> reduce 5%
            'negative_medium': 0.90,   # -0.5% to -1.0% miss -> reduce 10%
            'negative_large': 0.85,    # -1.0% to -2.0% miss -> reduce 15%
            'negative_huge': 0.80,     # > -2.0% miss -> reduce 20%
            
            # Accurate prediction
            'accurate': 1.0            # < 0.2% miss -> no change
        }
    
    def store_prediction(self, market: str, predicted_gap_pct: float, 
                        confidence: float, direction: str) -> bool:
        """
        Store a gap prediction before market open.
        
        Args:
            market: 'AU', 'UK', or 'US'
            predicted_gap_pct: Predicted gap percentage
            confidence: Prediction confidence (0-1)
            direction: 'BULLISH', 'BEARISH', or 'NEUTRAL'
        
        Returns:
            True if stored successfully
        """
        try:
            now = datetime.now(self.timezones[market])
            
            prediction = {
                'market': market,
                'predicted_gap_pct': predicted_gap_pct,
                'confidence': confidence,
                'direction': direction,
                'timestamp': now.isoformat(),
                'date': now.strftime('%Y-%m-%d'),
                'validated': False,
                'actual_gap_pct': None,
                'error_pct': None,
                'accuracy_rating': None,
                'score_multiplier': 1.0
            }
            
            # Save to state file
            state_file = os.path.join(self.state_dir, f'gap_prediction_{market}_{now.strftime("%Y%m%d")}.json')
            with open(state_file, 'w') as f:
                json.dump(prediction, f, indent=2)
            
            logger.info(f"[GAP CHECKER] Stored {market} prediction: {predicted_gap_pct:+.2f}% ({direction}, {confidence:.0%} confidence)")
            return True
            
        except Exception as e:
            logger.error(f"[GAP CHECKER] Failed to store {market} prediction: {e}")
            return False
    
    def check_actual_gap(self, market: str, minutes_after_open: int = 15) -> Optional[Dict]:
        """
        Check the actual market gap at open and validate against prediction.
        
        Args:
            market: 'AU', 'UK', or 'US'
            minutes_after_open: Wait N minutes after open for price stability (default 15)
        
        Returns:
            Dictionary with validation results, or None if not available yet
        """
        try:
            now = datetime.now(self.timezones[market])
            date_str = now.strftime('%Y-%m-%d')
            
            # Load prediction
            state_file = os.path.join(self.state_dir, f'gap_prediction_{market}_{now.strftime("%Y%m%d")}.json')
            
            if not os.path.exists(state_file):
                logger.debug(f"[GAP CHECKER] No prediction file for {market} on {date_str}")
                return None
            
            with open(state_file, 'r') as f:
                prediction = json.load(f)
            
            # Skip if already validated
            if prediction.get('validated', False):
                logger.debug(f"[GAP CHECKER] {market} gap already validated today")
                return prediction
            
            # Fetch actual market data
            symbol = self.market_symbols[market]
            ticker = Ticker(symbol)
            
            # Get intraday data (last 2 days to ensure we have yesterday's close)
            hist = ticker.history(period='2d', interval='1d')
            
            if hist is None or len(hist) < 2:
                logger.warning(f"[GAP CHECKER] Insufficient data for {market} gap check")
                return None
            
            # Get yesterday's close and today's open
            if symbol in hist.index.get_level_values(0):
                market_data = hist.loc[symbol]
                
                if len(market_data) >= 2:
                    yesterday_close = market_data['close'].iloc[-2]
                    today_open = market_data['open'].iloc[-1]
                    
                    # Calculate actual gap
                    actual_gap_pct = ((today_open - yesterday_close) / yesterday_close) * 100.0
                    
                    # Calculate prediction error
                    predicted_gap = prediction['predicted_gap_pct']
                    error_pct = actual_gap_pct - predicted_gap
                    
                    # Determine accuracy rating and score multiplier
                    accuracy_rating, score_multiplier = self._calculate_accuracy_rating(error_pct)
                    
                    # Update prediction state
                    prediction['validated'] = True
                    prediction['actual_gap_pct'] = round(actual_gap_pct, 2)
                    prediction['error_pct'] = round(error_pct, 2)
                    prediction['accuracy_rating'] = accuracy_rating
                    prediction['score_multiplier'] = score_multiplier
                    prediction['validation_timestamp'] = now.isoformat()
                    
                    # Save updated state
                    with open(state_file, 'w') as f:
                        json.dump(prediction, f, indent=2)
                    
                    # Log results
                    logger.info(f"[GAP CHECKER] {market} Gap Validation:")
                    logger.info(f"  Predicted: {predicted_gap:+.2f}%")
                    logger.info(f"  Actual: {actual_gap_pct:+.2f}%")
                    logger.info(f"  Error: {error_pct:+.2f}% ({accuracy_rating})")
                    logger.info(f"  Score Multiplier: {score_multiplier:.2f}x")
                    
                    return prediction
            
            logger.warning(f"[GAP CHECKER] Could not extract gap data for {market}")
            return None
            
        except Exception as e:
            logger.error(f"[GAP CHECKER] Failed to check {market} actual gap: {e}")
            return None
    
    def _calculate_accuracy_rating(self, error_pct: float) -> Tuple[str, float]:
        """
        Calculate accuracy rating and score multiplier based on prediction error.
        
        Args:
            error_pct: Prediction error in percentage points (actual - predicted)
        
        Returns:
            Tuple of (accuracy_rating, score_multiplier)
        """
        abs_error = abs(error_pct)
        
        # Determine accuracy level
        if abs_error <= self.accuracy_thresholds['excellent']:
            rating = 'EXCELLENT'
            multiplier = self.score_multipliers['accurate']
        
        elif abs_error <= self.accuracy_thresholds['good']:
            # Good accuracy - small adjustment
            if error_pct > 0:
                rating = 'GOOD_POSITIVE'
                multiplier = self.score_multipliers['positive_small']
            else:
                rating = 'GOOD_NEGATIVE'
                multiplier = self.score_multipliers['negative_small']
        
        elif abs_error <= self.accuracy_thresholds['poor']:
            # Poor accuracy - moderate adjustment
            if error_pct > 0:
                rating = 'POOR_POSITIVE'
                multiplier = self.score_multipliers['positive_medium']
            else:
                rating = 'POOR_NEGATIVE'
                multiplier = self.score_multipliers['negative_medium']
        
        elif abs_error <= self.accuracy_thresholds['terrible']:
            # Terrible accuracy - major adjustment
            if error_pct > 0:
                rating = 'TERRIBLE_POSITIVE'
                multiplier = self.score_multipliers['positive_large']
            else:
                rating = 'TERRIBLE_NEGATIVE'
                multiplier = self.score_multipliers['negative_large']
        
        else:
            # Catastrophic accuracy - huge adjustment
            if error_pct > 0:
                rating = 'CATASTROPHIC_POSITIVE'
                multiplier = self.score_multipliers['positive_huge']
            else:
                rating = 'CATASTROPHIC_NEGATIVE'
                multiplier = self.score_multipliers['negative_huge']
        
        return rating, multiplier
    
    def get_score_multiplier(self, market: str) -> float:
        """
        Get the current score adjustment multiplier for a market.
        
        Args:
            market: 'AU', 'UK', or 'US'
        
        Returns:
            Score multiplier (0.80 to 1.20), or 1.0 if no validation available
        """
        try:
            now = datetime.now(self.timezones[market])
            state_file = os.path.join(self.state_dir, f'gap_prediction_{market}_{now.strftime("%Y%m%d")}.json')
            
            if not os.path.exists(state_file):
                return 1.0
            
            with open(state_file, 'r') as f:
                prediction = json.load(f)
            
            if prediction.get('validated', False):
                return prediction.get('score_multiplier', 1.0)
            else:
                return 1.0
                
        except Exception as e:
            logger.error(f"[GAP CHECKER] Failed to get multiplier for {market}: {e}")
            return 1.0
    
    def apply_multiplier_to_stocks(self, stocks: list, market: str) -> list:
        """
        Apply gap accuracy multiplier to stock opportunity scores.
        
        Args:
            stocks: List of stock dictionaries with 'opportunity_score' field
            market: 'AU', 'UK', or 'US'
        
        Returns:
            Modified stock list with adjusted scores
        """
        multiplier = self.get_score_multiplier(market)
        
        if multiplier == 1.0:
            logger.debug(f"[GAP CHECKER] No adjustment for {market} stocks (multiplier = 1.0)")
            return stocks
        
        adjusted_count = 0
        for stock in stocks:
            if 'opportunity_score' in stock:
                old_score = stock['opportunity_score']
                new_score = old_score * multiplier
                stock['opportunity_score'] = round(new_score, 2)
                stock['gap_adjusted'] = True
                stock['gap_multiplier'] = multiplier
                adjusted_count += 1
        
        logger.info(f"[GAP CHECKER] Applied {multiplier:.2f}x multiplier to {adjusted_count} {market} stocks")
        return stocks
    
    def get_validation_summary(self, market: str) -> Optional[str]:
        """
        Get a human-readable summary of today's gap validation.
        
        Args:
            market: 'AU', 'UK', or 'US'
        
        Returns:
            Summary string, or None if no validation available
        """
        try:
            now = datetime.now(self.timezones[market])
            state_file = os.path.join(self.state_dir, f'gap_prediction_{market}_{now.strftime("%Y%m%d")}.json')
            
            if not os.path.exists(state_file):
                return None
            
            with open(state_file, 'r') as f:
                prediction = json.load(f)
            
            if not prediction.get('validated', False):
                return f"{market}: Prediction {prediction['predicted_gap_pct']:+.2f}% (not yet validated)"
            
            summary = (
                f"{market} Gap Validation:\n"
                f"  Predicted: {prediction['predicted_gap_pct']:+.2f}%\n"
                f"  Actual: {prediction['actual_gap_pct']:+.2f}%\n"
                f"  Error: {prediction['error_pct']:+.2f}% ({prediction['accuracy_rating']})\n"
                f"  Score Adjustment: {prediction['score_multiplier']:.2f}x"
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"[GAP CHECKER] Failed to get summary for {market}: {e}")
            return None


# === TEST MODULE ===
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    print("\n" + "="*80)
    print("GAP REALITY CHECKER TEST")
    print("="*80)
    
    checker = GapRealityChecker(state_dir="test_state")
    
    # Test 1: Store prediction
    print("\nTest 1: Store AU gap prediction")
    checker.store_prediction('AU', predicted_gap_pct=0.38, confidence=0.75, direction='BULLISH')
    
    # Test 2: Check actual gap (would need market to be open)
    print("\nTest 2: Check actual gap")
    result = checker.check_actual_gap('AU')
    if result:
        print(f"  Validation: {result['accuracy_rating']}")
        print(f"  Multiplier: {result['score_multiplier']:.2f}x")
    else:
        print("  (Market not open or insufficient data)")
    
    # Test 3: Apply multiplier to sample stocks
    print("\nTest 3: Apply multiplier to stocks")
    sample_stocks = [
        {'symbol': 'CBA.AX', 'opportunity_score': 65.0},
        {'symbol': 'BHP.AX', 'opportunity_score': 72.0},
        {'symbol': 'NAB.AX', 'opportunity_score': 58.0}
    ]
    
    adjusted = checker.apply_multiplier_to_stocks(sample_stocks, 'AU')
    for stock in adjusted:
        print(f"  {stock['symbol']}: {stock['opportunity_score']:.2f}")
    
    # Test 4: Get validation summary
    print("\nTest 4: Validation summary")
    summary = checker.get_validation_summary('AU')
    if summary:
        print(summary)
    else:
        print("  (No validation available)")
    
    print("\n" + "="*80)
