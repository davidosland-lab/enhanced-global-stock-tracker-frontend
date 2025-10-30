#!/usr/bin/env python3
"""
Patch to add estimated price and timeframe to predictions
This modifies the predict() method in TradingModel class
"""

# Add this code to the predict() method in app_finbert_ultimate.py
# Right after line where current_price is set (around line 840)

def calculate_price_target(current_price, prediction, confidence, feature_importances, df):
    """
    Calculate estimated price target and timeframe based on:
    - Historical volatility
    - Prediction confidence
    - Technical indicators
    - Recent price movements
    """
    import numpy as np
    
    # Calculate historical volatility (20-day)
    returns = df['Close'].pct_change().dropna()
    volatility = returns.tail(20).std() if len(returns) >= 20 else returns.std()
    
    # Calculate average true range (ATR) for better volatility estimate
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.tail(14).mean() if len(true_range) >= 14 else true_range.mean()
    atr_percent = (atr / current_price) * 100
    
    # Calculate recent momentum
    if len(df) >= 20:
        sma_20 = df['Close'].tail(20).mean()
        momentum = (current_price - sma_20) / sma_20
    else:
        momentum = 0
    
    # Base price movement calculation
    # Use combination of volatility and ATR for more accurate estimation
    base_movement = (volatility * 2 + atr_percent / 100) / 2
    
    # Adjust based on confidence
    confidence_multiplier = 0.5 + (confidence * 0.5)  # Range: 0.5 to 1.0
    
    # Adjust based on momentum
    momentum_adjustment = 1 + (momentum * 0.2)  # Slight adjustment based on trend
    
    # Calculate price movement
    price_movement_percent = base_movement * confidence_multiplier * momentum_adjustment * 100
    
    # Apply direction
    if prediction == 1:  # UP
        estimated_price = current_price * (1 + price_movement_percent / 100)
        price_range_low = current_price * (1 + price_movement_percent * 0.3 / 100)
        price_range_high = current_price * (1 + price_movement_percent * 1.5 / 100)
    else:  # DOWN
        estimated_price = current_price * (1 - price_movement_percent / 100)
        price_range_high = current_price * (1 - price_movement_percent * 0.3 / 100)
        price_range_low = current_price * (1 - price_movement_percent * 1.5 / 100)
    
    # Calculate timeframe based on volatility and movement size
    # Higher volatility = shorter timeframe
    # Larger movement = longer timeframe
    if volatility > 0.03:  # High volatility
        timeframe_days = 5
        timeframe_text = "5 trading days"
    elif volatility > 0.02:  # Medium volatility
        timeframe_days = 10
        timeframe_text = "2 weeks"
    elif volatility > 0.01:  # Low volatility
        timeframe_days = 20
        timeframe_text = "1 month"
    else:  # Very low volatility
        timeframe_days = 30
        timeframe_text = "1-2 months"
    
    # Adjust timeframe based on movement size
    if abs(price_movement_percent) > 10:
        timeframe_days = int(timeframe_days * 1.5)
        if timeframe_days <= 7:
            timeframe_text = "1 week"
        elif timeframe_days <= 14:
            timeframe_text = "2 weeks"
        elif timeframe_days <= 30:
            timeframe_text = "1 month"
        else:
            timeframe_text = "1-2 months"
    
    return {
        'estimated_price': round(estimated_price, 2),
        'price_range_low': round(price_range_low, 2),
        'price_range_high': round(price_range_high, 2),
        'price_change_percent': round(price_movement_percent, 2),
        'timeframe_days': timeframe_days,
        'timeframe_text': timeframe_text,
        'volatility': round(volatility * 100, 2),  # As percentage
        'atr': round(atr, 2),
        'momentum': round(momentum * 100, 2)  # As percentage
    }

# Example of how to integrate into existing predict() method:
"""
# Add this after getting current_price (around line 840):

# Calculate price target and timeframe
price_target_info = calculate_price_target(
    current_price, 
    prediction, 
    float(max(probabilities)),
    model.feature_importances_,
    df
)

# Add to result dictionary:
result = {
    "symbol": symbol,
    "prediction": "UP" if prediction == 1 else "DOWN",
    "confidence": float(max(probabilities)),
    "probabilities": {
        "up": float(probabilities[1]) if len(probabilities) > 1 else 0.5,
        "down": float(probabilities[0]) if len(probabilities) > 0 else 0.5
    },
    "current_price": current_price,
    "estimated_price": price_target_info['estimated_price'],
    "price_range": {
        "low": price_target_info['price_range_low'],
        "high": price_target_info['price_range_high']
    },
    "price_change_percent": price_target_info['price_change_percent'],
    "timeframe": price_target_info['timeframe_text'],
    "timeframe_days": price_target_info['timeframe_days'],
    "market_metrics": {
        "volatility": price_target_info['volatility'],
        "atr": price_target_info['atr'],
        "momentum": price_target_info['momentum']
    },
    "data_points_used": len(df),
    "top_features": top_features,
    "timestamp": datetime.now().isoformat()
}
"""