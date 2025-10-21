#!/usr/bin/env python3
"""
ML Stock Predictor - Multi-Source Data
Supports both Yahoo Finance and Alpha Vantage (including MCP server)
NO fallback data - only REAL market data from chosen source
"""

import os
import sys
import json
import logging
import warnings
from datetime import datetime
from typing import Dict, Optional, Any

warnings.filterwarnings('ignore')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our data fetchers
from alpha_vantage_fetcher import AlphaVantageMLDataFetcher

# Import the existing ML system
from ml_stock_predictor import (
    DataFetcher as YahooDataFetcher,
    FeatureEngineer,
    MLModels,
    PORT
)

# FastAPI setup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# ==================== CONFIGURATION ====================
# Try to import from config file first
try:
    from config import ALPHA_VANTAGE_API_KEY, DEFAULT_DATA_SOURCE, API_PORT
    DATA_SOURCE = os.getenv('DATA_SOURCE', DEFAULT_DATA_SOURCE).lower()
    ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', ALPHA_VANTAGE_API_KEY)
    PORT = API_PORT
    logger.info(f"✅ Config loaded - Alpha Vantage key configured")
except ImportError:
    DATA_SOURCE = os.getenv('DATA_SOURCE', 'yahoo').lower()
    ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    logger.info("Using environment variables for config")

# ==================== MULTI-SOURCE DATA FETCHER ====================
class MultiSourceDataFetcher:
    """
    Unified data fetcher that can use either Yahoo Finance or Alpha Vantage
    NO fallback - if primary source fails, system fails (no fake data)
    """
    
    def __init__(self, source: str = 'yahoo', api_key: Optional[str] = None):
        """
        Initialize data fetcher with specified source
        
        Args:
            source: 'yahoo' or 'alpha_vantage'
            api_key: API key for Alpha Vantage (optional for Yahoo)
        """
        self.source = source.lower()
        
        if self.source == 'alpha_vantage':
            if not api_key and not ALPHA_VANTAGE_KEY:
                raise ValueError(
                    "Alpha Vantage API key required. Set ALPHA_VANTAGE_API_KEY environment variable "
                    "or get a free key at https://www.alphavantage.co/support/#api-key"
                )
            self.fetcher = AlphaVantageMLDataFetcher(api_key or ALPHA_VANTAGE_KEY)
            logger.info("📊 Using Alpha Vantage as data source")
        else:
            self.fetcher = YahooDataFetcher()
            logger.info("📈 Using Yahoo Finance as data source")
    
    def fetch_stock_data(self, symbol: str, period: str = "6mo", interval: str = "1d"):
        """
        Fetch stock data from configured source
        NO FALLBACK - real data only
        """
        logger.info(f"Fetching {symbol} from {self.source.upper()}...")
        
        try:
            data = self.fetcher.fetch_stock_data(symbol, period, interval)
            
            if data is None or data.empty:
                raise ValueError(f"No data returned from {self.source}")
            
            logger.info(f"✅ Got {len(data)} days of REAL data from {self.source}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch from {self.source}: {e}")
            # NO FALLBACK - we fail if we can't get real data
            raise ValueError(f"Cannot fetch real data from {self.source}: {e}")
    
    def clear_cache(self):
        """Clear cache if applicable"""
        if hasattr(self.fetcher, 'clear_cache'):
            self.fetcher.clear_cache()

# ==================== ML SYSTEM WITH MULTI-SOURCE ====================
class MultiSourceMLPredictor:
    """ML predictor that can use multiple data sources"""
    
    def __init__(self, data_source: str = 'yahoo', api_key: Optional[str] = None):
        self.data_fetcher = MultiSourceDataFetcher(data_source, api_key)
        self.feature_engineer = FeatureEngineer()
        self.models = MLModels()
        self.data_source = data_source
    
    def train(self, symbol: str, period: str = "6mo") -> Dict:
        """Train models using data from configured source"""
        try:
            # Fetch REAL data (no fallback)
            df = self.data_fetcher.fetch_stock_data(symbol, period)
            
            # Add technical indicators
            df = self.feature_engineer.add_technical_indicators(df)
            
            # Prepare features
            X, y = self.models.prepare_features(df)
            
            # Train models
            self.models.train_models(X, y, symbol)
            
            return {
                'success': True,
                'symbol': symbol,
                'data_source': self.data_source,
                'data_points': len(df),
                'training_period': period,
                'features': len(self.models.feature_columns)
            }
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'data_source': self.data_source
            }
    
    def predict(self, symbol: str, days: int = 5) -> Dict:
        """Make predictions using trained model"""
        try:
            # Check if model exists
            if symbol not in self.models.scalers:
                return {
                    'success': False,
                    'error': f"No trained model for {symbol}. Train first."
                }
            
            # Fetch latest data
            df = self.data_fetcher.fetch_stock_data(symbol, period="1mo")
            
            # Add indicators
            df = self.feature_engineer.add_technical_indicators(df)
            
            # Get latest features
            latest_features = df[self.models.feature_columns].iloc[-1:].values
            
            # Scale
            scaler = self.models.scalers[symbol]
            latest_scaled = scaler.transform(latest_features)
            
            # Predict with ensemble
            if f"{symbol}_ensemble" in self.models.models:
                model = self.models.models[f"{symbol}_ensemble"]
            else:
                model = self.models.models[f"{symbol}_random_forest"]
            
            prediction = model.predict(latest_scaled)[0]
            
            # Get current price
            current_price = float(df['Close'].iloc[-1])
            
            # Calculate change
            price_change = prediction - current_price
            pct_change = (price_change / current_price) * 100
            
            return {
                'success': True,
                'symbol': symbol,
                'data_source': self.data_source,
                'current_price': current_price,
                'predicted_price': float(prediction),
                'price_change': float(price_change),
                'pct_change': float(pct_change),
                'prediction_days': days,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'data_source': self.data_source
            }

# ==================== FastAPI Application ====================
app = FastAPI(title="ML Stock Predictor - Multi-Source")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize predictor
predictor = MultiSourceMLPredictor(DATA_SOURCE)

# ==================== API Endpoints ====================

class TrainRequest(BaseModel):
    symbol: str
    period: str = "6mo"
    source: Optional[str] = None

class PredictRequest(BaseModel):
    symbol: str
    days: int = 5

class DataSourceRequest(BaseModel):
    source: str
    api_key: Optional[str] = None

@app.get("/")
async def root():
    return {
        "status": "ML Stock Predictor - Multi-Source",
        "current_source": DATA_SOURCE.upper(),
        "available_sources": ["Yahoo Finance", "Alpha Vantage"],
        "alpha_vantage_configured": bool(ALPHA_VANTAGE_KEY),
        "real_data_only": "NO fallback, NO demo, NO simulated data",
        "port": PORT
    }

@app.get("/source")
async def get_data_source():
    """Get current data source configuration"""
    return {
        "current_source": DATA_SOURCE,
        "alpha_vantage_available": bool(ALPHA_VANTAGE_KEY),
        "rate_limits": {
            "yahoo": "No official limit (be respectful)",
            "alpha_vantage_free": "5 requests/minute, 500/day",
            "alpha_vantage_premium": "Higher limits available"
        }
    }

@app.post("/source")
async def change_data_source(request: DataSourceRequest):
    """Change data source (Yahoo or Alpha Vantage)"""
    global predictor, DATA_SOURCE
    
    try:
        if request.source.lower() not in ['yahoo', 'alpha_vantage']:
            return {
                "success": False,
                "error": "Source must be 'yahoo' or 'alpha_vantage'"
            }
        
        # Create new predictor with new source
        predictor = MultiSourceMLPredictor(request.source, request.api_key)
        DATA_SOURCE = request.source.lower()
        
        return {
            "success": True,
            "message": f"Switched to {request.source}",
            "current_source": DATA_SOURCE
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/train")
async def train_model(request: TrainRequest):
    """Train ML models using configured data source"""
    # Allow temporary source override
    if request.source:
        temp_predictor = MultiSourceMLPredictor(request.source)
        result = temp_predictor.train(request.symbol, request.period)
    else:
        result = predictor.train(request.symbol, request.period)
    
    return result

@app.post("/predict")
async def make_prediction(request: PredictRequest):
    """Make prediction using trained model"""
    result = predictor.predict(request.symbol, request.days)
    return result

@app.get("/test/{symbol}")
async def test_data_fetch(symbol: str):
    """Test data fetching from current source"""
    try:
        df = predictor.data_fetcher.fetch_stock_data(symbol, period="1mo")
        return {
            "success": True,
            "source": DATA_SOURCE,
            "symbol": symbol,
            "records": len(df),
            "latest_date": str(df.index[-1]),
            "latest_close": float(df['Close'].iloc[-1])
        }
    except Exception as e:
        return {
            "success": False,
            "source": DATA_SOURCE,
            "error": str(e)
        }

@app.get("/compare/{symbol}")
async def compare_sources(symbol: str):
    """Compare data from both Yahoo and Alpha Vantage"""
    results = {}
    
    # Test Yahoo
    try:
        yahoo_fetcher = MultiSourceDataFetcher('yahoo')
        yahoo_data = yahoo_fetcher.fetch_stock_data(symbol, period="1mo")
        results['yahoo'] = {
            "success": True,
            "records": len(yahoo_data),
            "latest_close": float(yahoo_data['Close'].iloc[-1]),
            "date_range": f"{yahoo_data.index[0].date()} to {yahoo_data.index[-1].date()}"
        }
    except Exception as e:
        results['yahoo'] = {"success": False, "error": str(e)}
    
    # Test Alpha Vantage (if configured)
    if ALPHA_VANTAGE_KEY:
        try:
            av_fetcher = MultiSourceDataFetcher('alpha_vantage')
            av_data = av_fetcher.fetch_stock_data(symbol, period="1mo")
            results['alpha_vantage'] = {
                "success": True,
                "records": len(av_data),
                "latest_close": float(av_data['Close'].iloc[-1]),
                "date_range": f"{av_data.index[0].date()} to {av_data.index[-1].date()}"
            }
        except Exception as e:
            results['alpha_vantage'] = {"success": False, "error": str(e)}
    else:
        results['alpha_vantage'] = {"success": False, "error": "No API key configured"}
    
    return results

# ==================== Main ====================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("ML STOCK PREDICTOR - MULTI-SOURCE DATA")
    print("="*60)
    print(f"📊 Current Data Source: {DATA_SOURCE.upper()}")
    
    if DATA_SOURCE == 'alpha_vantage':
        if ALPHA_VANTAGE_KEY:
            print(f"✅ Alpha Vantage API key configured: {ALPHA_VANTAGE_KEY[:8]}...")
            print("⚠️  Rate limits: 5 requests/minute (free tier)")
        else:
            print("❌ No Alpha Vantage API key found!")
            print("   Set ALPHA_VANTAGE_API_KEY environment variable")
            print("   Get free key at: https://www.alphavantage.co/support/#api-key")
    else:
        print("✅ Using Yahoo Finance (no API key required)")
    
    print("\n📌 Features:")
    print("  • NO fallback data - real market data only")
    print("  • Switch between Yahoo and Alpha Vantage")
    print("  • Support for MCP server integration")
    print("  • 1+ year historical data available")
    
    print(f"\n🚀 Starting server on http://localhost:{PORT}")
    print("\nEndpoints:")
    print(f"  GET  /source - Check current data source")
    print(f"  POST /source - Change data source")
    print(f"  GET  /test/AAPL - Test data fetching")
    print(f"  GET  /compare/AAPL - Compare both sources")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)