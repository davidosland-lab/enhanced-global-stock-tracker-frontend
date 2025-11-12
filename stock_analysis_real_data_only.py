#!/usr/bin/env python3
"""
Stock Analysis System - Real Data Only Version
NO test data, NO synthetic data, NO random generation
Only Yahoo Finance + Alpha Vantage real market data
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
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# Alpha Vantage Configuration
ALPHA_VANTAGE_API_KEY = "68ZFANK047DL0KSR"

class MLPredictor:
    """Machine Learning prediction model for stock prices"""
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_features(self, df):
        """Prepare technical features for ML model"""
        features = pd.DataFrame(index=df.index)
        
        # Price features
        features['returns'] = df['Close'].pct_change()
        features['volatility'] = features['returns'].rolling(20).std()
        
        # Moving averages
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
        features['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
        
        # Price position
        features['price_position'] = (df['Close'] - df['Low']) / (df['High'] - df['Low'] + 1e-10)
        
        # Bollinger Bands position
        bb_sma = df['Close'].rolling(20).mean()
        bb_std = df['Close'].rolling(20).std()
        features['bb_position'] = (df['Close'] - bb_sma) / (bb_std + 1e-10)
        
        return features.dropna()
    
    def train(self, df):
        """Train the ML model on historical data"""
        if len(df) < 50:
            return False
        
        features = self.prepare_features(df)
        if len(features) < 30:
            return False
        
        # Prepare target (next day return)
        y = df['Close'].pct_change().shift(-1).loc[features.index]
        
        # Remove last row (no future data)
        features = features[:-1]
        y = y[:-1]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Calculate accuracy
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        return {
            'train_score': train_score,
            'test_score': test_score,
            'features_used': list(features.columns)
        }
    
    def predict(self, df, days=5):
        """Predict future stock prices based on trained model"""
        if not self.is_trained:
            self.train(df)
        
        if not self.is_trained:
            return None
        
        features = self.prepare_features(df)
        if len(features) == 0:
            return None
        
        # Get last features
        last_features = features.iloc[-1:].values
        last_features_scaled = self.scaler.transform(last_features)
        
        # Predict future returns
        predictions = []
        current_price = float(df['Close'].iloc[-1])
        
        for i in range(days):
            # Predict next return
            pred_return = self.model.predict(last_features_scaled)[0]
            
            # Limit prediction to realistic range
            pred_return = np.clip(pred_return, -0.05, 0.05)
            
            # Calculate predicted price
            pred_price = current_price * (1 + pred_return)
            predictions.append(pred_price)
            current_price = pred_price
            
            # Update features for next prediction
            last_features_scaled[0][0] = pred_return
        
        return predictions

class RealDataFetcher:
    """Data fetcher using ONLY real market data - NO synthetic/test data"""
    
    def __init__(self):
        self.av_api_key = ALPHA_VANTAGE_API_KEY
        self.au_stocks = ['CBA', 'BHP', 'CSL', 'NAB', 'ANZ', 'WBC', 'WES', 'MQG', 'TLS', 'WOW']
    
    def _add_au_suffix(self, symbol: str) -> str:
        """Add .AX suffix for Australian stocks"""
        symbol_upper = symbol.upper().replace('.AX', '')
        if symbol_upper in self.au_stocks and not symbol.endswith('.AX'):
            return f"{symbol_upper}.AX"
        return symbol
    
    def fetch_yahoo_data(self, symbol: str, period: str = '1mo') -> tuple:
        """Fetch real data from Yahoo Finance"""
        try:
            symbol = self._add_au_suffix(symbol)
            print(f"Fetching {symbol} from Yahoo Finance for period {period}")
            
            # Create ticker
            ticker = yf.Ticker(symbol)
            
            # Fetch based on period
            if period == '1d':
                hist = ticker.history(period='1d', interval='5m', prepost=False, actions=False)
            elif period == '5d':
                hist = ticker.history(period='5d', interval='30m', prepost=False, actions=False)
            elif period == '1mo':
                hist = ticker.history(period='1mo', interval='1d', prepost=False, actions=False)
            elif period == '3mo':
                hist = ticker.history(period='3mo', interval='1d', prepost=False, actions=False)
            elif period == '6mo':
                hist = ticker.history(period='6mo', interval='1d', prepost=False, actions=False)
            elif period == '1y':
                hist = ticker.history(period='1y', interval='1d', prepost=False, actions=False)
            elif period == '5y':
                hist = ticker.history(period='5y', interval='1wk', prepost=False, actions=False)
            else:
                hist = ticker.history(period='1mo', interval='1d', prepost=False, actions=False)
            
            if not hist.empty:
                print(f"Yahoo Finance: Successfully fetched {len(hist)} data points")
                
                # Get current price
                try:
                    info = ticker.info
                    current_price = info.get('currentPrice') or info.get('regularMarketPrice') or hist['Close'].iloc[-1]
                except:
                    current_price = hist['Close'].iloc[-1]
                
                return hist, "Yahoo Finance", float(current_price)
            
            # Try download method as alternative
            print(f"Trying yf.download for {symbol}")
            
            end_date = datetime.now()
            if period == '1d':
                start_date = end_date - timedelta(days=1)
                interval = '5m'
            elif period == '5d':
                start_date = end_date - timedelta(days=5)
                interval = '30m'
            elif period == '1mo':
                start_date = end_date - timedelta(days=30)
                interval = '1d'
            elif period == '3mo':
                start_date = end_date - timedelta(days=90)
                interval = '1d'
            elif period == '6mo':
                start_date = end_date - timedelta(days=180)
                interval = '1d'
            elif period == '1y':
                start_date = end_date - timedelta(days=365)
                interval = '1d'
            elif period == '5y':
                start_date = end_date - timedelta(days=1825)
                interval = '1wk'
            else:
                start_date = end_date - timedelta(days=30)
                interval = '1d'
            
            df = yf.download(
                symbol,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval=interval,
                progress=False,
                show_errors=False,
                auto_adjust=True,
                repair=True,
                threads=False
            )
            
            if not df.empty:
                # Handle MultiIndex columns
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(1)
                
                print(f"Yahoo download: Got {len(df)} data points")
                current_price = float(df['Close'].iloc[-1])
                return df, "Yahoo Finance", current_price
                
        except Exception as e:
            print(f"Yahoo Finance error: {str(e)}")
        
        return None, None, None
    
    def fetch_alpha_vantage_data(self, symbol: str, period: str = '1mo') -> tuple:
        """Fetch real data from Alpha Vantage"""
        try:
            # Remove .AX for Alpha Vantage
            av_symbol = symbol.replace('.AX', '')
            print(f"Fetching {av_symbol} from Alpha Vantage for period {period}")
            
            # Determine function and interval
            if period in ['1d', '5d']:
                # Intraday data
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
                # Daily data
                params = {
                    'function': 'TIME_SERIES_DAILY_ADJUSTED',
                    'symbol': av_symbol,
                    'apikey': self.av_api_key,
                    'outputsize': 'full',
                    'datatype': 'json'
                }
                time_key = 'Time Series (Daily)'
            
            response = requests.get('https://www.alphavantage.co/query', params=params, timeout=10)
            data = response.json()
            
            if 'Error Message' in data:
                print(f"Alpha Vantage error: {data['Error Message']}")
                return None, None, None
            
            if 'Note' in data:
                print(f"Alpha Vantage API limit reached")
                return None, None, None
            
            if time_key not in data:
                print(f"Alpha Vantage: No time series data found")
                return None, None, None
            
            # Parse time series
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
            
            df = pd.DataFrame(df_data)
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)
            
            # Filter based on period
            now = datetime.now()
            if period == '1d':
                cutoff = now - timedelta(days=1)
            elif period == '5d':
                cutoff = now - timedelta(days=5)
            elif period == '1mo':
                cutoff = now - timedelta(days=30)
            elif period == '3mo':
                cutoff = now - timedelta(days=90)
            elif period == '6mo':
                cutoff = now - timedelta(days=180)
            elif period == '1y':
                cutoff = now - timedelta(days=365)
            elif period == '5y':
                cutoff = now - timedelta(days=1825)
            else:
                cutoff = now - timedelta(days=30)
            
            df = df[df.index >= cutoff]
            
            if not df.empty:
                print(f"Alpha Vantage: Got {len(df)} real data points")
                current_price = float(df['Close'].iloc[-1])
                return df, "Alpha Vantage", current_price
                
        except Exception as e:
            print(f"Alpha Vantage error: {str(e)}")
        
        return None, None, None
    
    def fetch_data(self, symbol: str, period: str = '1mo') -> tuple:
        """Fetch ONLY real data - Yahoo primary, Alpha Vantage fallback"""
        # Try Yahoo Finance first
        df, source, price = self.fetch_yahoo_data(symbol, period)
        if df is not None and not df.empty:
            return df, source, price
        
        # Fallback to Alpha Vantage
        print(f"Yahoo failed, trying Alpha Vantage for {symbol}")
        df, source, price = self.fetch_alpha_vantage_data(symbol, period)
        if df is not None and not df.empty:
            return df, source, price
        
        # NO SYNTHETIC DATA - Return None if both fail
        print(f"No real data available for {symbol}")
        return None, None, None

# Global instances
data_fetcher = RealDataFetcher()
ml_predictor = MLPredictor()

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """API endpoint for real stock data"""
    try:
        period = request.args.get('period', '1mo')
        df, source, current_price = data_fetcher.fetch_data(symbol, period)
        
        if df is None or df.empty:
            return jsonify({
                'error': f'No real data available for {symbol}. Please check symbol or try again later.',
                'symbol': symbol,
                'period': period
            }), 404
        
        # Train ML model and get predictions
        ml_results = {}
        if len(df) >= 50:
            training_results = ml_predictor.train(df)
            predictions = ml_predictor.predict(df, days=5)
            
            if predictions:
                ml_results = {
                    'predictions': predictions,
                    'prediction_dates': [(datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d') 
                                        for i in range(len(predictions))],
                    'confidence': training_results.get('test_score', 0) if training_results else 0
                }
        
        # Calculate indicators
        indicators = {}
        if len(df) >= 14:
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            rs = gain / (loss + 1e-10)
            indicators['rsi'] = float((100 - (100 / (1 + rs))).iloc[-1])
        
        # Return real data
        data = {
            'dates': [d.strftime('%Y-%m-%d %H:%M:%S') for d in df.index],
            'open': [float(p) for p in df['Open'].values],
            'high': [float(p) for p in df['High'].values],
            'low': [float(p) for p in df['Low'].values],
            'close': [float(p) for p in df['Close'].values],
            'volume': [int(v) for v in df['Volume'].values],
            'current_price': current_price,
            'min_price': float(df['Low'].min()),
            'max_price': float(df['High'].max()),
            'data_points': len(df),
            'source': source,
            'period': period,
            'indicators': indicators,
            'ml_predictions': ml_results
        }
        
        return jsonify(data)
        
    except Exception as e:
        print(f"Error in get_stock_data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart', methods=['POST', 'OPTIONS'])
def generate_chart():
    """Generate chart with real data only"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        symbol = data.get('symbol', 'AAPL')
        period = data.get('period', '1mo')
        chart_type = data.get('chart_type', 'candlestick')
        show_ml = data.get('show_ml', True)
        
        # Fetch real data
        df, source, current_price = data_fetcher.fetch_data(symbol, period)
        
        if df is None or df.empty:
            return jsonify({
                'error': f'No real data available for {symbol}. Please verify the symbol or try again.',
                'success': False
            }), 404
        
        # Create subplots
        fig = make_subplots(
            rows=4, cols=1,
            row_heights=[0.5, 0.15, 0.15, 0.2],
            subplot_titles=['Price & Predictions', 'Volume', 'RSI', 'MACD'],
            vertical_spacing=0.05
        )
        
        # Main price chart
        if chart_type == 'candlestick':
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='OHLC',
                increasing=dict(line=dict(color='#26a69a'), fillcolor='#26a69a'),
                decreasing=dict(line=dict(color='#ef5350'), fillcolor='#ef5350')
            ), row=1, col=1)
            
            # Bollinger Bands
            if len(df) >= 20:
                sma20 = df['Close'].rolling(20).mean()
                std20 = df['Close'].rolling(20).std()
                upper_band = sma20 + (std20 * 2)
                lower_band = sma20 - (std20 * 2)
                
                fig.add_trace(go.Scatter(
                    x=df.index, y=upper_band,
                    line=dict(color='rgba(250, 128, 114, 0.3)', width=1),
                    name='Upper BB', showlegend=False
                ), row=1, col=1)
                
                fig.add_trace(go.Scatter(
                    x=df.index, y=lower_band,
                    line=dict(color='rgba(250, 128, 114, 0.3)', width=1),
                    name='Lower BB', fill='tonexty',
                    fillcolor='rgba(250, 128, 114, 0.1)', showlegend=False
                ), row=1, col=1)
                
        elif chart_type == 'line':
            fig.add_trace(go.Scatter(
                x=df.index, y=df['Close'],
                mode='lines', name='Close',
                line=dict(color='#2196F3', width=2)
            ), row=1, col=1)
        else:  # area
            fig.add_trace(go.Scatter(
                x=df.index, y=df['Close'],
                mode='lines', name='Close',
                line=dict(color='#2196F3', width=2),
                fill='tozeroy', fillcolor='rgba(33, 150, 243, 0.3)'
            ), row=1, col=1)
        
        # Moving averages
        if len(df) >= 20:
            sma20 = df['Close'].rolling(20).mean()
            fig.add_trace(go.Scatter(
                x=df.index, y=sma20,
                line=dict(color='orange', width=1, dash='dash'),
                name='SMA 20'
            ), row=1, col=1)
        
        if len(df) >= 50:
            sma50 = df['Close'].rolling(50).mean()
            fig.add_trace(go.Scatter(
                x=df.index, y=sma50,
                line=dict(color='red', width=1, dash='dot'),
                name='SMA 50'
            ), row=1, col=1)
        
        # ML predictions
        ml_info = {}
        if show_ml and len(df) >= 50:
            training_results = ml_predictor.train(df)
            predictions = ml_predictor.predict(df, days=5)
            
            if predictions:
                # Create future dates
                last_date = df.index[-1]
                future_dates = [last_date + timedelta(days=i+1) for i in range(len(predictions))]
                
                # Add prediction line
                fig.add_trace(go.Scatter(
                    x=[last_date] + future_dates,
                    y=[float(df['Close'].iloc[-1])] + predictions,
                    mode='lines+markers',
                    name='ML Prediction',
                    line=dict(color='purple', width=2, dash='dash'),
                    marker=dict(size=8, color='purple')
                ), row=1, col=1)
                
                ml_info = {
                    'predictions': predictions,
                    'confidence': training_results.get('test_score', 0) if training_results else 0,
                    'predicted_change': (predictions[-1] - float(df['Close'].iloc[-1])) / float(df['Close'].iloc[-1]) * 100
                }
        
        # Volume
        colors = ['#26a69a' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ef5350' 
                 for i in range(len(df))]
        fig.add_trace(go.Bar(
            x=df.index, y=df['Volume'],
            marker_color=colors, showlegend=False
        ), row=2, col=1)
        
        # RSI
        if len(df) >= 14:
            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            rs = gain / (loss + 1e-10)
            rsi = 100 - (100 / (1 + rs))
            
            fig.add_trace(go.Scatter(
                x=df.index, y=rsi,
                mode='lines', name='RSI',
                line=dict(color='purple', width=2)
            ), row=3, col=1)
            
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.3, row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.3, row=3, col=1)
        
        # MACD
        if len(df) >= 26:
            ema12 = df['Close'].ewm(span=12).mean()
            ema26 = df['Close'].ewm(span=26).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9).mean()
            histogram = macd_line - signal_line
            
            fig.add_trace(go.Scatter(
                x=df.index, y=macd_line,
                mode='lines', name='MACD',
                line=dict(color='blue', width=1.5)
            ), row=4, col=1)
            
            fig.add_trace(go.Scatter(
                x=df.index, y=signal_line,
                mode='lines', name='Signal',
                line=dict(color='red', width=1.5)
            ), row=4, col=1)
            
            hist_colors = ['green' if h >= 0 else 'red' for h in histogram]
            fig.add_trace(go.Bar(
                x=df.index, y=histogram,
                marker_color=hist_colors,
                showlegend=False, opacity=0.4
            ), row=4, col=1)
        
        # Calculate price range
        price_min = df[['Open', 'High', 'Low', 'Close']].min().min()
        price_max = df[['Open', 'High', 'Low', 'Close']].max().max()
        price_range = price_max - price_min
        
        # Update layout
        fig.update_layout(
            title=f'{symbol.upper()} - {period.upper()} - {source} (Real Data)',
            height=900,
            showlegend=True,
            hovermode='x unified',
            xaxis_rangeslider_visible=False,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Update y-axes
        fig.update_yaxes(
            title_text="Price ($)",
            range=[price_min - price_range*0.1, price_max + price_range*0.1],
            row=1, col=1
        )
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=3, col=1)
        fig.update_yaxes(title_text="MACD", row=4, col=1)
        
        # Return response
        return jsonify({
            'success': True,
            'chart': json.loads(fig.to_json()),
            'stats': {
                'symbol': symbol.upper(),
                'period': period,
                'min_price': float(price_min),
                'max_price': float(price_max),
                'current_price': current_price,
                'price_change': float(df['Close'].iloc[-1] - df['Close'].iloc[0]),
                'price_change_pct': float((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100),
                'data_points': len(df),
                'source': source,
                'ml_predictions': ml_info
            }
        })
        
    except Exception as e:
        print(f"Error in generate_chart: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/')
def index():
    """Main interface - Real Data Only"""
    html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Stock Analysis - Real Data Only</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
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
            border-radius: 12px;
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
        
        .real-data-badge {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            margin-left: 10px;
            font-weight: 600;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 10px;
        }
        
        .status-yahoo { background: #4CAF50; color: white; }
        .status-alpha { background: #FF9800; color: white; }
        
        .controls {
            background: white;
            border-radius: 12px;
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
            font-size: 12px;
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
        }
        
        .control-group input:focus,
        .control-group select:focus {
            border-color: #667eea;
            outline: none;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            margin-top: 10px;
        }
        
        .checkbox-group input {
            width: 20px;
            height: 20px;
            margin-right: 10px;
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
            margin-right: 15px;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        
        .chart-container {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        #chart {
            min-height: 900px;
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
            font-size: 12px;
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
        
        .ml-badge {
            background: linear-gradient(135deg, #9C27B0, #7B1FA2);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            margin-left: 8px;
            font-weight: 600;
        }
        
        .quick-symbols {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .symbol-btn {
            padding: 8px 16px;
            background: #f5f5f5;
            border: 1px solid #e0e0e0;
            border-radius: 20px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .symbol-btn:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        .error-message {
            background: #fee;
            color: #c00;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            display: none;
        }
        
        .success-message {
            background: #efe;
            color: #060;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            display: none;
        }
        
        #loading {
            text-align: center;
            padding: 100px;
            color: #999;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
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
            <h1>📈 Stock Analysis System 
                <span class="real-data-badge">REAL DATA ONLY</span>
                <span class="ml-badge">ML ENHANCED</span>
                <span id="dataSource" class="status-badge status-yahoo">Yahoo Finance</span>
            </h1>
            <p>Professional analysis with real market data only - NO synthetic/test data</p>
        </div>
        
        <div id="errorMessage" class="error-message"></div>
        <div id="successMessage" class="success-message"></div>
        
        <div class="controls">
            <div class="controls-grid">
                <div class="control-group">
                    <label>Stock Symbol</label>
                    <input type="text" id="symbol" value="AAPL" placeholder="Enter symbol">
                </div>
                
                <div class="control-group">
                    <label>Time Period</label>
                    <select id="period">
                        <option value="1d">1 Day (5-min)</option>
                        <option value="5d">5 Days (30-min)</option>
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
                
                <div class="control-group">
                    <label>Options</label>
                    <div class="checkbox-group">
                        <input type="checkbox" id="showML" checked>
                        <label for="showML">Show ML Predictions</label>
                    </div>
                </div>
            </div>
            
            <div>
                <button onclick="loadChart()">🔄 Generate Chart</button>
                <button onclick="fetchData()">📊 Get Raw Data</button>
            </div>
            
            <div class="quick-symbols">
                <span style="color: #666; margin-right: 10px;">Quick Access:</span>
                <span class="symbol-btn" onclick="quickLoad('AAPL')">AAPL</span>
                <span class="symbol-btn" onclick="quickLoad('GOOGL')">GOOGL</span>
                <span class="symbol-btn" onclick="quickLoad('MSFT')">MSFT</span>
                <span class="symbol-btn" onclick="quickLoad('TSLA')">TSLA</span>
                <span class="symbol-btn" onclick="quickLoad('AMZN')">AMZN</span>
                <span class="symbol-btn" onclick="quickLoad('CBA')">CBA</span>
                <span class="symbol-btn" onclick="quickLoad('BHP')">BHP</span>
                <span class="symbol-btn" onclick="quickLoad('CSL')">CSL</span>
            </div>
        </div>
        
        <div id="statsContainer" class="stats-grid"></div>
        
        <div class="chart-container">
            <div id="chart">
                <div id="loading">Select options and click "Generate Chart" to load real market data</div>
            </div>
        </div>
    </div>
    
    <script>
        function showError(message) {
            const errorDiv = document.getElementById('errorMessage');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            setTimeout(() => { errorDiv.style.display = 'none'; }, 10000);
        }
        
        function showSuccess(message) {
            const successDiv = document.getElementById('successMessage');
            successDiv.textContent = message;
            successDiv.style.display = 'block';
            setTimeout(() => { successDiv.style.display = 'none'; }, 5000);
        }
        
        function quickLoad(symbol) {
            document.getElementById('symbol').value = symbol;
            loadChart();
        }
        
        async function fetchData() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            
            try {
                const response = await fetch(`/api/stock/${symbol}?period=${period}`);
                const data = await response.json();
                
                if (data.error) {
                    showError('Error: ' + data.error);
                    return;
                }
                
                console.log('Real Stock Data:', data);
                showSuccess(`Real data fetched successfully! Source: ${data.source}, Points: ${data.data_points}`);
                
            } catch (error) {
                showError('Failed to fetch data: ' + error.message);
            }
        }
        
        async function loadChart() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            const chartType = document.getElementById('chartType').value;
            const showML = document.getElementById('showML').checked;
            
            if (!symbol) {
                showError('Please enter a stock symbol');
                return;
            }
            
            document.getElementById('chart').innerHTML = 
                '<div id="loading"><div class="spinner"></div>Loading real market data...</div>';
            
            try {
                const response = await fetch('/api/chart', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        symbol: symbol,
                        period: period,
                        chart_type: chartType,
                        show_ml: showML
                    })
                });
                
                const result = await response.json();
                
                if (!result.success) {
                    throw new Error(result.error || 'No real data available');
                }
                
                // Update data source badge
                const badge = document.getElementById('dataSource');
                badge.textContent = result.stats.source;
                badge.className = 'status-badge ' + 
                    (result.stats.source.includes('Yahoo') ? 'status-yahoo' : 'status-alpha');
                
                // Render chart
                Plotly.newPlot('chart', result.chart.data, result.chart.layout, {
                    responsive: true,
                    displayModeBar: true,
                    displaylogo: false
                });
                
                // Update stats
                updateStats(result.stats);
                
                showSuccess(`Chart loaded with real ${result.stats.source} data`);
                
            } catch (error) {
                document.getElementById('chart').innerHTML = 
                    `<div id="loading">❌ ${error.message}<br><br>Please verify the stock symbol and try again.</div>`;
                showError(error.message);
            }
        }
        
        function updateStats(stats) {
            const changeClass = stats.price_change >= 0 ? 'positive' : 'negative';
            const changeSymbol = stats.price_change >= 0 ? '▲' : '▼';
            
            let mlCard = '';
            if (stats.ml_predictions && stats.ml_predictions.predictions) {
                const mlChange = stats.ml_predictions.predicted_change;
                const mlClass = mlChange >= 0 ? 'positive' : 'negative';
                const mlSymbol = mlChange >= 0 ? '📈' : '📉';
                
                mlCard = `
                    <div class="stat-card">
                        <div class="stat-label">ML Prediction (5 days)</div>
                        <div class="stat-value">
                            ${mlSymbol} ${mlChange >= 0 ? '+' : ''}${mlChange.toFixed(2)}%
                        </div>
                        <div class="stat-change">
                            Confidence: ${(stats.ml_predictions.confidence * 100).toFixed(1)}%
                        </div>
                    </div>
                `;
            }
            
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
                    <div class="stat-label">Price Range (${stats.period})</div>
                    <div class="stat-value">$${stats.min_price.toFixed(2)} - $${stats.max_price.toFixed(2)}</div>
                    <div class="stat-change" style="color: #666;">
                        Data Points: ${stats.data_points}
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Data Source</div>
                    <div class="stat-value" style="font-size: 18px;">${stats.source}</div>
                    <div class="stat-change" style="color: #666;">
                        Symbol: ${stats.symbol}
                    </div>
                </div>
                ${mlCard}
            `;
        }
        
        // Load initial chart on page load
        window.addEventListener('load', () => {
            setTimeout(loadChart, 500);
        });
    </script>
</body>
</html>
    '''
    return render_template_string(html)

@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    print("=" * 70)
    print("STOCK ANALYSIS SYSTEM - REAL DATA ONLY")
    print("=" * 70)
    print("Features:")
    print("✅ REAL market data only - NO synthetic/test data")
    print("✅ Machine Learning predictions based on real data")
    print("✅ Yahoo Finance primary source")
    print("✅ Alpha Vantage fallback")
    print("✅ All timeframes: 1d, 5d, 1mo, 3mo, 6mo, 1y, 5y")
    print("✅ Technical indicators: RSI, MACD, Bollinger Bands")
    print("✅ Australian stocks auto-detection")
    print("=" * 70)
    print("Starting server at: http://localhost:8000")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=8000, debug=False)