"""
Market Timezone Manager
Handles different market timezones and trading hours
"""

import logging
from datetime import datetime, time
from typing import Dict, Optional, Tuple
import pytz

logger = logging.getLogger(__name__)


class MarketTimezoneManager:
    """Manages market timezones and trading hours for different exchanges"""
    
    # Market definitions with timezones and trading hours
    MARKETS = {
        'US': {
            'timezone': 'US/Eastern',
            'open_time': time(9, 30),
            'close_time': time(16, 0),
            'pre_market_prediction_time': time(8, 0),  # Generate predictions at 8:00 AM (90 min before open)
            'description': 'US Markets (NYSE, NASDAQ)',
            'suffixes': ['', '.US'],  # No suffix or .US
            'examples': ['AAPL', 'TSLA', 'GOOGL', 'MSFT']
        },
        'AU': {
            'timezone': 'Australia/Sydney',
            'open_time': time(10, 0),
            'close_time': time(16, 0),
            'pre_market_prediction_time': time(8, 30),  # Generate predictions at 8:30 AM (90 min before open)
            'description': 'Australian Securities Exchange (ASX)',
            'suffixes': ['.AX'],
            'examples': ['BHP.AX', 'CBA.AX', 'WBC.AX', 'EVN.AX']
        },
        'UK': {
            'timezone': 'Europe/London',
            'open_time': time(8, 0),
            'close_time': time(16, 30),
            'pre_market_prediction_time': time(6, 30),  # Generate predictions at 6:30 AM (90 min before open)
            'description': 'London Stock Exchange (LSE)',
            'suffixes': ['.L'],
            'examples': ['BP.L', 'HSBA.L', 'SHEL.L', 'VOD.L']
        }
    }
    
    def __init__(self):
        """Initialize market timezone manager"""
        self.markets = {}
        for market_code, market_info in self.MARKETS.items():
            self.markets[market_code] = {
                **market_info,
                'tz': pytz.timezone(market_info['timezone'])
            }
        logger.info(f"MarketTimezoneManager initialized with {len(self.markets)} markets")
    
    def detect_market(self, symbol: str) -> str:
        """
        Detect which market a symbol trades on based on suffix
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'BHP.AX', 'BP.L')
        
        Returns:
            Market code ('US', 'AU', 'UK')
        """
        symbol_upper = symbol.upper()
        
        # Check each market's suffixes
        for market_code, market_info in self.markets.items():
            for suffix in market_info['suffixes']:
                if suffix and symbol_upper.endswith(suffix):
                    logger.info(f"Detected {symbol} → {market_code} market (suffix: {suffix})")
                    return market_code
        
        # Default to US market if no suffix matches
        logger.info(f"Detected {symbol} → US market (default)")
        return 'US'
    
    def get_market_info(self, market_code: str) -> Dict:
        """
        Get market information
        
        Args:
            market_code: Market code ('US', 'AU', 'UK')
        
        Returns:
            Market information dictionary
        """
        return self.markets.get(market_code, self.markets['US'])
    
    def get_prediction_time(self, symbol: str, date: Optional[datetime] = None) -> datetime:
        """
        Get the time when prediction should be generated for a symbol
        (90 minutes before market open)
        
        Args:
            symbol: Stock symbol
            date: Date for prediction (default: today)
        
        Returns:
            Datetime when prediction should be generated
        """
        market_code = self.detect_market(symbol)
        market_info = self.markets[market_code]
        tz = market_info['tz']
        
        if date is None:
            date = datetime.now(tz)
        
        # Create prediction time (e.g., 8:00 AM for US, 8:30 AM for AU)
        prediction_datetime = datetime.combine(
            date.date(),
            market_info['pre_market_prediction_time']
        )
        prediction_datetime = tz.localize(prediction_datetime)
        
        # Skip weekends
        while prediction_datetime.weekday() >= 5:
            prediction_datetime = prediction_datetime + timedelta(days=1)
        
        logger.debug(f"Prediction time for {symbol} ({market_code}): {prediction_datetime}")
        return prediction_datetime
    
    def get_market_open_time(self, symbol: str, date: Optional[datetime] = None) -> datetime:
        """
        Get market open time for a symbol
        
        Args:
            symbol: Stock symbol
            date: Date for market open (default: today)
        
        Returns:
            Datetime of market open
        """
        market_code = self.detect_market(symbol)
        market_info = self.markets[market_code]
        tz = market_info['tz']
        
        if date is None:
            date = datetime.now(tz)
        
        open_datetime = datetime.combine(date.date(), market_info['open_time'])
        open_datetime = tz.localize(open_datetime)
        
        # Skip weekends
        while open_datetime.weekday() >= 5:
            open_datetime = open_datetime + timedelta(days=1)
        
        return open_datetime
    
    def get_market_close_time(self, symbol: str, date: Optional[datetime] = None) -> datetime:
        """
        Get market close time for a symbol
        
        Args:
            symbol: Stock symbol
            date: Date for market close (default: today)
        
        Returns:
            Datetime of market close
        """
        market_code = self.detect_market(symbol)
        market_info = self.markets[market_code]
        tz = market_info['tz']
        
        if date is None:
            date = datetime.now(tz)
        
        close_datetime = datetime.combine(date.date(), market_info['close_time'])
        close_datetime = tz.localize(close_datetime)
        
        # Skip weekends
        while close_datetime.weekday() >= 5:
            close_datetime = close_datetime + timedelta(days=1)
        
        return close_datetime
    
    def is_market_open(self, symbol: str) -> bool:
        """
        Check if market is currently open for a symbol
        
        Args:
            symbol: Stock symbol
        
        Returns:
            True if market is open, False otherwise
        """
        market_code = self.detect_market(symbol)
        market_info = self.markets[market_code]
        tz = market_info['tz']
        
        now = datetime.now(tz)
        
        # Weekend check
        if now.weekday() >= 5:
            return False
        
        # Time check
        market_open = now.replace(
            hour=market_info['open_time'].hour,
            minute=market_info['open_time'].minute,
            second=0,
            microsecond=0
        )
        
        market_close = now.replace(
            hour=market_info['close_time'].hour,
            minute=market_info['close_time'].minute,
            second=0,
            microsecond=0
        )
        
        is_open = market_open <= now <= market_close
        
        logger.debug(f"Market for {symbol} ({market_code}) is {'OPEN' if is_open else 'CLOSED'}")
        return is_open
    
    def should_generate_prediction(self, symbol: str) -> bool:
        """
        Check if prediction should be generated now
        (Between prediction time and market open)
        
        Args:
            symbol: Stock symbol
        
        Returns:
            True if prediction should be generated
        """
        market_code = self.detect_market(symbol)
        market_info = self.markets[market_code]
        tz = market_info['tz']
        
        now = datetime.now(tz)
        
        # Weekend check
        if now.weekday() >= 5:
            return False
        
        prediction_time = self.get_prediction_time(symbol, now)
        market_open = self.get_market_open_time(symbol, now)
        
        # Should generate if:
        # 1. It's after prediction time
        # 2. It's before market open
        should_generate = prediction_time <= now < market_open
        
        if should_generate:
            logger.info(f"✓ Should generate prediction for {symbol} ({market_code})")
        else:
            logger.debug(f"Prediction window: {prediction_time} - {market_open}, Now: {now}")
        
        return should_generate
    
    def can_generate_prediction(self, symbol: str) -> Tuple[bool, str]:
        """
        Check if prediction can be generated now
        Returns both status and reason
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Tuple of (can_generate: bool, reason: str)
        """
        market_code = self.detect_market(symbol)
        market_info = self.markets[market_code]
        tz = market_info['tz']
        
        now = datetime.now(tz)
        
        # Weekend check
        if now.weekday() >= 5:
            return False, "Market closed (weekend)"
        
        prediction_time = self.get_prediction_time(symbol, now)
        market_open = self.get_market_open_time(symbol, now)
        market_close = self.get_market_close_time(symbol, now)
        
        # Before prediction time
        if now < prediction_time:
            return False, f"Too early (prediction time: {prediction_time.strftime('%H:%M %Z')})"
        
        # After market close
        if now > market_close:
            return False, f"Market closed (closes at {market_close.strftime('%H:%M %Z')})"
        
        # Between prediction time and market open (ideal time)
        if prediction_time <= now < market_open:
            return True, f"Pre-market window ({prediction_time.strftime('%H:%M')} - {market_open.strftime('%H:%M %Z')})"
        
        # During market hours (can generate but warn)
        if market_open <= now <= market_close:
            return True, f"Market is OPEN (opened at {market_open.strftime('%H:%M %Z')})"
        
        return False, "Unknown state"
    
    def get_next_prediction_time(self, symbol: str) -> datetime:
        """
        Get the next prediction time for a symbol
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Next prediction datetime
        """
        market_code = self.detect_market(symbol)
        market_info = self.markets[market_code]
        tz = market_info['tz']
        
        now = datetime.now(tz)
        next_pred = self.get_prediction_time(symbol, now)
        
        # If prediction time has passed today, get tomorrow's
        if now >= next_pred:
            next_pred = self.get_prediction_time(symbol, now + timedelta(days=1))
        
        return next_pred


# Singleton instance
_market_tz_manager = None

def get_market_tz_manager() -> MarketTimezoneManager:
    """Get singleton market timezone manager instance"""
    global _market_tz_manager
    if _market_tz_manager is None:
        _market_tz_manager = MarketTimezoneManager()
    return _market_tz_manager
