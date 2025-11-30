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
        
        # Rate limiting settings to avoid Yahoo Finance throttling
        self.request_count = 0
        self.last_request_time = time.time()
        self.rate_limit_delay = 0.5  # Increased from 0.1s to 0.5s between requests
        
        logger.info(f"US Stock Scanner initialized with {len(self.sectors)} sectors")
        logger.info(f"Rate limiting: {self.rate_limit_delay}s delay between requests")
    
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
        Fetch US stock history using yahooquery with rate limiting
        
        Args:
            symbol: Stock ticker (no suffix needed for US stocks)
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
            symbol: US stock ticker (no suffix)
            
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
        Validate US stock meets selection criteria with enhanced error handling
        
        Args:
            symbol: Stock ticker symbol (no suffix)
            
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
            
            # Price check (US market: $5-$1000 typical range)
            if not (self.criteria['min_price'] <= current_price <= self.criteria['max_price']):
                logger.debug(f"{symbol}: Price ${current_price:.2f} out of range [{self.criteria['min_price']}-{self.criteria['max_price']}]")
                return False
            
            # Volume check (US market: typically higher volume)
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
    
    def _fetch_fundamentals(self, symbol: str) -> Dict:
        """
        Fetch fundamental data (market cap, beta, sector, name) using yahooquery
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with fundamental data (with safe defaults)
        """
        fundamentals = {
            'name': symbol,  # Default to ticker if name not found
            'market_cap': 0,
            'beta': 1.0,
            'sector_name': 'Unknown'
        }
        
        try:
            ticker = Ticker(symbol)
            
            # Get price info for company name
            price_info = ticker.price
            if isinstance(price_info, dict) and symbol in price_info:
                data = price_info[symbol]
                if isinstance(data, dict):
                    fundamentals['name'] = data.get('shortName', data.get('longName', symbol))
            
            # Get summary detail for market cap and beta
            summary_detail = ticker.summary_detail
            if isinstance(summary_detail, dict) and symbol in summary_detail:
                data = summary_detail[symbol]
                if isinstance(data, dict):
                    fundamentals['market_cap'] = data.get('marketCap', 0)
                    fundamentals['beta'] = data.get('beta', 1.0)
            
            # Get asset profile for sector
            asset_profile = ticker.asset_profile
            if isinstance(asset_profile, dict) and symbol in asset_profile:
                data = asset_profile[symbol]
                if isinstance(data, dict):
                    fundamentals['sector_name'] = data.get('sector', 'Unknown')
            
            logger.debug(f"{symbol}: {fundamentals['name']} - MCap: ${fundamentals['market_cap']/1e9:.1f}B, Beta: {fundamentals['beta']:.2f}, Sector: {fundamentals['sector_name']}")
            
        except Exception as e:
            logger.debug(f"{symbol}: Could not fetch fundamentals: {e}")
        
        return fundamentals
    
    def analyze_stock(self, symbol: str, sector_weight: float, include_intraday: bool = False) -> Optional[Dict]:
        """
        Perform complete analysis on a US stock
        
        Args:
            symbol: Stock ticker symbol
            sector_weight: Sector importance weight
            include_intraday: If True, fetch intraday data for momentum analysis
            
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
            
            # Fetch fundamental data (market cap, beta, sector)
            fundamentals = self._fetch_fundamentals(symbol)
            
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
            
            result = {
                'symbol': symbol,
                'name': fundamentals['name'],
                'price': float(current_price),
                'price_change': float(price_change),
                'volume': int(volume),
                'avg_volume': int(avg_volume),
                'score': float(score),
                'scan_time': datetime.now().isoformat(),
                # Fundamental data
                'market_cap': fundamentals['market_cap'],
                'beta': fundamentals['beta'],
                'sector_name': fundamentals['sector_name'],
                # Nested technical dictionary for batch_predictor compatibility
                'technical': {
                    'rsi': float(rsi),
                    'ma_20': float(ma_data['ma20']),
                    'ma_50': float(ma_data['ma50']),
                    'volatility': float(volatility),
                    'above_ma20': ma_data['above_ma20'],
                    'above_ma50': ma_data['above_ma50']
                }
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
    
    def scan_sector(self, sector_name: str, max_stocks: int = 30, include_intraday: bool = False) -> List[Dict]:
        """
        Scan all stocks in a US sector
        
        Args:
            sector_name: Name of the sector to scan
            max_stocks: Maximum number of stocks to analyze
            include_intraday: If True, fetch intraday data for momentum analysis
            
        Returns:
            List of analyzed stocks, sorted by score
        """
        if sector_name not in self.sectors:
            logger.error(f"Sector {sector_name} not found in config")
            return []
        
        sector_data = self.sectors[sector_name]
        sector_weight = sector_data.get('weight', 1.0)
        stocks = sector_data.get('stocks', [])[:max_stocks]
        
        mode_indicator = "📈 INTRADAY" if include_intraday else "🌙 OVERNIGHT"
        logger.info(f"Scanning {sector_name}: {len(stocks)} stocks - {mode_indicator}")
        
        results = []
        validation_failures = 0
        analysis_failures = 0
        
        for i, symbol in enumerate(stocks, 1):
            try:
                # Validate stock (rate limiting is handled in fetch_stock_history)
                if not self.validate_stock(symbol):
                    validation_failures += 1
                    continue
                
                # Analyze stock (with or without intraday data)
                analysis = self.analyze_stock(symbol, sector_weight, include_intraday=include_intraday)
                if analysis:
                    analysis['sector'] = sector_name
                    results.append(analysis)
                    
                    intraday_info = ""
                    if include_intraday and 'intraday_data' in analysis:
                        intraday_data = analysis['intraday_data']
                        intraday_info = f" | Mom: {intraday_data['session_change_pct']:+.2f}%"
                    
                    logger.debug(f"{i}/{len(stocks)}: {symbol} - Score: {analysis['score']:.1f}{intraday_info}")
                else:
                    analysis_failures += 1
                
            except Exception as e:
                logger.debug(f"Error scanning {symbol}: {e}")
                analysis_failures += 1
                continue
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"✓ {sector_name}: {len(results)}/{len(stocks)} stocks analyzed")
        if validation_failures > 0:
            logger.info(f"  ⚠️  Validation failures: {validation_failures}/{len(stocks)} stocks")
        if analysis_failures > 0:
            logger.info(f"  ⚠️  Analysis failures: {analysis_failures}/{len(stocks)} stocks")
        if include_intraday:
            intraday_count = sum(1 for s in results if 'intraday_data' in s)
            logger.info(f"  📈 Intraday data: {intraday_count}/{len(results)} stocks")
        
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
