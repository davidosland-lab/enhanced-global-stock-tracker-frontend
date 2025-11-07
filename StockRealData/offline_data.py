#!/usr/bin/env python3
"""
Offline Data Generator - Creates sample CSV files for testing when APIs are blocked
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def create_sample_data(symbol, days=30):
    """Create realistic sample stock data"""
    
    # Base prices for different symbols
    base_prices = {
        'AAPL': 175.0,
        'GOOGL': 140.0,
        'MSFT': 380.0,
        'TSLA': 250.0,
        'AMZN': 145.0,
        'CBA.AX': 115.0,
        'BHP.AX': 45.0
    }
    
    base_price = base_prices.get(symbol, 100.0)
    
    # Generate dates
    end_date = datetime.now()
    dates = pd.date_range(end=end_date, periods=days, freq='D')
    
    # Generate realistic price movements
    returns = np.random.normal(0.001, 0.02, days)  # Daily returns
    price_series = base_price * np.exp(np.cumsum(returns))
    
    # Create OHLCV data
    data = []
    for i, (date, close_price) in enumerate(zip(dates, price_series)):
        # Skip weekends
        if date.weekday() >= 5:
            continue
            
        daily_volatility = np.random.uniform(0.005, 0.02)
        
        open_price = close_price * (1 + np.random.uniform(-daily_volatility, daily_volatility))
        high_price = max(open_price, close_price) * (1 + np.random.uniform(0, daily_volatility))
        low_price = min(open_price, close_price) * (1 - np.random.uniform(0, daily_volatility))
        volume = int(np.random.uniform(10_000_000, 50_000_000))
        
        data.append({
            'Date': date,
            'Open': round(open_price, 2),
            'High': round(high_price, 2),
            'Low': round(low_price, 2),
            'Close': round(close_price, 2),
            'Volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    return df

def save_sample_data():
    """Save sample data for multiple symbols"""
    
    # Create data directory
    data_dir = 'offline_data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'CBA.AX', 'BHP.AX']
    
    print("Creating offline sample data...")
    print("="*50)
    
    for symbol in symbols:
        # Create data for different periods
        periods = {
            '1d': 1,
            '5d': 5,
            '1mo': 30,
            '3mo': 90,
            '6mo': 180,
            '1y': 365
        }
        
        for period_name, days in periods.items():
            df = create_sample_data(symbol, days)
            filename = f"{data_dir}/{symbol}_{period_name}.csv"
            df.to_csv(filename)
            print(f"Created: {filename} ({len(df)} data points)")
    
    print("="*50)
    print(f"Sample data created in '{data_dir}' directory")
    print("\nThis data can be used for testing when APIs are unavailable.")
    
    # Create a README
    readme_content = """
OFFLINE DATA FILES
==================

These CSV files contain sample stock data for testing purposes.
Use when Yahoo Finance and Alpha Vantage APIs are blocked.

Files Format:
- {SYMBOL}_{PERIOD}.csv
- Example: AAPL_1mo.csv (Apple stock, 1 month data)

Periods Available:
- 1d: 1 day
- 5d: 5 days  
- 1mo: 1 month
- 3mo: 3 months
- 6mo: 6 months
- 1y: 1 year

To use:
1. Modify app.py to load from CSV when APIs fail
2. Or import directly in Python:
   import pandas as pd
   df = pd.read_csv('offline_data/AAPL_1mo.csv', index_col='Date', parse_dates=True)
"""
    
    with open(f'{data_dir}/README.txt', 'w') as f:
        f.write(readme_content)

if __name__ == "__main__":
    save_sample_data()
    input("\nPress Enter to exit...")