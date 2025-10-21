#!/usr/bin/env python3
"""
Yahoo Finance Only Server - Optimized for Australian Stocks
No Alpha Vantage fallback for better reliability
"""

import os
import sys
import json
from datetime import datetime, timedelta

os.environ['FLASK_SKIP_DOTENV'] = '1'

from flask import Flask, jsonify, request, Response
from flask_cors import CORS

import yfinance as yf
import pandas as pd
import numpy as np

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# System state
system_state = {
    'yahoo': 'available',
    'last_fetch': {},
    'supported_markets': {
        'US': '',
        'Australia': '.AX',
        'UK': '.L',
        'Germany': '.DE',
        'Hong Kong': '.HK',
        'Japan': '.T',
        'Canada': '.TO'
    }
}

def get_stock_prediction(symbol, months=2):
    """Generate prediction for any stock"""
    try:
        # Download data
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1y")
        
        if data.empty:
            return None
            
        info = ticker.info
        company_name = info.get('longName', symbol)
        currency = info.get('currency', 'AUD' if '.AX' in symbol else 'USD')
        
        # Current price
        current_price = float(data['Close'].iloc[-1])
        
        # Calculate indicators
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['SMA_200'] = data['Close'].rolling(window=200).mean()
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # Recent performance
        returns_30d = (data['Close'].iloc[-1] / data['Close'].iloc[-30] - 1) * 100 if len(data) > 30 else 0
        returns_90d = (data['Close'].iloc[-1] / data['Close'].iloc[-90] - 1) * 100 if len(data) > 90 else 0
        
        # Volatility
        daily_returns = data['Close'].pct_change()
        volatility = daily_returns.rolling(window=30).std() * np.sqrt(252) * 100
        current_volatility = float(volatility.iloc[-1]) if not pd.isna(volatility.iloc[-1]) else 20
        
        # Trend analysis
        sma20 = float(data['SMA_20'].iloc[-1]) if not pd.isna(data['SMA_20'].iloc[-1]) else current_price
        sma50 = float(data['SMA_50'].iloc[-1]) if not pd.isna(data['SMA_50'].iloc[-1]) else current_price
        current_rsi = float(data['RSI'].iloc[-1]) if not pd.isna(data['RSI'].iloc[-1]) else 50
        
        # Determine trend
        if current_price > sma20 > sma50:
            trend = "Strong Uptrend"
            base_return = 8
        elif current_price > sma50:
            trend = "Uptrend"
            base_return = 5
        elif current_price < sma50:
            trend = "Downtrend"
            base_return = -2
        else:
            trend = "Neutral"
            base_return = 2
        
        # Adjust for RSI
        if current_rsi > 70:
            base_return -= 2
        elif current_rsi < 30:
            base_return += 2
        
        # Australian stocks adjustment
        if '.AX' in symbol:
            base_return *= 1.1
        
        # Generate predictions
        predictions = []
        for month in range(1, months + 1):
            return_pct = base_return * (month / 2)
            target = current_price * (1 + return_pct / 100)
            low = target * (1 - current_volatility / 200)
            high = target * (1 + current_volatility / 200)
            
            predictions.append({
                'month': month,
                'target': round(target, 2),
                'low': round(low, 2),
                'high': round(high, 2),
                'return': round(return_pct, 1)
            })
        
        return {
            'symbol': symbol,
            'company': company_name,
            'currency': currency,
            'current_price': round(current_price, 2),
            'trend': trend,
            'rsi': round(current_rsi, 1),
            'volatility': round(current_volatility, 1),
            'returns_30d': round(returns_30d, 1),
            'returns_90d': round(returns_90d, 1),
            'predictions': predictions
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def index():
    """Serve interface"""
    if os.path.exists('unified_interface_fixed.html'):
        with open('unified_interface_fixed.html', 'r', encoding='utf-8') as f:
            return Response(f.read(), mimetype='text/html')
    return jsonify({'status': 'running', 'service': 'Yahoo Finance Only'})

@app.route('/api/status')
def get_status():
    return jsonify({
        'status': 'running',
        'data_sources': {
            'yahoo': system_state['yahoo'],
            'alpha_vantage': 'disabled',
            'primary': 'yahoo'
        },
        'supported_markets': system_state['supported_markets'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/fetch', methods=['POST', 'OPTIONS'])
def fetch_data():
    """Fetch stock data using Yahoo Finance only"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.json or {}
    symbol = data.get('symbol', '').upper().strip()
    period = data.get('period', '1y')
    
    if not symbol:
        return jsonify({'error': 'Symbol required'}), 400
    
    # Auto-detect Australian stocks
    aus_stocks = ['CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'WOW', 'RIO', 'FMG', 
                  'TLS', 'MQG', 'GMG', 'TCL', 'ALL', 'REA', 'SHL', 'WDS', 'NCM', 'AMC']
    
    if symbol in aus_stocks and '.AX' not in symbol:
        symbol = f"{symbol}.AX"
        print(f"Auto-detected Australian stock: {symbol}")
    
    print(f"Fetching {symbol} from Yahoo Finance...")
    
    try:
        # Use yf.download for reliability
        period_map = {
            '5d': '5d', '1mo': '1mo', '3mo': '3mo',
            '6mo': '6mo', '1y': '1y', '2y': '2y', '5y': '5y'
        }
        yf_period = period_map.get(period, '1y')
        
        df = yf.download(symbol, period=yf_period, progress=False, auto_adjust=True)
        
        if df is not None and not df.empty:
            # Get additional info
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract data
            prices = df['Close'].values.flatten().tolist()
            volumes = df['Volume'].values.flatten().tolist() if 'Volume' in df else []
            
            # Store last fetch
            system_state['last_fetch'][symbol] = datetime.now().isoformat()
            
            return jsonify({
                'symbol': symbol,
                'company': info.get('longName', symbol),
                'currency': info.get('currency', 'AUD' if '.AX' in symbol else 'USD'),
                'source': 'yahoo',
                'data_points': len(df),
                'start_date': df.index[0].strftime('%Y-%m-%d'),
                'end_date': df.index[-1].strftime('%Y-%m-%d'),
                'latest_price': float(prices[-1]),
                'prices': prices,
                'dates': [d.strftime('%Y-%m-%d') for d in df.index],
                'volume': volumes,
                'is_real_data': True,
                'market': 'ASX' if '.AX' in symbol else 'NYSE/NASDAQ'
            })
        else:
            return jsonify({'error': f'No data found for {symbol}'}), 404
            
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return jsonify({
            'error': f'Failed to fetch {symbol}',
            'message': str(e),
            'suggestion': 'Check symbol format. For Australian stocks use .AX suffix (e.g., CBA.AX)'
        }), 500

@app.route('/api/predict', methods=['POST', 'OPTIONS'])
def predict():
    """Generate predictions"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.json or {}
    symbol = data.get('symbol', '').upper().strip()
    months = data.get('months', 2)
    
    if not symbol:
        return jsonify({'error': 'Symbol required'}), 400
    
    # Auto-detect Australian stocks
    aus_stocks = ['CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'WOW', 'RIO', 'FMG']
    if symbol in aus_stocks and '.AX' not in symbol:
        symbol = f"{symbol}.AX"
    
    prediction = get_stock_prediction(symbol, months)
    
    if prediction:
        return jsonify({
            'status': 'success',
            **prediction
        })
    else:
        return jsonify({'error': f'Could not generate prediction for {symbol}'}), 404

@app.route('/api/mcp/query', methods=['POST', 'OPTIONS'])
def mcp_query():
    """Handle AI Assistant queries"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.json or {}
    query = data.get('query', '').lower()
    
    # Extract symbol from query
    import re
    
    # Check for explicit symbols
    symbols = re.findall(r'\b[A-Z]{1,5}(?:\.[A-Z]{1,3})?\b', query.upper())
    
    # Check for company names
    company_map = {
        'commonwealth': 'CBA.AX',
        'cba': 'CBA.AX',
        'bhp': 'BHP.AX',
        'csl': 'CSL.AX',
        'westpac': 'WBC.AX',
        'anz': 'ANZ.AX',
        'woolworths': 'WOW.AX',
        'apple': 'AAPL',
        'microsoft': 'MSFT',
        'google': 'GOOGL'
    }
    
    for company, ticker in company_map.items():
        if company in query:
            symbols = [ticker]
            break
    
    if symbols:
        symbol = symbols[0]
        months = 2
        
        # Extract months if specified
        month_match = re.search(r'(\d+)\s*month', query)
        if month_match:
            months = min(int(month_match.group(1)), 6)
        
        prediction = get_stock_prediction(symbol, months)
        
        if prediction:
            # Format response
            response = f"""📊 **{prediction['symbol']} - {prediction['company']}**

**Current Status:**
• Price: {prediction['currency']} ${prediction['current_price']}
• Trend: {prediction['trend']}
• RSI: {prediction['rsi']}
• 30-Day Return: {prediction['returns_30d']:+.1f}%
• Volatility: {prediction['volatility']:.1f}%

**Predictions:**"""
            
            for pred in prediction['predictions']:
                response += f"""
**Month {pred['month']}:**
• Target: ${pred['target']} ({pred['return']:+.1f}%)
• Range: ${pred['low']} - ${pred['high']}"""
            
            return jsonify({
                'status': 'success',
                'response': response,
                'type': 'prediction'
            })
    
    # Default response
    return jsonify({
        'status': 'success',
        'response': """I can analyze any stock for you!

**Try asking:**
• "Show me prediction for CBA" (Commonwealth Bank)
• "Analyze BHP for 3 months"
• "Forecast Apple stock"

**Australian stocks supported:**
CBA, BHP, CSL, NAB, WBC, ANZ, WOW, WES, RIO, FMG, TLS, MQG

Just type a company name or stock symbol!""",
        'type': 'help'
    })

def main():
    print("\n" + "="*60)
    print("🚀 YAHOO FINANCE OPTIMIZED SERVER")
    print("="*60)
    print("✅ Yahoo Finance: PRIMARY source")
    print("✅ Australian Stocks: FULLY supported (.AX)")
    print("✅ Auto-detection: CBA → CBA.AX")
    print("❌ Alpha Vantage: DISABLED (not needed)")
    print("="*60)
    print("\n📊 Open: http://localhost:8000")
    print("\n📈 Australian Stocks:")
    print("   CBA.AX - Commonwealth Bank")
    print("   BHP.AX - BHP Group")
    print("   CSL.AX - CSL Limited")
    print("   WBC.AX - Westpac")
    print("   ANZ.AX - ANZ Bank")
    print("\n🌍 International Markets:")
    print("   US: AAPL, MSFT, GOOGL")
    print("   UK: BP.L, HSBA.L")
    print("   More: .DE, .HK, .T, .TO\n")
    
    app.run(host='127.0.0.1', port=8000, debug=False, use_reloader=False)

if __name__ == '__main__':
    main()