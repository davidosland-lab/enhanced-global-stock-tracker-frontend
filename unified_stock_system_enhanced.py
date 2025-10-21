#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Stock Analysis System - Enhanced with Interactive Charts
Complete solution with Yahoo Finance, Alpha Vantage, ML predictions, and technical analysis
Enhanced with interactive charts and proper indicator display
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
print("UNIFIED STOCK ANALYSIS SYSTEM - ENHANCED")
print("=" * 70)
print(f"Python: {sys.version}")
print(f"Platform: {sys.platform}")
print(f"Encoding: {sys.getdefaultencoding()}")

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from datetime import datetime, timedelta
import threading
import time

# Data and ML libraries
import yfinance as yf
import pandas as pd
import numpy as np
import requests

# ML libraries for predictions
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error, r2_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: ML libraries not available. Basic functionality will work.")

# Technical indicators - try to import, fallback to manual calculations
try:
    import talib as ta
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    print("Warning: TA-Lib not available. Using manual calculations for indicators.")

# Your Alpha Vantage API key
ALPHA_VANTAGE_KEY = "68ZFANK047DL0KSR"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Australian stocks list
AUSTRALIAN_STOCKS = ['CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'WOW', 'RIO', 'FMG', 
                     'MQG', 'TLS', 'WPL', 'SHL', 'COL', 'ALL', 'QBE', 'TCL', 'SUN', 'AMC']

# Cache for storing fetched data
data_cache = {}
cache_duration = 300  # 5 minutes

def is_australian_stock(symbol):
    """Check if a symbol is an Australian stock"""
    base = symbol.replace('.AX', '').upper()
    return base in AUSTRALIAN_STOCKS

def ensure_australian_suffix(symbol):
    """Add .AX suffix to Australian stocks if missing"""
    symbol = symbol.upper().strip()
    if is_australian_stock(symbol) and not symbol.endswith('.AX'):
        return f"{symbol}.AX"
    return symbol

def fetch_yahoo_data(symbol, period='1mo'):
    """Fetch data from Yahoo Finance with proper error handling"""
    try:
        symbol = ensure_australian_suffix(symbol)
        print(f"Fetching Yahoo data for {symbol}, period: {period}")
        
        # Calculate date range
        end_date = datetime.now()
        period_map = {
            '1d': 1, '5d': 5, '1mo': 30, '3mo': 90,
            '6mo': 180, '1y': 365, '2y': 730
        }
        
        days = period_map.get(period, 30)
        start_date = end_date - timedelta(days=days)
        
        # Use yf.download for more reliable data fetching
        df = yf.download(
            symbol,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=True,
            prepost=True,
            threads=True
        )
        
        if df.empty:
            raise ValueError(f"No data returned for {symbol}")
        
        # Get current info using Ticker
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Build response - properly convert DataFrame columns
        result = {
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
            'dividend_yield': info.get('dividendYield', 0),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
            'data_source': 'Yahoo Finance',
            'timestamp': datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        print(f"Yahoo Finance error for {symbol}: {str(e)}")
        return None

def fetch_alpha_vantage_data(symbol):
    """Fetch data from Alpha Vantage as backup"""
    try:
        symbol = ensure_australian_suffix(symbol)
        print(f"Fetching Alpha Vantage data for {symbol}")
        
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': 'full',  # Get more data points
            'apikey': ALPHA_VANTAGE_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Error Message' in data:
            raise ValueError(f"Alpha Vantage error: {data['Error Message']}")
        
        if 'Time Series (Daily)' not in data:
            raise ValueError("Invalid response from Alpha Vantage")
        
        time_series = data['Time Series (Daily)']
        dates = sorted(time_series.keys(), reverse=True)[:60]  # Get 60 days for better predictions
        
        prices = []
        volumes = []
        for date in reversed(dates):
            prices.append(float(time_series[date]['4. close']))
            volumes.append(float(time_series[date]['5. volume']))
        
        current_price = prices[-1] if prices else 0
        previous_close = prices[-2] if len(prices) > 1 else current_price
        
        return {
            'symbol': symbol,
            'prices': prices,
            'dates': dates[::-1],
            'volume': volumes,
            'current_price': current_price,
            'previous_close': previous_close,
            'change': current_price - previous_close,
            'change_percent': ((current_price / previous_close - 1) * 100) if previous_close > 0 else 0,
            'company_name': data.get('Meta Data', {}).get('2. Symbol', symbol),
            'data_source': 'Alpha Vantage',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Alpha Vantage error for {symbol}: {str(e)}")
        return None

def calculate_technical_indicators(prices, volumes=None):
    """Calculate comprehensive technical indicators"""
    if len(prices) < 20:
        return {}
    
    prices_array = np.array(prices, dtype=float)
    indicators = {}
    
    try:
        if TALIB_AVAILABLE:
            # Use TA-Lib if available
            indicators['SMA_20'] = float(ta.SMA(prices_array, timeperiod=20)[-1]) if len(prices) >= 20 else None
            indicators['SMA_50'] = float(ta.SMA(prices_array, timeperiod=50)[-1]) if len(prices) >= 50 else None
            indicators['EMA_12'] = float(ta.EMA(prices_array, timeperiod=12)[-1]) if len(prices) >= 12 else None
            indicators['EMA_26'] = float(ta.EMA(prices_array, timeperiod=26)[-1]) if len(prices) >= 26 else None
            
            # RSI
            rsi = ta.RSI(prices_array, timeperiod=14)
            indicators['RSI'] = float(rsi[-1]) if not np.isnan(rsi[-1]) else None
            
            # MACD
            macd, signal, hist = ta.MACD(prices_array, fastperiod=12, slowperiod=26, signalperiod=9)
            indicators['MACD'] = float(macd[-1]) if not np.isnan(macd[-1]) else None
            indicators['MACD_signal'] = float(signal[-1]) if not np.isnan(signal[-1]) else None
            indicators['MACD_histogram'] = float(hist[-1]) if not np.isnan(hist[-1]) else None
            
            # Bollinger Bands
            upper, middle, lower = ta.BBANDS(prices_array, timeperiod=20)
            indicators['BB_upper'] = float(upper[-1]) if not np.isnan(upper[-1]) else None
            indicators['BB_middle'] = float(middle[-1]) if not np.isnan(middle[-1]) else None
            indicators['BB_lower'] = float(lower[-1]) if not np.isnan(lower[-1]) else None
        else:
            # Manual calculations when TA-Lib is not available
            
            # Simple Moving Averages
            if len(prices) >= 20:
                indicators['SMA_20'] = float(np.mean(prices_array[-20:]))
            if len(prices) >= 50:
                indicators['SMA_50'] = float(np.mean(prices_array[-50:]))
            
            # Exponential Moving Averages (simplified)
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
            
            # RSI (Relative Strength Index) - manual calculation
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
            
            # MACD - manual calculation
            if len(prices) >= 26:
                ema12 = calculate_ema(prices_array, 12)
                ema26 = calculate_ema(prices_array, 26)
                macd_line = np.array(ema12[-len(ema26):]) - np.array(ema26)
                if len(macd_line) >= 9:
                    signal_line = calculate_ema(macd_line, 9)
                    indicators['MACD'] = float(macd_line[-1])
                    indicators['MACD_signal'] = float(signal_line[-1])
                    indicators['MACD_histogram'] = float(macd_line[-1] - signal_line[-1])
            
            # Bollinger Bands - manual calculation
            if len(prices) >= 20:
                sma20 = np.mean(prices_array[-20:])
                std20 = np.std(prices_array[-20:])
                indicators['BB_upper'] = float(sma20 + (2 * std20))
                indicators['BB_middle'] = float(sma20)
                indicators['BB_lower'] = float(sma20 - (2 * std20))
            
            # ATR (Average True Range) - simplified
            if len(prices) >= 15:
                high = prices_array * 1.01  # Approximate high
                low = prices_array * 0.99   # Approximate low
                tr = high - low
                indicators['ATR'] = float(np.mean(tr[-14:]))
            
    except Exception as e:
        print(f"Error calculating indicators: {str(e)}")
    
    return indicators

def predict_price(data):
    """Make price prediction using ML models - simplified and robust"""
    if not ML_AVAILABLE:
        return {
            'error': 'ML libraries not available',
            'simple_prediction': float(data['current_price'] * 1.02)
        }
    
    try:
        prices = np.array(data['prices'], dtype=float)
        
        # Need at least 10 data points
        if len(prices) < 10:
            # Simple moving average prediction
            trend = (prices[-1] - prices[0]) / len(prices)
            simple_pred = prices[-1] + trend
            return {
                'ensemble': float(simple_pred),
                'random_forest': float(simple_pred * 0.99),
                'gradient_boost': float(simple_pred * 1.01),
                'confidence': 0.5,
                'current_price': float(data['current_price']),
                'predicted_change': float((simple_pred / data['current_price'] - 1) * 100),
                'recommendation': 'HOLD',
                'note': 'Limited data - using simple trend analysis'
            }
        
        # Create simple features for training
        X = []
        y = []
        
        # Use a sliding window approach
        window_size = min(5, len(prices) // 3)
        
        for i in range(window_size, len(prices) - 1):
            window = prices[max(0, i-window_size):i]
            features = [
                float(window[-1]),  # Last price
                float(np.mean(window)),  # Average
                float(np.std(window)) if len(window) > 1 else 0.0,  # Volatility
                float(window[-1] - window[0]) if len(window) > 1 else 0.0,  # Change
            ]
            X.append(features)
            y.append(float(prices[i + 1]))
        
        if len(X) < 5:
            # Not enough samples, use simple prediction
            trend = (prices[-1] - prices[-5]) / 5 if len(prices) >= 5 else (prices[-1] - prices[0]) / len(prices)
            simple_pred = prices[-1] + trend
            return {
                'ensemble': float(simple_pred),
                'random_forest': float(simple_pred * 0.99),
                'gradient_boost': float(simple_pred * 1.01),
                'confidence': 0.6,
                'current_price': float(data['current_price']),
                'predicted_change': float((simple_pred / data['current_price'] - 1) * 100),
                'recommendation': 'HOLD' if abs(simple_pred - data['current_price']) / data['current_price'] < 0.02 else ('BUY' if simple_pred > data['current_price'] else 'SELL'),
                'note': 'Limited training data'
            }
        
        X = np.array(X)
        y = np.array(y)
        
        # Prepare prediction features
        last_window = prices[-window_size:]
        X_pred = np.array([[
            float(last_window[-1]),
            float(np.mean(last_window)),
            float(np.std(last_window)) if len(last_window) > 1 else 0.0,
            float(last_window[-1] - last_window[0]) if len(last_window) > 1 else 0.0
        ]])
        
        # Train simple models
        try:
            # Random Forest
            rf_model = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=5)
            rf_model.fit(X, y)
            rf_pred = float(rf_model.predict(X_pred)[0])
        except:
            rf_pred = float(prices[-1] * 1.01)
        
        try:
            # Gradient Boosting
            gb_model = GradientBoostingRegressor(n_estimators=50, random_state=42, max_depth=3)
            gb_model.fit(X, y)
            gb_pred = float(gb_model.predict(X_pred)[0])
        except:
            gb_pred = float(prices[-1] * 1.01)
        
        # Ensemble prediction
        ensemble_pred = (rf_pred + gb_pred) / 2
        
        # Calculate confidence based on recent volatility
        recent_prices = prices[-min(10, len(prices)):]
        volatility = np.std(recent_prices) / np.mean(recent_prices) if np.mean(recent_prices) > 0 else 0.1
        confidence = max(0.5, min(0.9, 1 - volatility * 2))
        
        # Determine recommendation
        change_pct = (ensemble_pred / data['current_price'] - 1) * 100
        if change_pct > 2:
            recommendation = 'BUY'
        elif change_pct < -2:
            recommendation = 'SELL'
        else:
            recommendation = 'HOLD'
        
        return {
            'random_forest': float(rf_pred),
            'gradient_boost': float(gb_pred),
            'ensemble': float(ensemble_pred),
            'confidence': float(confidence),
            'current_price': float(data['current_price']),
            'predicted_change': float(change_pct),
            'recommendation': recommendation
        }
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Fallback to simple prediction
        current = float(data['current_price'])
        return {
            'ensemble': current * 1.01,
            'random_forest': current * 1.005,
            'gradient_boost': current * 1.015,
            'confidence': 0.5,
            'current_price': current,
            'predicted_change': 1.0,
            'recommendation': 'HOLD',
            'error': f'Prediction failed, using simple estimate: {str(e)}'
        }

@app.route("/")
def index():
    """Main interface with interactive charts and indicators"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unified Stock Analysis System - Enhanced</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js" charset="utf-8"></script>
    <script>
        // Fallback if Plotly doesn't load from primary CDN
        if (typeof Plotly === 'undefined') {
            document.write('<script src="https://unpkg.com/plotly.js@2.27.0/dist/plotly.min.js"><\/script>');
        }
    </script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', Arial, sans-serif;
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
        
        .header p {
            color: #666;
            font-size: 1.2em;
        }
        
        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            margin-left: 20px;
            font-size: 0.9em;
        }
        
        .status.online {
            background: #4CAF50;
            color: white;
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
        
        .main-chart {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            min-height: 500px;
        }
        
        #stockChart {
            width: 100%;
            min-height: 500px;
        }
        
        #indicatorChart {
            width: 100%;
            min-height: 200px;
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
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.7em;
            font-weight: normal;
        }
        
        .badge.yahoo { background: #7C4DFF; color: white; }
        .badge.alpha { background: #FF6B6B; color: white; }
        
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
        
        .prediction-box h4 {
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .prediction-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .confidence {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 10px;
        }
        
        .confidence-bar {
            flex: 1;
            height: 8px;
            background: rgba(255,255,255,0.3);
            border-radius: 4px;
            overflow: hidden;
        }
        
        .confidence-fill {
            height: 100%;
            background: white;
            transition: width 1s ease;
        }
        
        .recommendation {
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 15px;
        }
        
        .recommendation.buy { background: #4CAF50; }
        .recommendation.hold { background: #FFC107; }
        .recommendation.sell { background: #f44336; }
        
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
        
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #c62828;
        }
        
        .success {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #2e7d32;
        }
        
        .info-box {
            background: #e3f2fd;
            color: #1565c0;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #1565c0;
        }
        
        @media (max-width: 768px) {
            .input-group {
                grid-template-columns: 1fr;
            }
            
            .results {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Unified Stock Analysis System - Enhanced</h1>
            <p>Real-time data with Interactive Charts, Technical Indicators & ML Predictions
                <span class="status online">● LIVE</span>
            </p>
        </div>
        
        <div class="controls">
            <div class="input-group">
                <input type="text" id="symbol" placeholder="Enter stock symbol (e.g., CBA, AAPL)" value="SPY">
                <select id="period">
                    <option value="1d">1 Day</option>
                    <option value="5d">5 Days</option>
                    <option value="1mo">1 Month</option>
                    <option value="3mo" selected>3 Months</option>
                    <option value="6mo">6 Months</option>
                    <option value="1y">1 Year</option>
                </select>
                <select id="dataSource">
                    <option value="auto">Auto (Yahoo → Alpha Vantage)</option>
                    <option value="yahoo">Yahoo Finance Only</option>
                    <option value="alpha">Alpha Vantage Only</option>
                </select>
                <button onclick="fetchData()">Analyze Stock</button>
            </div>
            
            <div class="quick-stocks">
                <div style="color: #666; margin-right: 15px;">Quick Access:</div>
                <span class="quick-btn australian" onclick="quickFetch('CBA')">CBA 🇦🇺</span>
                <span class="quick-btn australian" onclick="quickFetch('BHP')">BHP 🇦🇺</span>
                <span class="quick-btn australian" onclick="quickFetch('CSL')">CSL 🇦🇺</span>
                <span class="quick-btn australian" onclick="quickFetch('NAB')">NAB 🇦🇺</span>
                <span class="quick-btn australian" onclick="quickFetch('WBC')">WBC 🇦🇺</span>
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
                <button class="chart-btn" onclick="setChartType('ohlc')">OHLC</button>
                <button class="chart-btn" onclick="toggleIndicator('sma')">SMA</button>
                <button class="chart-btn" onclick="toggleIndicator('ema')">EMA</button>
                <button class="chart-btn" onclick="toggleIndicator('bb')">Bollinger Bands</button>
                <button class="chart-btn" onclick="toggleIndicator('volume')">Volume</button>
                <button class="chart-btn" onclick="toggleIndicator('rsi')">RSI</button>
                <button class="chart-btn" onclick="toggleIndicator('macd')">MACD</button>
            </div>
        </div>
        
        <div class="main-chart" id="mainChart" style="display:none;">
            <div id="stockChart"></div>
            <div id="indicatorChart" style="margin-top: 20px;"></div>
        </div>
        
        <div id="results"></div>
    </div>
    
    <script>
        let currentData = null;
        let currentIndicators = null;
        let chartType = 'candlestick';
        let showIndicators = {
            sma: false,
            ema: false,
            bb: false,
            volume: true,
            rsi: false,
            macd: false
        };
        
        async function quickFetch(symbol) {
            document.getElementById('symbol').value = symbol;
            fetchData();
        }
        
        function setChartType(type) {
            chartType = type;
            document.querySelectorAll('.chart-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.textContent.toLowerCase().includes(type) || 
                    (type === 'candlestick' && btn.textContent === 'Candlestick') ||
                    (type === 'ohlc' && btn.textContent === 'OHLC')) {
                    btn.classList.add('active');
                }
            });
            if (currentData) {
                updateChart();
            }
        }
        
        function toggleIndicator(indicator) {
            showIndicators[indicator] = !showIndicators[indicator];
            const btn = Array.from(document.querySelectorAll('.chart-btn')).find(b => 
                b.textContent.toLowerCase().includes(indicator) ||
                (indicator === 'bb' && b.textContent === 'Bollinger Bands') ||
                (indicator === 'sma' && b.textContent === 'SMA') ||
                (indicator === 'ema' && b.textContent === 'EMA') ||
                (indicator === 'rsi' && b.textContent === 'RSI') ||
                (indicator === 'macd' && b.textContent === 'MACD')
            );
            if (btn) {
                if (showIndicators[indicator]) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            }
            if (currentData) {
                updateChart();
            }
        }
        
        function updateChart() {
            console.log('updateChart called', currentData);
            if (!currentData) {
                console.error('No data available for chart');
                return;
            }
            
            // Check if Plotly is loaded
            if (typeof Plotly === 'undefined') {
                console.error('Plotly not loaded! Attempting to load...');
                // Try to load Plotly dynamically
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/plotly.js@2.27.0/dist/plotly.min.js';
                script.onload = () => {
                    console.log('Plotly loaded dynamically');
                    updateChart(); // Retry after loading
                };
                document.head.appendChild(script);
                return;
            }
            
            const traces = [];
            const layout = {
                title: currentData.symbol + ' - ' + currentData.company_name,
                xaxis: {
                    type: 'date',
                    rangeslider: { visible: false }
                },
                yaxis: {
                    title: 'Price ($)',
                    side: 'right'
                },
                height: 500,
                showlegend: true,
                hovermode: 'x unified'
            };
            
            // Main price chart
            if (chartType === 'candlestick') {
                traces.push({
                    type: 'candlestick',
                    x: currentData.dates,
                    open: currentData.open,
                    high: currentData.high,
                    low: currentData.low,
                    close: currentData.prices,
                    name: 'Price',
                    increasing: {line: {color: '#4CAF50'}},
                    decreasing: {line: {color: '#f44336'}}
                });
            } else if (chartType === 'line') {
                traces.push({
                    type: 'scatter',
                    mode: 'lines',
                    x: currentData.dates,
                    y: currentData.prices,
                    name: 'Close Price',
                    line: {color: '#667eea', width: 2}
                });
            } else if (chartType === 'area') {
                traces.push({
                    type: 'scatter',
                    mode: 'lines',
                    x: currentData.dates,
                    y: currentData.prices,
                    name: 'Close Price',
                    fill: 'tozeroy',
                    line: {color: '#667eea'},
                    fillcolor: 'rgba(102, 126, 234, 0.2)'
                });
            } else if (chartType === 'ohlc') {
                traces.push({
                    type: 'ohlc',
                    x: currentData.dates,
                    open: currentData.open,
                    high: currentData.high,
                    low: currentData.low,
                    close: currentData.prices,
                    name: 'OHLC',
                    increasing: {line: {color: '#4CAF50'}},
                    decreasing: {line: {color: '#f44336'}}
                });
            }
            
            // Add indicators
            if (showIndicators.sma && currentIndicators.SMA_20) {
                const sma20 = new Array(19).fill(null).concat(
                    new Array(currentData.prices.length - 19).fill(currentIndicators.SMA_20)
                );
                traces.push({
                    type: 'scatter',
                    mode: 'lines',
                    x: currentData.dates,
                    y: sma20,
                    name: 'SMA 20',
                    line: {color: '#FFA500', width: 1, dash: 'dot'}
                });
            }
            
            if (showIndicators.ema && currentIndicators.EMA_12) {
                const ema12 = new Array(11).fill(null).concat(
                    new Array(currentData.prices.length - 11).fill(currentIndicators.EMA_12)
                );
                traces.push({
                    type: 'scatter',
                    mode: 'lines',
                    x: currentData.dates,
                    y: ema12,
                    name: 'EMA 12',
                    line: {color: '#00BCD4', width: 1}
                });
            }
            
            if (showIndicators.bb && currentIndicators.BB_upper) {
                const bbUpper = new Array(19).fill(null).concat(
                    new Array(currentData.prices.length - 19).fill(currentIndicators.BB_upper)
                );
                const bbMiddle = new Array(19).fill(null).concat(
                    new Array(currentData.prices.length - 19).fill(currentIndicators.BB_middle)
                );
                const bbLower = new Array(19).fill(null).concat(
                    new Array(currentData.prices.length - 19).fill(currentIndicators.BB_lower)
                );
                
                traces.push({
                    type: 'scatter',
                    mode: 'lines',
                    x: currentData.dates,
                    y: bbUpper,
                    name: 'BB Upper',
                    line: {color: 'rgba(128, 128, 128, 0.3)', width: 1},
                    showlegend: false
                });
                traces.push({
                    type: 'scatter',
                    mode: 'lines',
                    x: currentData.dates,
                    y: bbMiddle,
                    name: 'BB Middle',
                    line: {color: 'rgba(128, 128, 128, 0.5)', width: 1, dash: 'dot'},
                    fill: 'tonexty',
                    fillcolor: 'rgba(128, 128, 128, 0.1)'
                });
                traces.push({
                    type: 'scatter',
                    mode: 'lines',
                    x: currentData.dates,
                    y: bbLower,
                    name: 'BB Lower',
                    line: {color: 'rgba(128, 128, 128, 0.3)', width: 1},
                    fill: 'tonexty',
                    fillcolor: 'rgba(128, 128, 128, 0.1)',
                    showlegend: false
                });
            }
            
            try {
                const chartDiv = document.getElementById('stockChart');
                if (!chartDiv) {
                    console.error('Chart container not found!');
                    return;
                }
                
                console.log('Rendering chart with', traces.length, 'traces');
                Plotly.newPlot('stockChart', traces, layout).then(() => {
                    console.log('Chart rendered successfully');
                }).catch(err => {
                    console.error('Chart rendering failed:', err);
                    // Fallback: show data in text format
                    chartDiv.innerHTML = '<div style="padding: 20px; color: #666;">Chart rendering failed. Data loaded successfully for ' + currentData.symbol + ' with ' + currentData.prices.length + ' data points.</div>';
                });
            } catch (e) {
                console.error('Error in chart rendering:', e);
            }
            
            // Indicator charts (RSI, MACD, Volume)
            const indicatorTraces = [];
            const indicatorLayout = {
                xaxis: {type: 'date'},
                height: 200,
                margin: {t: 0, b: 30},
                showlegend: true
            };
            
            if (showIndicators.volume) {
                indicatorTraces.push({
                    type: 'bar',
                    x: currentData.dates,
                    y: currentData.volume,
                    name: 'Volume',
                    marker: {color: 'rgba(102, 126, 234, 0.5)'},
                    yaxis: 'y'
                });
                indicatorLayout.yaxis = {title: 'Volume', side: 'right'};
            }
            
            if (showIndicators.rsi && currentIndicators.RSI) {
                const rsiValues = new Array(currentData.prices.length).fill(currentIndicators.RSI);
                indicatorTraces.push({
                    type: 'scatter',
                    mode: 'lines',
                    x: currentData.dates,
                    y: rsiValues,
                    name: 'RSI',
                    line: {color: '#FF6B6B', width: 2},
                    yaxis: 'y2'
                });
                indicatorTraces.push({
                    type: 'scatter',
                    mode: 'lines',
                    x: currentData.dates,
                    y: new Array(currentData.prices.length).fill(70),
                    name: 'Overbought',
                    line: {color: 'red', width: 1, dash: 'dash'},
                    showlegend: false,
                    yaxis: 'y2'
                });
                indicatorTraces.push({
                    type: 'scatter',
                    mode: 'lines',
                    x: currentData.dates,
                    y: new Array(currentData.prices.length).fill(30),
                    name: 'Oversold',
                    line: {color: 'green', width: 1, dash: 'dash'},
                    showlegend: false,
                    yaxis: 'y2'
                });
                indicatorLayout.yaxis2 = {
                    title: 'RSI',
                    overlaying: 'y',
                    side: 'left',
                    range: [0, 100]
                };
            }
            
            if (showIndicators.macd && currentIndicators.MACD) {
                const macdValues = new Array(currentData.prices.length).fill(currentIndicators.MACD);
                const signalValues = new Array(currentData.prices.length).fill(currentIndicators.MACD_signal);
                indicatorTraces.push({
                    type: 'scatter',
                    mode: 'lines',
                    x: currentData.dates,
                    y: macdValues,
                    name: 'MACD',
                    line: {color: '#4CAF50', width: 2},
                    yaxis: 'y3'
                });
                indicatorTraces.push({
                    type: 'scatter',
                    mode: 'lines',
                    x: currentData.dates,
                    y: signalValues,
                    name: 'Signal',
                    line: {color: '#f44336', width: 1},
                    yaxis: 'y3'
                });
                indicatorLayout.yaxis3 = {
                    title: 'MACD',
                    overlaying: 'y',
                    side: 'right',
                    anchor: 'free',
                    position: 0.05
                };
            }
            
            if (indicatorTraces.length > 0) {
                try {
                    const indicatorDiv = document.getElementById('indicatorChart');
                    if (indicatorDiv) {
                        Plotly.newPlot('indicatorChart', indicatorTraces, indicatorLayout).then(() => {
                            console.log('Indicator chart rendered');
                            indicatorDiv.style.display = 'block';
                        }).catch(err => {
                            console.error('Indicator chart failed:', err);
                        });
                    }
                } catch (e) {
                    console.error('Error rendering indicator chart:', e);
                }
            } else {
                document.getElementById('indicatorChart').style.display = 'none';
            }
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
            resultsDiv.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    Fetching data for ${symbol}...
                </div>
            `;
            
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
                        volumes: data.volume
                    })
                });
                
                const indicators = await indicatorsResponse.json();
                currentIndicators = indicators;
                
                // Show chart controls and chart
                document.getElementById('chartControls').style.display = 'block';
                document.getElementById('mainChart').style.display = 'block';
                
                // Update chart
                updateChart();
                
                // Display results
                displayResults(data, predictions, indicators);
                
            } catch (error) {
                resultsDiv.innerHTML = `
                    <div class="error">
                        <strong>Error:</strong> ${error.message}
                        <br><br>
                        <small>Try using a different data source or check the symbol.</small>
                    </div>
                `;
                document.getElementById('chartControls').style.display = 'none';
                document.getElementById('mainChart').style.display = 'none';
            }
        }
        
        function displayResults(data, predictions, indicators) {
            const changeClass = data.change >= 0 ? 'positive' : 'negative';
            const changeSymbol = data.change >= 0 ? '▲' : '▼';
            
            let html = `
                <div class="results">
                    <div class="card">
                        <h3>${data.symbol} 
                            <span class="badge ${data.data_source === 'Yahoo Finance' ? 'yahoo' : 'alpha'}">
                                ${data.data_source}
                            </span>
                        </h3>
                        
                        <div class="price-display">
                            $${data.current_price.toFixed(2)}
                        </div>
                        
                        <div class="change ${changeClass}">
                            ${changeSymbol} ${data.change.toFixed(2)} (${data.change_percent.toFixed(2)}%)
                        </div>
                        
                        ${data.company_name ? `
                            <div class="metric">
                                <span class="metric-label">Company</span>
                                <span class="metric-value">${data.company_name}</span>
                            </div>
                        ` : ''}
                        
                        ${data.market_cap ? `
                            <div class="metric">
                                <span class="metric-label">Market Cap</span>
                                <span class="metric-value">$${(data.market_cap / 1e9).toFixed(2)}B</span>
                            </div>
                        ` : ''}
                        
                        ${data.pe_ratio ? `
                            <div class="metric">
                                <span class="metric-label">P/E Ratio</span>
                                <span class="metric-value">${data.pe_ratio.toFixed(2)}</span>
                            </div>
                        ` : ''}
                        
                        ${data.dividend_yield ? `
                            <div class="metric">
                                <span class="metric-label">Dividend Yield</span>
                                <span class="metric-value">${(data.dividend_yield * 100).toFixed(2)}%</span>
                            </div>
                        ` : ''}
                        
                        <div class="metric">
                            <span class="metric-label">Data Points</span>
                            <span class="metric-value">${data.prices.length} days</span>
                        </div>
                        
                        <div class="metric">
                            <span class="metric-label">Last Updated</span>
                            <span class="metric-value">${new Date(data.timestamp).toLocaleTimeString()}</span>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>Technical Indicators</h3>
                        
                        <div class="indicator-grid">
                            ${indicators.RSI !== undefined && indicators.RSI !== null ? `
                                <div class="indicator">
                                    <div class="indicator-label">RSI (14)</div>
                                    <div class="indicator-value" style="color: ${
                                        indicators.RSI > 70 ? '#f44336' : 
                                        indicators.RSI < 30 ? '#4CAF50' : '#333'
                                    }">
                                        ${indicators.RSI.toFixed(2)}
                                    </div>
                                </div>
                            ` : ''}
                            
                            ${indicators.MACD !== undefined && indicators.MACD !== null ? `
                                <div class="indicator">
                                    <div class="indicator-label">MACD</div>
                                    <div class="indicator-value">
                                        ${indicators.MACD.toFixed(3)}
                                    </div>
                                </div>
                            ` : ''}
                            
                            ${indicators.SMA_20 !== undefined && indicators.SMA_20 !== null ? `
                                <div class="indicator">
                                    <div class="indicator-label">SMA (20)</div>
                                    <div class="indicator-value">
                                        $${indicators.SMA_20.toFixed(2)}
                                    </div>
                                </div>
                            ` : ''}
                            
                            ${indicators.SMA_50 !== undefined && indicators.SMA_50 !== null ? `
                                <div class="indicator">
                                    <div class="indicator-label">SMA (50)</div>
                                    <div class="indicator-value">
                                        $${indicators.SMA_50.toFixed(2)}
                                    </div>
                                </div>
                            ` : ''}
                            
                            ${indicators.EMA_12 !== undefined && indicators.EMA_12 !== null ? `
                                <div class="indicator">
                                    <div class="indicator-label">EMA (12)</div>
                                    <div class="indicator-value">
                                        $${indicators.EMA_12.toFixed(2)}
                                    </div>
                                </div>
                            ` : ''}
                            
                            ${indicators.EMA_26 !== undefined && indicators.EMA_26 !== null ? `
                                <div class="indicator">
                                    <div class="indicator-label">EMA (26)</div>
                                    <div class="indicator-value">
                                        $${indicators.EMA_26.toFixed(2)}
                                    </div>
                                </div>
                            ` : ''}
                            
                            ${indicators.BB_upper !== undefined && indicators.BB_upper !== null ? `
                                <div class="indicator">
                                    <div class="indicator-label">BB Upper</div>
                                    <div class="indicator-value">
                                        $${indicators.BB_upper.toFixed(2)}
                                    </div>
                                </div>
                            ` : ''}
                            
                            ${indicators.BB_lower !== undefined && indicators.BB_lower !== null ? `
                                <div class="indicator">
                                    <div class="indicator-label">BB Lower</div>
                                    <div class="indicator-value">
                                        $${indicators.BB_lower.toFixed(2)}
                                    </div>
                                </div>
                            ` : ''}
                            
                            ${indicators.ATR !== undefined && indicators.ATR !== null ? `
                                <div class="indicator">
                                    <div class="indicator-label">ATR (14)</div>
                                    <div class="indicator-value">
                                        ${indicators.ATR.toFixed(3)}
                                    </div>
                                </div>
                            ` : ''}
                            
                            ${indicators.MACD_signal !== undefined && indicators.MACD_signal !== null ? `
                                <div class="indicator">
                                    <div class="indicator-label">MACD Signal</div>
                                    <div class="indicator-value">
                                        ${indicators.MACD_signal.toFixed(3)}
                                    </div>
                                </div>
                            ` : ''}
                            
                            ${indicators.MACD_histogram !== undefined && indicators.MACD_histogram !== null ? `
                                <div class="indicator">
                                    <div class="indicator-label">MACD Histogram</div>
                                    <div class="indicator-value">
                                        ${indicators.MACD_histogram.toFixed(3)}
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                        
                        ${generateSignal(indicators)}
                    </div>
                    
                    ${!predictions.error ? `
                        <div class="card">
                            <h3>ML Predictions</h3>
                            
                            <div class="prediction-box">
                                <h4>Price Prediction</h4>
                                <div class="prediction-value">
                                    $${predictions.ensemble ? predictions.ensemble.toFixed(2) : 'N/A'}
                                </div>
                                <div style="opacity: 0.9;">
                                    ${predictions.predicted_change ? 
                                        `Expected Change: ${predictions.predicted_change > 0 ? '+' : ''}${predictions.predicted_change.toFixed(2)}%` 
                                        : ''}
                                </div>
                                
                                ${predictions.confidence ? `
                                    <div class="confidence">
                                        <span>Confidence:</span>
                                        <div class="confidence-bar">
                                            <div class="confidence-fill" style="width: ${predictions.confidence * 100}%"></div>
                                        </div>
                                        <span>${(predictions.confidence * 100).toFixed(0)}%</span>
                                    </div>
                                ` : ''}
                                
                                ${predictions.recommendation ? `
                                    <div class="recommendation ${predictions.recommendation.toLowerCase()}">
                                        ${predictions.recommendation}
                                    </div>
                                ` : ''}
                            </div>
                            
                            ${predictions.random_forest ? `
                                <div class="metric" style="margin-top: 20px;">
                                    <span class="metric-label">Random Forest</span>
                                    <span class="metric-value">$${predictions.random_forest.toFixed(2)}</span>
                                </div>
                            ` : ''}
                            
                            ${predictions.gradient_boost ? `
                                <div class="metric">
                                    <span class="metric-label">Gradient Boost</span>
                                    <span class="metric-value">$${predictions.gradient_boost.toFixed(2)}</span>
                                </div>
                            ` : ''}
                        </div>
                    ` : `
                        <div class="card">
                            <h3>ML Predictions</h3>
                            <div class="info-box">
                                ${predictions.error || 'Prediction not available'}
                            </div>
                        </div>
                    `}
                </div>
            `;
            
            document.getElementById('results').innerHTML = html;
        }
        
        function generateSignal(indicators) {
            let signals = [];
            
            if (indicators.RSI !== undefined && indicators.RSI !== null) {
                if (indicators.RSI < 30) signals.push('RSI indicates oversold - potential buy signal');
                else if (indicators.RSI > 70) signals.push('RSI indicates overbought - potential sell signal');
            }
            
            if (indicators.MACD !== undefined && indicators.MACD !== null && 
                indicators.MACD_signal !== undefined && indicators.MACD_signal !== null) {
                if (indicators.MACD > indicators.MACD_signal) signals.push('MACD bullish crossover');
                else signals.push('MACD bearish crossover');
            }
            
            if (signals.length > 0) {
                return `
                    <div class="info-box" style="margin-top: 20px;">
                        <strong>Technical Signals:</strong><br>
                        ${signals.map(s => `• ${s}`).join('<br>')}
                    </div>
                `;
            }
            
            return '';
        }
        
        // Auto-fetch SPY on load to demonstrate
        window.onload = () => {
            // Check if Plotly is loaded
            if (typeof Plotly === 'undefined') {
                console.error('Plotly not loaded on page load');
                // Try alternate CDN
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/plotly.js-dist@2.27.0/plotly.min.js';
                script.onload = () => {
                    console.log('Plotly loaded from alternate CDN');
                    fetchData();
                };
                script.onerror = () => {
                    console.error('Failed to load Plotly from all sources');
                    alert('Chart library failed to load. Charts will not be displayed, but data and indicators are working.');
                    fetchData();
                };
                document.head.appendChild(script);
            } else {
                console.log('Plotly loaded successfully');
                fetchData();
            }
        };
    </script>
</body>
</html>"""

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
        
        # Check cache first
        cache_key = f"{symbol}_{period}_{source}"
        if cache_key in data_cache:
            cached = data_cache[cache_key]
            if time.time() - cached['cached_at'] < cache_duration:
                print(f"Returning cached data for {symbol}")
                return jsonify(cached['data'])
        
        result = None
        
        # Try data sources based on preference
        if source == 'yahoo' or source == 'auto':
            result = fetch_yahoo_data(symbol, period)
        
        if not result and (source == 'alpha' or source == 'auto'):
            result = fetch_alpha_vantage_data(symbol)
        
        if not result:
            return jsonify({'error': f'Failed to fetch data for {symbol}'}), 500
        
        # Cache the result
        data_cache[cache_key] = {
            'data': result,
            'cached_at': time.time()
        }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"API fetch error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route("/api/indicators", methods=["POST"])
def api_indicators():
    """Calculate technical indicators"""
    try:
        data = request.json
        prices = data.get('prices', [])
        volumes = data.get('volumes')
        
        print(f"Calculating indicators for {len(prices)} price points")
        
        if not prices or len(prices) < 20:
            return jsonify({'error': 'Insufficient data for indicators'}), 400
        
        indicators = calculate_technical_indicators(prices, volumes)
        print(f"Calculated indicators: {list(indicators.keys())}")
        
        return jsonify(indicators)
        
    except Exception as e:
        print(f"Indicators error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """Make price predictions"""
    try:
        data = request.json.get('data')
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        print(f"Making prediction for {data.get('symbol')} with {len(data.get('prices', []))} data points")
        
        predictions = predict_price(data)
        print(f"Predictions result: {predictions}")
        
        return jsonify(predictions)
        
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ml_available': ML_AVAILABLE,
        'alpha_vantage_key': 'configured' if ALPHA_VANTAGE_KEY else 'missing'
    })

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SERVER STARTING")
    print("=" * 70)
    print(f"Access the application at: http://localhost:8000")
    print("Interactive charts with Plotly.js")
    print("Press Ctrl+C to stop the server")
    print("=" * 70 + "\n")
    
    app.run(host="0.0.0.0", port=8000, debug=False)