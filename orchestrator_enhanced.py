"""
Enhanced Orchestrator Backend - Complete Service Integration
Integrates all backend services including new indices and performance trackers
Port: 8000
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore')

# FastAPI imports
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# HTTP client
import aiohttp
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Enhanced Orchestrator", version="2.0")

# CORS middleware - allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service registry with all backend services
SERVICES = {
    "ml": {
        "url": "http://localhost:8002",
        "name": "ML Backend with FinBERT",
        "endpoints": ["/train", "/predict", "/models"]
    },
    "finbert": {
        "url": "http://localhost:8003",
        "name": "FinBERT Document Analyzer",
        "endpoints": ["/analyze", "/analyze_document"]
    },
    "historical": {
        "url": "http://localhost:8004",
        "name": "Historical Data with SQLite",
        "endpoints": ["/historical", "/patterns", "/correlations"]
    },
    "backtesting": {
        "url": "http://localhost:8005",
        "name": "Backtesting Engine",
        "endpoints": ["/backtest", "/strategies"]
    },
    "scraper": {
        "url": "http://localhost:8006",
        "name": "Global Sentiment Scraper",
        "endpoints": ["/scrape", "/sources", "/market_risk"]
    },
    "indices": {
        "url": "http://localhost:8007",
        "name": "Indices Tracker",
        "endpoints": ["/indices", "/sectors", "/correlations", "/market_breadth"]
    },
    "cba": {
        "url": "http://localhost:8008",
        "name": "CBA Specialist Analysis",
        "endpoints": ["/cba_analysis", "/asx_data", "/banking_sector"]
    },
    "social": {
        "url": "http://localhost:8009",
        "name": "Social Sentiment Tracker",
        "endpoints": ["/reddit", "/twitter", "/stocktwits", "/trending"]
    },
    "performance": {
        "url": "http://localhost:8010",
        "name": "Performance Tracker",
        "endpoints": ["/prediction_accuracy", "/model_performance", "/performance_summary"]
    }
}

# Health check cache
service_health = {}
last_health_check = datetime.now()

async def check_service_health(service_name: str, service_config: Dict) -> bool:
    """Check if a service is healthy"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{service_config['url']}/", timeout=2) as response:
                return response.status == 200
    except:
        return False

async def update_service_health():
    """Update health status of all services"""
    global service_health, last_health_check
    
    # Only check every 30 seconds
    if (datetime.now() - last_health_check).seconds < 30:
        return service_health
    
    for name, config in SERVICES.items():
        service_health[name] = await check_service_health(name, config)
    
    last_health_check = datetime.now()
    return service_health

@app.get("/")
async def root():
    """Root endpoint with service status"""
    health = await update_service_health()
    
    return {
        "message": "Enhanced Orchestrator Backend",
        "version": "2.0",
        "port": 8000,
        "services": {
            name: {
                "url": config["url"],
                "name": config["name"],
                "status": "online" if health.get(name, False) else "offline",
                "endpoints": config["endpoints"]
            }
            for name, config in SERVICES.items()
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    """Comprehensive health check of all services"""
    health = await update_service_health()
    
    total_services = len(SERVICES)
    online_services = sum(1 for status in health.values() if status)
    
    return {
        "status": "healthy" if online_services > total_services * 0.6 else "degraded",
        "services_online": online_services,
        "services_total": total_services,
        "service_status": {
            name: "online" if health.get(name, False) else "offline"
            for name in SERVICES.keys()
        },
        "timestamp": datetime.now().isoformat()
    }

# Proxy endpoints for ML service
@app.post("/api/train")
async def proxy_train(request: Request):
    """Proxy training requests to ML backend"""
    try:
        body = await request.json()
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVICES['ml']['url']}/train", json=body) as response:
                result = await response.json()
                
                # Record training in performance tracker
                if "performance" in service_health and service_health["performance"]:
                    try:
                        perf_data = {
                            "model_type": body.get("model_type", "RandomForest"),
                            "symbol": body.get("symbol", "Unknown"),
                            "training_date": datetime.now().isoformat(),
                            "training_samples": result.get("training_samples", 0),
                            "features_count": result.get("features_count", 0),
                            "mse": result.get("mse", 0),
                            "rmse": result.get("rmse", 0),
                            "mae": result.get("mae", 0),
                            "r2": result.get("r2", 0),
                            "training_time": result.get("training_time", 0)
                        }
                        async with session.post(f"{SERVICES['performance']['url']}/api/record_training", 
                                               json=perf_data) as perf_response:
                            pass
                    except:
                        pass  # Don't fail if performance tracking fails
                
                return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict")
async def proxy_predict(request: Request):
    """Proxy prediction requests to ML backend"""
    try:
        body = await request.json()
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVICES['ml']['url']}/predict", json=body) as response:
                result = await response.json()
                
                # Record prediction in performance tracker
                if "performance" in service_health and service_health["performance"]:
                    try:
                        perf_data = {
                            "symbol": body.get("symbol", "Unknown"),
                            "predicted_price": result.get("prediction", 0),
                            "prediction_date": datetime.now().isoformat(),
                            "target_date": result.get("target_date", datetime.now().isoformat()),
                            "model_type": body.get("model_type", "RandomForest"),
                            "confidence": result.get("confidence", 0),
                            "sentiment_score": result.get("sentiment_score", 0)
                        }
                        async with session.post(f"{SERVICES['performance']['url']}/api/record_prediction", 
                                               json=perf_data) as perf_response:
                            pass
                    except:
                        pass
                
                return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Proxy endpoints for Historical service
@app.get("/api/historical/{symbol}")
async def proxy_historical(symbol: str, period: str = "1mo", interval: str = "1d"):
    """Proxy historical data requests"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{SERVICES['historical']['url']}/api/historical/{symbol}",
                params={"period": period, "interval": interval}
            ) as response:
                return await response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Proxy endpoints for Indices service
@app.get("/api/indices")
async def proxy_indices():
    """Get all major indices data"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVICES['indices']['url']}/api/indices") as response:
                return await response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/index/{symbol}")
async def proxy_index(symbol: str, period: str = "1mo", interval: str = "1d"):
    """Get specific index data"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{SERVICES['indices']['url']}/api/index/{symbol}",
                params={"period": period, "interval": interval}
            ) as response:
                return await response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sectors")
async def proxy_sectors():
    """Get sector performance"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVICES['indices']['url']}/api/sectors") as response:
                return await response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market_breadth")
async def proxy_market_breadth():
    """Get market breadth indicators"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVICES['indices']['url']}/api/market_breadth") as response:
                return await response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Proxy endpoints for Performance tracker
@app.get("/api/performance/accuracy")
async def proxy_performance_accuracy(symbol: Optional[str] = None, days: int = 30):
    """Get prediction accuracy statistics"""
    try:
        async with aiohttp.ClientSession() as session:
            params = {"days": days}
            if symbol:
                params["symbol"] = symbol
            async with session.get(
                f"{SERVICES['performance']['url']}/api/prediction_accuracy",
                params=params
            ) as response:
                return await response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/performance/models")
async def proxy_performance_models(model_type: Optional[str] = None, days: int = 30):
    """Get model performance statistics"""
    try:
        async with aiohttp.ClientSession() as session:
            params = {"days": days}
            if model_type:
                params["model_type"] = model_type
            async with session.get(
                f"{SERVICES['performance']['url']}/api/model_performance",
                params=params
            ) as response:
                return await response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/performance/summary")
async def proxy_performance_summary(days: int = 30):
    """Get overall performance summary"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{SERVICES['performance']['url']}/api/performance_summary",
                params={"days": days}
            ) as response:
                return await response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Proxy endpoints for Global Sentiment
@app.get("/api/sentiment/global")
async def proxy_global_sentiment():
    """Get global sentiment analysis"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVICES['scraper']['url']}/api/scrape") as response:
                return await response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sentiment/sources")
async def proxy_sentiment_sources():
    """Get sentiment sources"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVICES['scraper']['url']}/api/sources") as response:
                return await response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Proxy endpoints for Backtesting
@app.post("/api/backtest")
async def proxy_backtest(request: Request):
    """Run backtesting"""
    try:
        body = await request.json()
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{SERVICES['backtesting']['url']}/api/backtest", json=body) as response:
                result = await response.json()
                
                # Record backtest in performance tracker
                if "performance" in service_health and service_health["performance"] and result.get("status") == "success":
                    try:
                        perf_data = {
                            "strategy": body.get("strategy", "Unknown"),
                            "symbol": body.get("symbol", "Unknown"),
                            "start_date": body.get("start_date", ""),
                            "end_date": body.get("end_date", ""),
                            "initial_capital": body.get("initial_capital", 100000),
                            "final_value": result.get("final_value", 0),
                            "total_return": result.get("total_return", 0),
                            "sharpe_ratio": result.get("sharpe_ratio", 0),
                            "max_drawdown": result.get("max_drawdown", 0),
                            "win_rate": result.get("win_rate", 0),
                            "total_trades": result.get("total_trades", 0)
                        }
                        async with session.post(f"{SERVICES['performance']['url']}/api/record_backtest", 
                                               json=perf_data) as perf_response:
                            pass
                    except:
                        pass
                
                return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Combined endpoints for dashboard
@app.get("/api/dashboard/overview")
async def get_dashboard_overview():
    """Get combined dashboard data"""
    try:
        overview = {
            "timestamp": datetime.now().isoformat(),
            "services_status": await update_service_health()
        }
        
        # Gather data from multiple services in parallel
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # Get indices data
            if service_health.get("indices", False):
                tasks.append(session.get(f"{SERVICES['indices']['url']}/api/indices"))
            
            # Get global sentiment
            if service_health.get("scraper", False):
                tasks.append(session.get(f"{SERVICES['scraper']['url']}/api/market_risk"))
            
            # Get performance summary
            if service_health.get("performance", False):
                tasks.append(session.get(f"{SERVICES['performance']['url']}/api/performance_summary?days=7"))
            
            # Execute all tasks
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process responses
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    continue
                try:
                    data = await response.json()
                    if i == 0:  # Indices
                        overview["indices"] = data
                    elif i == 1:  # Sentiment
                        overview["global_sentiment"] = data
                    elif i == 2:  # Performance
                        overview["performance"] = data
                except:
                    continue
        
        return overview
        
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {str(e)}")
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

# Serve HTML files
@app.get("/index")
async def serve_index():
    """Serve main index.html"""
    file_path = "index.html"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return HTMLResponse(content="<h1>Index file not found</h1>", status_code=404)

@app.get("/prediction")
async def serve_prediction():
    """Serve prediction center"""
    file_path = "prediction_center_fixed.html"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return HTMLResponse(content="<h1>Prediction center not found</h1>", status_code=404)

# Service management endpoints
@app.post("/api/services/restart/{service_name}")
async def restart_service(service_name: str):
    """Restart a specific service (placeholder for actual implementation)"""
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
    
    # In production, this would actually restart the service
    # For now, just return success
    return {
        "status": "success",
        "message": f"Service {service_name} restart initiated",
        "service": SERVICES[service_name]["name"]
    }

@app.get("/api/services/logs/{service_name}")
async def get_service_logs(service_name: str, lines: int = 100):
    """Get logs for a specific service (placeholder)"""
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
    
    # In production, this would read actual log files
    return {
        "service": service_name,
        "logs": f"Last {lines} lines of logs for {SERVICES[service_name]['name']}",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    port = 8000
    logger.info(f"Starting Enhanced Orchestrator on port {port}...")
    logger.info("Registered services:")
    for name, config in SERVICES.items():
        logger.info(f"  - {name}: {config['name']} at {config['url']}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)