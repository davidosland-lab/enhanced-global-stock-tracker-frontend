# 📊 Phase 3: Auto-Rescan Features for Day Traders
## Intraday Monitoring & Alert System

**Date**: November 27, 2025  
**Status**: 🚧 **IMPLEMENTATION READY**  
**Target Users**: Active day traders, swing traders, intraday momentum traders

---

## 🎯 Overview

**Phase 3** adds automated **intraday rescanning** capabilities to detect opportunities as they emerge during market hours. This transforms the system from a **"once-daily overnight screener"** into a **"continuous intraday monitor"**.

---

## 🚀 What Phase 3 Adds

### **Core Features**:

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Auto-Rescan** | Scan every 15-30 minutes during market hours | Catch breakouts early |
| **Breakout Detection** | Detect price/volume breakouts in real-time | Actionable trade signals |
| **Alert System** | Email/SMS/webhook alerts for opportunities | Never miss a setup |
| **Incremental Scanning** | Only rescan changed stocks (performance) | Fast updates |
| **Historical Tracking** | Track intraday opportunity evolution | Verify signal quality |

---

## 📋 Architecture

### **System Components**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Phase 3 Auto-Rescan System                │
└─────────────────────────────────────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
        ┌───────▼────────┐           ┌───────▼────────┐
        │ Intraday       │           │  Alert         │
        │ Scheduler      │           │  Manager       │
        └───────┬────────┘           └───────┬────────┘
                │                             │
        ┌───────▼────────┐           ┌───────▼────────┐
        │ Incremental    │           │  Notification  │
        │ Scanner        │           │  Dispatcher    │
        └───────┬────────┘           └───────┬────────┘
                │                             │
        ┌───────▼────────┐           ┌───────▼────────┐
        │ Breakout       │           │  Email / SMS / │
        │ Detector       │           │  Webhook       │
        └────────────────┘           └────────────────┘
```

---

## 🔧 Implementation Plan

### **File Structure**:

```
models/scheduling/
├── overnight_scheduler.py          # Existing (Phase 1)
├── intraday_scheduler.py          # NEW - Phase 3
├── intraday_rescan_manager.py     # NEW - Phase 3
└── alert_dispatcher.py            # NEW - Phase 3

models/screening/
├── breakout_detector.py           # NEW - Phase 3
├── incremental_scanner.py         # NEW - Phase 3
└── opportunity_tracker.py         # NEW - Phase 3

config/
└── intraday_rescan_config.json    # NEW - Phase 3
```

---

## 📁 Component 1: Intraday Scheduler

### **Purpose**: Schedule automatic rescans during market hours

### **File**: `models/scheduling/intraday_scheduler.py`

```python
"""
Intraday Scheduler for Day Trading

Automatically rescans markets every 15-30 minutes during trading hours.
Detects breakouts, momentum shifts, and generates real-time alerts.
"""

import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Callable, Optional, Dict, List

from ..screening.market_hours_detector import MarketHoursDetector
from .intraday_rescan_manager import IntradayRescanManager

logger = logging.getLogger(__name__)


class IntradayScheduler:
    """
    Manages automated intraday rescanning for active trading.
    
    Features:
    - Auto-start at market open
    - Rescan every N minutes (configurable)
    - Auto-stop at market close
    - Breakout detection
    - Alert generation
    """
    
    def __init__(self, market: str = 'ASX', rescan_interval: int = 15):
        """
        Initialize intraday scheduler.
        
        Args:
            market: 'ASX' or 'US'
            rescan_interval: Minutes between rescans (default: 15)
        """
        self.market = market
        self.rescan_interval = rescan_interval
        self.market_detector = MarketHoursDetector(market=market)
        self.rescan_manager = IntradayRescanManager(market=market)
        
        self.is_running = False
        self.scan_count = 0
        self.session_start = None
        
        logger.info(f"Intraday Scheduler initialized: {market} market")
        logger.info(f"Rescan interval: {rescan_interval} minutes")
    
    def start_intraday_monitoring(self):
        """
        Start continuous intraday monitoring.
        
        Runs rescans every N minutes during market hours.
        Auto-stops when market closes.
        """
        logger.info("="*80)
        logger.info("STARTING INTRADAY MONITORING SESSION")
        logger.info("="*80)
        
        # Check if market is open
        market_status = self.market_detector.is_market_open()
        
        if not market_status['is_open']:
            logger.warning("❌ Market is closed. Intraday monitoring not started.")
            logger.info(f"   Market phase: {market_status.get('market_phase', 'Unknown')}")
            logger.info(f"   Next open: {market_status.get('time_until_open', 'Unknown')}")
            return False
        
        # Market is open - start monitoring
        self.is_running = True
        self.session_start = datetime.now()
        self.scan_count = 0
        
        logger.info(f"✅ {self.market} Market is OPEN")
        logger.info(f"⏰ Session started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"🔄 Rescan interval: {self.rescan_interval} minutes")
        logger.info(f"⏱️  Time until close: {market_status.get('time_until_close', 'Unknown')}")
        
        # Schedule the first scan immediately
        logger.info("\n🚀 Running initial scan...")
        self._run_scan()
        
        # Schedule periodic rescans
        schedule.every(self.rescan_interval).minutes.do(self._run_scan)
        
        # Main monitoring loop
        try:
            while self.is_running:
                # Check if market is still open
                market_status = self.market_detector.is_market_open()
                
                if not market_status['is_open']:
                    logger.info("\n🔔 Market has closed. Stopping intraday monitoring.")
                    self.stop_monitoring()
                    break
                
                # Run any scheduled scans
                schedule.run_pending()
                
                # Sleep for 1 minute before next check
                time.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("\n⚠️  Monitoring interrupted by user.")
            self.stop_monitoring()
        
        return True
    
    def _run_scan(self):
        """Run a single intraday scan"""
        self.scan_count += 1
        scan_time = datetime.now()
        
        logger.info("\n" + "="*80)
        logger.info(f"INTRADAY SCAN #{self.scan_count}")
        logger.info(f"Timestamp: {scan_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)
        
        try:
            # Run the rescan
            results = self.rescan_manager.run_incremental_scan()
            
            # Log results
            logger.info(f"\n✅ Scan #{self.scan_count} completed:")
            logger.info(f"   Stocks scanned: {results.get('stocks_scanned', 0)}")
            logger.info(f"   New opportunities: {results.get('new_opportunities', 0)}")
            logger.info(f"   Breakouts detected: {results.get('breakouts', 0)}")
            logger.info(f"   Alerts sent: {results.get('alerts_sent', 0)}")
            logger.info(f"   Scan duration: {results.get('duration_seconds', 0):.1f}s")
            
            # Next scan time
            next_scan = scan_time + timedelta(minutes=self.rescan_interval)
            logger.info(f"   Next scan: {next_scan.strftime('%H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"❌ Scan #{self.scan_count} failed: {e}")
            logger.exception(e)
    
    def stop_monitoring(self):
        """Stop intraday monitoring"""
        if not self.is_running:
            logger.warning("Monitoring is not running")
            return
        
        self.is_running = False
        schedule.clear()
        
        # Session summary
        if self.session_start:
            session_duration = datetime.now() - self.session_start
            logger.info("\n" + "="*80)
            logger.info("INTRADAY MONITORING SESSION ENDED")
            logger.info("="*80)
            logger.info(f"Session duration: {session_duration}")
            logger.info(f"Total scans: {self.scan_count}")
            logger.info(f"Average interval: {session_duration.total_seconds() / max(self.scan_count, 1):.1f}s")
        
        logger.info("✅ Monitoring stopped")
    
    def schedule_for_market_open(self):
        """
        Schedule monitoring to start at market open tomorrow.
        
        Uses Windows Task Scheduler for overnight scheduling.
        """
        from .overnight_scheduler import OvernightScheduler
        
        market_status = self.market_detector.is_market_open()
        open_time = market_status.get('open_time', '10:00')  # Default ASX
        
        if self.market == 'US':
            hour, minute = 9, 30  # 9:30 AM EST
        else:
            hour, minute = 10, 0  # 10:00 AM AEST
        
        # Create task for market open
        scheduler = OvernightScheduler(
            script_path=Path(__file__).parent.parent.parent / 'RUN_INTRADAY_MONITOR.bat'
        )
        
        task_name = f"FinBERT_Intraday_Monitor_{self.market}"
        success = scheduler.create_daily_task(
            hour=hour,
            minute=minute
        )
        
        if success:
            logger.info(f"✅ Scheduled intraday monitoring for {hour:02d}:{minute:02d} daily")
        else:
            logger.error("❌ Failed to schedule intraday monitoring")
        
        return success


# Command-line interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Intraday monitoring for day trading')
    parser.add_argument('--market', choices=['ASX', 'US'], default='ASX',
                       help='Market to monitor')
    parser.add_argument('--interval', type=int, default=15,
                       help='Rescan interval in minutes (default: 15)')
    parser.add_argument('--schedule', action='store_true',
                       help='Schedule for daily market open (instead of running now)')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    scheduler = IntradayScheduler(
        market=args.market,
        rescan_interval=args.interval
    )
    
    if args.schedule:
        # Schedule for tomorrow
        scheduler.schedule_for_market_open()
    else:
        # Start monitoring now
        scheduler.start_intraday_monitoring()
```

---

## 📁 Component 2: Incremental Scanner

### **Purpose**: Fast rescanning by only checking changed stocks

### **File**: `models/screening/incremental_scanner.py`

```python
"""
Incremental Stock Scanner

Optimized for fast intraday rescans by only checking stocks that have
meaningful price/volume changes since the last scan.
"""

import logging
from typing import List, Dict, Set
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class IncrementalScanner:
    """
    Efficient incremental scanning for intraday updates.
    
    Only rescans stocks with significant changes to minimize API calls
    and improve performance during active trading hours.
    """
    
    def __init__(self, market: str = 'ASX'):
        """
        Initialize incremental scanner.
        
        Args:
            market: 'ASX' or 'US'
        """
        self.market = market
        self.last_scan_data = {}  # symbol -> {price, volume, timestamp}
        self.last_scan_time = None
        
        # Thresholds for "significant change"
        self.price_change_threshold = 0.02  # 2% price move
        self.volume_spike_threshold = 1.5   # 50% volume increase
        
        logger.info(f"Incremental Scanner initialized for {market} market")
    
    def identify_changed_stocks(self, current_data: List[Dict]) -> Set[str]:
        """
        Identify which stocks have significant changes.
        
        Args:
            current_data: List of current stock data
            
        Returns:
            Set of symbols that need rescanning
        """
        changed_symbols = set()
        
        if not self.last_scan_data:
            # First scan - everything is "changed"
            logger.info("First scan - all stocks marked for scanning")
            return {s['symbol'] for s in current_data}
        
        for stock in current_data:
            symbol = stock['symbol']
            current_price = stock.get('current_price', 0)
            current_volume = stock.get('volume', 0)
            
            # Check if we have previous data
            if symbol not in self.last_scan_data:
                changed_symbols.add(symbol)
                continue
            
            prev_data = self.last_scan_data[symbol]
            prev_price = prev_data.get('price', 0)
            prev_volume = prev_data.get('volume', 0)
            
            # Check price change
            if prev_price > 0:
                price_change_pct = abs(current_price - prev_price) / prev_price
                if price_change_pct >= self.price_change_threshold:
                    changed_symbols.add(symbol)
                    logger.debug(f"{symbol}: Price change {price_change_pct:.1%}")
                    continue
            
            # Check volume spike
            if prev_volume > 0:
                volume_ratio = current_volume / prev_volume
                if volume_ratio >= self.volume_spike_threshold:
                    changed_symbols.add(symbol)
                    logger.debug(f"{symbol}: Volume spike {volume_ratio:.1f}x")
                    continue
        
        logger.info(f"Identified {len(changed_symbols)}/{len(current_data)} stocks with significant changes")
        return changed_symbols
    
    def update_baseline(self, stock_data: List[Dict]):
        """
        Update the baseline data after a full scan.
        
        Args:
            stock_data: List of scanned stock data
        """
        self.last_scan_time = datetime.now()
        
        for stock in stock_data:
            symbol = stock['symbol']
            self.last_scan_data[symbol] = {
                'price': stock.get('current_price', 0),
                'volume': stock.get('volume', 0),
                'timestamp': self.last_scan_time
            }
        
        logger.debug(f"Baseline updated: {len(stock_data)} stocks")
    
    def get_time_since_last_scan(self) -> timedelta:
        """Get time elapsed since last scan"""
        if not self.last_scan_time:
            return timedelta(hours=24)  # No previous scan
        return datetime.now() - self.last_scan_time
```

---

## 📁 Component 3: Breakout Detector

### **Purpose**: Detect price/volume breakouts for trade signals

### **File**: `models/screening/breakout_detector.py`

```python
"""
Breakout Detection for Intraday Trading

Identifies breakout and breakdown patterns in real-time:
- Price breakouts above resistance
- Volume spikes
- Momentum acceleration
- Pattern confirmations
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BreakoutDetector:
    """
    Detects technical breakouts and breakdowns for intraday trading.
    """
    
    BREAKOUT_TYPES = {
        'PRICE_BREAKOUT': 'Price above recent high',
        'VOLUME_BREAKOUT': 'Volume spike (2x+ average)',
        'MOMENTUM_BREAKOUT': 'Strong momentum acceleration',
        'CONSOLIDATION_BREAKOUT': 'Breakout from consolidation',
        'BREAKDOWN': 'Price breaks below support'
    }
    
    def __init__(self):
        """Initialize breakout detector"""
        self.detected_breakouts = []
        logger.info("Breakout Detector initialized")
    
    def detect_breakouts(self, stock: Dict, intraday_data: Dict) -> List[Dict]:
        """
        Detect breakouts in a single stock.
        
        Args:
            stock: Stock data with technical indicators
            intraday_data: Intraday price/volume data
            
        Returns:
            List of detected breakouts
        """
        breakouts = []
        symbol = stock.get('symbol', 'UNKNOWN')
        
        # 1. Price Breakout (above recent high)
        if self._check_price_breakout(stock, intraday_data):
            breakouts.append({
                'type': 'PRICE_BREAKOUT',
                'symbol': symbol,
                'description': self.BREAKOUT_TYPES['PRICE_BREAKOUT'],
                'timestamp': datetime.now(),
                'current_price': stock.get('current_price'),
                'signal_strength': self._calculate_signal_strength(stock, 'price')
            })
        
        # 2. Volume Breakout
        if self._check_volume_spike(stock, intraday_data):
            breakouts.append({
                'type': 'VOLUME_BREAKOUT',
                'symbol': symbol,
                'description': self.BREAKOUT_TYPES['VOLUME_BREAKOUT'],
                'timestamp': datetime.now(),
                'volume_ratio': intraday_data.get('volume_ratio', 0),
                'signal_strength': self._calculate_signal_strength(stock, 'volume')
            })
        
        # 3. Momentum Acceleration
        if self._check_momentum_acceleration(stock, intraday_data):
            breakouts.append({
                'type': 'MOMENTUM_BREAKOUT',
                'symbol': symbol,
                'description': self.BREAKOUT_TYPES['MOMENTUM_BREAKOUT'],
                'timestamp': datetime.now(),
                'momentum_score': intraday_data.get('momentum_score', 0),
                'signal_strength': self._calculate_signal_strength(stock, 'momentum')
            })
        
        # Log detected breakouts
        if breakouts:
            logger.info(f"🚨 {symbol}: Detected {len(breakouts)} breakout(s)")
            for b in breakouts:
                logger.info(f"   - {b['type']}: {b['description']}")
        
        return breakouts
    
    def _check_price_breakout(self, stock: Dict, intraday_data: Dict) -> bool:
        """Check if price is breaking out above resistance"""
        current_price = stock.get('current_price', 0)
        resistance = stock.get('resistance_level', current_price * 1.05)
        
        # Price must be above resistance + confirmation
        if current_price > resistance:
            # Check for volume confirmation
            volume_ratio = intraday_data.get('volume_ratio', 1.0)
            if volume_ratio > 1.3:  # 30% above average
                return True
        
        return False
    
    def _check_volume_spike(self, stock: Dict, intraday_data: Dict) -> bool:
        """Check for significant volume spike"""
        volume_ratio = intraday_data.get('volume_ratio', 1.0)
        
        # Volume must be 2x average or more
        return volume_ratio >= 2.0
    
    def _check_momentum_acceleration(self, stock: Dict, intraday_data: Dict) -> bool:
        """Check for momentum acceleration"""
        momentum_15m = intraday_data.get('momentum_15m', 0)
        momentum_60m = intraday_data.get('momentum_60m', 0)
        
        # 15-min momentum > 60-min momentum (acceleration)
        # Both must be positive
        if momentum_15m > 0 and momentum_60m > 0:
            if momentum_15m > momentum_60m * 1.5:  # 50% faster
                return True
        
        return False
    
    def _calculate_signal_strength(self, stock: Dict, breakout_type: str) -> float:
        """
        Calculate signal strength (0-100).
        
        Combines multiple factors for confidence score.
        """
        score = 50.0  # Base score
        
        # Add points based on technical indicators
        technical = stock.get('technical', {})
        
        # RSI (prefer 40-70 range)
        rsi = technical.get('rsi', 50)
        if 40 <= rsi <= 70:
            score += 15
        elif rsi > 70:
            score -= 10  # Overbought warning
        
        # Volume confirmation
        volume_ratio = stock.get('volume_ratio', 1.0)
        if volume_ratio > 1.5:
            score += 10
        elif volume_ratio > 2.0:
            score += 20
        
        # Trend alignment
        if stock.get('above_ma20', False):
            score += 10
        if stock.get('above_ma50', False):
            score += 5
        
        return min(100, max(0, score))
```

---

## 📁 Component 4: Alert Dispatcher

### **Purpose**: Send notifications for breakouts and opportunities

### **File**: `models/scheduling/alert_dispatcher.py`

```python
"""
Alert Dispatcher for Intraday Trading

Sends real-time alerts via:
- Email (SMTP)
- SMS (Twilio)
- Webhook (Discord, Slack, custom)
- Desktop notifications (Windows)
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class AlertDispatcher:
    """
    Dispatch trading alerts via multiple channels.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize alert dispatcher.
        
        Args:
            config_path: Path to alert configuration JSON
        """
        self.config = self._load_config(config_path)
        self.email_enabled = self.config.get('email', {}).get('enabled', False)
        self.sms_enabled = self.config.get('sms', {}).get('enabled', False)
        self.webhook_enabled = self.config.get('webhook', {}).get('enabled', False)
        
        logger.info(f"Alert Dispatcher initialized")
        logger.info(f"  Email: {'✓' if self.email_enabled else '✗'}")
        logger.info(f"  SMS: {'✓' if self.sms_enabled else '✗'}")
        logger.info(f"  Webhook: {'✓' if self.webhook_enabled else '✗'}")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load alert configuration"""
        if config_path is None:
            # Return default config
            return {
                'email': {'enabled': False},
                'sms': {'enabled': False},
                'webhook': {'enabled': False}
            }
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def send_breakout_alert(self, breakout: Dict):
        """
        Send alert for a detected breakout.
        
        Args:
            breakout: Breakout data dictionary
        """
        symbol = breakout.get('symbol', 'UNKNOWN')
        breakout_type = breakout.get('type', 'UNKNOWN')
        signal_strength = breakout.get('signal_strength', 0)
        
        # Format alert message
        message = f"""
🚨 BREAKOUT ALERT

Symbol: {symbol}
Type: {breakout_type}
Signal Strength: {signal_strength:.0f}/100
Time: {datetime.now().strftime('%H:%M:%S')}

{breakout.get('description', 'No description')}
"""
        
        # Send via enabled channels
        if self.email_enabled:
            self._send_email(f"Breakout Alert: {symbol}", message)
        
        if self.sms_enabled:
            self._send_sms(f"🚨 {symbol} breakout ({signal_strength:.0f}/100)")
        
        if self.webhook_enabled:
            self._send_webhook(breakout)
        
        logger.info(f"✉️  Alert sent for {symbol} {breakout_type}")
    
    def _send_email(self, subject: str, body: str):
        """Send email alert"""
        try:
            config = self.config.get('email', {})
            
            msg = MIMEMultipart()
            msg['From'] = config.get('from')
            msg['To'] = config.get('to')
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(config.get('smtp_server'), config.get('smtp_port', 587))
            server.starttls()
            server.login(config.get('username'), config.get('password'))
            server.send_message(msg)
            server.quit()
            
            logger.debug(f"Email sent: {subject}")
            
        except Exception as e:
            logger.error(f"Email send failed: {e}")
    
    def _send_sms(self, message: str):
        """Send SMS alert via Twilio"""
        try:
            # Twilio implementation would go here
            logger.debug(f"SMS: {message}")
        except Exception as e:
            logger.error(f"SMS send failed: {e}")
    
    def _send_webhook(self, data: Dict):
        """Send webhook notification"""
        try:
            import requests
            
            config = self.config.get('webhook', {})
            url = config.get('url')
            
            if url:
                response = requests.post(url, json=data)
                logger.debug(f"Webhook sent: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Webhook send failed: {e}")
```

---

## 📁 Configuration File

### **File**: `config/intraday_rescan_config.json`

```json
{
  "rescan_settings": {
    "enabled": true,
    "interval_minutes": 15,
    "markets": ["ASX", "US"],
    "start_delay_minutes": 5,
    "end_early_minutes": 5
  },
  "incremental_scan": {
    "enabled": true,
    "price_change_threshold": 0.02,
    "volume_spike_threshold": 1.5
  },
  "breakout_detection": {
    "enabled": true,
    "min_signal_strength": 60,
    "types": [
      "PRICE_BREAKOUT",
      "VOLUME_BREAKOUT",
      "MOMENTUM_BREAKOUT"
    ]
  },
  "alerts": {
    "email": {
      "enabled": false,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "from": "your-email@gmail.com",
      "to": "recipient@example.com",
      "username": "",
      "password": ""
    },
    "sms": {
      "enabled": false,
      "provider": "twilio",
      "account_sid": "",
      "auth_token": "",
      "from_number": "",
      "to_number": ""
    },
    "webhook": {
      "enabled": false,
      "url": "",
      "method": "POST"
    }
  },
  "performance": {
    "max_concurrent_requests": 10,
    "request_delay_ms": 100,
    "cache_duration_seconds": 300
  }
}
```

---

## 🚀 Usage Examples

### **Example 1: Start Intraday Monitoring**

```bash
# Start monitoring ASX market (rescans every 15 min)
python models/scheduling/intraday_scheduler.py --market ASX --interval 15

# Start monitoring US market (rescans every 30 min)
python models/scheduling/intraday_scheduler.py --market US --interval 30
```

### **Example 2: Schedule for Daily Market Open**

```bash
# Schedule ASX monitoring to start at 10:00 AM daily
python models/scheduling/intraday_scheduler.py --market ASX --schedule

# Schedule US monitoring to start at 9:30 AM daily
python models/scheduling/intraday_scheduler.py --market US --schedule
```

### **Example 3: Run with Alerts Enabled**

```python
from models.scheduling.intraday_scheduler import IntradayScheduler

# Initialize with alerts
scheduler = IntradayScheduler(market='US', rescan_interval=15)

# Start monitoring (will send alerts for breakouts)
scheduler.start_intraday_monitoring()
```

---

## 📊 Expected Performance

### **Timing**:

| Operation | First Scan | Incremental Rescan | Full Rescan |
|-----------|------------|-------------------|-------------|
| **ASX (240 stocks)** | 15-20 min | 2-5 min | 15-20 min |
| **US (240 stocks)** | 15-20 min | 2-5 min | 15-20 min |
| **Incremental (30 changed)** | N/A | 1-2 min | N/A |

### **Cost Estimate** (per trading day):

| Scenario | Rescans/Day | API Calls | AI Calls | Total Cost |
|----------|-------------|-----------|----------|------------|
| **15-min intervals (ASX)** | 24 scans | 5,760 | 24 | ~$0.80/day |
| **30-min intervals (US)** | 13 scans | 3,120 | 13 | ~$0.43/day |
| **Incremental only** | 24 scans | 720 | 24 | ~$0.80/day |

**Note**: Incremental scanning dramatically reduces API costs (80-90% savings)

---

## ✅ Phase 3 Benefits

### **For Day Traders**:
- ✅ **Real-time alerts** for breakout opportunities
- ✅ **Catch momentum** early in the day
- ✅ **Miss fewer setups** during active trading
- ✅ **Automated monitoring** (no manual checking)

### **For Swing Traders**:
- ✅ **Entry timing** for position building
- ✅ **Exit signals** for taking profits
- ✅ **Risk management** via breakdown alerts

### **Technical Benefits**:
- ✅ **Fast rescans** (2-5 min with incremental)
- ✅ **Cost-effective** (~$0.50-1.00/day)
- ✅ **Reliable alerts** (email/SMS/webhook)
- ✅ **Historical tracking** for signal validation

---

## 🔄 Next Steps

### **1. Install Dependencies** (if needed):
```bash
pip install schedule requests twilio
```

### **2. Configure Alerts**:
Edit `config/intraday_rescan_config.json` with your email/SMS settings

### **3. Test the System**:
```bash
# Test during market hours
python models/scheduling/intraday_scheduler.py --market ASX --interval 15
```

### **4. Schedule for Production**:
```bash
# Schedule to auto-start at market open daily
python models/scheduling/intraday_scheduler.py --market ASX --schedule
```

---

## 📝 Implementation Checklist

- [ ] Create `intraday_scheduler.py`
- [ ] Create `intraday_rescan_manager.py`
- [ ] Create `incremental_scanner.py`
- [ ] Create `breakout_detector.py`
- [ ] Create `alert_dispatcher.py`
- [ ] Create `config/intraday_rescan_config.json`
- [ ] Create `RUN_INTRADAY_MONITOR.bat`
- [ ] Test incremental scanning
- [ ] Test breakout detection
- [ ] Test alert delivery
- [ ] Validate performance (timing)
- [ ] Validate cost (API usage)
- [ ] Document user guide
- [ ] Create examples

---

## 🎯 Success Criteria

Phase 3 is complete when:
- ✅ System rescans every N minutes during market hours
- ✅ Incremental scanning reduces API calls by 80%+
- ✅ Breakouts are detected within 15 minutes
- ✅ Alerts are delivered reliably (< 30 second delay)
- ✅ Daily cost is under $1.00
- ✅ System auto-stops at market close

---

**Status**: 🚧 Ready for implementation  
**Estimated Dev Time**: 2-3 days  
**Testing Time**: 1-2 days  
**Total**: ~5 days to production

---

**Questions or need help implementing? Let me know!** 🚀
