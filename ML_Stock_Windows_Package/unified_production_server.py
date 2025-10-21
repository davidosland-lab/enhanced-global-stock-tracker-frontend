#!/usr/bin/env python3
"""
Unified Production ML Stock Predictor
Complete system with all features integrated
Works with NumPy 2.x
"""

import os
import sys
import json
import sqlite3
import hashlib
import logging
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

from flask import Flask, jsonify, request, render_template_string, send_file
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('production_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import required libraries
try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    YF_AVAILABLE = True
    logger.info(f"✅ yfinance {yf.__version__} loaded")
except ImportError as e:
    YF_AVAILABLE = False
    logger.error(f"❌ yfinance not available: {e}")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Try importing ML libraries (optional)
ML_AVAILABLE = False
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error, r2_score
    ML_AVAILABLE = True
    logger.info("✅ ML libraries available")
except ImportError:
    logger.warning("⚠️ ML libraries not available - predictions will use statistical methods")

# Configuration
ALPHA_VANTAGE_API_KEY = '68ZFANK047DL0KSR'
PORT = 8000
DATABASE_FILE = 'stock_data.db'

# Australian stocks
AUSTRALIAN_STOCKS = [
    'CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'WOW', 'RIO', 'FMG',
    'TLS', 'MQG', 'SUN', 'IAG', 'QBE', 'AMP', 'ORG', 'STO', 'WPL', 'NCM',
    'ALL', 'TCL', 'COL', 'REA', 'SGP', 'JHX', 'GMG', 'ASX', 'QAN', 'TWE'
]

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# System state
class SystemState:
    def __init__(self):
        self.cache = {}
        self.models = {}
        self.fetch_history = deque(maxlen=100)
        self.predictions = {}
        self.technical_indicators = {}
        self.start_time = datetime.now()
        self.request_count = 0
        
system_state = SystemState()

# Database initialization
def init_database():
    """Initialize SQLite database for storing historical data"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date DATE NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL NOT NULL,
            volume INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, date)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            prediction_date DATE NOT NULL,
            target_date DATE NOT NULL,
            predicted_price REAL NOT NULL,
            actual_price REAL,
            confidence REAL,
            model_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            model_type TEXT NOT NULL,
            mse REAL,
            rmse REAL,
            r2_score REAL,
            training_samples INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("✅ Database initialized")

# Technical indicators calculation
def calculate_technical_indicators(df: pd.DataFrame) -> Dict:
    """Calculate various technical indicators"""
    indicators = {}
    
    try:
        close_prices = df['Close'].values
        
        # Moving Averages
        indicators['SMA_20'] = pd.Series(close_prices).rolling(window=20).mean().iloc[-1]
        indicators['SMA_50'] = pd.Series(close_prices).rolling(window=50).mean().iloc[-1]
        indicators['EMA_12'] = pd.Series(close_prices).ewm(span=12).mean().iloc[-1]
        indicators['EMA_26'] = pd.Series(close_prices).ewm(span=26).mean().iloc[-1]
        
        # RSI
        delta = pd.Series(close_prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['RSI'] = 100 - (100 / (1 + rs)).iloc[-1]
        
        # MACD
        exp1 = pd.Series(close_prices).ewm(span=12).mean()
        exp2 = pd.Series(close_prices).ewm(span=26).mean()
        macd = exp1 - exp2
        indicators['MACD'] = macd.iloc[-1]
        indicators['MACD_signal'] = macd.ewm(span=9).mean().iloc[-1]
        
        # Bollinger Bands
        sma = pd.Series(close_prices).rolling(window=20).mean()
        std = pd.Series(close_prices).rolling(window=20).std()
        indicators['BB_upper'] = (sma + (std * 2)).iloc[-1]
        indicators['BB_lower'] = (sma - (std * 2)).iloc[-1]
        indicators['BB_middle'] = sma.iloc[-1]
        
        # Volume indicators
        if 'Volume' in df.columns:
            volumes = df['Volume'].values
            indicators['Volume_SMA'] = pd.Series(volumes).rolling(window=20).mean().iloc[-1]
            indicators['Volume_ratio'] = volumes[-1] / indicators['Volume_SMA'] if indicators['Volume_SMA'] > 0 else 1
        
        # Volatility
        returns = pd.Series(close_prices).pct_change()
        indicators['Volatility'] = returns.std() * np.sqrt(252)  # Annualized
        
        # Price position
        min_price = pd.Series(close_prices).rolling(window=52*5).min().iloc[-1] if len(close_prices) > 260 else min(close_prices)
        max_price = pd.Series(close_prices).rolling(window=52*5).max().iloc[-1] if len(close_prices) > 260 else max(close_prices)
        current_price = close_prices[-1]
        indicators['Price_position'] = (current_price - min_price) / (max_price - min_price) if max_price > min_price else 0.5
        
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}")
    
    return indicators

# Prediction engine
def generate_predictions(symbol: str, prices: List[float], periods: List[int] = [1, 7, 30]) -> Dict:
    """Generate price predictions using ML or statistical methods"""
    predictions = {}
    
    try:
        if len(prices) < 30:
            return {'error': 'Insufficient data for predictions'}
        
        current_price = prices[-1]
        
        if ML_AVAILABLE and len(prices) > 100:
            # Use ML model
            try:
                # Prepare features
                X = []
                y = []
                window = 20
                
                for i in range(window, len(prices) - 1):
                    features = []
                    # Price features
                    features.extend(prices[i-window:i])
                    # Statistical features
                    features.append(np.mean(prices[i-window:i]))
                    features.append(np.std(prices[i-window:i]))
                    features.append(np.min(prices[i-window:i]))
                    features.append(np.max(prices[i-window:i]))
                    
                    X.append(features)
                    y.append(prices[i + 1])
                
                X = np.array(X)
                y = np.array(y)
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                
                # Scale features
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Train model
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X_train_scaled, y_train)
                
                # Calculate accuracy
                y_pred = model.predict(X_test_scaled)
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                # Prepare current features
                current_features = []
                current_features.extend(prices[-window:])
                current_features.append(np.mean(prices[-window:]))
                current_features.append(np.std(prices[-window:]))
                current_features.append(np.min(prices[-window:]))
                current_features.append(np.max(prices[-window:]))
                
                current_features = scaler.transform([current_features])
                
                # Generate predictions
                base_prediction = model.predict(current_features)[0]
                
                for period in periods:
                    # Simple projection with decay
                    change_rate = (base_prediction - current_price) / current_price
                    decay = 1.0 - (0.1 * np.log(period))  # Decay factor
                    predicted_price = current_price * (1 + change_rate * decay * period / 7)
                    
                    predictions[f'{period}_day'] = {
                        'price': float(predicted_price),
                        'change': float((predicted_price - current_price) / current_price * 100),
                        'confidence': float(r2 * 0.8)  # Adjust confidence
                    }
                
                predictions['model_info'] = {
                    'type': 'RandomForestRegressor',
                    'mse': float(mse),
                    'r2_score': float(r2),
                    'training_samples': len(X_train)
                }
                
            except Exception as e:
                logger.error(f"ML prediction failed: {e}")
                # Fall back to statistical method
                ML_AVAILABLE = False
        
        if not ML_AVAILABLE or len(prices) <= 100:
            # Statistical prediction
            returns = np.diff(prices) / prices[:-1]
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            
            # Calculate trend
            if len(prices) > 20:
                recent_trend = (prices[-1] - prices[-20]) / prices[-20] / 20
            else:
                recent_trend = mean_return
            
            for period in periods:
                # Monte Carlo simulation
                simulations = []
                for _ in range(1000):
                    price = current_price
                    for _ in range(period):
                        daily_return = np.random.normal(recent_trend, std_return)
                        price *= (1 + daily_return)
                    simulations.append(price)
                
                predicted_price = np.median(simulations)
                confidence = 1 - (np.std(simulations) / predicted_price)
                
                predictions[f'{period}_day'] = {
                    'price': float(predicted_price),
                    'change': float((predicted_price - current_price) / current_price * 100),
                    'confidence': float(max(0.3, min(0.9, confidence)))
                }
            
            predictions['model_info'] = {
                'type': 'Statistical Monte Carlo',
                'mean_return': float(mean_return),
                'volatility': float(std_return),
                'simulations': 1000
            }
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        predictions = {'error': str(e)}
    
    return predictions

# Backtesting engine
def backtest_strategy(symbol: str, prices: List[float], strategy: str = 'momentum') -> Dict:
    """Backtest trading strategies"""
    try:
        if len(prices) < 50:
            return {'error': 'Insufficient data for backtesting'}
        
        initial_capital = 10000
        positions = []
        cash = initial_capital
        shares = 0
        
        # Simple momentum strategy
        for i in range(20, len(prices) - 1):
            sma_20 = np.mean(prices[i-20:i])
            current_price = prices[i]
            
            if strategy == 'momentum':
                # Buy when price crosses above SMA20
                if current_price > sma_20 * 1.02 and shares == 0:
                    shares = cash / current_price
                    cash = 0
                    positions.append({'action': 'buy', 'price': current_price, 'date': i})
                
                # Sell when price drops below SMA20
                elif current_price < sma_20 * 0.98 and shares > 0:
                    cash = shares * current_price
                    shares = 0
                    positions.append({'action': 'sell', 'price': current_price, 'date': i})
        
        # Final position
        final_value = cash + (shares * prices[-1])
        total_return = (final_value - initial_capital) / initial_capital * 100
        
        # Calculate metrics
        num_trades = len([p for p in positions if p['action'] == 'buy'])
        win_trades = 0
        
        for i in range(0, len(positions) - 1, 2):
            if i + 1 < len(positions):
                if positions[i + 1]['price'] > positions[i]['price']:
                    win_trades += 1
        
        win_rate = win_trades / num_trades if num_trades > 0 else 0
        
        # Sharpe ratio (simplified)
        returns = np.diff(prices) / prices[:-1]
        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        
        # Max drawdown
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = np.min(drawdown) * 100
        
        return {
            'strategy': strategy,
            'initial_capital': initial_capital,
            'final_value': float(final_value),
            'total_return': float(total_return),
            'num_trades': num_trades,
            'win_rate': float(win_rate),
            'sharpe_ratio': float(sharpe),
            'max_drawdown': float(max_drawdown),
            'positions': positions[-10:]  # Last 10 positions
        }
        
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        return {'error': str(e)}

# Data fetching with multiple sources
def fetch_stock_data(symbol: str, period: str = '1mo') -> Optional[Dict]:
    """Fetch stock data with fallback sources"""
    try:
        # Check cache first
        cache_key = f"{symbol}_{period}"
        if cache_key in system_state.cache:
            cached_data, cache_time = system_state.cache[cache_key]
            if (datetime.now() - cache_time).seconds < 300:  # 5 minute cache
                cached_data['from_cache'] = True
                return cached_data
        
        # Auto-detect Australian stocks
        original_symbol = symbol
        if symbol in AUSTRALIAN_STOCKS and not symbol.endswith('.AX'):
            symbol = f"{symbol}.AX"
            logger.info(f"Auto-detected Australian stock: {original_symbol} -> {symbol}")
        
        # Try Yahoo Finance
        if YF_AVAILABLE:
            try:
                # Multiple fetch attempts
                df = None
                for attempt in range(3):
                    try:
                        if attempt == 0:
                            df = yf.download(symbol, period=period, progress=False, threads=False)
                        elif attempt == 1:
                            ticker = yf.Ticker(symbol)
                            df = ticker.history(period=period)
                        else:
                            ticker = yf.Ticker(symbol)
                            ticker._reset_session()
                            df = ticker.history(period=period)
                        
                        if df is not None and not df.empty:
                            break
                    except:
                        continue
                
                if df is not None and not df.empty:
                    # Get company info
                    try:
                        ticker = yf.Ticker(symbol)
                        info = ticker.info or {}
                    except:
                        info = {}
                    
                    # Process data
                    dates = [d.strftime('%Y-%m-%d') for d in df.index]
                    prices = df['Close'].values.flatten().tolist()
                    volumes = df['Volume'].values.flatten().tolist() if 'Volume' in df else []
                    
                    # Save to database
                    try:
                        conn = sqlite3.connect(DATABASE_FILE)
                        cursor = conn.cursor()
                        
                        for i, date in enumerate(dates):
                            cursor.execute('''
                                INSERT OR REPLACE INTO stock_data 
                                (symbol, date, close, volume) 
                                VALUES (?, ?, ?, ?)
                            ''', (symbol, date, prices[i], volumes[i] if i < len(volumes) else 0))
                        
                        conn.commit()
                        conn.close()
                    except Exception as e:
                        logger.error(f"Database save error: {e}")
                    
                    # Calculate metrics
                    latest_price = prices[-1]
                    price_change = prices[-1] - prices[0] if len(prices) >= 2 else 0
                    price_change_pct = (price_change / prices[0] * 100) if prices[0] > 0 else 0
                    
                    # Calculate indicators
                    indicators = calculate_technical_indicators(df)
                    
                    # Generate predictions
                    predictions = generate_predictions(symbol, prices)
                    
                    # Backtest
                    backtest = backtest_strategy(symbol, prices) if len(prices) > 50 else {}
                    
                    response_data = {
                        'symbol': symbol,
                        'original_symbol': original_symbol,
                        'company': info.get('longName', symbol),
                        'currency': info.get('currency', 'AUD' if '.AX' in symbol else 'USD'),
                        'source': 'yahoo',
                        'data_points': len(df),
                        'start_date': dates[0],
                        'end_date': dates[-1],
                        'latest_price': float(latest_price),
                        'price_change': float(price_change),
                        'price_change_pct': float(price_change_pct),
                        'prices': prices,
                        'dates': dates,
                        'volumes': volumes,
                        'technical_indicators': indicators,
                        'predictions': predictions,
                        'backtest': backtest,
                        'is_real_data': True,
                        'fetch_time': datetime.now().isoformat(),
                        'from_cache': False
                    }
                    
                    # Cache the result
                    system_state.cache[cache_key] = (response_data, datetime.now())
                    system_state.fetch_history.append({
                        'symbol': symbol,
                        'time': datetime.now().isoformat(),
                        'source': 'yahoo'
                    })
                    
                    return response_data
                    
            except Exception as e:
                logger.error(f"Yahoo Finance error: {e}")
        
        # Try Alpha Vantage for US stocks
        if REQUESTS_AVAILABLE and not symbol.endswith('.AX'):
            try:
                url = 'https://www.alphavantage.co/query'
                params = {
                    'function': 'TIME_SERIES_DAILY',
                    'symbol': symbol,
                    'apikey': ALPHA_VANTAGE_API_KEY,
                    'outputsize': 'full'
                }
                
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                
                if 'Time Series (Daily)' in data:
                    time_series = data['Time Series (Daily)']
                    
                    # Determine date range based on period
                    period_days = {
                        '1d': 1, '5d': 5, '1mo': 30, '3mo': 90,
                        '6mo': 180, '1y': 365, '2y': 730, '5y': 1825
                    }
                    days = period_days.get(period, 30)
                    
                    dates = sorted(list(time_series.keys()))[-days:]
                    prices = [float(time_series[d]['4. close']) for d in dates]
                    volumes = [int(time_series[d]['5. volume']) for d in dates]
                    
                    # Calculate metrics
                    latest_price = prices[-1]
                    price_change = prices[-1] - prices[0]
                    price_change_pct = (price_change / prices[0] * 100)
                    
                    # Generate predictions
                    predictions = generate_predictions(symbol, prices)
                    
                    # Backtest
                    backtest = backtest_strategy(symbol, prices) if len(prices) > 50 else {}
                    
                    response_data = {
                        'symbol': symbol,
                        'original_symbol': original_symbol,
                        'company': symbol,
                        'currency': 'USD',
                        'source': 'alpha_vantage',
                        'data_points': len(dates),
                        'start_date': dates[0],
                        'end_date': dates[-1],
                        'latest_price': float(latest_price),
                        'price_change': float(price_change),
                        'price_change_pct': float(price_change_pct),
                        'prices': prices,
                        'dates': dates,
                        'volumes': volumes,
                        'technical_indicators': {},
                        'predictions': predictions,
                        'backtest': backtest,
                        'is_real_data': True,
                        'fetch_time': datetime.now().isoformat(),
                        'from_cache': False
                    }
                    
                    # Cache the result
                    system_state.cache[cache_key] = (response_data, datetime.now())
                    
                    return response_data
                    
            except Exception as e:
                logger.error(f"Alpha Vantage error: {e}")
        
        return None
        
    except Exception as e:
        logger.error(f"Fetch error: {e}")
        return None

# HTML Interface
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ML Stock Predictor - Production System</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f23;
            color: #e0e0e0;
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        
        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .card {
            background: #1a1a2e;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #2a2a3e;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        input, select {
            flex: 1;
            padding: 12px;
            background: #0f0f23;
            border: 1px solid #3a3a4e;
            border-radius: 8px;
            color: #e0e0e0;
            font-size: 16px;
        }
        
        button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: transform 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
        }
        
        .price-display {
            font-size: 3em;
            font-weight: bold;
            margin: 20px 0;
        }
        
        .positive { color: #4CAF50; }
        .negative { color: #f44336; }
        
        .indicator {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #2a2a3e;
        }
        
        .indicator-label {
            color: #888;
        }
        
        .indicator-value {
            color: #e0e0e0;
            font-weight: 600;
        }
        
        .chart-container {
            position: relative;
            height: 400px;
            margin-top: 20px;
        }
        
        .predictions-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 20px;
        }
        
        .prediction-box {
            background: #0f0f23;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #3a3a4e;
        }
        
        .prediction-period {
            color: #888;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        
        .prediction-price {
            font-size: 1.5em;
            font-weight: bold;
            margin: 5px 0;
        }
        
        .prediction-change {
            font-size: 0.9em;
        }
        
        .backtest-metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #2a2a3e;
        }
        
        .metric-label {
            color: #888;
        }
        
        .metric-value {
            color: #e0e0e0;
            font-weight: 600;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #888;
        }
        
        .error {
            background: #2a1f1f;
            border: 1px solid #f44336;
            color: #f44336;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
        
        .success {
            background: #1f2a1f;
            border: 1px solid #4CAF50;
            color: #4CAF50;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #2a2a3e;
        }
        
        .tab {
            padding: 10px 20px;
            background: none;
            border: none;
            color: #888;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.3s;
        }
        
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
            
            .predictions-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>🚀 ML Stock Predictor - Production System</h1>
            <p>Real-time data • Technical analysis • ML predictions • Backtesting</p>
        </div>
    </div>
    
    <div class="container">
        <div class="card">
            <div class="input-group">
                <input type="text" id="symbol" placeholder="Enter symbol (e.g., CBA, AAPL)" value="CBA">
                <select id="period">
                    <option value="1mo" selected>1 Month</option>
                    <option value="3mo">3 Months</option>
                    <option value="6mo">6 Months</option>
                    <option value="1y">1 Year</option>
                    <option value="2y">2 Years</option>
                    <option value="5y">5 Years</option>
                </select>
                <button onclick="fetchData()">Analyze</button>
            </div>
            
            <div class="tabs">
                <button class="tab active" onclick="switchTab('overview')">Overview</button>
                <button class="tab" onclick="switchTab('technical')">Technical</button>
                <button class="tab" onclick="switchTab('predictions')">Predictions</button>
                <button class="tab" onclick="switchTab('backtest')">Backtest</button>
                <button class="tab" onclick="switchTab('chart')">Chart</button>
            </div>
        </div>
        
        <div id="results">
            <!-- Overview Tab -->
            <div id="overview-tab" class="tab-content active">
                <div class="grid">
                    <div class="card">
                        <h2>Price Information</h2>
                        <div id="price-info">
                            <p style="color: #888; text-align: center; padding: 40px;">
                                Enter a symbol and click Analyze to begin
                            </p>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h2>Market Summary</h2>
                        <div id="market-summary">
                            <p style="color: #888; text-align: center; padding: 40px;">
                                No data available
                            </p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Technical Tab -->
            <div id="technical-tab" class="tab-content">
                <div class="grid">
                    <div class="card">
                        <h2>Moving Averages</h2>
                        <div id="moving-averages"></div>
                    </div>
                    
                    <div class="card">
                        <h2>Momentum Indicators</h2>
                        <div id="momentum-indicators"></div>
                    </div>
                    
                    <div class="card">
                        <h2>Volatility Indicators</h2>
                        <div id="volatility-indicators"></div>
                    </div>
                </div>
            </div>
            
            <!-- Predictions Tab -->
            <div id="predictions-tab" class="tab-content">
                <div class="card">
                    <h2>ML Price Predictions</h2>
                    <div id="predictions-content"></div>
                </div>
            </div>
            
            <!-- Backtest Tab -->
            <div id="backtest-tab" class="tab-content">
                <div class="card">
                    <h2>Strategy Backtest Results</h2>
                    <div id="backtest-content"></div>
                </div>
            </div>
            
            <!-- Chart Tab -->
            <div id="chart-tab" class="tab-content">
                <div class="card">
                    <h2>Price Chart</h2>
                    <div class="chart-container">
                        <canvas id="priceChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let currentData = null;
        let priceChart = null;
        
        function switchTab(tabName) {
            // Update tab buttons
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Update tab content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(tabName + '-tab').classList.add('active');
        }
        
        async function fetchData() {
            const symbol = document.getElementById('symbol').value.trim().toUpperCase();
            const period = document.getElementById('period').value;
            
            if (!symbol) {
                alert('Please enter a stock symbol');
                return;
            }
            
            // Show loading
            document.getElementById('price-info').innerHTML = '<div class="loading">Loading...</div>';
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({symbol, period})
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to fetch data');
                }
                
                currentData = data;
                displayData(data);
                
            } catch (error) {
                document.getElementById('price-info').innerHTML = 
                    '<div class="error">Error: ' + error.message + '</div>';
            }
        }
        
        function displayData(data) {
            // Overview - Price Information
            const changeClass = data.price_change >= 0 ? 'positive' : 'negative';
            const changeSymbol = data.price_change >= 0 ? '▲' : '▼';
            
            document.getElementById('price-info').innerHTML = `
                <h3>${data.symbol} - ${data.company}</h3>
                <div class="price-display">${data.currency} $${data.latest_price.toFixed(2)}</div>
                <div class="${changeClass}" style="font-size: 1.2em;">
                    ${changeSymbol} ${Math.abs(data.price_change).toFixed(2)} 
                    (${data.price_change_pct >= 0 ? '+' : ''}${data.price_change_pct.toFixed(2)}%)
                </div>
            `;
            
            // Market Summary
            document.getElementById('market-summary').innerHTML = `
                <div class="indicator">
                    <span class="indicator-label">Data Points</span>
                    <span class="indicator-value">${data.data_points}</span>
                </div>
                <div class="indicator">
                    <span class="indicator-label">Period</span>
                    <span class="indicator-value">${data.start_date} to ${data.end_date}</span>
                </div>
                <div class="indicator">
                    <span class="indicator-label">Source</span>
                    <span class="indicator-value">${data.source}</span>
                </div>
                <div class="indicator">
                    <span class="indicator-label">Volume</span>
                    <span class="indicator-value">${(data.volumes[data.volumes.length-1] / 1000000).toFixed(2)}M</span>
                </div>
            `;
            
            // Technical Indicators
            if (data.technical_indicators) {
                const indicators = data.technical_indicators;
                
                // Moving Averages
                document.getElementById('moving-averages').innerHTML = `
                    <div class="indicator">
                        <span class="indicator-label">SMA 20</span>
                        <span class="indicator-value">$${(indicators.SMA_20 || 0).toFixed(2)}</span>
                    </div>
                    <div class="indicator">
                        <span class="indicator-label">SMA 50</span>
                        <span class="indicator-value">$${(indicators.SMA_50 || 0).toFixed(2)}</span>
                    </div>
                    <div class="indicator">
                        <span class="indicator-label">EMA 12</span>
                        <span class="indicator-value">$${(indicators.EMA_12 || 0).toFixed(2)}</span>
                    </div>
                    <div class="indicator">
                        <span class="indicator-label">EMA 26</span>
                        <span class="indicator-value">$${(indicators.EMA_26 || 0).toFixed(2)}</span>
                    </div>
                `;
                
                // Momentum Indicators
                document.getElementById('momentum-indicators').innerHTML = `
                    <div class="indicator">
                        <span class="indicator-label">RSI</span>
                        <span class="indicator-value">${(indicators.RSI || 0).toFixed(2)}</span>
                    </div>
                    <div class="indicator">
                        <span class="indicator-label">MACD</span>
                        <span class="indicator-value">${(indicators.MACD || 0).toFixed(4)}</span>
                    </div>
                    <div class="indicator">
                        <span class="indicator-label">MACD Signal</span>
                        <span class="indicator-value">${(indicators.MACD_signal || 0).toFixed(4)}</span>
                    </div>
                `;
                
                // Volatility Indicators
                document.getElementById('volatility-indicators').innerHTML = `
                    <div class="indicator">
                        <span class="indicator-label">Bollinger Upper</span>
                        <span class="indicator-value">$${(indicators.BB_upper || 0).toFixed(2)}</span>
                    </div>
                    <div class="indicator">
                        <span class="indicator-label">Bollinger Middle</span>
                        <span class="indicator-value">$${(indicators.BB_middle || 0).toFixed(2)}</span>
                    </div>
                    <div class="indicator">
                        <span class="indicator-label">Bollinger Lower</span>
                        <span class="indicator-value">$${(indicators.BB_lower || 0).toFixed(2)}</span>
                    </div>
                    <div class="indicator">
                        <span class="indicator-label">Volatility (Annual)</span>
                        <span class="indicator-value">${((indicators.Volatility || 0) * 100).toFixed(2)}%</span>
                    </div>
                `;
            }
            
            // Predictions
            if (data.predictions && !data.predictions.error) {
                let predictionsHTML = '<div class="predictions-grid">';
                
                ['1_day', '7_day', '30_day'].forEach(period => {
                    if (data.predictions[period]) {
                        const pred = data.predictions[period];
                        const changeClass = pred.change >= 0 ? 'positive' : 'negative';
                        
                        predictionsHTML += `
                            <div class="prediction-box">
                                <div class="prediction-period">${period.replace('_', ' ')}</div>
                                <div class="prediction-price">$${pred.price.toFixed(2)}</div>
                                <div class="prediction-change ${changeClass}">
                                    ${pred.change >= 0 ? '+' : ''}${pred.change.toFixed(2)}%
                                </div>
                                <div style="color: #888; font-size: 0.8em;">
                                    Confidence: ${(pred.confidence * 100).toFixed(1)}%
                                </div>
                            </div>
                        `;
                    }
                });
                
                predictionsHTML += '</div>';
                
                if (data.predictions.model_info) {
                    predictionsHTML += `
                        <div style="margin-top: 20px; padding: 15px; background: #0f0f23; border-radius: 8px;">
                            <h3 style="color: #667eea; margin-bottom: 10px;">Model Information</h3>
                            <div class="indicator">
                                <span class="indicator-label">Model Type</span>
                                <span class="indicator-value">${data.predictions.model_info.type}</span>
                            </div>
                            ${data.predictions.model_info.r2_score ? `
                                <div class="indicator">
                                    <span class="indicator-label">R² Score</span>
                                    <span class="indicator-value">${data.predictions.model_info.r2_score.toFixed(4)}</span>
                                </div>
                            ` : ''}
                        </div>
                    `;
                }
                
                document.getElementById('predictions-content').innerHTML = predictionsHTML;
            }
            
            // Backtest
            if (data.backtest && !data.backtest.error) {
                const backtest = data.backtest;
                const returnClass = backtest.total_return >= 0 ? 'positive' : 'negative';
                
                document.getElementById('backtest-content').innerHTML = `
                    <div class="backtest-metric">
                        <span class="metric-label">Strategy</span>
                        <span class="metric-value">${backtest.strategy}</span>
                    </div>
                    <div class="backtest-metric">
                        <span class="metric-label">Initial Capital</span>
                        <span class="metric-value">$${backtest.initial_capital.toFixed(2)}</span>
                    </div>
                    <div class="backtest-metric">
                        <span class="metric-label">Final Value</span>
                        <span class="metric-value">$${backtest.final_value.toFixed(2)}</span>
                    </div>
                    <div class="backtest-metric">
                        <span class="metric-label">Total Return</span>
                        <span class="metric-value ${returnClass}">
                            ${backtest.total_return >= 0 ? '+' : ''}${backtest.total_return.toFixed(2)}%
                        </span>
                    </div>
                    <div class="backtest-metric">
                        <span class="metric-label">Number of Trades</span>
                        <span class="metric-value">${backtest.num_trades}</span>
                    </div>
                    <div class="backtest-metric">
                        <span class="metric-label">Win Rate</span>
                        <span class="metric-value">${(backtest.win_rate * 100).toFixed(1)}%</span>
                    </div>
                    <div class="backtest-metric">
                        <span class="metric-label">Sharpe Ratio</span>
                        <span class="metric-value">${backtest.sharpe_ratio.toFixed(3)}</span>
                    </div>
                    <div class="backtest-metric">
                        <span class="metric-label">Max Drawdown</span>
                        <span class="metric-value" style="color: #f44336;">
                            ${backtest.max_drawdown.toFixed(2)}%
                        </span>
                    </div>
                `;
            }
            
            // Chart
            drawChart(data);
        }
        
        function drawChart(data) {
            const ctx = document.getElementById('priceChart').getContext('2d');
            
            if (priceChart) {
                priceChart.destroy();
            }
            
            // Limit data points for performance
            const maxPoints = 100;
            const step = Math.ceil(data.dates.length / maxPoints);
            const dates = data.dates.filter((_, i) => i % step === 0);
            const prices = data.prices.filter((_, i) => i % step === 0);
            
            priceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: data.symbol + ' Price',
                        data: prices,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 2,
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#e0e0e0'
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: {
                                color: '#888',
                                maxTicksLimit: 10
                            },
                            grid: {
                                color: '#2a2a3e'
                            }
                        },
                        y: {
                            ticks: {
                                color: '#888',
                                callback: function(value) {
                                    return '$' + value.toFixed(2);
                                }
                            },
                            grid: {
                                color: '#2a2a3e'
                            }
                        }
                    }
                }
            });
        }
        
        // Initialize on load
        window.addEventListener('load', () => {
            // You can auto-fetch a default stock here if desired
            // fetchData();
        });
    </script>
</body>
</html>
"""

# Initialize database on startup
init_database()

# Routes
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE)

@app.route('/api/status')
def api_status():
    """System status endpoint"""
    system_state.request_count += 1
    
    return jsonify({
        'status': 'running',
        'version': '2.0.0-production',
        'uptime': str(datetime.now() - system_state.start_time),
        'requests_served': system_state.request_count,
        'cache_size': len(system_state.cache),
        'fetch_history': list(system_state.fetch_history)[-10:],
        'components': {
            'yahoo_finance': YF_AVAILABLE,
            'alpha_vantage': REQUESTS_AVAILABLE,
            'ml_predictions': ML_AVAILABLE,
            'database': os.path.exists(DATABASE_FILE)
        }
    })

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def api_analyze():
    """Main analysis endpoint"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        system_state.request_count += 1
        
        data = request.get_json()
        symbol = data.get('symbol', '').upper().strip()
        period = data.get('period', '1mo')
        
        if not symbol:
            return jsonify({'error': 'Symbol required'}), 400
        
        logger.info(f"Analyzing {symbol} for period {period}")
        
        # Fetch comprehensive data
        result = fetch_stock_data(symbol, period)
        
        if result:
            return jsonify(result)
        else:
            return jsonify({'error': f'Could not fetch data for {symbol}'}), 404
            
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<symbol>')
def api_history(symbol):
    """Get historical data from database"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, close, volume 
            FROM stock_data 
            WHERE symbol = ? 
            ORDER BY date DESC 
            LIMIT 365
        ''', (symbol.upper(),))
        
        rows = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'symbol': symbol.upper(),
            'data': [{'date': row[0], 'close': row[1], 'volume': row[2]} for row in rows]
        })
        
    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/<symbol>')
def api_export(symbol):
    """Export data to CSV"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        df = pd.read_sql_query(
            "SELECT * FROM stock_data WHERE symbol = ? ORDER BY date",
            conn,
            params=(symbol.upper(),)
        )
        conn.close()
        
        csv_file = f"{symbol}_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(csv_file, index=False)
        
        return send_file(csv_file, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({'error': str(e)}), 500

def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("   ML STOCK PREDICTOR - PRODUCTION SYSTEM")
    print("="*80)
    print(f"Version: 2.0.0-production")
    print(f"Python: {sys.version}")
    print(f"NumPy: {np.__version__ if YF_AVAILABLE else 'N/A'}")
    print("-"*80)
    print("Features:")
    print(f"  ✅ Real-time data fetching")
    print(f"  ✅ Technical indicators (RSI, MACD, Bollinger)")
    print(f"  ✅ ML predictions ({'enabled' if ML_AVAILABLE else 'statistical fallback'})")
    print(f"  ✅ Backtesting engine")
    print(f"  ✅ Database storage")
    print(f"  ✅ Data export to CSV")
    print(f"  ✅ Multi-source data (Yahoo + Alpha Vantage)")
    print(f"  ✅ Australian stocks auto-detection")
    print("="*80)
    print(f"\n🚀 Starting server at: http://localhost:{PORT}")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='127.0.0.1', port=PORT, debug=False)

if __name__ == '__main__':
    main()