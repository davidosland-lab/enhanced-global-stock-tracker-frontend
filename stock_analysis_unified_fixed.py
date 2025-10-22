#!/usr/bin/env python3
"""
Unified Stock Analysis System - FIXED VERSION
Combines Yahoo Finance (primary) and Alpha Vantage (fallback)
Fixes the 404 errors by removing problematic Yahoo Finance parameters
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
import requests
import warnings
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import ta
import traceback
import sys
import os

warnings.filterwarnings('ignore')

# Flask app setup
app = Flask(__name__)
CORS(app)

# Configuration
ALPHA_VANTAGE_API_KEY = "68ZFANK047DL0KSR"

# Australian stock list
AUSTRALIAN_STOCKS = ['CBA', 'BHP', 'CSL', 'NAB', 'ANZ', 'WBC', 'WES', 'MQG', 'TLS', 'WOW', 
                     'RIO', 'FMG', 'TCL', 'ALL', 'REA', 'GMG', 'AMC', 'SUN', 'QBE', 'IAG']

class MLPredictor:
    """Machine Learning prediction model for stock prices"""
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=5,  # Prevent overfitting
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_features(self, df):
        """Prepare technical features for ML model"""
        features = pd.DataFrame(index=df.index)
        
        # Price features
        features['returns'] = df['Close'].pct_change()
        features['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        features['volatility'] = features['returns'].rolling(20).std()
        
        # Moving averages
        features['sma_5'] = df['Close'].rolling(5).mean()
        features['sma_20'] = df['Close'].rolling(20).mean()
        features['sma_50'] = df['Close'].rolling(50).mean()
        features['sma_ratio'] = features['sma_5'] / features['sma_20']
        features['price_to_sma20'] = df['Close'] / features['sma_20']
        
        # RSI
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / (loss + 1e-10)
        features['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema12 = df['Close'].ewm(span=12).mean()
        ema26 = df['Close'].ewm(span=26).mean()
        features['macd'] = ema12 - ema26
        features['macd_signal'] = features['macd'].ewm(span=9).mean()
        features['macd_diff'] = features['macd'] - features['macd_signal']
        
        # Volume features
        features['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
        features['volume_trend'] = df['Volume'].rolling(5).mean() / df['Volume'].rolling(20).mean()
        
        # Price position
        features['price_position'] = (df['Close'] - df['Low']) / (df['High'] - df['Low'] + 1e-10)
        features['high_low_ratio'] = df['High'] / (df['Low'] + 1e-10)
        
        # Bollinger Bands
        bb_sma = df['Close'].rolling(20).mean()
        bb_std = df['Close'].rolling(20).std()
        features['bb_upper'] = bb_sma + 2 * bb_std
        features['bb_lower'] = bb_sma - 2 * bb_std
        features['bb_position'] = (df['Close'] - bb_sma) / (bb_std + 1e-10)
        features['bb_width'] = (features['bb_upper'] - features['bb_lower']) / bb_sma
        
        # ATR (Average True Range)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        features['atr'] = true_range.rolling(14).mean()
        
        # Stochastic Oscillator
        low_14 = df['Low'].rolling(14).min()
        high_14 = df['High'].rolling(14).max()
        features['stoch_k'] = 100 * ((df['Close'] - low_14) / (high_14 - low_14 + 1e-10))
        features['stoch_d'] = features['stoch_k'].rolling(3).mean()
        
        return features.dropna()
    
    def train(self, df):
        """Train the ML model on historical data"""
        if len(df) < 100:
            print(f"Not enough data for training: {len(df)} rows")
            return False
        
        features = self.prepare_features(df)
        if len(features) < 50:
            print(f"Not enough features after preparation: {len(features)} rows")
            return False
        
        # Prepare target (next day return)
        y = df['Close'].pct_change().shift(-1).loc[features.index]
        
        # Remove last row (no future data)
        features = features[:-1]
        y = y[:-1]
        
        # Split data (80/20 split, no shuffle for time series)
        split_idx = int(len(features) * 0.8)
        X_train = features[:split_idx]
        X_test = features[split_idx:]
        y_train = y[:split_idx]
        y_test = y[split_idx:]
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Calculate accuracy
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        print(f"Model trained - Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
        return True
    
    def predict(self, df, days=5):
        """Predict future prices"""
        if not self.is_trained:
            return []
        
        features = self.prepare_features(df)
        if len(features) == 0:
            return []
        
        predictions = []
        current_price = float(df['Close'].iloc[-1])
        
        # Get last features
        last_features = features.iloc[-1:].copy()
        last_features_scaled = self.scaler.transform(last_features)
        
        for i in range(days):
            # Predict next return
            pred_return = self.model.predict(last_features_scaled)[0]
            
            # Calculate predicted price
            pred_price = current_price * (1 + pred_return)
            
            # Store prediction
            pred_date = df.index[-1] + timedelta(days=i+1)
            predictions.append({
                'date': pred_date.strftime('%Y-%m-%d'),
                'predicted_price': round(pred_price, 2),
                'confidence': 0.7 - (i * 0.05)  # Decrease confidence over time
            })
            
            # Update for next prediction
            current_price = pred_price
            
            # Simple feature update (would be more sophisticated in production)
            last_features_scaled[0][0] = pred_return
        
        return predictions

class UnifiedDataFetcher:
    """Unified data fetcher using Yahoo Finance (primary) and Alpha Vantage (fallback)"""
    
    def __init__(self):
        self.av_api_key = ALPHA_VANTAGE_API_KEY
        self.au_stocks = AUSTRALIAN_STOCKS
    
    def _add_au_suffix(self, symbol: str) -> str:
        """Add .AX suffix for Australian stocks"""
        symbol_upper = symbol.upper().replace('.AX', '')
        if symbol_upper in self.au_stocks:
            return f"{symbol_upper}.AX"
        return symbol
    
    def fetch_data(self, symbol: str, period: str = '1mo'):
        """Fetch data from Yahoo Finance, fallback to Alpha Vantage if needed"""
        
        # Try Yahoo Finance first
        data, source, price = self.fetch_yahoo_data(symbol, period)
        if data is not None and not data.empty:
            return data, source, price
        
        print(f"Yahoo Finance failed, trying Alpha Vantage...")
        
        # Fallback to Alpha Vantage
        data, source, price = self.fetch_alpha_vantage_data(symbol, period)
        if data is not None and not data.empty:
            return data, source, price
        
        # If both fail, return error indication
        print(f"Both data sources failed for {symbol}")
        return None, "Error", 0
    
    def fetch_yahoo_data(self, symbol: str, period: str = '1mo'):
        """Fetch real data from Yahoo Finance - SIMPLIFIED CALLS"""
        try:
            symbol = self._add_au_suffix(symbol)
            print(f"Fetching {symbol} from Yahoo Finance for period {period}")
            
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # CRITICAL FIX: Use simple history() call without problematic parameters
            # Remove prepost=False and actions=False which cause 404 errors
            hist = ticker.history(period=period)
            
            if hist.empty:
                print(f"Yahoo Finance returned empty data for {symbol}")
                return None, None, None
            
            print(f"Yahoo Finance: Successfully fetched {len(hist)} data points")
            
            # Get current price
            try:
                info = ticker.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice') or hist['Close'].iloc[-1]
            except:
                current_price = hist['Close'].iloc[-1]
            
            # Ensure price is float
            current_price = float(current_price)
            
            return hist, "Yahoo Finance", current_price
            
        except Exception as e:
            print(f"Yahoo Finance error for {symbol}: {str(e)}")
            return None, None, None
    
    def fetch_alpha_vantage_data(self, symbol: str, period: str = '1mo'):
        """Fetch real data from Alpha Vantage as fallback"""
        try:
            # Remove .AX for Alpha Vantage (doesn't support ASX suffix)
            av_symbol = symbol.replace('.AX', '')
            print(f"Fetching {av_symbol} from Alpha Vantage")
            
            # Determine API function based on period
            if period in ['1d', '5d']:
                # Use intraday data for short periods
                interval = '5min' if period == '1d' else '30min'
                params = {
                    'function': 'TIME_SERIES_INTRADAY',
                    'symbol': av_symbol,
                    'interval': interval,
                    'apikey': self.av_api_key,
                    'outputsize': 'full',
                    'datatype': 'json'
                }
                time_key = f'Time Series ({interval})'
            else:
                # Use daily data for longer periods
                params = {
                    'function': 'TIME_SERIES_DAILY_ADJUSTED',
                    'symbol': av_symbol,
                    'apikey': self.av_api_key,
                    'outputsize': 'full',
                    'datatype': 'json'
                }
                time_key = 'Time Series (Daily)'
            
            # Make API request
            response = requests.get('https://www.alphavantage.co/query', params=params, timeout=10)
            data = response.json()
            
            # Check for errors
            if 'Error Message' in data:
                print(f"Alpha Vantage error: {data['Error Message']}")
                return None, None, None
            
            if 'Note' in data:
                print(f"Alpha Vantage API limit reached")
                return None, None, None
            
            if time_key not in data:
                print(f"Alpha Vantage: No time series data found")
                return None, None, None
            
            # Parse time series data
            time_series = data[time_key]
            df_data = []
            
            for timestamp, values in time_series.items():
                df_data.append({
                    'Date': pd.to_datetime(timestamp),
                    'Open': float(values.get('1. open', 0)),
                    'High': float(values.get('2. high', 0)),
                    'Low': float(values.get('3. low', 0)),
                    'Close': float(values.get('4. close', values.get('5. adjusted close', 0))),
                    'Volume': int(values.get('6. volume', values.get('5. volume', 0)))
                })
            
            if not df_data:
                return None, None, None
            
            # Create DataFrame
            df = pd.DataFrame(df_data)
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)
            
            # Filter based on period
            now = datetime.now()
            period_days = {
                '1d': 1, '5d': 5, '1mo': 30, '3mo': 90,
                '6mo': 180, '1y': 365, '5y': 1825
            }
            
            if period in period_days:
                cutoff = now - timedelta(days=period_days[period])
                df = df[df.index >= cutoff]
            
            if df.empty:
                return None, None, None
            
            print(f"Alpha Vantage: Fetched {len(df)} data points")
            current_price = float(df['Close'].iloc[-1])
            
            return df, "Alpha Vantage", current_price
            
        except Exception as e:
            print(f"Alpha Vantage error: {str(e)}")
            return None, None, None

class TechnicalAnalyzer:
    """Technical analysis calculator"""
    
    @staticmethod
    def calculate_all(df):
        """Calculate all technical indicators"""
        indicators = {}
        
        if df is None or df.empty or len(df) < 20:
            return indicators
        
        try:
            # Current price and change
            current_price = float(df['Close'].iloc[-1])
            prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else current_price
            change = current_price - prev_close
            change_pct = (change / prev_close * 100) if prev_close != 0 else 0
            
            indicators['current_price'] = round(current_price, 2)
            indicators['change'] = round(change, 2)
            indicators['change_percent'] = round(change_pct, 2)
            
            # Moving Averages
            indicators['sma_20'] = round(float(df['Close'].rolling(20).mean().iloc[-1]), 2)
            if len(df) >= 50:
                indicators['sma_50'] = round(float(df['Close'].rolling(50).mean().iloc[-1]), 2)
            if len(df) >= 200:
                indicators['sma_200'] = round(float(df['Close'].rolling(200).mean().iloc[-1]), 2)
            
            indicators['ema_12'] = round(float(df['Close'].ewm(span=12).mean().iloc[-1]), 2)
            indicators['ema_26'] = round(float(df['Close'].ewm(span=26).mean().iloc[-1]), 2)
            
            # RSI
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            rs = gain / (loss + 1e-10)
            rsi = 100 - (100 / (1 + rs))
            indicators['rsi'] = round(float(rsi.iloc[-1]), 2)
            
            # Determine RSI signal
            if indicators['rsi'] < 30:
                indicators['rsi_signal'] = 'Oversold'
            elif indicators['rsi'] > 70:
                indicators['rsi_signal'] = 'Overbought'
            else:
                indicators['rsi_signal'] = 'Neutral'
            
            # MACD
            ema12 = df['Close'].ewm(span=12).mean()
            ema26 = df['Close'].ewm(span=26).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9).mean()
            macd_histogram = macd_line - signal_line
            
            indicators['macd'] = round(float(macd_line.iloc[-1]), 2)
            indicators['macd_signal'] = round(float(signal_line.iloc[-1]), 2)
            indicators['macd_histogram'] = round(float(macd_histogram.iloc[-1]), 2)
            
            # MACD Signal
            if indicators['macd'] > indicators['macd_signal']:
                indicators['macd_trend'] = 'Bullish'
            else:
                indicators['macd_trend'] = 'Bearish'
            
            # Bollinger Bands
            bb_sma = df['Close'].rolling(20).mean()
            bb_std = df['Close'].rolling(20).std()
            bb_upper = bb_sma + 2 * bb_std
            bb_lower = bb_sma - 2 * bb_std
            
            indicators['bb_upper'] = round(float(bb_upper.iloc[-1]), 2)
            indicators['bb_middle'] = round(float(bb_sma.iloc[-1]), 2)
            indicators['bb_lower'] = round(float(bb_lower.iloc[-1]), 2)
            
            # Bollinger Band Signal
            if current_price > indicators['bb_upper']:
                indicators['bb_signal'] = 'Overbought'
            elif current_price < indicators['bb_lower']:
                indicators['bb_signal'] = 'Oversold'
            else:
                indicators['bb_signal'] = 'Neutral'
            
            # ATR (Average True Range)
            high_low = df['High'] - df['Low']
            high_close = np.abs(df['High'] - df['Close'].shift())
            low_close = np.abs(df['Low'] - df['Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            atr = true_range.rolling(14).mean()
            indicators['atr'] = round(float(atr.iloc[-1]), 2)
            
            # Volume analysis
            indicators['volume'] = int(df['Volume'].iloc[-1])
            indicators['volume_avg'] = int(df['Volume'].rolling(20).mean().iloc[-1])
            volume_ratio = indicators['volume'] / indicators['volume_avg'] if indicators['volume_avg'] > 0 else 1
            indicators['volume_ratio'] = round(volume_ratio, 2)
            
            # Stochastic Oscillator
            low_14 = df['Low'].rolling(14).min()
            high_14 = df['High'].rolling(14).max()
            k_percent = 100 * ((df['Close'] - low_14) / (high_14 - low_14 + 1e-10))
            d_percent = k_percent.rolling(3).mean()
            
            indicators['stoch_k'] = round(float(k_percent.iloc[-1]), 2)
            indicators['stoch_d'] = round(float(d_percent.iloc[-1]), 2)
            
            # Support and Resistance (simple method)
            recent_high = float(df['High'].tail(20).max())
            recent_low = float(df['Low'].tail(20).min())
            indicators['resistance'] = round(recent_high, 2)
            indicators['support'] = round(recent_low, 2)
            
            # Overall trend signal
            signals = []
            if indicators['rsi'] < 30:
                signals.append('Buy')
            elif indicators['rsi'] > 70:
                signals.append('Sell')
            
            if indicators['macd'] > indicators['macd_signal']:
                signals.append('Buy')
            else:
                signals.append('Sell')
            
            if current_price < indicators['bb_lower']:
                signals.append('Buy')
            elif current_price > indicators['bb_upper']:
                signals.append('Sell')
            
            buy_signals = signals.count('Buy')
            sell_signals = signals.count('Sell')
            
            if buy_signals > sell_signals:
                indicators['overall_signal'] = 'Buy'
            elif sell_signals > buy_signals:
                indicators['overall_signal'] = 'Sell'
            else:
                indicators['overall_signal'] = 'Hold'
            
        except Exception as e:
            print(f"Error calculating indicators: {str(e)}")
            traceback.print_exc()
        
        return indicators

# Create global instances
data_fetcher = UnifiedDataFetcher()
ml_predictor = MLPredictor()
tech_analyzer = TechnicalAnalyzer()

# API Routes
@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get stock data with technical indicators and ML predictions"""
    try:
        period = request.args.get('period', '1mo')
        
        # Fetch data
        df, source, current_price = data_fetcher.fetch_data(symbol, period)
        
        if df is None or df.empty:
            return jsonify({
                'error': 'Failed to fetch data',
                'symbol': symbol,
                'source': 'None'
            }), 404
        
        # Calculate technical indicators
        indicators = tech_analyzer.calculate_all(df)
        
        # Train ML model and get predictions
        predictions = []
        if ml_predictor.train(df):
            predictions = ml_predictor.predict(df, days=5)
        
        # Prepare candlestick data for frontend
        candlestick_data = []
        for index, row in df.iterrows():
            candlestick_data.append({
                'date': index.strftime('%Y-%m-%d %H:%M:%S'),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            })
        
        response = {
            'symbol': symbol,
            'source': source,
            'period': period,
            'current_price': current_price,
            'indicators': indicators,
            'predictions': predictions,
            'candlestick_data': candlestick_data,
            'data_points': len(df),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in get_stock_data: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """Run backtesting simulation"""
    try:
        data = request.json
        symbol = data.get('symbol', 'AAPL')
        strategy = data.get('strategy', 'ma_crossover')
        period = data.get('period', '1y')
        
        # Fetch historical data
        df, source, _ = data_fetcher.fetch_data(symbol, period)
        
        if df is None or df.empty:
            return jsonify({'error': 'Failed to fetch data for backtesting'}), 404
        
        # Simple MA crossover strategy
        if strategy == 'ma_crossover':
            # Calculate moving averages
            df['SMA20'] = df['Close'].rolling(20).mean()
            df['SMA50'] = df['Close'].rolling(50).mean()
            
            # Generate signals
            df['Signal'] = 0
            df.loc[df['SMA20'] > df['SMA50'], 'Signal'] = 1  # Buy signal
            df.loc[df['SMA20'] < df['SMA50'], 'Signal'] = -1  # Sell signal
            
            # Calculate returns
            df['Returns'] = df['Close'].pct_change()
            df['Strategy_Returns'] = df['Signal'].shift(1) * df['Returns']
            
            # Calculate cumulative returns
            df['Cumulative_Returns'] = (1 + df['Returns']).cumprod()
            df['Cumulative_Strategy_Returns'] = (1 + df['Strategy_Returns']).cumprod()
            
            # Calculate metrics
            total_return = float(df['Cumulative_Strategy_Returns'].iloc[-1] - 1) * 100
            buy_hold_return = float(df['Cumulative_Returns'].iloc[-1] - 1) * 100
            
            # Count trades
            df['Position'] = df['Signal'].diff()
            trades = len(df[df['Position'] != 0])
            
            # Sharpe ratio (simplified)
            sharpe_ratio = df['Strategy_Returns'].mean() / (df['Strategy_Returns'].std() + 1e-10) * np.sqrt(252)
            
            results = {
                'strategy': strategy,
                'symbol': symbol,
                'period': period,
                'total_return': round(total_return, 2),
                'buy_hold_return': round(buy_hold_return, 2),
                'trades': trades,
                'sharpe_ratio': round(sharpe_ratio, 2),
                'data_source': source
            }
            
            return jsonify(results)
        
        return jsonify({'error': 'Unknown strategy'}), 400
        
    except Exception as e:
        print(f"Error in backtesting: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    """Serve the main HTML interface"""
    return render_template_string(HTML_TEMPLATE)

# HTML Template with Chart.js for candlestick charts
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis System - Unified</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial"></script>
    <script src="https://cdn.jsdelivr.net/npm/date-fns@2.29.3/index.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .search-section {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .search-controls {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        input[type="text"] {
            flex: 1;
            min-width: 200px;
            padding: 12px 20px;
            border: 2px solid #e1e8ed;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        select {
            padding: 12px 20px;
            border: 2px solid #e1e8ed;
            border-radius: 10px;
            font-size: 16px;
            background: white;
            cursor: pointer;
            transition: border-color 0.3s;
        }
        
        select:focus {
            outline: none;
            border-color: #667eea;
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
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .content-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            height: 500px;
            position: relative;
        }
        
        .indicator-item {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            margin: 5px 0;
            background: #f8f9fa;
            border-radius: 8px;
            transition: background 0.2s;
        }
        
        .indicator-item:hover {
            background: #e9ecef;
        }
        
        .indicator-label {
            font-weight: 600;
            color: #495057;
        }
        
        .indicator-value {
            font-weight: 700;
            color: #333;
        }
        
        .positive {
            color: #28a745;
        }
        
        .negative {
            color: #dc3545;
        }
        
        .neutral {
            color: #6c757d;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
            color: #6c757d;
        }
        
        .loading.active {
            display: block;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            display: none;
        }
        
        .error.active {
            display: block;
        }
        
        .prediction-item {
            padding: 10px;
            margin: 5px 0;
            background: #d1ecf1;
            border-radius: 8px;
            border-left: 4px solid #0c5460;
        }
        
        .data-source {
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 10px;
        }
        
        .signal-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
            margin-left: 10px;
        }
        
        .signal-buy {
            background: #d4edda;
            color: #155724;
        }
        
        .signal-sell {
            background: #f8d7da;
            color: #721c24;
        }
        
        .signal-hold {
            background: #fff3cd;
            color: #856404;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Unified Stock Analysis System</h1>
            <p>Real-time data from Yahoo Finance & Alpha Vantage with ML predictions</p>
        </div>
        
        <div class="search-section">
            <div class="search-controls">
                <input type="text" id="symbolInput" placeholder="Enter stock symbol (e.g., AAPL, CBA)" value="AAPL">
                <select id="periodSelect">
                    <option value="1d">1 Day</option>
                    <option value="5d">5 Days</option>
                    <option value="1mo" selected>1 Month</option>
                    <option value="3mo">3 Months</option>
                    <option value="6mo">6 Months</option>
                    <option value="1y">1 Year</option>
                    <option value="5y">5 Years</option>
                </select>
                <button onclick="fetchStockData()">Analyze</button>
                <button onclick="runBacktest()">Run Backtest</button>
            </div>
        </div>
        
        <div class="error" id="errorMessage"></div>
        
        <div class="chart-container">
            <h2>Price Chart</h2>
            <div class="loading" id="chartLoading">Loading chart data...</div>
            <canvas id="priceChart"></canvas>
            <div class="data-source" id="dataSource"></div>
        </div>
        
        <div class="content-grid">
            <div class="card">
                <h2>Price Information</h2>
                <div id="priceInfo" class="loading">Loading...</div>
            </div>
            
            <div class="card">
                <h2>Technical Indicators</h2>
                <div id="technicalIndicators" class="loading">Loading...</div>
            </div>
            
            <div class="card">
                <h2>ML Predictions</h2>
                <div id="predictions" class="loading">Loading...</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Backtesting Results</h2>
            <div id="backtestResults" class="loading">Click "Run Backtest" to see results</div>
        </div>
    </div>
    
    <script>
        let chartInstance = null;
        
        async function fetchStockData() {
            const symbol = document.getElementById('symbolInput').value.toUpperCase();
            const period = document.getElementById('periodSelect').value;
            
            if (!symbol) {
                showError('Please enter a stock symbol');
                return;
            }
            
            // Show loading states
            document.getElementById('chartLoading').classList.add('active');
            document.getElementById('priceInfo').classList.add('loading');
            document.getElementById('technicalIndicators').classList.add('loading');
            document.getElementById('predictions').classList.add('loading');
            hideError();
            
            try {
                const response = await fetch(`/api/stock/${symbol}?period=${period}`);
                const data = await response.json();
                
                if (response.ok) {
                    displayData(data);
                    drawChart(data);
                } else {
                    showError(data.error || 'Failed to fetch stock data');
                }
            } catch (error) {
                showError('Network error: ' + error.message);
            } finally {
                document.getElementById('chartLoading').classList.remove('active');
            }
        }
        
        function displayData(data) {
            // Display price information
            const priceInfo = document.getElementById('priceInfo');
            const indicators = data.indicators || {};
            
            priceInfo.innerHTML = `
                <div class="indicator-item">
                    <span class="indicator-label">Current Price</span>
                    <span class="indicator-value">$${indicators.current_price || data.current_price || 'N/A'}</span>
                </div>
                <div class="indicator-item">
                    <span class="indicator-label">Change</span>
                    <span class="indicator-value ${indicators.change >= 0 ? 'positive' : 'negative'}">
                        ${indicators.change >= 0 ? '+' : ''}${indicators.change || 0} 
                        (${indicators.change_percent >= 0 ? '+' : ''}${indicators.change_percent || 0}%)
                    </span>
                </div>
                <div class="indicator-item">
                    <span class="indicator-label">Volume</span>
                    <span class="indicator-value">${(indicators.volume || 0).toLocaleString()}</span>
                </div>
                <div class="indicator-item">
                    <span class="indicator-label">Data Points</span>
                    <span class="indicator-value">${data.data_points || 0}</span>
                </div>
            `;
            priceInfo.classList.remove('loading');
            
            // Display technical indicators
            const techIndicators = document.getElementById('technicalIndicators');
            techIndicators.innerHTML = `
                <div class="indicator-item">
                    <span class="indicator-label">RSI (14)</span>
                    <span class="indicator-value">${indicators.rsi || 'N/A'}
                        <span class="signal-badge signal-${indicators.rsi_signal === 'Oversold' ? 'buy' : indicators.rsi_signal === 'Overbought' ? 'sell' : 'hold'}">
                            ${indicators.rsi_signal || 'N/A'}
                        </span>
                    </span>
                </div>
                <div class="indicator-item">
                    <span class="indicator-label">MACD</span>
                    <span class="indicator-value">${indicators.macd || 'N/A'}
                        <span class="signal-badge signal-${indicators.macd_trend === 'Bullish' ? 'buy' : 'sell'}">
                            ${indicators.macd_trend || 'N/A'}
                        </span>
                    </span>
                </div>
                <div class="indicator-item">
                    <span class="indicator-label">BB Position</span>
                    <span class="indicator-value">
                        <span class="signal-badge signal-${indicators.bb_signal === 'Oversold' ? 'buy' : indicators.bb_signal === 'Overbought' ? 'sell' : 'hold'}">
                            ${indicators.bb_signal || 'N/A'}
                        </span>
                    </span>
                </div>
                <div class="indicator-item">
                    <span class="indicator-label">SMA 20</span>
                    <span class="indicator-value">$${indicators.sma_20 || 'N/A'}</span>
                </div>
                <div class="indicator-item">
                    <span class="indicator-label">Overall Signal</span>
                    <span class="indicator-value">
                        <span class="signal-badge signal-${indicators.overall_signal === 'Buy' ? 'buy' : indicators.overall_signal === 'Sell' ? 'sell' : 'hold'}">
                            ${indicators.overall_signal || 'Hold'}
                        </span>
                    </span>
                </div>
            `;
            techIndicators.classList.remove('loading');
            
            // Display predictions
            const predictions = document.getElementById('predictions');
            if (data.predictions && data.predictions.length > 0) {
                predictions.innerHTML = data.predictions.map(pred => `
                    <div class="prediction-item">
                        <strong>${pred.date}</strong>: $${pred.predicted_price}
                        <br><small>Confidence: ${(pred.confidence * 100).toFixed(0)}%</small>
                    </div>
                `).join('');
            } else {
                predictions.innerHTML = '<p>No predictions available. Need more historical data.</p>';
            }
            predictions.classList.remove('loading');
            
            // Display data source
            document.getElementById('dataSource').textContent = `Data Source: ${data.source} | Last Updated: ${data.last_updated}`;
        }
        
        function drawChart(data) {
            const ctx = document.getElementById('priceChart').getContext('2d');
            
            if (chartInstance) {
                chartInstance.destroy();
            }
            
            if (!data.candlestick_data || data.candlestick_data.length === 0) {
                document.getElementById('chartLoading').innerHTML = 'No data to display';
                return;
            }
            
            // Prepare candlestick data
            const candlestickData = data.candlestick_data.map(item => ({
                x: new Date(item.date).getTime(),
                o: item.open,
                h: item.high,
                l: item.low,
                c: item.close
            }));
            
            // Prepare volume data
            const volumeData = data.candlestick_data.map(item => ({
                x: new Date(item.date).getTime(),
                y: item.volume
            }));
            
            chartInstance = new Chart(ctx, {
                type: 'candlestick',
                data: {
                    datasets: [{
                        label: data.symbol,
                        data: candlestickData,
                        borderColor: {
                            up: '#26a69a',
                            down: '#ef5350',
                            unchanged: '#999'
                        },
                        backgroundColor: {
                            up: '#26a69a',
                            down: '#ef5350',
                            unchanged: '#999'
                        }
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'day',
                                displayFormats: {
                                    day: 'MMM dd'
                                }
                            },
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Price ($)'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const point = context.raw;
                                    return [
                                        'Open: $' + point.o.toFixed(2),
                                        'High: $' + point.h.toFixed(2),
                                        'Low: $' + point.l.toFixed(2),
                                        'Close: $' + point.c.toFixed(2)
                                    ];
                                }
                            }
                        }
                    }
                }
            });
        }
        
        async function runBacktest() {
            const symbol = document.getElementById('symbolInput').value.toUpperCase();
            const period = document.getElementById('periodSelect').value;
            
            if (!symbol) {
                showError('Please enter a stock symbol');
                return;
            }
            
            const resultsDiv = document.getElementById('backtestResults');
            resultsDiv.innerHTML = 'Running backtest...';
            resultsDiv.classList.add('loading');
            
            try {
                const response = await fetch('/api/backtest', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        symbol: symbol,
                        strategy: 'ma_crossover',
                        period: period
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    resultsDiv.innerHTML = `
                        <div class="indicator-item">
                            <span class="indicator-label">Strategy</span>
                            <span class="indicator-value">MA Crossover (20/50)</span>
                        </div>
                        <div class="indicator-item">
                            <span class="indicator-label">Total Return</span>
                            <span class="indicator-value ${data.total_return >= 0 ? 'positive' : 'negative'}">
                                ${data.total_return >= 0 ? '+' : ''}${data.total_return}%
                            </span>
                        </div>
                        <div class="indicator-item">
                            <span class="indicator-label">Buy & Hold Return</span>
                            <span class="indicator-value ${data.buy_hold_return >= 0 ? 'positive' : 'negative'}">
                                ${data.buy_hold_return >= 0 ? '+' : ''}${data.buy_hold_return}%
                            </span>
                        </div>
                        <div class="indicator-item">
                            <span class="indicator-label">Total Trades</span>
                            <span class="indicator-value">${data.trades}</span>
                        </div>
                        <div class="indicator-item">
                            <span class="indicator-label">Sharpe Ratio</span>
                            <span class="indicator-value">${data.sharpe_ratio}</span>
                        </div>
                        <div class="data-source">Data Source: ${data.data_source}</div>
                    `;
                } else {
                    resultsDiv.innerHTML = `<div class="error active">${data.error}</div>`;
                }
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error active">Failed to run backtest: ${error.message}</div>`;
            } finally {
                resultsDiv.classList.remove('loading');
            }
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('errorMessage');
            errorDiv.textContent = message;
            errorDiv.classList.add('active');
        }
        
        function hideError() {
            const errorDiv = document.getElementById('errorMessage');
            errorDiv.classList.remove('active');
        }
        
        // Load initial data
        window.addEventListener('DOMContentLoaded', () => {
            fetchStockData();
        });
        
        // Add enter key support
        document.getElementById('symbolInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                fetchStockData();
            }
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("=" * 60)
    print("UNIFIED STOCK ANALYSIS SYSTEM - FIXED VERSION")
    print("=" * 60)
    print("Features:")
    print("✓ Yahoo Finance (primary) with simplified API calls")
    print("✓ Alpha Vantage (fallback) with API key integrated")
    print("✓ Machine Learning predictions (RandomForest)")
    print("✓ Technical indicators (RSI, MACD, Bollinger Bands)")
    print("✓ Candlestick charts with Chart.js")
    print("✓ Australian stocks auto-suffix (.AX)")
    print("✓ Backtesting capabilities")
    print("✓ NO mock/synthetic data - 100% real market data")
    print("=" * 60)
    print(f"Starting server at http://localhost:8000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=8000, debug=False)