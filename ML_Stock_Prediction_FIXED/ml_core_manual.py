#!/usr/bin/env python3
"""
ML Core with Manual Data Input Option
For when Yahoo Finance is completely blocked
"""

PORT = 8000

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.preprocessing import StandardScaler

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn

class ManualDataPredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.manual_data = {}
        
    def load_manual_data(self, symbol: str, data: dict):
        """Load manually provided data"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            
            # Store
            self.manual_data[symbol] = df
            
            return {
                'status': 'success',
                'symbol': symbol,
                'rows': len(df),
                'columns': list(df.columns)
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_sample_data_format(self):
        """Return sample data format for manual input"""
        return {
            'format': 'JSON',
            'example': {
                'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
                'Open': [150.0, 151.0, 149.5],
                'High': [152.0, 153.0, 151.0],
                'Low': [149.0, 150.0, 148.5],
                'Close': [151.0, 149.5, 150.5],
                'Volume': [50000000, 45000000, 48000000]
            },
            'required_columns': ['Date', 'Open', 'High', 'Low', 'Close', 'Volume'],
            'minimum_rows': 60
        }
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Simple feature preparation"""
        features = pd.DataFrame(index=df.index)
        
        # Basic features
        features['returns'] = df['Close'].pct_change()
        features['volume'] = df['Volume']
        features['high_low'] = df['High'] - df['Low']
        features['close_open'] = df['Close'] - df['Open']
        
        # Simple moving averages
        for period in [5, 10, 20]:
            features[f'sma_{period}'] = df['Close'].rolling(window=period).mean()
        
        # Fill NaN
        features = features.fillna(0)
        
        return features
    
    def train_with_manual_data(self, symbol: str):
        """Train using manually provided data"""
        try:
            if symbol not in self.manual_data:
                return {'error': f'No manual data for {symbol}'}
            
            df = self.manual_data[symbol]
            
            if len(df) < 60:
                return {'error': f'Need at least 60 rows, got {len(df)}'}
            
            # Prepare features
            features = self.prepare_features(df)
            
            # Target
            target = df['Close'].shift(-1) / df['Close'] - 1
            
            # Clean
            features = features[20:-1]
            target = target[20:-1]
            
            # Split
            split = int(len(features) * 0.8)
            X_train = features[:split]
            y_train = target[:split]
            
            # Scale
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_train)
            
            # Train simple model
            model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
            model.fit(X_scaled, y_train)
            
            # Store
            self.models[symbol] = model
            self.scalers[symbol] = scaler
            
            score = model.score(X_scaled, y_train)
            
            return {
                'status': 'success',
                'symbol': symbol,
                'samples': len(X_train),
                'score': float(score),
                'message': 'Trained with manual data'
            }
            
        except Exception as e:
            return {'error': str(e)}

# Create app
app = FastAPI(title="ML Predictor - Manual Data Mode")
predictor = ManualDataPredictor()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Serve interface"""
    return {
        "message": "ML Predictor - Manual Data Mode",
        "instructions": "Use /api/manual/format to see data format",
        "note": "This mode allows manual data input when Yahoo Finance is blocked"
    }

@app.get("/api/manual/format")
async def get_format():
    """Get manual data format"""
    return predictor.get_sample_data_format()

@app.post("/api/manual/load")
async def load_data(request: dict):
    """Load manual data"""
    symbol = request.get('symbol', 'MANUAL').upper()
    data = request.get('data')
    
    if not data:
        raise HTTPException(status_code=400, detail="No data provided")
    
    result = predictor.load_manual_data(symbol, data)
    return JSONResponse(content=result)

@app.post("/api/manual/train")
async def train_manual(request: dict):
    """Train with manual data"""
    symbol = request.get('symbol', 'MANUAL').upper()
    result = predictor.train_with_manual_data(symbol)
    return JSONResponse(content=result)

@app.get("/api/manual/status")
async def status():
    """System status"""
    return {
        'mode': 'manual_data',
        'loaded_symbols': list(predictor.manual_data.keys()),
        'trained_models': list(predictor.models.keys()),
        'note': 'Using manual data input due to Yahoo Finance issues'
    }

if __name__ == "__main__":
    print("="*60)
    print("ML Predictor - MANUAL DATA MODE")
    print("="*60)
    print("\nThis mode allows manual data input")
    print("when Yahoo Finance is blocked\n")
    print(f"Starting on http://localhost:{PORT}")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)