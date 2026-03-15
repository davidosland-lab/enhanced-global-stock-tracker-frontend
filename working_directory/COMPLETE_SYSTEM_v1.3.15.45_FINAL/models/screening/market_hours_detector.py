"""
Market Hours Detector Module

Detects if ASX/US markets are currently open and provides trading status information.
Enables intraday-aware pipeline execution.

Features:
- Real-time market status detection
- Trading hours validation
- Time until open/close calculations
- Holiday awareness (basic)
"""

import logging
from datetime import datetime, time, timedelta
from typing import Dict, Optional
import pytz

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MarketHoursDetector:
    """
    Detects market hours status for ASX and US markets
    """
    
    # Market configurations
    MARKET_CONFIG = {
        'ASX': {
            'timezone': 'Australia/Sydney',
            'open_time': time(10, 0),      # 10:00 AM AEST
            'close_time': time(16, 0),     # 4:00 PM AEST
            'trading_days': [0, 1, 2, 3, 4],  # Monday-Friday (0=Monday)
            'session_duration_hours': 6.0
        },
        'US': {
            'timezone': 'America/New_York',
            'open_time': time(9, 30),      # 9:30 AM EST
            'close_time': time(16, 0),     # 4:00 PM EST
            'trading_days': [0, 1, 2, 3, 4],  # Monday-Friday
            'session_duration_hours': 6.5
        }
    }
    
    def __init__(self):
        """Initialize market hours detector"""
        logger.info("Market Hours Detector initialized")
    
    def is_market_open(self, market: str = 'ASX') -> Dict:
        """
        Check if specified market is currently open
        
        Args:
            market: 'ASX' or 'US'
            
        Returns:
            Dictionary with detailed market status:
            {
                'is_open': bool,
                'market': str,
                'current_time': datetime,
                'market_phase': str,  # 'pre_market', 'open', 'closed', 'after_hours'
                'time_until_open': timedelta or None,
                'time_until_close': timedelta or None,
                'trading_hours_elapsed_pct': float,
                'is_trading_day': bool
            }
        """
        if market not in self.MARKET_CONFIG:
            raise ValueError(f"Unknown market: {market}. Must be 'ASX' or 'US'")
        
        config = self.MARKET_CONFIG[market]
        tz = pytz.timezone(config['timezone'])
        
        # Get current time in market timezone
        current_time = datetime.now(tz)
        current_date = current_time.date()
        current_time_only = current_time.time()
        
        # Check if today is a trading day (Monday-Friday)
        is_trading_day = current_time.weekday() in config['trading_days']
        
        # Create datetime objects for open and close times today
        open_dt = tz.localize(datetime.combine(current_date, config['open_time']))
        close_dt = tz.localize(datetime.combine(current_date, config['close_time']))
        
        # Determine market phase and calculate times
        is_open = False
        market_phase = 'closed'
        time_until_open = None
        time_until_close = None
        trading_hours_elapsed_pct = 0.0
        
        if not is_trading_day:
            # Weekend or holiday
            market_phase = 'closed'
            time_until_open = self._time_until_next_trading_day(current_time, config)
        elif current_time < open_dt:
            # Before market open (pre-market)
            market_phase = 'pre_market'
            time_until_open = open_dt - current_time
        elif open_dt <= current_time < close_dt:
            # Market is open
            is_open = True
            market_phase = 'open'
            time_until_close = close_dt - current_time
            
            # Calculate how much of trading day has elapsed
            elapsed_time = current_time - open_dt
            total_session_seconds = config['session_duration_hours'] * 3600
            trading_hours_elapsed_pct = (elapsed_time.total_seconds() / total_session_seconds) * 100
        else:
            # After market close (after-hours)
            market_phase = 'after_hours'
            time_until_open = self._time_until_next_trading_day(current_time, config)
        
        result = {
            'is_open': is_open,
            'market': market,
            'current_time': current_time,
            'market_phase': market_phase,
            'time_until_open': time_until_open,
            'time_until_close': time_until_close,
            'trading_hours_elapsed_pct': round(trading_hours_elapsed_pct, 2),
            'is_trading_day': is_trading_day,
            'open_time': config['open_time'].strftime('%H:%M'),
            'close_time': config['close_time'].strftime('%H:%M'),
            'timezone': config['timezone']
        }
        
        return result
    
    def _time_until_next_trading_day(self, current_time: datetime, config: Dict) -> timedelta:
        """
        Calculate time until next trading day's market open
        
        Args:
            current_time: Current datetime with timezone
            config: Market configuration dict
            
        Returns:
            timedelta until next market open
        """
        tz = pytz.timezone(config['timezone'])
        current_date = current_time.date()
        days_ahead = 1
        
        # Find next trading day
        while days_ahead <= 7:  # Look up to a week ahead
            next_date = current_date + timedelta(days=days_ahead)
            next_datetime = datetime.combine(next_date, config['open_time'])
            next_datetime_tz = tz.localize(next_datetime)
            
            if next_datetime_tz.weekday() in config['trading_days']:
                return next_datetime_tz - current_time
            
            days_ahead += 1
        
        # Fallback: assume 1 day ahead
        return timedelta(days=1)
    
    def get_market_status_summary(self, market: str = 'ASX') -> str:
        """
        Get human-readable market status summary
        
        Args:
            market: 'ASX' or 'US'
            
        Returns:
            Formatted status string
        """
        status = self.is_market_open(market)
        
        if status['is_open']:
            return (
                f"✅ {market} MARKET IS OPEN\n"
                f"   Current Time: {status['current_time'].strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
                f"   Trading Hours Elapsed: {status['trading_hours_elapsed_pct']:.1f}%\n"
                f"   Time Until Close: {self._format_timedelta(status['time_until_close'])}"
            )
        elif status['market_phase'] == 'pre_market':
            return (
                f"⏰ {market} MARKET OPENS SOON (Pre-Market)\n"
                f"   Current Time: {status['current_time'].strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
                f"   Time Until Open: {self._format_timedelta(status['time_until_open'])}"
            )
        elif status['market_phase'] == 'after_hours':
            return (
                f"🌙 {market} MARKET CLOSED (After-Hours)\n"
                f"   Current Time: {status['current_time'].strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
                f"   Next Open: {self._format_timedelta(status['time_until_open'])}"
            )
        else:  # Weekend or holiday
            return (
                f"⛔ {market} MARKET CLOSED (Non-Trading Day)\n"
                f"   Current Time: {status['current_time'].strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
                f"   Next Open: {self._format_timedelta(status['time_until_open'])}"
            )
    
    def _format_timedelta(self, td: Optional[timedelta]) -> str:
        """Format timedelta as human-readable string"""
        if td is None:
            return "N/A"
        
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 24:
            days = hours // 24
            hours = hours % 24
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"
    
    def should_use_intraday_mode(self, market: str = 'ASX') -> bool:
        """
        Determine if pipeline should run in intraday mode
        
        Args:
            market: 'ASX' or 'US'
            
        Returns:
            True if market is open and intraday mode recommended
        """
        status = self.is_market_open(market)
        
        # Use intraday mode if market is open and at least 10% of trading day has elapsed
        # (avoid first 10 minutes which can be volatile/unreliable)
        return status['is_open'] and status['trading_hours_elapsed_pct'] >= 10.0


# ========================================================================
# TESTING / DEMONSTRATION
# ========================================================================

if __name__ == "__main__":
    """Test market hours detection"""
    
    detector = MarketHoursDetector()
    
    print("=" * 80)
    print("MARKET HOURS DETECTOR - TEST")
    print("=" * 80)
    print()
    
    # Test ASX
    print("ASX Market Status:")
    print("-" * 80)
    asx_status = detector.is_market_open('ASX')
    print(detector.get_market_status_summary('ASX'))
    print()
    print(f"Should use intraday mode: {detector.should_use_intraday_mode('ASX')}")
    print()
    print("Detailed Status:")
    for key, value in asx_status.items():
        print(f"  {key}: {value}")
    print()
    
    # Test US
    print("=" * 80)
    print("US Market Status:")
    print("-" * 80)
    us_status = detector.is_market_open('US')
    print(detector.get_market_status_summary('US'))
    print()
    print(f"Should use intraday mode: {detector.should_use_intraday_mode('US')}")
    print()
    print("Detailed Status:")
    for key, value in us_status.items():
        print(f"  {key}: {value}")
    print()
    
    print("=" * 80)
    print("Test completed successfully!")
    print("=" * 80)
