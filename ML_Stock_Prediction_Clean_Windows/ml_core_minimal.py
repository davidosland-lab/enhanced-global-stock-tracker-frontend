#!/usr/bin/env python3
"""
Minimal ML Core - Simplest possible version that should work
"""

PORT = 8000

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn

class SimpleMLPredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        
    def train_model(self, symbol: str):
        """Simplest possible training"""
        try:
            print(f"\n{'='*50}")
            print(f"Training {symbol}")
            print(f"{'='*50}")
            
            # Step 1: Get data
            print("Step 1: Fetching data...")
            df = yf.download(symbol, period="6mo", progress=False, threads=False)
            
            if df.empty or len(df) < 30:
                return {'error': f'Not enough data for {symbol}'}
            
            print(f"  Got {len(df)} rows of data")
            
            # Step 2: Simple features (just 5)
            print("Step 2: Creating features...")
            features = pd.DataFrame(index=df.index)
            features['returns'] = df['Close'].pct_change()
            features['volume'] = df['Volume']
            features['high_low'] = df['High'] - df['Low']
            features['close_open'] = df['Close'] - df['Open']
            features['sma_diff'] = df['Close'] - df['Close'].rolling(20).mean()
            
            # Remove NaN
            features = features.fillna(0)
            
            # Step 3: Prepare target (next day return)
            target = df['Close'].shift(-1) / df['Close'] - 1
            
            # Remove last row (no target)
            features = features[:-1]
            target = target[:-1]
            
            # Remove first 20 rows (not enough history)
            features = features[20:]
            target = target[20:]
            
            if len(features) < 30:
                return {'error': 'Not enough data after cleaning'}
            
            print(f"  Created {len(features.columns)} features, {len(features)} samples")
            
            # Step 4: Split data
            split = int(len(features) * 0.8)
            X_train = features[:split]
            y_train = target[:split]
            
            # Step 5: Scale
            print("Step 3: Scaling features...")
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_train)
            
            # Step 6: Train simple model
            print("Step 4: Training RandomForest...")
            model = RandomForestRegressor(
                n_estimators=50,  # Reduced for speed
                max_depth=10,
                random_state=42
            )
            model.fit(X_scaled, y_train)
            
            # Step 7: Calculate score
            score = model.score(X_scaled, y_train)
            print(f"  Training score: {score:.4f}")
            
            # Store
            self.models[symbol] = model
            self.scalers[symbol] = scaler
            
            print(f"✅ Training complete!")
            
            return {
                'symbol': symbol,
                'status': 'success',
                'samples': len(X_train),
                'features': len(features.columns),
                'score': float(score),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"❌ {error_msg}")
            return {'error': error_msg, 'symbol': symbol}
    
    def predict(self, symbol: str):
        """Simple prediction"""
        try:
            if symbol not in self.models:
                return {'error': f'No model for {symbol}'}
            
            # Get recent data
            df = yf.download(symbol, period="1mo", progress=False, threads=False)
            
            # Create same features
            features = pd.DataFrame(index=df.index)
            features['returns'] = df['Close'].pct_change()
            features['volume'] = df['Volume']
            features['high_low'] = df['High'] - df['Low']
            features['close_open'] = df['Close'] - df['Open']
            features['sma_diff'] = df['Close'] - df['Close'].rolling(20).mean()
            
            features = features.fillna(0)
            
            # Get last row
            X = features.iloc[-1:].values
            X_scaled = self.scalers[symbol].transform(X)
            
            # Predict
            prediction = self.models[symbol].predict(X_scaled)[0]
            
            return {
                'symbol': symbol,
                'prediction': float(prediction),
                'direction': 'UP' if prediction > 0 else 'DOWN',
                'current_price': float(df['Close'].iloc[-1]),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e), 'symbol': symbol}

# Create app
app = FastAPI()
predictor = SimpleMLPredictor()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    try:
        with open("ml_core_interface_clean.html", "r") as f:
            return HTMLResponse(content=f.read())
    except:
        return {"message": "ML Predictor - Minimal Version"}

@app.post("/api/train")
async def train(request: dict):
    symbol = request.get('symbol', 'AAPL').upper()
    result = predictor.train_model(symbol)
    return JSONResponse(content=result)

@app.post("/api/predict")
async def predict(request: dict):
    symbol = request.get('symbol', 'AAPL').upper()
    result = predictor.predict(symbol)
    return JSONResponse(content=result)

@app.get("/api/test")
async def test():
    """Test if API is running"""
    return {"status": "running", "version": "minimal"}

if __name__ == "__main__":
    print("="*60)
    print("ML Stock Predictor - MINIMAL VERSION")
    print("="*60)
    print(f"Starting on http://localhost:{PORT}")
    print("\nThis is the simplest possible version")
    print("Watch the console for training progress\n")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)