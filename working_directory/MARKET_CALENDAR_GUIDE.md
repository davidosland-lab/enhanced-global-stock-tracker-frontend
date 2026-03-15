# Market Calendar & Trading Hours System
**Version 1.3.5 - Complete Market Hours Tracking with 2026 Calendars**  
**Date: January 1, 2026**

---

## 🕐 Overview

The Phase 3 Trading System now includes a comprehensive **Market Calendar System** that tracks trading hours, holidays, and market status for three major global exchanges:

- **ASX** (Australian Securities Exchange) - Sydney
- **NYSE** (New York Stock Exchange) - New York  
- **LSE** (London Stock Exchange) - London

---

## ✨ Key Features

### 1. Real-Time Market Status
- **Live Status**: Shows if each exchange is OPEN, CLOSED, PRE-MARKET, POST-MARKET, HOLIDAY, or WEEKEND
- **Color-Coded Indicators**: 
  - 🟢 Green = OPEN
  - 🔴 Red = CLOSED
  - 🟡 Yellow = PRE/POST-MARKET
  - 🏖️ Orange = HOLIDAY
  - 📅 Gray = WEEKEND

### 2. Trading Hours Tracking
- **ASX**: 10:00 AM - 4:00 PM AEDT (Pre-market: 7:00 AM)
- **NYSE**: 9:30 AM - 4:00 PM EST (Pre-market: 4:00 AM, Post-market until 8:00 PM)
- **LSE**: 8:00 AM - 4:30 PM GMT (Pre-market auction: 7:50 AM)

### 3. Holiday Calendar (2024-2026)
Complete holiday tracking for all three exchanges including:
- New Year's Day
- Good Friday / Easter Monday
- National holidays (ANZAC Day, Independence Day, etc.)
- Christmas & Boxing Day
- Bank holidays (UK)

### 4. Countdown Timers
- **When OPEN**: Shows time remaining until market close
- **When CLOSED**: Shows time until next market open
- **Multi-day closures**: Shows days + hours for weekends/holidays

### 5. Automatic Trading Protection
- **Market Hours Check**: System automatically checks if markets are open before trading
- **Warning Logs**: Alerts when trying to trade closed markets
- **Symbol-Specific**: Checks correct exchange for each symbol (CBA.AX → ASX, AAPL → NYSE, etc.)

---

## 📊 Dashboard Display

### Market Status Panel

The unified dashboard now includes a prominent market status panel showing all three exchanges:

```
╔═══════════════════════════════════════════════════════════╗
║  🕐 Market Hours & Status                                 ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     ║
║  │    ASX      │  │    NYSE     │  │    LSE      │     ║
║  │ 🔴 CLOSED   │  │ 🔴 CLOSED   │  │ 🟢 OPEN     │     ║
║  │ 17:24 AEDT  │  │ 01:24 EST   │  │ 06:24 GMT   │     ║
║  │ Opens in    │  │ Opens in    │  │ Closes in   │     ║
║  │  16h 35m    │  │  8h 5m      │  │  1h 35m     │     ║
║  └─────────────┘  └─────────────┘  └─────────────┘     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

### Visual Features

1. **Exchange Cards**: Each exchange has its own card with border color matching status
2. **Live Clock**: Shows current time in each exchange's timezone
3. **Status Icon**: Visual indicator (circle) for quick status check
4. **Countdown**: Dynamic countdown to next event (open/close)
5. **Holiday Info**: Displays holiday name when market is closed for holiday

### Updates

- **Auto-Refresh**: Market status updates every 5 seconds
- **Live Countdown**: Timer decrements in real-time
- **Status Changes**: Automatically detects market open/close transitions

---

## 🔧 How It Works

### Symbol Exchange Detection

The system automatically determines which exchange to check based on the symbol suffix:

```python
Symbol Format  →  Exchange
─────────────────────────────
CBA.AX         →  ASX
BHP.AX         →  ASX
RIO.AX         →  ASX
─────────────────────────────
AAPL           →  NYSE
MSFT           →  NYSE
GOOGL          →  NYSE
─────────────────────────────
HSBA.L         →  LSE
BP.L           →  LSE
VOD.L          →  LSE
─────────────────────────────
SAP.DE         →  LSE (European)
MC.PA          →  LSE (European)
ASML.AS        →  LSE (European)
```

### Trading Cycle Integration

Every trading cycle now includes automatic market hours checking:

```
Trading Cycle Start
    ↓
Check Market Status for Each Symbol
    ↓
    ├─ Symbol Market OPEN → Continue trading
    │
    ├─ Symbol Market CLOSED → Log warning, skip symbol
    │
    └─ Symbol Market HOLIDAY → Log holiday name, skip symbol
    ↓
Process only symbols with open markets
    ↓
Continue with ML analysis and trading
```

### Example Console Output

```bash
[INFO] Trading Cycle: 2024-12-29 17:24:27
[CALENDAR] Some markets are closed:
   CBA.AX (ASX closed - Opens in 16h 35m)
   BHP.AX (ASX closed - Opens in 16h 35m)
   RIO.AX (ASX closed - Opens in 16h 35m)
[INFO] Continuing with available markets...
```

---

## 📅 Holiday Schedule

### ASX (Australian Securities Exchange)

**2024 Holidays:**
- January 1 - New Year's Day
- January 26 - Australia Day
- March 29 - Good Friday
- April 1 - Easter Monday
- April 25 - ANZAC Day
- June 10 - Queen's Birthday
- December 25 - Christmas Day
- December 26 - Boxing Day

**2025 Holidays:**
- January 1 - New Year's Day
- January 27 - Australia Day (Observed)
- April 18 - Good Friday
- April 21 - Easter Monday
- April 25 - ANZAC Day
- June 9 - Queen's Birthday
- December 25 - Christmas Day
- December 26 - Boxing Day

**2026 Holidays:**
- January 1 - New Year's Day
- January 26 - Australia Day
- April 3 - Good Friday
- April 6 - Easter Monday
- April 27 - ANZAC Day (Observed)
- June 8 - Queen's Birthday
- December 25 - Christmas Day
- December 28 - Boxing Day (Observed)

### NYSE (New York Stock Exchange)

**2024 Holidays:**
- January 1 - New Year's Day
- January 15 - Martin Luther King Jr. Day
- February 19 - Presidents Day
- March 29 - Good Friday
- May 27 - Memorial Day
- June 19 - Juneteenth
- July 4 - Independence Day
- September 2 - Labor Day
- November 28 - Thanksgiving Day
- December 25 - Christmas Day

**2025 Holidays:**
- January 1 - New Year's Day
- January 20 - Martin Luther King Jr. Day
- February 17 - Presidents Day
- April 18 - Good Friday
- May 26 - Memorial Day
- June 19 - Juneteenth
- July 4 - Independence Day
- September 1 - Labor Day
- November 27 - Thanksgiving Day
- December 25 - Christmas Day

**2026 Holidays:**
- January 1 - New Year's Day
- January 19 - Martin Luther King Jr. Day
- February 16 - Presidents Day
- April 3 - Good Friday
- May 25 - Memorial Day
- June 19 - Juneteenth
- July 3 - Independence Day (Observed)
- September 7 - Labor Day
- November 26 - Thanksgiving Day
- December 25 - Christmas Day

### LSE (London Stock Exchange)

**2024 Holidays:**
- January 1 - New Year's Day
- March 29 - Good Friday
- April 1 - Easter Monday
- May 6 - Early May Bank Holiday
- May 27 - Spring Bank Holiday
- August 26 - Summer Bank Holiday
- December 25 - Christmas Day
- December 26 - Boxing Day

**2025 Holidays:**
- January 1 - New Year's Day
- April 18 - Good Friday
- April 21 - Easter Monday
- May 5 - Early May Bank Holiday
- May 26 - Spring Bank Holiday
- August 25 - Summer Bank Holiday
- December 25 - Christmas Day
- December 26 - Boxing Day

**2026 Holidays:**
- January 1 - New Year's Day
- April 3 - Good Friday
- April 6 - Easter Monday
- May 4 - Early May Bank Holiday
- May 25 - Spring Bank Holiday
- August 31 - Summer Bank Holiday
- December 25 - Christmas Day
- December 28 - Boxing Day (Observed)

---

## 🎯 Practical Usage Examples

### Example 1: ASX Trading During US Hours

**Scenario**: You're trading ASX stocks (CBA.AX) during US daytime

```
Time: 2:00 PM EST (5:00 AM AEDT next day)
Status: ASX CLOSED (opens at 10:00 AM AEDT)

Dashboard shows:
┌─────────────┐
│    ASX      │
│ 🔴 CLOSED   │
│ 05:00 AEDT  │
│ Opens in 5h │
└─────────────┘

System behavior:
- Logs: [CALENDAR] CBA.AX (ASX closed - Opens in 5h)
- No new positions opened for ASX stocks
- Existing ASX positions still monitored
- Can trade NYSE stocks simultaneously
```

### Example 2: Trading Multiple Exchanges

**Scenario**: Portfolio with ASX, NYSE, and LSE stocks

```
Symbols: CBA.AX, AAPL, HSBA.L
Time: 9:00 PM EST (12:00 PM AEDT, 2:00 AM GMT)

Market Status:
- ASX: 🟢 OPEN (Closes in 4h)
- NYSE: 🔴 CLOSED (Opens in 12h 30m)
- LSE: 🔴 CLOSED (Opens in 6h)

System behavior:
- CBA.AX: ✅ Can trade (ASX open)
- AAPL: ⏸️ Skipped (NYSE closed)
- HSBA.L: ⏸️ Skipped (LSE closed)
```

### Example 3: Holiday Trading

**Scenario**: December 25, 2024 (Christmas Day)

```
All Exchanges Status:
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│    ASX      │  │    NYSE     │  │    LSE      │
│ 🏖️ HOLIDAY  │  │ 🏖️ HOLIDAY  │  │ 🏖️ HOLIDAY  │
│ Christmas   │  │ Christmas   │  │ Christmas   │
│ Opens       │  │ Opens       │  │ Opens       │
│ Dec 26      │  │ Dec 26      │  │ Dec 27      │
└─────────────┘  └─────────────┘  └─────────────┘

System behavior:
- No trading occurs
- Dashboard shows holiday status
- Countdown to next trading day
- Positions still tracked (mark-to-market paused)
```

---

## 🛠️ Advanced Features

### 1. Timezone Awareness

The system uses `pytz` for accurate timezone handling:

```python
ASX:  'Australia/Sydney'  (AEDT/AEST)
NYSE: 'America/New_York'  (EST/EDT)
LSE:  'Europe/London'     (GMT/BST)
```

All times automatically adjust for daylight saving time transitions.

### 2. Pre-Market & Post-Market

The system tracks extended trading hours:

**NYSE Extended Hours:**
- Pre-market: 4:00 AM - 9:30 AM EST
- Regular: 9:30 AM - 4:00 PM EST
- Post-market: 4:00 PM - 8:00 PM EST

**Status Display:**
```
8:45 AM EST:  🔵 PRE-MARKET (Opens in 45m)
10:00 AM EST: 🟢 OPEN (Closes in 6h)
5:30 PM EST:  🟡 POST-MARKET (Next open in 15h)
```

### 3. Weekend Handling

Weekends automatically calculated:

```
Saturday/Sunday Status:
┌─────────────┐
│    ASX      │
│ 📅 WEEKEND  │
│ 14:30 AEDT  │
│ Opens in    │
│  1d 19h     │
└─────────────┘
```

### 4. Next Trading Day Calculation

System automatically finds next available trading day:

```
Friday 5:00 PM → Monday 9:30 AM (skips weekend)
Wednesday before Thanksgiving → Friday (skips Thursday holiday)
Dec 24 → Dec 27 (skips Christmas + Boxing Day)
```

---

## 📱 API Reference

### `MarketCalendar` Class

```python
from ml_pipeline.market_calendar import MarketCalendar, Exchange

# Initialize
calendar = MarketCalendar()

# Get market status
info = calendar.get_market_status(Exchange.ASX)
print(f"Status: {info.status.value}")
print(f"Is Trading Day: {info.is_trading_day}")

# Check if symbol can be traded
can_trade, reason = calendar.can_trade_symbol("CBA.AX")
if can_trade:
    print("✅ Can trade")
else:
    print(f"❌ Cannot trade: {reason}")

# Get all market statuses
all_status = calendar.get_all_market_status()
for exchange, info in all_status.items():
    print(f"{exchange.value}: {info.status.value}")

# Get upcoming holidays
holidays = calendar.get_upcoming_holidays(Exchange.ASX, days_ahead=30)
for date, name in holidays:
    print(f"{date}: {name}")
```

### `MarketInfo` Dataclass

```python
@dataclass
class MarketInfo:
    exchange: Exchange
    status: MarketStatus
    current_time: datetime
    market_open_time: Optional[datetime]
    market_close_time: Optional[datetime]
    time_to_open: Optional[timedelta]
    time_to_close: Optional[timedelta]
    holiday_name: Optional[str]
    is_trading_day: bool
```

### `MarketStatus` Enum

```python
class MarketStatus(Enum):
    OPEN = "OPEN"           # Regular trading hours
    CLOSED = "CLOSED"       # Outside trading hours
    PRE_MARKET = "PRE_MARKET"     # Before market open
    POST_MARKET = "POST_MARKET"   # After market close
    HOLIDAY = "HOLIDAY"     # Public holiday
    WEEKEND = "WEEKEND"     # Saturday/Sunday
```

---

## 🧪 Testing

### Test Market Calendar

```bash
cd /home/user/webapp/working_directory
python ml_pipeline/market_calendar.py
```

**Expected Output:**
```
============================================================
MARKET CALENDAR TEST
============================================================

ASX Status:
ASX Market Status:
  Status: CLOSED
  Local Time: 2026-01-01 17:24:27 AEDT
  Time to Open: 16h 35m
  Next Open: 2026-01-01 10:00 AEDT

NYSE Status:
NYSE Market Status:
  Status: CLOSED
  Local Time: 2026-01-01 01:24:27 EST
  Time to Open: 8h 5m
  Next Open: 2026-01-01 09:30 EST

LSE Status:
LSE Market Status:
  Status: OPEN
  Local Time: 2026-01-01 06:24:27 GMT
  Time to Close: 10h 5m

============================================================
SYMBOL TRADING STATUS
============================================================
[OK] CAN TRADE: HSBA.L - LSE market is OPEN
[WARN] CANNOT TRADE: CBA.AX - ASX closed - Opens in 16h 35m
[WARN] CANNOT TRADE: AAPL - NYSE closed - Opens in 8h 5m
```

---

## 📈 Integration Benefits

### 1. Compliance
- Ensures trading only occurs during valid market hours
- Respects exchange holidays and closures
- Prevents execution errors from closed markets

### 2. User Awareness
- Clear visual indication of market status
- Countdown timers for planning trades
- Holiday notifications in advance

### 3. Multi-Exchange Trading
- Seamless handling of global portfolios
- Automatic timezone conversions
- Exchange-specific rules applied correctly

### 4. Error Prevention
- Automatic market hours validation
- Warning logs for debugging
- Graceful handling of closed markets

---

## 🎓 Pro Tips

### Tip 1: Plan Around Market Hours

```
Best times for multi-exchange trading:

📍 8:00 AM - 10:00 AM GMT (ASX + LSE overlap)
   - Trade both Australian and UK stocks

📍 9:30 AM - 4:00 PM EST (NYSE hours)
   - Trade US stocks
   - ASX already closed
   - LSE closes at 11:30 AM EST

📍 4:00 PM - 4:30 PM EST (LSE closing)
   - Last chance for UK stocks
   - NYSE post-market available
```

### Tip 2: Use Pre-Market Data

```
Pre-market status indicates:
🔵 PRE-MARKET = Market opening soon
   - Good time to prepare orders
   - Review overnight news
   - Check gaps from previous close
```

### Tip 3: Weekend & Holiday Planning

```
Dashboard shows days until next open:
📅 "Opens in 2d 15h" = Plan for Monday
🏖️ "Holiday: Christmas" = Extended closure
```

### Tip 4: Global Portfolio Strategy

```
Optimize trading by exchange hours:

Morning (EST):   Focus on LSE stocks
Midday (EST):    Trade NYSE actively  
Evening (EST):   Monitor ASX opening (next day)
```

---

## 📊 Summary

### What's New in v1.3.4

✅ **Market Calendar Module** - Complete trading hours tracking  
✅ **Holiday Database** - 2024-2025 holidays for ASX/NYSE/LSE  
✅ **Dashboard Panel** - Visual market status display  
✅ **Automatic Checking** - Prevents closed-market trading  
✅ **Countdown Timers** - Time to open/close for each exchange  
✅ **Timezone Support** - Accurate time across all exchanges  
✅ **Symbol Detection** - Auto-identifies correct exchange  
✅ **Holiday Warnings** - Clear notifications of market closures  

### Package Information

**Version:** 1.3.4 - Market Calendar System  
**File:** `phase3_trading_system_v1.3.4_WINDOWS.zip`  
**Size:** 326 KB  
**New Files:** `ml_pipeline/market_calendar.py`  
**Updated:** `unified_trading_dashboard.py`, `paper_trading_coordinator.py`  

---

## 🚀 Get Started

1. **Download** updated package v1.3.4
2. **Extract** to `C:\Users\david\Trading\`
3. **Start** unified dashboard: `START_UNIFIED_DASHBOARD.bat`
4. **See** live market status panel at top of dashboard
5. **Trade** with confidence knowing market hours are tracked!

---

**Your trading system is now market-aware! 🌍⏰📊**
