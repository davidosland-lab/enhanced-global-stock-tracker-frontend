"""
US Market Monitor - Market Sentiment Analysis
Tracks S&P 500, VIX, and overall US market sentiment

Equivalent to SPI Monitor but for US market indices
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from yahooquery import Ticker
import pytz

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class USMarketMonitor:
    """
    US Market Monitor - Tracks S&P 500, VIX, and market sentiment
    
    Key Indices:
    - ^GSPC (S&P 500) - Primary market index
    - ^VIX (VIX) - Volatility index (fear gauge)
    - ^DJI (Dow Jones) - Industrial average
    - ^IXIC (NASDAQ) - Tech-heavy index
    """
    
    def __init__(self):
        """Initialize US market monitor"""
        self.sp500_symbol = "^GSPC"
        self.vix_symbol = "^VIX"
        self.dow_symbol = "^DJI"
        self.nasdaq_symbol = "^IXIC"
        self.timezone = pytz.timezone('America/New_York')
        logger.info("US Market Monitor initialized")
    
    def fetch_index_data(self, symbol: str, period: str = "1mo") -> Optional[pd.DataFrame]:
        """
        Fetch index historical data
        
        Args:
            symbol: Index symbol (e.g., ^GSPC, ^VIX)
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y)
            
        Returns:
            DataFrame with OHLCV data or None on error
        """
        try:
            ticker = Ticker(symbol)
            hist = ticker.history(period=period)
            
            if isinstance(hist, pd.DataFrame) and not hist.empty:
                # Normalize column names
                hist.columns = [col.capitalize() for col in hist.columns]
                return hist
            else:
                logger.warning(f"No data returned for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None
    
    def get_sp500_sentiment(self) -> Dict:
        """
        Analyze S&P 500 sentiment
        
        Returns:
            Dictionary with S&P 500 metrics and sentiment
        """
        try:
            # Fetch 3 months of data for analysis
            hist = self.fetch_index_data(self.sp500_symbol, period="3mo")
            
            if hist is None or hist.empty:
                return self._get_default_sentiment("S&P 500")
            
            # Current metrics
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            day_change = ((current_price - prev_close) / prev_close) * 100
            
            # Calculate moving averages
            ma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            ma50 = hist['Close'].rolling(window=50).mean().iloc[-1]
            
            # Calculate volatility
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)  # Annualized
            
            # Calculate momentum (5-day change)
            if len(hist) >= 5:
                week_ago = hist['Close'].iloc[-5]
                week_change = ((current_price - week_ago) / week_ago) * 100
            else:
                week_change = day_change
            
            # Determine sentiment
            sentiment = self._calculate_sentiment(
                day_change=day_change,
                week_change=week_change,
                above_ma20=current_price > ma20,
                above_ma50=current_price > ma50,
                volatility=volatility
            )
            
            return {
                'index': 'S&P 500',
                'symbol': self.sp500_symbol,
                'price': float(current_price),
                'day_change': float(day_change),
                'week_change': float(week_change),
                'ma20': float(ma20),
                'ma50': float(ma50),
                'above_ma20': bool(current_price > ma20),
                'above_ma50': bool(current_price > ma50),
                'volatility': float(volatility),
                'sentiment': sentiment,
                'sentiment_score': self._sentiment_to_score(sentiment),
                'timestamp': datetime.now(self.timezone).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing S&P 500: {e}")
            return self._get_default_sentiment("S&P 500")
    
    def get_vix_analysis(self) -> Dict:
        """
        Analyze VIX (Volatility Index) - Market fear gauge
        
        VIX Interpretation:
        - Below 12: Very low volatility (complacent market)
        - 12-20: Normal volatility (healthy market)
        - 20-30: Elevated volatility (cautious market)
        - Above 30: High volatility (fearful market)
        
        Returns:
            Dictionary with VIX metrics and interpretation
        """
        try:
            hist = self.fetch_index_data(self.vix_symbol, period="1mo")
            
            if hist is None or hist.empty:
                return self._get_default_vix()
            
            current_vix = hist['Close'].iloc[-1]
            avg_vix = hist['Close'].mean()
            max_vix = hist['Close'].max()
            min_vix = hist['Close'].min()
            
            # VIX interpretation
            if current_vix < 12:
                level = "Very Low"
                market_mood = "Complacent"
                risk_rating = "Low"
            elif current_vix < 20:
                level = "Normal"
                market_mood = "Healthy"
                risk_rating = "Moderate"
            elif current_vix < 30:
                level = "Elevated"
                market_mood = "Cautious"
                risk_rating = "Elevated"
            else:
                level = "High"
                market_mood = "Fearful"
                risk_rating = "High"
            
            return {
                'index': 'VIX',
                'symbol': self.vix_symbol,
                'current_vix': float(current_vix),
                'avg_vix': float(avg_vix),
                'max_vix': float(max_vix),
                'min_vix': float(min_vix),
                'level': level,
                'market_mood': market_mood,
                'risk_rating': risk_rating,
                'interpretation': self._interpret_vix(current_vix),
                'timestamp': datetime.now(self.timezone).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing VIX: {e}")
            return self._get_default_vix()
    
    def get_market_overview(self) -> Dict:
        """
        Get comprehensive US market overview
        
        Returns:
            Dictionary with all major indices and overall sentiment
        """
        logger.info("Fetching US market overview...")
        
        # Get S&P 500 sentiment
        sp500 = self.get_sp500_sentiment()
        
        # Get VIX analysis
        vix = self.get_vix_analysis()
        
        # Get Dow Jones
        dow = self._get_index_summary(self.dow_symbol, "Dow Jones")
        
        # Get NASDAQ
        nasdaq = self._get_index_summary(self.nasdaq_symbol, "NASDAQ")
        
        # Calculate overall market sentiment
        overall_sentiment = self._calculate_overall_sentiment(sp500, vix, dow, nasdaq)
        
        logger.info(f"✓ US Market Overview: {overall_sentiment['sentiment']} ({overall_sentiment['score']:.1f}/100)")
        
        return {
            'market': 'US',
            'timestamp': datetime.now(self.timezone).isoformat(),
            'sp500': sp500,
            'vix': vix,
            'dow': dow,
            'nasdaq': nasdaq,
            'overall': overall_sentiment
        }
    
    def _get_index_summary(self, symbol: str, name: str) -> Dict:
        """Get quick summary of an index"""
        try:
            hist = self.fetch_index_data(symbol, period="5d")
            if hist is None or hist.empty:
                return {'index': name, 'symbol': symbol, 'available': False}
            
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
            change = ((current - prev) / prev) * 100
            
            return {
                'index': name,
                'symbol': symbol,
                'price': float(current),
                'day_change': float(change),
                'available': True
            }
        except:
            return {'index': name, 'symbol': symbol, 'available': False}
    
    def _calculate_sentiment(self, day_change: float, week_change: float,
                            above_ma20: bool, above_ma50: bool, volatility: float) -> str:
        """
        Calculate market sentiment from metrics
        
        Returns:
            Sentiment string: 'Bullish', 'Neutral', or 'Bearish'
        """
        score = 0
        
        # Day change (±2 points)
        if day_change > 1.0:
            score += 2
        elif day_change > 0:
            score += 1
        elif day_change < -1.0:
            score -= 2
        else:
            score -= 1
        
        # Week change (±2 points)
        if week_change > 3.0:
            score += 2
        elif week_change > 0:
            score += 1
        elif week_change < -3.0:
            score -= 2
        else:
            score -= 1
        
        # Moving averages (±2 points)
        if above_ma20 and above_ma50:
            score += 2
        elif above_ma20:
            score += 1
        elif not above_ma50:
            score -= 2
        else:
            score -= 1
        
        # Volatility penalty
        if volatility > 0.30:
            score -= 1
        
        # Determine sentiment
        if score >= 3:
            return "Bullish"
        elif score <= -3:
            return "Bearish"
        else:
            return "Neutral"
    
    def _sentiment_to_score(self, sentiment: str) -> float:
        """Convert sentiment to numeric score (0-100)"""
        sentiment_scores = {
            "Bullish": 75.0,
            "Neutral": 50.0,
            "Bearish": 25.0
        }
        return sentiment_scores.get(sentiment, 50.0)
    
    def _interpret_vix(self, vix_value: float) -> str:
        """Interpret VIX value"""
        if vix_value < 12:
            return "Market complacency - consider risk of sudden spikes"
        elif vix_value < 20:
            return "Normal market conditions - healthy volatility"
        elif vix_value < 30:
            return "Elevated uncertainty - exercise caution"
        else:
            return "High fear/uncertainty - defensive positioning advised"
    
    def _calculate_overall_sentiment(self, sp500: Dict, vix: Dict, 
                                     dow: Dict, nasdaq: Dict) -> Dict:
        """Calculate overall market sentiment from all indices"""
        score = sp500['sentiment_score']
        
        # Adjust for VIX
        if vix['current_vix'] < 15:
            score += 5
        elif vix['current_vix'] > 25:
            score -= 10
        
        # Adjust for index agreement
        positive_indices = 0
        total_indices = 0
        
        for idx in [sp500, dow, nasdaq]:
            if idx.get('available', True):
                total_indices += 1
                if idx.get('day_change', 0) > 0:
                    positive_indices += 1
        
        if total_indices > 0:
            agreement_ratio = positive_indices / total_indices
            if agreement_ratio >= 0.67:
                score += 5
            elif agreement_ratio <= 0.33:
                score -= 5
        
        # Clamp score
        score = max(0, min(100, score))
        
        # Determine sentiment
        if score >= 65:
            sentiment = "Bullish"
        elif score >= 35:
            sentiment = "Neutral"
        else:
            sentiment = "Bearish"
        
        return {
            'sentiment': sentiment,
            'score': float(score),
            'confidence': 'High' if abs(score - 50) > 20 else 'Moderate'
        }
    
    def _get_default_sentiment(self, index_name: str) -> Dict:
        """Return default sentiment when data unavailable"""
        return {
            'index': index_name,
            'sentiment': 'Neutral',
            'sentiment_score': 50.0,
            'available': False,
            'timestamp': datetime.now(self.timezone).isoformat()
        }
    
    def _get_default_vix(self) -> Dict:
        """Return default VIX data when unavailable"""
        return {
            'index': 'VIX',
            'symbol': self.vix_symbol,
            'current_vix': 20.0,
            'level': 'Normal',
            'market_mood': 'Healthy',
            'risk_rating': 'Moderate',
            'available': False,
            'timestamp': datetime.now(self.timezone).isoformat()
        }


if __name__ == "__main__":
    # Test the US market monitor
    monitor = USMarketMonitor()
    
    print("\n" + "="*80)
    print("US MARKET MONITOR TEST")
    print("="*80)
    
    # Test S&P 500 sentiment
    print("\n1. S&P 500 Sentiment:")
    sp500 = monitor.get_sp500_sentiment()
    print(f"   Price: {sp500['price']:.2f}")
    print(f"   Day Change: {sp500['day_change']:+.2f}%")
    print(f"   Sentiment: {sp500['sentiment']} ({sp500['sentiment_score']:.1f}/100)")
    
    # Test VIX analysis
    print("\n2. VIX Analysis:")
    vix = monitor.get_vix_analysis()
    print(f"   Current VIX: {vix['current_vix']:.2f}")
    print(f"   Level: {vix['level']}")
    print(f"   Market Mood: {vix['market_mood']}")
    print(f"   Risk Rating: {vix['risk_rating']}")
    
    # Test full market overview
    print("\n3. Full Market Overview:")
    overview = monitor.get_market_overview()
    print(f"   Overall Sentiment: {overview['overall']['sentiment']}")
    print(f"   Overall Score: {overview['overall']['score']:.1f}/100")
    print(f"   Confidence: {overview['overall']['confidence']}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
