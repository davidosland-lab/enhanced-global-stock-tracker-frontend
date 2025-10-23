# Desktop Deployment Guide - Technical Analysis Module

## 🖥️ Desktop Version Features

The desktop version (`technical_analysis_desktop.html`) includes **4 different candlestick chart libraries** that provide professional-grade financial visualizations:

### 1. **TradingView Lightweight Charts** (Recommended)
- Professional trading platform quality
- Smooth zooming and panning
- Real candlestick rendering
- Volume histogram overlay
- Best performance

### 2. **ApexCharts**
- Built-in candlestick support
- Interactive toolbar
- Download chart as image
- Excellent tooltips
- Good for reports

### 3. **Chart.js with Financial Plugin**
- Requires proper plugin setup
- Standard Chart.js integration
- Customizable appearance
- May need local plugin files

### 4. **Plotly.js**
- Scientific computing quality
- 3D capabilities
- Export to various formats
- Best for data analysis

## 📦 Installation Steps

### Option 1: Simple HTML Deployment

1. **Download Files**
```bash
# Clone the repository
git clone https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend.git
cd enhanced-global-stock-tracker-frontend/working_directory
```

2. **Start Backend**
```bash
# Install Python dependencies
pip install flask flask-cors yfinance pandas

# Run the backend
python backend_fixed_v2.py
```

3. **Open Module**
- Open `modules/technical_analysis_desktop.html` in your browser
- Or serve with Python: `python -m http.server 8000`

### Option 2: Electron Desktop App

1. **Setup Electron Project**
```bash
# Create new directory
mkdir trading-analysis-desktop
cd trading-analysis-desktop

# Initialize npm
npm init -y

# Install Electron
npm install electron --save-dev
```

2. **Create main.js**
```javascript
const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
    const win = new BrowserWindow({
        width: 1600,
        height: 900,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        },
        icon: path.join(__dirname, 'icon.png'),
        title: 'Technical Analysis Suite'
    });
    
    win.loadFile('technical_analysis_desktop.html');
    win.maximize();
}

app.whenReady().then(createWindow);
```

3. **Update package.json**
```json
{
  "name": "trading-analysis-desktop",
  "version": "1.0.0",
  "main": "main.js",
  "scripts": {
    "start": "electron ."
  }
}
```

4. **Run Desktop App**
```bash
npm start
```

### Option 3: Python Desktop App (with Tkinter WebView)

1. **Install Dependencies**
```bash
pip install pywebview flask flask-cors yfinance pandas
```

2. **Create desktop_app.py**
```python
import webview
import threading
from backend_fixed_v2 import app  # Import your Flask app

def start_backend():
    app.run(port=8002, debug=False)

if __name__ == '__main__':
    # Start backend in thread
    backend_thread = threading.Thread(target=start_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Create window
    webview.create_window(
        'Technical Analysis Suite',
        'http://localhost:8002/technical_analysis_desktop.html',
        width=1600,
        height=900
    )
    webview.start()
```

## 🔧 Backend Configuration

### Local Backend Setup

1. **Update Backend URL in HTML**
```javascript
// In technical_analysis_desktop.html, line ~355
const BACKEND_URL = 'http://localhost:8002';  // Your local backend
```

2. **Configure CORS** (if needed)
```python
# In backend_fixed_v2.py
from flask_cors import CORS
CORS(app, origins=['http://localhost:*', 'file://*'])
```

### Using External Data Sources

For desktop deployment, you can also use:

1. **Alpha Vantage API**
```javascript
const API_KEY = 'your_api_key';
const url = `https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=${symbol}&apikey=${API_KEY}`;
```

2. **IEX Cloud**
```javascript
const TOKEN = 'your_token';
const url = `https://cloud.iexapis.com/stable/stock/${symbol}/chart/1m?token=${TOKEN}`;
```

3. **Polygon.io**
```javascript
const API_KEY = 'your_api_key';
const url = `https://api.polygon.io/v2/aggs/ticker/${symbol}/range/1/day/2023-01-01/2024-01-01?apiKey=${API_KEY}`;
```

## 📊 Chart Library Setup

### Installing Chart Libraries Locally

1. **TradingView Lightweight Charts**
```bash
npm install lightweight-charts
# Copy to your project: node_modules/lightweight-charts/dist/
```

2. **ApexCharts**
```bash
npm install apexcharts
# Copy to your project: node_modules/apexcharts/dist/
```

3. **Chart.js with Financial**
```bash
npm install chart.js chartjs-chart-financial luxon chartjs-adapter-luxon
# Copy all dist files to your project
```

4. **Plotly.js**
```bash
npm install plotly.js-dist
# Copy to your project: node_modules/plotly.js-dist/
```

### Using Local Files Instead of CDN

Replace CDN links with local files:
```html
<!-- Instead of CDN -->
<script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>

<!-- Use local file -->
<script src="./lib/lightweight-charts.standalone.production.js"></script>
```

## 🚀 Performance Optimization

### For Desktop Deployment

1. **Cache Historical Data**
```javascript
const cache = new Map();

async function fetchWithCache(symbol) {
    if (cache.has(symbol)) {
        return cache.get(symbol);
    }
    const data = await fetch(`${BACKEND_URL}/api/historical/${symbol}`);
    cache.set(symbol, data);
    return data;
}
```

2. **Use WebWorkers for Calculations**
```javascript
// worker.js
self.onmessage = function(e) {
    const { data, indicator } = e.data;
    const result = calculateIndicator(data, indicator);
    self.postMessage(result);
}

// main.js
const worker = new Worker('worker.js');
worker.postMessage({data: ohlcData, indicator: 'RSI'});
```

3. **Optimize Chart Rendering**
```javascript
// Limit data points for better performance
const maxDataPoints = 500;
if (ohlcData.length > maxDataPoints) {
    ohlcData = ohlcData.slice(-maxDataPoints);
}
```

## 🎨 Customization

### Dark Theme (Professional Trading Look)
```css
body {
    background: #0d1117;
    color: #c9d1d9;
}

.chart-container {
    background: #161b22;
    border: 1px solid #30363d;
}
```

### Custom Indicators
```javascript
// Add custom indicators to any chart library
function addBollingerBands(chart, data, period = 20, stdDev = 2) {
    const sma = calculateSMA(data, period);
    const std = calculateStandardDeviation(data, period);
    
    const upper = sma.map((val, i) => val + (std[i] * stdDev));
    const lower = sma.map((val, i) => val - (std[i] * stdDev));
    
    // Add to chart based on library
    return { upper, middle: sma, lower };
}
```

## 📋 Features Checklist

Desktop version includes:
- ✅ Real candlestick charts (4 libraries)
- ✅ Volume visualization
- ✅ Multiple timeframes
- ✅ Technical indicators
- ✅ Drawing tools (TradingView)
- ✅ Export functionality
- ✅ Offline capability
- ✅ High performance
- ✅ No sandbox limitations

## 🔍 Troubleshooting

### Common Issues and Solutions

1. **Chart.js Financial Plugin Not Working**
   - Download the plugin locally
   - Register it properly: `Chart.register(window.ChartFinancial);`

2. **CORS Errors**
   - Run Chrome with: `--disable-web-security --user-data-dir=/tmp/chrome`
   - Or use a local proxy

3. **Performance Issues**
   - Reduce data points
   - Use pagination for historical data
   - Implement virtual scrolling

4. **Missing Data**
   - Check backend is running
   - Verify API endpoints
   - Check network tab in DevTools

## 📚 Additional Resources

- [TradingView Docs](https://tradingview.github.io/lightweight-charts/)
- [ApexCharts Docs](https://apexcharts.com/docs/chart-types/candlestick/)
- [Chart.js Financial](https://github.com/chartjs/chartjs-chart-financial)
- [Plotly Financial Charts](https://plotly.com/javascript/candlestick-charts/)

## 🎯 Quick Start

```bash
# 1. Clone repo
git clone [repo-url]

# 2. Install backend dependencies
pip install -r requirements.txt

# 3. Start backend
python backend_fixed_v2.py

# 4. Open desktop version
open modules/technical_analysis_desktop.html

# 5. Select your preferred chart library
# 6. Analyze any stock!
```

---

**Desktop Version Advantages:**
- No sandbox restrictions
- Full plugin support
- Better performance
- Local data caching
- Offline capability
- Custom integrations

Last Updated: October 3, 2025