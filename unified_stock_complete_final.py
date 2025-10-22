#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Stock Analysis System - COMPLETE FINAL VERSION
With working charts, intraday options, and fixed ML predictions
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
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: ML libraries not available")

print("=" * 70)
print("UNIFIED STOCK ANALYSIS - COMPLETE FINAL VERSION")
print("=" * 70)
print(f"Python: {sys.version}")
print(f"Platform: {sys.platform}")

ALPHA_VANTAGE_KEY = "68ZFANK047DL0KSR"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Australian stocks
AUSTRALIAN_STOCKS = ['CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'WOW', 'RIO', 'FMG']

# Cache
data_cache = {}
cache_duration = 300

def ensure_australian_suffix(symbol):
    """Add .AX suffix to Australian stocks if missing"""
    symbol = symbol.upper().strip()
    base = symbol.replace('.AX', '')
    if base in AUSTRALIAN_STOCKS and not symbol.endswith('.AX'):
        return f"{symbol}.AX"
    return symbol

def calculate_technical_indicators(df):
    """Calculate all technical indicators"""
    indicators = {}
    
    if len(df) < 3:
        return indicators
    
    close_prices = df['Close'].values
    high_prices = df['High'].values if 'High' in df else close_prices
    low_prices = df['Low'].values if 'Low' in df else close_prices
    
    # RSI
    if len(close_prices) >= 14:
        delta = pd.Series(close_prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
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
    
    # MACD
    if len(close_prices) >= 26:
        ema12 = pd.Series(close_prices).ewm(span=12, adjust=False).mean()
        ema26 = pd.Series(close_prices).ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        indicators['MACD'] = float(macd_line.iloc[-1])
        indicators['MACD_signal'] = float(signal_line.iloc[-1])
        indicators['MACD_histogram'] = float(macd_line.iloc[-1] - signal_line.iloc[-1])
    
    # ATR
    if len(close_prices) >= 14:
        tr_list = []
        for i in range(1, len(close_prices)):
            high_low = high_prices[i] - low_prices[i]
            high_close = abs(high_prices[i] - close_prices[i-1])
            low_close = abs(low_prices[i] - close_prices[i-1])
            tr_list.append(max(high_low, high_close, low_close))
        
        if len(tr_list) >= 14:
            indicators['ATR'] = float(pd.Series(tr_list).rolling(window=14).mean().iloc[-1])
    
    # Stochastic
    if len(close_prices) >= 14:
        low14 = pd.Series(low_prices).rolling(window=14).min()
        high14 = pd.Series(high_prices).rolling(window=14).max()
        k_percent = 100 * ((close_prices[-1] - low14.iloc[-1]) / (high14.iloc[-1] - low14.iloc[-1]))
        indicators['Stochastic_K'] = float(k_percent) if not np.isnan(k_percent) else 50.0
    
    # OBV
    if 'Volume' in df and len(df) >= 2:
        obv = 0
        obv_list = []
        for i in range(1, len(close_prices)):
            if close_prices[i] > close_prices[i-1]:
                obv += df['Volume'].iloc[i]
            elif close_prices[i] < close_prices[i-1]:
                obv -= df['Volume'].iloc[i]
            obv_list.append(obv)
        if obv_list:
            indicators['OBV'] = float(obv_list[-1])
    
    # VWAP
    if 'Volume' in df and len(df) >= 1:
        typical_price = (high_prices + low_prices + close_prices) / 3
        vwap = (typical_price * df['Volume'].values).sum() / df['Volume'].sum()
        indicators['VWAP'] = float(vwap)
    
    # Williams %R
    if len(close_prices) >= 14:
        highest_high = pd.Series(high_prices).rolling(window=14).max().iloc[-1]
        lowest_low = pd.Series(low_prices).rolling(window=14).min().iloc[-1]
        wr = -100 * ((highest_high - close_prices[-1]) / (highest_high - lowest_low))
        indicators['Williams_R'] = float(wr) if not np.isnan(wr) else -50.0
    
    return indicators

def fetch_yahoo_data(symbol, period='1mo', interval=None):
    """Fetch data from Yahoo Finance with intraday support"""
    try:
        symbol = ensure_australian_suffix(symbol)
        
        # Handle intraday periods
        if period in ['1d', '5d', '1wk'] and interval:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval, prepost=True, actions=False)
        else:
            # Regular daily data
            end_date = datetime.now()
            period_map = {
                '1d': 1, '5d': 5, '1wk': 7, '1mo': 30, '3mo': 90,
                '6mo': 180, '1y': 365, '5y': 1825
            }
            days = period_map.get(period, 30)
            start_date = end_date - timedelta(days=days)
            
            df = yf.download(symbol, start=start_date, end=end_date,
                           progress=False, auto_adjust=True, prepost=True, threads=True)
        
        if df.empty:
            return None
        
        # Handle MultiIndex columns from yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
            
        return df
    except Exception as e:
        print(f"Yahoo Finance error: {e}")
        return None

def fetch_alpha_vantage_data(symbol):
    """Fallback to Alpha Vantage if Yahoo fails"""
    try:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}'
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'Time Series (Daily)' in data:
            ts = data['Time Series (Daily)']
            df_data = []
            for date, values in list(ts.items())[:30]:
                df_data.append({
                    'Date': pd.Timestamp(date),
                    'Open': float(values['1. open']),
                    'High': float(values['2. high']),
                    'Low': float(values['3. low']),
                    'Close': float(values['4. close']),
                    'Volume': int(values['5. volume'])
                })
            df = pd.DataFrame(df_data)
            df.set_index('Date', inplace=True)
            df = df.sort_index()
            return df
    except Exception as e:
        print(f"Alpha Vantage error: {e}")
    return None

def generate_ml_predictions(df, symbol):
    """Generate realistic ML predictions"""
    if not ML_AVAILABLE or len(df) < 10:
        return None
    
    try:
        # Prepare features with more stable calculations
        df = df.copy()
        df['Returns'] = df['Close'].pct_change().fillna(0)
        df['MA5'] = df['Close'].rolling(window=5, min_periods=1).mean()
        df['MA20'] = df['Close'].rolling(window=20, min_periods=1).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume'].rolling(window=5, min_periods=1).mean()
        
        # Remove extreme outliers
        df['Returns'] = df['Returns'].clip(lower=-0.1, upper=0.1)
        df = df.fillna(method='ffill').fillna(0)
        
        # Features and target - predict next day's price
        feature_cols = ['Open', 'High', 'Low', 'Volume', 'Returns', 'MA5', 'Volume_Ratio']
        available_features = [col for col in feature_cols if col in df.columns]
        
        if len(available_features) < 3:
            return None
            
        X = df[available_features].values[:-1]
        y = df['Close'].values[1:]
        
        if len(X) < 5:
            return None
        
        # Use more conservative train/test split
        train_size = max(5, int(len(X) * 0.8))
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        # Scale features for better predictions
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test) if len(X_test) > 0 else X_train_scaled[-1:]
        
        # Train model with conservative parameters
        model = RandomForestRegressor(
            n_estimators=50, 
            max_depth=3,  # Shallow trees to prevent overfitting
            min_samples_split=5,
            random_state=42
        )
        model.fit(X_train_scaled, y_train)
        
        # Make prediction
        last_features = scaler.transform(X[-1].reshape(1, -1))
        current_price = float(df['Close'].iloc[-1])
        
        # Get prediction with trend adjustment
        base_prediction = float(model.predict(last_features)[0])
        
        # Calculate recent trend (last 5 days)
        if len(df) >= 5:
            recent_trend = (df['Close'].iloc[-1] - df['Close'].iloc[-5]) / df['Close'].iloc[-5]
            # Apply dampened trend (maximum 2% adjustment)
            trend_adjustment = min(0.02, max(-0.02, recent_trend * 0.3))
            predicted_price = base_prediction * (1 + trend_adjustment)
        else:
            predicted_price = base_prediction
        
        # Ensure prediction is within reasonable bounds (max 5% change)
        max_change = current_price * 0.05
        predicted_price = max(current_price - max_change, 
                             min(current_price + max_change, predicted_price))
        
        # Calculate confidence based on model performance and data quality
        if len(X_test) > 0:
            test_predictions = model.predict(X_test_scaled)
            test_score = model.score(X_test_scaled, y_test)
            # Adjust confidence based on score and data points
            base_confidence = max(0.4, min(0.85, test_score))
            data_penalty = 0.1 * max(0, (30 - len(df)) / 30)  # Penalty for less data
            confidence = base_confidence - data_penalty
        else:
            confidence = 0.5
        
        return {
            'current_price': current_price,
            'predicted_price': predicted_price,
            'change_percent': ((predicted_price - current_price) / current_price) * 100,
            'confidence': confidence * 100,
            'model': 'RandomForest (Conservative)',
            'features_used': len(available_features),
            'data_points': len(df),
            'symbol': symbol
        }
    except Exception as e:
        print(f"ML prediction error: {e}")
        return None

def create_plotly_chart(df, symbol, indicators=None, chart_type='candlestick'):
    """Create an interactive Plotly chart with selectable chart types"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f'{symbol} Stock Price', 'Volume', 'RSI'),
        row_heights=[0.6, 0.2, 0.2]
    )
    
    # Choose chart type based on user selection
    if chart_type == 'candlestick' and all(col in df.columns for col in ['Open', 'High', 'Low', 'Close']):
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='OHLC',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350',
                increasing_fillcolor='#26a69a',
                decreasing_fillcolor='#ef5350'
            ),
            row=1, col=1
        )
    elif chart_type == 'line' or not all(col in df.columns for col in ['Open', 'High', 'Low', 'Close']):
        # Line chart
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color='#2962FF', width=2),
                fill='tozeroy',
                fillcolor='rgba(41, 98, 255, 0.1)'
            ),
            row=1, col=1
        )
    elif chart_type == 'area':
        # Area chart
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color='#7c4dff', width=2),
                fill='tonexty',
                fillcolor='rgba(124, 77, 255, 0.2)'
            ),
            row=1, col=1
        )
    
    # Add SMA lines
    if len(df) >= 20:
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['SMA20'],
                mode='lines',
                name='SMA 20',
                line=dict(color='orange', width=1)
            ),
            row=1, col=1
        )
    
    # Volume chart
    if 'Volume' in df.columns:
        colors = ['red' if i > 0 and df['Close'].iloc[i] < df['Close'].iloc[i-1] else 'green' 
                  for i in range(len(df))]
        
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
    if indicators and 'RSI' in indicators and len(df) >= 14:
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=rsi,
                mode='lines',
                name='RSI',
                line=dict(color='purple', width=1)
            ),
            row=3, col=1
        )
        
        # Add RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=3, col=1)
    
    # Update layout with modern styling
    fig.update_layout(
        title={
            'text': f"{symbol} Stock Analysis",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title="Date",
        yaxis_title="Price ($)",
        yaxis2_title="Volume",
        yaxis3_title="RSI",
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True,
        hovermode='x unified',
        template='plotly_white',
        font=dict(family="Arial, sans-serif", size=12),
        plot_bgcolor='rgba(240, 240, 240, 0.1)',
        paper_bgcolor='white',
        margin=dict(t=80, b=80, l=80, r=80)
    )
    
    # Update axes styling
    fig.update_xaxes(
        gridcolor='lightgray',
        showgrid=True,
        zeroline=False,
        title_text="Date", 
        row=3, col=1
    )
    
    fig.update_yaxes(
        gridcolor='lightgray',
        showgrid=True,
        zeroline=False
    )
    
    return fig

@app.route('/favicon.ico')
def favicon():
    """Serve favicon to prevent 404 errors"""
    return Response(status=204)

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Main API endpoint for stock data with intraday support"""
    try:
        period = request.args.get('period', '1mo')
        interval = request.args.get('interval', None)
        
        # Validate intraday intervals
        if interval and interval not in ['1m', '5m', '15m', '30m', '60m', '1h']:
            interval = None
        
        # Check cache
        cache_key = f"{symbol}_{period}_{interval}"
        if cache_key in data_cache:
            cached_data, cache_time = data_cache[cache_key]
            if time.time() - cache_time < cache_duration:
                return jsonify(cached_data)
        
        # Fetch data
        df = fetch_yahoo_data(symbol, period, interval)
        
        if df is None:
            df = fetch_alpha_vantage_data(symbol)
        
        if df is None or df.empty:
            return jsonify({'error': f'No data found for {symbol}'}), 404
        
        # Calculate indicators
        indicators = calculate_technical_indicators(df)
        
        # Generate predictions with symbol context
        prediction = generate_ml_predictions(df, ensure_australian_suffix(symbol)) if ML_AVAILABLE else None
        
        # Prepare response
        response_data = {
            'symbol': ensure_australian_suffix(symbol),
            'dates': df.index.strftime('%Y-%m-%d %H:%M' if interval else '%Y-%m-%d').tolist(),
            'prices': df['Close'].values.flatten().tolist(),
            'open': df['Open'].values.flatten().tolist() if 'Open' in df else [],
            'high': df['High'].values.flatten().tolist() if 'High' in df else [],
            'low': df['Low'].values.flatten().tolist() if 'Low' in df else [],
            'volume': df['Volume'].values.flatten().tolist() if 'Volume' in df else [],
            'indicators': indicators,
            'prediction': prediction,
            'data_points': len(df),
            'interval': interval,
            'source': 'Yahoo Finance' if 'yahoo' not in str(df.index.name).lower() else 'Alpha Vantage',
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache the data
        data_cache[cache_key] = (response_data, time.time())
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/plotly-chart', methods=['POST'])
def generate_plotly_chart():
    """Generate Plotly chart and return as JSON data for rendering"""
    try:
        data = request.json
        symbol = data.get('symbol', 'STOCK')
        period = data.get('period', '1mo')
        interval = data.get('interval', None)
        chart_type = data.get('chart_type', 'candlestick')
        
        # Fetch fresh data
        df = fetch_yahoo_data(symbol, period, interval)
        
        if df is None:
            df = fetch_alpha_vantage_data(symbol)
        
        if df is None:
            return jsonify({'error': 'No data available'}), 404
        
        # Calculate indicators
        indicators = calculate_technical_indicators(df)
        
        # Create Plotly figure with selected chart type
        fig = create_plotly_chart(df, ensure_australian_suffix(symbol), indicators, chart_type)
        
        # Convert to JSON for client-side rendering
        chart_json = fig.to_json()
        
        return jsonify({
            'chart_data': json.loads(chart_json),
            'success': True,
            'chart_type': chart_type
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """Serve the main HTML page with working chart display"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis System - Complete Final</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
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
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2d3748;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #718096;
            font-size: 14px;
        }
        .main-content {
            display: grid;
            grid-template-columns: 380px 1fr;
            gap: 20px;
        }
        .control-panel {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            height: fit-content;
        }
        .data-panel {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .input-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #4a5568;
            font-weight: 500;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        .interval-group {
            display: none;
            margin-top: 10px;
        }
        .interval-group.show {
            display: block;
        }
        .quick-stocks {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        .quick-btn {
            padding: 8px 12px;
            background: #f7fafc;
            border: 1px solid #cbd5e0;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.3s;
        }
        .quick-btn:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
            margin-bottom: 10px;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .chart-btn {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        .indicators-display {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            max-height: 300px;
            overflow-y: auto;
        }
        .indicator-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e2e8f0;
        }
        .indicator-label {
            color: #4a5568;
            font-size: 13px;
        }
        .indicator-value {
            font-weight: 600;
            color: #2d3748;
        }
        .prediction-box {
            margin-top: 20px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            color: white;
        }
        .prediction-title {
            font-size: 18px;
            margin-bottom: 15px;
            font-weight: 600;
        }
        .prediction-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .prediction-value {
            font-size: 20px;
            font-weight: bold;
        }
        .positive { color: #68d391; }
        .negative { color: #fc8181; }
        .neutral { color: #ffd93d; }
        .loading {
            text-align: center;
            padding: 40px;
            color: #718096;
        }
        .error {
            background: #fed7d7;
            color: #c53030;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        #plotlyChart {
            min-height: 600px;
            width: 100%;
        }
        .status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            font-size: 13px;
        }
        .status.success {
            background: #c6f6d5;
            color: #276749;
        }
        .status.info {
            background: #bee3f8;
            color: #2c5282;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Professional Stock Analysis System - Final Version</h1>
            <div class="subtitle">Real-time Yahoo Finance | Alpha Vantage Backup | ML Predictions | Intraday Support</div>
        </div>

        <div class="main-content">
            <div class="control-panel">
                <div class="input-group">
                    <label>Stock Symbol</label>
                    <input type="text" id="symbolInput" placeholder="Enter symbol (e.g., CBA, AAPL)" value="CBA">
                    <div class="quick-stocks">
                        <div class="quick-btn" onclick="setSymbol('CBA')">CBA</div>
                        <div class="quick-btn" onclick="setSymbol('BHP')">BHP</div>
                        <div class="quick-btn" onclick="setSymbol('CSL')">CSL</div>
                        <div class="quick-btn" onclick="setSymbol('NAB')">NAB</div>
                        <div class="quick-btn" onclick="setSymbol('AAPL')">AAPL</div>
                        <div class="quick-btn" onclick="setSymbol('MSFT')">MSFT</div>
                    </div>
                </div>

                <div class="input-group">
                    <label>Time Period</label>
                    <select id="periodSelect" onchange="toggleIntervalOptions()">
                        <option value="1d">1 Day (Intraday)</option>
                        <option value="5d">5 Days (Intraday)</option>
                        <option value="1mo" selected>1 Month</option>
                        <option value="3mo">3 Months</option>
                        <option value="6mo">6 Months</option>
                        <option value="1y">1 Year</option>
                        <option value="5y">5 Years</option>
                    </select>
                    
                    <div id="intervalGroup" class="interval-group">
                        <label style="margin-top: 10px;">Interval (for intraday)</label>
                        <select id="intervalSelect">
                            <option value="1m">1 Minute</option>
                            <option value="5m" selected>5 Minutes</option>
                            <option value="15m">15 Minutes</option>
                            <option value="30m">30 Minutes</option>
                            <option value="1h">1 Hour</option>
                        </select>
                    </div>
                </div>

                <div class="input-group">
                    <label>Chart Type</label>
                    <select id="chartTypeSelect">
                        <option value="candlestick">Candlestick</option>
                        <option value="line">Line Chart</option>
                        <option value="area">Area Chart</option>
                    </select>
                </div>

                <button onclick="fetchData()">📊 Get Stock Data</button>
                <button class="chart-btn" onclick="generateChart()">📈 Generate Chart</button>

                <div id="indicators" class="indicators-display" style="display:none;">
                    <h3 style="margin-bottom: 15px; color: #2d3748;">Technical Indicators</h3>
                    <div id="indicatorsList"></div>
                </div>

                <div id="prediction" class="prediction-box" style="display:none;">
                    <div class="prediction-title">🤖 ML Prediction</div>
                    <div id="predictionContent"></div>
                </div>
            </div>

            <div class="data-panel">
                <div id="status"></div>
                <div id="plotlyChart">
                    <div class="loading">Select a stock and click "Get Stock Data" to begin</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentData = null;
        let currentSymbol = '';

        function setSymbol(symbol) {
            document.getElementById('symbolInput').value = symbol;
        }

        function toggleIntervalOptions() {
            const period = document.getElementById('periodSelect').value;
            const intervalGroup = document.getElementById('intervalGroup');
            
            if (period === '1d' || period === '5d') {
                intervalGroup.classList.add('show');
            } else {
                intervalGroup.classList.remove('show');
            }
        }

        function showStatus(message, type = 'info') {
            const status = document.getElementById('status');
            status.className = `status ${type}`;
            status.textContent = message;
            status.style.display = 'block';
            
            if (type === 'success') {
                setTimeout(() => {
                    status.style.display = 'none';
                }, 5000);
            }
        }

        async function fetchData() {
            const symbol = document.getElementById('symbolInput').value.trim();
            const period = document.getElementById('periodSelect').value;
            const interval = (period === '1d' || period === '5d') ? 
                document.getElementById('intervalSelect').value : null;
            
            if (!symbol) {
                alert('Please enter a stock symbol');
                return;
            }
            
            currentSymbol = symbol;
            showStatus('Fetching stock data...', 'info');
            document.getElementById('plotlyChart').innerHTML = '<div class="loading">Loading data...</div>';
            
            try {
                let url = `/api/stock/${symbol}?period=${period}`;
                if (interval) {
                    url += `&interval=${interval}`;
                }
                
                const response = await fetch(url);
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to fetch data');
                }
                
                currentData = data;
                const intervalText = data.interval ? ` (${data.interval} interval)` : '';
                showStatus(`Successfully loaded ${data.data_points} data points for ${data.symbol}${intervalText}`, 'success');
                
                // Display indicators
                if (data.indicators && Object.keys(data.indicators).length > 0) {
                    displayIndicators(data.indicators);
                }
                
                // Display prediction
                if (data.prediction) {
                    displayPrediction(data.prediction);
                }
                
                // Show basic info in chart container
                document.getElementById('plotlyChart').innerHTML = `
                    <div style="padding: 20px;">
                        <h3>${data.symbol} - Latest Data</h3>
                        <p>Current Price: $${data.prices[data.prices.length - 1].toFixed(2)}</p>
                        <p>Data Points: ${data.data_points}</p>
                        <p>Source: ${data.source}</p>
                        ${data.interval ? `<p>Interval: ${data.interval}</p>` : ''}
                        <p style="margin-top: 20px; color: #718096;">
                            Click "Generate Chart" to visualize the data
                        </p>
                    </div>
                `;
                
            } catch (error) {
                showStatus(`Error: ${error.message}`, 'error');
                document.getElementById('plotlyChart').innerHTML = 
                    `<div class="error">Failed to load data: ${error.message}</div>`;
            }
        }

        function displayIndicators(indicators) {
            const container = document.getElementById('indicators');
            const list = document.getElementById('indicatorsList');
            
            let html = '';
            for (const [key, value] of Object.entries(indicators)) {
                const formattedValue = typeof value === 'number' ? value.toFixed(2) : value;
                html += `
                    <div class="indicator-item">
                        <span class="indicator-label">${key}</span>
                        <span class="indicator-value">${formattedValue}</span>
                    </div>
                `;
            }
            
            list.innerHTML = html;
            container.style.display = 'block';
        }

        function displayPrediction(prediction) {
            const container = document.getElementById('prediction');
            const content = document.getElementById('predictionContent');
            
            // Determine color based on realistic thresholds
            let changeClass = 'neutral';
            if (Math.abs(prediction.change_percent) < 0.5) {
                changeClass = 'neutral';
            } else if (prediction.change_percent > 0) {
                changeClass = 'positive';
            } else {
                changeClass = 'negative';
            }
            
            const arrow = prediction.change_percent >= 0 ? '↑' : '↓';
            
            content.innerHTML = `
                <div class="prediction-item">
                    <span>Current Price:</span>
                    <span class="prediction-value">$${prediction.current_price.toFixed(2)}</span>
                </div>
                <div class="prediction-item">
                    <span>Predicted Price:</span>
                    <span class="prediction-value">$${prediction.predicted_price.toFixed(2)}</span>
                </div>
                <div class="prediction-item">
                    <span>Expected Change:</span>
                    <span class="prediction-value ${changeClass}">
                        ${arrow} ${Math.abs(prediction.change_percent).toFixed(2)}%
                    </span>
                </div>
                <div class="prediction-item">
                    <span>Confidence:</span>
                    <span class="prediction-value">${prediction.confidence.toFixed(1)}%</span>
                </div>
                <div class="prediction-item">
                    <span>Model:</span>
                    <span style="font-size: 14px;">${prediction.model}</span>
                </div>
            `;
            
            container.style.display = 'block';
        }

        async function generateChart() {
            if (!currentData) {
                alert('Please fetch stock data first');
                return;
            }
            
            const chartType = document.getElementById('chartTypeSelect').value;
            showStatus(`Generating ${chartType} chart...`, 'info');
            
            try {
                const period = document.getElementById('periodSelect').value;
                const interval = (period === '1d' || period === '5d') ? 
                    document.getElementById('intervalSelect').value : null;
                
                const requestData = {
                    symbol: currentSymbol,
                    period: period,
                    chart_type: chartType
                };
                
                if (interval) {
                    requestData.interval = interval;
                }
                
                const response = await fetch('/api/plotly-chart', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestData)
                });
                
                const result = await response.json();
                
                if (!response.ok) {
                    throw new Error(result.error || 'Failed to generate chart');
                }
                
                // Display the chart using Plotly with modern config
                if (result.chart_data) {
                    const config = {
                        responsive: true,
                        displayModeBar: true,
                        displaylogo: false,
                        modeBarButtonsToAdd: ['drawline', 'drawopenpath', 'eraseshape'],
                        modeBarButtonsToRemove: ['lasso2d', 'select2d']
                    };
                    
                    Plotly.newPlot('plotlyChart', result.chart_data.data, result.chart_data.layout, config);
                    showStatus(`${chartType.charAt(0).toUpperCase() + chartType.slice(1)} chart generated successfully!`, 'success');
                } else {
                    throw new Error('No chart data received');
                }
                
            } catch (error) {
                showStatus(`Error generating chart: ${error.message}`, 'error');
                console.error('Chart generation error:', error);
            }
        }

        // Initialize on load
        window.addEventListener('load', () => {
            toggleIntervalOptions();
        });
    </script>
</body>
</html>'''

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("Starting Complete Final Stock Analysis Server")
    print("=" * 70)
    print(f"Server URL: http://localhost:8000")
    print(f"Alpha Vantage API Key: {ALPHA_VANTAGE_KEY[:4]}...{ALPHA_VANTAGE_KEY[-4:]}")
    print("Features: Intraday support, Fixed ML predictions, Working charts")
    print("=" * 70)
    print("\nPress Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=8000, debug=False)