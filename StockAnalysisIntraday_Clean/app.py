#!/usr/bin/env python3
"""
Stock Analysis System with Intraday Support - FIXED CHARTS
Reverted to working chart configuration and added line chart option
"""

import yfinance as yf
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import requests
import warnings
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import traceback

warnings.filterwarnings('ignore')

# Flask app setup
app = Flask(__name__)
CORS(app)

# Configuration
ALPHA_VANTAGE_API_KEY = "68ZFANK047DL0KSR"

# Australian stock list
AUSTRALIAN_STOCKS = ['CBA', 'BHP', 'CSL', 'NAB', 'ANZ', 'WBC', 'WES', 'MQG', 'TLS', 'WOW', 
                     'RIO', 'FMG', 'TCL', 'ALL', 'REA', 'GMG', 'AMC', 'SUN', 'QBE', 'IAG']

# Intraday interval mappings
INTRADAY_INTERVALS = {
    '1m': {'yahoo': '1m', 'display': '1 Minute', 'max_period': '7d'},
    '2m': {'yahoo': '2m', 'display': '2 Minutes', 'max_period': '60d'},
    '5m': {'yahoo': '5m', 'display': '5 Minutes', 'max_period': '60d'},
    '15m': {'yahoo': '15m', 'display': '15 Minutes', 'max_period': '60d'},
    '30m': {'yahoo': '30m', 'display': '30 Minutes', 'max_period': '60d'},
    '60m': {'yahoo': '60m', 'display': '1 Hour', 'max_period': '730d'},
    '90m': {'yahoo': '90m', 'display': '90 Minutes', 'max_period': '60d'},
    '1h': {'yahoo': '1h', 'display': '1 Hour', 'max_period': '730d'},
    '1d': {'yahoo': '1d', 'display': '1 Day', 'max_period': 'max'},
    '5d': {'yahoo': '5d', 'display': '5 Days', 'max_period': 'max'},
    '1wk': {'yahoo': '1wk', 'display': '1 Week', 'max_period': 'max'},
    '1mo': {'yahoo': '1mo', 'display': '1 Month', 'max_period': 'max'}
}

class MLPredictor:
    """Machine Learning prediction model for stock prices"""
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=5,
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
        
        # Moving averages - adjusted for intraday
        features['sma_5'] = df['Close'].rolling(5).mean()
        features['sma_20'] = df['Close'].rolling(20).mean()
        features['sma_ratio'] = features['sma_5'] / features['sma_20']
        
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
        
        # Volume features
        if 'Volume' in df.columns and df['Volume'].sum() > 0:
            features['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
        else:
            features['volume_ratio'] = 1.0
        
        # Price position
        features['price_position'] = (df['Close'] - df['Low']) / (df['High'] - df['Low'] + 1e-10)
        
        # Bollinger Bands
        bb_sma = df['Close'].rolling(20).mean()
        bb_std = df['Close'].rolling(20).std()
        features['bb_position'] = (df['Close'] - bb_sma) / (bb_std + 1e-10)
        
        return features.dropna()
    
    def train(self, df):
        """Train the ML model on historical data"""
        if len(df) < 50:
            print(f"Not enough data for training: {len(df)} rows")
            return False
        
        features = self.prepare_features(df)
        if len(features) < 30:
            print(f"Not enough features after preparation: {len(features)} rows")
            return False
        
        # Prepare target (next period return)
        y = df['Close'].pct_change().shift(-1).loc[features.index]
        
        # Remove last row (no future data)
        features = features[:-1]
        y = y[:-1]
        
        # Split data
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
    
    def predict(self, df, periods=5):
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
        
        for i in range(periods):
            # Predict next return
            pred_return = self.model.predict(last_features_scaled)[0]
            
            # Calculate predicted price
            pred_price = current_price * (1 + pred_return)
            
            # Store prediction
            pred_date = df.index[-1] + timedelta(hours=i+1)  # Adjust for intraday
            predictions.append({
                'date': pred_date.strftime('%Y-%m-%d %H:%M:%S'),
                'predicted_price': round(pred_price, 2),
                'confidence': 0.7 - (i * 0.05)
            })
            
            # Update for next prediction
            current_price = pred_price
            last_features_scaled[0][0] = pred_return
        
        return predictions

class IntradayDataFetcher:
    """Enhanced data fetcher with intraday support"""
    
    def __init__(self):
        self.av_api_key = ALPHA_VANTAGE_API_KEY
        self.au_stocks = AUSTRALIAN_STOCKS
    
    def _add_au_suffix(self, symbol: str) -> str:
        """Add .AX suffix for Australian stocks"""
        symbol_upper = symbol.upper().replace('.AX', '')
        if symbol_upper in self.au_stocks:
            return f"{symbol_upper}.AX"
        return symbol
    
    def fetch_data(self, symbol: str, period: str = '1d', interval: str = '5m'):
        """Fetch data with intraday support"""
        
        # Try Yahoo Finance first
        data, source, price = self.fetch_yahoo_intraday(symbol, period, interval)
        if data is not None and not data.empty:
            return data, source, price
        
        print(f"Yahoo Finance failed, trying Alpha Vantage...")
        
        # Fallback to Alpha Vantage
        data, source, price = self.fetch_alpha_vantage_intraday(symbol, interval)
        if data is not None and not data.empty:
            return data, source, price
        
        print(f"Both data sources failed for {symbol}")
        return None, "Error", 0
    
    def fetch_yahoo_intraday(self, symbol: str, period: str = '1d', interval: str = '5m'):
        """Fetch intraday data from Yahoo Finance"""
        try:
            symbol = self._add_au_suffix(symbol)
            print(f"Fetching {symbol} from Yahoo Finance - Period: {period}, Interval: {interval}")
            
            # Validate interval
            if interval not in INTRADAY_INTERVALS:
                interval = '5m'  # Default to 5 minutes
            
            # Get Yahoo interval format
            yahoo_interval = INTRADAY_INTERVALS[interval]['yahoo']
            
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # For intraday data, we need to use specific parameters
            if interval in ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h']:
                # Intraday intervals - fetch with appropriate period
                if period == '1d':
                    hist = ticker.history(period='1d', interval=yahoo_interval)
                elif period == '5d':
                    hist = ticker.history(period='5d', interval=yahoo_interval)
                elif period == '1mo':
                    hist = ticker.history(period='1mo', interval=yahoo_interval)
                else:
                    hist = ticker.history(period=period, interval=yahoo_interval)
            else:
                # Daily or longer intervals
                hist = ticker.history(period=period)
            
            if hist.empty:
                print(f"Yahoo Finance returned empty data for {symbol}")
                return None, None, None
            
            print(f"Yahoo Finance: Successfully fetched {len(hist)} data points at {interval} intervals")
            
            # Get current price
            try:
                info = ticker.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice') or hist['Close'].iloc[-1]
            except:
                current_price = hist['Close'].iloc[-1]
            
            current_price = float(current_price)
            
            return hist, f"Yahoo Finance ({interval})", current_price
            
        except Exception as e:
            print(f"Yahoo Finance error for {symbol}: {str(e)}")
            return None, None, None
    
    def fetch_alpha_vantage_intraday(self, symbol: str, interval: str = '5m'):
        """Fetch intraday data from Alpha Vantage"""
        try:
            av_symbol = symbol.replace('.AX', '')
            print(f"Fetching {av_symbol} from Alpha Vantage with {interval} interval")
            
            # Map interval to Alpha Vantage format
            av_interval_map = {
                '1m': '1min',
                '5m': '5min',
                '15m': '15min',
                '30m': '30min',
                '60m': '60min',
                '1h': '60min'
            }
            
            av_interval = av_interval_map.get(interval, '5min')
            
            params = {
                'function': 'TIME_SERIES_INTRADAY',
                'symbol': av_symbol,
                'interval': av_interval,
                'apikey': self.av_api_key,
                'outputsize': 'full',
                'datatype': 'json'
            }
            
            response = requests.get('https://www.alphavantage.co/query', params=params, timeout=10)
            data = response.json()
            
            if 'Error Message' in data:
                print(f"Alpha Vantage error: {data['Error Message']}")
                return None, None, None
            
            time_key = f'Time Series ({av_interval})'
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
                    'Close': float(values.get('4. close', 0)),
                    'Volume': int(values.get('5. volume', 0))
                })
            
            if not df_data:
                return None, None, None
            
            df = pd.DataFrame(df_data)
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)
            
            print(f"Alpha Vantage: Fetched {len(df)} intraday data points")
            current_price = float(df['Close'].iloc[-1])
            
            return df, f"Alpha Vantage ({interval})", current_price
            
        except Exception as e:
            print(f"Alpha Vantage error: {str(e)}")
            return None, None, None

class TechnicalAnalyzer:
    """Technical analysis calculator with intraday support"""
    
    @staticmethod
    def calculate_all(df, interval='5m'):
        """Calculate technical indicators adjusted for intraday data"""
        indicators = {}
        
        if df is None or df.empty:
            return indicators
        
        try:
            # Adjust periods based on interval
            if interval in ['1m', '2m', '5m']:
                rsi_period = 14
                sma_short = 10
                sma_long = 20
                bb_period = 20
            else:
                rsi_period = 14
                sma_short = 20
                sma_long = 50
                bb_period = 20
            
            # Current price and change
            current_price = float(df['Close'].iloc[-1])
            prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else current_price
            change = current_price - prev_close
            change_pct = (change / prev_close * 100) if prev_close != 0 else 0
            
            indicators['current_price'] = round(current_price, 2)
            indicators['change'] = round(change, 2)
            indicators['change_percent'] = round(change_pct, 2)
            indicators['interval'] = interval
            
            # Moving Averages (adjusted for available data)
            if len(df) >= sma_short:
                indicators[f'sma_{sma_short}'] = round(float(df['Close'].rolling(sma_short).mean().iloc[-1]), 2)
            
            if len(df) >= sma_long:
                indicators[f'sma_{sma_long}'] = round(float(df['Close'].rolling(sma_long).mean().iloc[-1]), 2)
            
            # RSI
            if len(df) >= rsi_period + 1:
                delta = df['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(rsi_period).mean()
                loss = -delta.where(delta < 0, 0).rolling(rsi_period).mean()
                rs = gain / (loss + 1e-10)
                rsi = 100 - (100 / (1 + rs))
                indicators['rsi'] = round(float(rsi.iloc[-1]), 2)
                
                # RSI Signal
                if indicators['rsi'] < 30:
                    indicators['rsi_signal'] = 'Oversold'
                elif indicators['rsi'] > 70:
                    indicators['rsi_signal'] = 'Overbought'
                else:
                    indicators['rsi_signal'] = 'Neutral'
            
            # MACD
            if len(df) >= 26:
                ema12 = df['Close'].ewm(span=12).mean()
                ema26 = df['Close'].ewm(span=26).mean()
                macd_line = ema12 - ema26
                signal_line = macd_line.ewm(span=9).mean()
                
                indicators['macd'] = round(float(macd_line.iloc[-1]), 2)
                indicators['macd_signal'] = round(float(signal_line.iloc[-1]), 2)
                
                if indicators['macd'] > indicators['macd_signal']:
                    indicators['macd_trend'] = 'Bullish'
                else:
                    indicators['macd_trend'] = 'Bearish'
            
            # Bollinger Bands
            if len(df) >= bb_period:
                bb_sma = df['Close'].rolling(bb_period).mean()
                bb_std = df['Close'].rolling(bb_period).std()
                bb_upper = bb_sma + 2 * bb_std
                bb_lower = bb_sma - 2 * bb_std
                
                indicators['bb_upper'] = round(float(bb_upper.iloc[-1]), 2)
                indicators['bb_middle'] = round(float(bb_sma.iloc[-1]), 2)
                indicators['bb_lower'] = round(float(bb_lower.iloc[-1]), 2)
                
                if current_price > indicators['bb_upper']:
                    indicators['bb_signal'] = 'Overbought'
                elif current_price < indicators['bb_lower']:
                    indicators['bb_signal'] = 'Oversold'
                else:
                    indicators['bb_signal'] = 'Neutral'
            
            # Volume analysis
            if 'Volume' in df.columns and df['Volume'].sum() > 0:
                indicators['volume'] = int(df['Volume'].iloc[-1])
                if len(df) >= 20:
                    indicators['volume_avg'] = int(df['Volume'].rolling(20).mean().iloc[-1])
                    volume_ratio = indicators['volume'] / indicators['volume_avg'] if indicators['volume_avg'] > 0 else 1
                    indicators['volume_ratio'] = round(volume_ratio, 2)
            
            # Support and Resistance
            recent_periods = min(20, len(df))
            indicators['resistance'] = round(float(df['High'].tail(recent_periods).max()), 2)
            indicators['support'] = round(float(df['Low'].tail(recent_periods).min()), 2)
            
            # Overall signal
            signals = []
            if 'rsi' in indicators:
                if indicators['rsi'] < 30:
                    signals.append('Buy')
                elif indicators['rsi'] > 70:
                    signals.append('Sell')
            
            if 'macd_trend' in indicators:
                if indicators['macd_trend'] == 'Bullish':
                    signals.append('Buy')
                else:
                    signals.append('Sell')
            
            if 'bb_signal' in indicators:
                if indicators['bb_signal'] == 'Oversold':
                    signals.append('Buy')
                elif indicators['bb_signal'] == 'Overbought':
                    signals.append('Sell')
            
            if signals:
                buy_signals = signals.count('Buy')
                sell_signals = signals.count('Sell')
                
                if buy_signals > sell_signals:
                    indicators['overall_signal'] = 'Buy'
                elif sell_signals > buy_signals:
                    indicators['overall_signal'] = 'Sell'
                else:
                    indicators['overall_signal'] = 'Hold'
            else:
                indicators['overall_signal'] = 'Hold'
            
        except Exception as e:
            print(f"Error calculating indicators: {str(e)}")
            traceback.print_exc()
        
        return indicators

# Create global instances
data_fetcher = IntradayDataFetcher()
ml_predictor = MLPredictor()
tech_analyzer = TechnicalAnalyzer()

# API Routes
@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get stock data with intraday support"""
    try:
        period = request.args.get('period', '1d')
        interval = request.args.get('interval', '5m')
        
        # Validate interval
        if interval not in INTRADAY_INTERVALS:
            interval = '5m'
        
        # Fetch data
        df, source, current_price = data_fetcher.fetch_data(symbol, period, interval)
        
        if df is None or df.empty:
            return jsonify({
                'error': 'Failed to fetch data',
                'symbol': symbol,
                'source': 'None'
            }), 404
        
        # Calculate technical indicators
        indicators = tech_analyzer.calculate_all(df, interval)
        
        # Train ML model and get predictions (adjust for intraday)
        predictions = []
        if len(df) >= 50:  # Need enough data for ML
            if ml_predictor.train(df):
                predictions = ml_predictor.predict(df, periods=5)
        
        # Prepare candlestick data for frontend
        candlestick_data = []
        for index, row in df.iterrows():
            candlestick_data.append({
                'date': index.strftime('%Y-%m-%d %H:%M:%S'),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row.get('Volume', 0))
            })
        
        # Also prepare line chart data (just closing prices)
        line_data = []
        for index, row in df.iterrows():
            line_data.append({
                'x': index.strftime('%Y-%m-%d %H:%M:%S'),
                'y': float(row['Close'])
            })
        
        response = {
            'symbol': symbol,
            'source': source,
            'period': period,
            'interval': interval,
            'interval_display': INTRADAY_INTERVALS[interval]['display'],
            'current_price': current_price,
            'indicators': indicators,
            'predictions': predictions,
            'candlestick_data': candlestick_data,
            'line_data': line_data,
            'data_points': len(df),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in get_stock_data: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    """Handle favicon request to prevent 404"""
    return '', 204

@app.route('/')
def home():
    """Serve the main HTML interface with intraday support"""
    return render_template_string(HTML_TEMPLATE)

# HTML Template with WORKING chart configuration and line chart option
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis with Intraday Support</title>
    <!-- USING THE WORKING VERSION IMPORTS -->
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
            max-width: 1600px;
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
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.95;
        }
        
        .search-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .search-controls {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr 1fr auto;
            gap: 10px;
            align-items: center;
        }
        
        @media (max-width: 768px) {
            .search-controls {
                grid-template-columns: 1fr;
            }
        }
        
        .control-group {
            display: flex;
            flex-direction: column;
        }
        
        .control-group label {
            font-size: 0.85em;
            color: #666;
            margin-bottom: 5px;
            font-weight: 600;
        }
        
        input[type="text"] {
            padding: 12px 20px;
            border: 2px solid #e1e8ed;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            align-items: flex-end;
        }
        
        button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            white-space: nowrap;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button.secondary {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        
        .interval-buttons {
            display: flex;
            gap: 5px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        .interval-btn {
            padding: 8px 16px;
            background: #f0f2f5;
            color: #333;
            border: 2px solid transparent;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .interval-btn:hover {
            background: #e4e6eb;
        }
        
        .interval-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-color: #667eea;
        }
        
        .content-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.3em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            min-height: 600px;
            position: relative;
        }
        
        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .chart-title {
            font-size: 1.4em;
            font-weight: 700;
            color: #333;
        }
        
        .chart-controls {
            display: flex;
            gap: 10px;
        }
        
        .chart-type-btn {
            padding: 8px 16px;
            background: #f0f2f5;
            color: #333;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .chart-type-btn:hover {
            background: #e4e6eb;
        }
        
        .chart-type-btn.active {
            background: #667eea;
            color: white;
        }
        
        .chart-info {
            display: flex;
            gap: 20px;
            font-size: 0.9em;
            color: #666;
        }
        
        .chart-info span {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .indicator-item {
            display: flex;
            justify-content: space-between;
            padding: 12px;
            margin: 8px 0;
            background: #f8f9fa;
            border-radius: 8px;
            transition: all 0.2s;
        }
        
        .indicator-item:hover {
            background: #e9ecef;
            transform: translateX(5px);
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
        
        .loading-spinner {
            width: 40px;
            height: 40px;
            margin: 0 auto 20px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            display: none;
            border-left: 4px solid #dc3545;
        }
        
        .error.active {
            display: block;
        }
        
        .prediction-item {
            padding: 12px;
            margin: 8px 0;
            background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
            border-radius: 8px;
            border-left: 4px solid #0c5460;
        }
        
        .data-source {
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 15px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
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
        
        .interval-info {
            background: #e7f3ff;
            color: #004085;
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
            font-size: 0.9em;
        }
        
        canvas {
            max-height: 500px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Stock Analysis with Intraday Support</h1>
            <p>Real-time market data with candlestick and line charts</p>
        </div>
        
        <div class="search-section">
            <div class="search-controls">
                <div class="control-group">
                    <label>Stock Symbol</label>
                    <input type="text" id="symbolInput" placeholder="Enter stock symbol (e.g., AAPL, CBA)" value="AAPL">
                </div>
                <div class="control-group">
                    <label>Time Period</label>
                    <select id="periodSelect">
                        <option value="1d" selected>1 Day</option>
                        <option value="5d">5 Days</option>
                        <option value="1mo">1 Month</option>
                        <option value="3mo">3 Months</option>
                        <option value="6mo">6 Months</option>
                        <option value="1y">1 Year</option>
                        <option value="2y">2 Years</option>
                        <option value="5y">5 Years</option>
                    </select>
                </div>
                <div class="control-group">
                    <label>Interval</label>
                    <select id="intervalSelect">
                        <option value="1m">1 Minute</option>
                        <option value="2m">2 Minutes</option>
                        <option value="5m" selected>5 Minutes</option>
                        <option value="15m">15 Minutes</option>
                        <option value="30m">30 Minutes</option>
                        <option value="60m">1 Hour</option>
                        <option value="90m">90 Minutes</option>
                        <option value="1d">1 Day</option>
                        <option value="1wk">1 Week</option>
                        <option value="1mo">1 Month</option>
                    </select>
                </div>
                <div class="control-group">
                    <label>Chart Type</label>
                    <select id="chartTypeSelect">
                        <option value="candlestick">Candlestick</option>
                        <option value="line">Line</option>
                    </select>
                </div>
                <div class="control-group">
                    <label>Update Rate</label>
                    <select id="updateRate">
                        <option value="0">Manual</option>
                        <option value="30">30 sec</option>
                        <option value="60">1 min</option>
                        <option value="300">5 min</option>
                        <option value="600">10 min</option>
                    </select>
                </div>
                <div class="control-group">
                    <label>&nbsp;</label>
                    <div class="button-group">
                        <button onclick="fetchStockData()">Analyze</button>
                        <button class="secondary" onclick="exportData()">Export</button>
                    </div>
                </div>
            </div>
            
            <div class="interval-buttons">
                <button class="interval-btn" onclick="quickInterval('1m', '1d')">1m</button>
                <button class="interval-btn" onclick="quickInterval('5m', '1d')">5m</button>
                <button class="interval-btn" onclick="quickInterval('15m', '5d')">15m</button>
                <button class="interval-btn" onclick="quickInterval('30m', '5d')">30m</button>
                <button class="interval-btn" onclick="quickInterval('1h', '1mo')">1H</button>
                <button class="interval-btn" onclick="quickInterval('1d', '3mo')">1D</button>
                <button class="interval-btn" onclick="quickInterval('1wk', '1y')">1W</button>
                <button class="interval-btn" onclick="quickInterval('1mo', '5y')">1M</button>
            </div>
        </div>
        
        <div class="error" id="errorMessage"></div>
        
        <div class="chart-container">
            <div class="chart-header">
                <div class="chart-title" id="chartTitle">Price Chart</div>
                <div class="chart-controls">
                    <button class="chart-type-btn active" onclick="switchChartType('candlestick')">Candlestick</button>
                    <button class="chart-type-btn" onclick="switchChartType('line')">Line</button>
                </div>
                <div class="chart-info">
                    <span id="intervalInfo"></span>
                    <span id="dataPointsInfo"></span>
                    <span id="lastUpdateInfo"></span>
                </div>
            </div>
            <div class="loading" id="chartLoading">
                <div class="loading-spinner"></div>
                Loading chart data...
            </div>
            <canvas id="priceChart"></canvas>
            <div class="data-source" id="dataSource"></div>
        </div>
        
        <div class="content-grid">
            <div class="card">
                <h2>Price Information</h2>
                <div id="priceInfo" class="loading">
                    <div class="loading-spinner"></div>
                    Loading...
                </div>
            </div>
            
            <div class="card">
                <h2>Technical Indicators</h2>
                <div id="technicalIndicators" class="loading">
                    <div class="loading-spinner"></div>
                    Loading...
                </div>
            </div>
            
            <div class="card">
                <h2>ML Predictions</h2>
                <div id="predictions" class="loading">
                    <div class="loading-spinner"></div>
                    Loading...
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let chartInstance = null;
        let currentData = null;
        let updateInterval = null;
        let currentChartType = 'candlestick';
        
        // Quick interval buttons
        function quickInterval(interval, period) {
            document.getElementById('intervalSelect').value = interval;
            document.getElementById('periodSelect').value = period;
            
            // Update active button
            document.querySelectorAll('.interval-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            fetchStockData();
        }
        
        // Switch chart type
        function switchChartType(type) {
            currentChartType = type;
            document.getElementById('chartTypeSelect').value = type;
            
            // Update buttons
            document.querySelectorAll('.chart-type-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Redraw chart if data exists
            if (currentData) {
                drawChart(currentData);
            }
        }
        
        // Auto-update functionality
        document.getElementById('updateRate').addEventListener('change', (e) => {
            if (updateInterval) {
                clearInterval(updateInterval);
                updateInterval = null;
            }
            
            const rate = parseInt(e.target.value);
            if (rate > 0) {
                updateInterval = setInterval(() => {
                    fetchStockData();
                }, rate * 1000);
            }
        });
        
        // Chart type change
        document.getElementById('chartTypeSelect').addEventListener('change', (e) => {
            switchChartType(e.target.value);
        });
        
        async function fetchStockData() {
            const symbol = document.getElementById('symbolInput').value.toUpperCase();
            const period = document.getElementById('periodSelect').value;
            const interval = document.getElementById('intervalSelect').value;
            
            if (!symbol) {
                showError('Please enter a stock symbol');
                return;
            }
            
            // Show loading states
            document.getElementById('chartLoading').classList.add('active');
            document.getElementById('priceInfo').classList.add('loading');
            document.getElementById('priceInfo').innerHTML = '<div class="loading-spinner"></div>Loading...';
            document.getElementById('technicalIndicators').classList.add('loading');
            document.getElementById('technicalIndicators').innerHTML = '<div class="loading-spinner"></div>Loading...';
            document.getElementById('predictions').classList.add('loading');
            document.getElementById('predictions').innerHTML = '<div class="loading-spinner"></div>Loading...';
            hideError();
            
            try {
                const response = await fetch(`/api/stock/${symbol}?period=${period}&interval=${interval}`);
                const data = await response.json();
                
                if (response.ok) {
                    currentData = data;
                    displayData(data);
                    drawChart(data);
                    updateChartInfo(data);
                } else {
                    showError(data.error || 'Failed to fetch stock data');
                }
            } catch (error) {
                showError('Network error: ' + error.message);
            } finally {
                document.getElementById('chartLoading').classList.remove('active');
            }
        }
        
        function updateChartInfo(data) {
            document.getElementById('chartTitle').textContent = `${data.symbol} - ${data.interval_display || data.interval} Chart`;
            document.getElementById('intervalInfo').textContent = `Interval: ${data.interval_display || data.interval}`;
            document.getElementById('dataPointsInfo').textContent = `Points: ${data.data_points}`;
            document.getElementById('lastUpdateInfo').textContent = `Updated: ${new Date().toLocaleTimeString()}`;
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
                    <span class="indicator-label">Support</span>
                    <span class="indicator-value">$${indicators.support || 'N/A'}</span>
                </div>
                <div class="indicator-item">
                    <span class="indicator-label">Resistance</span>
                    <span class="indicator-value">$${indicators.resistance || 'N/A'}</span>
                </div>
                ${indicators.interval ? `
                <div class="interval-info">
                    Trading at ${indicators.interval} intervals
                </div>` : ''}
            `;
            priceInfo.classList.remove('loading');
            
            // Display technical indicators
            const techIndicators = document.getElementById('technicalIndicators');
            techIndicators.innerHTML = `
                <div class="indicator-item">
                    <span class="indicator-label">RSI (14)</span>
                    <span class="indicator-value">${indicators.rsi || 'N/A'}
                        ${indicators.rsi_signal ? `
                        <span class="signal-badge signal-${indicators.rsi_signal === 'Oversold' ? 'buy' : indicators.rsi_signal === 'Overbought' ? 'sell' : 'hold'}">
                            ${indicators.rsi_signal}
                        </span>` : ''}
                    </span>
                </div>
                <div class="indicator-item">
                    <span class="indicator-label">MACD</span>
                    <span class="indicator-value">${indicators.macd || 'N/A'}
                        ${indicators.macd_trend ? `
                        <span class="signal-badge signal-${indicators.macd_trend === 'Bullish' ? 'buy' : 'sell'}">
                            ${indicators.macd_trend}
                        </span>` : ''}
                    </span>
                </div>
                <div class="indicator-item">
                    <span class="indicator-label">BB Position</span>
                    <span class="indicator-value">
                        ${indicators.bb_signal ? `
                        <span class="signal-badge signal-${indicators.bb_signal === 'Oversold' ? 'buy' : indicators.bb_signal === 'Overbought' ? 'sell' : 'hold'}">
                            ${indicators.bb_signal}
                        </span>` : 'N/A'}
                    </span>
                </div>
                ${indicators.sma_10 ? `
                <div class="indicator-item">
                    <span class="indicator-label">SMA 10</span>
                    <span class="indicator-value">$${indicators.sma_10}</span>
                </div>` : ''}
                ${indicators.sma_20 ? `
                <div class="indicator-item">
                    <span class="indicator-label">SMA 20</span>
                    <span class="indicator-value">$${indicators.sma_20}</span>
                </div>` : ''}
                ${indicators.sma_50 ? `
                <div class="indicator-item">
                    <span class="indicator-label">SMA 50</span>
                    <span class="indicator-value">$${indicators.sma_50}</span>
                </div>` : ''}
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
                predictions.innerHTML = '<p>Insufficient data for predictions. Need at least 50 data points.</p>';
            }
            predictions.classList.remove('loading');
            
            // Display data source
            document.getElementById('dataSource').innerHTML = `
                Data Source: ${data.source} | 
                Last Updated: ${data.last_updated} | 
                Interval: ${data.interval_display || data.interval}
            `;
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
            
            const chartType = document.getElementById('chartTypeSelect').value;
            
            if (chartType === 'line') {
                // Draw line chart
                drawLineChart(ctx, data);
            } else {
                // Draw candlestick chart
                drawCandlestickChart(ctx, data);
            }
        }
        
        function drawCandlestickChart(ctx, data) {
            // Prepare candlestick data
            const candlestickData = data.candlestick_data.map(item => ({
                x: new Date(item.date).getTime(),
                o: item.open,
                h: item.high,
                l: item.low,
                c: item.close
            }));
            
            // Determine time unit based on interval
            let timeUnit = 'hour';
            if (data.interval === '1m' || data.interval === '2m' || data.interval === '5m') {
                timeUnit = 'minute';
            } else if (data.interval === '15m' || data.interval === '30m' || data.interval === '60m' || data.interval === '1h') {
                timeUnit = 'hour';
            } else if (data.interval === '1d') {
                timeUnit = 'day';
            } else if (data.interval === '1wk') {
                timeUnit = 'week';
            } else if (data.interval === '1mo') {
                timeUnit = 'month';
            }
            
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
                                unit: timeUnit,
                                displayFormats: {
                                    minute: 'HH:mm',
                                    hour: 'MMM dd HH:mm',
                                    day: 'MMM dd',
                                    week: 'MMM dd',
                                    month: 'MMM yyyy'
                                }
                            },
                            title: {
                                display: true,
                                text: 'Date/Time'
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
        
        function drawLineChart(ctx, data) {
            // Prepare line data
            const lineData = data.candlestick_data.map(item => ({
                x: new Date(item.date).getTime(),
                y: item.close
            }));
            
            // Determine time unit based on interval
            let timeUnit = 'hour';
            if (data.interval === '1m' || data.interval === '2m' || data.interval === '5m') {
                timeUnit = 'minute';
            } else if (data.interval === '15m' || data.interval === '30m' || data.interval === '60m' || data.interval === '1h') {
                timeUnit = 'hour';
            } else if (data.interval === '1d') {
                timeUnit = 'day';
            } else if (data.interval === '1wk') {
                timeUnit = 'week';
            } else if (data.interval === '1mo') {
                timeUnit = 'month';
            }
            
            chartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    datasets: [{
                        label: data.symbol + ' Price',
                        data: lineData,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: timeUnit,
                                displayFormats: {
                                    minute: 'HH:mm',
                                    hour: 'MMM dd HH:mm',
                                    day: 'MMM dd',
                                    week: 'MMM dd',
                                    month: 'MMM yyyy'
                                }
                            },
                            title: {
                                display: true,
                                text: 'Date/Time'
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
                            display: true
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return 'Price: $' + context.parsed.y.toFixed(2);
                                }
                            }
                        }
                    }
                }
            });
        }
        
        function exportData() {
            if (!currentData) {
                showError('No data to export');
                return;
            }
            
            const csvContent = convertToCSV(currentData.candlestick_data);
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.setAttribute('href', url);
            a.setAttribute('download', `${currentData.symbol}_${currentData.interval}_${new Date().toISOString()}.csv`);
            a.click();
        }
        
        function convertToCSV(data) {
            const headers = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume'];
            const rows = data.map(item => [
                item.date,
                item.open,
                item.high,
                item.low,
                item.close,
                item.volume
            ]);
            
            return [headers, ...rows].map(row => row.join(',')).join('\\n');
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
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            if (updateInterval) {
                clearInterval(updateInterval);
            }
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("=" * 60)
    print("STOCK ANALYSIS WITH INTRADAY - CHARTS FIXED")
    print("=" * 60)
    print("Features:")
    print("✓ Candlestick charts working (reverted to working config)")
    print("✓ Line chart option added") 
    print("✓ Intraday intervals: 1m, 2m, 5m, 15m, 30m, 1h, 90m")
    print("✓ Chart type selector")
    print("✓ All JavaScript errors fixed")
    print("✓ Export to CSV working")
    print("=" * 60)
    print(f"Starting server at http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)