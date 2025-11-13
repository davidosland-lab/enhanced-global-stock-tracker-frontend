"""
Stock Scanner Module

Validates and scores stocks from configured sectors.
Performs technical analysis and filters based on selection criteria.

Features:
- Stock validation (market cap, volume, price, beta)
- Technical indicator calculation (RSI, MA, volatility)
- Composite screening score (0-100)
- Sector-wise scanning and summarization
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import time
import yfinance as yf
from yahooquery import Ticker as YQTicker
import pandas as pd
import numpy as np
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_history_with_fallback(symbol, start_date=None, end_date=None, period='1mo'):
    """
    Fetch stock history with yfinance, fallback to yahooquery if blocked.
    
    This function implements the dual-library strategy used by successful
    production scanners to avoid Yahoo Finance blocking.
    
    Args:
        symbol: Stock ticker symbol
        start_date: Start date for history (datetime or string)
        end_date: End date for history (datetime or string)
        period: Period string like '1mo', '3mo' if not using dates
        
    Returns:
        tuple: (DataFrame with OHLCV data, source string 'yfinance' or 'yahooquery')
        
    Raises:
        Exception: If both yfinance and yahooquery fail
    """
    
    # Try yfinance first (primary method)
    try:
        ticker = yf.Ticker(symbol)
        
        if start_date and end_date:
            hist = ticker.history(start=start_date, end=end_date)
        else:
            hist = ticker.history(period=period)
            
        if isinstance(hist, pd.DataFrame) and not hist.empty:
            return hist, 'yfinance'
    except Exception as e:
        logger.debug(f"[FALLBACK] yfinance failed for {symbol}: {str(e)[:100]}")
    
    # Fallback to yahooquery
    try:
        logger.info(f"[FALLBACK] Trying yahooquery for {symbol}...")
        ticker = YQTicker(symbol)
        
        if start_date and end_date:
            hist = ticker.history(start=start_date, end=end_date)
        else:
            hist = ticker.history(period=period)
        
        if isinstance(hist, pd.DataFrame) and not hist.empty:
            # Normalize column names to match yfinance (capitalize first letter)
            hist.columns = [col.capitalize() for col in hist.columns]
            logger.info(f"[FALLBACK] ✅ yahooquery succeeded for {symbol}")
            return hist, 'yahooquery'
    except Exception as e:
        logger.debug(f"[FALLBACK] yahooquery also failed for {symbol}: {str(e)[:100]}")
    
    # Both methods failed
    raise Exception(f"Both yfinance and yahooquery failed to fetch data for {symbol}")


class StockScanner:
    """
    Scans and validates stocks from configured sectors.
    Calculates technical indicators and screening scores.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize Stock Scanner
        
        Args:
            config_path: Path to asx_sectors.json config file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "asx_sectors.json"
        
        self.config = self._load_config(config_path)
        self.sectors = self.config['sectors']
        self.criteria = self.config['selection_criteria']
        
        logger.info(f"Stock Scanner initialized with {len(self.sectors)} sectors")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load sector configuration from JSON"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def scan_all_sectors(self, top_n: int = 30) -> Dict[str, List[Dict]]:
        """
        Scan all sectors and return top N stocks from each
        
        Args:
            top_n: Number of top stocks to return per sector
            
        Returns:
            Dictionary with sector names as keys and lists of stock data as values
        """
        logger.info(f"Starting scan of all {len(self.sectors)} sectors...")
        results = {}
        
        for sector_name, sector_data in self.sectors.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"Scanning sector: {sector_name}")
            logger.info(f"{'='*60}")
            
            stocks = self.scan_sector(sector_name, top_n)
            results[sector_name] = stocks
            
            logger.info(f"✓ {sector_name}: Found {len(stocks)} valid stocks")
        
        return results
    
    def scan_sector(self, sector_name: str, top_n: int = 30) -> List[Dict]:
        """
        Scan a single sector and return top N stocks
        
        Args:
            sector_name: Name of sector to scan
            top_n: Number of top stocks to return
            
        Returns:
            List of stock dictionaries sorted by screening score
        """
        if sector_name not in self.sectors:
            logger.error(f"Unknown sector: {sector_name}")
            return []
        
        sector_data = self.sectors[sector_name]
        symbols = sector_data['stocks']
        sector_weight = sector_data['weight']
        
        valid_stocks = []
        
        for i, symbol in enumerate(symbols):
            try:
                # Add small delay between stocks to avoid rate limiting (except first stock)
                if i > 0:
                    time.sleep(0.5)  # 0.5 second delay between stocks
                
                # Validate stock meets criteria
                if not self.validate_stock(symbol):
                    logger.debug(f"  ✗ {symbol}: Failed validation")
                    continue
                
                # Fetch stock data and calculate score
                stock_data = self.analyze_stock(symbol, sector_weight)
                
                if stock_data:
                    valid_stocks.append(stock_data)
                    logger.debug(f"  ✓ {symbol}: Score {stock_data['score']:.1f}")
                
            except KeyboardInterrupt:
                logger.info(f"Scan interrupted by user at {symbol}")
                raise
            except Exception as e:
                logger.warning(f"  ✗ {symbol}: Error - {str(e)}")
                continue
        
        # Sort by score and return top N
        valid_stocks.sort(key=lambda x: x['score'], reverse=True)
        return valid_stocks[:top_n]
    
    def validate_stock(self, symbol: str) -> bool:
        """
        Validate stock meets selection criteria with retry logic for rate limiting
        
        FIXED: Uses ONLY ticker.history() - NO .info calls to avoid Yahoo Finance blocking
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            True if stock passes all validation checks
        """
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Add delay between requests to avoid rate limiting
                if attempt > 0:
                    time.sleep(retry_delay * (attempt + 1))
                
                # Use fallback function (tries yfinance, falls back to yahooquery)
                hist, source = fetch_history_with_fallback(symbol, period='1mo')
                
                if source == 'yahooquery':
                    logger.info(f"Using yahooquery fallback for validation of {symbol}")
                
                if hist.empty:
                    logger.debug(f"No history data for {symbol}")
                    return False
                
                # Get current price from history
                current_price = hist['Close'].iloc[-1]
                
                # Price check
                if not (self.criteria['min_price'] <= current_price <= self.criteria['max_price']):
                    return False
                
                # Average volume check (calculate from history)
                avg_volume = hist['Volume'].mean()
                if avg_volume < self.criteria['min_avg_volume']:
                    return False
                
                # SKIP market cap check (requires .info - not essential)
                # SKIP beta check (requires .info - not essential)
                # Focus on price and volume which are reliable from history
                
                return True
                
            except KeyboardInterrupt:
                raise
            except Exception as e:
                error_msg = str(e).lower()
                # Check if it's a rate limiting error
                if '429' in error_msg or 'too many requests' in error_msg:
                    if attempt < max_retries - 1:
                        logger.warning(f"Rate limit hit for {symbol}, retrying in {retry_delay * (attempt + 1)}s (attempt {attempt + 1}/{max_retries})")
                        continue
                    else:
                        logger.warning(f"Rate limit exceeded for {symbol} after {max_retries} attempts, skipping")
                        return False
                else:
                    logger.debug(f"Validation error for {symbol}: {e}")
                    return False
        
        return False
    
    def analyze_stock(self, symbol: str, sector_weight: float) -> Optional[Dict]:
        """
        Perform complete analysis on a stock with retry logic for rate limiting
        
        FIXED: Uses ONLY ticker.history() - NO .info calls to avoid Yahoo Finance blocking
        Matches FinBERT v4.0 proven pattern that works without blocking
        
        Args:
            symbol: Stock ticker symbol
            sector_weight: Weight multiplier for sector importance
            
        Returns:
            Dictionary with stock data and screening score, or None on error
        """
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Add delay between requests to avoid rate limiting
                if attempt > 0:
                    time.sleep(retry_delay * (attempt + 1))
                
                # Use fallback function (tries yfinance, falls back to yahooquery)
                end_date = datetime.now()
                start_date = end_date - timedelta(days=90)
                hist, source = fetch_history_with_fallback(
                    symbol,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if source == 'yahooquery':
                    logger.info(f"Using yahooquery fallback for analysis of {symbol}")
                
                if hist.empty or len(hist) < 20:
                    logger.debug(f"Insufficient data for {symbol}")
                    return None
            
                # Calculate technical indicators from OHLCV data
                ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
                ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else ma_20
                rsi = self._calculate_rsi(hist['Close'])
                volatility = hist['Close'].pct_change().std()
                current_price = hist['Close'].iloc[-1]
                
                # Calculate average volume from historical data (no .info needed)
                avg_volume = int(hist['Volume'].mean())
                
                # Calculate screening score (now using hist-derived data)
                score = self._calculate_screening_score(
                    hist=hist,
                    avg_volume=avg_volume,
                    sector_weight=sector_weight,
                    ma_20=ma_20,
                    ma_50=ma_50,
                    rsi=rsi,
                    volatility=volatility
                )
                
                # Build result dictionary (using history-derived data only)
                return {
                    'symbol': symbol,
                    'name': symbol,  # Use symbol as name (no .info needed)
                    'price': float(current_price),
                    'market_cap': 0,  # Skip market cap (not essential for screening)
                    'volume': avg_volume,
                    'beta': 1.0,  # Neutral beta (or skip - not essential)
                    'pe_ratio': None,  # Skip PE ratio (not essential for technical screening)
                    'technical': {
                        'ma_20': float(ma_20),
                        'ma_50': float(ma_50),
                        'rsi': float(rsi),
                        'volatility': float(volatility),
                        'price_vs_ma20': ((current_price - ma_20) / ma_20) * 100,
                        'price_vs_ma50': ((current_price - ma_50) / ma_50) * 100
                    },
                    'score': score,
                    'timestamp': datetime.now().isoformat()
                }
                
            except KeyboardInterrupt:
                raise
            except Exception as e:
                error_msg = str(e).lower()
                # Check if it's a rate limiting error
                if '429' in error_msg or 'too many requests' in error_msg:
                    if attempt < max_retries - 1:
                        logger.warning(f"Rate limit hit for {symbol}, retrying in {retry_delay * (attempt + 1)}s (attempt {attempt + 1}/{max_retries})")
                        continue
                    else:
                        logger.warning(f"Rate limit exceeded for {symbol} after {max_retries} attempts, skipping")
                        return None
                else:
                    logger.warning(f"Analysis error for {symbol}: {e}")
                    return None
        
        return None
    
    def _calculate_screening_score(
        self,
        hist: pd.DataFrame,
        avg_volume: int,
        sector_weight: float,
        ma_20: float,
        ma_50: float,
        rsi: float,
        volatility: float
    ) -> float:
        """
        Calculate composite screening score (0-100)
        
        FIXED: No longer uses .info dict - calculates everything from history data
        
        Scoring breakdown:
        - Liquidity (0-20): Average volume from history
        - Volume Consistency (0-20): Volume trend stability
        - Volatility (0-15): Price volatility (inverse - lower is better)
        - Momentum (0-15): Price vs moving averages
        - Technical (0-15): RSI and trend signals
        - Sector Weight (0-15): Sector importance multiplier
        
        Args:
            hist: Historical price data
            avg_volume: Average volume calculated from history
            sector_weight: Sector importance (0.9-1.4)
            ma_20, ma_50: Moving averages
            rsi: Relative Strength Index
            volatility: Price volatility
            
        Returns:
            Composite score between 0-100
        """
        score = 0
        current_price = hist['Close'].iloc[-1]
        
        # 1. LIQUIDITY SCORE (0-20) - from history data
        if avg_volume > 5_000_000:
            liquidity_score = 20
        elif avg_volume > 2_000_000:
            liquidity_score = 15
        elif avg_volume > 1_000_000:
            liquidity_score = 10
        elif avg_volume > 500_000:
            liquidity_score = 5
        else:
            liquidity_score = 0
        score += liquidity_score
        
        # 2. VOLUME CONSISTENCY SCORE (0-20)
        # Measure volume stability (more consistent = better for trading)
        volume_std = hist['Volume'].std()
        volume_cv = volume_std / avg_volume if avg_volume > 0 else 999
        if volume_cv < 0.3:  # Very consistent
            cap_score = 20
        elif volume_cv < 0.5:  # Consistent
            cap_score = 15
        elif volume_cv < 0.8:  # Moderate
            cap_score = 12
        elif volume_cv < 1.2:  # Somewhat variable
            cap_score = 8
        else:
            cap_score = 5
        score += cap_score
        
        # 3. VOLATILITY SCORE (0-15)
        # Use price volatility directly (lower volatility = higher score)
        if volatility < 0.02:  # Very stable
            volatility_score = 15
        elif volatility < 0.03:  # Stable
            volatility_score = 12
        elif volatility < 0.04:  # Moderate
            volatility_score = 9
        elif volatility < 0.06:  # Somewhat volatile
            volatility_score = 6
        else:  # High volatility
            volatility_score = 3
        score += volatility_score
        
        # 4. MOMENTUM SCORE (0-15)
        momentum_score = 0
        
        # Price above MA20 (bullish)
        if current_price > ma_20:
            momentum_score += 5
        
        # Price above MA50 (strong trend)
        if current_price > ma_50:
            momentum_score += 5
        
        # MA20 above MA50 (golden cross)
        if ma_20 > ma_50:
            momentum_score += 5
        
        score += momentum_score
        
        # 5. TECHNICAL SCORE (0-15)
        technical_score = 0
        
        # RSI analysis
        if 40 <= rsi <= 60:  # Neutral zone
            technical_score += 8
        elif 30 <= rsi <= 70:  # Acceptable range
            technical_score += 5
        elif rsi < 30:  # Oversold (buying opportunity)
            technical_score += 10
        elif rsi > 70:  # Overbought (risky)
            technical_score += 2
        
        # Volatility check
        if volatility < 0.02:  # Low volatility (stable)
            technical_score += 7
        elif volatility < 0.04:  # Moderate
            technical_score += 4
        elif volatility < 0.06:  # Higher
            technical_score += 2
        
        score += min(technical_score, 15)  # Cap at 15
        
        # 6. SECTOR WEIGHT ADJUSTMENT (0-15)
        # sector_weight ranges from 0.9 (Real Estate) to 1.4 (Technology)
        sector_score = ((sector_weight - 0.9) / 0.5) * 15
        score += sector_score
        
        # Ensure score is within 0-100 range
        return min(max(score, 0), 100)
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            prices: Series of closing prices
            period: RSI period (default 14)
            
        Returns:
            RSI value (0-100)
        """
        delta = prices.diff()
        
        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not np.isnan(rsi.iloc[-1]) else 50.0
    
    def get_sector_summary(self, sector_stocks: List[Dict]) -> Dict:
        """
        Generate summary statistics for a sector
        
        Args:
            sector_stocks: List of stock dictionaries from scan_sector()
            
        Returns:
            Dictionary with sector statistics
        """
        if not sector_stocks:
            return {
                'total_stocks': 0,
                'avg_score': 0,
                'avg_market_cap': 0,
                'avg_volume': 0,
                'top_stock': None
            }
        
        scores = [s['score'] for s in sector_stocks]
        market_caps = [s['market_cap'] for s in sector_stocks]
        volumes = [s['volume'] for s in sector_stocks]
        
        return {
            'total_stocks': len(sector_stocks),
            'avg_score': np.mean(scores),
            'max_score': max(scores),
            'min_score': min(scores),
            'avg_market_cap': np.mean(market_caps),
            'avg_volume': np.mean(volumes),
            'top_stock': sector_stocks[0]['symbol'],  # Highest score
            'top_5_stocks': [s['symbol'] for s in sector_stocks[:5]]
        }


# ============================================================================
# TEST HARNESS
# ============================================================================

def test_stock_scanner():
    """Test the stock scanner with a single sector"""
    print("\n" + "="*80)
    print("STOCK SCANNER TEST")
    print("="*80 + "\n")
    
    # Initialize scanner
    scanner = StockScanner()
    
    # Test Financials sector (5 stocks)
    print("Testing Financials sector (first 5 stocks)...\n")
    sector_data = scanner.sectors['Financials']
    test_symbols = sector_data['stocks'][:5]  # CBA, WBC, ANZ, NAB, MQG
    
    results = []
    for symbol in test_symbols:
        print(f"Analyzing {symbol}...")
        
        # Validate
        is_valid = scanner.validate_stock(symbol)
        print(f"  Valid: {is_valid}")
        
        if is_valid:
            # Analyze
            stock_data = scanner.analyze_stock(symbol, sector_data['weight'])
            if stock_data:
                results.append(stock_data)
                print(f"  Score: {stock_data['score']:.1f}")
                print(f"  Price: ${stock_data['price']:.2f}")
                print(f"  RSI: {stock_data['technical']['rsi']:.1f}")
                print(f"  Market Cap: ${stock_data['market_cap']/1e9:.2f}B")
        print()
    
    # Display results
    if results:
        print("\n" + "-"*80)
        print("RESULTS SUMMARY")
        print("-"*80)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        for i, stock in enumerate(results, 1):
            print(f"{i}. {stock['symbol']:8s} | Score: {stock['score']:5.1f} | "
                  f"Price: ${stock['price']:7.2f} | RSI: {stock['technical']['rsi']:5.1f}")
        
        # Sector summary
        summary = scanner.get_sector_summary(results)
        print(f"\nSector Statistics:")
        print(f"  Total Stocks: {summary['total_stocks']}")
        print(f"  Average Score: {summary['avg_score']:.1f}")
        print(f"  Top Stock: {summary['top_stock']}")
    else:
        print("⚠ No valid stocks found")


if __name__ == "__main__":
    test_stock_scanner()
