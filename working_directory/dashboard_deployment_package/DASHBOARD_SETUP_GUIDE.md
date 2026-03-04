# Live Trading Dashboard - Setup Guide

## Overview

A real-time web dashboard for monitoring the integrated Swing Trading + Intraday system.

**Features:**
- Real-time position tracking
- Performance metrics and charts
- Market sentiment indicators
- Intraday monitoring status
- Alert feed
- Trade history
- Risk exposure monitoring

## Installation

### Prerequisites

```bash
pip install flask flask-cors pandas numpy
```

### Directory Structure

```
working_directory/
├── live_trading_dashboard.py     # Flask backend
├── templates/
│   └── dashboard.html            # Main dashboard HTML
├── static/
│   ├── css/
│   │   └── dashboard.css         # Styles
│   └── js/
│       └── dashboard.js          # Frontend logic
└── requirements.txt
```

## Quick Start

### 1. Standalone Testing (No Coordinator)

```bash
cd working_directory
python live_trading_dashboard.py
```

Visit: `http://localhost:5000`

### 2. Integration with Trading System

```python
from live_trading_dashboard import set_coordinator, start_dashboard
from live_trading_coordinator import LiveTradingCoordinator
import threading

# Initialize trading coordinator
coordinator = LiveTradingCoordinator(
    market="US",
    initial_capital=100000.0,
    paper_trading=True
)

# Register with dashboard
set_coordinator(coordinator)

# Start dashboard in background thread
dashboard_thread = threading.Thread(
    target=start_dashboard,
    kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False}
)
dashboard_thread.daemon = True
dashboard_thread.start()

# Start trading
coordinator.start_intraday_monitoring()
# ... your trading logic ...
```

### 3. Production Deployment

#### Using Gunicorn (Recommended)

```bash
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 live_trading_dashboard:app
```

#### Using NGINX (Production)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## API Endpoints

### GET /api/status
Returns current system status, portfolio summary, and market context.

**Response:**
```json
{
  "status": "online",
  "timestamp": "2024-12-21T10:30:00",
  "portfolio": {
    "capital": {
      "total_value": 105000.00,
      "current_cash": 75000.00,
      "invested": 30000.00,
      "total_return_pct": 5.00
    },
    "positions": {
      "count": 2,
      "swing": 2,
      "intraday": 0
    },
    "performance": {
      "win_rate": 72.5,
      "total_trades": 15,
      "winning_trades": 11,
      "losing_trades": 4
    }
  }
}
```

### GET /api/positions
Returns all open positions with detailed information.

### GET /api/trades?limit=50&offset=0
Returns trade history with pagination.

### GET /api/performance
Returns performance metrics and cumulative returns.

### GET /api/market-context
Returns current market sentiment and analysis.

### GET /api/alerts?limit=50
Returns recent alerts.

### GET /api/risk
Returns risk exposure metrics.

### GET /api/intraday
Returns intraday monitoring status and opportunities.

## Dashboard Features

### Summary Cards
- **Total Capital**: Current portfolio value with return percentage
- **Open Positions**: Count of swing vs intraday positions
- **Win Rate**: Percentage of winning trades
- **Realized P&L**: Total profit/loss from closed trades
- **Market Sentiment**: Real-time sentiment gauge (0-100)
- **Portfolio Heat**: Risk exposure percentage

### Charts
- **Cumulative Returns**: Line chart showing portfolio growth over time
- **Daily P&L**: Bar chart showing daily profit/loss

### Tables
- **Open Positions**: Real-time position tracking with P&L
- **Recent Trades**: History of closed trades

### Intraday Monitoring
- Rescan count and statistics
- Breakouts detected
- Top opportunities with strength scores
- Market status (open/closed)

### Alerts Feed
- Real-time alert stream
- Color-coded by severity (info/warning/error/success)
- Filterable by type

## Customization

### Update Interval

Edit `static/js/dashboard.js`:

```javascript
const CONFIG = {
    updateInterval: 5000,  // Change to 10000 for 10-second updates
    // ...
};
```

### Color Scheme

Edit `static/css/dashboard.css`:

```css
:root {
    --primary-color: #2563eb;  /* Change primary color */
    --success-color: #10b981;
    --danger-color: #ef4444;
    /* ... */
}
```

### Chart Configuration

Edit `static/js/dashboard.js` in the `initializeCharts()` function.

## Security Considerations

### Production Checklist:

1. **Enable Authentication**
   ```python
   from flask_httpauth import HTTPBasicAuth
   
   auth = HTTPBasicAuth()
   
   @auth.verify_password
   def verify_password(username, password):
       # Implement your authentication logic
       return username == "admin" and password == "secure_password"
   
   @app.route('/api/status')
   @auth.login_required
   def get_status():
       # ...
   ```

2. **Use HTTPS** (SSL/TLS)
   - Configure NGINX with SSL certificates
   - Use Let's Encrypt for free certificates

3. **Set SECRET_KEY**
   ```python
   app.config['SECRET_KEY'] = 'your-secret-key-here'
   ```

4. **Rate Limiting**
   ```python
   from flask_limiter import Limiter
   
   limiter = Limiter(app, key_func=lambda: request.remote_addr)
   
   @app.route('/api/status')
   @limiter.limit("60 per minute")
   def get_status():
       # ...
   ```

5. **CORS Configuration**
   ```python
   CORS(app, origins=['https://yourdomain.com'])
   ```

## Monitoring & Logging

### Enable Logging

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/dashboard.log',
    maxBytes=10000000,  # 10MB
    backupCount=5
)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
```

### Health Check Endpoint

```python
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
```

## Troubleshooting

### Dashboard shows "Offline"
- Check if trading coordinator is initialized
- Verify `set_coordinator()` was called

### Charts not updating
- Check browser console for JavaScript errors
- Verify API endpoints are returning data

### Positions not displaying
- Ensure coordinator has open positions
- Check `/api/positions` endpoint directly

### Port already in use
```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
python live_trading_dashboard.py --port 5001
```

## Performance Optimization

### For High-Frequency Updates

1. **Use WebSockets** instead of polling:
   ```python
   from flask_socketio import SocketIO
   
   socketio = SocketIO(app)
   
   @socketio.on('connect')
   def handle_connect():
       emit('status', get_status())
   ```

2. **Cache frequently accessed data**:
   ```python
   from flask_caching import Cache
   
   cache = Cache(app, config={'CACHE_TYPE': 'simple'})
   
   @app.route('/api/status')
   @cache.cached(timeout=5)
   def get_status():
       # ...
   ```

3. **Use Redis for shared state**:
   ```python
   import redis
   r = redis.Redis(host='localhost', port=6379, db=0)
   ```

## Mobile Responsiveness

The dashboard is fully responsive and works on:
- Desktop (1920x1080+)
- Tablet (768x1024)
- Mobile (375x667)

Test responsive design:
- Chrome DevTools (F12 > Device Toolbar)
- Real devices

## Browser Compatibility

Tested on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Support & Issues

For questions or issues:
1. Check logs: `logs/dashboard.log`
2. Test API endpoints directly: `curl http://localhost:5000/api/status`
3. Review browser console errors

## Future Enhancements

Planned features:
- [ ] WebSocket support for real-time updates
- [ ] Trade execution from dashboard
- [ ] Advanced charting with TradingView
- [ ] Mobile app
- [ ] Alert configuration UI
- [ ] Backtesting interface
- [ ] Multi-account support

## License

Part of the FinBERT Enhanced Trading System
© 2024

---

**Ready to monitor your live trading system!** 🚀

Visit `http://localhost:5000` after starting the dashboard.
