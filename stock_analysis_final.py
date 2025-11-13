#!/usr/bin/env python3
"""
Stock Analysis System - FINAL WORKING VERSION
Complete rewrite with verified chart rendering
"""

import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

from flask import Flask, jsonify, request, Response, render_template_string
from flask_cors import CORS
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

app = Flask(__name__)
CORS(app)

AUSTRALIAN_STOCKS = ['CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'WOW', 'RIO', 'FMG']
ALPHA_VANTAGE_KEY = "68ZFANK047DL0KSR"

def ensure_australian_suffix(symbol):
    symbol = symbol.upper().strip()
    base = symbol.replace('.AX', '')
    if base in AUSTRALIAN_STOCKS and not symbol.endswith('.AX'):
        return f"{symbol}.AX"
    return symbol

@app.route('/favicon.ico')
def favicon():
    return Response(status=204)

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get stock data with proper formatting"""
    try:
        period = request.args.get('period', '1mo')
        interval = request.args.get('interval', None)
        
        symbol = ensure_australian_suffix(symbol)
        ticker = yf.Ticker(symbol)
        
        # Fetch data based on period
        if interval and period in ['1d', '5d']:
            df = ticker.history(period=period, interval=interval, prepost=False, actions=False)
        else:
            df = ticker.history(period=period, prepost=False, actions=False)
        
        if df.empty:
            return jsonify({'error': 'No data found'}), 404
        
        # Calculate indicators
        indicators = {}
        if len(df) >= 14:
            close = df['Close']
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            rs = gain / (loss + 0.0001)
            indicators['RSI'] = float(100 - (100 / (1 + rs.iloc[-1])))
        
        if len(df) >= 20:
            indicators['SMA_20'] = float(df['Close'].rolling(20).mean().iloc[-1])
        
        # Ensure proper data conversion
        dates = [d.strftime('%Y-%m-%d') for d in df.index]
        prices = [float(p) for p in df['Close'].values]
        opens = [float(p) for p in df['Open'].values]
        highs = [float(p) for p in df['High'].values]
        lows = [float(p) for p in df['Low'].values]
        volumes = [int(v) for v in df['Volume'].values]
        
        return jsonify({
            'symbol': symbol,
            'dates': dates,
            'prices': prices,
            'open': opens,
            'high': highs,
            'low': lows,
            'volume': volumes,
            'indicators': indicators,
            'data_points': len(df),
            'min_price': min(lows),
            'max_price': max(highs),
            'current_price': prices[-1]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart', methods=['POST'])
def generate_chart():
    """Generate Plotly chart with verified data"""
    try:
        data = request.json
        symbol = ensure_australian_suffix(data.get('symbol', 'CBA'))
        period = data.get('period', '1mo')
        chart_type = data.get('chart_type', 'candlestick')
        
        # Fetch fresh data
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, prepost=False, actions=False)
        
        if df.empty:
            return jsonify({'error': 'No data'}), 404
        
        # Create figure
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=(f'{symbol} Price', 'Volume', 'RSI')
        )
        
        # Add main chart based on type
        if chart_type == 'candlestick':
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='OHLC',
                    increasing_line_color='green',
                    decreasing_line_color='red'
                ),
                row=1, col=1
            )
        else:  # Line or area chart
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['Close'],
                    mode='lines',
                    name='Close Price',
                    line=dict(color='blue', width=2),
                    fill='tozeroy' if chart_type == 'area' else None
                ),
                row=1, col=1
            )
            
            # Add SMA for line/area charts
            if len(df) >= 20:
                sma = df['Close'].rolling(20).mean()
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=sma,
                        mode='lines',
                        name='SMA 20',
                        line=dict(color='orange', width=1, dash='dash')
                    ),
                    row=1, col=1
                )
        
        # Volume
        colors = ['green' if df['Close'].iloc[i] >= df['Open'].iloc[i] else 'red' 
                  for i in range(len(df))]
        fig.add_trace(
            go.Bar(x=df.index, y=df['Volume'], marker_color=colors, showlegend=False),
            row=2, col=1
        )
        
        # RSI
        if len(df) >= 14:
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            rs = gain / (loss + 0.0001)
            rsi = 100 - (100 / (1 + rs))
            
            fig.add_trace(
                go.Scatter(x=df.index, y=rsi, mode='lines', name='RSI', line=dict(color='purple')),
                row=3, col=1
            )
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=3, col=1)
        
        # Update layout
        fig.update_layout(
            title=f'{symbol} Analysis',
            height=800,
            showlegend=True,
            hovermode='x unified',
            xaxis_rangeslider_visible=False
        )
        
        # Set Y-axis ranges
        price_min = df[['Open', 'High', 'Low', 'Close']].min().min()
        price_max = df[['Open', 'High', 'Low', 'Close']].max().max()
        price_range = price_max - price_min
        
        fig.update_yaxes(
            title_text="Price ($)",
            range=[price_min - price_range*0.1, price_max + price_range*0.1],
            row=1, col=1
        )
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=3, col=1)
        fig.update_xaxes(title_text="Date", row=3, col=1)
        
        # Convert to JSON
        return jsonify({
            'success': True,
            'chart': json.loads(fig.to_json()),
            'stats': {
                'min_price': float(price_min),
                'max_price': float(price_max),
                'current_price': float(df['Close'].iloc[-1]),
                'data_points': len(df)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """Main interface"""
    html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Stock Analysis - Final</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, Arial;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .controls {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }
        .control-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        label {
            font-size: 12px;
            color: #666;
            font-weight: 600;
        }
        input, select {
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            min-width: 150px;
        }
        button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            min-height: 400px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .stat-label {
            font-size: 12px;
            color: #666;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        #loading {
            text-align: center;
            padding: 40px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Stock Analysis System - Final Working Version</h1>
            <p>Real-time data with accurate chart rendering</p>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label>Symbol</label>
                <input type="text" id="symbol" value="CBA" placeholder="Stock symbol">
            </div>
            
            <div class="control-group">
                <label>Period</label>
                <select id="period">
                    <option value="1d">1 Day</option>
                    <option value="5d">5 Days</option>
                    <option value="1mo" selected>1 Month</option>
                    <option value="3mo">3 Months</option>
                    <option value="6mo">6 Months</option>
                    <option value="1y">1 Year</option>
                    <option value="5y">5 Years</option>
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
            
            <button onclick="loadChart()">Generate Chart</button>
            <button onclick="fetchData()" style="background: #4CAF50;">Get Data Only</button>
        </div>
        
        <div class="chart-container">
            <div id="chart">
                <div id="loading">Select options and click "Generate Chart"</div>
            </div>
        </div>
        
        <div class="stats" id="stats"></div>
    </div>
    
    <script>
        async function fetchData() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            
            const response = await fetch(`/api/stock/${symbol}?period=${period}`);
            const data = await response.json();
            
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }
            
            // Display stats
            document.getElementById('stats').innerHTML = `
                <div class="stat-card">
                    <div class="stat-label">Current Price</div>
                    <div class="stat-value">$${data.current_price.toFixed(2)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Min Price</div>
                    <div class="stat-value">$${data.min_price.toFixed(2)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Max Price</div>
                    <div class="stat-value">$${data.max_price.toFixed(2)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Data Points</div>
                    <div class="stat-value">${data.data_points}</div>
                </div>
            `;
        }
        
        async function loadChart() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            const chartType = document.getElementById('chartType').value;
            
            document.getElementById('chart').innerHTML = '<div id="loading">Loading chart...</div>';
            
            try {
                const response = await fetch('/api/chart', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({symbol, period, chart_type: chartType})
                });
                
                const result = await response.json();
                
                if (result.error) {
                    alert('Error: ' + result.error);
                    return;
                }
                
                // Display chart
                Plotly.newPlot('chart', result.chart.data, result.chart.layout, {responsive: true});
                
                // Display stats
                if (result.stats) {
                    document.getElementById('stats').innerHTML = `
                        <div class="stat-card">
                            <div class="stat-label">Current Price</div>
                            <div class="stat-value">$${result.stats.current_price.toFixed(2)}</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Min Price</div>
                            <div class="stat-value">$${result.stats.min_price.toFixed(2)}</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Max Price</div>
                            <div class="stat-value">$${result.stats.max_price.toFixed(2)}</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Data Points</div>
                            <div class="stat-value">${result.stats.data_points}</div>
                        </div>
                    `;
                }
                
            } catch (error) {
                alert('Error loading chart: ' + error.message);
            }
        }
        
        // Load chart on page load
        window.addEventListener('load', () => {
            loadChart();
        });
    </script>
</body>
</html>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    print("=" * 70)
    print("Stock Analysis System - Final Working Version")
    print("=" * 70)
    print("Server: http://localhost:8000")
    print("=" * 70)
    app.run(host='0.0.0.0', port=8000, debug=False)