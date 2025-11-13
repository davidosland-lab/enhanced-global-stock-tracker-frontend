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
import pandas as pd
import numpy as np
from pathlib import Path

# Import our optimized data fetcher
from .alpha_vantage_fetcher import AlphaVantageDataFetcher as HybridDataFetcher

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StockScanner:
    """
    Scans and validates stocks from configured sectors.
    Calculates technical indicators and screening scores.
    """
    
    def __init__(self, config_path: str = None, use_batch_fetching: bool = True, cache_ttl_minutes: int = 240):
        """
        Initialize Stock Scanner (ALPHA VANTAGE MODE)
        
        Args:
            config_path: Path to asx_sectors.json config file
            use_batch_fetching: Enable batch fetching with caching (recommended)
            cache_ttl_minutes: Cache time-to-live in minutes (240 = 4 hours for Alpha Vantage)
        """
        if config_path is None:
            # Use fast config by default (5 stocks per sector for Alpha Vantage limits)
            config_path = Path(__file__).parent.parent / "config" / "asx_sectors_fast.json"
        
        self.config = self._load_config(config_path)
        self.sectors = self.config['sectors']
        self.criteria = self.config['selection_criteria']
        
        # Rate limiting configuration - INCREASED FOR STABILITY
        self.base_delay = 2.0  # Base delay between stocks (seconds)
        self.max_retries = 3   # Max retry attempts for 429 errors
        self.retry_backoff = 5  # Exponential backoff multiplier
        
        # Initialize optimized data fetcher
        self.use_batch_fetching = use_batch_fetching
        if use_batch_fetching:
            self.data_fetcher = HybridDataFetcher(cache_ttl_minutes=cache_ttl_minutes)
            logger.info(f"Stock Scanner initialized with BATCH FETCHING enabled")
            logger.info(f"  Cache TTL: {cache_ttl_minutes} minutes")
        else:
            self.data_fetcher = None
            logger.info(f"Stock Scanner initialized with INDIVIDUAL FETCHING (legacy mode)")
        
        logger.info(f"  Sectors: {len(self.sectors)}")
        logger.info(f"  Rate limiting: {self.base_delay}s base delay, {self.max_retries} retries")
    
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
        
        # Use batch fetching if enabled (MUCH faster and avoids rate limits)
        if self.use_batch_fetching and self.data_fetcher:
            return self._scan_sector_batch(symbols, sector_weight, top_n)
        else:
            return self._scan_sector_individual(symbols, sector_weight, top_n)
    
    def _scan_sector_batch(self, symbols: List[str], sector_weight: float, top_n: int) -> List[Dict]:
        """
        Scan sector using optimized batch fetching with PRICE-BASED validation.
        
        This method:
        1. Pre-validates all stocks using price data (NO /quoteSummary calls)
        2. Batch-fetches historical data for valid stocks
        3. Analyzes all stocks with minimal API calls and NO fundamentals lookups
        
        Args:
            symbols: List of ticker symbols
            sector_weight: Sector importance weight
            top_n: Number of top stocks to return
            
        Returns:
            List of stock dictionaries sorted by screening score
        """
        logger.info(f"Batch scanning {len(symbols)} symbols (price-based validation)...")
        
        # Step 1: Validate all stocks using price data (NO quoteSummary)
        valid_symbols = self.data_fetcher.validate_stock_batch(symbols, self.criteria)
        logger.info(f"  Validation: {len(valid_symbols)}/{len(symbols)} passed")
        
        if not valid_symbols:
            return []
        
        # Step 2: Batch fetch historical data for valid stocks
        hist_data = self.data_fetcher.fetch_batch(valid_symbols, period='3mo', interval='1d')
        logger.info(f"  Batch fetch: {len(hist_data)}/{len(valid_symbols)} tickers retrieved")
        
        # Step 3: Analyze each stock with pre-fetched OHLCV data ONLY
        # NO info/fundamentals lookups - compute everything from price data
        valid_stocks = []
        for symbol in valid_symbols:
            try:
                hist = hist_data.get(symbol)
                if hist is None or hist.empty or len(hist) < 20:
                    logger.debug(f"  ✗ {symbol}: Insufficient data")
                    continue
                
                # Build lightweight "info" dict from price data (no fundamentals)
                # This avoids ANY /quoteSummary calls
                mock_info = {
                    'longName': symbol,  # We don't have company name
                    'marketCap': 0,  # Unknown - not needed for scoring
                    'averageVolume': int(hist['Volume'].tail(20).mean()) if 'Volume' in hist else 0,
                    'beta': 1.0,  # Default neutral beta
                    'trailingPE': None,  # Unknown - not needed
                    'currentPrice': float(hist['Close'].iloc[-1])
                }
                
                # Analyze with pre-fetched data
                stock_data = self._analyze_with_data(symbol, hist, mock_info, sector_weight)
                
                if stock_data:
                    valid_stocks.append(stock_data)
                    logger.debug(f"  ✓ {symbol}: Score {stock_data['score']:.1f}")
                
            except Exception as e:
                logger.warning(f"  ✗ {symbol}: Analysis error - {str(e)[:100]}")
                continue
        
        # Sort by score and return top N
        valid_stocks.sort(key=lambda x: x['score'], reverse=True)
        return valid_stocks[:top_n]
    
    def _scan_sector_individual(self, symbols: List[str], sector_weight: float, top_n: int) -> List[Dict]:
        """
        Scan sector using individual stock fetching (legacy mode)
        
        Args:
            symbols: List of ticker symbols
            sector_weight: Sector importance weight
            top_n: Number of top stocks to return
            
        Returns:
            List of stock dictionaries sorted by screening score
        """
        valid_stocks = []
        
        for i, symbol in enumerate(symbols):
            try:
                # Add delay between stocks to avoid rate limiting
                # IMPORTANT: Delay BEFORE request, not after
                if i > 0:
                    time.sleep(self.base_delay)  # Increased to 2 seconds
                
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
        Validate stock meets selection criteria with enhanced retry logic for rate limiting
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            True if stock passes all validation checks
        """
        for attempt in range(self.max_retries):
            try:
                # Wait before retry (exponential backoff)
                if attempt > 0:
                    backoff_time = self.retry_backoff * (2 ** (attempt - 1))  # 5s, 10s, 20s
                    logger.info(f"Retry {attempt}/{self.max_retries} for {symbol} after {backoff_time}s backoff")
                    time.sleep(backoff_time)
                
                # Create ticker and fetch info in try-catch
                stock = yf.Ticker(symbol)
                
                # This is where 429 errors occur - wrap it carefully
                try:
                    info = stock.info
                except Exception as info_error:
                    # Check if this is a rate limit or connection error
                    error_str = str(info_error).lower()
                    if '429' in error_str or 'too many requests' in error_str or 'rate limit' in error_str:
                        if attempt < self.max_retries - 1:
                            logger.warning(f"Rate limit (429) hit for {symbol}, will retry")
                            continue  # Retry with backoff
                        else:
                            logger.warning(f"Rate limit persists for {symbol} after {self.max_retries} attempts, skipping")
                            return False
                    else:
                        # Other error (network, timeout, etc) - skip this stock
                        logger.debug(f"Error fetching info for {symbol}: {info_error}")
                        return False
                
                # If we got here, we have valid info - do validation checks
                # Market cap check
                market_cap = info.get('marketCap', 0)
                if market_cap < self.criteria['min_market_cap']:
                    return False
                
                # Average volume check
                avg_volume = info.get('averageVolume', 0)
                if avg_volume < self.criteria['min_avg_volume']:
                    return False
                
                # Price check
                current_price = info.get('currentPrice', 0)
                if not (self.criteria['min_price'] <= current_price <= self.criteria['max_price']):
                    return False
                
                # Beta check (volatility)
                beta = info.get('beta')
                if beta is not None:
                    if not (self.criteria['beta_min'] <= beta <= self.criteria['beta_max']):
                        return False
                
                # All checks passed
                return True
                
            except KeyboardInterrupt:
                # Allow clean exit
                logger.info(f"Scan interrupted by user at {symbol}")
                raise
            except Exception as e:
                # Catch-all for any other unexpected errors
                logger.warning(f"Unexpected error validating {symbol}: {str(e)[:100]}")
                return False
        
        # If we exhausted all retries
        return False
    
    def _analyze_with_data(self, symbol: str, hist: pd.DataFrame, info: Dict, sector_weight: float) -> Optional[Dict]:
        """
        Analyze stock with pre-fetched data (used by batch fetching)
        
        Args:
            symbol: Stock ticker symbol
            hist: Pre-fetched historical data
            info: Pre-fetched ticker info
            sector_weight: Sector importance weight
            
        Returns:
            Dictionary with stock data and screening score, or None on error
        """
        try:
            # Calculate technical indicators
            ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else ma_20
            rsi = self._calculate_rsi(hist['Close'])
            volatility = hist['Close'].pct_change().std()
            current_price = hist['Close'].iloc[-1]
            
            # Calculate screening score
            score = self._calculate_screening_score(
                hist=hist,
                info=info,
                sector_weight=sector_weight,
                ma_20=ma_20,
                ma_50=ma_50,
                rsi=rsi,
                volatility=volatility
            )
            
            # Build result dictionary
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'price': float(current_price),
                'market_cap': info.get('marketCap', 0),
                'volume': info.get('averageVolume', 0),
                'beta': info.get('beta', 1.0),
                'pe_ratio': info.get('trailingPE'),
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
        except Exception as e:
            logger.warning(f"Analysis error for {symbol}: {str(e)[:100]}")
            return None
    
    def analyze_stock(self, symbol: str, sector_weight: float) -> Optional[Dict]:
        """
        Perform complete analysis on a stock with retry logic for rate limiting
        
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
                stock = yf.Ticker(symbol)
                
                # Add delay between requests to avoid rate limiting
                if attempt > 0:
                    time.sleep(retry_delay * (attempt + 1))
                
                info = stock.info
                
                # Fetch 3 months of historical data
                end_date = datetime.now()
                start_date = end_date - timedelta(days=90)
                hist = stock.history(start=start_date, end=end_date)
                
                if hist.empty or len(hist) < 20:
                    logger.debug(f"Insufficient data for {symbol}")
                    return None
            
                # Calculate technical indicators
                ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
                ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else ma_20
                rsi = self._calculate_rsi(hist['Close'])
                volatility = hist['Close'].pct_change().std()
                current_price = hist['Close'].iloc[-1]
                
                # Calculate screening score
                score = self._calculate_screening_score(
                    hist=hist,
                    info=info,
                    sector_weight=sector_weight,
                    ma_20=ma_20,
                    ma_50=ma_50,
                    rsi=rsi,
                    volatility=volatility
                )
                
                # Build result dictionary
                return {
                    'symbol': symbol,
                    'name': info.get('longName', symbol),
                    'price': float(current_price),
                    'market_cap': info.get('marketCap', 0),
                    'volume': info.get('averageVolume', 0),
                    'beta': info.get('beta', 1.0),
                    'pe_ratio': info.get('trailingPE'),
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
        info: Dict,
        sector_weight: float,
        ma_20: float,
        ma_50: float,
        rsi: float,
        volatility: float
    ) -> float:
        """
        Calculate composite screening score (0-100)
        
        Scoring breakdown:
        - Liquidity (0-20): Average volume and market cap
        - Market Cap (0-20): Company size and stability
        - Volatility (0-15): Risk assessment (beta)
        - Momentum (0-15): Price vs moving averages
        - Technical (0-15): RSI and trend signals
        - Sector Weight (0-15): Sector importance multiplier
        
        Args:
            hist: Historical price data
            info: Stock info from yfinance
            sector_weight: Sector importance (0.9-1.4)
            ma_20, ma_50: Moving averages
            rsi: Relative Strength Index
            volatility: Price volatility
            
        Returns:
            Composite score between 0-100
        """
        score = 0
        current_price = hist['Close'].iloc[-1]
        
        # 1. LIQUIDITY SCORE (0-20)
        avg_volume = info.get('averageVolume', 0)
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
        
        # 2. MARKET CAP SCORE (0-20)
        market_cap = info.get('marketCap', 0)
        if market_cap > 10_000_000_000:  # >$10B (large cap)
            cap_score = 20
        elif market_cap > 5_000_000_000:  # $5-10B
            cap_score = 15
        elif market_cap > 1_000_000_000:  # $1-5B (mid cap)
            cap_score = 12
        elif market_cap > 500_000_000:    # $500M-1B
            cap_score = 8
        else:
            cap_score = 5
        score += cap_score
        
        # 3. VOLATILITY SCORE (0-15)
        beta = info.get('beta', 1.0)
        if beta is not None:
            if 0.8 <= beta <= 1.3:  # Ideal range
                volatility_score = 15
            elif 0.5 <= beta <= 1.5:  # Acceptable
                volatility_score = 10
            elif 0.3 <= beta <= 2.0:  # Higher risk
                volatility_score = 5
            else:  # Too volatile or too stable
                volatility_score = 0
        else:
            volatility_score = 7  # Neutral if unknown
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
