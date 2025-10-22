#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Stock Analysis - Intraday with Chart.js (More Reliable)
Fixed version using Chart.js instead of TradingView for better compatibility
"""

import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

# Ensure UTF-8 encoding
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

print("=" * 70)
print("INTRADAY STOCK ANALYSIS - CHART.JS VERSION")
print("=" * 70)

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import time
import yfinance as yf
import pandas as pd
import numpy as np
import requests

# ML libraries
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

ALPHA_VANTAGE_KEY = "68ZFANK047DL0KSR"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

AUSTRALIAN_STOCKS = ['CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'WOW', 'RIO', 'FMG']

data_cache = {}
cache_duration = 60  # 1 minute for intraday

def ensure_australian_suffix(symbol):
    """Add .AX suffix to Australian stocks if missing"""
    symbol = symbol.upper().strip()
    base = symbol.replace('.AX', '')
    if base in AUSTRALIAN_STOCKS and not symbol.endswith('.AX'):
        return f"{symbol}.AX"
    return symbol

def fetch_intraday_data(symbol, interval='5m', period='1d'):
    """Fetch intraday data with minute-level precision"""
    try:
        symbol = ensure_australian_suffix(symbol)
        print(f"Fetching intraday data for {symbol}, interval: {interval}, period: {period}")
        
        ticker = yf.Ticker(symbol)
        
        # Get intraday data
        df = ticker.history(period=period, interval=interval, prepost=True, actions=False)
        
        if df.empty:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            df = yf.download(symbol, start=start_date, end=end_date, interval=interval, 
                           progress=False, auto_adjust=True, prepost=True, threads=True)
        
        if df.empty:
            raise ValueError(f"No intraday data returned for {symbol}")
        
        info = ticker.info
        
        # Get current quote
        try:
            quote = ticker.fast_info
            current_price = quote.get('lastPrice', df['Close'].iloc[-1] if not df.empty else 0)
        except:
            current_price = float(df['Close'].iloc[-1]) if not df.empty else info.get('currentPrice', 0)
        
        # Format timestamps
        if interval in ['1m', '2m', '5m', '15m', '30m', '60m', '90m']:
            timestamps = [d.strftime('%Y-%m-%d %H:%M:%S') for d in df.index]
        else:
            timestamps = [d.strftime('%Y-%m-%d') for d in df.index]
        
        return {
            'symbol': symbol,
            'prices': df['Close'].values.tolist(),
            'dates': timestamps,
            'volume': df['Volume'].values.tolist(),
            'high': df['High'].values.tolist(),
            'low': df['Low'].values.tolist(),
            'open': df['Open'].values.tolist(),
            'current_price': float(current_price),
            'previous_close': info.get('previousClose', float(df['Close'].iloc[0]) if not df.empty else 0),
            'change': float(current_price - info.get('previousClose', current_price)),
            'change_percent': float(((current_price / info.get('previousClose', current_price) - 1) * 100)) if info.get('previousClose', 0) > 0 else 0,
            'company_name': info.get('longName', symbol),
            'day_high': info.get('dayHigh', max(df['High'].values) if not df.empty else 0),
            'day_low': info.get('dayLow', min(df['Low'].values) if not df.empty else 0),
            'bid': info.get('bid', 0),
            'ask': info.get('ask', 0),
            'data_source': 'Yahoo Finance Intraday',
            'interval': interval,
            'timestamp': datetime.now().isoformat(),
            'last_update': datetime.now().strftime('%H:%M:%S')
        }
        
    except Exception as e:
        print(f"Intraday fetch error: {str(e)}")
        return None

@app.route("/")
def index():
    """Main interface with Chart.js"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Intraday Stock Analysis - Real-Time</title>
    <!-- Chart.js for reliable charting -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <!-- Chart.js Financial plugin for candlestick charts -->
    <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial@0.1.1/dist/chartjs-chart-financial.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .header h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3em;
            margin-bottom: 10px;
        }
        
        .live-ticker {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            margin-top: 15px;
            display: flex;
            align-items: center;
            gap: 20px;
            font-size: 1.1em;
        }
        
        .live-price {
            font-size: 1.4em;
            font-weight: bold;
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
            grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        input, select {
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
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
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }
        
        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            position: relative;
        }
        
        .chart-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .chart-btn {
            padding: 8px 16px;
            background: white;
            border: 1px solid #ddd;
            color: #333;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .chart-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        .auto-refresh {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 15px;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 10px;
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
            font-weight: 600;
        }
        
        .quick-btn:hover {
            background: #667eea;
            color: white;
        }
        
        .market-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            padding: 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .market-stat {
            text-align: center;
            padding: 10px;
        }
        
        .market-stat-value {
            color: white;
            font-size: 1.4em;
            font-weight: bold;
        }
        
        .loading {
            text-align: center;
            padding: 60px;
            color: white;
            font-size: 1.3em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Intraday Stock Analysis</h1>
            <p>Real-time data with Chart.js for maximum reliability</p>
            
            <div class="live-ticker" id="liveTicker" style="display:none;">
                <span>Current Price:</span>
                <span class="live-price" id="livePrice">-</span>
                <span id="liveChange">-</span>
                <span id="lastUpdate">Last Update: -</span>
            </div>
            
            <div class="market-info" id="marketInfo" style="display:none;">
                <div class="market-stat">
                    <div>Day High</div>
                    <div class="market-stat-value" id="dayHigh">-</div>
                </div>
                <div class="market-stat">
                    <div>Day Low</div>
                    <div class="market-stat-value" id="dayLow">-</div>
                </div>
                <div class="market-stat">
                    <div>Volume</div>
                    <div class="market-stat-value" id="volumeToday">-</div>
                </div>
                <div class="market-stat">
                    <div>Bid/Ask</div>
                    <div class="market-stat-value" id="bidAsk">-</div>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <div class="input-group">
                <input type="text" id="symbol" placeholder="Stock symbol" value="CBA">
                <select id="period">
                    <option value="1d" selected>Intraday</option>
                    <option value="5d">5 Days</option>
                    <option value="1mo">1 Month</option>
                </select>
                <select id="interval">
                    <option value="1m">1 Minute</option>
                    <option value="5m" selected>5 Minutes</option>
                    <option value="15m">15 Minutes</option>
                    <option value="30m">30 Minutes</option>
                    <option value="60m">1 Hour</option>
                </select>
                <button onclick="fetchData()">📊 Analyze</button>
                <button onclick="toggleAutoRefresh()" id="autoBtn">🔄 Auto-Refresh: OFF</button>
            </div>
            
            <div class="quick-stocks">
                <span class="quick-btn" onclick="quickFetch('CBA')">CBA 🇦🇺</span>
                <span class="quick-btn" onclick="quickFetch('BHP')">BHP 🇦🇺</span>
                <span class="quick-btn" onclick="quickFetch('CSL')">CSL 🇦🇺</span>
                <span class="quick-btn" onclick="quickFetch('AAPL')">AAPL 🇺🇸</span>
                <span class="quick-btn" onclick="quickFetch('MSFT')">MSFT 🇺🇸</span>
                <span class="quick-btn" onclick="quickFetch('TSLA')">TSLA 🇺🇸</span>
            </div>
        </div>
        
        <div class="chart-container" id="chartContainer" style="display:none;">
            <div class="chart-controls">
                <button class="chart-btn active" onclick="setChartType('line')">Line Chart</button>
                <button class="chart-btn" onclick="setChartType('candlestick')">Candlestick</button>
                <button class="chart-btn" onclick="setChartType('bar')">Volume</button>
            </div>
            <canvas id="stockChart"></canvas>
        </div>
        
        <div id="results"></div>
    </div>
    
    <script>
        let currentData = null;
        let stockChart = null;
        let chartType = 'line';
        let autoRefreshTimer = null;
        let autoRefreshEnabled = false;
        
        async function quickFetch(symbol) {
            document.getElementById('symbol').value = symbol;
            fetchData();
        }
        
        async function fetchData() {
            const symbol = document.getElementById('symbol').value.trim().toUpperCase();
            const period = document.getElementById('period').value;
            const interval = document.getElementById('interval').value;
            
            if (!symbol) {
                alert('Please enter a stock symbol');
                return;
            }
            
            document.getElementById('results').innerHTML = '<div class="loading">Loading...</div>';
            
            try {
                const response = await fetch('/api/fetch', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({symbol, period, interval})
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to fetch data');
                }
                
                currentData = data;
                updateDisplay(data);
                drawChart(data);
                
            } catch (error) {
                document.getElementById('results').innerHTML = `<div style="color:white; padding:20px;">Error: ${error.message}</div>`;
            }
        }
        
        function updateDisplay(data) {
            document.getElementById('liveTicker').style.display = 'flex';
            document.getElementById('marketInfo').style.display = 'grid';
            
            document.getElementById('livePrice').textContent = `$${data.current_price.toFixed(2)}`;
            document.getElementById('liveChange').textContent = `${data.change >= 0 ? '▲' : '▼'} ${data.change.toFixed(2)} (${data.change_percent.toFixed(2)}%)`;
            document.getElementById('liveChange').style.color = data.change >= 0 ? '#4CAF50' : '#f44336';
            document.getElementById('lastUpdate').textContent = `Last Update: ${data.last_update || new Date().toLocaleTimeString()}`;
            
            document.getElementById('dayHigh').textContent = `$${(data.day_high || 0).toFixed(2)}`;
            document.getElementById('dayLow').textContent = `$${(data.day_low || 0).toFixed(2)}`;
            document.getElementById('volumeToday').textContent = formatVolume(data.volume ? data.volume.reduce((a,b) => a+b, 0) : 0);
            document.getElementById('bidAsk').textContent = data.bid && data.ask ? `${data.bid.toFixed(2)}/${data.ask.toFixed(2)}` : '-';
        }
        
        function formatVolume(vol) {
            if (vol >= 1000000) return (vol/1000000).toFixed(1) + 'M';
            if (vol >= 1000) return (vol/1000).toFixed(1) + 'K';
            return vol.toString();
        }
        
        function drawChart(data) {
            document.getElementById('chartContainer').style.display = 'block';
            
            const ctx = document.getElementById('stockChart').getContext('2d');
            
            if (stockChart) {
                stockChart.destroy();
            }
            
            const chartConfig = {
                type: chartType === 'candlestick' ? 'candlestick' : chartType === 'bar' ? 'bar' : 'line',
                data: {
                    labels: data.dates,
                    datasets: [{
                        label: data.symbol + ' Price',
                        data: chartType === 'candlestick' && data.open ? 
                            data.dates.map((d, i) => ({
                                x: d,
                                o: data.open[i],
                                h: data.high[i],
                                l: data.low[i],
                                c: data.prices[i]
                            })) :
                            chartType === 'bar' ? data.volume : data.prices,
                        borderColor: chartType === 'line' ? 'rgb(75, 192, 192)' : undefined,
                        backgroundColor: chartType === 'bar' ? 'rgba(75, 192, 192, 0.5)' : 
                                        chartType === 'line' ? 'rgba(75, 192, 192, 0.1)' : undefined,
                        fill: chartType === 'line',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        title: {
                            display: true,
                            text: `${data.symbol} - ${data.interval || '5m'} intervals`
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: chartType === 'bar',
                            title: {
                                display: true,
                                text: chartType === 'bar' ? 'Volume' : 'Price ($)'
                            }
                        },
                        x: {
                            ticks: {
                                maxTicksLimit: 10,
                                autoSkip: true
                            }
                        }
                    }
                }
            };
            
            stockChart = new Chart(ctx, chartConfig);
        }
        
        function setChartType(type) {
            chartType = type;
            document.querySelectorAll('.chart-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            if (currentData) drawChart(currentData);
        }
        
        function toggleAutoRefresh() {
            autoRefreshEnabled = !autoRefreshEnabled;
            const btn = document.getElementById('autoBtn');
            
            if (autoRefreshEnabled) {
                btn.textContent = '🔄 Auto-Refresh: ON';
                btn.style.background = '#4CAF50';
                startAutoRefresh();
            } else {
                btn.textContent = '🔄 Auto-Refresh: OFF';
                btn.style.background = '';
                stopAutoRefresh();
            }
        }
        
        function startAutoRefresh() {
            fetchData();
            autoRefreshTimer = setInterval(fetchData, 30000); // 30 seconds
        }
        
        function stopAutoRefresh() {
            if (autoRefreshTimer) {
                clearInterval(autoRefreshTimer);
                autoRefreshTimer = null;
            }
        }
        
        // Auto-fetch on load
        window.onload = () => fetchData();
    </script>
</body>
</html>"""

@app.route("/api/fetch", methods=["POST"])
def api_fetch():
    """Fetch stock data"""
    try:
        data = request.json
        symbol = data.get('symbol', '').upper()
        period = data.get('period', '1d')
        interval = data.get('interval', '5m')
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        # Check cache
        cache_key = f"{symbol}_{period}_{interval}"
        if cache_key in data_cache:
            cached = data_cache[cache_key]
            if time.time() - cached['cached_at'] < cache_duration:
                return jsonify(cached['data'])
        
        result = fetch_intraday_data(symbol, interval=interval, period=period)
        
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

@app.route("/health")
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'version': 'chartjs-intraday',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == "__main__":
    print("\nServer starting at: http://localhost:8002")
    print("Using Chart.js for reliable charting")
    app.run(host="0.0.0.0", port=8002, debug=False)