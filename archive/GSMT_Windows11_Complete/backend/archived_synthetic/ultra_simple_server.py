#!/usr/bin/env python3
"""
Ultra Simple Server - Guaranteed to Work
This is the simplest possible server with no external dependencies except FastAPI
"""

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse
    import uvicorn
    print("✓ FastAPI imported successfully")
except ImportError as e:
    print(f"ERROR: {e}")
    print("\nPlease install FastAPI and Uvicorn:")
    print("  pip install fastapi uvicorn")
    input("\nPress Enter to exit...")
    exit(1)

# Create app
app = FastAPI(title="GSMT Simple Server")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/", response_class=HTMLResponse)
def home():
    """Home page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>GSMT Server</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #1a1a1a; color: white; }
            h1 { color: #4CAF50; }
            .box { background: #2a2a2a; padding: 20px; border-radius: 10px; margin: 20px 0; }
            a { color: #4CAF50; text-decoration: none; display: block; margin: 10px 0; }
            .success { color: #4CAF50; font-size: 24px; }
        </style>
    </head>
    <body>
        <h1>✓ GSMT Server is Running!</h1>
        <div class="box">
            <p class="success">Success! The server is working correctly.</p>
            <p>FastAPI Version: Working</p>
            <p>Server Status: Active</p>
        </div>
        <div class="box">
            <h2>Test These Endpoints:</h2>
            <a href="/health">→ /health - Health Check</a>
            <a href="/api/tracker">→ /api/tracker - Stock Data</a>
            <a href="/api/test">→ /api/test - Test Endpoint</a>
        </div>
    </body>
    </html>
    """
    return html

@app.get("/health")
def health():
    """Health check"""
    return {"status": "healthy", "server": "GSMT Ultra Simple", "working": True}

@app.get("/api/tracker")
def tracker():
    """Mock tracker data"""
    return {
        "status": "success",
        "data": [
            {"symbol": "AAPL", "price": 150.25, "change": 2.30},
            {"symbol": "GOOGL", "price": 2750.80, "change": -15.20},
            {"symbol": "MSFT", "price": 380.50, "change": 5.10}
        ]
    }

@app.get("/api/test")
def test():
    """Test endpoint"""
    return {"message": "Test successful!", "working": True}

@app.get("/api/predict/{symbol}")
def predict(symbol: str):
    """Simple prediction"""
    import random
    price = 100 + random.random() * 400
    prediction = price * (1 + random.uniform(-0.05, 0.05))
    return {
        "symbol": symbol.upper(),
        "current_price": round(price, 2),
        "prediction": round(prediction, 2),
        "confidence": round(random.uniform(0.6, 0.9), 2)
    }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("    GSMT ULTRA SIMPLE SERVER")
    print("="*60)
    print("\nStarting server on: http://localhost:8000")
    print("\nTest URLs:")
    print("  http://localhost:8000")
    print("  http://localhost:8000/health")
    print("  http://localhost:8000/api/tracker")
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")
    
    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000)