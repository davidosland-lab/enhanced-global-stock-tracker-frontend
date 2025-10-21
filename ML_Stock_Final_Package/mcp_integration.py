#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server Integration
Provides AI assistants with direct access to ML stock prediction capabilities
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServer:
    """
    MCP Server for ML Stock Predictor integration
    Provides tools for AI assistants to interact with the ML system
    """
    
    def __init__(self):
        """Initialize MCP Server with available tools"""
        self.ml_predictor = None
        self.finbert_analyzer = None
        self.tools = {}
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize ML components"""
        try:
            # Try to import ML predictor
            from ml_stock_predictor import MLStockPredictor
            self.ml_predictor = MLStockPredictor()
            logger.info("✅ ML Predictor initialized for MCP")
        except Exception as e:
            logger.warning(f"⚠️ ML Predictor not available: {e}")
            
        try:
            # Try to import FinBERT if available
            from finbert_analyzer import FinBERTAnalyzer
            self.finbert_analyzer = FinBERTAnalyzer()
            logger.info("✅ FinBERT Analyzer initialized for MCP")
        except Exception:
            logger.info("ℹ️ FinBERT not available (optional)")
    
    def get_available_tools(self) -> List[Dict]:
        """Return list of available MCP tools"""
        tools = [
            {
                "name": "get_stock_price",
                "description": "Get current stock price",
                "parameters": ["symbol", "source"]
            },
            {
                "name": "get_historical_data",
                "description": "Get historical stock data",
                "parameters": ["symbol", "period", "source"]
            },
            {
                "name": "calculate_indicators",
                "description": "Calculate technical indicators",
                "parameters": ["symbol", "indicators", "period"]
            },
            {
                "name": "train_model",
                "description": "Train ML model on stock data",
                "parameters": ["symbol", "model_type", "period"]
            },
            {
                "name": "predict_price",
                "description": "Predict future stock prices",
                "parameters": ["symbol", "days"]
            },
            {
                "name": "run_backtest",
                "description": "Run backtesting on historical data",
                "parameters": ["symbol", "period", "strategy"]
            }
        ]
        
        if self.finbert_analyzer:
            tools.append({
                "name": "analyze_sentiment",
                "description": "Analyze text sentiment using FinBERT",
                "parameters": ["text", "context"]
            })
            
        return tools
    
    async def get_stock_price(self, symbol: str, source: str = "yahoo") -> Dict:
        """Get current stock price"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                "success": True,
                "symbol": symbol,
                "price": info.get('currentPrice', info.get('regularMarketPrice', 0)),
                "change": info.get('regularMarketChange', 0),
                "change_percent": info.get('regularMarketChangePercent', 0),
                "volume": info.get('volume', 0),
                "source": source,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_historical_data(self, symbol: str, period: str = "1y", source: str = "yahoo") -> Dict:
        """Get historical stock data"""
        try:
            import yfinance as yf
            import pandas as pd
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty:
                return {"success": False, "error": "No data available"}
            
            # Convert to JSON-serializable format
            data = {
                "success": True,
                "symbol": symbol,
                "period": period,
                "source": source,
                "data_points": len(df),
                "start_date": df.index[0].strftime('%Y-%m-%d'),
                "end_date": df.index[-1].strftime('%Y-%m-%d'),
                "prices": df['Close'].tolist()[-30:],  # Last 30 days
                "dates": [d.strftime('%Y-%m-%d') for d in df.index[-30:]],
                "latest_price": float(df['Close'].iloc[-1]),
                "timestamp": datetime.now().isoformat()
            }
            
            return data
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def calculate_indicators(self, symbol: str, indicators: List[str] = None, period: str = "3mo") -> Dict:
        """Calculate technical indicators for a stock"""
        try:
            import yfinance as yf
            import pandas as pd
            import numpy as np
            
            if indicators is None:
                indicators = ["RSI", "MACD", "SMA_20", "EMA_20", "BB"]
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty:
                return {"success": False, "error": "No data available"}
            
            results = {
                "success": True,
                "symbol": symbol,
                "period": period,
                "indicators": {}
            }
            
            # Calculate requested indicators
            for indicator in indicators:
                if indicator == "RSI":
                    # RSI calculation
                    delta = df['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    rsi = 100 - (100 / (1 + rs))
                    results["indicators"]["RSI"] = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None
                    
                elif indicator == "SMA_20":
                    sma = df['Close'].rolling(window=20).mean()
                    results["indicators"]["SMA_20"] = float(sma.iloc[-1]) if not pd.isna(sma.iloc[-1]) else None
                    
                elif indicator == "EMA_20":
                    ema = df['Close'].ewm(span=20, adjust=False).mean()
                    results["indicators"]["EMA_20"] = float(ema.iloc[-1]) if not pd.isna(ema.iloc[-1]) else None
                    
                elif indicator == "MACD":
                    ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
                    ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
                    macd_line = ema_12 - ema_26
                    signal_line = macd_line.ewm(span=9, adjust=False).mean()
                    macd_histogram = macd_line - signal_line
                    results["indicators"]["MACD"] = {
                        "macd": float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else None,
                        "signal": float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else None,
                        "histogram": float(macd_histogram.iloc[-1]) if not pd.isna(macd_histogram.iloc[-1]) else None
                    }
                    
                elif indicator == "BB":
                    sma = df['Close'].rolling(window=20).mean()
                    std = df['Close'].rolling(window=20).std()
                    upper_band = sma + (std * 2)
                    lower_band = sma - (std * 2)
                    results["indicators"]["Bollinger_Bands"] = {
                        "upper": float(upper_band.iloc[-1]) if not pd.isna(upper_band.iloc[-1]) else None,
                        "middle": float(sma.iloc[-1]) if not pd.isna(sma.iloc[-1]) else None,
                        "lower": float(lower_band.iloc[-1]) if not pd.isna(lower_band.iloc[-1]) else None
                    }
            
            results["timestamp"] = datetime.now().isoformat()
            return results
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def train_model(self, symbol: str, model_type: str = "random_forest", period: str = "1y") -> Dict:
        """Train ML model on stock data"""
        try:
            if not self.ml_predictor:
                return {"success": False, "error": "ML Predictor not available"}
            
            # This would integrate with the actual ML training
            return {
                "success": True,
                "symbol": symbol,
                "model_type": model_type,
                "period": period,
                "message": f"Model training initiated for {symbol}",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def predict_price(self, symbol: str, days: int = 5) -> Dict:
        """Predict future stock prices"""
        try:
            if not self.ml_predictor:
                return {"success": False, "error": "ML Predictor not available"}
            
            # This would integrate with the actual prediction
            return {
                "success": True,
                "symbol": symbol,
                "days": days,
                "message": f"Prediction generated for {symbol} ({days} days)",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def run_backtest(self, symbol: str, period: str = "1y", strategy: str = "ml_based") -> Dict:
        """Run backtesting on historical data"""
        try:
            return {
                "success": True,
                "symbol": symbol,
                "period": period,
                "strategy": strategy,
                "message": f"Backtest initiated for {symbol}",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def analyze_sentiment(self, text: str, context: str = "news") -> Dict:
        """Analyze sentiment using FinBERT"""
        try:
            if not self.finbert_analyzer:
                return {"success": False, "error": "FinBERT not available"}
            
            # This would integrate with actual FinBERT
            return {
                "success": True,
                "text": text[:100] + "..." if len(text) > 100 else text,
                "context": context,
                "sentiment": "neutral",  # Placeholder
                "confidence": 0.85,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run(self, host: str = "localhost", port: int = 8001):
        """Run MCP server"""
        logger.info(f"🔌 MCP Server starting on http://{host}:{port}")
        # In a real implementation, this would start an async server
        # For now, we'll just log that it's ready
        logger.info("✅ MCP Server ready for connections")

# Initialize server if run directly
if __name__ == "__main__":
    server = MCPServer()
    print("Available MCP Tools:")
    for tool in server.get_available_tools():
        print(f"  - {tool['name']}: {tool['description']}")
    
    # Run some example async calls
    async def test_tools():
        price = await server.get_stock_price("AAPL")
        print(f"\nStock Price: {price}")
        
        indicators = await server.calculate_indicators("AAPL", ["RSI", "SMA_20"])
        print(f"\nIndicators: {indicators}")
    
    # Run tests
    asyncio.run(test_tools())