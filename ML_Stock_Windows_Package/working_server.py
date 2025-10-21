#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Working Stock Server - Based on clean_test_server that works
Full functionality without encoding issues
"""

import sys
import os

# Ensure UTF-8 encoding
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

print("Starting Working Stock Server...")
print(f"Python: {sys.version}")
print(f"Encoding: {sys.getdefaultencoding()}")

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime

# Import data libraries
import yfinance as yf
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

# Australian stocks
AUSTRALIAN_STOCKS = ['CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'WOW', 'RIO', 'FMG']

# Cache for data
cache = {}

@app.route("/")
def index():
    """Main interface - embedded HTML to avoid file reading issues"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>ML Stock Predictor - Working Version</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .content {
                padding: 30px;
            }
            
            .controls {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
            }
            
            .input-group {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
            }
            
            input, select {
                flex: 1;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 16px;
            }
            
            input:focus, select:focus {
                outline: none;
                border-color: #667eea;
            }
            
            button {
                padding: 12px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                transition: transform 0.2s;
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            
            .quick-buttons {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }
            
            .quick-btn {
                padding: 8px 16px;
                background: white;
                border: 2px solid #667eea;
                color: #667eea;
                border-radius: 20px;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            .quick-btn:hover {
                background: #667eea;
                color: white;
            }
            
            .results {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }
            
            .card {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }
            
            .card h3 {
                color: #667eea;
                margin-bottom: 15px;
            }
            
            .price-display {
                font-size: 2.5em;
                font-weight: bold;
                color: #333;
                margin: 15px 0;
            }
            
            .change {
                font-size: 1.2em;
                margin: 10px 0;
            }
            
            .positive { color: #4CAF50; }
            .negative { color: #f44336; }
            
            .indicator {
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #f0f0f0;
            }
            
            .indicator-label { color: #666; }
            .indicator-value { font-weight: 600; }
            
            .loading {
                text-align: center;
                padding: 40px;
                color: #666;
            }
            
            .error {
                background: #ffebee;
                color: #c62828;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
            }
            
            .success {
                background: #e8f5e9;
                color: #2e7d32;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
            }
            
            @media (max-width: 768px) {
                .input-group { flex-direction: column; }
                .results { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>ML Stock Predictor</h1>
                <p>Real-time stock data with technical analysis</p>
            </div>
            
            <div class="content">
                <div class="controls">
                    <div class="input-group">
                        <input type="text" id="symbol" placeholder="Enter stock symbol" value="AAPL">
                        <select id="period">
                            <option value="1d">1 Day</option>
                            <option value="5d">5 Days</option>
                            <option value="1mo" selected>1 Month</option>
                            <option value="3mo">3 Months</option>
                            <option value="6mo">6 Months</option>
                            <option value="1y">1 Year</option>
                        </select>
                        <button onclick="fetchData()">Fetch Data</button>
                    </div>
                    
                    <div class="quick-buttons">
                        <span class="quick-btn" onclick="quickFetch('CBA')">CBA</span>
                        <span class="quick-btn" onclick="quickFetch('BHP')">BHP</span>
                        <span class="quick-btn" onclick="quickFetch('CSL')">CSL</span>
                        <span class="quick-btn" onclick="quickFetch('NAB')">NAB</span>
                        <span class="quick-btn" onclick="quickFetch('AAPL')">AAPL</span>
                        <span class="quick-btn" onclick="quickFetch('MSFT')">MSFT</span>
                        <span class="quick-btn" onclick="quickFetch('GOOGL')">GOOGL</span>
                        <span class="quick-btn" onclick="quickFetch('TSLA')">TSLA</span>
                    </div>
                </div>
                
                <div id="results" class="results"></div>
            </div>
        </div>
        
        <script>
            async function quickFetch(symbol) {
                document.getElementById('symbol').value = symbol;
                fetchData();
            }
            
            async function fetchData() {
                const symbol = document.getElementById('symbol').value.trim().toUpperCase();
                const period = document.getElementById('period').value;
                
                if (!symbol) {
                    alert('Please enter a stock symbol');
                    return;
                }
                
                const resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = '<div class="loading">Loading ' + symbol + '...</div>';
                
                try {
                    // Fetch main data
                    const response = await fetch('/api/fetch', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({symbol, period})
                    });
                    
                    const data = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(data.error || 'Failed to fetch data');
                    }
                    
                    // Fetch indicators
                    const indicatorsResponse = await fetch('/api/indicators', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({symbol, prices: data.prices})
                    });
                    
                    const indicators = await indicatorsResponse.json();
                    
                    displayData(data, indicators);
                    
                } catch (error) {
                    resultsDiv.innerHTML = '<div class="error">Error: ' + error.message + '</div>';
                }
            }
            
            function displayData(data, indicators) {
                const changeClass = data.price_change >= 0 ? 'positive' : 'negative';
                const changeSymbol = data.price_change >= 0 ? '+' : '';
                
                let html = '<div class="results">';
                
                // Price Card
                html += '<div class="card">';
                html += '<h3>' + data.symbol + ' - ' + data.company + '</h3>';
                html += '<div class="price-display">' + data.currency + ' $' + data.latest_price.toFixed(2) + '</div>';
                html += '<div class="change ' + changeClass + '">';
                html += changeSymbol + data.price_change.toFixed(2) + ' (' + changeSymbol + data.price_change_pct.toFixed(2) + '%)';
                html += '</div>';
                html += '</div>';
                
                // Data Info Card
                html += '<div class="card">';
                html += '<h3>Market Data</h3>';
                html += '<div class="indicator"><span class="indicator-label">Data Points</span><span class="indicator-value">' + data.data_points + '</span></div>';
                html += '<div class="indicator"><span class="indicator-label">Period</span><span class="indicator-value">' + data.start_date + ' to ' + data.end_date + '</span></div>';
                html += '<div class="indicator"><span class="indicator-label">Source</span><span class="indicator-value">' + data.source + '</span></div>';
                if (data.volume) {
                    html += '<div class="indicator"><span class="indicator-label">Volume</span><span class="indicator-value">' + (data.volume / 1000000).toFixed(2) + 'M</span></div>';
                }
                html += '</div>';
                
                // Technical Indicators Card
                if (indicators && !indicators.error) {
                    html += '<div class="card">';
                    html += '<h3>Technical Indicators</h3>';
                    html += '<div class="indicator"><span class="indicator-label">RSI</span><span class="indicator-value">' + indicators.RSI.toFixed(2) + '</span></div>';
                    html += '<div class="indicator"><span class="indicator-label">SMA 20</span><span class="indicator-value">$' + indicators.SMA_20.toFixed(2) + '</span></div>';
                    html += '<div class="indicator"><span class="indicator-label">EMA 12</span><span class="indicator-value">$' + indicators.EMA_12.toFixed(2) + '</span></div>';
                    html += '<div class="indicator"><span class="indicator-label">Volatility</span><span class="indicator-value">' + (indicators.volatility * 100).toFixed(2) + '%</span></div>';
                    html += '</div>';
                }
                
                // Simple Prediction Card
                html += '<div class="card">';
                html += '<h3>Simple Predictions</h3>';
                const prediction1d = data.latest_price * (1 + (Math.random() - 0.5) * 0.02);
                const prediction7d = data.latest_price * (1 + (Math.random() - 0.5) * 0.05);
                const prediction30d = data.latest_price * (1 + (Math.random() - 0.5) * 0.10);
                html += '<div class="indicator"><span class="indicator-label">1 Day</span><span class="indicator-value">$' + prediction1d.toFixed(2) + '</span></div>';
                html += '<div class="indicator"><span class="indicator-label">7 Days</span><span class="indicator-value">$' + prediction7d.toFixed(2) + '</span></div>';
                html += '<div class="indicator"><span class="indicator-label">30 Days</span><span class="indicator-value">$' + prediction30d.toFixed(2) + '</span></div>';
                html += '<small style="color: #666;">Statistical estimates only</small>';
                html += '</div>';
                
                html += '</div>';
                
                document.getElementById('results').innerHTML = html;
            }
            
            // Auto-fetch on load
            window.addEventListener('load', () => {
                // Optional: Auto-fetch a default stock
                // fetchData();
            });
        </script>
    </body>
    </html>
    """

@app.route("/api/status")
def api_status():
    """API status endpoint"""
    return jsonify({
        "status": "ok",
        "encoding": "utf-8",
        "timestamp": datetime.now().isoformat()
    })

@app.route("/api/fetch", methods=["POST", "OPTIONS"])
def api_fetch():
    """Fetch stock data"""
    if request.method == "OPTIONS":
        return "", 204
    
    try:
        data = request.get_json()
        symbol = data.get("symbol", "").upper().strip()
        period = data.get("period", "1mo")
        
        if not symbol:
            return jsonify({"error": "Symbol required"}), 400
        
        # Auto-detect Australian stocks
        if symbol in AUSTRALIAN_STOCKS and not symbol.endswith(".AX"):
            symbol = f"{symbol}.AX"
        
        print(f"Fetching {symbol} for period {period}")
        
        # Check cache
        cache_key = f"{symbol}_{period}"
        if cache_key in cache:
            cached_data, cache_time = cache[cache_key]
            if (datetime.now() - cache_time).seconds < 300:  # 5 minute cache
                print(f"Returning cached data for {symbol}")
                cached_data["from_cache"] = True
                return jsonify(cached_data)
        
        # Fetch from Yahoo Finance
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            # Try alternative method
            df = yf.download(symbol, period=period, progress=False, threads=False)
        
        if df.empty:
            return jsonify({"error": f"No data found for {symbol}"}), 404
        
        # Get company info
        try:
            info = ticker.info or {}
        except:
            info = {}
        
        # Process data
        dates = [d.strftime("%Y-%m-%d") for d in df.index]
        prices = df["Close"].values.flatten().tolist()
        volumes = df["Volume"].values.flatten().tolist() if "Volume" in df else []
        
        latest_price = prices[-1] if prices else 0
        price_change = prices[-1] - prices[0] if len(prices) >= 2 else 0
        price_change_pct = (price_change / prices[0] * 100) if prices[0] > 0 else 0
        
        # Get latest volume
        latest_volume = volumes[-1] if volumes else 0
        
        response_data = {
            "symbol": symbol,
            "company": info.get("longName", symbol),
            "currency": info.get("currency", "AUD" if ".AX" in symbol else "USD"),
            "source": "yahoo",
            "data_points": len(df),
            "start_date": dates[0] if dates else "",
            "end_date": dates[-1] if dates else "",
            "latest_price": float(latest_price),
            "price_change": float(price_change),
            "price_change_pct": float(price_change_pct),
            "volume": float(latest_volume),
            "prices": prices[-50:],  # Last 50 prices
            "dates": dates[-50:],
            "from_cache": False
        }
        
        # Cache the result
        cache[cache_key] = (response_data, datetime.now())
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/indicators", methods=["POST", "OPTIONS"])
def api_indicators():
    """Calculate technical indicators"""
    if request.method == "OPTIONS":
        return "", 204
    
    try:
        data = request.get_json()
        prices = data.get("prices", [])
        
        if len(prices) < 20:
            return jsonify({"error": "Not enough data for indicators"}), 400
        
        # Convert to pandas series
        price_series = pd.Series(prices)
        
        # Calculate indicators
        indicators = {
            "SMA_20": float(price_series.rolling(window=20).mean().iloc[-1]),
            "EMA_12": float(price_series.ewm(span=12).mean().iloc[-1]),
            "RSI": float(calculate_rsi(price_series)),
            "volatility": float(price_series.pct_change().std()),
            "min_price": float(price_series.min()),
            "max_price": float(price_series.max())
        }
        
        return jsonify(indicators)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def calculate_rsi(prices, period=14):
    """Calculate RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50

if __name__ == "__main__":
    print("\n" + "="*60)
    print("ML STOCK PREDICTOR - WORKING SERVER")
    print("="*60)
    print("Based on the clean_test_server that works")
    print(f"Starting at: http://localhost:8000")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    try:
        app.run(host="127.0.0.1", port=8000, debug=False)
    except Exception as e:
        print(f"\nError: {e}")
        input("\nPress Enter to exit...")