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
import sys
import io

# Setup logging with UTF-8 encoding for Windows compatibility
if sys.platform == 'win32':
    try:
        # Try to set UTF-8 mode for stdout
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        # Python < 3.7 or output already redirected
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except:
            pass  # If all else fails, continue without UTF-8

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StockScanner:
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
            config_path = Path(__file__).parent.parent / "config" / "asx_sectors.json"
        
        self.config = self._load_config(config_path)
        
        # Handle both old format (with 'sectors' wrapper) and new format (sectors at root)
        if 'sectors' in self.config:
            self.sectors = self.config['sectors']
        else:
            # New format: sectors are at root level
            self.sectors = self.config
        
        # Selection criteria with defaults
        self.criteria = self.config.get('selection_criteria', {
            'min_price': 0.50,
            'max_price': 500.0,
            'min_avg_volume': 100000
        })
        self.logger = logger
        
        # Rate limiting settings to avoid Yahoo Finance throttling
        self.request_count = 0
        self.last_request_time = time.time()
        self.rate_limit_delay = 0.5  # 0.5s delay between requests
        
        logger.info(f"ASX Stock Scanner initialized")
        logger.info(f"Rate limiting: {self.rate_limit_delay}s delay between requests")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            # Return minimal default config (empty sectors, default criteria)
            return {
                'selection_criteria': {
                    'min_price': 0.50,
                    'max_price': 500.0,
                    'min_avg_volume': 100000
                }
            }
    
    # ========================================================================
    # DATA FETCHING - yahooquery ONLY
    # ========================================================================
    
    def _apply_rate_limit(self):
        """Apply rate limiting between requests to avoid Yahoo Finance throttling"""
        self.request_count += 1
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        # Enforce minimum delay between requests
        if elapsed < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - elapsed
            time.sleep(sleep_time)
        
        # Every 50 requests, add an extra pause to avoid aggressive rate limiting
        if self.request_count % 50 == 0:
            logger.debug(f"Rate limit pause: {self.request_count} requests made")
            time.sleep(2.0)
        
        self.last_request_time = time.time()
    
    def fetch_stock_history(self, symbol: str, start_date=None, end_date=None, period='1mo', interval='1d'):
        """
        Fetch stock history using yahooquery with rate limiting
        
        Args:
            symbol: Stock ticker
            start_date: Start date (optional)
            end_date: End date (optional)
            period: Period string if not using dates
            interval: Data interval ('1d', '1m', '5m', '15m', '1h')
            
        Returns:
            DataFrame with OHLCV data, or None on error
        """
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Apply rate limiting before request
                self._apply_rate_limit()
                
                ticker = Ticker(symbol)
                
                if start_date and end_date:
                    hist = ticker.history(start=start_date, end=end_date, interval=interval)
                else:
                    hist = ticker.history(period=period, interval=interval)
                
                if isinstance(hist, pd.DataFrame) and not hist.empty:
                    # Normalize column names
                    hist.columns = [col.capitalize() for col in hist.columns]
                    return hist
                else:
                    return None
                    
            except Exception as e:
                error_msg = str(e).lower()
                # Check if it's a rate limiting error
                if 'rate' in error_msg or 'limit' in error_msg or 'throttle' in error_msg or '429' in error_msg:
                    if attempt < max_retries - 1:
                        # Exponential backoff for rate limit errors
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Rate limit detected for {symbol}, waiting {delay}s (attempt {attempt+1}/{max_retries})")
                        time.sleep(delay)
                        continue
                
                if attempt < max_retries - 1:
                    logger.debug(f"Retry {attempt + 1} for {symbol}: {e}")
                    time.sleep(1)
                else:
                    logger.debug(f"Error fetching {symbol} after {max_retries} attempts: {e}")
                return None
        
        return None
    
    def fetch_intraday_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch intraday data for momentum analysis (1-minute bars)
        
        Args:
            symbol: Stock ticker
            
        Returns:
            Dictionary with intraday data or None
        """
        try:
            # Fetch 1-minute bars for today
            intraday_hist = self.fetch_stock_history(symbol, period='1d', interval='1m')
            
            if intraday_hist is None or intraday_hist.empty:
                logger.debug(f"No intraday data for {symbol}")
                return None
            
            # Calculate intraday metrics
            current_price = float(intraday_hist['Close'].iloc[-1])
            open_price = float(intraday_hist['Open'].iloc[0])
            high_price = float(intraday_hist['High'].max())
            low_price = float(intraday_hist['Low'].min())
            current_volume = int(intraday_hist['Volume'].sum())
            
            # Extract price series for momentum calculations
            prices = intraday_hist['Close'].values
            
            # Calculate momentum metrics
            session_change_pct = ((current_price - open_price) / open_price) * 100 if open_price > 0 else 0
            intraday_range_pct = ((high_price - low_price) / open_price) * 100 if open_price > 0 else 0
            
            # 15-minute momentum (if enough data)
            mom_15m = 0
            if len(prices) >= 15:
                price_15m_ago = float(prices[-15])
                mom_15m = ((current_price - price_15m_ago) / price_15m_ago) * 100 if price_15m_ago > 0 else 0
            
            # 60-minute momentum (if enough data)
            mom_60m = 0
            if len(prices) >= 60:
                price_60m_ago = float(prices[-60])
                mom_60m = ((current_price - price_60m_ago) / price_60m_ago) * 100 if price_60m_ago > 0 else 0
            
            return {
                'current_price': current_price,
                'open_price': open_price,
                'high_price': high_price,
                'low_price': low_price,
                'current_volume': current_volume,
                'session_change_pct': session_change_pct,
                'intraday_range_pct': intraday_range_pct,
                'momentum_15m': mom_15m,
                'momentum_60m': mom_60m,
                'prices': prices.tolist(),  # For advanced calculations
                'data_points': len(prices)
            }
            
        except Exception as e:
            logger.debug(f"Error fetching intraday data for {symbol}: {e}")
            return None
    
    # ========================================================================
    # STOCK VALIDATION
    # ========================================================================
    
    def validate_stock(self, symbol: str) -> bool:
        """
        Validate stock meets selection criteria with enhanced error handling
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            True if stock passes validation
        """
        try:
            # Fetch recent data (rate limiting is handled in fetch_stock_history)
            hist = self.fetch_stock_history(symbol, period='1mo')
            
            if hist is None or hist.empty:
                logger.debug(f"{symbol}: No history data available")
                return False
            
            # Get current price
            current_price = hist['Close'].iloc[-1]
            
            # Price check
            if not (self.criteria['min_price'] <= current_price <= self.criteria['max_price']):
                logger.debug(f"{symbol}: Price ${current_price:.2f} out of range [{self.criteria['min_price']}-{self.criteria['max_price']}]")
                return False
            
            # Volume check
            avg_volume = hist['Volume'].mean()
            if avg_volume < self.criteria['min_avg_volume']:
                logger.debug(f"{symbol}: Avg volume {int(avg_volume):,} below minimum {self.criteria['min_avg_volume']:,}")
                return False
            
            logger.debug(f"{symbol}: ✓ Validation passed (Price: ${current_price:.2f}, Volume: {int(avg_volume):,})")
            return True
            
        except Exception as e:
            logger.debug(f"{symbol}: Validation failed - {e}")
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
    
    def analyze_stock(self, symbol: str, sector_weight: float, include_intraday: bool = False) -> Optional[Dict]:
        """
        Perform complete analysis on a stock
        
        Args:
            symbol: Stock ticker symbol
            sector_weight: Weight multiplier for sector importance
            include_intraday: If True, fetch intraday data for momentum analysis
            
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
                result = {
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
                
                # Fetch intraday data if requested (for intraday mode)
                if include_intraday:
                    intraday_data = self.fetch_intraday_data(symbol)
                    if intraday_data:
                        result['intraday_data'] = intraday_data
                        # Update current price with intraday price if available
                        result['price'] = intraday_data['current_price']
                        logger.debug(f"{symbol}: Intraday data included ({intraday_data['data_points']} points)")
                    else:
                        logger.debug(f"{symbol}: No intraday data available")
                
                return result
                
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
    
    def scan_sector(self, sector_name: str, top_n: int = 10, include_intraday: bool = False) -> List[Dict]:
        """
        Scan stocks in a specific sector
        
        Args:
            sector_name: Name of sector to scan
            top_n: Number of top stocks to return
            include_intraday: If True, fetch intraday data for momentum analysis
            
        Returns:
            List of stock dictionaries sorted by score
        """
        if sector_name not in self.sectors:
            logger.error(f"Unknown sector: {sector_name}")
            return []
        
        sector_data = self.sectors[sector_name]
        symbols = sector_data['stocks']
        sector_weight = sector_data.get('weight', 1.0)  # Default weight = 1.0 if not specified
        
        mode_indicator = "📈 INTRADAY" if include_intraday else "🌙 OVERNIGHT"
        logger.info(f"\n{'='*80}")
        logger.info(f"Scanning {sector_name} Sector ({len(symbols)} stocks) - {mode_indicator}")
        logger.info(f"{'='*80}\n")
        
        valid_stocks = []
        validation_failures = 0
        analysis_failures = 0
        
        for i, symbol in enumerate(symbols):
            try:
                # Rate limiting is handled in fetch_stock_history, no need for additional sleep
                logger.info(f"[{i+1}/{len(symbols)}] Processing {symbol}...")
                
                # Validate
                if not self.validate_stock(symbol):
                    logger.info(f"  ✗ {symbol}: Failed validation")
                    validation_failures += 1
                    continue
                
                # Analyze (with or without intraday data)
                stock_data = self.analyze_stock(symbol, sector_weight, include_intraday=include_intraday)
                
                if stock_data:
                    valid_stocks.append(stock_data)
                    intraday_info = ""
                    if include_intraday and 'intraday_data' in stock_data:
                        intraday_data = stock_data['intraday_data']
                        intraday_info = f" | Mom: {intraday_data['session_change_pct']:+.2f}%"
                    logger.info(f"  ✓ {symbol}: Score {stock_data['score']:.0f}/100{intraday_info}")
                else:
                    logger.info(f"  ✗ {symbol}: Analysis failed")
                    analysis_failures += 1
                    
            except KeyboardInterrupt:
                logger.info("\n\nScan interrupted by user")
                break
            except Exception as e:
                logger.error(f"  ✗ {symbol}: Error - {e}")
                analysis_failures += 1
                continue
        
        # Sort by score and return top N
        valid_stocks.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Sector Summary: {len(valid_stocks)}/{len(symbols)} stocks validated")
        if validation_failures > 0:
            logger.info(f"  ⚠️  Validation failures: {validation_failures}/{len(symbols)} stocks")
        if analysis_failures > 0:
            logger.info(f"  ⚠️  Analysis failures: {analysis_failures}/{len(symbols)} stocks")
        if include_intraday:
            intraday_count = sum(1 for s in valid_stocks if 'intraday_data' in s)
            logger.info(f"  📈 Intraday data: {intraday_count}/{len(valid_stocks)} stocks")
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
    
    def get_sector_summary(self, stocks: List[Dict]) -> Dict:
        """
        Generate summary statistics for a sector's scan results
        
        Args:
            stocks: List of stock dictionaries from scan_sector
            
        Returns:
            Dictionary with sector statistics
        """
        if not stocks:
            return {
                'total_stocks': 0,
                'avg_score': 0,
                'top_score': 0,
                'score_range': (0, 0)
            }
        
        scores = [s['score'] for s in stocks if 'score' in s]
        
        return {
            'total_stocks': len(stocks),
            'avg_score': sum(scores) / len(scores) if scores else 0,
            'top_score': max(scores) if scores else 0,
            'bottom_score': min(scores) if scores else 0,
            'score_range': (min(scores), max(scores)) if scores else (0, 0),
            'high_quality_count': len([s for s in scores if s >= 75]),
            'medium_quality_count': len([s for s in scores if 50 <= s < 75]),
            'low_quality_count': len([s for s in scores if s < 50])
        }


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
