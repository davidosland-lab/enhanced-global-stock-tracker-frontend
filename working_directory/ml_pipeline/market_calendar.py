"""
Market Calendar and Trading Hours System
Tracks trading hours and holidays for ASX, NYSE, and LSE
Includes complete holiday calendars for 2024-2026
Author: Phase 3 Trading System
Date: January 1, 2026
"""

import logging
from datetime import datetime, time, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import pytz

# Setup logging
logger = logging.getLogger(__name__)

class MarketStatus(Enum):
    """Market status enum"""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PRE_MARKET = "PRE_MARKET"
    POST_MARKET = "POST_MARKET"
    HOLIDAY = "HOLIDAY"
    WEEKEND = "WEEKEND"

class Exchange(Enum):
    """Stock exchange enum"""
    ASX = "ASX"
    NYSE = "NYSE"
    LSE = "LSE"

@dataclass
class TradingHours:
    """Trading hours for an exchange"""
    exchange: Exchange
    timezone: str
    market_open: time
    market_close: time
    pre_market_open: Optional[time] = None
    post_market_close: Optional[time] = None

@dataclass
class MarketInfo:
    """Current market information"""
    exchange: Exchange
    status: MarketStatus
    current_time: datetime
    market_open_time: Optional[datetime] = None
    market_close_time: Optional[datetime] = None
    time_to_open: Optional[timedelta] = None
    time_to_close: Optional[timedelta] = None
    holiday_name: Optional[str] = None
    is_trading_day: bool = False

class MarketCalendar:
    """
    Market Calendar System
    Tracks trading hours and holidays for ASX, NYSE, and LSE
    """
    
    # Trading hours for each exchange
    TRADING_HOURS = {
        Exchange.ASX: TradingHours(
            exchange=Exchange.ASX,
            timezone="Australia/Sydney",
            market_open=time(10, 0),  # 10:00 AM AEDT
            market_close=time(16, 0),  # 4:00 PM AEDT
            pre_market_open=time(7, 0),  # 7:00 AM AEDT
            post_market_close=time(17, 0)  # 5:00 PM AEDT
        ),
        Exchange.NYSE: TradingHours(
            exchange=Exchange.NYSE,
            timezone="America/New_York",
            market_open=time(9, 30),  # 9:30 AM EST
            market_close=time(16, 0),  # 4:00 PM EST
            pre_market_open=time(4, 0),  # 4:00 AM EST
            post_market_close=time(20, 0)  # 8:00 PM EST
        ),
        Exchange.LSE: TradingHours(
            exchange=Exchange.LSE,
            timezone="Europe/London",
            market_open=time(8, 0),  # 8:00 AM GMT
            market_close=time(16, 30),  # 4:30 PM GMT
            pre_market_open=time(7, 50),  # 7:50 AM GMT (auction)
            post_market_close=time(17, 30)  # 5:30 PM GMT
        )
    }
    
    # 2024-2026 Holidays
    HOLIDAYS_2024_2026 = {
        Exchange.ASX: [
            # 2024
            ("2024-01-01", "New Year's Day"),
            ("2024-01-26", "Australia Day"),
            ("2024-03-29", "Good Friday"),
            ("2024-04-01", "Easter Monday"),
            ("2024-04-25", "ANZAC Day"),
            ("2024-06-10", "Queen's Birthday"),
            ("2024-12-25", "Christmas Day"),
            ("2024-12-26", "Boxing Day"),
            # 2025
            ("2025-01-01", "New Year's Day"),
            ("2025-01-27", "Australia Day (Observed)"),
            ("2025-04-18", "Good Friday"),
            ("2025-04-21", "Easter Monday"),
            ("2025-04-25", "ANZAC Day"),
            ("2025-06-09", "Queen's Birthday"),
            ("2025-12-25", "Christmas Day"),
            ("2025-12-26", "Boxing Day"),
            # 2026
            ("2026-01-01", "New Year's Day"),
            ("2026-01-26", "Australia Day"),
            ("2026-04-03", "Good Friday"),
            ("2026-04-06", "Easter Monday"),
            ("2026-04-27", "ANZAC Day (Observed)"),
            ("2026-06-08", "Queen's Birthday"),
            ("2026-12-25", "Christmas Day"),
            ("2026-12-28", "Boxing Day (Observed)"),
        ],
        Exchange.NYSE: [
            # 2024
            ("2024-01-01", "New Year's Day"),
            ("2024-01-15", "Martin Luther King Jr. Day"),
            ("2024-02-19", "Presidents Day"),
            ("2024-03-29", "Good Friday"),
            ("2024-05-27", "Memorial Day"),
            ("2024-06-19", "Juneteenth"),
            ("2024-07-04", "Independence Day"),
            ("2024-09-02", "Labor Day"),
            ("2024-11-28", "Thanksgiving Day"),
            ("2024-12-25", "Christmas Day"),
            # 2025
            ("2025-01-01", "New Year's Day"),
            ("2025-01-20", "Martin Luther King Jr. Day"),
            ("2025-02-17", "Presidents Day"),
            ("2025-04-18", "Good Friday"),
            ("2025-05-26", "Memorial Day"),
            ("2025-06-19", "Juneteenth"),
            ("2025-07-04", "Independence Day"),
            ("2025-09-01", "Labor Day"),
            ("2025-11-27", "Thanksgiving Day"),
            ("2025-12-25", "Christmas Day"),
            # 2026
            ("2026-01-01", "New Year's Day"),
            ("2026-01-19", "Martin Luther King Jr. Day"),
            ("2026-02-16", "Presidents Day"),
            ("2026-04-03", "Good Friday"),
            ("2026-05-25", "Memorial Day"),
            ("2026-06-19", "Juneteenth"),
            ("2026-07-03", "Independence Day (Observed)"),
            ("2026-09-07", "Labor Day"),
            ("2026-11-26", "Thanksgiving Day"),
            ("2026-12-25", "Christmas Day"),
        ],
        Exchange.LSE: [
            # 2024
            ("2024-01-01", "New Year's Day"),
            ("2024-03-29", "Good Friday"),
            ("2024-04-01", "Easter Monday"),
            ("2024-05-06", "Early May Bank Holiday"),
            ("2024-05-27", "Spring Bank Holiday"),
            ("2024-08-26", "Summer Bank Holiday"),
            ("2024-12-25", "Christmas Day"),
            ("2024-12-26", "Boxing Day"),
            # 2025
            ("2025-01-01", "New Year's Day"),
            ("2025-04-18", "Good Friday"),
            ("2025-04-21", "Easter Monday"),
            ("2025-05-05", "Early May Bank Holiday"),
            ("2025-05-26", "Spring Bank Holiday"),
            ("2025-08-25", "Summer Bank Holiday"),
            ("2025-12-25", "Christmas Day"),
            ("2025-12-26", "Boxing Day"),
            # 2026
            ("2026-01-01", "New Year's Day"),
            ("2026-04-03", "Good Friday"),
            ("2026-04-06", "Easter Monday"),
            ("2026-05-04", "Early May Bank Holiday"),
            ("2026-05-25", "Spring Bank Holiday"),
            ("2026-08-31", "Summer Bank Holiday"),
            ("2026-12-25", "Christmas Day"),
            ("2026-12-28", "Boxing Day (Observed)"),
        ]
    }
    
    def __init__(self):
        """Initialize market calendar"""
        self.holidays = self._load_holidays()
        logger.info("[CALENDAR] Market Calendar initialized")
    
    def _load_holidays(self) -> Dict[Exchange, Dict[str, str]]:
        """Load holidays into a dictionary for quick lookup"""
        holidays = {}
        for exchange, holiday_list in self.HOLIDAYS_2024_2026.items():
            holidays[exchange] = {date: name for date, name in holiday_list}
        return holidays
    
    def get_current_time(self, exchange: Exchange) -> datetime:
        """Get current time in exchange timezone"""
        tz = pytz.timezone(self.TRADING_HOURS[exchange].timezone)
        return datetime.now(tz)
    
    def is_weekend(self, dt: datetime) -> bool:
        """Check if date is weekend"""
        return dt.weekday() >= 5  # Saturday = 5, Sunday = 6
    
    def is_holiday(self, exchange: Exchange, dt: datetime) -> Tuple[bool, Optional[str]]:
        """
        Check if date is a holiday
        Returns: (is_holiday, holiday_name)
        """
        date_str = dt.strftime("%Y-%m-%d")
        holiday_name = self.holidays.get(exchange, {}).get(date_str)
        return (holiday_name is not None, holiday_name)
    
    def is_trading_day(self, exchange: Exchange, dt: Optional[datetime] = None) -> bool:
        """Check if it's a trading day (not weekend or holiday)"""
        if dt is None:
            dt = self.get_current_time(exchange)
        
        # Check weekend
        if self.is_weekend(dt):
            return False
        
        # Check holiday
        is_hol, _ = self.is_holiday(exchange, dt)
        return not is_hol
    
    def get_market_status(self, exchange: Exchange, dt: Optional[datetime] = None) -> MarketInfo:
        """
        Get current market status for an exchange
        Returns detailed MarketInfo object
        """
        if dt is None:
            dt = self.get_current_time(exchange)
        
        hours = self.TRADING_HOURS[exchange]
        
        # Check if it's a trading day
        if not self.is_trading_day(exchange, dt):
            is_hol, holiday_name = self.is_holiday(exchange, dt)
            if is_hol:
                status = MarketStatus.HOLIDAY
            else:
                status = MarketStatus.WEEKEND
            
            # Find next trading day
            next_open = self._find_next_market_open(exchange, dt)
            time_to_open = next_open - dt if next_open else None
            
            return MarketInfo(
                exchange=exchange,
                status=status,
                current_time=dt,
                market_open_time=next_open,
                time_to_open=time_to_open,
                holiday_name=holiday_name,
                is_trading_day=False
            )
        
        # It's a trading day - check market hours
        current_time = dt.time()
        
        # Create datetime objects for today's market times
        market_open_dt = dt.replace(hour=hours.market_open.hour, 
                                     minute=hours.market_open.minute,
                                     second=0, microsecond=0)
        market_close_dt = dt.replace(hour=hours.market_close.hour,
                                      minute=hours.market_close.minute,
                                      second=0, microsecond=0)
        
        # Determine status
        if current_time < hours.market_open:
            if hours.pre_market_open and current_time >= hours.pre_market_open:
                status = MarketStatus.PRE_MARKET
            else:
                status = MarketStatus.CLOSED
            time_to_open = market_open_dt - dt
            time_to_close = None
        elif current_time >= hours.market_close:
            if hours.post_market_close and current_time < hours.post_market_close:
                status = MarketStatus.POST_MARKET
            else:
                status = MarketStatus.CLOSED
            # Find next trading day open
            next_open = self._find_next_market_open(exchange, dt)
            time_to_open = next_open - dt if next_open else None
            time_to_close = None
        else:
            status = MarketStatus.OPEN
            time_to_open = None
            time_to_close = market_close_dt - dt
        
        return MarketInfo(
            exchange=exchange,
            status=status,
            current_time=dt,
            market_open_time=market_open_dt,
            market_close_time=market_close_dt,
            time_to_open=time_to_open,
            time_to_close=time_to_close,
            is_trading_day=True
        )
    
    def _find_next_market_open(self, exchange: Exchange, from_dt: datetime) -> Optional[datetime]:
        """Find next market open time"""
        hours = self.TRADING_HOURS[exchange]
        tz = pytz.timezone(hours.timezone)
        
        # Start from next day
        check_date = from_dt + timedelta(days=1)
        
        # Check up to 14 days ahead
        for _ in range(14):
            if self.is_trading_day(exchange, check_date):
                # Found next trading day
                next_open = check_date.replace(
                    hour=hours.market_open.hour,
                    minute=hours.market_open.minute,
                    second=0,
                    microsecond=0
                )
                return next_open
            check_date += timedelta(days=1)
        
        return None
    
    def get_all_market_status(self) -> Dict[Exchange, MarketInfo]:
        """Get status for all exchanges"""
        return {
            exchange: self.get_market_status(exchange)
            for exchange in Exchange
        }
    
    def can_trade_symbol(self, symbol: str) -> Tuple[bool, str]:
        """
        Check if a symbol can be traded right now
        Returns: (can_trade, reason)
        """
        # Determine exchange from symbol
        exchange = self._get_exchange_from_symbol(symbol)
        
        if exchange is None:
            return (False, f"Unknown exchange for symbol {symbol}")
        
        # Get market status
        info = self.get_market_status(exchange)
        
        # Can trade if market is open
        if info.status == MarketStatus.OPEN:
            return (True, f"{exchange.value} market is OPEN")
        
        # Build reason message
        if info.status == MarketStatus.HOLIDAY:
            reason = f"{exchange.value} closed - {info.holiday_name}"
        elif info.status == MarketStatus.WEEKEND:
            reason = f"{exchange.value} closed - Weekend"
        elif info.status == MarketStatus.PRE_MARKET:
            hours = int(info.time_to_open.total_seconds() // 3600)
            minutes = int((info.time_to_open.total_seconds() % 3600) // 60)
            reason = f"{exchange.value} in pre-market - Opens in {hours}h {minutes}m"
        elif info.status == MarketStatus.POST_MARKET:
            if info.time_to_open:
                hours = int(info.time_to_open.total_seconds() // 3600)
                reason = f"{exchange.value} in post-market - Opens in {hours}h"
            else:
                reason = f"{exchange.value} in post-market - Check next day"
        else:  # CLOSED
            if info.time_to_open:
                hours = int(info.time_to_open.total_seconds() // 3600)
                minutes = int((info.time_to_open.total_seconds() % 3600) // 60)
                if hours >= 24:
                    days = hours // 24
                    reason = f"{exchange.value} closed - Opens in {days} day(s)"
                else:
                    reason = f"{exchange.value} closed - Opens in {hours}h {minutes}m"
            else:
                reason = f"{exchange.value} closed"
        
        return (False, reason)
    
    def _get_exchange_from_symbol(self, symbol: str) -> Optional[Exchange]:
        """Determine exchange from symbol suffix"""
        symbol_upper = symbol.upper()
        
        if symbol_upper.endswith(".AX"):
            return Exchange.ASX
        elif symbol_upper.endswith(".L"):
            return Exchange.LSE
        elif any(symbol_upper.endswith(suffix) for suffix in [".DE", ".PA", ".AS"]):
            # European exchanges - use LSE timezone for now
            return Exchange.LSE
        else:
            # Assume US stock (NYSE/NASDAQ)
            return Exchange.NYSE
    
    def format_market_status(self, info: MarketInfo) -> str:
        """Format market status as a readable string"""
        lines = []
        lines.append(f"{info.exchange.value} Market Status:")
        lines.append(f"  Status: {info.status.value}")
        lines.append(f"  Local Time: {info.current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        if info.holiday_name:
            lines.append(f"  Holiday: {info.holiday_name}")
        
        if info.status == MarketStatus.OPEN:
            if info.time_to_close:
                hours = int(info.time_to_close.total_seconds() // 3600)
                minutes = int((info.time_to_close.total_seconds() % 3600) // 60)
                lines.append(f"  Time to Close: {hours}h {minutes}m")
        elif info.time_to_open:
            hours = int(info.time_to_open.total_seconds() // 3600)
            minutes = int((info.time_to_open.total_seconds() % 3600) // 60)
            if hours >= 24:
                days = hours // 24
                hours = hours % 24
                lines.append(f"  Time to Open: {days} day(s) {hours}h {minutes}m")
            else:
                lines.append(f"  Time to Open: {hours}h {minutes}m")
        
        if info.market_open_time:
            lines.append(f"  Next Open: {info.market_open_time.strftime('%Y-%m-%d %H:%M %Z')}")
        
        return "\n".join(lines)
    
    def get_upcoming_holidays(self, exchange: Exchange, days_ahead: int = 30) -> List[Tuple[str, str]]:
        """Get upcoming holidays for an exchange"""
        current_time = self.get_current_time(exchange)
        end_date = current_time + timedelta(days=days_ahead)
        
        upcoming = []
        for date_str, holiday_name in self.HOLIDAYS_2024_2026[exchange]:
            holiday_date = datetime.strptime(date_str, "%Y-%m-%d")
            holiday_date = holiday_date.replace(tzinfo=current_time.tzinfo)
            
            if current_time.date() <= holiday_date.date() <= end_date.date():
                upcoming.append((date_str, holiday_name))
        
        return sorted(upcoming)


def test_market_calendar():
    """Test market calendar functionality"""
    calendar = MarketCalendar()
    
    print("\n" + "="*60)
    print("MARKET CALENDAR TEST")
    print("="*60)
    
    # Test all exchanges
    for exchange in Exchange:
        print(f"\n{exchange.value} Status:")
        info = calendar.get_market_status(exchange)
        print(calendar.format_market_status(info))
        
        # Show upcoming holidays
        holidays = calendar.get_upcoming_holidays(exchange, days_ahead=60)
        if holidays:
            print(f"\n  Upcoming Holidays ({len(holidays)}):")
            for date, name in holidays[:5]:  # Show next 5
                print(f"    {date}: {name}")
    
    # Test symbol trading
    print("\n" + "="*60)
    print("SYMBOL TRADING STATUS")
    print("="*60)
    
    test_symbols = ["CBA.AX", "AAPL", "HSBA.L", "BHP.AX", "MSFT", "BP.L"]
    for symbol in test_symbols:
        can_trade, reason = calendar.can_trade_symbol(symbol)
        status = "[OK] CAN TRADE" if can_trade else "[WARN] CANNOT TRADE"
        print(f"{status}: {symbol} - {reason}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_market_calendar()
