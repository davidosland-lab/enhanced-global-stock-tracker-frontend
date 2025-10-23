#!/usr/bin/env python3
"""
Example of using mplfinance for candlestick chart generation
Inspired by matplotlib/mplfinance repository
"""

import yfinance as yf
import mplfinance as mpf
import pandas as pd
from datetime import datetime, timedelta
import json
import base64
from io import BytesIO

def fetch_ohlc_data(symbol, period="1mo", interval="1d"):
    """
    Fetch OHLC data from Yahoo Finance
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'CBA.AX')
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    
    Returns:
        DataFrame with OHLC data
    """
    ticker = yf.Ticker(symbol)
    data = ticker.history(period=period, interval=interval)
    return data

def create_candlestick_chart(data, symbol, style='charles', volume=True, mav=(10, 20, 50)):
    """
    Create candlestick chart using mplfinance
    
    Args:
        data: OHLC DataFrame
        symbol: Stock symbol for title
        style: mplfinance style ('charles', 'mike', 'nightclouds', 'sas', 'yahoo')
        volume: Show volume subplot
        mav: Moving averages to plot (tuple of periods)
    
    Returns:
        Base64 encoded image or saves to file
    """
    # Create custom style inspired by mplfinance defaults
    custom_style = mpf.make_mpf_style(
        base_mpf_style=style,
        gridcolor='#e0e0e0',
        gridstyle='-',
        y_on_right=True,
        marketcolors=mpf.make_marketcolors(
            up='#26a69a',      # Green for up days
            down='#ef5350',    # Red for down days
            edge='inherit',
            wick={'up':'#26a69a', 'down':'#ef5350'},
            volume='inherit',
            alpha=0.9
        )
    )
    
    # Create the plot
    fig, axes = mpf.plot(
        data,
        type='candle',
        style=custom_style,
        title=f'{symbol} - Candlestick Chart',
        ylabel='Price ($)',
        volume=volume,
        mav=mav,
        returnfig=True,
        figsize=(12, 8),
        tight_layout=True
    )
    
    # Save to BytesIO for base64 encoding
    buffer = BytesIO()
    fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    
    return image_base64

def generate_technical_indicators(data):
    """
    Generate technical indicators from OHLC data
    
    Args:
        data: OHLC DataFrame
    
    Returns:
        Dictionary with technical indicators
    """
    indicators = {}
    
    # Simple Moving Averages
    indicators['SMA_10'] = data['Close'].rolling(window=10).mean().iloc[-1]
    indicators['SMA_20'] = data['Close'].rolling(window=20).mean().iloc[-1]
    indicators['SMA_50'] = data['Close'].rolling(window=50).mean().iloc[-1] if len(data) >= 50 else None
    
    # Exponential Moving Averages
    indicators['EMA_12'] = data['Close'].ewm(span=12, adjust=False).mean().iloc[-1]
    indicators['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean().iloc[-1]
    
    # RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    indicators['RSI'] = (100 - (100 / (1 + rs))).iloc[-1]
    
    # MACD
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    indicators['MACD'] = macd.iloc[-1]
    indicators['MACD_signal'] = macd.ewm(span=9, adjust=False).mean().iloc[-1]
    
    # Bollinger Bands
    sma20 = data['Close'].rolling(window=20).mean()
    std20 = data['Close'].rolling(window=20).std()
    indicators['BB_upper'] = (sma20 + (std20 * 2)).iloc[-1]
    indicators['BB_middle'] = sma20.iloc[-1]
    indicators['BB_lower'] = (sma20 - (std20 * 2)).iloc[-1]
    
    # Support and Resistance
    indicators['support'] = data['Low'].rolling(window=20).min().iloc[-1]
    indicators['resistance'] = data['High'].rolling(window=20).max().iloc[-1]
    
    return indicators

def analyze_patterns(data):
    """
    Analyze candlestick patterns in OHLC data
    
    Args:
        data: OHLC DataFrame
    
    Returns:
        List of detected patterns
    """
    patterns = []
    
    # Get last few candles for pattern detection
    if len(data) >= 3:
        last_3 = data.tail(3)
        opens = last_3['Open'].values
        closes = last_3['Close'].values
        highs = last_3['High'].values
        lows = last_3['Low'].values
        
        # Doji pattern (open ≈ close)
        if abs(closes[-1] - opens[-1]) < (highs[-1] - lows[-1]) * 0.1:
            patterns.append({
                'name': 'Doji',
                'type': 'neutral',
                'description': 'Indecision in the market'
            })
        
        # Hammer pattern
        body = abs(closes[-1] - opens[-1])
        lower_shadow = min(opens[-1], closes[-1]) - lows[-1]
        upper_shadow = highs[-1] - max(opens[-1], closes[-1])
        if lower_shadow > body * 2 and upper_shadow < body * 0.5:
            patterns.append({
                'name': 'Hammer',
                'type': 'bullish',
                'description': 'Potential reversal to upside'
            })
        
        # Shooting star pattern
        if upper_shadow > body * 2 and lower_shadow < body * 0.5:
            patterns.append({
                'name': 'Shooting Star',
                'type': 'bearish',
                'description': 'Potential reversal to downside'
            })
        
        # Engulfing pattern
        if len(data) >= 2:
            if closes[-1] > opens[-1] and closes[-2] < opens[-2]:  # Bullish engulfing
                if opens[-1] < closes[-2] and closes[-1] > opens[-2]:
                    patterns.append({
                        'name': 'Bullish Engulfing',
                        'type': 'bullish',
                        'description': 'Strong bullish reversal signal'
                    })
            elif closes[-1] < opens[-1] and closes[-2] > opens[-2]:  # Bearish engulfing
                if opens[-1] > closes[-2] and closes[-1] < opens[-2]:
                    patterns.append({
                        'name': 'Bearish Engulfing',
                        'type': 'bearish',
                        'description': 'Strong bearish reversal signal'
                    })
    
    return patterns

def main():
    """
    Example usage of mplfinance-inspired analysis
    """
    # Example: Analyze CBA.AX
    symbol = 'CBA.AX'
    
    print(f"Fetching data for {symbol}...")
    data = fetch_ohlc_data(symbol, period='3mo', interval='1d')
    
    print("\nGenerating candlestick chart...")
    chart_base64 = create_candlestick_chart(data, symbol)
    print(f"Chart generated (base64 length: {len(chart_base64)})")
    
    print("\nCalculating technical indicators...")
    indicators = generate_technical_indicators(data)
    for key, value in indicators.items():
        if value is not None:
            print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")
    
    print("\nDetecting candlestick patterns...")
    patterns = analyze_patterns(data)
    for pattern in patterns:
        print(f"  - {pattern['name']} ({pattern['type']}): {pattern['description']}")
    
    # Convert data to JSON format for frontend
    ohlc_json = []
    for index, row in data.tail(30).iterrows():
        ohlc_json.append({
            'date': index.isoformat(),
            'open': row['Open'],
            'high': row['High'],
            'low': row['Low'],
            'close': row['Close'],
            'volume': row['Volume']
        })
    
    result = {
        'symbol': symbol,
        'ohlc_data': ohlc_json,
        'indicators': indicators,
        'patterns': patterns,
        'chart': f"data:image/png;base64,{chart_base64}"
    }
    
    # Save result to file
    with open('analysis_result.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print("\nAnalysis complete! Results saved to analysis_result.json")
    return result

if __name__ == "__main__":
    # Note: Requires installation of:
    # pip install mplfinance yfinance pandas
    print("=== mplfinance-inspired Technical Analysis ===")
    print("This demonstrates how to use mplfinance for backend chart generation")
    print("and technical analysis similar to the matplotlib/mplfinance repository\n")
    
    try:
        main()
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("\nTo use this script, install required packages:")
        print("pip install mplfinance yfinance pandas matplotlib")
    except Exception as e:
        print(f"Error: {e}")