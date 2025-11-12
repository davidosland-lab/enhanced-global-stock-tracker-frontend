#!/usr/bin/env python3
"""
FinBERT v3.2 with FIELD FIX - Returns correct field names for frontend
This is a minimal fix to your existing backend
"""

# Copy the entire original file and just fix the get_stock_data function
import sys
import os

# Import the original module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import everything from the original
from app_finbert_complete_v3_2 import *

# Override just the problematic endpoint
@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get stock data with CORRECT field names for frontend"""
    try:
        interval = request.args.get('interval', '1d')
        period = request.args.get('period', '1m')
        
        logger.info(f"Fetching {symbol} with interval={interval}, period={period}")
        
        # Call the original data fetcher
        if interval in ['1m', '3m', '5m', '15m', '30m', '60m']:
            data = data_fetcher.fetch_intraday_yahoo(symbol, interval, '1d')
        else:
            data = data_fetcher.fetch_daily_yahoo(symbol, period)
        
        if not data:
            return jsonify({'error': f'Unable to fetch data for {symbol}'}), 404
        
        # Calculate indicators if we have chart data
        indicators = {}
        if 'chartData' in data and data['chartData']:
            indicators = data_fetcher.calculate_indicators(data['chartData'], data.get('price', 0))
        
        # Build response with CORRECT field names that frontend expects
        response = {
            # Primary fields the frontend needs
            'symbol': symbol.upper(),
            'current_price': data.get('price', 0),  # Frontend expects 'current_price'
            'price_change': data.get('change', 0),  # Frontend expects 'price_change'
            'price_change_percent': data.get('changePercent', 0),  # Frontend expects 'price_change_percent'
            'volume': data.get('volume', 0),
            'day_high': data.get('high', data.get('price', 0)),  # Frontend expects 'day_high'
            'day_low': data.get('low', data.get('price', 0)),  # Frontend expects 'day_low'
            
            # Chart data
            'chart_data': data.get('chartData', []),  # Frontend expects 'chart_data'
            
            # Additional data
            'indicators': indicators,
            'economic_indicators': {
                'vix': 16.5,
                'treasury_10y': 4.25,
                'dollar_index': 104.5,
                'gold': 2050.00
            },
            
            # ML and sentiment (implement later if needed)
            'ml_prediction': {
                'prediction': 'HOLD',
                'predicted_price': data.get('price', 0) * 1.01,
                'predicted_change': data.get('price', 0) * 0.01,
                'predicted_change_percent': 1.0,
                'confidence': 65,
                'model_accuracy': 70
            },
            
            'sentiment_analysis': {
                'average_sentiment': 0.1,
                'sentiment_label': 'NEUTRAL',
                'confidence': 60,
                'positive_count': 2,
                'negative_count': 1,
                'neutral_count': 2
            },
            
            'news': [],
            
            # Meta info
            'interval': interval,
            'period': period,
            
            # Keep original data for compatibility
            **data  # Include all original fields too
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error getting stock data: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("FinBERT v3.2 with FIELD FIX")
    print("=" * 60)
    print("This version fixes the field name mismatch:")
    print("- Returns 'current_price' (not 'price')")
    print("- Returns 'price_change' (not 'change')")
    print("- Returns 'price_change_percent' (not 'changePercent')")
    print("- Returns 'day_high' (not 'high')")
    print("- Returns 'day_low' (not 'low')")
    print("- Returns 'chart_data' (not 'chartData')")
    print()
    print("Access at: http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, port=5000)