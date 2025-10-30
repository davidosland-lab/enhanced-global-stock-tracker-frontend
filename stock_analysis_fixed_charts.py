#!/usr/bin/env python3
"""
Stock Analysis System - Fixed Chart Rendering
Fixes: Candlestick bars not showing, price scales incorrect
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

app = Flask(__name__)
CORS(app)

def fetch_stock_data(symbol, period='1mo'):
    """Fetch stock data with proper error handling"""
    try:
        # Auto-detect Australian stocks
        au_stocks = ['CBA', 'BHP', 'CSL', 'NAB', 'ANZ', 'WBC', 'WES', 'MQG', 'TLS', 'WOW']
        if symbol.upper() in au_stocks and not symbol.endswith('.AX'):
            symbol = f"{symbol.upper()}.AX"
        
        # Download data using yfinance
        ticker = yf.Ticker(symbol)
        
        # Map period to appropriate parameters
        if period == '1d':
            df = ticker.history(period='5d', interval='5m')
            # Get only today's data
            today = datetime.now().date()
            df = df[df.index.date == today] if len(df) > 0 else ticker.history(period='1d', interval='5m')
        elif period == '5d':
            df = ticker.history(period='5d', interval='30m')
        elif period == '1mo':
            df = ticker.history(period='1mo', interval='1d')
        elif period == '3mo':
            df = ticker.history(period='3mo', interval='1d')
        elif period == '6mo':
            df = ticker.history(period='6mo', interval='1d')
        elif period == '1y':
            df = ticker.history(period='1y', interval='1d')
        elif period == '5y':
            df = ticker.history(period='5y', interval='1wk')
        else:
            df = ticker.history(period='1mo', interval='1d')
        
        if df.empty:
            raise ValueError(f"No data available for {symbol}")
        
        # Ensure we have OHLC columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        return df
        
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        raise

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """API endpoint for raw stock data"""
    try:
        period = request.args.get('period', '1mo')
        df = fetch_stock_data(symbol, period)
        
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
            'data_points': len(df)
        }
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart', methods=['POST'])
def generate_chart():
    """Generate interactive chart with technical indicators"""
    try:
        data = request.json
        symbol = data.get('symbol', 'AAPL')
        period = data.get('period', '1mo')
        chart_type = data.get('chart_type', 'candlestick')
        
        # Fetch data
        df = fetch_stock_data(symbol, period)
        
        # Create subplots
        fig = make_subplots(
            rows=4, cols=1,
            row_heights=[0.5, 0.15, 0.15, 0.2],
            subplot_titles=['Price', 'Volume', 'RSI', 'MACD'],
            vertical_spacing=0.05,
            specs=[[{"secondary_y": False}],
                   [{"secondary_y": False}],
                   [{"secondary_y": False}],
                   [{"secondary_y": False}]]
        )
        
        # Price chart
        if chart_type == 'candlestick':
            # Ensure we have proper OHLC data
            candlestick_trace = go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='OHLC',
                increasing=dict(line=dict(color='#26a69a', width=1), fillcolor='#26a69a'),
                decreasing=dict(line=dict(color='#ef5350', width=1), fillcolor='#ef5350'),
                showlegend=True
            )
            fig.add_trace(candlestick_trace, row=1, col=1)
            
            # Add Bollinger Bands for candlestick
            if len(df) >= 20:
                sma20 = df['Close'].rolling(20).mean()
                std20 = df['Close'].rolling(20).std()
                upper_band = sma20 + (std20 * 2)
                lower_band = sma20 - (std20 * 2)
                
                fig.add_trace(go.Scatter(
                    x=df.index, y=upper_band, 
                    line=dict(color='rgba(250, 128, 114, 0.5)', width=1),
                    name='Upper BB', showlegend=False
                ), row=1, col=1)
                
                fig.add_trace(go.Scatter(
                    x=df.index, y=lower_band,
                    line=dict(color='rgba(250, 128, 114, 0.5)', width=1),
                    name='Lower BB', fill='tonexty',
                    fillcolor='rgba(250, 128, 114, 0.1)', showlegend=False
                ), row=1, col=1)
                
                fig.add_trace(go.Scatter(
                    x=df.index, y=sma20,
                    line=dict(color='orange', width=1, dash='dash'),
                    name='SMA 20'
                ), row=1, col=1)
                
        elif chart_type == 'line':
            fig.add_trace(go.Scatter(
                x=df.index, y=df['Close'],
                mode='lines',
                name='Close',
                line=dict(color='#2196F3', width=2)
            ), row=1, col=1)
            
            # Add moving averages for line chart
            if len(df) >= 20:
                sma20 = df['Close'].rolling(20).mean()
                fig.add_trace(go.Scatter(
                    x=df.index, y=sma20,
                    mode='lines',
                    name='SMA 20',
                    line=dict(color='orange', width=1, dash='dash')
                ), row=1, col=1)
            
            if len(df) >= 50:
                sma50 = df['Close'].rolling(50).mean()
                fig.add_trace(go.Scatter(
                    x=df.index, y=sma50,
                    mode='lines',
                    name='SMA 50',
                    line=dict(color='red', width=1, dash='dot')
                ), row=1, col=1)
                
        else:  # area chart
            fig.add_trace(go.Scatter(
                x=df.index, y=df['Close'],
                mode='lines',
                name='Close',
                line=dict(color='#2196F3', width=2),
                fill='tozeroy',
                fillcolor='rgba(33, 150, 243, 0.3)'
            ), row=1, col=1)
        
        # Volume bars with colors
        volume_colors = ['#26a69a' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ef5350' 
                        for i in range(len(df))]
        fig.add_trace(go.Bar(
            x=df.index, y=df['Volume'],
            marker_color=volume_colors,
            showlegend=False,
            name='Volume'
        ), row=2, col=1)
        
        # RSI calculation and plot
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
            
            # Add RSI levels
            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                         opacity=0.3, row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", 
                         opacity=0.3, row=3, col=1)
        
        # MACD calculation and plot
        if len(df) >= 26:
            ema12 = df['Close'].ewm(span=12).mean()
            ema26 = df['Close'].ewm(span=26).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9).mean()
            histogram = macd_line - signal_line
            
            fig.add_trace(go.Scatter(
                x=df.index, y=macd_line,
                mode='lines',
                name='MACD',
                line=dict(color='blue', width=1.5)
            ), row=4, col=1)
            
            fig.add_trace(go.Scatter(
                x=df.index, y=signal_line,
                mode='lines',
                name='Signal',
                line=dict(color='red', width=1.5)
            ), row=4, col=1)
            
            # Histogram
            hist_colors = ['green' if h >= 0 else 'red' for h in histogram]
            fig.add_trace(go.Bar(
                x=df.index, y=histogram,
                marker_color=hist_colors,
                showlegend=False,
                name='Histogram',
                opacity=0.4
            ), row=4, col=1)
        
        # Calculate proper price range
        price_min = df[['Open', 'High', 'Low', 'Close']].min().min()
        price_max = df[['Open', 'High', 'Low', 'Close']].max().max()
        price_range = price_max - price_min
        price_padding = price_range * 0.1
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f'{symbol.upper()} - {period.upper()} - {chart_type.title()} Chart',
                font=dict(size=20, color='#333')
            ),
            height=900,
            showlegend=True,
            hovermode='x unified',
            xaxis_rangeslider_visible=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif', size=12),
            margin=dict(t=80, b=80, l=80, r=80)
        )
        
        # Update y-axes
        fig.update_yaxes(
            title_text="Price ($)",
            range=[price_min - price_padding, price_max + price_padding],
            gridcolor='#e0e0e0',
            row=1, col=1
        )
        fig.update_yaxes(title_text="Volume", gridcolor='#e0e0e0', row=2, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100], gridcolor='#e0e0e0', row=3, col=1)
        fig.update_yaxes(title_text="MACD", gridcolor='#e0e0e0', row=4, col=1)
        
        # Update x-axes
        fig.update_xaxes(gridcolor='#e0e0e0', row=1, col=1)
        fig.update_xaxes(gridcolor='#e0e0e0', row=2, col=1)
        fig.update_xaxes(gridcolor='#e0e0e0', row=3, col=1)
        fig.update_xaxes(title_text="Date", gridcolor='#e0e0e0', row=4, col=1)
        
        # Return chart data
        return jsonify({
            'success': True,
            'chart': json.loads(fig.to_json()),
            'stats': {
                'symbol': symbol.upper(),
                'period': period,
                'chart_type': chart_type,
                'min_price': float(price_min),
                'max_price': float(price_max),
                'current_price': float(df['Close'].iloc[-1]),
                'price_change': float(df['Close'].iloc[-1] - df['Close'].iloc[0]),
                'price_change_pct': float((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100),
                'data_points': len(df),
                'last_updated': df.index[-1].strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/')
def index():
    """Main interface with improved UI"""
    html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Stock Analysis System - Professional Charts</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #333;
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 16px;
        }
        
        .controls-panel {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .controls-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .control-group {
            display: flex;
            flex-direction: column;
        }
        
        .control-group label {
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .control-group input,
        .control-group select {
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s;
            background: white;
        }
        
        .control-group input:focus,
        .control-group select:focus {
            border-color: #667eea;
            outline: none;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .buttons {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        button {
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        
        button.secondary {
            background: linear-gradient(135deg, #4CAF50, #45a049);
        }
        
        .chart-container {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            min-height: 500px;
        }
        
        #chart {
            width: 100%;
            height: 100%;
            min-height: 900px;
        }
        
        #loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 400px;
            color: #999;
            font-size: 18px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        .stat-label {
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: bold;
            color: #333;
        }
        
        .stat-change {
            font-size: 14px;
            margin-top: 5px;
        }
        
        .positive { color: #4CAF50; }
        .negative { color: #f44336; }
        
        .popular-stocks {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        .stock-btn {
            padding: 8px 16px;
            background: #f5f5f5;
            border: 1px solid #e0e0e0;
            border-radius: 20px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .stock-btn:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        @media (max-width: 768px) {
            .controls-grid {
                grid-template-columns: 1fr;
            }
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Professional Stock Analysis System</h1>
            <p>Real-time market data with advanced technical analysis and charting</p>
        </div>
        
        <div class="controls-panel">
            <div class="controls-grid">
                <div class="control-group">
                    <label>Stock Symbol</label>
                    <input type="text" id="symbol" value="AAPL" placeholder="Enter symbol (e.g., AAPL, CBA)">
                </div>
                
                <div class="control-group">
                    <label>Time Period</label>
                    <select id="period">
                        <option value="1d">1 Day (5-min bars)</option>
                        <option value="5d">5 Days (30-min bars)</option>
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
                        <option value="candlestick">Candlestick (OHLC)</option>
                        <option value="line">Line Chart</option>
                        <option value="area">Area Chart</option>
                    </select>
                </div>
            </div>
            
            <div class="buttons">
                <button onclick="loadChart()">🔄 Generate Chart</button>
                <button class="secondary" onclick="fetchRawData()">📊 Get Raw Data</button>
                <button onclick="autoRefresh()" id="autoRefreshBtn">⏰ Auto Refresh: OFF</button>
            </div>
            
            <div class="popular-stocks">
                <span style="color: #666; margin-right: 10px;">Quick Access:</span>
                <span class="stock-btn" onclick="quickLoad('AAPL')">AAPL</span>
                <span class="stock-btn" onclick="quickLoad('GOOGL')">GOOGL</span>
                <span class="stock-btn" onclick="quickLoad('MSFT')">MSFT</span>
                <span class="stock-btn" onclick="quickLoad('TSLA')">TSLA</span>
                <span class="stock-btn" onclick="quickLoad('CBA.AX')">CBA</span>
                <span class="stock-btn" onclick="quickLoad('BHP.AX')">BHP</span>
                <span class="stock-btn" onclick="quickLoad('CSL.AX')">CSL</span>
            </div>
        </div>
        
        <div id="statsContainer" class="stats-grid"></div>
        
        <div class="chart-container">
            <div id="chart">
                <div id="loading">Select options and click "Generate Chart" to begin</div>
            </div>
        </div>
    </div>
    
    <script>
        let autoRefreshInterval = null;
        let lastSymbol = '';
        let lastPeriod = '';
        let lastChartType = '';
        
        function quickLoad(symbol) {
            document.getElementById('symbol').value = symbol;
            loadChart();
        }
        
        async function fetchRawData() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            
            try {
                const response = await fetch(`/api/stock/${symbol}?period=${period}`);
                const data = await response.json();
                
                if (data.error) {
                    alert('Error: ' + data.error);
                    return;
                }
                
                console.log('Raw Data:', data);
                alert(`Data fetched successfully!\\n` +
                      `Symbol: ${symbol}\\n` +
                      `Data Points: ${data.data_points}\\n` +
                      `Current Price: $${data.current_price.toFixed(2)}\\n` +
                      `Price Range: $${data.min_price.toFixed(2)} - $${data.max_price.toFixed(2)}`);
            } catch (error) {
                alert('Error fetching data: ' + error.message);
            }
        }
        
        async function loadChart() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            const chartType = document.getElementById('chartType').value;
            
            if (!symbol) {
                alert('Please enter a stock symbol');
                return;
            }
            
            // Store last values for auto-refresh
            lastSymbol = symbol;
            lastPeriod = period;
            lastChartType = chartType;
            
            document.getElementById('chart').innerHTML = '<div id="loading">⏳ Loading chart data...</div>';
            
            try {
                const response = await fetch('/api/chart', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        symbol: symbol,
                        period: period,
                        chart_type: chartType
                    })
                });
                
                const result = await response.json();
                
                if (!result.success) {
                    throw new Error(result.error || 'Failed to generate chart');
                }
                
                // Render chart with Plotly
                const config = {
                    responsive: true,
                    displayModeBar: true,
                    displaylogo: false,
                    modeBarButtonsToRemove: ['lasso2d', 'select2d']
                };
                
                Plotly.newPlot('chart', result.chart.data, result.chart.layout, config);
                
                // Update stats
                if (result.stats) {
                    updateStats(result.stats);
                }
                
            } catch (error) {
                document.getElementById('chart').innerHTML = 
                    `<div id="loading">❌ Error: ${error.message}</div>`;
            }
        }
        
        function updateStats(stats) {
            const changeClass = stats.price_change >= 0 ? 'positive' : 'negative';
            const changeSymbol = stats.price_change >= 0 ? '▲' : '▼';
            
            document.getElementById('statsContainer').innerHTML = `
                <div class="stat-card">
                    <div class="stat-label">Current Price</div>
                    <div class="stat-value">$${stats.current_price.toFixed(2)}</div>
                    <div class="stat-change ${changeClass}">
                        ${changeSymbol} $${Math.abs(stats.price_change).toFixed(2)} 
                        (${stats.price_change_pct >= 0 ? '+' : ''}${stats.price_change_pct.toFixed(2)}%)
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Price Range</div>
                    <div class="stat-value">$${stats.min_price.toFixed(2)} - $${stats.max_price.toFixed(2)}</div>
                    <div class="stat-change" style="color: #666;">
                        Period: ${stats.period.toUpperCase()}
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Data Points</div>
                    <div class="stat-value">${stats.data_points}</div>
                    <div class="stat-change" style="color: #666;">
                        Chart: ${stats.chart_type}
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Last Updated</div>
                    <div class="stat-value" style="font-size: 18px;">${stats.last_updated}</div>
                    <div class="stat-change" style="color: #666;">
                        Symbol: ${stats.symbol}
                    </div>
                </div>
            `;
        }
        
        function autoRefresh() {
            const btn = document.getElementById('autoRefreshBtn');
            
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
                autoRefreshInterval = null;
                btn.textContent = '⏰ Auto Refresh: OFF';
                btn.style.background = '';
            } else {
                if (!lastSymbol) {
                    alert('Please load a chart first');
                    return;
                }
                autoRefreshInterval = setInterval(() => {
                    loadChart();
                }, 30000); // Refresh every 30 seconds
                btn.textContent = '⏰ Auto Refresh: ON';
                btn.style.background = 'linear-gradient(135deg, #4CAF50, #45a049)';
            }
        }
        
        // Load initial chart on page load
        window.addEventListener('load', () => {
            setTimeout(() => {
                document.getElementById('symbol').value = 'AAPL';
                loadChart();
            }, 500);
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                loadChart();
            }
        });
    </script>
</body>
</html>
    '''
    return render_template_string(html)

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests"""
    return '', 204

if __name__ == '__main__':
    print("=" * 70)
    print("STOCK ANALYSIS SYSTEM - FIXED CHARTS")
    print("=" * 70)
    print("Features:")
    print("✅ Proper candlestick OHLC bars rendering")
    print("✅ Correct price scales for all stocks")
    print("✅ Australian stocks auto-detection (.AX suffix)")
    print("✅ Multiple timeframes with appropriate intervals")
    print("✅ Technical indicators: RSI, MACD, Bollinger Bands")
    print("✅ Volume analysis with color coding")
    print("✅ Real-time data from Yahoo Finance")
    print("=" * 70)
    print("Starting server at: http://localhost:8000")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=8000, debug=False)