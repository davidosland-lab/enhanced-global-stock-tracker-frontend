"""
SPI 200 Futures Monitor Module

Tracks SPI 200 futures overnight and monitors US market indices
to predict ASX 200 opening direction and magnitude.

Features:
- SPI 200 futures tracking (5:10 PM - 8:00 AM AEST)
- US market indices monitoring (S&P 500, Nasdaq, Dow)
- Gap prediction and market sentiment analysis
- Correlation-based opening predictions
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import time
import pandas as pd
import numpy as np
from pathlib import Path
import pytz
from yahooquery import Ticker
import yfinance as yf

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SPIMonitor:
    """
    Monitors SPI 200 futures and US markets to predict ASX opening.
    
    The SPI 200 trades overnight (5:10 PM - 8:00 AM AEST) and provides
    an early indication of where the Australian market will open.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize SPI Monitor
        
        Args:
            config_path: Path to screening_config.json
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "screening_config.json"
        
        self.config = self._load_config(config_path)
        self.spi_config = self.config['spi_monitoring']
        
        # Market symbols
        self.asx_symbol = self.spi_config['symbol']  # ^AXJO (ASX 200)
        self.us_symbols = self.spi_config['us_indices']['symbols']  # S&P 500, Nasdaq, Dow
        
        # Timezone
        self.timezone = pytz.timezone('Australia/Sydney')
        
        # Use yfinance for all data fetching
        logger.info("Using yfinance for data source")
        
        logger.info("SPI Monitor initialized")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load screening configuration from JSON"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def get_market_sentiment(self) -> Dict:
        """
        Get comprehensive market sentiment analysis
        
        Returns:
            Dictionary with sentiment scores, predictions, and analysis
        """
        logger.info("Calculating market sentiment...")
        
        # Get ASX 200 current state
        asx_data = self._get_asx_state()
        
        # Get US market closes
        us_data = self._get_us_market_data()
        
        # Calculate gap prediction
        gap_prediction = self._predict_opening_gap(asx_data, us_data)
        
        # Calculate sentiment score
        sentiment_score = self._calculate_sentiment_score(us_data, gap_prediction)
        
        return {
            'timestamp': datetime.now(self.timezone).isoformat(),
            'asx_200': asx_data,
            'us_markets': us_data,
            'gap_prediction': gap_prediction,
            'sentiment_score': sentiment_score,
            'recommendation': self._get_recommendation(sentiment_score, gap_prediction)
        }
    
    def _get_asx_state(self) -> Dict:
        """
        Get current ASX 200 state using yahooquery (primary) or yfinance (backup)
        
        Returns:
            Dictionary with ASX data
        """
        try:
            # Try yahooquery first (most reliable, no API key needed)
            try:
                ticker = Ticker(self.asx_symbol)
                hist = ticker.history(period="1mo")
                
                if isinstance(hist, pd.DataFrame) and not hist.empty and len(hist) >= 2:
                    # Normalize column names
                    hist.columns = [col.capitalize() for col in hist.columns]
                    
                    last_close = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change_pct = ((last_close - prev_close) / prev_close) * 100
                    
                    # Calculate 5-day trend
                    if len(hist) >= 5:
                        five_day_change = ((last_close - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100
                    else:
                        five_day_change = change_pct
                    
                    logger.info(f"✓ ASX data fetched from yahooquery: {self.asx_symbol}")
                    return {
                        'available': True,
                        'symbol': self.asx_symbol,
                        'last_close': float(last_close),
                        'prev_close': float(prev_close),
                        'change_pct': float(change_pct),
                        'five_day_change_pct': float(five_day_change),
                        'volume': int(hist['Volume'].iloc[-1]),
                        'last_updated': hist.index[-1].isoformat() if hasattr(hist.index[-1], 'isoformat') else str(hist.index[-1])
                    }
            except Exception as yq_error:
                logger.warning(f"yahooquery failed for ASX, trying yfinance: {yq_error}")
            
            # Fallback to yfinance if yahooquery fails
            try:
                ticker_yf = yf.Ticker(self.asx_symbol)
                hist = ticker_yf.history(period="1mo")
                
                if hist is not None and not hist.empty and len(hist) >= 2:
                    last_close = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change_pct = ((last_close - prev_close) / prev_close) * 100
                    
                    if len(hist) >= 5:
                        five_day_change = ((last_close - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]) * 100
                    else:
                        five_day_change = change_pct
                    
                    logger.info(f"✓ ASX data fetched from yfinance: {self.asx_symbol}")
                    return {
                        'available': True,
                        'symbol': self.asx_symbol,
                        'last_close': float(last_close),
                        'prev_close': float(prev_close),
                        'change_pct': float(change_pct),
                        'five_day_change_pct': float(five_day_change),
                        'volume': int(hist['Volume'].iloc[-1]),
                        'last_updated': hist.index[-1].isoformat()
                    }
            except Exception as yf_error:
                logger.warning(f"yfinance also failed: {yf_error}")
            
            logger.warning("No ASX data available from any source")
            return {'available': False}
            
        except Exception as e:
            logger.error(f"Error fetching ASX data: {e}")
            return {'available': False, 'error': str(e)}
    
    def _get_us_market_data(self) -> Dict:
        """
        Get US market indices data (S&P 500, Nasdaq, Dow) using yahooquery (primary) or yfinance (backup)
        
        Returns:
            Dictionary with US market data
        """
        us_data = {}
        
        # Map symbol to friendly name
        name_map = {
            '^GSPC': 'SP500',
            '^IXIC': 'Nasdaq',
            '^DJI': 'Dow'
        }
        
        for symbol in self.us_symbols:
            try:
                # Try yahooquery first (most reliable, no API key needed)
                hist = None
                try:
                    ticker = Ticker(symbol)
                    hist = ticker.history(period="1mo")
                    
                    if isinstance(hist, pd.DataFrame) and not hist.empty and len(hist) >= 2:
                        # Normalize column names (yahooquery uses lowercase)
                        hist.columns = [col.capitalize() for col in hist.columns]
                        logger.info(f"✓ {name_map.get(symbol, symbol)} data from yahooquery")
                except Exception as yq_error:
                    logger.warning(f"yahooquery failed for {symbol}, trying yfinance: {yq_error}")
                    hist = None
                
                # Fallback to yfinance if yahooquery fails
                if hist is None or hist.empty:
                    try:
                        ticker_yf = yf.Ticker(symbol)
                        hist = ticker_yf.history(period="1mo")
                        if hist is not None and not hist.empty:
                            logger.info(f"✓ {name_map.get(symbol, symbol)} data from yfinance")
                    except Exception as yf_error:
                        logger.warning(f"yfinance also failed for {symbol}: {yf_error}")
                
                if hist is None or hist.empty:
                    logger.warning(f"No data for {symbol} from any source")
                    continue
                
                if len(hist) < 2:
                    logger.warning(f"Insufficient data for {symbol}")
                    continue
                
                last_close = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                change_pct = ((last_close - prev_close) / prev_close) * 100
                
                us_data[name_map.get(symbol, symbol)] = {
                    'symbol': symbol,
                    'last_close': float(last_close),
                    'prev_close': float(prev_close),
                    'change_pct': float(change_pct),
                    'volume': int(hist['Volume'].iloc[-1]),
                    'last_updated': hist.index[-1].isoformat() if hasattr(hist.index[-1], 'isoformat') else str(hist.index[-1])
                }
                
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                continue
        
        return us_data
    
    def _predict_opening_gap(self, asx_data: Dict, us_data: Dict) -> Dict:
        """
        Predict ASX 200 opening gap based on US market performance
        
        Historical correlation: ASX 200 moves ~0.6-0.7x of US market changes
        
        Args:
            asx_data: ASX 200 current state
            us_data: US market indices data
            
        Returns:
            Dictionary with gap prediction
        """
        if not asx_data.get('available') or not us_data:
            return {
                'predicted_gap_pct': 0,
                'confidence': 0,
                'direction': 'neutral',
                'error': 'Insufficient data'
            }
        
        # Calculate weighted average of US market changes
        us_changes = []
        weights = []
        
        for market_name, data in us_data.items():
            us_changes.append(data['change_pct'])
            # S&P 500 has highest correlation with ASX
            if market_name == 'SP500':
                weights.append(0.5)
            elif market_name == 'Nasdaq':
                weights.append(0.3)
            else:  # Dow
                weights.append(0.2)
        
        if not us_changes:
            return {
                'predicted_gap_pct': 0,
                'confidence': 0,
                'direction': 'neutral'
            }
        
        # Weighted average of US market changes
        weighted_us_change = np.average(us_changes, weights=weights)
        
        # Apply correlation factor (ASX typically moves 60-70% of US changes)
        correlation_factor = self.spi_config['us_indices'].get('correlation_weight', 0.35)
        predicted_gap = weighted_us_change * (correlation_factor / 0.35) * 0.65  # Scale to ~65%
        
        # Calculate confidence based on US market agreement
        us_changes_array = np.array(us_changes)
        if len(us_changes_array) > 1:
            # High confidence if all markets moved in same direction
            same_direction = np.all(us_changes_array > 0) or np.all(us_changes_array < 0)
            std_dev = np.std(us_changes_array)
            
            if same_direction and std_dev < 0.5:
                confidence = 90
            elif same_direction:
                confidence = 75
            elif std_dev < 0.5:
                confidence = 60
            else:
                confidence = 40
        else:
            confidence = 50
        
        # Determine direction
        if predicted_gap > 0.3:
            direction = 'bullish'
        elif predicted_gap < -0.3:
            direction = 'bearish'
        else:
            direction = 'neutral'
        
        return {
            'predicted_gap_pct': float(predicted_gap),
            'confidence': confidence,
            'direction': direction,
            'us_weighted_change': float(weighted_us_change),
            'correlation_used': 0.65,
            'threshold': self.spi_config['gap_threshold_pct']
        }
    
    def _calculate_sentiment_score(self, us_data: Dict, gap_prediction: Dict) -> float:
        """
        Calculate overall market sentiment score (0-100)
        
        Factors:
        - US market performance (40%)
        - Gap prediction magnitude (30%)
        - US market agreement (20%)
        - Recent ASX trend (10%)
        
        Args:
            us_data: US market data
            gap_prediction: Gap prediction data
            
        Returns:
            Sentiment score (0-100)
        """
        score = 50  # Neutral baseline
        
        if not us_data:
            return score
        
        # 1. US market performance (40 points)
        us_changes = [data['change_pct'] for data in us_data.values()]
        avg_us_change = np.mean(us_changes)
        
        # Scale US change to score (-3% = 0, 0% = 50, +3% = 100)
        us_score = 50 + (avg_us_change / 3.0) * 50
        us_score = max(0, min(100, us_score))
        score += (us_score - 50) * 0.4
        
        # 2. Gap prediction magnitude (30 points)
        predicted_gap = gap_prediction.get('predicted_gap_pct', 0)
        gap_score = 50 + (predicted_gap / 2.0) * 50
        gap_score = max(0, min(100, gap_score))
        score += (gap_score - 50) * 0.3
        
        # 3. US market agreement (20 points)
        if len(us_changes) > 1:
            same_direction = np.all(np.array(us_changes) > 0) or np.all(np.array(us_changes) < 0)
            if same_direction:
                score += 10  # Bonus for agreement
            else:
                score -= 5   # Penalty for disagreement
        
        # 4. Confidence factor (10 points)
        confidence = gap_prediction.get('confidence', 50)
        score += (confidence - 50) * 0.2
        
        # Ensure score is within bounds
        return max(0, min(100, score))
    
    def _get_recommendation(self, sentiment_score: float, gap_prediction: Dict) -> Dict:
        """
        Generate trading recommendation based on sentiment
        
        Args:
            sentiment_score: Overall sentiment (0-100)
            gap_prediction: Gap prediction data
            
        Returns:
            Dictionary with recommendation details
        """
        predicted_gap = gap_prediction.get('predicted_gap_pct', 0)
        confidence = gap_prediction.get('confidence', 0)
        
        # Determine stance
        if sentiment_score >= 70 and confidence >= 70:
            stance = 'STRONG_BUY'
            message = 'Strong bullish sentiment. Consider aggressive long positions.'
        elif sentiment_score >= 60:
            stance = 'BUY'
            message = 'Bullish sentiment. Favor long positions.'
        elif sentiment_score >= 45 and sentiment_score <= 55:
            stance = 'NEUTRAL'
            message = 'Mixed signals. Wait for market direction.'
        elif sentiment_score <= 30 and confidence >= 70:
            stance = 'STRONG_SELL'
            message = 'Strong bearish sentiment. Consider protective measures.'
        elif sentiment_score <= 40:
            stance = 'SELL'
            message = 'Bearish sentiment. Reduce exposure or short.'
        else:
            stance = 'HOLD'
            message = 'Cautious sentiment. Maintain current positions.'
        
        return {
            'stance': stance,
            'message': message,
            'expected_open': f"{'+' if predicted_gap > 0 else ''}{predicted_gap:.2f}%",
            'confidence': f"{confidence}%",
            'risk_level': 'HIGH' if confidence < 50 else 'MEDIUM' if confidence < 75 else 'LOW'
        }
    
    def get_overnight_summary(self) -> Dict:
        """
        Get complete overnight market summary for morning report
        
        Returns:
            Dictionary with full overnight analysis
        """
        sentiment = self.get_market_sentiment()
        
        # Add additional context
        sentiment['overnight_summary'] = {
            'generated_at': datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z'),
            'market_status': self._get_market_status(),
            'key_levels': self._calculate_key_levels(sentiment['asx_200'])
        }
        
        return sentiment
    
    def _get_market_status(self) -> str:
        """Determine if markets are currently trading"""
        now = datetime.now(self.timezone)
        hour = now.hour
        minute = now.minute
        
        # ASX trading hours: 10:00 AM - 4:00 PM AEST
        if 10 <= hour < 16:
            return 'ASX_OPEN'
        
        # SPI futures trading: 5:10 PM - 8:00 AM AEST
        if (hour >= 17 and minute >= 10) or hour < 8:
            return 'SPI_TRADING'
        
        # Pre-market
        if 8 <= hour < 10:
            return 'PRE_MARKET'
        
        return 'CLOSED'
    
    def _calculate_key_levels(self, asx_data: Dict) -> Dict:
        """
        Calculate key support/resistance levels for ASX 200
        
        Args:
            asx_data: Current ASX data
            
        Returns:
            Dictionary with key levels
        """
        if not asx_data.get('available'):
            return {}
        
        last_close = asx_data['last_close']
        
        # Simple pivot levels
        return {
            'resistance_1': round(last_close * 1.01, 2),
            'resistance_2': round(last_close * 1.02, 2),
            'support_1': round(last_close * 0.99, 2),
            'support_2': round(last_close * 0.98, 2),
            'pivot': round(last_close, 2)
        }


# ============================================================================
# TEST HARNESS
# ============================================================================

def test_spi_monitor():
    """Test the SPI monitor"""
    print("\n" + "="*80)
    print("SPI 200 FUTURES MONITOR TEST")
    print("="*80 + "\n")
    
    # Initialize monitor
    monitor = SPIMonitor()
    
    # Get market sentiment
    print("Fetching market sentiment...\n")
    sentiment = monitor.get_overnight_summary()
    
    # Display results
    print("-"*80)
    print("ASX 200 STATUS")
    print("-"*80)
    asx = sentiment['asx_200']
    if asx.get('available'):
        print(f"Last Close: {asx['last_close']:.2f}")
        print(f"Change: {asx['change_pct']:+.2f}%")
        print(f"5-Day Change: {asx['five_day_change_pct']:+.2f}%")
    else:
        print("⚠ ASX data not available")
    
    print("\n" + "-"*80)
    print("US MARKETS")
    print("-"*80)
    for market, data in sentiment['us_markets'].items():
        print(f"{market:8s}: {data['last_close']:8.2f}  Change: {data['change_pct']:+6.2f}%")
    
    print("\n" + "-"*80)
    print("OPENING PREDICTION")
    print("-"*80)
    gap = sentiment['gap_prediction']
    print(f"Predicted Gap: {gap['predicted_gap_pct']:+.2f}%")
    print(f"Direction: {gap['direction'].upper()}")
    print(f"Confidence: {gap['confidence']}%")
    
    print("\n" + "-"*80)
    print("SENTIMENT ANALYSIS")
    print("-"*80)
    print(f"Sentiment Score: {sentiment['sentiment_score']:.1f}/100")
    rec = sentiment['recommendation']
    print(f"Recommendation: {rec['stance']}")
    print(f"Message: {rec['message']}")
    print(f"Expected Open: {rec['expected_open']}")
    print(f"Risk Level: {rec['risk_level']}")
    
    print("\n" + "-"*80)
    print("KEY LEVELS")
    print("-"*80)
    levels = sentiment['overnight_summary']['key_levels']
    if levels:
        print(f"Resistance 2: {levels['resistance_2']:.2f}")
        print(f"Resistance 1: {levels['resistance_1']:.2f}")
        print(f"Pivot Point:  {levels['pivot']:.2f}")
        print(f"Support 1:    {levels['support_1']:.2f}")
        print(f"Support 2:    {levels['support_2']:.2f}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    test_spi_monitor()
