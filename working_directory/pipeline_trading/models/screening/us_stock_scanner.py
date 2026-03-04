"""
US Stock Scanner - yahooquery ONLY Implementation
Specialized for US market (NYSE/NASDAQ)

Key Differences from ASX Scanner:
- No .AX suffix on tickers
- US market hours and timezone
- Higher volume/market cap thresholds
- US-specific technical indicators
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time
from yahooquery import Ticker
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import io

# Setup logging with UTF-8 encoding for Windows compatibility
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except:
            pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class USStockScanner:
    """
    US Stock Scanner using ONLY yahooquery
    
    Features:
    - Stock validation (price, volume, market cap)
    - Technical analysis (RSI, MA, volatility)
    - Scoring system (0-100)
    - Sector-wise scanning for US markets
    """
    
    def __init__(self, config_path: str = None):
        """Initialize US scanner with config"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "us_sectors.json"
        
        self.config = self._load_config(config_path)
        
        # Handle both old format (with 'sectors' wrapper) and new format (sectors at root)
        if 'sectors' in self.config:
            self.sectors = self.config['sectors']
        else:
            self.sectors = self.config
        
        # US-specific selection criteria with defaults
        self.criteria = self.config.get('selection_criteria', {
            'min_price': 5.00,
            'max_price': 1000.0,
            'min_avg_volume': 1000000,
            'min_market_cap': 2000000000
        })
        self.logger = logger
        logger.info(f"US Stock Scanner initialized with {len(self.sectors)} sectors")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {
                'selection_criteria': {
                    'min_price': 5.00,
                    'max_price': 1000.0,
                    'min_avg_volume': 1000000,
                    'min_market_cap': 2000000000
                }
            }
    
    # ========================================================================
    # DATA FETCHING - yahooquery ONLY
    # ========================================================================
    
    def fetch_stock_history(self, symbol: str, start_date=None, end_date=None, period='1mo'):
        """
        Fetch US stock history using yahooquery
        
        Args:
            symbol: Stock ticker (no suffix needed for US stocks)
            start_date: Start date (optional)
            end_date: End date (optional)
            period: Period string if not using dates
            
        Returns:
            DataFrame with OHLCV data, or None on error
        """
        try:
            ticker = Ticker(symbol)
            
            if start_date and end_date:
                hist = ticker.history(start=start_date, end=end_date)
            else:
                hist = ticker.history(period=period)
            
            if isinstance(hist, pd.DataFrame) and not hist.empty:
                # Normalize column names
                hist.columns = [col.capitalize() for col in hist.columns]
                return hist
            else:
                return None
                
        except Exception as e:
            logger.debug(f"Error fetching {symbol}: {e}")
            return None
    
    # ========================================================================
    # STOCK VALIDATION
    # ========================================================================
    
    def validate_stock(self, symbol: str) -> bool:
        """
        Validate US stock meets selection criteria
        
        Args:
            symbol: Stock ticker symbol (no suffix)
            
        Returns:
            True if stock passes validation
        """
        max_retries = 2
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    time.sleep(retry_delay)
                
                # Fetch recent data
                hist = self.fetch_stock_history(symbol, period='1mo')
                
                if hist is None or hist.empty:
                    logger.debug(f"No history data for {symbol}")
                    return False
                
                # Get current price
                current_price = hist['Close'].iloc[-1]
                
                # Price check (US market: $5-$1000 typical range)
                if not (self.criteria['min_price'] <= current_price <= self.criteria['max_price']):
                    logger.debug(f"{symbol}: Price ${current_price:.2f} out of range")
                    return False
                
                # Volume check (US market: typically higher volume)
                avg_volume = hist['Volume'].mean()
                if avg_volume < self.criteria['min_avg_volume']:
                    logger.debug(f"{symbol}: Volume {int(avg_volume):,} too low")
                    return False
                
                return True
                
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.debug(f"Retry {attempt + 1} for {symbol}")
                    continue
                else:
                    logger.debug(f"Validation error for {symbol}: {e}")
                    return False
        
        return False
    
    # ========================================================================
    # TECHNICAL ANALYSIS
    # ========================================================================
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1])
        except:
            return 50.0
    
    def _calculate_moving_averages(self, prices: pd.Series) -> Dict:
        """Calculate moving averages"""
        try:
            ma20 = prices.rolling(window=20).mean().iloc[-1]
            ma50 = prices.rolling(window=50).mean().iloc[-1]
            current_price = prices.iloc[-1]
            
            return {
                'ma20': float(ma20),
                'ma50': float(ma50),
                'above_ma20': current_price > ma20,
                'above_ma50': current_price > ma50
            }
        except:
            return {'ma20': 0, 'ma50': 0, 'above_ma20': False, 'above_ma50': False}
    
    def _calculate_volatility(self, prices: pd.Series) -> float:
        """Calculate annualized volatility"""
        try:
            returns = prices.pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)  # 252 trading days
            return float(volatility)
        except:
            return 0.0
    
    def analyze_stock(self, symbol: str, sector_weight: float) -> Optional[Dict]:
        """
        Perform complete analysis on a US stock
        
        Args:
            symbol: Stock ticker symbol
            sector_weight: Sector importance weight
            
        Returns:
            Dictionary with analysis results, or None if analysis fails
        """
        try:
            # Fetch 3 months of data for analysis
            hist = self.fetch_stock_history(symbol, period='3mo')
            
            if hist is None or len(hist) < 20:
                logger.debug(f"{symbol}: Insufficient data")
                return None
            
            # Extract basic data
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].mean()
            
            # Calculate technical indicators
            rsi = self._calculate_rsi(hist['Close'])
            ma_data = self._calculate_moving_averages(hist['Close'])
            volatility = self._calculate_volatility(hist['Close'])
            
            # Calculate price change
            price_change = ((current_price - prev_close) / prev_close) * 100
            
            # Calculate score (0-100)
            score = self._calculate_score(
                rsi=rsi,
                above_ma20=ma_data['above_ma20'],
                above_ma50=ma_data['above_ma50'],
                volatility=volatility,
                volume_ratio=volume / avg_volume,
                sector_weight=sector_weight
            )
            
            return {
                'symbol': symbol,
                'price': float(current_price),
                'price_change': float(price_change),
                'volume': int(volume),
                'avg_volume': int(avg_volume),
                'rsi': float(rsi),
                'ma20': float(ma_data['ma20']),
                'ma50': float(ma_data['ma50']),
                'volatility': float(volatility),
                'score': float(score),
                'above_ma20': ma_data['above_ma20'],
                'above_ma50': ma_data['above_ma50'],
                'scan_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.debug(f"Analysis error for {symbol}: {e}")
            return None
    
    def _calculate_score(self, rsi: float, above_ma20: bool, above_ma50: bool, 
                        volatility: float, volume_ratio: float, sector_weight: float) -> float:
        """
        Calculate opportunity score (0-100)
        
        Scoring factors:
        - RSI (oversold = higher score)
        - Moving averages (above = higher score)
        - Volume (high volume = higher score)
        - Volatility (moderate volatility preferred)
        - Sector weight
        """
        score = 0.0
        
        # RSI scoring (30 points)
        if rsi < 30:  # Oversold
            score += 30
        elif rsi < 40:
            score += 20
        elif 40 <= rsi <= 60:  # Neutral
            score += 15
        elif rsi < 70:
            score += 10
        else:  # Overbought
            score += 5
        
        # Moving average scoring (25 points)
        if above_ma50:
            score += 15
        if above_ma20:
            score += 10
        
        # Volume scoring (20 points)
        if volume_ratio > 2.0:
            score += 20
        elif volume_ratio > 1.5:
            score += 15
        elif volume_ratio > 1.0:
            score += 10
        else:
            score += 5
        
        # Volatility scoring (15 points) - prefer moderate volatility
        if 0.15 < volatility < 0.35:  # Sweet spot
            score += 15
        elif 0.10 < volatility < 0.50:
            score += 10
        else:
            score += 5
        
        # Sector weight bonus (10 points)
        score += min(sector_weight * 10, 10)
        
        return min(score, 100.0)
    
    # ========================================================================
    # SECTOR SCANNING
    # ========================================================================
    
    def scan_sector(self, sector_name: str, max_stocks: int = 30) -> List[Dict]:
        """
        Scan all stocks in a US sector
        
        Args:
            sector_name: Name of the sector to scan
            max_stocks: Maximum number of stocks to analyze
            
        Returns:
            List of analyzed stocks, sorted by score
        """
        if sector_name not in self.sectors:
            logger.error(f"Sector {sector_name} not found in config")
            return []
        
        sector_data = self.sectors[sector_name]
        sector_weight = sector_data.get('weight', 1.0)
        stocks = sector_data.get('stocks', [])[:max_stocks]
        
        logger.info(f"Scanning {sector_name}: {len(stocks)} stocks")
        
        results = []
        for i, symbol in enumerate(stocks, 1):
            try:
                # Validate stock
                if not self.validate_stock(symbol):
                    logger.debug(f"{symbol}: Failed validation")
                    continue
                
                # Analyze stock
                analysis = self.analyze_stock(symbol, sector_weight)
                if analysis:
                    analysis['sector'] = sector_name
                    results.append(analysis)
                    logger.debug(f"{i}/{len(stocks)}: {symbol} - Score: {analysis['score']:.1f}")
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.debug(f"Error scanning {symbol}: {e}")
                continue
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"✓ {sector_name}: {len(results)}/{len(stocks)} stocks analyzed")
        return results
    
    def scan_all_sectors(self, stocks_per_sector: int = 30) -> Dict[str, List[Dict]]:
        """
        Scan all configured US sectors
        
        Args:
            stocks_per_sector: Number of stocks to scan per sector
            
        Returns:
            Dictionary mapping sector name to list of analyzed stocks
        """
        logger.info("="*80)
        logger.info("STARTING US MARKET SECTOR SCAN")
        logger.info(f"Sectors: {len(self.sectors)}")
        logger.info(f"Stocks per sector: {stocks_per_sector}")
        logger.info("="*80)
        
        results = {}
        total_stocks = 0
        
        for sector_name in self.sectors.keys():
            sector_results = self.scan_sector(sector_name, stocks_per_sector)
            results[sector_name] = sector_results
            total_stocks += len(sector_results)
        
        logger.info("="*80)
        logger.info(f"SCAN COMPLETE: {total_stocks} stocks analyzed")
        logger.info("="*80)
        
        return results
    
    def get_top_opportunities(self, sector_results: Dict[str, List[Dict]], 
                            top_n: int = 20) -> List[Dict]:
        """
        Get top N opportunities across all sectors
        
        Args:
            sector_results: Results from scan_all_sectors()
            top_n: Number of top opportunities to return
            
        Returns:
            List of top opportunities sorted by score
        """
        all_stocks = []
        for sector_stocks in sector_results.values():
            all_stocks.extend(sector_stocks)
        
        # Sort by score
        all_stocks.sort(key=lambda x: x['score'], reverse=True)
        
        return all_stocks[:top_n]


if __name__ == "__main__":
    # Test the US scanner
    scanner = USStockScanner()
    
    # Test single stock
    print("\nTesting single stock analysis: AAPL")
    result = scanner.analyze_stock("AAPL", sector_weight=1.4)
    if result:
        print(f"✓ AAPL Analysis:")
        print(f"  Price: ${result['price']:.2f}")
        print(f"  RSI: {result['rsi']:.1f}")
        print(f"  Score: {result['score']:.1f}")
    
    # Test sector scan
    print("\nTesting Technology sector scan (5 stocks):")
    tech_results = scanner.scan_sector("Technology", max_stocks=5)
    print(f"✓ Scanned {len(tech_results)} Technology stocks")
    for stock in tech_results[:3]:
        print(f"  {stock['symbol']}: ${stock['price']:.2f} - Score: {stock['score']:.1f}")
