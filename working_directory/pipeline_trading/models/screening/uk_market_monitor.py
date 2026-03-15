"""
UK Market Monitor - Market Sentiment Analysis
Tracks FTSE 100, FTSE 250, and UK market volatility indices

Equivalent to SPI Monitor (AU) and US Market Monitor but for UK/London markets

UK Overnight Indicators:
- FTSE 100 Futures (overnight trading 01:00-21:00 GMT via ICE)
- VFTSE (FTSE 100 Volatility Index) - UK equivalent of VIX
- US market close impact (S&P 500 correlation ~0.75 with FTSE)
- European market sentiment (DAX, CAC 40)
"""

import logging
from typing import Dict, Optional, List
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


class UKMarketMonitor:
    """
    UK Market Monitor - Tracks FTSE 100, VFTSE volatility, and market sentiment
    
    Key Indices:
    - ^FTSE (FTSE 100) - Primary UK market index (100 largest companies on LSE)
    - ^FTMC (FTSE 250) - Mid-cap index
    - ^GSPC (S&P 500) - For correlation analysis (US overnight impact)
    - ^GDAXI (DAX) - German index for European sentiment
    - ^FCHI (CAC 40) - French index for European sentiment
    
    Note: VFTSE (volatility index) not directly available via yfinance,
    so we calculate implied volatility from FTSE 100 price action
    """
    
    def __init__(self):
        """Initialize UK market monitor"""
        self.ftse100_symbol = "^FTSE"
        self.ftse250_symbol = "^FTMC"
        self.sp500_symbol = "^GSPC"
        self.dax_symbol = "^GDAXI"
        self.cac_symbol = "^FCHI"
        
        # FTSE 100 futures symbol (note: may not be available via yahooquery)
        # Alternative: use ^FTSE with extended hours or ICE futures data
        self.ftse_futures_symbol = "^FTSE"  # Will use cash index as proxy
        
        self.timezone = pytz.timezone('Europe/London')
        logger.info("UK Market Monitor initialized")
    
    def fetch_index_data(self, symbol: str, period: str = "1mo") -> Optional[pd.DataFrame]:
        """
        Fetch index historical data
        
        Args:
            symbol: Index symbol (e.g., ^FTSE, ^FTMC)
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
    
    def get_ftse100_sentiment(self) -> Dict:
        """
        Analyze FTSE 100 sentiment
        
        Returns:
            Dictionary with FTSE 100 metrics and sentiment
        """
        try:
            # Fetch 3 months of data for analysis
            hist = self.fetch_index_data(self.ftse100_symbol, period="3mo")
            
            if hist is None or hist.empty:
                return self._get_default_sentiment("FTSE 100")
            
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
            
            # Calculate 7-day and 14-day trends
            if len(hist) >= 7:
                seven_day_ago = hist['Close'].iloc[-7]
                seven_day_change = ((current_price - seven_day_ago) / seven_day_ago) * 100
            else:
                seven_day_change = week_change
            
            if len(hist) >= 14:
                fourteen_day_ago = hist['Close'].iloc[-14]
                fourteen_day_change = ((current_price - fourteen_day_ago) / fourteen_day_ago) * 100
            else:
                fourteen_day_change = seven_day_change
            
            # Determine sentiment
            sentiment = self._calculate_sentiment(
                day_change=day_change,
                week_change=week_change,
                above_ma20=current_price > ma20,
                above_ma50=current_price > ma50,
                volatility=volatility
            )
            
            return {
                'index': 'FTSE 100',
                'symbol': self.ftse100_symbol,
                'price': float(current_price),
                'day_change': float(day_change),
                'week_change': float(week_change),
                'seven_day_change': float(seven_day_change),
                'fourteen_day_change': float(fourteen_day_change),
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
            logger.error(f"Error analyzing FTSE 100: {e}")
            return self._get_default_sentiment("FTSE 100")
    
    def get_implied_volatility_analysis(self) -> Dict:
        """
        Calculate implied volatility from FTSE 100 price action
        (UK equivalent of VIX analysis)
        
        Since VFTSE is not readily available via free APIs, we calculate
        a proxy volatility measure from recent price action.
        
        Volatility Interpretation:
        - Below 10%: Very low volatility (complacent market)
        - 10-15%: Normal volatility (healthy market)
        - 15-25%: Elevated volatility (cautious market)
        - Above 25%: High volatility (fearful market)
        
        Returns:
            Dictionary with volatility metrics and interpretation
        """
        try:
            # Fetch 3 months of data
            hist = self.fetch_index_data(self.ftse100_symbol, period="3mo")
            
            if hist is None or hist.empty:
                return self._get_default_volatility()
            
            # Calculate realized volatility (20-day rolling)
            returns = hist['Close'].pct_change().dropna()
            
            # Annualized 20-day volatility
            vol_20d = returns.tail(20).std() * np.sqrt(252) * 100
            
            # Annualized 60-day volatility
            vol_60d = returns.tail(60).std() * np.sqrt(252) * 100 if len(returns) >= 60 else vol_20d
            
            # Average volatility
            avg_vol = returns.std() * np.sqrt(252) * 100
            
            # Max/min volatility (rolling 20-day)
            rolling_vol = returns.rolling(window=20).std() * np.sqrt(252) * 100
            max_vol = rolling_vol.max()
            min_vol = rolling_vol.min()
            
            current_vol = vol_20d
            
            # Volatility interpretation
            if current_vol < 10:
                level = "Very Low"
                market_mood = "Complacent"
                risk_rating = "Low"
            elif current_vol < 15:
                level = "Normal"
                market_mood = "Healthy"
                risk_rating = "Moderate"
            elif current_vol < 25:
                level = "Elevated"
                market_mood = "Cautious"
                risk_rating = "Elevated"
            else:
                level = "High"
                market_mood = "Fearful"
                risk_rating = "High"
            
            return {
                'index': 'FTSE 100 Volatility (Implied)',
                'symbol': self.ftse100_symbol,
                'current_vol': float(current_vol),
                'vol_20d': float(vol_20d),
                'vol_60d': float(vol_60d),
                'avg_vol': float(avg_vol),
                'max_vol': float(max_vol),
                'min_vol': float(min_vol),
                'level': level,
                'market_mood': market_mood,
                'risk_rating': risk_rating,
                'interpretation': self._interpret_volatility(current_vol),
                'note': 'Calculated from realized volatility (VFTSE proxy)',
                'timestamp': datetime.now(self.timezone).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing UK volatility: {e}")
            return self._get_default_volatility()
    
    def get_overnight_us_impact(self) -> Dict:
        """
        Analyze US market close impact on UK opening
        
        Historical correlation: FTSE 100 ~ 0.75 with S&P 500
        UK market opens at 08:00 GMT, 6 hours after US close (21:00 GMT)
        
        Returns:
            Dictionary with US market data and predicted UK impact
        """
        try:
            # Fetch S&P 500 data
            sp500_hist = self.fetch_index_data(self.sp500_symbol, period="1mo")
            
            if sp500_hist is None or sp500_hist.empty:
                return {'available': False, 'error': 'No S&P 500 data'}
            
            # Current S&P 500 metrics
            sp500_current = sp500_hist['Close'].iloc[-1]
            sp500_prev = sp500_hist['Close'].iloc[-2] if len(sp500_hist) > 1 else sp500_current
            sp500_change = ((sp500_current - sp500_prev) / sp500_prev) * 100
            
            # Predict FTSE impact (correlation factor ~0.75, but typically 50-70% transmission)
            correlation_factor = 0.65  # Conservative estimate
            predicted_ftse_impact = sp500_change * correlation_factor
            
            # Determine direction and confidence
            if abs(sp500_change) > 1.5:
                confidence = 85  # Strong US move = high confidence
            elif abs(sp500_change) > 0.75:
                confidence = 70  # Moderate US move
            else:
                confidence = 50  # Small US move = low confidence
            
            if predicted_ftse_impact > 0.3:
                direction = 'bullish'
            elif predicted_ftse_impact < -0.3:
                direction = 'bearish'
            else:
                direction = 'neutral'
            
            return {
                'available': True,
                'sp500_symbol': self.sp500_symbol,
                'sp500_close': float(sp500_current),
                'sp500_change_pct': float(sp500_change),
                'predicted_ftse_impact_pct': float(predicted_ftse_impact),
                'correlation_factor': correlation_factor,
                'confidence': confidence,
                'direction': direction,
                'timestamp': datetime.now(self.timezone).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing US overnight impact: {e}")
            return {'available': False, 'error': str(e)}
    
    def get_european_sentiment(self) -> Dict:
        """
        Get European market sentiment from DAX and CAC 40
        
        Returns:
            Dictionary with European indices data
        """
        european_data = {}
        
        indices = {
            'DAX': self.dax_symbol,
            'CAC_40': self.cac_symbol
        }
        
        for name, symbol in indices.items():
            try:
                hist = self.fetch_index_data(symbol, period="1mo")
                
                if hist is None or hist.empty:
                    continue
                
                current = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                change = ((current - prev) / prev) * 100
                
                european_data[name] = {
                    'symbol': symbol,
                    'price': float(current),
                    'day_change': float(change),
                    'timestamp': datetime.now(self.timezone).isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error fetching {name}: {e}")
                continue
        
        return european_data
    
    def get_market_overview(self) -> Dict:
        """
        Get comprehensive UK market overview
        
        Returns:
            Dictionary with FTSE indices, volatility, US impact, and European sentiment
        """
        logger.info("Fetching UK market overview...")
        
        # Get FTSE 100 sentiment
        ftse100 = self.get_ftse100_sentiment()
        
        # Get implied volatility
        volatility = self.get_implied_volatility_analysis()
        
        # Get US overnight impact
        us_impact = self.get_overnight_us_impact()
        
        # Get European sentiment
        european = self.get_european_sentiment()
        
        # Calculate overall sentiment score
        overall_sentiment = self._calculate_overall_sentiment(
            ftse100, volatility, us_impact, european
        )
        
        return {
            'ftse_100': ftse100,
            'volatility': volatility,
            'us_overnight_impact': us_impact,
            'european_markets': european,
            'overall_sentiment': overall_sentiment,
            'recommendation': self._get_recommendation(overall_sentiment),
            'timestamp': datetime.now(self.timezone).isoformat()
        }
    
    def _calculate_overall_sentiment(
        self, 
        ftse100: Dict, 
        volatility: Dict, 
        us_impact: Dict,
        european: Dict
    ) -> float:
        """
        Calculate overall UK market sentiment score (0-100)
        
        Factors:
        - FTSE 100 performance and trend (35%)
        - US overnight impact (30%)
        - European market sentiment (20%)
        - Volatility level (15%)
        
        Returns:
            Overall sentiment score (0-100)
        """
        score = 50  # Neutral baseline
        
        # 1. FTSE 100 sentiment (35 points)
        ftse_sentiment = ftse100.get('sentiment_score', 50)
        score += (ftse_sentiment - 50) * 0.35
        
        # 2. US overnight impact (30 points)
        if us_impact.get('available'):
            us_change = us_impact.get('sp500_change_pct', 0)
            us_score = 50 + (us_change / 3.0) * 50  # Scale: -3% to +3%
            us_score = max(0, min(100, us_score))
            score += (us_score - 50) * 0.30
        
        # 3. European sentiment (20 points)
        if european:
            eu_changes = [data['day_change'] for data in european.values()]
            avg_eu_change = np.mean(eu_changes) if eu_changes else 0
            eu_score = 50 + (avg_eu_change / 2.0) * 50  # Scale: -2% to +2%
            eu_score = max(0, min(100, eu_score))
            score += (eu_score - 50) * 0.20
        
        # 4. Volatility impact (15 points)
        vol_risk = volatility.get('risk_rating', 'Moderate')
        if vol_risk == 'Low':
            score += 7.5
        elif vol_risk == 'High':
            score -= 7.5
        # Moderate has no impact (neutral)
        
        return max(0, min(100, score))
    
    def _calculate_sentiment(
        self, 
        day_change: float, 
        week_change: float,
        above_ma20: bool,
        above_ma50: bool,
        volatility: float
    ) -> str:
        """Determine sentiment from metrics"""
        # Calculate sentiment score
        score = 0
        
        # Day change weight
        if day_change > 1.0:
            score += 3
        elif day_change > 0.3:
            score += 1
        elif day_change < -1.0:
            score -= 3
        elif day_change < -0.3:
            score -= 1
        
        # Week change weight
        if week_change > 2.0:
            score += 2
        elif week_change > 0:
            score += 1
        elif week_change < -2.0:
            score -= 2
        elif week_change < 0:
            score -= 1
        
        # Moving average position
        if above_ma20 and above_ma50:
            score += 2
        elif above_ma20:
            score += 1
        elif not above_ma50:
            score -= 1
        
        # Volatility penalty
        if volatility > 0.25:
            score -= 1
        
        # Determine sentiment
        if score >= 4:
            return "Very Bullish"
        elif score >= 2:
            return "Bullish"
        elif score >= -1:
            return "Neutral"
        elif score >= -3:
            return "Bearish"
        else:
            return "Very Bearish"
    
    def _sentiment_to_score(self, sentiment: str) -> float:
        """Convert sentiment string to 0-100 score"""
        sentiment_map = {
            "Very Bullish": 85,
            "Bullish": 65,
            "Neutral": 50,
            "Bearish": 35,
            "Very Bearish": 15
        }
        return sentiment_map.get(sentiment, 50)
    
    def _interpret_volatility(self, vol: float) -> str:
        """Interpret volatility level"""
        if vol < 10:
            return "Market is calm with low volatility. Good environment for trend following."
        elif vol < 15:
            return "Normal volatility levels. Balanced market conditions."
        elif vol < 25:
            return "Elevated volatility. Exercise caution and tighten stops."
        else:
            return "High volatility environment. Consider reducing position sizes."
    
    def _get_recommendation(self, sentiment_score: float) -> Dict:
        """
        Generate trading recommendation based on overall sentiment
        
        Args:
            sentiment_score: Overall sentiment (0-100)
            
        Returns:
            Dictionary with recommendation details
        """
        if sentiment_score >= 70:
            stance = 'STRONG_BUY'
            message = 'Strong bullish sentiment across UK and global markets. Consider aggressive long positions.'
        elif sentiment_score >= 60:
            stance = 'BUY'
            message = 'Bullish sentiment. Favor long positions with normal sizing.'
        elif sentiment_score >= 45 and sentiment_score <= 55:
            stance = 'NEUTRAL'
            message = 'Mixed signals across markets. Wait for clearer direction.'
        elif sentiment_score <= 30:
            stance = 'STRONG_SELL'
            message = 'Strong bearish sentiment. Consider protective measures or short positions.'
        elif sentiment_score <= 40:
            stance = 'SELL'
            message = 'Bearish sentiment. Reduce exposure or hedge positions.'
        else:
            stance = 'HOLD'
            message = 'Cautious sentiment. Maintain current positions and monitor closely.'
        
        return {
            'stance': stance,
            'message': message,
            'confidence': 'HIGH' if abs(sentiment_score - 50) > 20 else 'MODERATE' if abs(sentiment_score - 50) > 10 else 'LOW'
        }
    
    def _get_default_sentiment(self, index_name: str) -> Dict:
        """Return default sentiment when data unavailable"""
        return {
            'index': index_name,
            'available': False,
            'error': 'Data unavailable',
            'sentiment': 'Unknown',
            'sentiment_score': 50
        }
    
    def _get_default_volatility(self) -> Dict:
        """Return default volatility when data unavailable"""
        return {
            'index': 'FTSE 100 Volatility',
            'available': False,
            'error': 'Data unavailable',
            'level': 'Unknown',
            'market_mood': 'Unknown',
            'risk_rating': 'Unknown'
        }


# ============================================================================
# TEST HARNESS
# ============================================================================

def test_uk_market_monitor():
    """Test the UK market monitor"""
    print("\n" + "="*80)
    print("UK MARKET MONITOR TEST")
    print("="*80 + "\n")
    
    # Initialize monitor
    monitor = UKMarketMonitor()
    
    # Get market overview
    print("Fetching UK market overview...\n")
    overview = monitor.get_market_overview()
    
    # Display FTSE 100
    print("-"*80)
    print("FTSE 100 STATUS")
    print("-"*80)
    ftse = overview['ftse_100']
    if ftse.get('price'):
        print(f"Price: {ftse['price']:.2f}")
        print(f"Day Change: {ftse['day_change']:+.2f}%")
        print(f"Week Change: {ftse['week_change']:+.2f}%")
        print(f"7-Day Change: {ftse['seven_day_change']:+.2f}%")
        print(f"14-Day Change: {ftse['fourteen_day_change']:+.2f}%")
        print(f"Sentiment: {ftse['sentiment']} ({ftse['sentiment_score']:.1f}/100)")
    
    # Display volatility
    print("\n" + "-"*80)
    print("VOLATILITY ANALYSIS (VFTSE Proxy)")
    print("-"*80)
    vol = overview['volatility']
    if vol.get('current_vol'):
        print(f"Current Vol: {vol['current_vol']:.1f}%")
        print(f"20-Day Vol: {vol['vol_20d']:.1f}%")
        print(f"60-Day Vol: {vol['vol_60d']:.1f}%")
        print(f"Level: {vol['level']}")
        print(f"Market Mood: {vol['market_mood']}")
        print(f"Risk Rating: {vol['risk_rating']}")
    
    # Display US impact
    print("\n" + "-"*80)
    print("US OVERNIGHT IMPACT")
    print("-"*80)
    us = overview['us_overnight_impact']
    if us.get('available'):
        print(f"S&P 500 Close: {us['sp500_close']:.2f}")
        print(f"S&P 500 Change: {us['sp500_change_pct']:+.2f}%")
        print(f"Predicted FTSE Impact: {us['predicted_ftse_impact_pct']:+.2f}%")
        print(f"Direction: {us['direction'].upper()}")
        print(f"Confidence: {us['confidence']}%")
    
    # Display European markets
    print("\n" + "-"*80)
    print("EUROPEAN MARKETS")
    print("-"*80)
    for market, data in overview['european_markets'].items():
        print(f"{market:8s}: {data['price']:8.2f}  Change: {data['day_change']:+6.2f}%")
    
    # Display overall sentiment
    print("\n" + "-"*80)
    print("OVERALL MARKET SENTIMENT")
    print("-"*80)
    print(f"Sentiment Score: {overview['overall_sentiment']:.1f}/100")
    rec = overview['recommendation']
    print(f"Recommendation: {rec['stance']}")
    print(f"Message: {rec['message']}")
    print(f"Confidence: {rec['confidence']}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    test_uk_market_monitor()
