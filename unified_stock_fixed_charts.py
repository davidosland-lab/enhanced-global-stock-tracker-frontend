#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Stock Analysis System - FIXED CHART RENDERING
Complete rewrite of chart rendering to fix all display issues
"""

import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

# Ensure UTF-8 encoding for Windows
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from datetime import datetime, timedelta
import time

# Data libraries
import yfinance as yf
import pandas as pd
import numpy as np
import requests

# Charting
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ML libraries
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

print("=" * 70)
print("UNIFIED STOCK ANALYSIS - FIXED CHARTS VERSION")
print("=" * 70)

ALPHA_VANTAGE_KEY = "68ZFANK047DL0KSR"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Australian stocks
AUSTRALIAN_STOCKS = ['CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'WOW', 'RIO', 'FMG']

def ensure_australian_suffix(symbol):
    """Add .AX suffix to Australian stocks if missing"""
    symbol = symbol.upper().strip()
    base = symbol.replace('.AX', '')
    if base in AUSTRALIAN_STOCKS and not symbol.endswith('.AX'):
        return f"{symbol}.AX"
    return symbol

def calculate_technical_indicators(df):
    """Calculate technical indicators"""
    indicators = {}
    
    if len(df) < 3:
        return indicators
    
    close_prices = df['Close'].values
    
    # RSI
    if len(close_prices) >= 14:
        delta = pd.Series(close_prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 0.0001)  # Avoid division by zero
        rsi_value = 100 - (100 / (1 + rs.iloc[-1]))
        indicators['RSI'] = float(rsi_value) if not np.isnan(rsi_value) else 50.0
    
    # SMA
    if len(close_prices) >= 20:
        indicators['SMA_20'] = float(pd.Series(close_prices).rolling(window=20).mean().iloc[-1])
    
    # EMA
    if len(close_prices) >= 12:
        indicators['EMA_12'] = float(pd.Series(close_prices).ewm(span=12, adjust=False).mean().iloc[-1])
    
    # Bollinger Bands
    if len(close_prices) >= 20:
        sma = pd.Series(close_prices).rolling(window=20).mean()
        std = pd.Series(close_prices).rolling(window=20).std()
        indicators['BB_upper'] = float(sma.iloc[-1] + (std.iloc[-1] * 2))
        indicators['BB_middle'] = float(sma.iloc[-1])
        indicators['BB_lower'] = float(sma.iloc[-1] - (std.iloc[-1] * 2))
    
    # ATR
    if 'High' in df and 'Low' in df and len(df) >= 14:
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        indicators['ATR'] = float(true_range.rolling(14).mean().iloc[-1])
    
    return indicators

def fetch_yahoo_data(symbol, period='1mo', interval=None):
    """Fetch data from Yahoo Finance - FIXED VERSION"""
    try:
        symbol = ensure_australian_suffix(symbol)
        print(f"Fetching {symbol} for period {period}, interval {interval}")
        
        # Use yfinance Ticker object
        ticker = yf.Ticker(symbol)
        
        # For intraday data
        if interval and period in ['1d', '5d', '1wk']:
            df = ticker.history(period=period, interval=interval, prepost=False, actions=False)
        else:
            # For daily data - ensure we get OHLC data
            df = ticker.history(period=period, interval='1d', prepost=False, actions=False)
        
        if df.empty:
            print(f"No data returned for {symbol}")
            return None
        
        # Drop unnecessary columns if they exist
        cols_to_drop = ['Dividends', 'Stock Splits']
        for col in cols_to_drop:
            if col in df.columns:
                df = df.drop(columns=[col])
        
        # Verify OHLC data is present and valid
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in df.columns:
                print(f"Warning: {col} column missing")
                return None
        
        # Ensure OHLC values are floats
        for col in ['Open', 'High', 'Low', 'Close']:
            df[col] = df[col].astype(float)
        
        print(f"Fetched {len(df)} rows from {df.index[0]} to {df.index[-1]}")
        print(f"OHLC spread check - Mean H-L: {(df['High'] - df['Low']).mean():.2f}")
        return df
        
    except Exception as e:
        print(f"Error fetching Yahoo data: {e}")
        return None

def generate_ml_predictions(df, symbol):
    """Generate ML predictions - simplified and fixed"""
    if not ML_AVAILABLE or len(df) < 20:
        return None
    
    try:
        # Prepare features
        df = df.copy()
        df['Returns'] = df['Close'].pct_change().fillna(0).clip(-0.1, 0.1)
        df['MA5'] = df['Close'].rolling(window=5, min_periods=1).mean()
        df['MA20'] = df['Close'].rolling(window=20, min_periods=1).mean()
        df['Volume_Ratio'] = (df['Volume'] / df['Volume'].rolling(window=5, min_periods=1).mean()).fillna(1)
        
        df = df.fillna(method='ffill').fillna(0)
        
        # Features
        feature_cols = ['Returns', 'MA5', 'MA20', 'Volume_Ratio']
        X = df[feature_cols].iloc[:-1].values
        y = df['Close'].iloc[1:].values
        
        if len(X) < 10:
            return None
        
        # Split data
        split_idx = int(len(X) * 0.8)
        X_train = X[:split_idx]
        y_train = y[:split_idx]
        
        # Scale and train
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        
        model = RandomForestRegressor(n_estimators=50, max_depth=3, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Predict
        last_features = scaler.transform(X[-1:])
        predicted_price = float(model.predict(last_features)[0])
        current_price = float(df['Close'].iloc[-1])
        
        # Limit prediction to reasonable range (max 5% change)
        max_change = current_price * 0.05
        predicted_price = np.clip(predicted_price, current_price - max_change, current_price + max_change)
        
        return {
            'current_price': current_price,
            'predicted_price': predicted_price,
            'change_percent': ((predicted_price - current_price) / current_price) * 100,
            'confidence': 65.0,
            'model': 'RandomForest',
            'symbol': symbol
        }
    except Exception as e:
        print(f"ML prediction error: {e}")
        return None

def create_plotly_chart(df, symbol, indicators=None, chart_type='candlestick'):
    """Create Plotly chart - FIXED CANDLESTICK RENDERING"""
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f'{symbol} Stock Price', 'Volume', 'RSI'),
        row_heights=[0.6, 0.2, 0.2]
    )
    
    # Main price chart
    if chart_type == 'candlestick' and all(col in df.columns for col in ['Open', 'High', 'Low', 'Close']):
        # Ensure data is properly formatted for candlesticks
        candlestick_trace = go.Candlestick(
            x=df.index,
            open=df['Open'].values,
            high=df['High'].values,
            low=df['Low'].values, 
            close=df['Close'].values,
            name='OHLC',
            increasing=dict(line=dict(color='#00CC00', width=1)),
            decreasing=dict(line=dict(color='#FF0000', width=1)),
            showlegend=False
        )
        fig.add_trace(candlestick_trace, row=1, col=1)
    elif chart_type == 'area':
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Close'],
                mode='lines',
                name='Close Price',
                fill='tozeroy',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )
    else:  # Line chart (default)
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )
    
    # Add SMA if enough data
    if len(df) >= 20 and chart_type != 'candlestick':
        sma20 = df['Close'].rolling(window=20).mean()
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=sma20,
                mode='lines',
                name='SMA 20',
                line=dict(color='orange', width=1, dash='dash')
            ),
            row=1, col=1
        )
    
    # Volume chart
    if 'Volume' in df.columns:
        colors = ['red' if i > 0 and df['Close'].iloc[i] < df['Close'].iloc[i-1] else 'green' 
                  for i in range(len(df))]
        colors[0] = 'gray'  # First bar
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='Volume',
                marker_color=colors,
                showlegend=False
            ),
            row=2, col=1
        )
    
    # RSI chart
    if len(df) >= 14:
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / (loss + 0.0001)
        rsi = 100 - (100 / (1 + rs))
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=rsi,
                mode='lines',
                name='RSI',
                line=dict(color='purple', width=2),
                showlegend=False
            ),
            row=3, col=1
        )
        
        # Add RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.3, row=3, col=1)
        fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.3, row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.3, row=3, col=1)
    
    # Update layout with proper configuration for candlesticks
    fig.update_layout(
        title=f"{symbol} Stock Analysis",
        height=800,
        showlegend=True,
        hovermode='x unified',
        template='plotly',  # Use default template for better candlestick display
        xaxis_rangeslider_visible=False,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Update axes with proper configuration
    fig.update_xaxes(
        type='date',
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all", label="All")
            ])
        ),
        row=1, col=1
    )
    
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="RSI", range=[0, 100], row=3, col=1)
    fig.update_xaxes(title_text="Date", row=3, col=1)
    
    return fig

@app.route('/favicon.ico')
def favicon():
    return Response(status=204)

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get stock data API endpoint"""
    try:
        period = request.args.get('period', '1mo')
        interval = request.args.get('interval', None)
        
        # Fetch data
        df = fetch_yahoo_data(symbol, period, interval)
        
        if df is None or df.empty:
            return jsonify({'error': f'No data found for {symbol}'}), 404
        
        # Calculate indicators
        indicators = calculate_technical_indicators(df)
        
        # Generate predictions
        prediction = generate_ml_predictions(df, ensure_australian_suffix(symbol))
        
        # Prepare response
        response_data = {
            'symbol': ensure_australian_suffix(symbol),
            'dates': df.index.strftime('%Y-%m-%d %H:%M' if interval else '%Y-%m-%d').tolist(),
            'prices': df['Close'].tolist(),
            'open': df['Open'].tolist() if 'Open' in df else [],
            'high': df['High'].tolist() if 'High' in df else [],
            'low': df['Low'].tolist() if 'Low' in df else [],
            'volume': df['Volume'].tolist() if 'Volume' in df else [],
            'indicators': indicators,
            'prediction': prediction,
            'data_points': len(df),
            'interval': interval,
            'source': 'Yahoo Finance',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/plotly-chart', methods=['POST'])
def generate_plotly_chart_api():
    """Generate Plotly chart API"""
    try:
        data = request.json
        symbol = data.get('symbol', 'STOCK')
        period = data.get('period', '1mo')
        interval = data.get('interval', None)
        chart_type = data.get('chart_type', 'candlestick')
        
        print(f"Chart request: {symbol}, {period}, {interval}, {chart_type}")
        
        # Fetch data
        df = fetch_yahoo_data(symbol, period, interval)
        
        if df is None:
            return jsonify({'error': 'No data available'}), 404
        
        # Calculate indicators
        indicators = calculate_technical_indicators(df)
        
        # Create chart
        fig = create_plotly_chart(df, ensure_australian_suffix(symbol), indicators, chart_type)
        
        # Convert to JSON
        chart_json = fig.to_json()
        
        return jsonify({
            'chart_data': json.loads(chart_json),
            'success': True,
            'chart_type': chart_type
        })
        
    except Exception as e:
        print(f"Chart generation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chart/<symbol>')
def chart_page(symbol):
    """Standalone chart page"""
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>{symbol} Chart</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body {{ margin: 0; padding: 10px; font-family: Arial; }}
        .controls {{ position: fixed; top: 10px; right: 10px; background: white; padding: 10px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); z-index: 1000; }}
        select, button {{ padding: 8px; margin: 5px; }}
        button {{ background: #4CAF50; color: white; border: none; cursor: pointer; }}
        #chart {{ width: 100%; height: calc(100vh - 20px); }}
    </style>
</head>
<body>
    <div class="controls">
        <select id="period">
            <option value="1d">1 Day</option>
            <option value="5d">5 Days</option>
            <option value="1mo" selected>1 Month</option>
            <option value="3mo">3 Months</option>
            <option value="6mo">6 Months</option>
            <option value="1y">1 Year</option>
            <option value="5y">5 Years</option>
        </select>
        <select id="chartType">
            <option value="candlestick">Candlestick</option>
            <option value="line">Line</option>
            <option value="area">Area</option>
        </select>
        <button onclick="updateChart()">Update</button>
    </div>
    <div id="chart"></div>
    <script>
        async function loadChart() {{
            const period = document.getElementById('period').value;
            const chartType = document.getElementById('chartType').value;
            
            const response = await fetch('/api/plotly-chart', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    symbol: '{symbol}',
                    period: period,
                    chart_type: chartType
                }})
            }});
            
            const data = await response.json();
            if (data.success) {{
                Plotly.newPlot('chart', data.chart_data.data, data.chart_data.layout, {{responsive: true}});
            }}
        }}
        
        function updateChart() {{ loadChart(); }}
        loadChart();
    </script>
</body>
</html>'''

@app.route('/')
def index():
    """Main page"""
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Stock Analysis - Fixed</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body { font-family: Arial; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .main { display: grid; grid-template-columns: 350px 1fr; gap: 20px; }
        .panel { background: white; padding: 20px; border-radius: 10px; }
        input, select, button { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #4CAF50; color: white; cursor: pointer; }
        button:hover { background: #45a049; }
        .chart-btn { background: #2196F3; }
        .new-window-btn { background: #FF9800; }
        #chart { min-height: 500px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Stock Analysis System - Fixed Charts</h1>
            <p>Real-time data with working chart rendering</p>
        </div>
        
        <div class="main">
            <div class="panel">
                <h3>Controls</h3>
                <input type="text" id="symbol" placeholder="Stock Symbol" value="CBA">
                
                <select id="period">
                    <option value="1d">1 Day</option>
                    <option value="5d">5 Days</option>
                    <option value="1mo" selected>1 Month</option>
                    <option value="3mo">3 Months</option>
                    <option value="6mo">6 Months</option>
                    <option value="1y">1 Year</option>
                    <option value="5y">5 Years</option>
                </select>
                
                <select id="interval" style="display:none;">
                    <option value="1m">1 Minute</option>
                    <option value="5m" selected>5 Minutes</option>
                    <option value="15m">15 Minutes</option>
                    <option value="30m">30 Minutes</option>
                    <option value="1h">1 Hour</option>
                </select>
                
                <select id="chartType">
                    <option value="candlestick">Candlestick</option>
                    <option value="line">Line</option>
                    <option value="area">Area</option>
                </select>
                
                <button onclick="fetchData()">Get Data</button>
                <button class="chart-btn" onclick="generateChart()">Generate Chart</button>
                <button class="new-window-btn" onclick="openNewWindow()">Open in New Window</button>
                
                <div id="indicators" style="margin-top: 20px;"></div>
                <div id="prediction" style="margin-top: 20px;"></div>
            </div>
            
            <div class="panel">
                <div id="chart"></div>
            </div>
        </div>
    </div>
    
    <script>
        let currentData = null;
        
        // Show/hide interval selector
        document.getElementById('period').addEventListener('change', function() {
            const interval = document.getElementById('interval');
            interval.style.display = (this.value === '1d' || this.value === '5d') ? 'block' : 'none';
        });
        
        async function fetchData() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            let url = `/api/stock/${symbol}?period=${period}`;
            
            if (period === '1d' || period === '5d') {
                const interval = document.getElementById('interval').value;
                url += `&interval=${interval}`;
            }
            
            const response = await fetch(url);
            currentData = await response.json();
            
            if (currentData.indicators) {
                let html = '<h4>Indicators</h4>';
                for (const [key, value] of Object.entries(currentData.indicators)) {
                    html += `<p>${key}: ${value.toFixed(2)}</p>`;
                }
                document.getElementById('indicators').innerHTML = html;
            }
            
            if (currentData.prediction) {
                const pred = currentData.prediction;
                document.getElementById('prediction').innerHTML = `
                    <h4>ML Prediction</h4>
                    <p>Current: $${pred.current_price.toFixed(2)}</p>
                    <p>Predicted: $${pred.predicted_price.toFixed(2)}</p>
                    <p>Change: ${pred.change_percent.toFixed(2)}%</p>
                `;
            }
        }
        
        async function generateChart() {
            if (!currentData) {
                alert('Please fetch data first');
                return;
            }
            
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            const chartType = document.getElementById('chartType').value;
            let interval = null;
            
            if (period === '1d' || period === '5d') {
                interval = document.getElementById('interval').value;
            }
            
            const response = await fetch('/api/plotly-chart', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    symbol: symbol,
                    period: period,
                    interval: interval,
                    chart_type: chartType
                })
            });
            
            const result = await response.json();
            if (result.success) {
                Plotly.newPlot('chart', result.chart_data.data, result.chart_data.layout, {responsive: true});
            }
        }
        
        function openNewWindow() {
            const symbol = document.getElementById('symbol').value;
            window.open(`/chart/${symbol}`, '_blank');
        }
    </script>
</body>
</html>'''

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("Starting Fixed Chart Server")
    print("=" * 70)
    print("Server URL: http://localhost:8000")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=8000, debug=False)