#!/usr/bin/env python3
"""
Stock Analysis System - With Offline Data Fallback
Uses real data when available, falls back to offline CSV files
"""

import os
import pandas as pd
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import json
from datetime import datetime

# Import the original app
from app import MLPredictor, RealDataFetcher, app as original_app

class OfflineDataFetcher(RealDataFetcher):
    """Extended fetcher with offline data support"""
    
    def fetch_offline_data(self, symbol: str, period: str = '1mo') -> tuple:
        """Load data from offline CSV files"""
        try:
            # Check for offline data directory
            data_dir = 'offline_data'
            if not os.path.exists(data_dir):
                print(f"No offline data directory found")
                return None, None, None
            
            # Construct filename
            filename = f"{data_dir}/{symbol}_{period}.csv"
            
            if not os.path.exists(filename):
                # Try without .AX for Australian stocks
                if symbol.endswith('.AX'):
                    filename = f"{data_dir}/{symbol}_{period}.csv"
                    if not os.path.exists(filename):
                        print(f"No offline data for {symbol} {period}")
                        return None, None, None
            
            # Load CSV
            df = pd.read_csv(filename, index_col='Date', parse_dates=True)
            
            if not df.empty:
                print(f"Loaded offline data: {filename} ({len(df)} points)")
                current_price = float(df['Close'].iloc[-1])
                return df, "Offline Data (CSV)", current_price
                
        except Exception as e:
            print(f"Error loading offline data: {str(e)}")
        
        return None, None, None
    
    def fetch_data(self, symbol: str, period: str = '1mo') -> tuple:
        """Fetch data with offline fallback"""
        
        # Try real data sources first
        df, source, price = super().fetch_data(symbol, period)
        if df is not None and not df.empty:
            return df, source, price
        
        # Try offline data
        print(f"Attempting to load offline data for {symbol}")
        df, source, price = self.fetch_offline_data(symbol, period)
        if df is not None and not df.empty:
            return df, source, price
        
        # No data available
        return None, None, None

# Create new app with offline support
app = Flask(__name__)
CORS(app)

# Use extended data fetcher
data_fetcher = OfflineDataFetcher()
ml_predictor = MLPredictor()

# Copy all routes from original app
for rule in original_app.url_map.iter_rules():
    endpoint = rule.endpoint
    if endpoint and endpoint != 'static':
        view_func = original_app.view_functions[endpoint]
        app.add_url_rule(
            rule.rule,
            endpoint=endpoint,
            view_func=view_func,
            methods=rule.methods
        )

@app.route('/api/status')
def api_status():
    """Check data source availability"""
    sources = {
        'yahoo_finance': False,
        'alpha_vantage': False,
        'offline_data': False
    }
    
    # Check offline data
    if os.path.exists('offline_data'):
        csv_files = [f for f in os.listdir('offline_data') if f.endswith('.csv')]
        sources['offline_data'] = len(csv_files) > 0
    
    return jsonify({
        'status': 'running',
        'data_sources': sources,
        'message': 'Using offline data' if sources['offline_data'] else 'No data sources available'
    })

if __name__ == '__main__':
    print("=" * 70)
    print("STOCK ANALYSIS SYSTEM - WITH OFFLINE FALLBACK")
    print("=" * 70)
    print("Features:")
    print("✅ Real data from Yahoo/Alpha Vantage when available")
    print("✅ Offline CSV data fallback")
    print("✅ Machine Learning predictions")
    print("✅ Technical indicators")
    print("=" * 70)
    
    # Check for offline data
    if os.path.exists('offline_data'):
        csv_files = [f for f in os.listdir('offline_data') if f.endswith('.csv')]
        print(f"Offline data available: {len(csv_files)} files")
    else:
        print("No offline data found. Run 'python offline_data.py' to create sample data.")
    
    print("=" * 70)
    print("Starting server at: http://localhost:8000")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=8000, debug=False)