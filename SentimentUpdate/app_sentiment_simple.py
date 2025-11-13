"""
Simplified Sentiment Analysis App - Works without scikit-learn compilation
"""

import os
os.environ['FLASK_SKIP_DOTENV'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import traceback

app = Flask(__name__)
CORS(app)

class SimpleSentimentAnalyzer:
    """Simplified market sentiment analyzer"""
    
    def __init__(self):
        self.indicators = {
            'VIX': '^VIX',
            'SP500': '^GSPC',
            'DJI': '^DJI',
            'NASDAQ': '^IXIC',
            '10Y_YIELD': '^TNX',
            'DOLLAR': 'DX-Y.NYB'
        }
        
    def safe_get_data(self, ticker, period='5d'):
        """Safely fetch data with error handling"""
        try:
            data = yf.Ticker(ticker).history(period=period)
            if data.empty:
                return None
            return data
        except:
            return None
    
    def get_vix_sentiment(self):
        """Get VIX-based sentiment"""
        try:
            vix_data = self.safe_get_data('^VIX')
            if vix_data is None or vix_data.empty:
                return {'score': 0, 'level': 'Unknown', 'value': 0}
            
            current_vix = float(vix_data['Close'].iloc[-1])
            
            # VIX levels interpretation
            if current_vix < 12:
                sentiment = 'Low Fear'
                score = 80
            elif current_vix < 20:
                sentiment = 'Normal'
                score = 50
            elif current_vix < 30:
                sentiment = 'Elevated Fear'
                score = 20
            else:
                sentiment = 'High Fear'
                score = -20
            
            return {
                'score': score,
                'level': sentiment,
                'value': round(current_vix, 2)
            }
        except Exception as e:
            return {'score': 0, 'level': 'Error', 'value': 0, 'error': str(e)}
    
    def get_market_breadth(self):
        """Calculate simple market breadth"""
        try:
            indices = {}
            for name, ticker in [('SP500', '^GSPC'), ('DOW', '^DJI'), ('NASDAQ', '^IXIC')]:
                data = self.safe_get_data(ticker, '2d')
                if data is not None and len(data) >= 2:
                    change = ((data['Close'].iloc[-1] / data['Close'].iloc[-2]) - 1) * 100
                    indices[name] = round(change, 2)
                else:
                    indices[name] = 0
            
            # Calculate average change
            avg_change = sum(indices.values()) / len(indices) if indices else 0
            
            # Determine sentiment
            if avg_change > 1:
                sentiment = 'Strong Positive'
                score = 60
            elif avg_change > 0:
                sentiment = 'Positive'
                score = 30
            elif avg_change > -1:
                sentiment = 'Negative'
                score = -30
            else:
                sentiment = 'Strong Negative'
                score = -60
            
            return {
                'score': score,
                'sentiment': sentiment,
                'indices': indices,
                'average_change': round(avg_change, 2)
            }
        except Exception as e:
            return {'score': 0, 'sentiment': 'Error', 'indices': {}, 'error': str(e)}
    
    def get_combined_sentiment(self):
        """Get combined sentiment score"""
        try:
            vix = self.get_vix_sentiment()
            breadth = self.get_market_breadth()
            
            # Weighted average
            total_score = (vix.get('score', 0) * 0.5 + breadth.get('score', 0) * 0.5)
            
            # Determine overall sentiment
            if total_score > 40:
                overall = 'Bullish'
            elif total_score > 0:
                overall = 'Slightly Bullish'
            elif total_score > -40:
                overall = 'Slightly Bearish'
            else:
                overall = 'Bearish'
            
            return {
                'overall_score': round(total_score, 2),
                'overall_sentiment': overall,
                'vix': vix,
                'market_breadth': breadth,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'overall_score': 0,
                'overall_sentiment': 'Error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

class SimpleTechnicalAnalyzer:
    """Simple technical indicators without talib"""
    
    @staticmethod
    def calculate_sma(data, period):
        """Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def calculate_rsi(data, period=14):
        """Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_indicators(df):
        """Calculate basic indicators"""
        try:
            close = df['Close']
            
            # Moving averages
            sma_20 = SimpleTechnicalAnalyzer.calculate_sma(close, 20)
            sma_50 = SimpleTechnicalAnalyzer.calculate_sma(close, 50)
            
            # RSI
            rsi = SimpleTechnicalAnalyzer.calculate_rsi(close)
            
            # Current values
            current_price = float(close.iloc[-1])
            
            return {
                'current_price': round(current_price, 2),
                'sma_20': round(float(sma_20.iloc[-1]), 2) if not pd.isna(sma_20.iloc[-1]) else 0,
                'sma_50': round(float(sma_50.iloc[-1]), 2) if len(sma_50) > 0 and not pd.isna(sma_50.iloc[-1]) else 0,
                'rsi': round(float(rsi.iloc[-1]), 2) if not pd.isna(rsi.iloc[-1]) else 50,
                'volume': int(df['Volume'].iloc[-1])
            }
        except Exception as e:
            return {
                'current_price': 0,
                'sma_20': 0,
                'sma_50': 0,
                'rsi': 50,
                'volume': 0,
                'error': str(e)
            }

# Global instances
sentiment_analyzer = SimpleSentimentAnalyzer()
tech_analyzer = SimpleTechnicalAnalyzer()

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get stock data with indicators"""
    try:
        # Handle Australian stocks
        if symbol.upper() in ['CBA', 'BHP', 'WBC', 'ANZ', 'CSL', 'NAB', 'WES', 'WOW', 'MQG', 'TLS']:
            symbol = f"{symbol.upper()}.AX"
        
        period = request.args.get('period', '1mo')
        
        # Fetch data
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            return jsonify({'error': 'No data available', 'symbol': symbol}), 404
        
        # Get indicators
        indicators = tech_analyzer.calculate_indicators(df)
        
        # Prepare candlestick data
        candlestick_data = []
        for index, row in df.iterrows():
            candlestick_data.append({
                'date': index.strftime('%Y-%m-%d'),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            })
        
        return jsonify({
            'symbol': symbol,
            'period': period,
            'indicators': indicators,
            'candlestick_data': candlestick_data,
            'data_points': len(candlestick_data)
        })
        
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e), 'symbol': symbol}), 500

@app.route('/api/sentiment')
def get_sentiment():
    """Get market sentiment"""
    try:
        sentiment = sentiment_analyzer.get_combined_sentiment()
        return jsonify(sentiment)
    except Exception as e:
        print(f"Sentiment error: {e}")
        return jsonify({'error': str(e), 'overall_score': 0, 'overall_sentiment': 'Unknown'}), 500

@app.route('/')
def home():
    """Serve the main interface"""
    return render_template_string(HTML_TEMPLATE)

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis with Sentiment</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <script src="https://cdn.jsdelivr.net/npm/hammerjs@2.0.8"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .card {
            background: white;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 { color: #333; margin-bottom: 10px; }
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        input, select, button {
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ddd;
            font-size: 14px;
        }
        button {
            background: #667eea;
            color: white;
            cursor: pointer;
            border: none;
        }
        button:hover { background: #5a67d8; }
        .sentiment-card {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .sentiment-item {
            padding: 15px;
            background: #f7f7f7;
            border-radius: 8px;
            text-align: center;
        }
        .sentiment-score {
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }
        .bullish { color: #10b981; }
        .bearish { color: #ef4444; }
        .neutral { color: #6b7280; }
        #chartContainer {
            position: relative;
            height: 500px;
        }
        .indicators {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 20px;
        }
        .indicator {
            padding: 10px;
            background: #f3f4f6;
            border-radius: 8px;
        }
        .indicator-label {
            font-size: 12px;
            color: #6b7280;
        }
        .indicator-value {
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }
        .error {
            background: #fee;
            color: #c00;
            padding: 10px;
            border-radius: 8px;
            margin: 10px 0;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card header">
            <h1>📈 Stock Analysis with Market Sentiment</h1>
            <p style="color: #666;">Real-time data from Yahoo Finance</p>
        </div>

        <div class="card">
            <h2 style="margin-bottom: 15px;">Market Sentiment</h2>
            <div id="sentimentDashboard" class="sentiment-card">
                <div class="loading">Loading sentiment data...</div>
            </div>
        </div>

        <div class="card">
            <div class="controls">
                <input type="text" id="symbolInput" placeholder="Enter symbol (e.g., AAPL, CBA)" value="AAPL">
                <select id="periodSelect">
                    <option value="1d">1 Day</option>
                    <option value="5d">5 Days</option>
                    <option value="1mo" selected>1 Month</option>
                    <option value="3mo">3 Months</option>
                    <option value="6mo">6 Months</option>
                    <option value="1y">1 Year</option>
                </select>
                <button onclick="loadStockData()">Load Data</button>
                <button onclick="resetZoom()">Reset Zoom</button>
            </div>
            
            <div id="errorMessage"></div>
            
            <div id="chartContainer">
                <canvas id="stockChart"></canvas>
            </div>
            
            <div id="indicators" class="indicators"></div>
        </div>
    </div>

    <script>
        let chart = null;
        
        // Load sentiment on page load
        window.addEventListener('load', () => {
            loadSentiment();
            loadStockData();
            // Refresh sentiment every 30 seconds
            setInterval(loadSentiment, 30000);
        });

        async function loadSentiment() {
            try {
                const response = await fetch('/api/sentiment');
                const data = await response.json();
                
                if (response.ok) {
                    updateSentimentDashboard(data);
                } else {
                    document.getElementById('sentimentDashboard').innerHTML = 
                        '<div class="error">Failed to load sentiment data</div>';
                }
            } catch (error) {
                console.error('Sentiment error:', error);
                document.getElementById('sentimentDashboard').innerHTML = 
                    '<div class="error">Error loading sentiment</div>';
            }
        }

        function updateSentimentDashboard(data) {
            const dashboard = document.getElementById('sentimentDashboard');
            const score = data.overall_score || 0;
            const sentiment = data.overall_sentiment || 'Unknown';
            
            let sentimentClass = 'neutral';
            if (score > 20) sentimentClass = 'bullish';
            else if (score < -20) sentimentClass = 'bearish';
            
            let html = `
                <div class="sentiment-item">
                    <div class="sentiment-label">Overall Sentiment</div>
                    <div class="sentiment-score ${sentimentClass}">${sentiment}</div>
                    <div>Score: ${score.toFixed(1)}</div>
                </div>
            `;
            
            // Add VIX if available
            if (data.vix) {
                html += `
                    <div class="sentiment-item">
                        <div class="sentiment-label">VIX Fear Index</div>
                        <div class="sentiment-score">${data.vix.value || 0}</div>
                        <div>${data.vix.level || ''}</div>
                    </div>
                `;
            }
            
            // Add market breadth if available
            if (data.market_breadth && data.market_breadth.average_change !== undefined) {
                const change = data.market_breadth.average_change;
                const changeClass = change > 0 ? 'bullish' : 'bearish';
                html += `
                    <div class="sentiment-item">
                        <div class="sentiment-label">Market Breadth</div>
                        <div class="sentiment-score ${changeClass}">${change > 0 ? '+' : ''}${change.toFixed(2)}%</div>
                        <div>${data.market_breadth.sentiment || ''}</div>
                    </div>
                `;
            }
            
            dashboard.innerHTML = html;
        }

        async function loadStockData() {
            const symbol = document.getElementById('symbolInput').value;
            const period = document.getElementById('periodSelect').value;
            const errorDiv = document.getElementById('errorMessage');
            const indicatorsDiv = document.getElementById('indicators');
            
            errorDiv.innerHTML = '';
            indicatorsDiv.innerHTML = '<div class="loading">Loading...</div>';
            
            try {
                const response = await fetch(`/api/stock/${symbol}?period=${period}`);
                const data = await response.json();
                
                if (response.ok) {
                    updateChart(data);
                    updateIndicators(data.indicators);
                } else {
                    errorDiv.innerHTML = `<div class="error">Error: ${data.error || 'Failed to load data'}</div>`;
                }
            } catch (error) {
                console.error('Error:', error);
                errorDiv.innerHTML = '<div class="error">Network error. Please try again.</div>';
            }
        }

        function updateIndicators(indicators) {
            if (!indicators) return;
            
            const indicatorsDiv = document.getElementById('indicators');
            indicatorsDiv.innerHTML = `
                <div class="indicator">
                    <div class="indicator-label">Current Price</div>
                    <div class="indicator-value">$${indicators.current_price || 0}</div>
                </div>
                <div class="indicator">
                    <div class="indicator-label">SMA 20</div>
                    <div class="indicator-value">$${indicators.sma_20 || 0}</div>
                </div>
                <div class="indicator">
                    <div class="indicator-label">SMA 50</div>
                    <div class="indicator-value">$${indicators.sma_50 || 0}</div>
                </div>
                <div class="indicator">
                    <div class="indicator-label">RSI</div>
                    <div class="indicator-value">${indicators.rsi || 50}</div>
                </div>
                <div class="indicator">
                    <div class="indicator-label">Volume</div>
                    <div class="indicator-value">${(indicators.volume / 1000000).toFixed(2)}M</div>
                </div>
            `;
        }

        function updateChart(data) {
            const ctx = document.getElementById('stockChart').getContext('2d');
            
            if (chart) {
                chart.destroy();
            }
            
            const candlestickData = data.candlestick_data.map(d => ({
                x: new Date(d.date).getTime(),
                o: d.open,
                h: d.high,
                l: d.low,
                c: d.close
            }));
            
            chart = new Chart(ctx, {
                type: 'candlestick',
                data: {
                    datasets: [{
                        label: data.symbol,
                        data: candlestickData,
                        borderColor: 'rgba(102, 126, 234, 1)',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        zoom: {
                            zoom: {
                                wheel: { enabled: true },
                                pinch: { enabled: true },
                                mode: 'x'
                            },
                            pan: {
                                enabled: true,
                                mode: 'x'
                            }
                        },
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'day',
                                displayFormats: { day: 'MMM dd' }
                            }
                        },
                        y: {
                            position: 'right'
                        }
                    }
                }
            });
        }

        function resetZoom() {
            if (chart) {
                chart.resetZoom();
            }
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("=" * 60)
    print("SIMPLIFIED STOCK ANALYSIS WITH SENTIMENT")
    print("=" * 60)
    print("Starting server at http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)