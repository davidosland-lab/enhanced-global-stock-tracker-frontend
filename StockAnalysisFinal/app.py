#!/usr/bin/env python3
"""
Stock Analysis System - Windows 11 Fixed Version
Handles connectivity issues and provides proper error handling
"""

import yfinance as yf
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import requests
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# Alpha Vantage Configuration
ALPHA_VANTAGE_API_KEY = "68ZFANK047DL0KSR"

def get_test_data(symbol='AAPL'):
    """Generate test data when API fails"""
    now = datetime.now()
    dates = pd.date_range(end=now, periods=30, freq='D')
    
    # Generate realistic price data
    base_price = 150 if 'AAPL' in symbol else 100
    prices = []
    for i in range(30):
        change = np.random.randn() * 2  # Random daily change
        base_price = base_price * (1 + change/100)
        prices.append(base_price)
    
    df = pd.DataFrame({
        'Open': [p * (1 + np.random.randn()*0.01) for p in prices],
        'High': [p * (1 + abs(np.random.randn())*0.02) for p in prices],
        'Low': [p * (1 - abs(np.random.randn())*0.02) for p in prices],
        'Close': prices,
        'Volume': [np.random.randint(10000000, 50000000) for _ in range(30)]
    }, index=dates)
    
    # Ensure High >= Close >= Low
    df['High'] = df[['Open', 'High', 'Close']].max(axis=1)
    df['Low'] = df[['Open', 'Low', 'Close']].min(axis=1)
    
    return df

def fetch_stock_data(symbol, period='1mo'):
    """Fetch stock data with multiple fallback options"""
    try:
        # Auto-detect Australian stocks
        au_stocks = ['CBA', 'BHP', 'CSL', 'NAB', 'ANZ', 'WBC', 'WES', 'MQG', 'TLS', 'WOW']
        if symbol.upper().replace('.AX', '') in au_stocks and not symbol.endswith('.AX'):
            symbol = f"{symbol.upper()}.AX"
        
        # Try Yahoo Finance first
        print(f"Attempting to fetch {symbol} from Yahoo Finance...")
        
        # Create ticker object
        ticker = yf.Ticker(symbol)
        
        # Use download method as alternative
        end_date = datetime.now()
        if period == '1d':
            start_date = end_date - timedelta(days=1)
            interval = '5m'
        elif period == '5d':
            start_date = end_date - timedelta(days=5)
            interval = '30m'
        elif period == '1mo':
            start_date = end_date - timedelta(days=30)
            interval = '1d'
        elif period == '3mo':
            start_date = end_date - timedelta(days=90)
            interval = '1d'
        elif period == '6mo':
            start_date = end_date - timedelta(days=180)
            interval = '1d'
        elif period == '1y':
            start_date = end_date - timedelta(days=365)
            interval = '1d'
        else:
            start_date = end_date - timedelta(days=30)
            interval = '1d'
        
        # Try yfinance download
        df = yf.download(
            symbol, 
            start=start_date, 
            end=end_date, 
            interval=interval,
            progress=False,
            show_errors=False,
            threads=False,
            auto_adjust=True,
            repair=True
        )
        
        if not df.empty:
            print(f"Successfully fetched {len(df)} data points for {symbol}")
            # Handle MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
            return df, "Yahoo Finance"
        
        # Try ticker.history as backup
        print(f"Trying ticker.history for {symbol}...")
        df = ticker.history(period=period)
        
        if not df.empty:
            print(f"Successfully fetched {len(df)} data points using history")
            return df, "Yahoo Finance (history)"
            
    except Exception as e:
        print(f"Yahoo Finance error: {str(e)}")
    
    # Try Alpha Vantage
    try:
        print(f"Trying Alpha Vantage for {symbol}...")
        
        # Remove .AX for Alpha Vantage
        av_symbol = symbol.replace('.AX', '')
        
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': av_symbol,
            'apikey': ALPHA_VANTAGE_API_KEY,
            'outputsize': 'compact'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Time Series (Daily)' in data:
            time_series = data['Time Series (Daily)']
            df_data = []
            for date, values in list(time_series.items())[:30]:  # Last 30 days
                df_data.append({
                    'Date': pd.to_datetime(date),
                    'Open': float(values['1. open']),
                    'High': float(values['2. high']),
                    'Low': float(values['3. low']),
                    'Close': float(values['4. close']),
                    'Volume': int(values['5. volume'])
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)
            print(f"Alpha Vantage: Got {len(df)} data points")
            return df, "Alpha Vantage"
            
    except Exception as e:
        print(f"Alpha Vantage error: {str(e)}")
    
    # Use test data as last resort
    print(f"Using test data for {symbol}")
    return get_test_data(symbol), "Test Data (APIs unavailable)"

@app.route('/api/test')
def test_endpoint():
    """Test endpoint to verify server is running"""
    return jsonify({
        'status': 'ok',
        'message': 'Server is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """API endpoint for raw stock data"""
    try:
        period = request.args.get('period', '1mo')
        df, source = fetch_stock_data(symbol, period)
        
        if df.empty:
            return jsonify({'error': f'No data available for {symbol}'}), 404
        
        # Convert to JSON-friendly format
        data = {
            'dates': [d.strftime('%Y-%m-%d %H:%M:%S') for d in df.index],
            'open': [float(p) for p in df['Open'].values],
            'high': [float(p) for p in df['High'].values],
            'low': [float(p) for p in df['Low'].values],
            'close': [float(p) for p in df['Close'].values],
            'volume': [int(v) for v in df['Volume'].values],
            'current_price': float(df['Close'].iloc[-1]),
            'min_price': float(df['Low'].min()),
            'max_price': float(df['High'].max()),
            'data_points': len(df),
            'source': source
        }
        
        return jsonify(data)
    except Exception as e:
        print(f"Error in get_stock_data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart', methods=['POST', 'OPTIONS'])
def generate_chart():
    """Generate interactive chart with technical indicators"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        return '', 204
        
    try:
        data = request.json
        symbol = data.get('symbol', 'AAPL')
        period = data.get('period', '1mo')
        chart_type = data.get('chart_type', 'candlestick')
        
        # Fetch data
        df, source = fetch_stock_data(symbol, period)
        
        if df.empty:
            return jsonify({
                'error': f'No data available for {symbol}',
                'success': False
            }), 404
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=['Price', 'Volume', 'RSI'],
            vertical_spacing=0.05,
            specs=[[{"secondary_y": False}],
                   [{"secondary_y": False}],
                   [{"secondary_y": False}]]
        )
        
        # Price chart
        if chart_type == 'candlestick':
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='OHLC',
                increasing=dict(line=dict(color='#26a69a'), fillcolor='#26a69a'),
                decreasing=dict(line=dict(color='#ef5350'), fillcolor='#ef5350')
            ), row=1, col=1)
            
            # Add moving average
            if len(df) >= 20:
                sma20 = df['Close'].rolling(20).mean()
                fig.add_trace(go.Scatter(
                    x=df.index, y=sma20,
                    line=dict(color='orange', width=1),
                    name='SMA 20'
                ), row=1, col=1)
                
        elif chart_type == 'line':
            fig.add_trace(go.Scatter(
                x=df.index, y=df['Close'],
                mode='lines',
                name='Close',
                line=dict(color='#2196F3', width=2)
            ), row=1, col=1)
        else:  # area
            fig.add_trace(go.Scatter(
                x=df.index, y=df['Close'],
                mode='lines',
                name='Close',
                line=dict(color='#2196F3', width=2),
                fill='tozeroy',
                fillcolor='rgba(33, 150, 243, 0.3)'
            ), row=1, col=1)
        
        # Volume bars
        colors = ['#26a69a' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ef5350' 
                 for i in range(len(df))]
        fig.add_trace(go.Bar(
            x=df.index, y=df['Volume'],
            marker_color=colors,
            showlegend=False,
            name='Volume'
        ), row=2, col=1)
        
        # RSI
        if len(df) >= 14:
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            rs = gain / (loss + 1e-10)
            rsi = 100 - (100 / (1 + rs))
            
            fig.add_trace(go.Scatter(
                x=df.index, y=rsi,
                mode='lines',
                name='RSI',
                line=dict(color='purple', width=2)
            ), row=3, col=1)
            
            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                         opacity=0.3, row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", 
                         opacity=0.3, row=3, col=1)
        
        # Calculate price range
        price_min = df[['Open', 'High', 'Low', 'Close']].min().min()
        price_max = df[['Open', 'High', 'Low', 'Close']].max().max()
        price_range = price_max - price_min
        
        # Update layout
        fig.update_layout(
            title=f'{symbol.upper()} - {source}',
            height=800,
            showlegend=True,
            hovermode='x unified',
            xaxis_rangeslider_visible=False,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Update axes
        fig.update_yaxes(
            title_text="Price ($)",
            range=[price_min - price_range*0.1, price_max + price_range*0.1],
            row=1, col=1
        )
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=3, col=1)
        fig.update_xaxes(title_text="Date", row=3, col=1)
        
        # Return chart data
        return jsonify({
            'success': True,
            'chart': json.loads(fig.to_json()),
            'stats': {
                'symbol': symbol.upper(),
                'period': period,
                'min_price': float(price_min),
                'max_price': float(price_max),
                'current_price': float(df['Close'].iloc[-1]),
                'data_points': len(df),
                'source': source
            }
        })
        
    except Exception as e:
        print(f"Error in generate_chart: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/')
def index():
    """Main interface"""
    html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Stock Analysis System - Windows 11</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', system-ui, Arial, sans-serif;
            background: #f0f2f5;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 8px;
            padding: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 24px;
        }
        
        .header h1 {
            color: #1a1a1a;
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .header p {
            color: #666;
            font-size: 14px;
        }
        
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4CAF50;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .controls {
            background: white;
            border-radius: 8px;
            padding: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 24px;
        }
        
        .controls-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }
        
        .control-group {
            display: flex;
            flex-direction: column;
        }
        
        .control-group label {
            font-size: 12px;
            color: #666;
            margin-bottom: 6px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .control-group input,
        .control-group select {
            padding: 10px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 14px;
            transition: all 0.2s;
        }
        
        .control-group input:focus,
        .control-group select:focus {
            border-color: #0078d4;
            outline: none;
            box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.1);
        }
        
        .button-group {
            display: flex;
            gap: 12px;
        }
        
        button {
            padding: 10px 20px;
            background: #0078d4;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        button:hover {
            background: #106ebe;
        }
        
        button:active {
            transform: translateY(1px);
        }
        
        button.secondary {
            background: #6c757d;
        }
        
        button.secondary:hover {
            background: #5a6268;
        }
        
        .chart-container {
            background: white;
            border-radius: 8px;
            padding: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            min-height: 500px;
        }
        
        #chart {
            width: 100%;
            height: 800px;
        }
        
        #loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 400px;
            color: #666;
            font-size: 14px;
        }
        
        .stats-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        
        .stat-card {
            background: white;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stat-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 4px;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: 600;
            color: #1a1a1a;
        }
        
        .quick-symbols {
            display: flex;
            gap: 8px;
            margin-top: 16px;
            flex-wrap: wrap;
        }
        
        .symbol-btn {
            padding: 6px 12px;
            background: #f0f2f5;
            border: 1px solid #d1d5db;
            border-radius: 16px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .symbol-btn:hover {
            background: #0078d4;
            color: white;
            border-color: #0078d4;
        }
        
        .error-msg {
            background: #fee;
            color: #c00;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 16px;
            display: none;
        }
        
        .success-msg {
            background: #efe;
            color: #060;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 16px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="status-indicator"></span>Stock Analysis System</h1>
            <p>Professional stock charts with real-time data</p>
        </div>
        
        <div id="errorMsg" class="error-msg"></div>
        <div id="successMsg" class="success-msg"></div>
        
        <div class="controls">
            <div class="controls-grid">
                <div class="control-group">
                    <label>Stock Symbol</label>
                    <input type="text" id="symbol" value="AAPL" placeholder="AAPL, MSFT, CBA...">
                </div>
                
                <div class="control-group">
                    <label>Time Period</label>
                    <select id="period">
                        <option value="1d">1 Day</option>
                        <option value="5d">5 Days</option>
                        <option value="1mo" selected>1 Month</option>
                        <option value="3mo">3 Months</option>
                        <option value="6mo">6 Months</option>
                        <option value="1y">1 Year</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label>Chart Type</label>
                    <select id="chartType">
                        <option value="candlestick">Candlestick</option>
                        <option value="line">Line</option>
                        <option value="area">Area</option>
                    </select>
                </div>
            </div>
            
            <div class="button-group">
                <button onclick="loadChart()">Generate Chart</button>
                <button class="secondary" onclick="testConnection()">Test Connection</button>
            </div>
            
            <div class="quick-symbols">
                <span style="color: #666; margin-right: 8px;">Quick access:</span>
                <span class="symbol-btn" onclick="setSymbol('AAPL')">AAPL</span>
                <span class="symbol-btn" onclick="setSymbol('GOOGL')">GOOGL</span>
                <span class="symbol-btn" onclick="setSymbol('MSFT')">MSFT</span>
                <span class="symbol-btn" onclick="setSymbol('TSLA')">TSLA</span>
                <span class="symbol-btn" onclick="setSymbol('CBA')">CBA</span>
                <span class="symbol-btn" onclick="setSymbol('BHP')">BHP</span>
            </div>
        </div>
        
        <div id="statsRow" class="stats-row"></div>
        
        <div class="chart-container">
            <div id="chart">
                <div id="loading">Ready to load chart data</div>
            </div>
        </div>
    </div>
    
    <script>
        function showError(msg) {
            const errorDiv = document.getElementById('errorMsg');
            errorDiv.textContent = msg;
            errorDiv.style.display = 'block';
            setTimeout(() => { errorDiv.style.display = 'none'; }, 5000);
        }
        
        function showSuccess(msg) {
            const successDiv = document.getElementById('successMsg');
            successDiv.textContent = msg;
            successDiv.style.display = 'block';
            setTimeout(() => { successDiv.style.display = 'none'; }, 5000);
        }
        
        function setSymbol(symbol) {
            document.getElementById('symbol').value = symbol;
            loadChart();
        }
        
        async function testConnection() {
            try {
                const response = await fetch('/api/test');
                const data = await response.json();
                if (data.status === 'ok') {
                    showSuccess('Connection successful! Server is running.');
                }
            } catch (error) {
                showError('Connection failed: ' + error.message);
            }
        }
        
        async function loadChart() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            const chartType = document.getElementById('chartType').value;
            
            if (!symbol) {
                showError('Please enter a stock symbol');
                return;
            }
            
            document.getElementById('chart').innerHTML = '<div id="loading">Loading chart data...</div>';
            
            try {
                const response = await fetch('/api/chart', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        symbol: symbol,
                        period: period,
                        chart_type: chartType
                    })
                });
                
                const result = await response.json();
                
                if (!result.success) {
                    throw new Error(result.error || 'Failed to load chart');
                }
                
                // Render chart
                Plotly.newPlot('chart', result.chart.data, result.chart.layout, {
                    responsive: true,
                    displayModeBar: true,
                    displaylogo: false
                });
                
                // Update stats
                if (result.stats) {
                    updateStats(result.stats);
                }
                
                showSuccess(`Chart loaded successfully (Source: ${result.stats.source})`);
                
            } catch (error) {
                document.getElementById('chart').innerHTML = 
                    '<div id="loading">Error loading chart: ' + error.message + '</div>';
                showError('Failed to load chart: ' + error.message);
            }
        }
        
        function updateStats(stats) {
            const statsHtml = `
                <div class="stat-card">
                    <div class="stat-label">Current Price</div>
                    <div class="stat-value">$${stats.current_price.toFixed(2)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Min Price</div>
                    <div class="stat-value">$${stats.min_price.toFixed(2)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Max Price</div>
                    <div class="stat-value">$${stats.max_price.toFixed(2)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Data Points</div>
                    <div class="stat-value">${stats.data_points}</div>
                </div>
            `;
            document.getElementById('statsRow').innerHTML = statsHtml;
        }
        
        // Test connection on load
        window.addEventListener('load', () => {
            testConnection();
        });
    </script>
</body>
</html>
    '''
    return render_template_string(html)

@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    print("=" * 70)
    print("STOCK ANALYSIS SYSTEM - WINDOWS 11 FIXED")
    print("=" * 70)
    print("Starting server at: http://localhost:8000")
    print("=" * 70)
    print("NOTE: If APIs fail, test data will be used automatically")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=8000, debug=False)