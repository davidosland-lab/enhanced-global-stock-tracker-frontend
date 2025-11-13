"""
ASX Stock Scanner
=================

Selects and validates top stocks from each ASX sector based on defined criteria.
Supports filtering by market cap, liquidity, volatility, and technical indicators.

Author: FinBERT v4.4
Date: November 2025
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import yfinance as yf
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class StockScanner:
    """
    Scans and validates ASX stocks across multiple sectors
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize stock scanner with sector configuration
        
        Args:
            config_path: Path to asx_sectors.json configuration file
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), 
                '../config/asx_sectors.json'
            )
        
        self.config = self.load_config(config_path)
        self.sectors = self.config['sectors']
        self.criteria = self.config['selection_criteria']
        
        logger.info(f"Stock Scanner initialized with {len(self.sectors)} sectors")
    
    def load_config(self, config_path: str) -> Dict:
        """Load sector configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            raise
    
    def scan_all_sectors(self, top_n: int = 30) -> Dict[str, List[Dict]]:
        """
        Scan all sectors and return top N stocks from each
        
        Args:
            top_n: Number of top stocks to return per sector
            
        Returns:
            Dictionary mapping sector names to lists of stock data
        """
        logger.info(f"Starting full sector scan (top {top_n} per sector)...")
        
        results = {}
        total_stocks = 0
        
        for sector_name, sector_data in self.sectors.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"Scanning {sector_name} sector...")
            logger.info(f"{'='*60}")
            
            stocks = self.scan_sector(sector_name, top_n)
            results[sector_name] = stocks
            total_stocks += len(stocks)
            
            logger.info(f"✓ {sector_name}: {len(stocks)} stocks selected")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Scan complete: {total_stocks} total stocks from {len(results)} sectors")
        logger.info(f"{'='*60}\n")
        
        return results
    
    def scan_sector(self, sector_name: str, top_n: int = 30) -> List[Dict]:
        """
        Scan a specific sector and return top N stocks
        
        Args:
            sector_name: Name of the sector to scan
            top_n: Number of top stocks to return
            
        Returns:
            List of validated stock data dictionaries
        """
        if sector_name not in self.sectors:
            raise ValueError(f"Unknown sector: {sector_name}")
        
        sector_data = self.sectors[sector_name]
        stock_symbols = sector_data['stocks']
        sector_weight = sector_data.get('weight', 1.0)
        
        logger.info(f"Processing {len(stock_symbols)} stocks in {sector_name}...")
        
        validated_stocks = []
        failed_count = 0
        
        for i, symbol in enumerate(stock_symbols, 1):
            logger.info(f"  [{i}/{len(stock_symbols)}] Validating {symbol}...")
            
            try:
                if self.validate_stock(symbol):
                    stock_data = self.get_stock_data(symbol, sector_name, sector_weight)
                    if stock_data:
                        validated_stocks.append(stock_data)
                        logger.info(f"    ✓ {symbol}: Score={stock_data['screening_score']:.1f}")
                    else:
                        failed_count += 1
                        logger.warning(f"    ✗ {symbol}: Failed to fetch data")
                else:
                    failed_count += 1
                    logger.warning(f"    ✗ {symbol}: Failed validation criteria")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"    ✗ {symbol}: Error - {str(e)}")
        
        # Sort by screening score
        validated_stocks.sort(key=lambda x: x['screening_score'], reverse=True)
        
        # Return top N
        top_stocks = validated_stocks[:top_n]
        
        logger.info(f"\n  Summary: {len(top_stocks)} stocks selected, {failed_count} failed")
        
        return top_stocks
    
    def validate_stock(self, symbol: str) -> bool:
        """
        Validate stock against basic criteria
        
        Args:
            symbol: Stock symbol to validate
            
        Returns:
            True if stock meets all criteria, False otherwise
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Check market cap
            market_cap = info.get('marketCap', 0)
            if market_cap < self.criteria['min_market_cap']:
                logger.debug(f"{symbol}: Market cap too low (${market_cap/1e6:.1f}M)")
                return False
            
            # Check average volume
            avg_volume = info.get('averageVolume', 0)
            if avg_volume < self.criteria['min_avg_volume']:
                logger.debug(f"{symbol}: Volume too low ({avg_volume:,})")
                return False
            
            # Check current price
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            if current_price < self.criteria['min_price']:
                logger.debug(f"{symbol}: Price too low (${current_price:.2f})")
                return False
            
            # Check if suspended or in trading halt
            if self.criteria['exclude_suspended']:
                trading_status = info.get('market', '').lower()
                if 'suspended' in trading_status or 'halt' in trading_status:
                    logger.debug(f"{symbol}: Trading suspended/halted")
                    return False
            
            # Check beta if available
            beta = info.get('beta')
            if beta is not None:
                if not (self.criteria['beta_min'] <= beta <= self.criteria['beta_max']):
                    logger.debug(f"{symbol}: Beta out of range ({beta:.2f})")
                    return False
            
            return True
            
        except Exception as e:
            logger.debug(f"{symbol}: Validation error - {str(e)}")
            return False
    
    def get_stock_data(self, symbol: str, sector: str, sector_weight: float) -> Optional[Dict]:
        """
        Get comprehensive stock data for screening
        
        Args:
            symbol: Stock symbol
            sector: Sector name
            sector_weight: Sector importance weight
            
        Returns:
            Dictionary with stock data or None if failed
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Get historical data for technical analysis
            hist = stock.history(period='3mo', interval='1d')
            
            if hist.empty:
                logger.warning(f"{symbol}: No historical data available")
                return None
            
            # Calculate technical indicators
            current_price = hist['Close'].iloc[-1]
            ma_20 = hist['Close'].rolling(20).mean().iloc[-1] if len(hist) >= 20 else current_price
            ma_50 = hist['Close'].rolling(50).mean().iloc[-1] if len(hist) >= 50 else current_price
            
            # Calculate volatility (annualized)
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252) if len(returns) > 0 else 0
            
            # RSI calculation
            rsi = self.calculate_rsi(hist['Close']) if len(hist) >= 14 else 50
            
            # Calculate screening score
            screening_score = self.calculate_screening_score(
                hist, info, sector_weight, ma_20, ma_50, rsi, volatility
            )
            
            stock_data = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': sector,
                'price': float(current_price),
                'market_cap': info.get('marketCap', 0),
                'volume': info.get('averageVolume', 0),
                'beta': info.get('beta', 1.0),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield', 0),
                'ma_20': float(ma_20),
                'ma_50': float(ma_50),
                'rsi': float(rsi),
                'volatility': float(volatility),
                'price_above_ma20': current_price > ma_20,
                'price_above_ma50': current_price > ma_50,
                'screening_score': screening_score,
                'last_updated': datetime.now().isoformat()
            }
            
            return stock_data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """
        Calculate Relative Strength Index
        
        Args:
            prices: Series of closing prices
            period: RSI period (default 14)
            
        Returns:
            RSI value (0-100)
        """
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
            
        except Exception:
            return 50.0  # Neutral RSI if calculation fails
    
    def calculate_screening_score(
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
        
        Scoring factors:
        - Liquidity (0-20 points)
        - Market cap (0-20 points)
        - Volatility appropriateness (0-15 points)
        - Price momentum (0-15 points)
        - Technical indicators (0-15 points)
        - Sector weight (0-15 points)
        
        Args:
            hist: Historical price data
            info: Stock info dictionary
            sector_weight: Sector importance multiplier
            ma_20, ma_50: Moving averages
            rsi: Relative Strength Index
            volatility: Annualized volatility
            
        Returns:
            Screening score (0-100)
        """
        score = 0
        
        # 1. Liquidity Score (0-20 points)
        avg_volume = info.get('averageVolume', 0)
        if avg_volume > 5_000_000:
            score += 20
        elif avg_volume > 2_000_000:
            score += 15
        elif avg_volume > 1_000_000:
            score += 10
        elif avg_volume > 500_000:
            score += 5
        
        # 2. Market Cap Score (0-20 points)
        market_cap = info.get('marketCap', 0)
        if market_cap > 20_000_000_000:  # $20B+ (Large cap)
            score += 20
        elif market_cap > 10_000_000_000:  # $10B+ (Mid-large cap)
            score += 15
        elif market_cap > 2_000_000_000:  # $2B+ (Mid cap)
            score += 10
        elif market_cap > 500_000_000:  # $500M+ (Small cap)
            score += 5
        
        # 3. Volatility Score (0-15 points)
        # Prefer moderate volatility (0.15 - 0.35 annualized)
        beta = info.get('beta', 1.0)
        if 0.8 <= beta <= 1.3:
            score += 15
        elif 0.5 <= beta <= 1.5:
            score += 10
        elif 0.3 <= beta <= 2.0:
            score += 5
        
        # 4. Price Momentum Score (0-15 points)
        current_price = hist['Close'].iloc[-1]
        if current_price > ma_50 > ma_20:  # Strong uptrend
            score += 15
        elif current_price > ma_50:  # Above MA50
            score += 10
        elif current_price > ma_20:  # Above MA20
            score += 5
        
        # 5. Technical Indicators Score (0-15 points)
        # RSI: Prefer not overbought/oversold
        if 40 <= rsi <= 60:  # Neutral zone
            score += 8
        elif 30 <= rsi < 40 or 60 < rsi <= 70:  # Moderate
            score += 5
        
        # MACD signal (simplified - using price vs MA)
        if current_price > ma_20:
            score += 7
        
        # 6. Sector Weight Bonus (0-15 points)
        sector_bonus = min(15, sector_weight * 10)
        score += sector_bonus
        
        return round(min(score, 100), 2)
    
    def get_sector_summary(self, sector_stocks: Dict[str, List[Dict]]) -> Dict:
        """
        Generate summary statistics for scanned sectors
        
        Args:
            sector_stocks: Dictionary of sector name to stock lists
            
        Returns:
            Summary statistics dictionary
        """
        summary = {
            'total_sectors': len(sector_stocks),
            'total_stocks': sum(len(stocks) for stocks in sector_stocks.values()),
            'sectors': {}
        }
        
        for sector_name, stocks in sector_stocks.items():
            if stocks:
                scores = [s['screening_score'] for s in stocks]
                summary['sectors'][sector_name] = {
                    'count': len(stocks),
                    'avg_score': round(np.mean(scores), 2),
                    'max_score': round(max(scores), 2),
                    'min_score': round(min(scores), 2),
                    'top_stock': stocks[0]['symbol'],
                    'avg_market_cap': round(np.mean([s['market_cap'] for s in stocks]) / 1e9, 2)
                }
        
        return summary


if __name__ == '__main__':
    # Test the scanner
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scanner = StockScanner()
    
    # Test scanning a single sector
    print("\n=== Testing Financials Sector ===")
    financials = scanner.scan_sector('Financials', top_n=10)
    
    print(f"\nTop 10 Financials:")
    for i, stock in enumerate(financials, 1):
        print(f"{i}. {stock['symbol']} - Score: {stock['screening_score']}")
