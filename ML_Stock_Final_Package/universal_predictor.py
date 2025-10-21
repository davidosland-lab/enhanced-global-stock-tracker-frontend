#!/usr/bin/env python3
"""
Universal Stock Predictor - Works with any symbol including Australian stocks
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sys

def analyze_stock(symbol, months=2):
    """Generate prediction for any stock symbol"""
    
    print(f"Fetching {symbol} data...")
    
    # Try standard symbol first
    data = yf.download(symbol, period='1y', progress=False, auto_adjust=True)
    
    # If no data and symbol doesn't have a suffix, try Australian .AX
    if data.empty and '.' not in symbol:
        aus_symbols = ['CBA', 'BHP', 'CSL', 'NAB', 'WBC', 'ANZ', 'WES', 'WOW', 'RIO', 'FMG', 
                      'TLS', 'MQG', 'GMG', 'TCL', 'ALL', 'REA', 'SHL', 'WDS', 'NCM', 'AMC']
        if symbol.upper() in aus_symbols:
            symbol = f"{symbol}.AX"
            print(f"Trying Australian symbol: {symbol}")
            data = yf.download(symbol, period='1y', progress=False, auto_adjust=True)
    
    if data.empty:
        # Try Alpha Vantage as backup
        print(f"Yahoo Finance failed, trying Alpha Vantage...")
        return try_alpha_vantage(symbol, months)
    
    # Get stock info
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        company_name = info.get('longName', symbol)
        currency = info.get('currency', 'USD')
    except:
        company_name = symbol
        currency = 'AUD' if '.AX' in symbol else 'USD'
    
    # Extract Close prices
    close_prices = data['Close'].squeeze() if len(data['Close'].shape) > 1 else data['Close']
    
    # Current price
    current_price = float(close_prices.iloc[-1])
    
    # Calculate technical indicators
    sma_20 = close_prices.rolling(window=20).mean()
    sma_50 = close_prices.rolling(window=50).mean()
    sma_200 = close_prices.rolling(window=200).mean()
    
    # RSI
    delta = close_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    bb_middle = close_prices.rolling(window=20).mean()
    bb_std = close_prices.rolling(window=20).std()
    bb_upper = bb_middle + (bb_std * 2)
    bb_lower = bb_middle - (bb_std * 2)
    
    # MACD
    ema_12 = close_prices.ewm(span=12, adjust=False).mean()
    ema_26 = close_prices.ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    macd_histogram = macd - macd_signal
    
    # Recent performance
    returns_30d = (close_prices.iloc[-1] / close_prices.iloc[-30] - 1) * 100 if len(close_prices) > 30 else 0
    returns_90d = (close_prices.iloc[-1] / close_prices.iloc[-90] - 1) * 100 if len(close_prices) > 90 else 0
    
    # Volatility
    daily_returns = close_prices.pct_change()
    volatility = daily_returns.rolling(window=30).std() * np.sqrt(252) * 100
    current_volatility = float(volatility.iloc[-1]) if not pd.isna(volatility.iloc[-1]) else 20
    
    # Trend analysis
    sma20_current = float(sma_20.iloc[-1]) if not pd.isna(sma_20.iloc[-1]) else current_price
    sma50_current = float(sma_50.iloc[-1]) if not pd.isna(sma_50.iloc[-1]) else current_price
    sma200_current = float(sma_200.iloc[-1]) if not pd.isna(sma_200.iloc[-1]) else sma50_current
    
    # Determine trend
    if current_price > sma20_current > sma50_current:
        trend = "Strong Uptrend"
        trend_score = 2
    elif current_price > sma50_current:
        trend = "Uptrend"
        trend_score = 1
    elif current_price < sma50_current and current_price > sma200_current:
        trend = "Neutral"
        trend_score = 0
    else:
        trend = "Downtrend"
        trend_score = -1
    
    # RSI analysis
    current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50
    if current_rsi > 70:
        rsi_signal = "Overbought"
        rsi_score = -0.5
    elif current_rsi < 30:
        rsi_signal = "Oversold"
        rsi_score = 0.5
    else:
        rsi_signal = "Neutral"
        rsi_score = 0
    
    # MACD analysis
    macd_current = float(macd_histogram.iloc[-1]) if not pd.isna(macd_histogram.iloc[-1]) else 0
    macd_trend = "Bullish" if macd_current > 0 else "Bearish"
    
    # Bollinger Band position
    bb_position = (current_price - float(bb_lower.iloc[-1])) / (float(bb_upper.iloc[-1]) - float(bb_lower.iloc[-1]))
    bb_position = max(0, min(1, bb_position))  # Clamp between 0 and 1
    
    # Base return calculation
    if trend_score > 0:
        base_return = 8  # Uptrend base
    elif trend_score == 0:
        base_return = 4  # Neutral base
    else:
        base_return = -2  # Downtrend base
    
    # Adjustments
    base_return += rsi_score * 2
    base_return += 1 if macd_current > 0 else -1
    
    # Australian market adjustment (typically more volatile)
    if '.AX' in symbol:
        base_return *= 1.2  # 20% adjustment for Australian stocks
    
    # Generate predictions for requested months
    predictions = {}
    for month in range(1, months + 1):
        return_rate = base_return * (month / 2)  # Scale by time
        pred_price = current_price * (1 + return_rate / 100)
        pred_low = pred_price * (1 - current_volatility / (200 / month))
        pred_high = pred_price * (1 + current_volatility / (200 / month))
        
        predictions[f"{month}_month"] = {
            "date": (datetime.now() + timedelta(days=30*month)).strftime("%Y-%m-%d"),
            "target_price": round(pred_price, 2),
            "range_low": round(pred_low, 2),
            "range_high": round(pred_high, 2),
            "expected_return": f"{return_rate:+.1f}%"
        }
    
    # Confidence calculation
    confidence = 0.7
    if trend_score > 0 and current_price > sma200_current:
        confidence += 0.1
    if 30 < current_rsi < 70:
        confidence += 0.05
    if 0.3 < bb_position < 0.7:
        confidence += 0.05
    
    # Support and resistance levels
    recent_high = float(data['High'].tail(20).max())
    recent_low = float(data['Low'].tail(20).min())
    
    # Year range
    year_high = float(data['High'].max())
    year_low = float(data['Low'].min())
    position_in_range = (current_price - year_low) / (year_high - year_low) if year_high != year_low else 0.5
    
    result = {
        "symbol": symbol,
        "company": company_name,
        "currency": currency,
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "current_price": round(current_price, 2),
        "technical_indicators": {
            "trend": trend,
            "trend_strength": ["Weak", "Moderate", "Strong"][min(abs(trend_score), 2)],
            "sma_20": round(sma20_current, 2),
            "sma_50": round(sma50_current, 2),
            "sma_200": round(sma200_current, 2),
            "rsi": round(current_rsi, 2),
            "rsi_signal": rsi_signal,
            "macd_trend": macd_trend,
            "bollinger_position": f"{round(bb_position * 100, 1)}%",
            "volatility_annual": f"{round(current_volatility, 1)}%"
        },
        "support_resistance": {
            "immediate_support": round(recent_low, 2),
            "immediate_resistance": round(recent_high, 2),
            "major_support": round(sma50_current, 2),
            "major_resistance": round(year_high, 2)
        },
        "performance": {
            "30_days": f"{returns_30d:+.1f}%",
            "90_days": f"{returns_90d:+.1f}%"
        },
        "predictions": predictions,
        "confidence_score": round(confidence, 2),
        "year_range": {
            "52_week_high": round(year_high, 2),
            "52_week_low": round(year_low, 2),
            "position": f"{round(position_in_range * 100, 1)}%"
        }
    }
    
    return result

def try_alpha_vantage(symbol, months=2):
    """Fallback to Alpha Vantage for Australian and international stocks"""
    try:
        import requests
        
        # Convert Australian symbols for Alpha Vantage
        av_symbol = symbol.replace('.AX', '.AUS') if '.AX' in symbol else symbol
        
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': av_symbol,
            'apikey': '68ZFANK047DL0KSR',
            'outputsize': 'full'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Time Series (Daily)' in data:
            time_series = data['Time Series (Daily)']
            dates = sorted(list(time_series.keys()))[-252:]  # Last year
            
            if len(dates) < 30:
                return {"error": f"Insufficient data for {symbol}"}
            
            # Extract prices
            prices = []
            for date in dates:
                prices.append(float(time_series[date]['4. close']))
            
            current_price = prices[-1]
            
            # Simple calculations
            returns_30d = (prices[-1] / prices[-30] - 1) * 100 if len(prices) > 30 else 0
            volatility = np.std([prices[i]/prices[i-1] - 1 for i in range(1, len(prices))]) * np.sqrt(252) * 100
            
            # Simple prediction
            avg_return = returns_30d / 30 * 30  # Monthly return estimate
            
            predictions = {}
            for month in range(1, months + 1):
                pred_return = avg_return * month * 0.7  # Conservative estimate
                pred_price = current_price * (1 + pred_return / 100)
                
                predictions[f"{month}_month"] = {
                    "date": (datetime.now() + timedelta(days=30*month)).strftime("%Y-%m-%d"),
                    "target_price": round(pred_price, 2),
                    "range_low": round(pred_price * 0.95, 2),
                    "range_high": round(pred_price * 1.05, 2),
                    "expected_return": f"{pred_return:+.1f}%"
                }
            
            return {
                "symbol": symbol,
                "source": "Alpha Vantage",
                "current_price": round(current_price, 2),
                "currency": "AUD" if '.AUS' in av_symbol else "USD",
                "performance": {
                    "30_days": f"{returns_30d:+.1f}%"
                },
                "predictions": predictions,
                "confidence_score": 0.65,
                "note": "Using Alpha Vantage data with simplified analysis"
            }
        else:
            if 'Information' in data:
                return {"error": "Alpha Vantage API limit reached. Please wait 1 minute."}
            return {"error": f"Could not fetch data for {symbol}"}
            
    except Exception as e:
        return {"error": f"Alpha Vantage error: {str(e)}"}

def format_analysis(result):
    """Format the analysis into readable text"""
    if "error" in result:
        return f"❌ Error: {result['error']}"
    
    symbol = result['symbol']
    price = result['current_price']
    currency = result.get('currency', 'USD')
    
    output = f"""
📊 **{symbol} PREDICTION ANALYSIS**

**Current Status:**
- Price: {currency}${price}
- Company: {result.get('company', symbol)}
- Data Source: {result.get('source', 'Yahoo Finance')}
"""
    
    if 'technical_indicators' in result:
        ti = result['technical_indicators']
        output += f"""
**Technical Analysis:**
- Trend: {ti['trend']} ({ti.get('trend_strength', 'Moderate')})
- RSI: {ti['rsi']} ({ti['rsi_signal']})
- MACD: {ti.get('macd_trend', 'N/A')}
- Volatility: {ti['volatility_annual']}
"""
    
    if 'performance' in result:
        perf = result['performance']
        output += f"""
**Recent Performance:**
- 30 Days: {perf.get('30_days', 'N/A')}
- 90 Days: {perf.get('90_days', 'N/A')}
"""
    
    output += "\n**PREDICTIONS:**\n"
    for period, pred in result['predictions'].items():
        output += f"""
📅 **{period.replace('_', ' ').title()} (by {pred['date']}):**
- Target: {currency}${pred['target_price']} ({pred['expected_return']})
- Range: {currency}${pred['range_low']} - {currency}${pred['range_high']}
"""
    
    confidence = result.get('confidence_score', 0.7)
    output += f"\n**Confidence Level:** {int(confidence * 100)}%"
    
    if 'support_resistance' in result:
        sr = result['support_resistance']
        output += f"""
**Key Levels:**
- Support: {currency}${sr['immediate_support']}
- Resistance: {currency}${sr['immediate_resistance']}
"""
    
    return output

if __name__ == "__main__":
    # Get symbol from command line or use default
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    months = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    print(f"\nAnalyzing {symbol}...")
    result = analyze_stock(symbol.upper(), months)
    
    print(format_analysis(result))
    
    if "error" not in result:
        print("\n" + "="*60)
        print("Note: This analysis uses technical indicators and historical patterns.")
        print("Always do your own research before making investment decisions.")
        print("="*60)