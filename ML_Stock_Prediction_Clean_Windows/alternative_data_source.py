#!/usr/bin/env python3
"""
Use alternative data sources when Yahoo Finance is blocked
This uses REAL data from other sources, not simulated
"""

import pandas as pd
import requests
from datetime import datetime, timedelta

def get_data_from_alphavantage(symbol, api_key):
    """
    Get REAL data from Alpha Vantage
    Free API key from: https://www.alphavantage.co/support/#api-key
    """
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}&outputsize=full'
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if 'Time Series (Daily)' in data:
            ts = data['Time Series (Daily)']
            df = pd.DataFrame.from_dict(ts, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            # Rename columns to match yfinance format
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            # Convert to numeric
            for col in df.columns:
                df[col] = pd.to_numeric(df[col])
            
            return df
        else:
            print(f"Error: {data.get('Error Message', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"Error fetching from Alpha Vantage: {e}")
        return None

def get_data_from_twelvedata(symbol, api_key):
    """
    Get REAL data from Twelve Data
    Free API key from: https://twelvedata.com/
    """
    url = f'https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=200&apikey={api_key}'
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if 'values' in data:
            df = pd.DataFrame(data['values'])
            df['datetime'] = pd.to_datetime(df['datetime'])
            df.set_index('datetime', inplace=True)
            df = df.sort_index()
            
            # Rename and convert
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in df.columns:
                df[col] = pd.to_numeric(df[col])
            
            return df
        else:
            print(f"Error: {data.get('message', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"Error fetching from Twelve Data: {e}")
        return None

def get_data_from_iex(symbol, token):
    """
    Get REAL data from IEX Cloud
    Free token from: https://iexcloud.io/
    """
    base_url = 'https://cloud.iexapis.com/stable'
    url = f'{base_url}/stock/{symbol}/chart/6m?token={token}'
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if isinstance(data, list):
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # Select and rename columns
            df = df[['open', 'high', 'low', 'close', 'volume']]
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            return df
        else:
            print(f"Error from IEX: {data}")
            return None
            
    except Exception as e:
        print(f"Error fetching from IEX: {e}")
        return None

def setup_alternative_source():
    """Guide user to set up alternative data source"""
    
    print("=" * 60)
    print("Setting Up Alternative REAL Data Source")
    print("=" * 60)
    print()
    print("Since Yahoo Finance is blocked, you can use these")
    print("FREE alternatives that provide REAL stock data:")
    print()
    print("1. Alpha Vantage (Recommended)")
    print("   - Sign up: https://www.alphavantage.co/support/#api-key")
    print("   - Completely FREE")
    print("   - 500 requests/day")
    print()
    print("2. Twelve Data")
    print("   - Sign up: https://twelvedata.com/")
    print("   - Free tier: 800 requests/day")
    print()
    print("3. IEX Cloud")
    print("   - Sign up: https://iexcloud.io/")
    print("   - Free tier: 50,000 messages/month")
    print()
    print("4. Polygon.io")
    print("   - Sign up: https://polygon.io/")
    print("   - Free tier available")
    print()
    
    choice = input("Which service would you like to use? (1-4): ")
    
    if choice == '1':
        print("\nAlpha Vantage Setup:")
        print("1. Go to: https://www.alphavantage.co/support/#api-key")
        print("2. Enter your email")
        print("3. Copy the API key")
        api_key = input("4. Paste your API key here: ")
        
        # Save to config
        with open('api_config.py', 'w') as f:
            f.write(f"DATA_SOURCE = 'alphavantage'\n")
            f.write(f"API_KEY = '{api_key}'\n")
        
        print("\n✅ Configuration saved!")
        print("Testing connection...")
        
        df = get_data_from_alphavantage('AAPL', api_key)
        if df is not None:
            print(f"✅ SUCCESS! Got {len(df)} days of REAL AAPL data")
            print(f"Latest close: ${df['Close'].iloc[-1]:.2f}")
        else:
            print("❌ Connection failed. Check your API key.")
    
    # Similar for other services...

if __name__ == "__main__":
    setup_alternative_source()