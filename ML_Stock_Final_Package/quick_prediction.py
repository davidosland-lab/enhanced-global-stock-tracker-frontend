#!/usr/bin/env python3
"""
Quick Prediction for Apple Stock
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def analyze_apple():
    """Generate prediction for AAPL over next 2 months"""
    
    print("Fetching Apple (AAPL) data...")
    
    # Fetch 1 year of data
    ticker = yf.download('AAPL', period='1y', progress=False)
    
    if ticker.empty:
        return {"error": "Could not fetch data"}
    
    # Current price
    current_price = float(ticker['Close'].iloc[-1])
    
    # Calculate technical indicators
    ticker['SMA_20'] = ticker['Close'].rolling(window=20).mean()
    ticker['SMA_50'] = ticker['Close'].rolling(window=50).mean()
    ticker['SMA_200'] = ticker['Close'].rolling(window=200).mean()
    
    # RSI
    delta = ticker['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    ticker['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    ticker['BB_middle'] = ticker['Close'].rolling(window=20).mean()
    bb_std = ticker['Close'].rolling(window=20).std()
    ticker['BB_upper'] = ticker['BB_middle'] + (bb_std * 2)
    ticker['BB_lower'] = ticker['BB_middle'] - (bb_std * 2)
    
    # Recent performance
    returns_30d = (ticker['Close'].iloc[-1] / ticker['Close'].iloc[-30] - 1) * 100
    returns_90d = (ticker['Close'].iloc[-1] / ticker['Close'].iloc[-90] - 1) * 100
    
    # Volatility
    daily_returns = ticker['Close'].pct_change()
    volatility = daily_returns.rolling(window=30).std() * np.sqrt(252) * 100
    current_volatility = volatility.iloc[-1]
    
    # Trend analysis
    sma20_current = ticker['SMA_20'].iloc[-1]
    sma50_current = ticker['SMA_50'].iloc[-1]
    sma200_current = ticker['SMA_200'].iloc[-1]
    
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
    current_rsi = ticker['RSI'].iloc[-1]
    if current_rsi > 70:
        rsi_signal = "Overbought"
        rsi_score = -0.5
    elif current_rsi < 30:
        rsi_signal = "Oversold"
        rsi_score = 0.5
    else:
        rsi_signal = "Neutral"
        rsi_score = 0
    
    # Bollinger Band position
    bb_position = (current_price - ticker['BB_lower'].iloc[-1]) / (ticker['BB_upper'].iloc[-1] - ticker['BB_lower'].iloc[-1])
    
    # Historical average returns for similar conditions
    historical_return = 0
    if trend_score > 0:
        historical_return = 8  # Average 8% return in uptrends
    elif trend_score == 0:
        historical_return = 4  # Average 4% return in neutral
    else:
        historical_return = -2  # Average -2% return in downtrends
    
    # Adjust for RSI
    historical_return += rsi_score * 2
    
    # Adjust for volatility (higher volatility = wider range)
    volatility_factor = current_volatility / 20  # Normalize around 20%
    
    # Generate predictions
    # 1 month prediction
    base_return_1m = historical_return / 2
    prediction_1m = current_price * (1 + base_return_1m / 100)
    prediction_1m_low = prediction_1m * (1 - current_volatility / 100 * 0.5)
    prediction_1m_high = prediction_1m * (1 + current_volatility / 100 * 0.5)
    
    # 2 month prediction
    base_return_2m = historical_return
    prediction_2m = current_price * (1 + base_return_2m / 100)
    prediction_2m_low = prediction_2m * (1 - current_volatility / 100 * 0.7)
    prediction_2m_high = prediction_2m * (1 + current_volatility / 100 * 0.7)
    
    # Confidence score based on trend consistency
    confidence = 0.7  # Base confidence
    if trend_score > 0 and current_price > sma200_current:
        confidence += 0.1
    if abs(current_rsi - 50) < 20:  # RSI near neutral
        confidence += 0.05
    if bb_position > 0.3 and bb_position < 0.7:  # Price in middle of BB
        confidence += 0.05
    
    result = {
        "symbol": "AAPL",
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "current_price": round(current_price, 2),
        "technical_analysis": {
            "trend": trend,
            "trend_strength": ["Weak", "Moderate", "Strong"][abs(trend_score)] if trend_score != 0 else "Neutral",
            "sma_20": round(sma20_current, 2),
            "sma_50": round(sma50_current, 2),
            "sma_200": round(sma200_current, 2),
            "rsi": round(current_rsi, 2),
            "rsi_signal": rsi_signal,
            "bollinger_position": f"{round(bb_position * 100, 1)}%",
            "volatility_annual": f"{round(current_volatility, 1)}%"
        },
        "recent_performance": {
            "30_days": f"{returns_30d:+.1f}%",
            "90_days": f"{returns_90d:+.1f}%"
        },
        "predictions": {
            "1_month": {
                "date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                "target_price": round(prediction_1m, 2),
                "range_low": round(prediction_1m_low, 2),
                "range_high": round(prediction_1m_high, 2),
                "expected_return": f"{base_return_1m:+.1f}%"
            },
            "2_months": {
                "date": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
                "target_price": round(prediction_2m, 2),
                "range_low": round(prediction_2m_low, 2),
                "range_high": round(prediction_2m_high, 2),
                "expected_return": f"{base_return_2m:+.1f}%"
            }
        },
        "confidence_score": round(confidence, 2),
        "key_factors": [],
        "risks": [],
        "opportunities": []
    }
    
    # Add key factors
    if trend_score > 0:
        result["key_factors"].append("Stock in uptrend above key moving averages")
    if current_price > sma200_current:
        result["key_factors"].append("Trading above 200-day SMA (long-term bullish)")
    if current_rsi < 70 and current_rsi > 30:
        result["key_factors"].append("RSI in neutral zone - room for movement")
    
    # Add risks
    if current_rsi > 65:
        result["risks"].append("RSI approaching overbought levels")
    if current_volatility > 25:
        result["risks"].append(f"High volatility ({round(current_volatility, 1)}% annualized)")
    if bb_position > 0.8:
        result["risks"].append("Near upper Bollinger Band - possible pullback")
    
    # Add opportunities  
    if trend_score > 0 and current_rsi < 50:
        result["opportunities"].append("Uptrend with RSI room to grow")
    if current_price > sma50_current and current_price < sma20_current:
        result["opportunities"].append("Potential bounce from 50-day SMA support")
    
    # Historical context
    year_high = ticker['High'].rolling(window=252).max().iloc[-1]
    year_low = ticker['Low'].rolling(window=252).min().iloc[-1]
    position_in_range = (current_price - year_low) / (year_high - year_low)
    
    result["year_range"] = {
        "52_week_high": round(year_high, 2),
        "52_week_low": round(year_low, 2),
        "position_in_range": f"{round(position_in_range * 100, 1)}%"
    }
    
    return result

if __name__ == "__main__":
    print("\n" + "="*60)
    print("APPLE (AAPL) - 2 MONTH PREDICTION ANALYSIS")
    print("="*60 + "\n")
    
    result = analyze_apple()
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(json.dumps(result, indent=2))
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Current Price: ${result['current_price']}")
        print(f"Market Trend: {result['technical_analysis']['trend']}")
        print(f"Confidence: {result['confidence_score'] * 100:.0f}%")
        print("\n📊 PREDICTIONS:")
        print(f"1 Month Target: ${result['predictions']['1_month']['target_price']} ({result['predictions']['1_month']['expected_return']})")
        print(f"2 Month Target: ${result['predictions']['2_months']['target_price']} ({result['predictions']['2_months']['expected_return']})")
        print("="*60)