"""
Orchestrator Backend - Loads and coordinates ALL original modules
This connects to all the enhanced separate services you created
Requires all original Python files to be running
"""

import os
import sys
import asyncio
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import httpx
import json
from typing import Dict, Any, Optional

# Add current directory to path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Stock Tracker Orchestrator", version="1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service endpoints - connects to your original modules
SERVICES = {
    "ml": "http://localhost:8002",           # ml_backend_enhanced_finbert.py
    "finbert": "http://localhost:8003",       # finbert_backend.py
    "historical": "http://localhost:8004",    # historical_backend_sqlite.py
    "backtesting": "http://localhost:8005",   # backtesting_enhanced.py
    "scraper": "http://localhost:8006"        # enhanced_global_scraper.py
}

# Client for making requests to services
client = httpx.AsyncClient(timeout=60.0)

async def check_service_health(service_name: str, url: str) -> Dict[str, Any]:
    """Check if a service is healthy"""
    try:
        response = await client.get(f"{url}/health")
        if response.status_code == 200:
            return {"status": "online", "details": response.json()}
        else:
            return {"status": "error", "details": f"Status code: {response.status_code}"}
    except Exception as e:
        return {"status": "offline", "details": str(e)}

async def forward_request(service_url: str, method: str = "GET", 
                         endpoint: str = "", json_data: Optional[Dict] = None) -> Any:
    """Forward request to a service"""
    url = f"{service_url}{endpoint}"
    
    try:
        if method == "GET":
            response = await client.get(url)
        elif method == "POST":
            response = await client.post(url, json=json_data)
        elif method == "DELETE":
            response = await client.delete(url)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, 
                              detail=f"Service returned {response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"Error connecting to service: {e}")
        raise HTTPException(status_code=503, 
                          detail=f"Service unavailable: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    """Main entry point"""
    return HTMLResponse("""
    <html>
        <head><title>Stock Tracker Orchestrator</title></head>
        <body>
            <h1>Stock Tracker Orchestrator</h1>
            <p>This backend orchestrates all your enhanced modules:</p>
            <ul>
                <li>ML Backend with FinBERT (Port 8002)</li>
                <li>Document Analyzer (Port 8003)</li>
                <li>Historical Data with SQLite (Port 8004)</li>
                <li>Backtesting Engine (Port 8005)</li>
                <li>Global Sentiment Scraper (Port 8006)</li>
            </ul>
            <p><strong>Status:</strong> <span id="status">Checking services...</span></p>
            <p><a href="/prediction_center_fixed.html">Open Prediction Center</a></p>
            <script>
                fetch('/api/services/status')
                    .then(r => r.json())
                    .then(data => {
                        let online = 0;
                        for (let service in data) {
                            if (data[service].status === 'online') online++;
                        }
                        document.getElementById('status').innerText = 
                            online + ' of 5 services online';
                    });
            </script>
        </body>
    </html>
    """)

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "orchestrator": "online"}

@app.get("/api/services/status")
async def services_status():
    """Check all services status"""
    status = {}
    for service_name, service_url in SERVICES.items():
        status[service_name] = await check_service_health(service_name, service_url)
    return status

# Forward ML endpoints to ml_backend_enhanced_finbert.py
@app.post("/train")
async def train(request: Request):
    """Forward to ML backend for training"""
    json_data = await request.json()
    return await forward_request(SERVICES["ml"], "POST", "/train", json_data)

@app.post("/predict")
async def predict(request: Request):
    """Forward to ML backend for prediction"""
    json_data = await request.json()
    return await forward_request(SERVICES["ml"], "POST", "/predict", json_data)

@app.get("/models/{symbol}")
async def get_models(symbol: str):
    """Forward to ML backend"""
    return await forward_request(SERVICES["ml"], "GET", f"/models/{symbol}")

# Forward historical data endpoints to historical_backend_sqlite.py
@app.post("/api/historical")
async def get_historical(request: Request):
    """Forward to historical backend"""
    json_data = await request.json()
    return await forward_request(SERVICES["historical"], "POST", "/historical", json_data)

@app.post("/api/analysis")
async def analyze(request: Request):
    """Forward to historical backend"""
    json_data = await request.json()
    return await forward_request(SERVICES["historical"], "POST", "/analysis", json_data)

@app.get("/api/patterns/{symbol}")
async def get_patterns(symbol: str):
    """Forward to historical backend"""
    return await forward_request(SERVICES["historical"], "GET", f"/patterns/{symbol}")

@app.get("/api/indicators/{symbol}")
async def get_indicators(symbol: str):
    """Calculate indicators using historical service"""
    analysis = await forward_request(
        SERVICES["historical"], 
        "POST", 
        "/analysis",
        {"symbol": symbol, "analysis_types": ["trend", "volatility"], "period": "3mo"}
    )
    
    if analysis and "trend_analysis" in analysis:
        trend = analysis["trend_analysis"]
        volatility = analysis.get("volatility_analysis", {})
        
        return {
            "symbol": symbol,
            "indicators": {
                "rsi": volatility.get("current_volatility"),
                "macd": trend.get("macd"),
                "macd_signal": trend.get("macd_signal"),
                "sma_20": trend.get("sma_20"),
                "sma_50": trend.get("sma_50"),
                "sma_200": trend.get("sma_200"),
                "atr": trend.get("atr"),
                "current_price": analysis.get("metadata", {}).get("current_price")
            },
            "interpretation": [
                f"Trend: {trend.get('trend', 'unknown')}",
                f"Trend Strength: {trend.get('trend_strength', 0):.1f}%",
                f"Volatility Regime: {volatility.get('volatility_regime', 'normal')}"
            ]
        }
    
    raise HTTPException(status_code=503, detail="Analysis service unavailable")

# Forward sentiment endpoints to enhanced_global_scraper.py
@app.post("/scrape")
async def scrape(request: Request):
    """Forward to scraper backend"""
    json_data = await request.json()
    return await forward_request(SERVICES["scraper"], "POST", "/scrape", json_data)

@app.get("/api/sentiment/{symbol}")
async def get_sentiment(symbol: str):
    """Get sentiment from scraper"""
    result = await forward_request(
        SERVICES["scraper"], 
        "POST", 
        "/scrape",
        {"symbol": symbol, "include_global": True}
    )
    return result

@app.get("/api/global-sentiment")
async def global_sentiment():
    """Forward to scraper backend"""
    return await forward_request(SERVICES["scraper"], "GET", "/global-sentiment")

@app.get("/api/market-risk")
async def market_risk():
    """Forward to scraper backend"""
    return await forward_request(SERVICES["scraper"], "GET", "/market-risk")

# Forward backtesting endpoints to backtesting_enhanced.py
@app.post("/backtest")
async def backtest(request: Request):
    """Forward to backtesting backend"""
    json_data = await request.json()
    return await forward_request(SERVICES["backtesting"], "POST", "/backtest", json_data)

@app.get("/api/backtest/results/{symbol}")
async def backtest_results(symbol: str):
    """Forward to backtesting backend"""
    return await forward_request(SERVICES["backtesting"], "GET", f"/results/{symbol}")

# Forward document analysis to finbert_backend.py
@app.post("/api/analyze-document")
async def analyze_document(request: Request):
    """Forward to FinBERT document analyzer"""
    json_data = await request.json()
    return await forward_request(SERVICES["finbert"], "POST", "/analyze", json_data)

# Serve HTML files
@app.get("/{filename}")
async def serve_file(filename: str):
    """Serve HTML files"""
    if os.path.exists(filename) and filename.endswith('.html'):
        return FileResponse(filename)
    raise HTTPException(status_code=404, detail="File not found")

# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown():
    """Cleanup"""
    await client.aclose()

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("STOCK TRACKER ORCHESTRATOR")
    print("="*70)
    print("This orchestrator connects to your original enhanced modules:")
    print("  • ML Backend (8002) - ml_backend_enhanced_finbert.py")
    print("  • FinBERT (8003) - finbert_backend.py")
    print("  • Historical (8004) - historical_backend_sqlite.py")
    print("  • Backtesting (8005) - backtesting_enhanced.py")
    print("  • Scraper (8006) - enhanced_global_scraper.py")
    print("="*70)
    print("Make sure all services are running first!")
    print("Use START_ALL_SERVICES.bat to start them")
    print("="*70)
    print("Orchestrator starting on http://localhost:8000")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)