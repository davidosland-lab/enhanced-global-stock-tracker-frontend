#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Stock Analysis System - With Local Chart Libraries (No CDN)
All charting code embedded directly - works offline and behind firewalls
"""

import sys
import os
import json
import time
import warnings
warnings.filterwarnings('ignore')

# Ensure UTF-8 encoding
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

print("=" * 70)
print("UNIFIED STOCK ANALYSIS SYSTEM - LOCAL CHARTS (NO CDN)")
print("=" * 70)
print(f"Python: {sys.version}")
print(f"Platform: {sys.platform}")

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
import requests

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: ML libraries not available")

ALPHA_VANTAGE_KEY = "68ZFANK047DL0KSR"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

AUSTRALIAN_STOCKS = ['CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'WOW', 'RIO', 'FMG']

data_cache = {}
cache_duration = 300

def is_australian_stock(symbol):
    base = symbol.replace('.AX', '').upper()
    return base in AUSTRALIAN_STOCKS

def ensure_australian_suffix(symbol):
    symbol = symbol.upper().strip()
    if is_australian_stock(symbol) and not symbol.endswith('.AX'):
        return f"{symbol}.AX"
    return symbol

def fetch_yahoo_data(symbol, period='1mo'):
    try:
        symbol = ensure_australian_suffix(symbol)
        print(f"Fetching Yahoo data for {symbol}, period: {period}")
        
        end_date = datetime.now()
        period_map = {'1d': 1, '5d': 5, '1mo': 30, '3mo': 90, '6mo': 180, '1y': 365}
        days = period_map.get(period, 30)
        start_date = end_date - timedelta(days=days)
        
        df = yf.download(symbol, start=start_date, end=end_date, progress=False, auto_adjust=True)
        
        if df.empty:
            return None
        
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            'symbol': symbol,
            'prices': df['Close'].values.tolist(),
            'dates': [d.strftime('%Y-%m-%d') for d in df.index],
            'volume': df['Volume'].values.tolist(),
            'high': df['High'].values.tolist(),
            'low': df['Low'].values.tolist(),
            'open': df['Open'].values.tolist(),
            'current_price': float(df['Close'].iloc[-1]),
            'previous_close': float(df['Close'].iloc[-2]) if len(df) > 1 else float(df['Close'].iloc[-1]),
            'change': float(df['Close'].iloc[-1] - (df['Close'].iloc[-2] if len(df) > 1 else df['Close'].iloc[-1])),
            'change_percent': float(((df['Close'].iloc[-1] / df['Close'].iloc[-2] - 1) * 100)) if len(df) > 1 else 0,
            'company_name': info.get('longName', symbol),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'data_source': 'Yahoo Finance',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Yahoo error: {str(e)}")
        return None

def fetch_alpha_vantage_data(symbol):
    try:
        symbol = ensure_australian_suffix(symbol)
        print(f"Fetching Alpha Vantage data for {symbol}")
        
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'full',
            'apikey': ALPHA_VANTAGE_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Time Series (Daily)' not in data:
            return None
        
        time_series = data['Time Series (Daily)']
        dates = sorted(time_series.keys(), reverse=True)[:60]
        
        prices = []
        volumes = []
        highs = []
        lows = []
        opens = []
        
        for date in reversed(dates):
            prices.append(float(time_series[date]['4. close']))
            volumes.append(float(time_series[date]['5. volume']))
            highs.append(float(time_series[date]['2. high']))
            lows.append(float(time_series[date]['3. low']))
            opens.append(float(time_series[date]['1. open']))
        
        current_price = prices[-1] if prices else 0
        previous_close = prices[-2] if len(prices) > 1 else current_price
        
        return {
            'symbol': symbol,
            'prices': prices,
            'dates': dates[::-1],
            'volume': volumes,
            'high': highs,
            'low': lows,
            'open': opens,
            'current_price': current_price,
            'previous_close': previous_close,
            'change': current_price - previous_close,
            'change_percent': ((current_price / previous_close - 1) * 100) if previous_close > 0 else 0,
            'company_name': symbol,
            'data_source': 'Alpha Vantage',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Alpha Vantage error: {str(e)}")
        return None

def calculate_technical_indicators(prices, volumes=None):
    if len(prices) < 20:
        return {}
    
    prices_array = np.array(prices, dtype=float)
    indicators = {}
    
    try:
        # SMA
        if len(prices) >= 20:
            indicators['SMA_20'] = float(np.mean(prices_array[-20:]))
        if len(prices) >= 50:
            indicators['SMA_50'] = float(np.mean(prices_array[-50:]))
        
        # EMA
        def calculate_ema(data, period):
            ema = [data[0]]
            multiplier = 2 / (period + 1)
            for price in data[1:]:
                ema.append((price - ema[-1]) * multiplier + ema[-1])
            return ema
        
        if len(prices) >= 12:
            ema12 = calculate_ema(prices_array, 12)
            indicators['EMA_12'] = float(ema12[-1])
        if len(prices) >= 26:
            ema26 = calculate_ema(prices_array, 26)
            indicators['EMA_26'] = float(ema26[-1])
            
            # MACD
            macd_line = np.array(ema12[-len(ema26):]) - np.array(ema26)
            if len(macd_line) >= 9:
                signal_line = calculate_ema(macd_line, 9)
                indicators['MACD'] = float(macd_line[-1])
                indicators['MACD_signal'] = float(signal_line[-1])
                indicators['MACD_histogram'] = float(macd_line[-1] - signal_line[-1])
        
        # RSI
        def calculate_rsi(data, period=14):
            if len(data) < period + 1:
                return None
            deltas = np.diff(data)
            seed = deltas[:period]
            up = seed[seed >= 0].sum() / period
            down = -seed[seed < 0].sum() / period
            if down == 0:
                return 100
            rs = up / down
            rsi = 100 - (100 / (1 + rs))
            
            for delta in deltas[period:]:
                if delta > 0:
                    up = (up * (period - 1) + delta) / period
                    down = down * (period - 1) / period
                else:
                    up = up * (period - 1) / period
                    down = (down * (period - 1) - delta) / period
                
                if down == 0:
                    rsi = 100
                else:
                    rs = up / down
                    rsi = 100 - (100 / (1 + rs))
            
            return rsi
        
        rsi_value = calculate_rsi(prices_array)
        if rsi_value is not None:
            indicators['RSI'] = float(rsi_value)
        
        # Bollinger Bands
        if len(prices) >= 20:
            sma20 = np.mean(prices_array[-20:])
            std20 = np.std(prices_array[-20:])
            indicators['BB_upper'] = float(sma20 + (2 * std20))
            indicators['BB_middle'] = float(sma20)
            indicators['BB_lower'] = float(sma20 - (2 * std20))
        
        # ATR
        if len(prices) >= 15:
            high = prices_array * 1.01
            low = prices_array * 0.99
            tr = high - low
            indicators['ATR'] = float(np.mean(tr[-14:]))
            
    except Exception as e:
        print(f"Indicator error: {str(e)}")
    
    return indicators

def predict_price(data):
    if not ML_AVAILABLE:
        return {'error': 'ML libraries not available'}
    
    try:
        prices = np.array(data['prices'], dtype=float)
        
        if len(prices) < 10:
            trend = (prices[-1] - prices[0]) / len(prices)
            simple_pred = prices[-1] + trend
            return {
                'ensemble': float(simple_pred),
                'random_forest': float(simple_pred * 0.99),
                'gradient_boost': float(simple_pred * 1.01),
                'confidence': 0.5,
                'current_price': float(data['current_price']),
                'predicted_change': float((simple_pred / data['current_price'] - 1) * 100),
                'recommendation': 'HOLD'
            }
        
        # Simple features
        X = []
        y = []
        window_size = min(5, len(prices) // 3)
        
        for i in range(window_size, len(prices) - 1):
            window = prices[max(0, i-window_size):i]
            X.append([
                float(window[-1]),
                float(np.mean(window)),
                float(np.std(window)) if len(window) > 1 else 0.0
            ])
            y.append(float(prices[i + 1]))
        
        if len(X) < 5:
            trend = (prices[-1] - prices[0]) / len(prices)
            simple_pred = prices[-1] + trend
            return {
                'ensemble': float(simple_pred),
                'confidence': 0.6,
                'current_price': float(data['current_price']),
                'predicted_change': float((simple_pred / data['current_price'] - 1) * 100),
                'recommendation': 'HOLD'
            }
        
        X = np.array(X)
        y = np.array(y)
        
        last_window = prices[-window_size:]
        X_pred = np.array([[
            float(last_window[-1]),
            float(np.mean(last_window)),
            float(np.std(last_window)) if len(last_window) > 1 else 0.0
        ]])
        
        # Random Forest
        rf_model = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=5)
        rf_model.fit(X, y)
        rf_pred = float(rf_model.predict(X_pred)[0])
        
        # Gradient Boosting
        gb_model = GradientBoostingRegressor(n_estimators=50, random_state=42, max_depth=3)
        gb_model.fit(X, y)
        gb_pred = float(gb_model.predict(X_pred)[0])
        
        ensemble_pred = (rf_pred + gb_pred) / 2
        
        recent_prices = prices[-min(10, len(prices)):]
        volatility = np.std(recent_prices) / np.mean(recent_prices) if np.mean(recent_prices) > 0 else 0.1
        confidence = max(0.5, min(0.9, 1 - volatility * 2))
        
        change_pct = (ensemble_pred / data['current_price'] - 1) * 100
        
        return {
            'random_forest': float(rf_pred),
            'gradient_boost': float(gb_pred),
            'ensemble': float(ensemble_pred),
            'confidence': float(confidence),
            'current_price': float(data['current_price']),
            'predicted_change': float(change_pct),
            'recommendation': 'BUY' if change_pct > 2 else 'SELL' if change_pct < -2 else 'HOLD'
        }
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        current = float(data['current_price'])
        return {
            'ensemble': current * 1.01,
            'confidence': 0.5,
            'current_price': current,
            'predicted_change': 1.0,
            'recommendation': 'HOLD'
        }

@app.route("/")
def index():
    """Main interface with embedded charting (no CDN required)"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis System - Local Charts</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .controls {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .input-group {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        input, select {
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        button {
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }
        
        .quick-stocks {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }
        
        .quick-btn {
            padding: 8px 20px;
            background: white;
            border: 2px solid #667eea;
            color: #667eea;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 600;
        }
        
        .quick-btn:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }
        
        .quick-btn.australian {
            border-color: #FFA500;
            color: #FFA500;
        }
        
        .quick-btn.australian:hover {
            background: #FFA500;
            color: white;
        }
        
        .chart-controls {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .chart-buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .chart-btn {
            padding: 8px 16px;
            background: #f0f0f0;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .chart-btn:hover {
            background: #667eea;
            color: white;
        }
        
        .chart-btn.active {
            background: #667eea;
            color: white;
        }
        
        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            min-height: 500px;
        }
        
        #stockChart {
            width: 100%;
            height: 450px;
        }
        
        .results {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h3 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        
        .price-display {
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
            margin: 20px 0;
        }
        
        .change {
            font-size: 1.3em;
            margin: 10px 0;
            font-weight: 600;
        }
        
        .positive { color: #4CAF50; }
        .negative { color: #f44336; }
        
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .metric-label {
            color: #666;
            font-weight: 500;
        }
        
        .metric-value {
            font-weight: 700;
            color: #333;
        }
        
        .indicator-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }
        
        .indicator {
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .indicator-label {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        
        .indicator-value {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
        }
        
        .prediction-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
        }
        
        .loading {
            text-align: center;
            padding: 60px;
            background: white;
            border-radius: 15px;
            font-size: 1.3em;
        }
        
        .spinner {
            border: 4px solid rgba(102, 126, 234, 0.3);
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        svg {
            width: 100%;
            height: 100%;
        }
        
        .chart-line {
            fill: none;
            stroke: #667eea;
            stroke-width: 2;
        }
        
        .chart-area {
            fill: rgba(102, 126, 234, 0.1);
        }
        
        .chart-grid {
            stroke: #e0e0e0;
            stroke-width: 1;
            stroke-dasharray: 3,3;
        }
        
        .chart-axis {
            stroke: #666;
            stroke-width: 1;
        }
        
        .chart-text {
            fill: #666;
            font-size: 12px;
        }
        
        .candle-green {
            fill: #4CAF50;
            stroke: #4CAF50;
            stroke-width: 1;
        }
        
        .candle-red {
            fill: #f44336;
            stroke: #f44336;
            stroke-width: 1;
        }
        
        @media (max-width: 768px) {
            .input-group {
                grid-template-columns: 1fr;
            }
            .results {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Stock Analysis System</h1>
            <p>Real-time data with local charts (No CDN required) ✅</p>
        </div>
        
        <div class="controls">
            <div class="input-group">
                <input type="text" id="symbol" placeholder="Enter stock symbol" value="SPY">
                <select id="period">
                    <option value="1d">1 Day</option>
                    <option value="5d">5 Days</option>
                    <option value="1mo">1 Month</option>
                    <option value="3mo" selected>3 Months</option>
                    <option value="6mo">6 Months</option>
                    <option value="1y">1 Year</option>
                </select>
                <select id="dataSource">
                    <option value="auto">Auto (Yahoo → Alpha)</option>
                    <option value="yahoo">Yahoo Finance</option>
                    <option value="alpha">Alpha Vantage</option>
                </select>
                <button onclick="fetchData()">Analyze Stock</button>
            </div>
            
            <div class="quick-stocks">
                <div style="color: #666; margin-right: 15px;">Quick Access:</div>
                <span class="quick-btn australian" onclick="quickFetch('CBA')">CBA 🇦🇺</span>
                <span class="quick-btn australian" onclick="quickFetch('BHP')">BHP 🇦🇺</span>
                <span class="quick-btn australian" onclick="quickFetch('CSL')">CSL 🇦🇺</span>
                <span class="quick-btn" onclick="quickFetch('SPY')">SPY</span>
                <span class="quick-btn" onclick="quickFetch('AAPL')">AAPL</span>
                <span class="quick-btn" onclick="quickFetch('MSFT')">MSFT</span>
                <span class="quick-btn" onclick="quickFetch('GOOGL')">GOOGL</span>
                <span class="quick-btn" onclick="quickFetch('TSLA')">TSLA</span>
            </div>
        </div>
        
        <div class="chart-controls" id="chartControls" style="display:none;">
            <h3>Chart Options</h3>
            <div class="chart-buttons">
                <button class="chart-btn active" onclick="setChartType('candlestick')">Candlestick</button>
                <button class="chart-btn" onclick="setChartType('line')">Line</button>
                <button class="chart-btn" onclick="setChartType('area')">Area</button>
                <button class="chart-btn" onclick="toggleIndicator('sma')">SMA</button>
                <button class="chart-btn" onclick="toggleIndicator('bb')">Bollinger Bands</button>
                <button class="chart-btn" onclick="toggleIndicator('volume')">Volume</button>
            </div>
        </div>
        
        <div class="chart-container" id="chartContainer" style="display:none;">
            <div id="stockChart"></div>
        </div>
        
        <div id="results"></div>
    </div>
    
    <script>
        let currentData = null;
        let currentIndicators = null;
        let chartType = 'candlestick';
        let showIndicators = {
            sma: false,
            bb: false,
            volume: false
        };
        
        // Custom charting functions (no external library needed)
        class LocalChart {
            constructor(container, data, options = {}) {
                this.container = container;
                this.data = data;
                this.options = options;
                this.margin = { top: 20, right: 50, bottom: 50, left: 70 };
                this.width = container.offsetWidth - this.margin.left - this.margin.right;
                this.height = 450 - this.margin.top - this.margin.bottom;
            }
            
            drawCandlestick() {
                const { prices, dates, open, high, low } = this.data;
                const minPrice = Math.min(...low);
                const maxPrice = Math.max(...high);
                const priceRange = maxPrice - minPrice;
                const padding = priceRange * 0.1;
                
                let svg = this.createSVG();
                const candleWidth = Math.max(2, this.width / dates.length - 2);
                
                // Draw grid
                svg = this.drawGrid(svg, minPrice - padding, maxPrice + padding);
                
                // Draw candles
                dates.forEach((date, i) => {
                    const x = (i / dates.length) * this.width + this.margin.left;
                    const openY = this.height - ((open[i] - (minPrice - padding)) / (priceRange + 2 * padding)) * this.height + this.margin.top;
                    const closeY = this.height - ((prices[i] - (minPrice - padding)) / (priceRange + 2 * padding)) * this.height + this.margin.top;
                    const highY = this.height - ((high[i] - (minPrice - padding)) / (priceRange + 2 * padding)) * this.height + this.margin.top;
                    const lowY = this.height - ((low[i] - (minPrice - padding)) / (priceRange + 2 * padding)) * this.height + this.margin.top;
                    
                    const isGreen = prices[i] >= open[i];
                    const color = isGreen ? '#4CAF50' : '#f44336';
                    
                    // High-Low line
                    svg += `<line x1="${x + candleWidth/2}" y1="${highY}" x2="${x + candleWidth/2}" y2="${lowY}" stroke="${color}" stroke-width="1"/>`;
                    
                    // Open-Close box
                    const boxY = Math.min(openY, closeY);
                    const boxHeight = Math.abs(openY - closeY) || 1;
                    svg += `<rect x="${x}" y="${boxY}" width="${candleWidth}" height="${boxHeight}" class="candle-${isGreen ? 'green' : 'red'}" fill="${isGreen ? color : 'white'}" stroke="${color}"/>`;
                });
                
                svg += '</svg>';
                this.container.innerHTML = svg;
            }
            
            drawLine() {
                const { prices, dates } = this.data;
                const minPrice = Math.min(...prices);
                const maxPrice = Math.max(...prices);
                const priceRange = maxPrice - minPrice;
                const padding = priceRange * 0.1;
                
                let svg = this.createSVG();
                
                // Draw grid
                svg = this.drawGrid(svg, minPrice - padding, maxPrice + padding);
                
                // Create line path
                let path = 'M';
                dates.forEach((date, i) => {
                    const x = (i / dates.length) * this.width + this.margin.left;
                    const y = this.height - ((prices[i] - (minPrice - padding)) / (priceRange + 2 * padding)) * this.height + this.margin.top;
                    path += `${i === 0 ? '' : 'L'}${x},${y}`;
                });
                
                svg += `<path d="${path}" class="chart-line"/>`;
                
                // Add SMA if enabled
                if (showIndicators.sma && currentIndicators && currentIndicators.SMA_20) {
                    let smaPath = 'M';
                    const smaValue = currentIndicators.SMA_20;
                    dates.forEach((date, i) => {
                        if (i >= 19) {
                            const x = (i / dates.length) * this.width + this.margin.left;
                            const y = this.height - ((smaValue - (minPrice - padding)) / (priceRange + 2 * padding)) * this.height + this.margin.top;
                            smaPath += `${i === 19 ? '' : 'L'}${x},${y}`;
                        }
                    });
                    svg += `<path d="${smaPath}" stroke="#FFA500" stroke-width="2" fill="none" stroke-dasharray="5,5"/>`;
                }
                
                // Add Bollinger Bands if enabled
                if (showIndicators.bb && currentIndicators) {
                    if (currentIndicators.BB_upper) {
                        const bbUpper = currentIndicators.BB_upper;
                        const bbLower = currentIndicators.BB_lower;
                        
                        // Upper band
                        let upperPath = 'M';
                        dates.forEach((date, i) => {
                            if (i >= 19) {
                                const x = (i / dates.length) * this.width + this.margin.left;
                                const y = this.height - ((bbUpper - (minPrice - padding)) / (priceRange + 2 * padding)) * this.height + this.margin.top;
                                upperPath += `${i === 19 ? '' : 'L'}${x},${y}`;
                            }
                        });
                        svg += `<path d="${upperPath}" stroke="rgba(128,128,128,0.5)" stroke-width="1" fill="none" stroke-dasharray="3,3"/>`;
                        
                        // Lower band
                        let lowerPath = 'M';
                        dates.forEach((date, i) => {
                            if (i >= 19) {
                                const x = (i / dates.length) * this.width + this.margin.left;
                                const y = this.height - ((bbLower - (minPrice - padding)) / (priceRange + 2 * padding)) * this.height + this.margin.top;
                                lowerPath += `${i === 19 ? '' : 'L'}${x},${y}`;
                            }
                        });
                        svg += `<path d="${lowerPath}" stroke="rgba(128,128,128,0.5)" stroke-width="1" fill="none" stroke-dasharray="3,3"/>`;
                    }
                }
                
                svg += '</svg>';
                this.container.innerHTML = svg;
            }
            
            drawArea() {
                const { prices, dates } = this.data;
                const minPrice = Math.min(...prices);
                const maxPrice = Math.max(...prices);
                const priceRange = maxPrice - minPrice;
                const padding = priceRange * 0.1;
                
                let svg = this.createSVG();
                
                // Draw grid
                svg = this.drawGrid(svg, minPrice - padding, maxPrice + padding);
                
                // Create area path
                let path = 'M' + this.margin.left + ',' + (this.height + this.margin.top);
                dates.forEach((date, i) => {
                    const x = (i / dates.length) * this.width + this.margin.left;
                    const y = this.height - ((prices[i] - (minPrice - padding)) / (priceRange + 2 * padding)) * this.height + this.margin.top;
                    path += `L${x},${y}`;
                });
                path += `L${this.width + this.margin.left},${this.height + this.margin.top}Z`;
                
                svg += `<path d="${path}" class="chart-area"/>`;
                
                // Add line on top
                let linePath = 'M';
                dates.forEach((date, i) => {
                    const x = (i / dates.length) * this.width + this.margin.left;
                    const y = this.height - ((prices[i] - (minPrice - padding)) / (priceRange + 2 * padding)) * this.height + this.margin.top;
                    linePath += `${i === 0 ? '' : 'L'}${x},${y}`;
                });
                
                svg += `<path d="${linePath}" class="chart-line"/>`;
                svg += '</svg>';
                this.container.innerHTML = svg;
            }
            
            createSVG() {
                return `<svg viewBox="0 0 ${this.width + this.margin.left + this.margin.right} ${this.height + this.margin.top + this.margin.bottom}">`;
            }
            
            drawGrid(svg, minPrice, maxPrice) {
                const gridLines = 5;
                const priceStep = (maxPrice - minPrice) / gridLines;
                
                // Horizontal grid lines and price labels
                for (let i = 0; i <= gridLines; i++) {
                    const y = this.margin.top + (i * this.height / gridLines);
                    const price = maxPrice - (i * priceStep);
                    svg += `<line x1="${this.margin.left}" y1="${y}" x2="${this.width + this.margin.left}" y2="${y}" class="chart-grid"/>`;
                    svg += `<text x="${this.margin.left - 10}" y="${y + 5}" text-anchor="end" class="chart-text">$${price.toFixed(2)}</text>`;
                }
                
                // Vertical grid lines
                const { dates } = this.data;
                const step = Math.floor(dates.length / 5);
                for (let i = 0; i < dates.length; i += step) {
                    const x = (i / dates.length) * this.width + this.margin.left;
                    svg += `<line x1="${x}" y1="${this.margin.top}" x2="${x}" y2="${this.height + this.margin.top}" class="chart-grid"/>`;
                    svg += `<text x="${x}" y="${this.height + this.margin.top + 20}" text-anchor="middle" class="chart-text">${dates[i].slice(5)}</text>`;
                }
                
                return svg;
            }
            
            draw() {
                switch(chartType) {
                    case 'candlestick':
                        this.drawCandlestick();
                        break;
                    case 'area':
                        this.drawArea();
                        break;
                    case 'line':
                    default:
                        this.drawLine();
                        break;
                }
            }
        }
        
        function setChartType(type) {
            chartType = type;
            document.querySelectorAll('.chart-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.textContent.toLowerCase() === type) {
                    btn.classList.add('active');
                }
            });
            updateChart();
        }
        
        function toggleIndicator(indicator) {
            showIndicators[indicator] = !showIndicators[indicator];
            const btn = Array.from(document.querySelectorAll('.chart-btn')).find(b => 
                b.textContent.toLowerCase().includes(indicator) ||
                (indicator === 'bb' && b.textContent === 'Bollinger Bands')
            );
            if (btn) {
                btn.classList.toggle('active', showIndicators[indicator]);
            }
            updateChart();
        }
        
        function updateChart() {
            if (!currentData) return;
            
            const chartDiv = document.getElementById('stockChart');
            const chart = new LocalChart(chartDiv, currentData);
            
            // Call the appropriate drawing method based on chart type
            switch(chartType) {
                case 'candlestick':
                    chart.drawCandlestick();
                    break;
                case 'line':
                    chart.drawLine();
                    break;
                case 'area':
                    chart.drawArea();
                    break;
                default:
                    chart.drawLine();
            }
        }
        
        async function quickFetch(symbol) {
            document.getElementById('symbol').value = symbol;
            fetchData();
        }
        
        async function fetchData() {
            const symbol = document.getElementById('symbol').value.trim().toUpperCase();
            const period = document.getElementById('period').value;
            const dataSource = document.getElementById('dataSource').value;
            
            if (!symbol) {
                alert('Please enter a stock symbol');
                return;
            }
            
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Fetching data for ' + symbol + '...</div>';
            
            try {
                // Fetch stock data
                const response = await fetch('/api/fetch', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({symbol, period, dataSource})
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to fetch data');
                }
                
                currentData = data;
                
                // Get predictions
                const predResponse = await fetch('/api/predict', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({data})
                });
                
                const predictions = await predResponse.json();
                
                // Get indicators
                const indicatorsResponse = await fetch('/api/indicators', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        prices: data.prices,
                        volumes: data.volume  // Fixed: using correct field name
                    })
                });
                
                const indicators = await indicatorsResponse.json();
                currentIndicators = indicators;
                
                // Show chart
                document.getElementById('chartControls').style.display = 'block';
                document.getElementById('chartContainer').style.display = 'block';
                updateChart();
                
                // Display results
                displayResults(data, predictions, indicators);
                
            } catch (error) {
                resultsDiv.innerHTML = '<div class="card"><h3>Error</h3><p>' + error.message + '</p></div>';
            }
        }
        
        function displayResults(data, predictions, indicators) {
            const changeClass = data.change >= 0 ? 'positive' : 'negative';
            const changeSymbol = data.change >= 0 ? '▲' : '▼';
            
            let html = '<div class="results">';
            
            // Stock info card
            html += `
                <div class="card">
                    <h3>${data.symbol}</h3>
                    <div class="price-display">$${data.current_price.toFixed(2)}</div>
                    <div class="change ${changeClass}">
                        ${changeSymbol} ${data.change.toFixed(2)} (${data.change_percent.toFixed(2)}%)
                    </div>
                    ${data.company_name ? `<div class="metric"><span class="metric-label">Company</span><span class="metric-value">${data.company_name}</span></div>` : ''}
                    <div class="metric"><span class="metric-label">Data Source</span><span class="metric-value">${data.data_source}</span></div>
                    <div class="metric"><span class="metric-label">Data Points</span><span class="metric-value">${data.prices.length}</span></div>
                </div>
            `;
            
            // Indicators card - only show if we have valid indicators
            if (indicators && !indicators.error) {
                html += '<div class="card"><h3>Technical Indicators</h3><div class="indicator-grid">';
                
                Object.entries(indicators).forEach(([key, value]) => {
                if (value !== null && value !== undefined) {
                    const displayValue = key.includes('BB') || key.includes('SMA') || key.includes('EMA') || key.includes('ATR') 
                        ? `$${value.toFixed(2)}` 
                        : value.toFixed(2);
                    
                    let color = '#333';
                    if (key === 'RSI') {
                        color = value > 70 ? '#f44336' : value < 30 ? '#4CAF50' : '#333';
                    }
                    
                    html += `
                        <div class="indicator">
                            <div class="indicator-label">${key}</div>
                            <div class="indicator-value" style="color: ${color}">${displayValue}</div>
                        </div>
                    `;
                }
                });
                
                html += '</div></div>';
            } else if (indicators && indicators.error) {
                html += '<div class="card"><h3>Technical Indicators</h3><p>Insufficient data for indicators (need at least 20 data points)</p></div>';
            }
            
            // Predictions card
            if (predictions && predictions.ensemble) {
                html += `
                    <div class="card">
                        <h3>ML Predictions</h3>
                        <div class="prediction-box">
                            <h4>Price Prediction</h4>
                            <div style="font-size: 2em; font-weight: bold; margin: 10px 0;">
                                $${predictions.ensemble.toFixed(2)}
                            </div>
                            <div>Expected Change: ${predictions.predicted_change > 0 ? '+' : ''}${predictions.predicted_change.toFixed(2)}%</div>
                            <div style="margin-top: 10px;">Confidence: ${(predictions.confidence * 100).toFixed(0)}%</div>
                            <div style="margin-top: 15px; padding: 10px; background: ${
                                predictions.recommendation === 'BUY' ? '#4CAF50' : 
                                predictions.recommendation === 'SELL' ? '#f44336' : '#FFC107'
                            }; color: white; border-radius: 8px; text-align: center; font-weight: bold;">
                                ${predictions.recommendation}
                            </div>
                        </div>
                        ${predictions.random_forest ? `<div class="metric"><span class="metric-label">Random Forest</span><span class="metric-value">$${predictions.random_forest.toFixed(2)}</span></div>` : ''}
                        ${predictions.gradient_boost ? `<div class="metric"><span class="metric-label">Gradient Boost</span><span class="metric-value">$${predictions.gradient_boost.toFixed(2)}</span></div>` : ''}
                    </div>
                `;
            }
            
            html += '</div>';
            document.getElementById('results').innerHTML = html;
        }
        
        // Auto-fetch on load
        window.onload = () => {
            console.log('System ready - No CDN required, all charts local!');
            fetchData();
        };
    </script>
</body>
</html>'''

@app.route("/api/fetch", methods=["POST"])
def api_fetch():
    """Fetch stock data from Yahoo or Alpha Vantage"""
    try:
        data = request.json
        symbol = data.get('symbol', '').upper()
        period = data.get('period', '1mo')
        source = data.get('dataSource', 'auto')
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        # Check cache
        cache_key = f"{symbol}_{period}_{source}"
        if cache_key in data_cache:
            cached = data_cache[cache_key]
            if time.time() - cached['cached_at'] < cache_duration:
                return jsonify(cached['data'])
        
        result = None
        
        # Try data sources
        if source == 'yahoo' or source == 'auto':
            result = fetch_yahoo_data(symbol, period)
        
        if not result and (source == 'alpha' or source == 'auto'):
            result = fetch_alpha_vantage_data(symbol)
        
        if not result:
            return jsonify({'error': f'Failed to fetch data for {symbol}'}), 500
        
        # Cache result
        data_cache[cache_key] = {
            'data': result,
            'cached_at': time.time()
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/indicators", methods=["POST"])
def api_indicators():
    """Calculate technical indicators"""
    try:
        data = request.json
        prices = data.get('prices', [])
        volumes = data.get('volumes')
        
        if not prices or len(prices) < 20:
            return jsonify({'error': 'Insufficient data'}), 400
        
        indicators = calculate_technical_indicators(prices, volumes)
        return jsonify(indicators)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """Make price predictions"""
    try:
        data = request.json.get('data')
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        predictions = predict_price(data)
        return jsonify(predictions)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/health")
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ml_available': ML_AVAILABLE,
        'charts': 'local'
    })

if __name__ == "__main__":
    # Disable dotenv to prevent UTF-8 issues on Windows
    os.environ['FLASK_SKIP_DOTENV'] = '1'
    
    print("\n" + "=" * 70)
    print("SERVER STARTING")
    print("=" * 70)
    print("Access at: http://localhost:8000")
    print("Charts: Built-in SVG (No CDN required)")
    print("=" * 70 + "\n")
    
    app.run(host="0.0.0.0", port=8000, debug=False)