# Complete Live Trading System Architecture

## Overview

This document provides a comprehensive view of the integrated Swing Trading + Intraday Monitoring system with the new web dashboard.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        LIVE TRADING PLATFORM                            │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                   WEB MONITORING DASHBOARD                         │ │
│  │  http://localhost:5000                                            │ │
│  │  ┌──────────┬──────────┬──────────┬──────────┬──────────┐       │ │
│  │  │ Capital  │Positions │ Win Rate │   P&L    │ Sentiment│       │ │
│  │  │$105,000  │    2     │  72.5%   │ +$5,000  │  65/100  │       │ │
│  │  └──────────┴──────────┴──────────┴──────────┴──────────┘       │ │
│  │  ┌─────────────────────┬──────────────────────────────┐         │ │
│  │  │ Cumulative Returns  │      Daily P&L Chart        │         │ │
│  │  │   [Line Chart]      │      [Bar Chart]            │         │ │
│  │  └─────────────────────┴──────────────────────────────┘         │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                 ▲                                         │
│                                 │ REST API (8 endpoints)                 │
│                                 │ Auto-refresh every 5 seconds            │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │            FLASK BACKEND (live_trading_dashboard.py)               │ │
│  │  /api/status | /api/positions | /api/trades | /api/performance    │ │
│  │  /api/market-context | /api/alerts | /api/risk | /api/intraday    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                 ▲                                         │
│                                 │                                         │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │         LIVE TRADING COORDINATOR (Core Trading Logic)              │ │
│  │                                                                      │ │
│  │  ┌──────────────────────┐      ┌──────────────────────────┐       │ │
│  │  │  SWING TRADING       │◄────►│  INTRADAY MONITORING     │       │ │
│  │  │  ENGINE (Phase 1-3)  │      │  SYSTEM                  │       │ │
│  │  │                      │      │                          │       │ │
│  │  │ • Entry/Exit Logic   │      │ • SPI Monitor (ASX)      │       │ │
│  │  │ • Position Mgmt      │      │ • US Market Monitor      │       │ │
│  │  │ • Risk Management    │      │ • Macro News Monitor     │       │ │
│  │  │ • Trailing Stops     │      │ • Breakout Detector      │       │ │
│  │  │ • Profit Targets     │      │ • Intraday Scheduler     │       │ │
│  │  │ • Regime Detection   │      │ • Alert Dispatcher       │       │ │
│  │  │ • ML Optimization    │      │ • Every 15-min rescans   │       │ │
│  │  └──────────────────────┘      └──────────────────────────┘       │ │
│  │           │                                 │                        │ │
│  │           └────────────┬────────────────────┘                        │ │
│  │                        ▼                                             │ │
│  │           ┌────────────────────────────┐                            │ │
│  │           │  CROSS-TIMEFRAME INTEGRATION│                            │ │
│  │           │  • Entry enhancement        │                            │ │
│  │           │  • Exit enhancement         │                            │ │
│  │           │  • Position sizing boost    │                            │ │
│  │           │  • Early breakdown exits    │                            │ │
│  │           └────────────────────────────┘                            │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                 ▲                                         │
│                                 │                                         │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    BROKER API INTEGRATION                           │ │
│  │         Alpaca | Interactive Brokers | TD Ameritrade               │ │
│  │  • Place orders (market/limit)                                      │ │
│  │  • Get real-time quotes                                             │ │
│  │  • Fetch account info                                               │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                 ▲                                         │
│                                 │                                         │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                     DATA SOURCES                                    │ │
│  │  Yahoo Finance | Alpha Vantage | NewsAPI | Federal Reserve         │ │
│  │  • Historical prices                                                │ │
│  │  • Real-time quotes                                                 │ │
│  │  • News sentiment                                                   │ │
│  │  • Macro indicators                                                 │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Market Data Ingestion
```
Yahoo Finance / Alpha Vantage
         ↓
[Historical prices, Real-time quotes]
         ↓
LiveTradingCoordinator
```

### 2. Signal Generation
```
Price Data + News Data
         ↓
Swing Trading Engine (FinBERT + LSTM + Technical + Momentum)
         ↓
Signal (confidence, prediction, components)
```

### 3. Cross-Timeframe Enhancement
```
Swing Signal + Intraday Sentiment
         ↓
Enhanced Decision
         ↓
• Block entry if sentiment < 30
• Boost position if sentiment > 70
• Early exit if breakdown > 80
```

### 4. Position Execution
```
Enhanced Signal
         ↓
Calculate Position Size (volatility-adjusted)
         ↓
Broker API (place order)
         ↓
Position Tracking
```

### 5. Monitoring & Alerts
```
Position Updates
         ↓
Dashboard Backend (Flask)
         ↓
REST API (JSON)
         ↓
Web Dashboard (Auto-refresh)
         ↓
User sees real-time updates
```

---

## Component Details

### Swing Trading Engine
**File**: `finbert_v4.4.4/models/backtesting/swing_trader_engine.py`

**Phases**:
- **Phase 1**: Trailing stops, profit targets, 3 concurrent positions
- **Phase 2**: Adaptive holding (3-15 days), regime detection, dynamic weights
- **Phase 3**: Multi-timeframe, volatility sizing, ML optimization, correlation hedging

**Key Methods**:
- `_generate_swing_signal()` - Generate trading signal
- `_enter_position()` - Open new position with dynamic sizing
- `_check_position_exits()` - Check exit conditions
- `run_backtest()` - Run complete backtest

### Intraday Monitoring System

#### SPI Monitor
**File**: `models/screening/spi_monitor.py`
- Tracks ASX 200 and US markets
- Predicts opening gaps
- Calculates sentiment (0-100)

#### US Market Monitor
**File**: `models/screening/us_market_monitor.py`
- Tracks S&P 500, VIX, Dow, Nasdaq
- Calculates volatility and momentum

#### Macro News Monitor
**File**: `models/screening/macro_news_monitor.py`
- Monitors Fed/RBA announcements
- Analyzes sentiment using FinBERT
- Provides macro economic context

#### Intraday Rescan Manager
**File**: `models/scheduling/intraday_rescan_manager.py`
- Orchestrates rescan workflow
- Integrates incremental scanning
- Detects breakouts
- Dispatches alerts

### Web Dashboard

#### Backend
**File**: `live_trading_dashboard.py`
- Flask server with 8 REST API endpoints
- JSON responses
- Alert management
- Performance tracking

#### Frontend
**File**: `templates/dashboard.html`
- Responsive HTML5 UI
- 6 summary cards
- 2 interactive charts
- 3 data tables
- Alert feed

**File**: `static/js/dashboard.js`
- Auto-refresh every 5 seconds
- Chart.js integration
- AJAX requests
- Real-time updates

**File**: `static/css/dashboard.css`
- Modern professional styling
- Responsive design
- Animations and transitions
- Color-coded metrics

---

## Communication Protocols

### REST API (Dashboard ← Coordinator)
```
Request:  GET /api/status
Response: {
  "status": "online",
  "portfolio": {...},
  "positions": [...],
  "market_context": {...}
}
```

### Broker API (Coordinator ← Broker)
```
# Place Order
coordinator.broker.place_order(
    symbol="GOOGL",
    side="buy",
    quantity=10,
    order_type="market"
)

# Get Quote
price = coordinator.broker.get_quote("GOOGL")
```

---

## Configuration

### Swing Trading Config
```json
{
  "swing_trading": {
    "holding_period_days": 5,
    "stop_loss_percent": 3.0,
    "confidence_threshold": 52.0,
    "max_position_size": 0.25,
    "use_trailing_stop": true,
    "use_profit_targets": true
  }
}
```

### Intraday Monitoring Config
```json
{
  "intraday_monitoring": {
    "scan_interval_minutes": 15,
    "breakout_threshold": 70.0,
    "auto_trade_intraday": false
  }
}
```

### Cross-Timeframe Config
```json
{
  "cross_timeframe": {
    "use_intraday_for_entries": true,
    "use_intraday_for_exits": true,
    "sentiment_boost_threshold": 70,
    "sentiment_block_threshold": 30,
    "early_exit_threshold": 80
  }
}
```

---

## Deployment Architecture

### Development
```
Local Machine
├── Python 3.9+
├── Flask dev server
├── SQLite (optional)
└── Browser (localhost:5000)
```

### Production (Single Server)
```
VPS / Cloud Server
├── Gunicorn (WSGI server, 4 workers)
├── NGINX (reverse proxy)
├── PostgreSQL (persistent data)
├── Redis (caching)
└── Supervisor (process management)
```

### Production (Distributed)
```
Load Balancer (NGINX)
     ↓
┌────────────┬────────────┬────────────┐
│ App Server │ App Server │ App Server │
│ Gunicorn   │ Gunicorn   │ Gunicorn   │
└────────────┴────────────┴────────────┘
            ↓
┌────────────────────────────────────┐
│       Shared Services              │
│ • PostgreSQL (positions, trades)   │
│ • Redis (caching, sessions)        │
│ • Message Queue (RabbitMQ/Celery) │
└────────────────────────────────────┘
```

---

## Security Layers

### Layer 1: Network
- Firewall (only ports 80, 443 open)
- VPN for admin access
- DDoS protection

### Layer 2: Application
- HTTPS/SSL (TLS 1.3)
- HTTP Basic Auth or OAuth2
- Rate limiting (60 req/min)
- CORS configuration

### Layer 3: Data
- API keys in environment variables
- Encrypted database connections
- Secure session management
- Input validation and sanitization

---

## Monitoring & Logging

### Application Logs
```
logs/
├── live_trading.log      # Trading coordinator logs
├── dashboard.log         # Dashboard access logs
├── intraday.log          # Intraday monitoring logs
└── errors.log            # Error logs
```

### Health Checks
```
GET /health
→ {"status": "healthy", "timestamp": "..."}

GET /api/status
→ {"status": "online", "market_open": true}
```

### Metrics
- Position count
- Win rate
- Total P&L
- Portfolio heat
- API response times
- Error rate

---

## Disaster Recovery

### State Persistence
```python
# Save state every 5 minutes
coordinator.save_state('live_trading_state.json')

# Restore on startup
coordinator.load_state('live_trading_state.json')
```

### Backup Strategy
- Hourly: State snapshots
- Daily: Full database backup
- Weekly: Remote backup to S3

### Failure Scenarios

**Dashboard Down**
- Trading continues (independent)
- Check logs: `logs/dashboard.log`
- Restart: `supervisorctl restart dashboard`

**Trading System Down**
- Positions remain in broker
- Manual intervention required
- Review last saved state

**Broker API Down**
- Switch to backup broker
- Manual order entry
- Wait for reconnection

---

## Performance Characteristics

| Component | Metric | Target |
|-----------|--------|--------|
| Dashboard Update | Latency | <100ms |
| API Response | Time | <50ms |
| Position Calculation | Time | <10ms |
| Signal Generation | Time | 2-5s |
| Intraday Rescan | Frequency | 15 min |
| Chart Rendering | Time | <200ms |

---

## Scalability

### Vertical Scaling (Single Server)
- ✅ 10+ concurrent dashboard users
- ✅ 50+ positions monitored
- ✅ 1,000+ trades/year tracked
- ✅ 4 CPU cores utilized

### Horizontal Scaling (Multiple Servers)
- Load balancer distributes requests
- Shared database for state
- Redis for distributed caching
- Message queue for async tasks

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, JavaScript ES6 |
| **Charts** | Chart.js 3.9 |
| **Backend** | Flask 2.0+, Python 3.9+ |
| **Server** | Gunicorn, NGINX |
| **Database** | SQLite (dev), PostgreSQL (prod) |
| **Caching** | Redis |
| **Broker** | Alpaca API, Interactive Brokers API |
| **Data** | Yahoo Finance, Alpha Vantage |
| **ML** | TensorFlow/Keras (LSTM), FinBERT |
| **Deployment** | Docker, Supervisor |

---

## Quick Reference

### Start Development
```bash
cd working_directory
python live_trading_with_dashboard.py --paper-trading
```

### Start Production
```bash
gunicorn -w 4 -b 0.0.0.0:5000 live_trading_dashboard:app
```

### Access Dashboard
```
http://localhost:5000
```

### Test API
```bash
curl http://localhost:5000/api/status
```

### Check Logs
```bash
tail -f logs/live_trading.log
```

---

## Further Reading

- **Dashboard Setup**: `DASHBOARD_SETUP_GUIDE.md`
- **Dashboard Summary**: `DASHBOARD_COMPLETE_SUMMARY.md`
- **Final Summary**: `MONITORING_DASHBOARD_FINAL_SUMMARY.md`
- **Phase 1-3 Docs**: `PHASE_1_2_IMPLEMENTATION.md`, `PHASE_3_IMPLEMENTATION.md`
- **Live Trading Guide**: `LIVE_TRADING_INTEGRATION_GUIDE.md`

---

**System Status**: ✅ Production Ready  
**Last Updated**: December 21, 2024  
**Version**: 2.0
