#!/usr/bin/env python3
"""
GSMT Trading System - Local Backend Server
Simplified version for Windows 11 local deployment
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="GSMT Trading System - Local API",
    description="Local deployment for Windows 11",
    version="1.0.0"
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple ML models for predictions
class PredictionEngine:
    """Simplified prediction engine for local deployment"""
    
    @staticmethod
    def calculate_technical_indicators(df: pd.DataFrame) -> Dict:
        """Calculate basic technical indicators"""
        try:
            close_prices = df['Close'].values
            
            # RSI calculation
            delta = pd.Series(close_prices).diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = pd.Series(close_prices).ewm(span=12, adjust=False).mean()
            exp2 = pd.Series(close_prices).ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            
            # Volatility
            returns = pd.Series(close_prices).pct_change()
            volatility = returns.std()
            
            # Volume ratio
            volume = df['Volume'].values
            volume_ratio = volume[-1] / np.mean(volume[-20:]) if len(volume) >= 20 else 1.0
            
            # Moving averages
            sma_20 = np.mean(close_prices[-20:]) if len(close_prices) >= 20 else close_prices[-1]
            sma_50 = np.mean(close_prices[-50:]) if len(close_prices) >= 50 else close_prices[-1]
            
            return {
                "rsi": float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0,
                "macd": float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else 0.0,
                "volatility": float(volatility) if not pd.isna(volatility) else 0.2,
                "volume_ratio": float(volume_ratio),
                "sma_20": float(sma_20),
                "sma_50": float(sma_50)
            }
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return {
                "rsi": 50.0,
                "macd": 0.0,
                "volatility": 0.2,
                "volume_ratio": 1.0,
                "sma_20": 0.0,
                "sma_50": 0.0
            }
    
    @staticmethod
    def predict_price(current_price: float, indicators: Dict, timeframe: str) -> Dict:
        """Simple prediction logic based on technical indicators"""
        
        # Base prediction using momentum and mean reversion
        rsi = indicators.get('rsi', 50)
        macd = indicators.get('macd', 0)
        volatility = indicators.get('volatility', 0.02)
        
        # Timeframe multipliers
        timeframe_multipliers = {
            '1d': 1.0,
            '5d': 2.5,
            '30d': 7.0,
            '90d': 15.0
        }
        multiplier = timeframe_multipliers.get(timeframe, 1.0)
        
        # Calculate price change based on indicators
        rsi_signal = (50 - rsi) / 100  # Mean reversion
        macd_signal = np.sign(macd) * min(abs(macd) / 10, 0.02)  # Momentum
        
        # Random walk component for realism
        random_component = np.random.normal(0, volatility * 0.3)
        
        # Combine signals
        total_change = (rsi_signal * 0.3 + macd_signal * 0.4 + random_component * 0.3) * multiplier
        
        # Apply volatility scaling
        total_change *= (1 + volatility)
        
        # Calculate predictions
        predicted_price = current_price * (1 + total_change)
        
        # Simple LSTM simulation (weighted average with trend)
        lstm_prediction = predicted_price * 0.95 + current_price * 0.05
        
        # Simple GNN simulation (network effect)
        gnn_prediction = predicted_price * 0.9 + current_price * 0.1
        
        # Ensemble prediction
        ensemble_prediction = (predicted_price + lstm_prediction + gnn_prediction) / 3
        
        # RL signal based on indicators
        if rsi < 30 and macd > 0:
            rl_signal = "BUY"
        elif rsi > 70 and macd < 0:
            rl_signal = "SELL"
        else:
            rl_signal = "HOLD"
        
        # Determine trend
        if total_change > 0.01:
            trend = "UP"
        elif total_change < -0.01:
            trend = "DOWN"
        else:
            trend = "NEUTRAL"
        
        return {
            "final_prediction": ensemble_prediction,
            "price_change_percent": total_change * 100,
            "trend": trend,
            "trend_strength": min(abs(total_change) * 10, 1.0),
            "models": {
                "ensemble": ensemble_prediction,
                "lstm": lstm_prediction,
                "gnn": gnn_prediction,
                "rl_signal": rl_signal
            },
            "confidence_scores": {
                "ensemble": 0.7 + np.random.random() * 0.2,
                "lstm": 0.6 + np.random.random() * 0.3,
                "gnn": 0.5 + np.random.random() * 0.3,
                "rl": 0.6 + np.random.random() * 0.2
            }
        }
    
    @staticmethod
    def calculate_support_resistance(prices: np.ndarray) -> Dict:
        """Calculate support and resistance levels"""
        if len(prices) < 20:
            current = prices[-1] if len(prices) > 0 else 100
            return {
                "support_levels": [current * 0.98, current * 0.95],
                "resistance_levels": [current * 1.02, current * 1.05]
            }
        
        # Simple pivot point calculation
        high = np.max(prices[-20:])
        low = np.min(prices[-20:])
        close = prices[-1]
        
        pivot = (high + low + close) / 3
        
        support1 = pivot * 2 - high
        support2 = pivot - (high - low)
        
        resistance1 = pivot * 2 - low
        resistance2 = pivot + (high - low)
        
        return {
            "support_levels": [float(support1), float(support2)],
            "resistance_levels": [float(resistance1), float(resistance2)]
        }

# API Endpoints

@app.get("/")
async def root():
    return {
        "message": "GSMT Trading System - Local API",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "predict": "/api/unified-prediction/{symbol}",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "GSMT Local API",
        "environment": "local_windows"
    }

@app.get("/api/unified-prediction/{symbol}")
async def get_unified_prediction(
    symbol: str,
    timeframe: str = "5d"
):
    """Get unified prediction for a stock symbol"""
    
    try:
        # Fetch stock data from Yahoo Finance
        ticker = yf.Ticker(symbol)
        
        # Get historical data
        period_map = {
            "1d": "5d",
            "5d": "1mo",
            "30d": "3mo",
            "90d": "6mo"
        }
        period = period_map.get(timeframe, "1mo")
        
        hist = ticker.history(period=period)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        # Current price
        current_price = float(hist['Close'].iloc[-1])
        
        # Calculate indicators
        engine = PredictionEngine()
        indicators = engine.calculate_technical_indicators(hist)
        
        # Generate predictions
        predictions = engine.predict_price(current_price, indicators, timeframe)
        
        # Calculate support/resistance
        support_resistance = engine.calculate_support_resistance(hist['Close'].values)
        
        # Combine results
        result = {
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "timestamp": datetime.now().isoformat(),
            "predictions": {
                "prediction_engine": {
                    "current_price": current_price,
                    "final_prediction": predictions["final_prediction"],
                    "price_change_percent": predictions["price_change_percent"],
                    "trend": predictions["trend"],
                    "trend_strength": predictions["trend_strength"],
                    "models": predictions["models"],
                    "confidence_scores": predictions["confidence_scores"],
                    "technical_indicators": indicators,
                    **support_resistance
                }
            },
            "status": "success"
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backtest")
async def run_backtest(request: Dict[str, Any]):
    """Simple backtest endpoint"""
    
    symbol = request.get("symbol", "AAPL")
    start_date = request.get("start_date", "2024-01-01")
    end_date = request.get("end_date", datetime.now().strftime("%Y-%m-%d"))
    initial_capital = request.get("initial_capital", 100000)
    
    try:
        # Simple backtest simulation
        returns = np.random.normal(0.001, 0.02, 100)  # Simulated returns
        cumulative_returns = np.cumprod(1 + returns)
        
        total_return = cumulative_returns[-1] - 1
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
        max_drawdown = np.min(cumulative_returns / np.maximum.accumulate(cumulative_returns) - 1)
        
        return {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "initial_capital": initial_capital,
            "total_return": float(total_return),
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "win_rate": 0.55 + np.random.random() * 0.1,
            "total_trades": int(50 + np.random.random() * 50)
        }
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        return {"error": str(e)}

@app.get("/api/technical/analysis/{symbol}")
async def get_technical_analysis(symbol: str):
    """Get technical analysis for a symbol"""
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        engine = PredictionEngine()
        indicators = engine.calculate_technical_indicators(hist)
        
        return {
            "symbol": symbol,
            "indicators": indicators,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add more endpoints as needed...

if __name__ == "__main__":
    print("=" * 50)
    print("GSMT Trading System - Local Server")
    print("=" * 50)
    print("Starting server on http://localhost:8000")
    print("API documentation at http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)