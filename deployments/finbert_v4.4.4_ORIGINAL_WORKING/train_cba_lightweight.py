#!/usr/bin/env python3
"""
Lightweight LSTM Training Script for CBA.AX
Uses simple neural network approach without full TensorFlow
"""

import sys
import os
import json
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def fetch_stock_data(symbol: str, days: int = 365):
    """Fetch stock data from Yahoo Finance"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        print(f"Fetching data for {symbol}...")
        stock = yf.Ticker(symbol)
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty:
            raise ValueError(f"No data found for {symbol}")
        
        # Calculate technical indicators
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # RSI calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        
        # Volume ratio
        df['Volume_Ratio'] = df['Volume'] / df['Volume'].rolling(window=20).mean()
        
        # Fill NaN values
        df = df.fillna(method='ffill').fillna(0)
        
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def prepare_sequences(df, sequence_length=30):
    """Prepare sequences for training"""
    features = ['Close', 'Volume', 'High', 'Low', 'Open', 'SMA_20', 'RSI', 'MACD']
    
    # Select available features
    available_features = [f for f in features if f in df.columns]
    data = df[available_features].values
    
    # Normalize data
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    
    # Create sequences
    X, y = [], []
    for i in range(sequence_length, len(scaled_data) - 1):
        X.append(scaled_data[i - sequence_length:i])
        y.append(scaled_data[i, 0])  # Predict next close price
    
    return np.array(X), np.array(y), scaler, available_features

def create_simple_model(input_shape):
    """Create a simple neural network model"""
    import tensorflow.keras as keras
    from tensorflow.keras import layers
    
    model = keras.Sequential([
        layers.LSTM(50, return_sequences=True, input_shape=input_shape),
        layers.Dropout(0.2),
        layers.LSTM(50, return_sequences=False),
        layers.Dropout(0.2),
        layers.Dense(25),
        layers.Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def train_lightweight_model(symbol: str, epochs: int = 50, sequence_length: int = 30):
    """Train a lightweight model for the given symbol"""
    
    # Fetch data
    df = fetch_stock_data(symbol, days=500)
    if df is None:
        return {"error": "Failed to fetch data"}
    
    print(f"Data fetched: {len(df)} days")
    
    # Prepare sequences
    X, y, scaler, features = prepare_sequences(df, sequence_length)
    
    if len(X) == 0:
        return {"error": "Insufficient data for training"}
    
    print(f"Prepared {len(X)} sequences with {len(features)} features")
    
    # Split data
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
    
    # Try to use TensorFlow if available
    try:
        import tensorflow as tf
        print("Using TensorFlow for training...")
        
        model = create_simple_model((sequence_length, len(features)))
        
        # Train model
        history = model.fit(
            X_train, y_train,
            batch_size=32,
            epochs=epochs,
            validation_data=(X_test, y_test),
            verbose=1
        )
        
        # Save model
        model_path = f"models/lstm_{symbol.replace('.', '_')}_model.h5"
        model.save(model_path)
        print(f"Model saved to {model_path}")
        
        # Get final metrics
        final_loss = history.history['loss'][-1]
        final_val_loss = history.history['val_loss'][-1]
        
        result = {
            "status": "success",
            "symbol": symbol,
            "training_date": datetime.now().isoformat(),
            "epochs": epochs,
            "final_loss": final_loss,
            "final_val_loss": final_val_loss,
            "features": features,
            "sequence_length": sequence_length,
            "model_path": model_path
        }
        
    except ImportError:
        print("TensorFlow not available. Using simple prediction model...")
        
        # Fallback: Simple moving average based prediction
        current_price = df['Close'].iloc[-1]
        sma_20 = df['SMA_20'].iloc[-1] if 'SMA_20' in df.columns else current_price
        sma_50 = df['SMA_50'].iloc[-1] if 'SMA_50' in df.columns else current_price
        rsi = df['RSI'].iloc[-1] if 'RSI' in df.columns else 50
        
        # Simple prediction logic
        if current_price > sma_20 and current_price > sma_50 and rsi < 70:
            prediction = "BUY"
            predicted_price = current_price * 1.02  # 2% increase
            confidence = 65
        elif current_price < sma_20 and current_price < sma_50 and rsi > 30:
            prediction = "SELL"
            predicted_price = current_price * 0.98  # 2% decrease
            confidence = 65
        else:
            prediction = "HOLD"
            predicted_price = current_price
            confidence = 50
        
        result = {
            "status": "success (fallback)",
            "symbol": symbol,
            "training_date": datetime.now().isoformat(),
            "current_price": float(current_price),
            "predicted_price": float(predicted_price),
            "prediction": prediction,
            "confidence": confidence,
            "sma_20": float(sma_20),
            "sma_50": float(sma_50),
            "rsi": float(rsi),
            "note": "Using simple technical analysis model (TensorFlow not available)"
        }
    
    # Save metadata
    metadata_path = f"models/lstm_{symbol.replace('.', '_')}_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"Metadata saved to {metadata_path}")
    
    return result

def main():
    print("\n" + "="*60)
    print("CBA.AX LSTM Training - Lightweight Version")
    print("="*60 + "\n")
    
    # Train for CBA.AX
    result = train_lightweight_model("CBA.AX", epochs=50, sequence_length=30)
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE")
    print("="*60 + "\n")
    
    if "error" not in result:
        print(f"Symbol: {result.get('symbol')}")
        print(f"Status: {result.get('status')}")
        
        if 'final_loss' in result:
            print(f"Final Loss: {result.get('final_loss', 'N/A'):.6f}")
            print(f"Final Val Loss: {result.get('final_val_loss', 'N/A'):.6f}")
        
        if 'prediction' in result:
            print(f"\nCurrent Analysis:")
            print(f"  Current Price: ${result.get('current_price', 0):.2f}")
            print(f"  Predicted Price: ${result.get('predicted_price', 0):.2f}")
            print(f"  Prediction: {result.get('prediction')} ({result.get('confidence')}% confidence)")
            print(f"  SMA 20: ${result.get('sma_20', 0):.2f}")
            print(f"  SMA 50: ${result.get('sma_50', 0):.2f}")
            print(f"  RSI: {result.get('rsi', 0):.2f}")
            
            if 'note' in result:
                print(f"\nNote: {result['note']}")
    else:
        print(f"Error: {result['error']}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    # Change to the correct directory
    os.chdir('/home/user/webapp/FinBERT_v4.0_Development')
    main()