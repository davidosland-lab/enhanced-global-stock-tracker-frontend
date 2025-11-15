# Event Risk Guard - Web UI Guide

## Quick Start

### 1. Start the Web Interface

**Double-click**:
```
START_WEB_UI.bat
```

**Or run manually**:
```batch
python web_ui.py
```

### 2. Access Dashboard

Open your web browser and go to:
```
http://localhost:5000
```

### 3. Stop the Server

Press `Ctrl+C` in the command window

---

## Dashboard Features

### 📊 System Status Cards

**Real-time monitoring of**:
- System Active/Inactive status
- Email notifications enabled/disabled
- LSTM training enabled/disabled
- SPI monitoring enabled/disabled

### 📄 Latest Report

- View most recent overnight screening report
- See report date, size, and last modified time
- Click "View Report" to open full HTML report in new tab

### 🔄 Pipeline Summary

- Stocks scanned count
- Opportunities found
- SPI sentiment score (0-100)
- Market bias (Bullish/Bearish/Neutral)

### 🎯 Top Opportunities

**Table showing**:
- Stock symbol
- Opportunity score (color-coded)
- Trading signal (BUY/SELL/HOLD)
- Confidence percentage
- Sector classification

**Color Coding**:
- 🟢 Green (80-100): High confidence
- 🟡 Yellow (60-79): Medium confidence
- 🔴 Red (0-59): Low confidence

### 🧠 Trained Models

Grid of all trained LSTM models showing:
- Stock symbols with trained models
- Click to see model details

### 📋 Recent Logs

Tail of overnight_pipeline.log showing:
- Last 100 log lines
- Real-time system activity
- Errors and warnings

---

## Settings Panel

### ⚙️ Email Notifications

**Configure**:
- Enable/disable email notifications
- SMTP server (smtp.gmail.com)
- SMTP port (587)
- Username (your Gmail address)
- Password (Gmail App Password)

**Test Email**:
- Click "📧 Send Test Email" button
- Verifies SMTP configuration
- Sends test email to configured recipients

### 🤖 LSTM Training

**Configure**:
- Enable/disable LSTM training
- Max models to train per night
- Priority strategy

### 📈 SPI Monitoring

**Enable/disable**:
- Real-time SPI/ASX200 monitoring
- Gap detection and alerts

---

## Reports Browser

### 📄 View All Reports

Click "View All" to see:
- Complete list of historical reports
- Sorted by date (newest first)
- Report metadata (size, modified date)
- Click any report to open in new tab

---

## API Endpoints

The Web UI provides REST API endpoints:

### System Status
```
GET /api/status
Returns: System status, latest report, pipeline state
```

### Configuration
```
GET /api/config
Returns: Current configuration (password masked)

POST /api/config
Body: Updated configuration JSON
Returns: Success/failure message
```

### Reports
```
GET /api/reports
Returns: List of all available reports

GET /api/reports/<filename>
Returns: HTML content of specific report
```

### Models
```
GET /api/models
Returns: List of trained LSTM models
```

### Logs
```
GET /api/logs
Returns: Last 100 lines of overnight_pipeline.log
```

### Test Email
```
POST /api/test-email
Returns: Success/failure of test email
```

### Sectors
```
GET /api/sectors
Returns: ASX sectors configuration (100+ stocks)
```

---

## Troubleshooting

### "Port 5000 already in use"

**Solution 1**: Close other applications using port 5000

**Solution 2**: Change port in web_ui.py:
```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

### "Flask not installed"

**Solution**: Install Flask:
```batch
pip install flask flask-cors
```

Or run:
```batch
INSTALL.bat
```

### "Cannot connect to http://localhost:5000"

**Check**:
1. Web server is running (see command window)
2. No firewall blocking port 5000
3. Try http://127.0.0.1:5000 instead

### "Configuration not saving"

**Check**:
1. File permissions on screening_config.json
2. Config file is not read-only
3. Valid JSON format in settings

### "Reports not showing"

**Check**:
1. `reports/html/` directory exists
2. At least one overnight pipeline run completed
3. HTML reports generated (run RUN_OVERNIGHT_PIPELINE.bat)

### "Models list empty"

**Check**:
1. `models/lstm_models/` directory exists
2. At least one LSTM model trained
3. .keras files present (run TRAIN_LSTM_SINGLE.bat)

---

## Access from Other Devices

### Local Network Access

**Edit web_ui.py** to allow external access:
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

**Find your IP address**:
```batch
ipconfig
```
Look for "IPv4 Address" (e.g., 192.168.1.100)

**Access from other devices**:
```
http://192.168.1.100:5000
```

**Security Note**: Only do this on trusted networks

### Internet Access (Advanced)

**Not recommended for production** without proper security.

For production deployment, use:
- Reverse proxy (nginx)
- HTTPS/SSL certificates
- Authentication system
- Firewall rules

---

## Auto-Refresh

Dashboard auto-refreshes every 30 seconds:
- System status
- Latest report
- Top opportunities

Manual refresh available via "🔄 Refresh" button

---

## Keyboard Shortcuts

- `Ctrl+R`: Refresh page
- `Ctrl+C`: Stop server (in terminal)
- `Escape`: Close modals

---

## Browser Compatibility

**Tested on**:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+

**Not supported**:
- ❌ Internet Explorer

---

## Mobile Responsive

Dashboard is fully responsive:
- Tablet: 2-column layout
- Phone: Single-column layout
- Touch-friendly buttons
- Swipe-friendly modals

---

## Performance

**Dashboard loads**:
- Initial load: <2 seconds
- Status refresh: <500ms
- Report viewing: <1 second
- Settings save: <500ms

**Resource usage**:
- RAM: ~100 MB
- CPU: <5% idle, <10% during refresh
- Network: Minimal (local API calls only)

---

## Security Considerations

### ⚠️ Important Security Notes

**This is a LOCAL development server**:
- Not intended for public internet access
- No built-in authentication
- No HTTPS/SSL encryption
- Debug mode enabled by default

**Production deployment requires**:
1. Authentication system (login/password)
2. HTTPS with SSL certificates
3. Proper firewall configuration
4. Debug mode disabled
5. Security headers
6. Rate limiting
7. CSRF protection

**For local/trusted network use only**

---

## Development

### Project Structure

```
deployment_event_risk_guard/
├── web_ui.py                 # Flask application
├── templates/
│   └── dashboard.html        # Main dashboard page
├── static/
│   ├── css/
│   │   └── dashboard.css     # Dashboard styles
│   └── js/
│       └── dashboard.js      # Dashboard JavaScript
├── models/                   # Event Risk Guard modules
├── reports/                  # Generated reports
└── logs/                     # System logs
```

### Adding New Features

**1. Add API endpoint** (web_ui.py):
```python
@app.route('/api/my-feature')
def my_feature():
    return jsonify({'data': 'value'})
```

**2. Add UI elements** (dashboard.html):
```html
<div class="my-feature">
    <h2>My Feature</h2>
    <div id="my-feature-content"></div>
</div>
```

**3. Add JavaScript** (dashboard.js):
```javascript
async function loadMyFeature() {
    const response = await fetch('/api/my-feature');
    const data = await response.json();
    document.getElementById('my-feature-content').innerHTML = data.data;
}
```

**4. Add styles** (dashboard.css):
```css
.my-feature {
    /* Your styles */
}
```

---

## Support

For issues or questions:
1. Check this guide first
2. Review logs in `logs/screening/`
3. Check configuration in `models/config/screening_config.json`
4. Refer to main documentation in `docs/`

---

## Summary

**The Web UI provides**:
- ✅ Real-time system monitoring
- ✅ Visual dashboard with charts
- ✅ Easy configuration management
- ✅ Report viewing and history
- ✅ LSTM model tracking
- ✅ Live log viewing
- ✅ Email testing
- ✅ Mobile-responsive design

**Access**: http://localhost:5000 after running START_WEB_UI.bat

**Perfect for**: Local monitoring and system management
