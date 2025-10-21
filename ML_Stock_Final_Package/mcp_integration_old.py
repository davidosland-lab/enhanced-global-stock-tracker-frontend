#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Integration
For Alpha Vantage data and FinBERT sentiment analysis
Enables AI assistants to access market data and sentiment analysis
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import asyncio
import aiohttp

# For FinBERT
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
import numpy as np

# For Alpha Vantage
from alpha_vantage_fetcher import AlphaVantageDataFetcher

logger = logging.getLogger(__name__)

# ==================== MCP SERVER INTERFACE ====================
class MCPServer:
    """
    MCP Server implementation for financial data and sentiment analysis
    Provides tools that AI assistants can call through the MCP protocol
    """
    
    def __init__(self):
        self.name = "financial_mcp_server"
        self.version = "1.0.0"
        self.tools = self._register_tools()
        
    def _register_tools(self) -> Dict:
        """Register all available MCP tools"""
        return {
            # Market Data Tools
            "get_stock_price": {
                "description": "Get current stock price and quote information",
                "parameters": {
                    "symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL)"},
                    "source": {"type": "string", "description": "Data source: yahoo or alpha_vantage", "default": "yahoo"}
                },
                "handler": self.get_stock_price
            },
            "get_historical_data": {
                "description": "Get historical stock data for analysis",
                "parameters": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                    "period": {"type": "string", "description": "Time period: 1mo, 3mo, 6mo, 1y, 2y", "default": "6mo"},
                    "source": {"type": "string", "description": "Data source", "default": "yahoo"}
                },
                "handler": self.get_historical_data
            },
            "get_technical_indicators": {
                "description": "Calculate technical indicators for a stock",
                "parameters": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                    "indicators": {"type": "array", "description": "List of indicators: RSI, MACD, SMA, EMA, etc."},
                    "period": {"type": "string", "description": "Time period", "default": "3mo"}
                },
                "handler": self.get_technical_indicators
            },
            
            # Sentiment Analysis Tools
            "analyze_sentiment": {
                "description": "Analyze sentiment of financial text using FinBERT",
                "parameters": {
                    "text": {"type": "string", "description": "Text to analyze"},
                    "context": {"type": "string", "description": "Context: news, earnings, social", "default": "news"}
                },
                "handler": self.analyze_sentiment
            },
            "analyze_news_sentiment": {
                "description": "Analyze sentiment of multiple news articles",
                "parameters": {
                    "articles": {"type": "array", "description": "List of article texts"},
                    "aggregate": {"type": "boolean", "description": "Return aggregate sentiment", "default": true}
                },
                "handler": self.analyze_news_sentiment
            },
            "get_market_sentiment": {
                "description": "Get overall market sentiment from various sources",
                "parameters": {
                    "symbols": {"type": "array", "description": "List of symbols to analyze"},
                    "sources": {"type": "array", "description": "Sources: news, social, analyst", "default": ["news"]}
                },
                "handler": self.get_market_sentiment
            },
            
            # ML Prediction Tools
            "train_model": {
                "description": "Train ML model on stock data",
                "parameters": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                    "period": {"type": "string", "description": "Training period", "default": "6mo"},
                    "include_sentiment": {"type": "boolean", "description": "Include sentiment features", "default": false}
                },
                "handler": self.train_model
            },
            "predict_price": {
                "description": "Predict future stock price",
                "parameters": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                    "days": {"type": "integer", "description": "Days to predict", "default": 5},
                    "include_sentiment": {"type": "boolean", "description": "Include sentiment in prediction", "default": false}
                },
                "handler": self.predict_price
            }
        }
    
    async def get_stock_price(self, symbol: str, source: str = "yahoo") -> Dict:
        """Get current stock price through MCP"""
        try:
            if source == "alpha_vantage":
                fetcher = AlphaVantageDataFetcher()
                quote = fetcher.get_quote_endpoint(symbol)
                return {
                    "success": True,
                    "symbol": symbol,
                    "price": quote['price'],
                    "change": quote['change'],
                    "change_percent": quote['change_percent'],
                    "volume": quote['volume'],
                    "source": "alpha_vantage"
                }
            else:
                # Use Yahoo Finance
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
                    "source": "yahoo"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_historical_data(self, symbol: str, period: str = "6mo", source: str = "yahoo") -> Dict:
        """Get historical data through MCP"""
        try:
            if source == "alpha_vantage":
                fetcher = AlphaVantageDataFetcher()
                df = fetcher.fetch_daily_data(symbol)
            else:
                import yfinance as yf
                df = yf.download(symbol, period=period, progress=False)
            
            return {
                "success": True,
                "symbol": symbol,
                "period": period,
                "data_points": len(df),
                "start_date": str(df.index[0]),
                "end_date": str(df.index[-1]),
                "latest_close": float(df['Close'].iloc[-1]),
                "data": df.to_dict('records')[-10:]  # Last 10 days
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def analyze_sentiment(self, text: str, context: str = "news") -> Dict:
        """Analyze sentiment using FinBERT through MCP"""
        try:
            analyzer = FinBERTSentimentAnalyzer()
            result = analyzer.analyze_text(text)
            
            return {
                "success": True,
                "text": text[:100] + "..." if len(text) > 100 else text,
                "sentiment": result['sentiment'],
                "confidence": result['confidence'],
                "scores": result['scores'],
                "context": context
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def analyze_news_sentiment(self, articles: List[str], aggregate: bool = True) -> Dict:
        """Analyze sentiment of multiple articles"""
        try:
            analyzer = FinBERTSentimentAnalyzer()
            results = []
            
            for article in articles:
                result = analyzer.analyze_text(article)
                results.append(result)
            
            if aggregate:
                # Calculate aggregate sentiment
                sentiments = [r['sentiment'] for r in results]
                sentiment_counts = {
                    'positive': sentiments.count('positive'),
                    'negative': sentiments.count('negative'),
                    'neutral': sentiments.count('neutral')
                }
                
                # Weighted average confidence
                avg_confidence = np.mean([r['confidence'] for r in results])
                
                # Overall sentiment
                overall = max(sentiment_counts, key=sentiment_counts.get)
                
                return {
                    "success": True,
                    "articles_analyzed": len(articles),
                    "overall_sentiment": overall,
                    "sentiment_distribution": sentiment_counts,
                    "average_confidence": float(avg_confidence),
                    "individual_results": results if not aggregate else None
                }
            else:
                return {
                    "success": True,
                    "articles_analyzed": len(articles),
                    "results": results
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}


# ==================== FINBERT SENTIMENT ANALYZER ====================
class FinBERTSentimentAnalyzer:
    """
    FinBERT-based sentiment analyzer for financial text
    Uses pre-trained FinBERT model for financial sentiment analysis
    """
    
    def __init__(self):
        self.model_name = "ProsusAI/finbert"
        self.tokenizer = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load FinBERT model and tokenizer"""
        try:
            logger.info("Loading FinBERT model...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.eval()
            logger.info("✅ FinBERT model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load FinBERT: {e}")
            logger.info("To use FinBERT, install: pip install transformers torch")
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of financial text
        
        Returns:
            Dictionary with sentiment (positive/negative/neutral) and confidence scores
        """
        if not self.model or not self.tokenizer:
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "error": "FinBERT model not loaded"
            }
        
        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Get sentiment scores
            positive = float(predictions[0][0])
            negative = float(predictions[0][1])
            neutral = float(predictions[0][2])
            
            # Determine sentiment
            scores = {'positive': positive, 'negative': negative, 'neutral': neutral}
            sentiment = max(scores, key=scores.get)
            confidence = scores[sentiment]
            
            return {
                "sentiment": sentiment,
                "confidence": confidence,
                "scores": scores,
                "text_length": len(text)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """Analyze sentiment of multiple texts efficiently"""
        results = []
        for text in texts:
            result = self.analyze_text(text)
            results.append(result)
        return results


# ==================== MCP CLIENT FOR AI ASSISTANTS ====================
class MCPClient:
    """
    MCP Client for AI assistants to interact with financial tools
    This is what AI assistants would use to call MCP tools
    """
    
    def __init__(self, server_url: str = "http://localhost:8001"):
        self.server_url = server_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def call_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """
        Call an MCP tool with parameters
        
        Example:
            result = await client.call_tool("get_stock_price", {"symbol": "AAPL"})
        """
        try:
            async with self.session.post(
                f"{self.server_url}/mcp/tools/{tool_name}",
                json=parameters
            ) as response:
                return await response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_stock_data_with_sentiment(self, symbol: str) -> Dict:
        """
        Get comprehensive stock data with sentiment analysis
        Combines multiple MCP tools for complete analysis
        """
        results = {}
        
        # Get current price
        price_data = await self.call_tool("get_stock_price", {"symbol": symbol})
        results['current'] = price_data
        
        # Get historical data
        hist_data = await self.call_tool("get_historical_data", {
            "symbol": symbol,
            "period": "1mo"
        })
        results['historical'] = hist_data
        
        # Get technical indicators
        indicators = await self.call_tool("get_technical_indicators", {
            "symbol": symbol,
            "indicators": ["RSI", "MACD", "SMA_20", "SMA_50"]
        })
        results['technical'] = indicators
        
        # Get market sentiment (would need news data)
        sentiment = await self.call_tool("get_market_sentiment", {
            "symbols": [symbol],
            "sources": ["news", "social"]
        })
        results['sentiment'] = sentiment
        
        return results


# ==================== FASTAPI MCP SERVER ====================
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Financial MCP Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP server
mcp_server = MCPServer()

@app.get("/")
async def root():
    return {
        "name": "Financial MCP Server",
        "version": "1.0.0",
        "tools": list(mcp_server.tools.keys()),
        "description": "MCP server for financial data and sentiment analysis"
    }

@app.get("/mcp/tools")
async def list_tools():
    """List all available MCP tools"""
    return {
        "tools": [
            {
                "name": name,
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
            for name, tool in mcp_server.tools.items()
        ]
    }

@app.post("/mcp/tools/{tool_name}")
async def call_tool(tool_name: str, parameters: Dict = {}):
    """Call an MCP tool with parameters"""
    if tool_name not in mcp_server.tools:
        raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
    
    try:
        handler = mcp_server.tools[tool_name]["handler"]
        result = await handler(**parameters)
        return result
    except Exception as e:
        return {"success": False, "error": str(e), "tool": tool_name}


# ==================== EXAMPLE USAGE ====================
async def example_usage():
    """Example of using MCP client to get data and sentiment"""
    
    # Initialize MCP client
    async with MCPClient() as client:
        
        # Get Apple stock data with sentiment
        print("Fetching AAPL data with sentiment...")
        result = await client.get_stock_data_with_sentiment("AAPL")
        
        print(f"Current Price: ${result['current'].get('price', 'N/A')}")
        print(f"Sentiment: {result['sentiment'].get('overall_sentiment', 'N/A')}")
        
        # Analyze specific news
        news_text = "Apple reported record earnings beating analyst expectations"
        sentiment = await client.call_tool("analyze_sentiment", {
            "text": news_text,
            "context": "earnings"
        })
        print(f"News Sentiment: {sentiment.get('sentiment')} "
              f"(confidence: {sentiment.get('confidence', 0):.2%})")


if __name__ == "__main__":
    import sys
    
    if "--example" in sys.argv:
        # Run example
        asyncio.run(example_usage())
    else:
        # Start MCP server
        print("\n" + "="*60)
        print("FINANCIAL MCP SERVER")
        print("="*60)
        print("📊 Features:")
        print("  • Alpha Vantage market data integration")
        print("  • FinBERT sentiment analysis")
        print("  • Technical indicators calculation")
        print("  • ML model training and prediction")
        print("\n🚀 Starting MCP server on http://localhost:8001")
        print("\nAvailable tools:")
        for tool in mcp_server.tools:
            print(f"  • {tool}")
        print("="*60 + "\n")
        
        uvicorn.run(app, host="0.0.0.0", port=8001)