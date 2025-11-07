#!/usr/bin/env python3
"""
Stock Analysis using Alpha Vantage as Primary Source
For when Yahoo Finance is rate limiting (429 errors)
"""

import os
import sys
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import warnings
import requests

warnings.filterwarnings('ignore')

# Skip dotenv
os.environ['FLASK_SKIP_DOTENV'] = '1'

print("=" * 60)
print("STOCK ANALYSIS - ALPHA VANTAGE PRIMARY")
print("=" * 60)
print("Using Alpha Vantage to avoid Yahoo rate limits")
print("API Key configured: 68ZFANK047DL0KSR")
print("=" * 60)
print(f"Starting server at http://localhost:5000")
print("Press Ctrl+C to stop")
print("=" * 60)

app = Flask(__name__)
CORS(app)

# Alpha Vantage configuration
ALPHA_VANTAGE_KEY = "68ZFANK047DL0KSR"
AV_CALL_COUNT = 0
AV_LAST_CALL = time.time()

def av_rate_limit():
    """Alpha Vantage allows 5 calls per minute"""
    global AV_CALL_COUNT, AV_LAST_CALL
    
    now = time.time()
    if now - AV_LAST_CALL > 60:
        AV_CALL_COUNT = 0
        AV_LAST_CALL = now
    
    if AV_CALL_COUNT >= 5:
        wait_time = 60 - (now - AV_LAST_CALL)
        if wait_time > 0:
            print(f"Rate limit: waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
            AV_CALL_COUNT = 0
            AV_LAST_CALL = time.time()
    
    AV_CALL_COUNT += 1

class AlphaVantageDataFetcher:
    """Fetch data from Alpha Vantage"""
    
    def fetch_daily(self, symbol):
        """Fetch daily data from Alpha Vantage"""
        av_rate_limit()
        
        # Handle Australian stocks - try different formats
        original_symbol = symbol
        
        # Australian stock list
        aus_stocks = {'CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'MQG', 'WOW', 'TLS', 'RIO', 'FMG'}
        
        # Check if it's an Australian stock
        symbol_base = symbol.upper().replace('.AX', '').replace('.AUS', '')
        if symbol_base in aus_stocks:
            # Try with .AUS suffix for Alpha Vantage
            symbols_to_try = [f"{symbol_base}.AUS", symbol_base, f"{symbol_base}.AX"]
        else:
            symbols_to_try = [symbol]
        
        for test_symbol in symbols_to_try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': test_symbol,
                'apikey': ALPHA_VANTAGE_KEY,
                'outputsize': 'compact'  # Last 100 days
            }
        
            try:
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                
                if 'Time Series (Daily)' in data:
                    print(f"✓ Found data for {test_symbol}")
                    ts = data['Time Series (Daily)']
                    df = pd.DataFrame.from_dict(ts, orient='index')
                    df.index = pd.to_datetime(df.index)
                    df = df.sort_index()
                    
                    # Rename columns
                    df.columns = ['1. open', '2. high', '3. low', '4. close', '5. volume']
                    df = df.rename(columns={
                        '1. open': 'Open',
                        '2. high': 'High',
                        '3. low': 'Low',
                        '4. close': 'Close',
                        '5. volume': 'Volume'
                    })
                    df = df.astype(float)
                    
                    return df, float(df['Close'].iloc[-1])
                    
                elif 'Note' in data:
                    print(f"Alpha Vantage rate limit: {data['Note']}")
                    if test_symbol == symbols_to_try[-1]:
                        return None, None
                        
                elif 'Error Message' in data:
                    if test_symbol == symbols_to_try[-1]:
                        print(f"Symbol {original_symbol} not found in Alpha Vantage")
                        return None, None
                    continue
                    
            except Exception as e:
                if test_symbol == symbols_to_try[-1]:
                    print(f"Alpha Vantage error: {e}")
                    return None, None
        
        return None, None
    
    def fetch_quote(self, symbol):
        """Get current quote from Alpha Vantage"""
        av_rate_limit()
        
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': ALPHA_VANTAGE_KEY
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Global Quote' in data and data['Global Quote']:
                quote = data['Global Quote']
                return {
                    'symbol': quote.get('01. symbol'),
                    'open': float(quote.get('02. open', 0)),
                    'high': float(quote.get('03. high', 0)),
                    'low': float(quote.get('04. low', 0)),
                    'price': float(quote.get('05. price', 0)),
                    'volume': int(quote.get('06. volume', 0)),
                    'change': float(quote.get('09. change', 0)),
                    'change_percent': quote.get('10. change percent', '0%')
                }
        except Exception as e:
            print(f"Quote error: {e}")
            return None

class SimpleIndicators:
    """Calculate technical indicators"""
    
    def calculate_all(self, df):
        if df is None or df.empty:
            return {}
        
        indicators = {}
        
        # Moving averages
        if len(df) >= 20:
            indicators['sma_20'] = float(df['Close'].rolling(20).mean().iloc[-1])
        if len(df) >= 50:
            indicators['sma_50'] = float(df['Close'].rolling(50).mean().iloc[-1])
        if len(df) >= 10:
            indicators['sma_10'] = float(df['Close'].rolling(10).mean().iloc[-1])
        
        # RSI
        if len(df) >= 14:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            indicators['rsi'] = float(rsi.iloc[-1])
        
        # Price change
        if len(df) >= 2:
            indicators['daily_change'] = float(
                (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
            )
        
        return indicators

class SimplePredictions:
    """Generate simple trend-based predictions"""
    
    def predict(self, df, days=5):
        if df is None or df.empty or len(df) < 5:
            return []
        
        # Calculate trend
        recent_prices = df['Close'].tail(5)
        trend = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / recent_prices.iloc[0]
        daily_trend = trend / 5
        
        predictions = []
        current_price = float(df['Close'].iloc[-1])
        
        for i in range(1, days + 1):
            predicted_price = current_price * (1 + daily_trend * i)
            predictions.append({
                'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
                'predicted_price': round(predicted_price, 2),
                'trend': 'Bullish' if daily_trend > 0 else 'Bearish' if daily_trend < 0 else 'Neutral'
            })
        
        return predictions

# Global instances
data_fetcher = AlphaVantageDataFetcher()
indicators = SimpleIndicators()
predictor = SimplePredictions()

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get stock data from Alpha Vantage"""
    try:
        # Get daily data
        df, current_price = data_fetcher.fetch_daily(symbol)
        
        if df is None:
            return jsonify({
                'error': 'Unable to fetch data',
                'symbol': symbol,
                'message': 'Check symbol or Alpha Vantage rate limit (5 per minute, 500 per day)'
            }), 404
        
        # Get current quote for more info
        quote = data_fetcher.fetch_quote(symbol)
        
        # Calculate indicators
        tech_indicators = indicators.calculate_all(df)
        
        # Generate predictions
        predictions = predictor.predict(df, days=5)
        
        # Prepare candlestick data
        candlestick_data = []
        for index, row in df.tail(30).iterrows():  # Last 30 days
            candlestick_data.append({
                'date': index.strftime('%Y-%m-%d'),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            })
        
        response = {
            'symbol': symbol,
            'source': 'Alpha Vantage',
            'current_price': current_price,
            'data': candlestick_data,
            'indicators': tech_indicators,
            'predictions': predictions
        }
        
        if quote:
            response['quote'] = quote
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'symbol': symbol
        }), 500

@app.route('/api/sentiment')
def get_sentiment():
    """Simple sentiment based on major indices"""
    # Note: Alpha Vantage doesn't provide VIX, so we'll use major indices
    try:
        # Check S&P 500
        df, price = data_fetcher.fetch_daily('SPY')  # SPY ETF as proxy for S&P 500
        
        if df is not None and len(df) >= 2:
            change = (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]
            
            if change > 0.01:
                sentiment = "Bullish"
                score = 0.5
            elif change < -0.01:
                sentiment = "Bearish"
                score = -0.5
            else:
                sentiment = "Neutral"
                score = 0
                
            return jsonify({
                'sentiment': sentiment,
                'score': score,
                'spy_change': f"{change*100:.2f}%",
                'source': 'Alpha Vantage'
            })
        
        return jsonify({
            'sentiment': 'Unknown',
            'score': 0,
            'message': 'Limited data available'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Stock Analysis - Alpha Vantage</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 20px;
            margin: 0;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 20px;
        }
        .controls {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            align-items: center;
        }
        input, button {
            padding: 12px;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            font-size: 16px;
        }
        input {
            flex: 1;
            max-width: 300px;
        }
        button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            cursor: pointer;
            padding: 12px 30px;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .info-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        .chart-container {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            height: 400px;
        }
        .info-panel {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }
        .price-display {
            font-size: 2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .source {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 20px;
        }
        .indicator {
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        .error {
            background: #fee2e2;
            color: #dc2626;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .warning {
            background: #fef3c7;
            color: #92400e;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        @media (max-width: 768px) {
            .info-grid {
                grid-template-columns: 1fr;
            }
            .controls {
                flex-direction: column;
            }
            input {
                max-width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 Stock Analysis - Alpha Vantage Data</h1>
        <p class="subtitle">Using Alpha Vantage API (Yahoo Finance is rate limiting)</p>
        
        <div class="warning">
            ⚠️ Alpha Vantage Rate Limits: 5 calls per minute, 500 per day
        </div>
        
        <div class="controls">
            <input type="text" id="symbol" placeholder="Enter stock symbol (e.g., AAPL)" value="AAPL">
            <button onclick="fetchData()">Get Analysis</button>
        </div>
        
        <div id="error"></div>
        
        <div class="info-grid">
            <div class="chart-container">
                <canvas id="chart"></canvas>
            </div>
            
            <div class="info-panel">
                <div id="price-info">
                    <div class="price-display">--</div>
                    <div class="source">Enter a symbol to begin</div>
                </div>
                
                <div id="indicators">
                    <h3>Indicators</h3>
                    <div id="indicator-list"></div>
                </div>
                
                <div id="predictions" style="margin-top: 20px;">
                    <h3>Predictions</h3>
                    <div id="prediction-list"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let chart = null;
        
        async function fetchData() {
            const symbol = document.getElementById('symbol').value.toUpperCase();
            
            if (!symbol) {
                document.getElementById('error').innerHTML = 
                    '<div class="error">Please enter a stock symbol</div>';
                return;
            }
            
            // Show loading
            document.getElementById('error').innerHTML = 
                '<div class="warning">Loading from Alpha Vantage...</div>';
            
            try {
                const response = await fetch(`/api/stock/${symbol}`);
                const data = await response.json();
                
                if (data.error) {
                    document.getElementById('error').innerHTML = 
                        `<div class="error">${data.error}: ${data.message || ''}</div>`;
                    return;
                }
                
                document.getElementById('error').innerHTML = '';
                
                // Update price
                document.querySelector('.price-display').textContent = 
                    `$${data.current_price.toFixed(2)}`;
                document.querySelector('.source').textContent = 
                    `Source: ${data.source} | Symbol: ${data.symbol}`;
                
                // Update chart
                updateChart(data);
                
                // Update indicators
                let indicatorHtml = '';
                if (data.indicators) {
                    for (const [key, value] of Object.entries(data.indicators)) {
                        if (typeof value === 'number') {
                            indicatorHtml += `
                                <div class="indicator">
                                    <strong>${key.toUpperCase()}:</strong> ${value.toFixed(2)}
                                </div>
                            `;
                        }
                    }
                }
                document.getElementById('indicator-list').innerHTML = indicatorHtml || 'No indicators';
                
                // Update predictions
                let predictionHtml = '';
                if (data.predictions && data.predictions.length > 0) {
                    data.predictions.forEach(p => {
                        const color = p.trend === 'Bullish' ? 'green' : 
                                     p.trend === 'Bearish' ? 'red' : 'gray';
                        predictionHtml += `
                            <div class="indicator">
                                ${p.date}: <strong>$${p.predicted_price}</strong>
                                <span style="color: ${color}; margin-left: 10px;">${p.trend}</span>
                            </div>
                        `;
                    });
                }
                document.getElementById('prediction-list').innerHTML = predictionHtml || 'No predictions';
                
            } catch (error) {
                document.getElementById('error').innerHTML = 
                    `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        function updateChart(data) {
            const ctx = document.getElementById('chart').getContext('2d');
            
            if (chart) {
                chart.destroy();
            }
            
            chart = new Chart(ctx, {
                type: 'candlestick',
                data: {
                    datasets: [{
                        label: data.symbol,
                        data: data.data.map(d => ({
                            x: new Date(d.date).getTime(),
                            o: d.open,
                            h: d.high,
                            l: d.low,
                            c: d.close
                        }))
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        zoom: {
                            zoom: {
                                enabled: true,
                                mode: 'x'
                            },
                            pan: {
                                enabled: true,
                                mode: 'x'
                            }
                        }
                    }
                }
            });
        }
        
        // Load on enter key
        document.getElementById('symbol').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                fetchData();
            }
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)