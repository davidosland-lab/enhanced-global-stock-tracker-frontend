#!/usr/bin/env python3
"""
Stock Analysis System - WORKING VERSION
Fixed to match yesterday's working code
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

def fetch_stock_data(symbol, period='1mo'):
    """WORKING fetch function - simplified and tested"""
    try:
        # Auto-detect Australian stocks
        au_stocks = ['CBA', 'BHP', 'CSL', 'NAB', 'ANZ', 'WBC', 'WES', 'MQG', 'TLS', 'WOW']
        symbol_upper = symbol.upper().replace('.AX', '')
        if symbol_upper in au_stocks and not symbol.endswith('.AX'):
            symbol = f"{symbol_upper}.AX"
        
        print(f"Fetching {symbol} from Yahoo Finance for period {period}")
        
        # Create ticker - THIS WORKS
        ticker = yf.Ticker(symbol)
        
        # Use simple history call - THIS IS WHAT WORKS
        hist = ticker.history(period=period)
        
        if hist.empty:
            print(f"No data returned for {symbol}")
            # Try Alpha Vantage as fallback
            return fetch_alpha_vantage_data(symbol, period)
        
        print(f"Successfully fetched {len(hist)} data points for {symbol}")
        
        # Get current price
        current_price = float(hist['Close'].iloc[-1])
        
        return hist, "Yahoo Finance", current_price
        
    except Exception as e:
        print(f"Yahoo Finance error: {str(e)}")
        # Try Alpha Vantage as fallback
        return fetch_alpha_vantage_data(symbol, period)

def fetch_alpha_vantage_data(symbol, period='1mo'):
    """Alpha Vantage fallback"""
    try:
        # Remove .AX for Alpha Vantage
        av_symbol = symbol.replace('.AX', '')
        print(f"Fetching {av_symbol} from Alpha Vantage")
        
        # Use simple daily data
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': av_symbol,
            'apikey': ALPHA_VANTAGE_API_KEY,
            'outputsize': 'full'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Time Series (Daily)' not in data:
            print("Alpha Vantage: No data returned")
            return None, None, None
        
        # Parse time series
        time_series = data['Time Series (Daily)']
        df_data = []
        
        for timestamp, values in time_series.items():
            df_data.append({
                'Date': pd.to_datetime(timestamp),
                'Open': float(values['1. open']),
                'High': float(values['2. high']),
                'Low': float(values['3. low']),
                'Close': float(values['4. close']),
                'Volume': int(values['5. volume'])
            })
        
        df = pd.DataFrame(df_data)
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        
        # Filter by period
        days_map = {'1d': 1, '5d': 5, '1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '5y': 1825}
        days = days_map.get(period, 30)
        cutoff = datetime.now() - timedelta(days=days)
        df = df[df.index >= cutoff]
        
        if not df.empty:
            print(f"Alpha Vantage: Got {len(df)} data points")
            return df, "Alpha Vantage", float(df['Close'].iloc[-1])
            
    except Exception as e:
        print(f"Alpha Vantage error: {str(e)}")
    
    return None, None, None

# Global instances
ml_predictor = MLPredictor()

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """API endpoint for stock data"""
    try:
        period = request.args.get('period', '1mo')
        df, source, current_price = fetch_stock_data(symbol, period)
        
        if df is None or df.empty:
            return jsonify({
                'error': f'No data available for {symbol}',
                'symbol': symbol,
                'period': period
            }), 404
        
        # ML predictions
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
        
        # Return data
        return jsonify({
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
            'ml_predictions': ml_results
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart', methods=['POST', 'OPTIONS'])
def generate_chart():
    """Generate chart"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        symbol = data.get('symbol', 'AAPL')
        period = data.get('period', '1mo')
        chart_type = data.get('chart_type', 'candlestick')
        show_ml = data.get('show_ml', True)
        
        # Fetch data
        df, source, current_price = fetch_stock_data(symbol, period)
        
        if df is None or df.empty:
            return jsonify({
                'error': f'No data available for {symbol}',
                'success': False
            }), 404
        
        # Create chart
        fig = make_subplots(
            rows=4, cols=1,
            row_heights=[0.5, 0.15, 0.15, 0.2],
            subplot_titles=['Price', 'Volume', 'RSI', 'MACD'],
            vertical_spacing=0.05
        )
        
        # Price chart
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
        else:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['Close'],
                mode='lines', name='Close',
                line=dict(color='#2196F3', width=2)
            ), row=1, col=1)
        
        # Moving averages
        if len(df) >= 20:
            sma20 = df['Close'].rolling(20).mean()
            fig.add_trace(go.Scatter(
                x=df.index, y=sma20,
                line=dict(color='orange', width=1),
                name='SMA 20'
            ), row=1, col=1)
        
        # ML predictions
        ml_info = {}
        if show_ml and len(df) >= 50:
            training_results = ml_predictor.train(df)
            predictions = ml_predictor.predict(df, days=5)
            
            if predictions:
                last_date = df.index[-1]
                future_dates = [last_date + timedelta(days=i+1) for i in range(len(predictions))]
                
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
        
        # Update layout
        price_min = df[['Open', 'High', 'Low', 'Close']].min().min()
        price_max = df[['Open', 'High', 'Low', 'Close']].max().max()
        price_range = price_max - price_min
        
        fig.update_layout(
            title=f'{symbol.upper()} - {source}',
            height=900,
            showlegend=True,
            hovermode='x unified',
            xaxis_rangeslider_visible=False
        )
        
        fig.update_yaxes(
            title_text="Price ($)",
            range=[price_min - price_range*0.1, price_max + price_range*0.1],
            row=1, col=1
        )
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=3, col=1)
        fig.update_yaxes(title_text="MACD", row=4, col=1)
        
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
        print(f"Chart error: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/')
def index():
    """Main interface"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Stock Analysis - WORKING VERSION</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 20px;
        }
        .container { max-width: 1600px; margin: 0 auto; }
        .header, .controls, .chart-container {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
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
        }
        .control-group input, .control-group select {
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
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
            margin-right: 10px;
        }
        button:hover {
            transform: translateY(-2px);
        }
        #chart { min-height: 900px; }
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
        }
        .symbol-btn:hover {
            background: #667eea;
            color: white;
        }
        .status { 
            padding: 10px; 
            margin: 20px 0; 
            border-radius: 8px;
            display: none;
        }
        .status.success { background: #d4edda; color: #155724; display: block; }
        .status.error { background: #f8d7da; color: #721c24; display: block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Stock Analysis System - WORKING VERSION</h1>
            <p>Fixed Yahoo Finance + Alpha Vantage with ML predictions</p>
        </div>
        
        <div id="status" class="status"></div>
        
        <div class="controls">
            <div class="controls-grid">
                <div class="control-group">
                    <label>Stock Symbol</label>
                    <input type="text" id="symbol" value="AAPL">
                </div>
                <div class="control-group">
                    <label>Time Period</label>
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
                    </select>
                </div>
            </div>
            
            <button onclick="loadChart()">Generate Chart</button>
            <button onclick="testAPI()">Test API</button>
            
            <div class="quick-symbols">
                <span style="color: #666;">Quick: </span>
                <span class="symbol-btn" onclick="setSymbol('AAPL')">AAPL</span>
                <span class="symbol-btn" onclick="setSymbol('GOOGL')">GOOGL</span>
                <span class="symbol-btn" onclick="setSymbol('MSFT')">MSFT</span>
                <span class="symbol-btn" onclick="setSymbol('TSLA')">TSLA</span>
                <span class="symbol-btn" onclick="setSymbol('CBA')">CBA</span>
                <span class="symbol-btn" onclick="setSymbol('BHP')">BHP</span>
            </div>
        </div>
        
        <div class="chart-container">
            <div id="chart">Click "Generate Chart" to load data</div>
        </div>
    </div>
    
    <script>
        function setSymbol(sym) {
            document.getElementById('symbol').value = sym;
            loadChart();
        }
        
        function showStatus(message, isError) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + (isError ? 'error' : 'success');
        }
        
        async function testAPI() {
            const symbol = document.getElementById('symbol').value;
            try {
                const response = await fetch(`/api/stock/${symbol}?period=1mo`);
                const data = await response.json();
                if (data.error) {
                    showStatus('Error: ' + data.error, true);
                } else {
                    showStatus(`Success! Source: ${data.source}, Points: ${data.data_points}`, false);
                }
            } catch (e) {
                showStatus('Error: ' + e.message, true);
            }
        }
        
        async function loadChart() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            const chartType = document.getElementById('chartType').value;
            
            document.getElementById('chart').innerHTML = 'Loading...';
            
            try {
                const response = await fetch('/api/chart', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({symbol, period, chart_type: chartType})
                });
                
                const result = await response.json();
                
                if (!result.success) {
                    throw new Error(result.error || 'Failed to load');
                }
                
                Plotly.newPlot('chart', result.chart.data, result.chart.layout);
                showStatus(`Loaded ${result.stats.data_points} points from ${result.stats.source}`, false);
                
            } catch (error) {
                document.getElementById('chart').innerHTML = 'Error: ' + error.message;
                showStatus('Failed: ' + error.message, true);
            }
        }
        
        // Load on start
        window.addEventListener('load', () => setTimeout(loadChart, 500));
    </script>
</body>
</html>
    ''')

@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    print("=" * 70)
    print("STOCK ANALYSIS - WORKING VERSION")
    print("=" * 70)
    print("FIXED: Using simple ticker.history() that actually works")
    print("NO random/test data - Only real Yahoo/Alpha Vantage")
    print("=" * 70)
    print("Starting at: http://localhost:8000")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=8000, debug=False)