"""
Stock Scanner - yahooquery ONLY Implementation
NO yfinance, NO Alpha Vantage - Pure yahooquery

Simplified, clean implementation focused on reliability
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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StockScannerYahooQueryOnly:
    """
    Stock Scanner using ONLY yahooquery
    
    Features:
    - Stock validation (price, volume)
    - Technical analysis (RSI, MA, volatility)
    - Scoring system (0-100)
    - Sector-wise scanning
    """
    
    def __init__(self, config_path: str = None):
        """Initialize scanner with config"""
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "asx_sectors.json"
        
        self.config = self._load_config(config_path)
        self.sectors = self.config['sectors']
        self.criteria = self.config['selection_criteria']
        self.logger = logger
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            # Return minimal default config
            return {
                'sectors': {},
                'selection_criteria': {
                    'min_price': 0.50,
                    'max_price': 500.0,
                    'min_avg_volume': 100000
                }
            }
    
    # ========================================================================
    # DATA FETCHING - yahooquery ONLY
    # ========================================================================
    
    def fetch_stock_history(self, symbol: str, start_date=None, end_date=None, period='1mo'):
        """
        Fetch stock history using yahooquery
        
        Args:
            symbol: Stock ticker
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
        Validate stock meets selection criteria
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            True if stock passes validation
        """
        max_retries = 2
        retry_delay = 1  # seconds
        
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
                
                # Price check
                if not (self.criteria['min_price'] <= current_price <= self.criteria['max_price']):
                    logger.debug(f"{symbol}: Price ${current_price:.2f} out of range")
                    return False
                
                # Volume check
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
            return 50.0  # Neutral RSI
    
    def analyze_stock(self, symbol: str, sector_weight: float) -> Optional[Dict]:
        """
        Perform complete analysis on a stock
        
        Args:
            symbol: Stock ticker symbol
            sector_weight: Weight multiplier for sector importance
            
        Returns:
            Dictionary with stock data and score, or None on error
        """
        max_retries = 2
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    time.sleep(retry_delay)
                
                # Fetch 3 months of data
                end_date = datetime.now()
                start_date = end_date - timedelta(days=90)
                hist = self.fetch_stock_history(symbol, start_date=start_date, end_date=end_date)
                
                if hist is None or hist.empty or len(hist) < 20:
                    logger.debug(f"Insufficient data for {symbol}")
                    return None
                
                # Calculate technical indicators
                ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
                ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else ma_20
                rsi = self._calculate_rsi(hist['Close'])
                volatility = hist['Close'].pct_change().std()
                current_price = hist['Close'].iloc[-1]
                avg_volume = int(hist['Volume'].mean())
                
                # Calculate score
                score = self._calculate_score(
                    hist=hist,
                    avg_volume=avg_volume,
                    sector_weight=sector_weight,
                    ma_20=ma_20,
                    ma_50=ma_50,
                    rsi=rsi,
                    volatility=volatility
                )
                
                # Build result
                return {
                    'symbol': symbol,
                    'name': symbol,
                    'price': float(current_price),
                    'volume': avg_volume,
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
                if attempt < max_retries - 1:
                    logger.debug(f"Retry {attempt + 1} for {symbol}")
                    continue
                else:
                    logger.warning(f"Analysis error for {symbol}: {e}")
                    return None
        
        return None
    
    def _calculate_score(
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
        
        Scoring:
        - Liquidity (0-20): Volume
        - Momentum (0-20): Price vs MAs
        - Technical (0-20): RSI
        - Volatility (0-20): Lower is better
        - Sector Weight (0-20): Sector importance
        """
        score = 0
        current_price = hist['Close'].iloc[-1]
        
        # Liquidity score (0-20)
        if avg_volume > 1000000:
            score += 20
        elif avg_volume > 500000:
            score += 15
        elif avg_volume > 200000:
            score += 10
        else:
            score += 5
        
        # Momentum score (0-20)
        if current_price > ma_20 > ma_50:
            score += 20
        elif current_price > ma_20:
            score += 15
        elif current_price > ma_50:
            score += 10
        else:
            score += 5
        
        # RSI score (0-20)
        if 40 <= rsi <= 60:  # Neutral range
            score += 20
        elif 30 <= rsi <= 70:  # Not extreme
            score += 15
        else:
            score += 5
        
        # Volatility score (0-20) - lower is better
        if volatility < 0.015:
            score += 20
        elif volatility < 0.025:
            score += 15
        elif volatility < 0.035:
            score += 10
        else:
            score += 5
        
        # Sector weight (0-20)
        sector_score = 10 + (10 * (sector_weight - 1.0))
        score += max(0, min(20, sector_score))
        
        return min(100, score)
    
    # ========================================================================
    # SECTOR SCANNING
    # ========================================================================
    
    def scan_sector(self, sector_name: str, top_n: int = 10) -> List[Dict]:
        """
        Scan stocks in a specific sector
        
        Args:
            sector_name: Name of sector to scan
            top_n: Number of top stocks to return
            
        Returns:
            List of stock dictionaries sorted by score
        """
        if sector_name not in self.sectors:
            logger.error(f"Unknown sector: {sector_name}")
            return []
        
        sector_data = self.sectors[sector_name]
        symbols = sector_data['stocks']
        sector_weight = sector_data['weight']
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Scanning {sector_name} Sector ({len(symbols)} stocks)")
        logger.info(f"{'='*80}\n")
        
        valid_stocks = []
        
        for i, symbol in enumerate(symbols):
            try:
                # Small delay between stocks
                if i > 0:
                    time.sleep(0.5)
                
                logger.info(f"[{i+1}/{len(symbols)}] Processing {symbol}...")
                
                # Validate
                if not self.validate_stock(symbol):
                    logger.info(f"  ✗ {symbol}: Failed validation")
                    continue
                
                # Analyze
                stock_data = self.analyze_stock(symbol, sector_weight)
                
                if stock_data:
                    valid_stocks.append(stock_data)
                    logger.info(f"  ✓ {symbol}: Score {stock_data['score']:.0f}/100")
                else:
                    logger.info(f"  ✗ {symbol}: Analysis failed")
                    
            except KeyboardInterrupt:
                logger.info("\n\nScan interrupted by user")
                break
            except Exception as e:
                logger.error(f"  ✗ {symbol}: Error - {e}")
                continue
        
        # Sort by score and return top N
        valid_stocks.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Sector Summary: {len(valid_stocks)} stocks validated")
        logger.info(f"{'='*80}\n")
        
        return valid_stocks[:top_n]
    
    def scan_all_sectors(self, top_n_per_sector: int = 10) -> Dict[str, List[Dict]]:
        """
        Scan all configured sectors
        
        Args:
            top_n_per_sector: Top stocks per sector
            
        Returns:
            Dictionary mapping sector names to stock lists
        """
        results = {}
        
        logger.info(f"\n{'#'*80}")
        logger.info(f"FULL MARKET SCAN - {len(self.sectors)} SECTORS")
        logger.info(f"{'#'*80}\n")
        
        for sector_name in self.sectors:
            stocks = self.scan_sector(sector_name, top_n_per_sector)
            results[sector_name] = stocks
        
        logger.info(f"\n{'#'*80}")
        logger.info(f"SCAN COMPLETE")
        logger.info(f"{'#'*80}\n")
        
        return results


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def run_financial_sector_test():
    """Quick test on Financial sector only"""
    scanner = StockScannerYahooQueryOnly()
    results = scanner.scan_sector('Financial', top_n=5)
    
    if results:
        logger.info("\nTop Financial Stocks:\n")
        logger.info(f"{'Rank':<6} {'Symbol':<10} {'Price':<10} {'Score':<8}")
        logger.info("-" * 40)
        
        for i, stock in enumerate(results, 1):
            logger.info(
                f"{i:<6} "
                f"{stock['symbol']:<10} "
                f"${stock['price']:<9.2f} "
                f"{stock['score']:<8.0f}"
            )
    
    return results


if __name__ == "__main__":
    run_financial_sector_test()
