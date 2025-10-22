#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Stock Analysis System - INTRADAY VERSION
Enhanced with real-time intraday data, auto-refresh, and live price updates
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
print("UNIFIED STOCK ANALYSIS SYSTEM - INTRADAY EDITION")
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
cache_duration = 60  # Reduced to 1 minute for intraday accuracy

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

def fetch_intraday_data(symbol, interval='1m', period='1d'):
    """Fetch intraday data with minute-level precision"""
    try:
        symbol = ensure_australian_suffix(symbol)
        print(f"Fetching intraday data for {symbol}, interval: {interval}, period: {period}")
        
        # For intraday data, we use specific intervals
        ticker = yf.Ticker(symbol)
        
        # Get intraday data
        df = ticker.history(period=period, interval=interval, prepost=True, actions=False)
        
        if df.empty:
            # Fallback to regular download if history fails
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            
            df = yf.download(
                symbol,
                start=start_date,
                end=end_date,
                interval=interval,
                progress=False,
                auto_adjust=True,
                prepost=True,
                threads=True
            )
        
        if df.empty:
            raise ValueError(f"No intraday data returned for {symbol}")
        
        # Get live price
        info = ticker.info
        
        # Get current quote for most accurate price
        quote = None
        try:
            quote = ticker.fast_info
            current_price = quote.get('lastPrice', df['Close'].iloc[-1] if not df.empty else 0)
            market_state = quote.get('marketState', 'REGULAR')
        except:
            current_price = float(df['Close'].iloc[-1]) if not df.empty else info.get('currentPrice', 0)
            market_state = 'UNKNOWN'
        
        # Format timestamps based on interval
        if interval in ['1m', '2m', '5m', '15m', '30m', '60m', '90m']:
            timestamps = [d.strftime('%Y-%m-%d %H:%M:%S') for d in df.index]
        else:
            timestamps = [d.strftime('%Y-%m-%d') for d in df.index]
        
        # Build response with intraday data
        result = {
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
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'dividend_yield': info.get('dividendYield', 0),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
            'bid': info.get('bid', 0),
            'ask': info.get('ask', 0),
            'bid_size': info.get('bidSize', 0),
            'ask_size': info.get('askSize', 0),
            'day_high': info.get('dayHigh', max(df['High'].values) if not df.empty else 0),
            'day_low': info.get('dayLow', min(df['Low'].values) if not df.empty else 0),
            'volume_today': info.get('volume', sum(df['Volume'].values) if not df.empty else 0),
            'avg_volume': info.get('averageVolume', 0),
            'market_state': market_state,
            'data_source': 'Yahoo Finance Intraday',
            'interval': interval,
            'timestamp': datetime.now().isoformat(),
            'last_update': datetime.now().strftime('%H:%M:%S')
        }
        
        return result
        
    except Exception as e:
        print(f"Intraday fetch error for {symbol}: {str(e)}")
        return None

def fetch_yahoo_data(symbol, period='1mo'):
    """Fetch data from Yahoo Finance with proper error handling"""
    try:
        symbol = ensure_australian_suffix(symbol)
        print(f"Fetching Yahoo data for {symbol}, period: {period}")
        
        # For intraday periods, use intraday function
        if period in ['1d', '5d']:
            # Map period to appropriate interval
            interval = '5m' if period == '1d' else '15m'
            return fetch_intraday_data(symbol, interval=interval, period=period)
        
        # Calculate date range for longer periods
        end_date = datetime.now()
        period_map = {
            '1mo': 30, '3mo': 90,
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
        
        # Try to get real-time price
        try:
            quote = ticker.fast_info
            current_price = quote.get('lastPrice', df['Close'].iloc[-1])
        except:
            current_price = info.get('currentPrice', float(df['Close'].iloc[-1]))
        
        # Build response
        result = {
            'symbol': symbol,
            'prices': df['Close'].values.tolist(),
            'dates': [d.strftime('%Y-%m-%d') for d in df.index],
            'volume': df['Volume'].values.tolist(),
            'high': df['High'].values.tolist(),
            'low': df['Low'].values.tolist(),
            'open': df['Open'].values.tolist(),
            'current_price': float(current_price),
            'previous_close': float(df['Close'].iloc[-2]) if len(df) > 1 else float(df['Close'].iloc[-1]),
            'change': float(current_price - (df['Close'].iloc[-2] if len(df) > 1 else df['Close'].iloc[-1])),
            'change_percent': float(((current_price / df['Close'].iloc[-2] - 1) * 100)) if len(df) > 1 else 0,
            'company_name': info.get('longName', symbol),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'dividend_yield': info.get('dividendYield', 0),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
            'bid': info.get('bid', 0),
            'ask': info.get('ask', 0),
            'day_high': info.get('dayHigh', 0),
            'day_low': info.get('dayLow', 0),
            'volume_today': info.get('volume', 0),
            'avg_volume': info.get('averageVolume', 0),
            'data_source': 'Yahoo Finance',
            'timestamp': datetime.now().isoformat(),
            'last_update': datetime.now().strftime('%H:%M:%S')
        }
        
        return result
        
    except Exception as e:
        print(f"Yahoo Finance error for {symbol}: {str(e)}")
        return None

def fetch_alpha_vantage_intraday(symbol, interval='1min'):
    """Fetch intraday data from Alpha Vantage"""
    try:
        symbol = ensure_australian_suffix(symbol)
        print(f"Fetching Alpha Vantage intraday data for {symbol}")
        
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': interval,
            'outputsize': 'full',
            'apikey': ALPHA_VANTAGE_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Error Message' in data:
            raise ValueError(f"Alpha Vantage error: {data['Error Message']}")
        
        time_series_key = f'Time Series ({interval})'
        if time_series_key not in data:
            raise ValueError("Invalid response from Alpha Vantage")
        
        time_series = data[time_series_key]
        timestamps = sorted(time_series.keys(), reverse=True)[:390]  # Get full trading day
        
        prices = []
        volumes = []
        opens = []
        highs = []
        lows = []
        dates = []
        
        for timestamp in reversed(timestamps):
            prices.append(float(time_series[timestamp]['4. close']))
            volumes.append(float(time_series[timestamp]['5. volume']))
            opens.append(float(time_series[timestamp]['1. open']))
            highs.append(float(time_series[timestamp]['2. high']))
            lows.append(float(time_series[timestamp]['3. low']))
            dates.append(timestamp)
        
        current_price = prices[-1] if prices else 0
        
        # Get daily data for previous close
        daily_params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': ALPHA_VANTAGE_KEY
        }
        
        quote_response = requests.get(url, params=daily_params, timeout=10)
        quote_data = quote_response.json()
        
        previous_close = float(quote_data.get('Global Quote', {}).get('08. previous close', prices[0] if prices else 0))
        
        return {
            'symbol': symbol,
            'prices': prices,
            'dates': dates,
            'volume': volumes,
            'open': opens,
            'high': highs,
            'low': lows,
            'current_price': current_price,
            'previous_close': previous_close,
            'change': current_price - previous_close,
            'change_percent': ((current_price / previous_close - 1) * 100) if previous_close > 0 else 0,
            'company_name': symbol,
            'day_high': max(highs) if highs else 0,
            'day_low': min(lows) if lows else 0,
            'volume_today': sum(volumes) if volumes else 0,
            'data_source': 'Alpha Vantage Intraday',
            'interval': interval,
            'timestamp': datetime.now().isoformat(),
            'last_update': datetime.now().strftime('%H:%M:%S')
        }
        
    except Exception as e:
        print(f"Alpha Vantage intraday error for {symbol}: {str(e)}")
        return None

def calculate_technical_indicators(prices, volumes=None):
    """Calculate technical indicators with support for any data length"""
    if not prices or len(prices) < 3:
        return {}
    
    prices = np.array(prices, dtype=float)
    indicators = {}
    
    try:
        # SMA - Simple Moving Average (adaptive period)
        period = min(10, len(prices))
        if period >= 2:
            indicators['SMA_10'] = float(np.mean(prices[-period:]))
        
        # EMA - Exponential Moving Average (adaptive)
        if len(prices) >= 5:
            period = min(12, len(prices))
            alpha = 2 / (period + 1)
            ema = prices[0]
            for price in prices[1:]:
                ema = alpha * price + (1 - alpha) * ema
            indicators['EMA_12'] = float(ema)
        
        # RSI - Relative Strength Index (minimum 3 periods)
        if len(prices) >= 3:
            deltas = np.diff(prices)
            gains = deltas[deltas > 0]
            losses = -deltas[deltas < 0]
            
            avg_gain = np.mean(gains) if len(gains) > 0 else 0
            avg_loss = np.mean(losses) if len(losses) > 0 else 0.001
            
            rs = avg_gain / avg_loss if avg_loss != 0 else 100
            indicators['RSI'] = float(100 - (100 / (1 + rs)))
        
        # MACD - if we have enough data
        if len(prices) >= 12:
            ema12 = pd.Series(prices).ewm(span=12, adjust=False).mean().iloc[-1]
            ema26 = pd.Series(prices).ewm(span=min(26, len(prices)), adjust=False).mean().iloc[-1]
            indicators['MACD'] = float(ema12 - ema26)
            indicators['MACD_signal'] = float(pd.Series([ema12 - ema26]).ewm(span=9, adjust=False).mean().iloc[-1])
        
        # Bollinger Bands (adaptive period)
        if len(prices) >= 5:
            period = min(20, len(prices))
            sma = np.mean(prices[-period:])
            std = np.std(prices[-period:])
            indicators['BB_upper'] = float(sma + (2 * std))
            indicators['BB_middle'] = float(sma)
            indicators['BB_lower'] = float(sma - (2 * std))
        
        # ATR - Average True Range (if we have high/low data)
        if len(prices) >= 3:
            period = min(14, len(prices) - 1)
            tr_values = []
            for i in range(1, min(period + 1, len(prices))):
                tr = abs(prices[i] - prices[i-1])
                tr_values.append(tr)
            if tr_values:
                indicators['ATR'] = float(np.mean(tr_values))
        
        # Stochastic Oscillator (adaptive)
        if len(prices) >= 5:
            period = min(14, len(prices))
            lowest = min(prices[-period:])
            highest = max(prices[-period:])
            if highest != lowest:
                k = ((prices[-1] - lowest) / (highest - lowest)) * 100
                indicators['STOCH_K'] = float(k)
        
        # Volume indicators (if volume data available)
        if volumes is not None and len(volumes) >= len(prices):
            volumes = np.array(volumes, dtype=float)
            
            # OBV - On Balance Volume
            obv = 0
            for i in range(1, len(prices)):
                if prices[i] > prices[i-1]:
                    obv += volumes[i]
                elif prices[i] < prices[i-1]:
                    obv -= volumes[i]
            indicators['OBV'] = float(obv)
            
            # Volume SMA
            if len(volumes) >= 10:
                indicators['Volume_SMA'] = float(np.mean(volumes[-10:]))
        
    except Exception as e:
        print(f"Indicator calculation error: {str(e)}")
    
    return indicators

def predict_price(data):
    """Make price predictions using ML models"""
    if not ML_AVAILABLE:
        return {
            'error': 'ML libraries not available',
            'ensemble': data.get('current_price', 0) * 1.01,
            'confidence': 0.5
        }
    
    try:
        prices = np.array(data.get('prices', []))
        
        if len(prices) < 10:
            # Simple prediction for limited data
            current = float(data['current_price'])
            trend = (prices[-1] - prices[0]) / len(prices) if len(prices) > 1 else 0
            return {
                'ensemble': current + trend,
                'random_forest': current + (trend * 0.8),
                'gradient_boost': current + (trend * 1.2),
                'confidence': 0.5,
                'current_price': current,
                'predicted_change': trend / current * 100 if current > 0 else 0,
                'recommendation': 'HOLD',
                'warning': 'Limited data - predictions less reliable'
            }
        
        # Prepare features for ML models
        X = []
        y = []
        window_size = min(5, len(prices) - 1)
        
        for i in range(window_size, len(prices)):
            window = prices[i-window_size:i]
            features = [
                float(window[-1]),  # Last price
                float(np.mean(window)),  # Mean
                float(np.std(window)) if len(window) > 1 else 0,  # Std dev
                float(window[-1] - window[0])  # Change
            ]
            X.append(features)
            y.append(float(prices[i]))
        
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
    """Main interface with intraday features"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unified Stock Analysis - Intraday Edition</title>
    <!-- TradingView Lightweight Charts - Multiple CDN sources for reliability -->
    <script src="https://unpkg.com/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js"></script>
    <!-- Fallback CDN -->
    <script>
        if (typeof LightweightCharts === 'undefined') {
            document.write('<script src="https://cdn.jsdelivr.net/npm/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js"></scr' + 'ipt>');
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
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
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
        
        .live-change {
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: 600;
        }
        
        .live-change.positive {
            background: rgba(76, 175, 80, 0.2);
            color: #4CAF50;
        }
        
        .live-change.negative {
            background: rgba(244, 67, 54, 0.2);
            color: #f44336;
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
        
        .auto-refresh {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 15px;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 10px;
        }
        
        .auto-refresh input[type="checkbox"] {
            width: 20px;
            height: 20px;
        }
        
        .refresh-indicator {
            padding: 5px 10px;
            background: #4CAF50;
            color: white;
            border-radius: 5px;
            font-size: 0.9em;
            display: none;
        }
        
        .refresh-indicator.active {
            display: inline-block;
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
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
        
        .chart-btn {
            padding: 8px 16px;
            background: white;
            border: 1px solid #ddd;
            color: #333;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
            font-weight: 500;
            margin-left: 5px;
        }
        
        .chart-btn:hover {
            background: #f5f5f5;
            border-color: #667eea;
        }
        
        .chart-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
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
        
        .market-stat-label {
            color: rgba(255,255,255,0.7);
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        
        .market-stat-value {
            color: white;
            font-size: 1.4em;
            font-weight: bold;
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
        
        .price-display {
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
            margin: 20px 0;
        }
        
        .indicator-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }
        
        .loading {
            text-align: center;
            padding: 60px;
            color: white;
            font-size: 1.3em;
        }
        
        .spinner {
            border: 4px solid rgba(255,255,255,0.3);
            border-top: 4px solid white;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Unified Stock Analysis - Intraday</h1>
            <p>Real-time intraday data with minute-level precision
                <span class="status online">● LIVE</span>
            </p>
            
            <div class="live-ticker" id="liveTicker" style="display:none;">
                <span>Current Price:</span>
                <span class="live-price" id="livePrice">-</span>
                <span class="live-change" id="liveChange">-</span>
                <span id="lastUpdate">Last Update: -</span>
                <span id="marketState">Market: -</span>
            </div>
            
            <div class="market-info" id="marketInfo" style="display:none;">
                <div class="market-stat">
                    <div class="market-stat-label">Day High</div>
                    <div class="market-stat-value" id="dayHigh">-</div>
                </div>
                <div class="market-stat">
                    <div class="market-stat-label">Day Low</div>
                    <div class="market-stat-value" id="dayLow">-</div>
                </div>
                <div class="market-stat">
                    <div class="market-stat-label">Volume</div>
                    <div class="market-stat-value" id="volumeToday">-</div>
                </div>
                <div class="market-stat">
                    <div class="market-stat-label">Bid/Ask</div>
                    <div class="market-stat-value" id="bidAsk">-</div>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <div class="input-group">
                <input type="text" id="symbol" placeholder="Enter stock symbol (e.g., CBA, AAPL)" value="CBA">
                <select id="period">
                    <option value="1d" selected>Intraday (1D)</option>
                    <option value="5d">5 Days</option>
                    <option value="1mo">1 Month</option>
                    <option value="3mo">3 Months</option>
                    <option value="6mo">6 Months</option>
                    <option value="1y">1 Year</option>
                </select>
                <select id="interval">
                    <option value="1m">1 Minute</option>
                    <option value="5m" selected>5 Minutes</option>
                    <option value="15m">15 Minutes</option>
                    <option value="30m">30 Minutes</option>
                    <option value="60m">1 Hour</option>
                </select>
                <select id="dataSource">
                    <option value="auto">Auto (Yahoo → Alpha)</option>
                    <option value="yahoo">Yahoo Finance</option>
                    <option value="alpha">Alpha Vantage</option>
                </select>
                <button onclick="fetchData()">📊 Analyze</button>
            </div>
            
            <div class="auto-refresh">
                <input type="checkbox" id="autoRefresh" onchange="toggleAutoRefresh()">
                <label for="autoRefresh">Auto-refresh every</label>
                <select id="refreshInterval">
                    <option value="10">10 seconds</option>
                    <option value="30" selected>30 seconds</option>
                    <option value="60">1 minute</option>
                    <option value="300">5 minutes</option>
                </select>
                <span class="refresh-indicator" id="refreshIndicator">Refreshing...</span>
                <span id="countdown" style="margin-left: 15px; color: #666;"></span>
            </div>
            
            <div class="quick-stocks">
                <div style="color: #666; margin-right: 15px;">Quick Access:</div>
                <span class="quick-btn australian" onclick="quickFetch('CBA')">CBA 🇦🇺</span>
                <span class="quick-btn australian" onclick="quickFetch('BHP')">BHP 🇦🇺</span>
                <span class="quick-btn australian" onclick="quickFetch('CSL')">CSL 🇦🇺</span>
                <span class="quick-btn australian" onclick="quickFetch('NAB')">NAB 🇦🇺</span>
                <span class="quick-btn australian" onclick="quickFetch('WBC')">WBC 🇦🇺</span>
                <span class="quick-btn" onclick="quickFetch('AAPL')">AAPL</span>
                <span class="quick-btn" onclick="quickFetch('MSFT')">MSFT</span>
                <span class="quick-btn" onclick="quickFetch('GOOGL')">GOOGL</span>
                <span class="quick-btn" onclick="quickFetch('TSLA')">TSLA</span>
                <span class="quick-btn" onclick="quickFetch('NVDA')">NVDA</span>
            </div>
        </div>
        
        <!-- Professional Chart Container -->
        <div id="chartContainer" style="display:none; background:white; border-radius:15px; padding:25px; margin-bottom:30px; box-shadow:0 10px 30px rgba(0,0,0,0.2);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                <h3 style="color:#333; margin:0;">Intraday Trading Chart</h3>
                <div>
                    <button onclick="setChartType('candlestick', event)" class="chart-btn active" id="btnCandlestick">Candlestick</button>
                    <button onclick="setChartType('line', event)" class="chart-btn" id="btnLine">Line</button>
                    <button onclick="setChartType('area', event)" class="chart-btn" id="btnArea">Area</button>
                    <button onclick="toggleVolume(event)" class="chart-btn active" id="btnVolume">Volume</button>
                </div>
            </div>
            <div id="tradingViewChart" style="width:100%; height:500px;"></div>
        </div>
        
        <div id="results"></div>
    </div>
    
    <script>
        let currentData = null;
        let autoRefreshTimer = null;
        let countdownTimer = null;
        let tvChart = null;
        let candleSeries = null;
        let volumeSeries = null;
        let lineSeries = null;
        let areaSeries = null;
        let currentChartType = 'candlestick';
        let showVolume = true;
        
        async function quickFetch(symbol) {
            document.getElementById('symbol').value = symbol;
            // Set to intraday for quick fetch
            document.getElementById('period').value = '1d';
            document.getElementById('interval').value = '5m';
            fetchData();
        }
        
        async function fetchData() {
            const symbol = document.getElementById('symbol').value.trim().toUpperCase();
            const period = document.getElementById('period').value;
            const interval = document.getElementById('interval').value;
            const dataSource = document.getElementById('dataSource').value;
            
            if (!symbol) {
                alert('Please enter a stock symbol');
                return;
            }
            
            // Show loading state
            document.getElementById('refreshIndicator').classList.add('active');
            
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    Fetching intraday data for ${symbol}...
                </div>
            `;
            
            try {
                // Fetch stock data with interval parameter
                const response = await fetch('/api/fetch', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({symbol, period, interval, dataSource})
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to fetch data');
                }
                
                currentData = data;
                
                // Update live ticker
                updateLiveTicker(data);
                
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
                
                // Display chart
                setTimeout(() => {
                    displayChart(data);
                }, 100);
                
                displayResults(data, predictions, indicators);
                
            } catch (error) {
                resultsDiv.innerHTML = `
                    <div class="error">
                        <strong>Error:</strong> ${error.message}
                    </div>
                `;
            } finally {
                document.getElementById('refreshIndicator').classList.remove('active');
            }
        }
        
        function updateLiveTicker(data) {
            const ticker = document.getElementById('liveTicker');
            const marketInfo = document.getElementById('marketInfo');
            ticker.style.display = 'flex';
            marketInfo.style.display = 'grid';
            
            document.getElementById('livePrice').textContent = `$${data.current_price.toFixed(2)}`;
            
            const changeElement = document.getElementById('liveChange');
            const changeSymbol = data.change >= 0 ? '▲' : '▼';
            changeElement.textContent = `${changeSymbol} ${data.change.toFixed(2)} (${data.change_percent.toFixed(2)}%)`;
            changeElement.className = data.change >= 0 ? 'live-change positive' : 'live-change negative';
            
            document.getElementById('lastUpdate').textContent = `Last Update: ${data.last_update || new Date().toLocaleTimeString()}`;
            document.getElementById('marketState').textContent = `Market: ${data.market_state || 'OPEN'}`;
            
            // Update market info
            document.getElementById('dayHigh').textContent = `$${(data.day_high || 0).toFixed(2)}`;
            document.getElementById('dayLow').textContent = `$${(data.day_low || 0).toFixed(2)}`;
            document.getElementById('volumeToday').textContent = formatVolume(data.volume_today || 0);
            
            if (data.bid && data.ask) {
                document.getElementById('bidAsk').textContent = `${data.bid.toFixed(2)} / ${data.ask.toFixed(2)}`;
            } else {
                document.getElementById('bidAsk').textContent = '-';
            }
        }
        
        function formatVolume(volume) {
            if (volume >= 1000000) {
                return (volume / 1000000).toFixed(1) + 'M';
            } else if (volume >= 1000) {
                return (volume / 1000).toFixed(1) + 'K';
            }
            return volume.toString();
        }
        
        function toggleAutoRefresh() {
            const checkbox = document.getElementById('autoRefresh');
            
            if (checkbox.checked) {
                startAutoRefresh();
            } else {
                stopAutoRefresh();
            }
        }
        
        function startAutoRefresh() {
            const interval = parseInt(document.getElementById('refreshInterval').value) * 1000;
            let countdown = interval / 1000;
            
            // Initial fetch
            fetchData();
            
            // Set up countdown
            countdownTimer = setInterval(() => {
                countdown--;
                document.getElementById('countdown').textContent = `Next refresh in ${countdown}s`;
                
                if (countdown <= 0) {
                    countdown = interval / 1000;
                }
            }, 1000);
            
            // Set up refresh
            autoRefreshTimer = setInterval(() => {
                fetchData();
            }, interval);
        }
        
        function stopAutoRefresh() {
            if (autoRefreshTimer) {
                clearInterval(autoRefreshTimer);
                autoRefreshTimer = null;
            }
            
            if (countdownTimer) {
                clearInterval(countdownTimer);
                countdownTimer = null;
            }
            
            document.getElementById('countdown').textContent = '';
        }
        
        function displayChart(data) {
            console.log('Creating intraday chart with', data.prices.length, 'data points');
            
            // Show chart container
            document.getElementById('chartContainer').style.display = 'block';
            
            // Check if LightweightCharts is loaded
            if (typeof LightweightCharts === 'undefined') {
                console.error('TradingView Lightweight Charts library not loaded!');
                document.getElementById('tradingViewChart').innerHTML = '<p style="padding:20px;">Chart library loading... Please refresh the page.</p>';
                return;
            }
            
            // Destroy existing chart if any
            if (tvChart) {
                tvChart.remove();
                tvChart = null;
            }
            
            // Create new chart
            const chartContainer = document.getElementById('tradingViewChart');
            
            tvChart = LightweightCharts.createChart(chartContainer, {
                width: chartContainer.offsetWidth,
                height: 500,
                layout: {
                    backgroundColor: '#ffffff',
                    textColor: '#333',
                },
                grid: {
                    vertLines: { color: '#e1e4e8' },
                    horzLines: { color: '#e1e4e8' },
                },
                crosshair: {
                    mode: LightweightCharts.CrosshairMode.Normal,
                },
                priceScale: {
                    borderColor: '#d1d4dc',
                },
                timeScale: {
                    borderColor: '#d1d4dc',
                    timeVisible: true,
                    secondsVisible: data.interval && data.interval.includes('m'),
                },
            });
            
            // Prepare data for TradingView format
            const candleData = [];
            const volumeData = [];
            const lineData = [];
            
            for (let i = 0; i < data.dates.length; i++) {
                // Parse date/time appropriately
                let timestamp;
                if (data.dates[i].includes(':')) {
                    // Intraday timestamp
                    timestamp = new Date(data.dates[i]).getTime() / 1000;
                } else {
                    // Daily timestamp
                    timestamp = data.dates[i];
                }
                
                // Candlestick data
                if (data.open && data.high && data.low && data.open[i] && data.high[i] && data.low[i]) {
                    candleData.push({
                        time: timestamp,
                        open: data.open[i],
                        high: data.high[i],
                        low: data.low[i],
                        close: data.prices[i]
                    });
                }
                
                // Line/Area data
                lineData.push({
                    time: timestamp,
                    value: data.prices[i]
                });
                
                // Volume data
                if (data.volume && data.volume[i]) {
                    const prevPrice = i > 0 ? data.prices[i-1] : data.prices[i];
                    const openPrice = (data.open && data.open[i]) ? data.open[i] : prevPrice;
                    volumeData.push({
                        time: timestamp,
                        value: data.volume[i],
                        color: data.prices[i] >= openPrice 
                            ? 'rgba(38, 166, 154, 0.5)' 
                            : 'rgba(239, 83, 80, 0.5)'
                    });
                }
            }
            
            // Add the appropriate series
            let actualChartType = currentChartType;
            if (currentChartType === 'candlestick' && candleData.length === 0) {
                actualChartType = 'line';
            }
            
            try {
                if (actualChartType === 'candlestick' && candleData.length > 0) {
                    candleSeries = tvChart.addCandlestickSeries({
                        upColor: '#26a69a',
                        downColor: '#ef5350',
                        borderVisible: false,
                        wickUpColor: '#26a69a',
                        wickDownColor: '#ef5350',
                    });
                    candleSeries.setData(candleData);
                } else if (actualChartType === 'line' || (currentChartType === 'candlestick' && candleData.length === 0)) {
                    // Try to add line series
                    if (typeof tvChart.addLineSeries === 'function') {
                        lineSeries = tvChart.addLineSeries({
                            color: '#2962FF',
                            lineWidth: 2,
                            lastValueVisible: true,
                            priceLineVisible: true,
                        });
                        lineSeries.setData(lineData);
                    } else {
                        // Fallback to basic line chart if method doesn't exist
                        console.warn('addLineSeries not available, using alternative');
                        // Use candlestick series with same open/close for line effect
                        const lineAsCandleData = lineData.map(point => ({
                            time: point.time,
                            open: point.value,
                            high: point.value,
                            low: point.value,
                            close: point.value
                        }));
                        candleSeries = tvChart.addCandlestickSeries({
                            upColor: '#2962FF',
                            downColor: '#2962FF',
                            borderVisible: false,
                            wickVisible: false
                        });
                        candleSeries.setData(lineAsCandleData);
                    }
                } else if (actualChartType === 'area') {
                    if (typeof tvChart.addAreaSeries === 'function') {
                        areaSeries = tvChart.addAreaSeries({
                            topColor: 'rgba(41, 98, 255, 0.56)',
                            bottomColor: 'rgba(41, 98, 255, 0.04)',
                            lineColor: 'rgba(41, 98, 255, 1)',
                            lineWidth: 2,
                            lastValueVisible: true,
                            priceLineVisible: true,
                        });
                        areaSeries.setData(lineData);
                    } else {
                        // Fallback
                        console.warn('addAreaSeries not available');
                    }
                }
            } catch (error) {
                console.error('Error adding chart series:', error);
                // Fallback to simple display
                document.getElementById('tradingViewChart').innerHTML = `
                    <div style="padding:20px;">
                        <h3>Price Chart</h3>
                        <p>Current: $${data.current_price ? data.current_price.toFixed(2) : 'N/A'}</p>
                        <p>Data Points: ${data.prices ? data.prices.length : 0}</p>
                        <p style="color:#666; margin-top:10px;">Chart rendering issue detected. Data is still accurate.</p>
                    </div>
                `;
            }
            
            // Add volume if enabled
            if (showVolume && volumeData.length > 0) {
                volumeSeries = tvChart.addHistogramSeries({
                    color: '#26a69a',
                    priceFormat: {
                        type: 'volume',
                    },
                    priceScaleId: '',
                    scaleMargins: {
                        top: 0.8,
                        bottom: 0,
                    },
                });
                volumeSeries.setData(volumeData);
            }
            
            // Fit content
            tvChart.timeScale().fitContent();
            
            // Handle resize
            window.addEventListener('resize', () => {
                if (tvChart) {
                    tvChart.applyOptions({ 
                        width: chartContainer.offsetWidth 
                    });
                }
            });
        }
        
        function setChartType(type, evt) {
            currentChartType = type;
            
            // Update button states
            document.querySelectorAll('.chart-btn').forEach(btn => {
                if (!btn.id.includes('Volume')) {
                    btn.classList.remove('active');
                }
            });
            
            // Find and activate the clicked button
            if (evt && evt.target) {
                evt.target.classList.add('active');
            }
            
            if (currentData) {
                displayChart(currentData);
            }
        }
        
        function toggleVolume(evt) {
            showVolume = !showVolume;
            
            if (evt && evt.target) {
                evt.target.classList.toggle('active');
            }
            
            if (currentData) {
                displayChart(currentData);
            }
        }
        
        function displayResults(data, predictions, indicators) {
            const changeClass = data.change >= 0 ? 'positive' : 'negative';
            const changeSymbol = data.change >= 0 ? '▲' : '▼';
            
            let html = `
                <div class="results">
                    <div class="card">
                        <h3>${data.symbol}</h3>
                        <div class="price-display">$${data.current_price.toFixed(2)}</div>
                        ${generateIndicatorsHTML(indicators)}
                    </div>
                    
                    <div class="card">
                        <h3>ML Predictions</h3>
                        ${generatePredictionsHTML(predictions)}
                    </div>
                </div>
            `;
            
            document.getElementById('results').innerHTML = html;
        }
        
        function generateIndicatorsHTML(indicators) {
            if (!indicators || Object.keys(indicators).length === 0) {
                return '<p>Insufficient data for indicators</p>';
            }
            
            return `
                <div class="indicator-grid">
                    ${indicators.RSI ? `<div>RSI: ${indicators.RSI.toFixed(2)}</div>` : ''}
                    ${indicators.MACD ? `<div>MACD: ${indicators.MACD.toFixed(2)}</div>` : ''}
                    ${indicators.SMA_10 ? `<div>SMA: ${indicators.SMA_10.toFixed(2)}</div>` : ''}
                    ${indicators.ATR ? `<div>ATR: ${indicators.ATR.toFixed(2)}</div>` : ''}
                </div>
            `;
        }
        
        function generatePredictionsHTML(predictions) {
            if (!predictions || predictions.error) {
                return '<p>Predictions unavailable</p>';
            }
            
            return `
                <div>
                    <p>Predicted: $${predictions.ensemble ? predictions.ensemble.toFixed(2) : 'N/A'}</p>
                    <p>Confidence: ${predictions.confidence ? (predictions.confidence * 100).toFixed(0) : 0}%</p>
                    <p>Recommendation: <strong>${predictions.recommendation || 'HOLD'}</strong></p>
                </div>
            `;
        }
        
        // Auto-fetch on load with intraday data
        window.onload = () => {
            document.getElementById('period').value = '1d';
            document.getElementById('interval').value = '5m';
            fetchData();
        };
    </script>
</body>
</html>"""

@app.route("/api/fetch", methods=["POST"])
def api_fetch():
    """Fetch stock data with intraday support"""
    try:
        data = request.json
        symbol = data.get('symbol', '').upper()
        period = data.get('period', '1d')
        interval = data.get('interval', '5m')
        source = data.get('dataSource', 'auto')
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        # Check cache with shorter duration for intraday
        cache_duration_local = 60 if period in ['1d', '5d'] else cache_duration
        cache_key = f"{symbol}_{period}_{interval}_{source}"
        
        if cache_key in data_cache:
            cached = data_cache[cache_key]
            if time.time() - cached['cached_at'] < cache_duration_local:
                print(f"Returning cached data for {symbol}")
                # Update current price even from cache
                try:
                    ticker = yf.Ticker(ensure_australian_suffix(symbol))
                    quote = ticker.fast_info
                    cached['data']['current_price'] = quote.get('lastPrice', cached['data']['current_price'])
                    cached['data']['last_update'] = datetime.now().strftime('%H:%M:%S')
                except:
                    pass
                return jsonify(cached['data'])
        
        result = None
        
        # For intraday, prefer Yahoo Finance
        if period in ['1d', '5d'] and (source == 'yahoo' or source == 'auto'):
            result = fetch_intraday_data(symbol, interval=interval, period=period)
        
        # Try regular Yahoo Finance
        if not result and (source == 'yahoo' or source == 'auto'):
            result = fetch_yahoo_data(symbol, period)
        
        # Try Alpha Vantage intraday
        if not result and period in ['1d'] and (source == 'alpha' or source == 'auto'):
            result = fetch_alpha_vantage_intraday(symbol, interval='1min' if interval == '1m' else interval)
        
        # Try regular Alpha Vantage
        if not result and (source == 'alpha' or source == 'auto'):
            # Fallback to daily data from Alpha Vantage
            result = fetch_alpha_vantage_intraday(symbol, interval='60min')
        
        if not result:
            return jsonify({'error': f'Failed to fetch data for {symbol}'}), 500
        
        # Add interval to result
        result['interval'] = interval
        
        # Cache the result
        data_cache[cache_key] = {
            'data': result,
            'cached_at': time.time()
        }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"API fetch error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route("/api/realtime/<symbol>")
def api_realtime(symbol):
    """Get real-time price for a symbol"""
    try:
        symbol = ensure_australian_suffix(symbol.upper())
        ticker = yf.Ticker(symbol)
        
        # Get fast info for real-time data
        try:
            fast_info = ticker.fast_info
            current_price = fast_info.get('lastPrice', 0)
            market_state = fast_info.get('marketState', 'UNKNOWN')
        except:
            info = ticker.info
            current_price = info.get('currentPrice', 0)
            market_state = 'REGULAR'
        
        # Get latest minute data
        df = ticker.history(period='1d', interval='1m')
        
        if not df.empty:
            latest_price = float(df['Close'].iloc[-1])
            latest_volume = float(df['Volume'].iloc[-1])
            timestamp = df.index[-1].strftime('%H:%M:%S')
        else:
            latest_price = current_price
            latest_volume = 0
            timestamp = datetime.now().strftime('%H:%M:%S')
        
        return jsonify({
            'symbol': symbol,
            'price': latest_price or current_price,
            'volume': latest_volume,
            'timestamp': timestamp,
            'market_state': market_state
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/indicators", methods=["POST"])
def api_indicators():
    """Calculate technical indicators"""
    try:
        data = request.json
        prices = data.get('prices', [])
        volumes = data.get('volumes')
        
        if not prices or len(prices) < 3:
            return jsonify({'error': 'Need at least 3 data points'}), 400
        
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
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': 'intraday',
        'timestamp': datetime.now().isoformat(),
        'ml_available': ML_AVAILABLE,
        'alpha_vantage_key': 'configured' if ALPHA_VANTAGE_KEY else 'missing'
    })

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("INTRADAY SERVER STARTING")
    print("=" * 70)
    print(f"Access the application at: http://localhost:8001")
    print("Features: Real-time intraday data, auto-refresh, minute-level precision")
    print("Press Ctrl+C to stop the server")
    print("=" * 70 + "\n")
    app.run(host="0.0.0.0", port=8001, debug=False)