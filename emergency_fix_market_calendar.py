"""
EMERGENCY FIX - Replace market_calendar.py with correct version

Run this in your project directory:
C:\\Users\\david\\Regime_trading\\complete_backend_clean_install_v1.3.15\\

Command:
    python emergency_fix_market_calendar.py
"""

import shutil
from pathlib import Path

# Your correct file content
CORRECT_MARKET_CALENDAR = '''# -*- coding: utf-8 -*-
"""
Market Calendar Module
Provides market hours and trading session information

This is a stub implementation to prevent import errors.
Full implementation can be added as needed.
"""

from enum import Enum
from datetime import datetime, time
from typing import Optional
import pytz


class Exchange(Enum):
    """Supported exchanges"""
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    LSE = "LSE"
    ASX = "ASX"


class MarketStatus(Enum):
    """Market status enumeration"""
    OPEN = "open"
    CLOSED = "closed"
    PRE_MARKET = "pre_market"
    AFTER_HOURS = "after_hours"
    POST_MARKET = "after_hours"  # Alias for after_hours
    HOLIDAY = "holiday"
    WEEKEND = "weekend"  # Explicit weekend status


class MarketStatusInfo:
    """Market status information object"""
    def __init__(self, status: MarketStatus, exchange: Exchange, current_time: datetime,
                 market_open: time, market_close: time, timezone, holiday_name: Optional[str] = None):
        self.status = status
        self.exchange = exchange
        self.current_time = current_time
        self.market_open = market_open
        self.market_close = market_close
        self.timezone = timezone
        self.holiday_name = holiday_name or ""
        
        # Calculate time_to_open and time_to_close
        self.time_to_open = None
        self.time_to_close = None
        
        if status == MarketStatus.OPEN:
            # Calculate time until market close
            close_dt = current_time.replace(
                hour=market_close.hour,
                minute=market_close.minute,
                second=0,
                microsecond=0
            )
            if close_dt > current_time:
                self.time_to_close = close_dt - current_time
        elif status in [MarketStatus.CLOSED, MarketStatus.PRE_MARKET, MarketStatus.AFTER_HOURS, MarketStatus.WEEKEND]:
            # Calculate time until market open
            import datetime as dt_module
            open_dt = current_time.replace(
                hour=market_open.hour,
                minute=market_open.minute,
                second=0,
                microsecond=0
            )
            
            # If before market open today
            if current_time.time() < market_open:
                if current_time.weekday() < 5:  # Weekday
                    self.time_to_open = open_dt - current_time
                else:  # Weekend - find next Monday
                    days_ahead = 7 - current_time.weekday()
                    open_dt = open_dt + dt_module.timedelta(days=days_ahead)
                    self.time_to_open = open_dt - current_time
            else:
                # After market close - next trading day
                if current_time.weekday() == 4:  # Friday
                    days_ahead = 3  # Skip to Monday
                elif current_time.weekday() == 5:  # Saturday
                    days_ahead = 2
                elif current_time.weekday() == 6:  # Sunday
                    days_ahead = 1
                else:
                    days_ahead = 1
                
                open_dt = open_dt + dt_module.timedelta(days=days_ahead)
                self.time_to_open = open_dt - current_time
    
    def __repr__(self):
        return f"MarketStatusInfo(status={self.status}, exchange={self.exchange})"


class MarketCalendar:
    """
    Market calendar for tracking trading hours and sessions
    """
    
    # Market hours (local time)
    MARKET_HOURS = {
        Exchange.NYSE: {
            'timezone': 'America/New_York',
            'open': time(9, 30),
            'close': time(16, 0),
            'pre_market': time(4, 0),
            'after_hours': time(20, 0)
        },
        Exchange.NASDAQ: {
            'timezone': 'America/New_York',
            'open': time(9, 30),
            'close': time(16, 0),
            'pre_market': time(4, 0),
            'after_hours': time(20, 0)
        },
        Exchange.LSE: {
            'timezone': 'Europe/London',
            'open': time(8, 0),
            'close': time(16, 30),
            'pre_market': time(5, 0),
            'after_hours': time(20, 0)
        },
        Exchange.ASX: {
            'timezone': 'Australia/Sydney',
            'open': time(10, 0),
            'close': time(16, 0),
            'pre_market': time(7, 0),
            'after_hours': time(19, 0)
        }
    }
    
    def __init__(self, exchange: Exchange = Exchange.NYSE):
        """
        Initialize market calendar for a specific exchange
        
        Args:
            exchange: Target exchange
        """
        self.exchange = exchange
        self.hours = self.MARKET_HOURS.get(exchange)
        if self.hours:
            self.timezone = pytz.timezone(self.hours['timezone'])
        else:
            self.timezone = pytz.UTC
    
    def get_market_status(self, exchange_or_dt=None) -> 'MarketStatusInfo':
        """
        Get current market status
        
        Args:
            exchange_or_dt: Exchange enum OR datetime to check (None = current exchange, now)
            
        Returns:
            MarketStatusInfo object with status, exchange, and time info
        """
        # Handle overloaded parameter
        if isinstance(exchange_or_dt, Exchange):
            # Create a new calendar for the specified exchange
            calendar = MarketCalendar(exchange_or_dt)
            return calendar.get_market_status(None)
        
        # Standard datetime check
        dt = exchange_or_dt
        if dt is None:
            dt = datetime.now(self.timezone)
        elif hasattr(dt, 'tzinfo'):
            if dt.tzinfo is None:
                dt = self.timezone.localize(dt)
            else:
                dt = dt.astimezone(self.timezone)
        else:
            # If not a datetime, treat as current time
            dt = datetime.now(self.timezone)
        
        # Check if weekend
        if dt.weekday() >= 5:  # Saturday = 5, Sunday = 6
            status = MarketStatus.WEEKEND
        else:
            current_time = dt.time()
            
            # Check trading hours
            if self.hours['open'] <= current_time < self.hours['close']:
                status = MarketStatus.OPEN
            elif self.hours['pre_market'] <= current_time < self.hours['open']:
                status = MarketStatus.PRE_MARKET
            elif self.hours['close'] <= current_time < self.hours['after_hours']:
                status = MarketStatus.AFTER_HOURS
            else:
                status = MarketStatus.CLOSED
        
        # Return MarketStatusInfo object
        return MarketStatusInfo(
            status=status,
            exchange=self.exchange,
            current_time=dt,
            market_open=self.hours['open'],
            market_close=self.hours['close'],
            timezone=self.timezone,
            holiday_name=None
        )
    
    def is_market_open(self, dt: Optional[datetime] = None) -> bool:
        """
        Check if market is currently open
        
        Args:
            dt: Datetime to check (None = now)
            
        Returns:
            True if market is open
        """
        info = self.get_market_status(dt)
        return info.status == MarketStatus.OPEN
    
    def is_trading_day(self, dt: Optional[datetime] = None) -> bool:
        """
        Check if given date is a trading day (not weekend/holiday)
        
        Args:
            dt: Datetime to check (None = now)
            
        Returns:
            True if trading day
        """
        if dt is None:
            dt = datetime.now(self.timezone)
        elif hasattr(dt, 'tzinfo'):
            if dt.tzinfo is None:
                dt = self.timezone.localize(dt)
            else:
                dt = dt.astimezone(self.timezone)
        
        # Basic check: not weekend
        # TODO: Add holiday calendar support
        return dt.weekday() < 5
    
    def get_next_market_open(self, dt: Optional[datetime] = None) -> datetime:
        """
        Get next market open time
        
        Args:
            dt: Start datetime (None = now)
            
        Returns:
            Datetime of next market open
        """
        if dt is None:
            dt = datetime.now(self.timezone)
        elif hasattr(dt, 'tzinfo'):
            if dt.tzinfo is None:
                dt = self.timezone.localize(dt)
            else:
                dt = dt.astimezone(self.timezone)
        
        # Simple implementation: return next open time
        # TODO: Handle holidays, special sessions
        import datetime as dt_module
        
        target = dt
        while True:
            # Move to next day if past market close
            if target.time() >= self.hours['close']:
                target = target + dt_module.timedelta(days=1)
                target = target.replace(
                    hour=self.hours['open'].hour,
                    minute=self.hours['open'].minute,
                    second=0,
                    microsecond=0
                )
            
            # Skip weekends
            if target.weekday() >= 5:
                target = target + dt_module.timedelta(days=1)
                continue
            
            # Found next open
            return target.replace(
                hour=self.hours['open'].hour,
                minute=self.hours['open'].minute,
                second=0,
                microsecond=0
            )
    
    def can_trade_symbol(self, symbol: str) -> tuple[bool, str]:
        """
        Check if a symbol can be traded right now
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'CBA.AX', 'BP.L')
            
        Returns:
            Tuple of (can_trade: bool, reason: str)
        """
        # Determine exchange from symbol suffix
        if symbol.endswith('.AX'):
            exchange = Exchange.ASX
        elif symbol.endswith('.L'):
            exchange = Exchange.LSE
        else:
            # Default to NYSE/NASDAQ for US symbols
            exchange = Exchange.NYSE
        
        # Create calendar for this exchange
        calendar = MarketCalendar(exchange)
        
        # Check if market is open
        if calendar.is_market_open():
            return (True, "Market open")
        
        # Get status to provide better reason
        info = calendar.get_market_status()
        
        if info.status == MarketStatus.CLOSED:
            if not calendar.is_trading_day():
                return (False, "Weekend/Holiday")
            else:
                return (False, "Market closed")
        elif info.status == MarketStatus.PRE_MARKET:
            return (False, "Pre-market hours")
        elif info.status == MarketStatus.AFTER_HOURS:
            return (False, "After-hours")
        elif info.status == MarketStatus.HOLIDAY:
            return (False, "Holiday")
        else:
            return (False, "Unknown status")
'''

def main():
    print("=" * 80)
    print("EMERGENCY FIX: Replacing market_calendar.py")
    print("=" * 80)
    
    # Find the file
    target_file = Path("ml_pipeline/market_calendar.py")
    
    if not target_file.exists():
        print(f"ERROR: Cannot find {target_file}")
        print("Are you in the correct directory?")
        print("Should be: C:\\Users\\david\\Regime_trading\\complete_backend_clean_install_v1.3.15\\")
        input("Press Enter to exit...")
        return
    
    # Backup old file
    backup_file = target_file.with_suffix(".py.OLD")
    print(f"Backing up old file to: {backup_file}")
    shutil.copy(target_file, backup_file)
    
    # Write new file
    print(f"Writing corrected file to: {target_file}")
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(CORRECT_MARKET_CALENDAR)
    
    print("✅ File replaced successfully!")
    print()
    print("Now test it:")
    print('python -c "from ml_pipeline.market_calendar import MarketCalendar, Exchange; mc = MarketCalendar(); info = mc.get_market_status(Exchange.ASX); print(f\'Status: {info.status}\'); print(\'SUCCESS!\')"')
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
