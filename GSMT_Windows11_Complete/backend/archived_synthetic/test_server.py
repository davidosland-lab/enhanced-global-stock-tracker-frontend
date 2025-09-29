#!/usr/bin/env python3
"""
Minimal test server to verify FastAPI is working
This is the most basic server that should definitely work
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from datetime import datetime

# Create FastAPI app
app = FastAPI(title="GSMT Test Server")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Main page"""
    return """
    <html>
        <head>
            <title>GSMT Test Server</title>
            <style>
                body { 
                    font-family: Arial; 
                    max-width: 800px; 
                    margin: 50px auto; 
                    padding: 20px;
                    background: #1a1a1a;
                    color: #fff;
                }
                h1 { color: #4CAF50; }
                .status { 
                    background: #2a2a2a; 
                    padding: 15px; 
                    border-radius: 5px; 
                    margin: 10px 0;
                }
                a { 
                    color: #4CAF50; 
                    text-decoration: none; 
                    display: block;
                    margin: 10px 0;
                }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>✅ GSMT Test Server is Running!</h1>
            <div class="status">
                <h2>Server Status: ACTIVE</h2>
                <p>FastAPI is working correctly!</p>
                <p>Time: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            </div>
            <h2>Available Endpoints:</h2>
            <a href="/health">→ Health Check</a>
            <a href="/docs">→ API Documentation</a>
            <a href="/test">→ Test Endpoint</a>
            <h3>What to do next:</h3>
            <ol>
                <li>If you see this page, FastAPI is working!</li>
                <li>Close this server (Ctrl+C)</li>
                <li>Run the main backend: python backend\\simple_ml_backend.py</li>
            </ol>
        </body>
    </html>
    """

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Test server is running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test")
async def test():
    """Test endpoint"""
    return {
        "message": "Test endpoint working!",
        "server": "GSMT Test Server",
        "working": True
    }

@app.get("/docs")
async def custom_docs():
    """Override docs to ensure it works"""
    return {"message": "API docs are available at /docs (this is a test response)"}

if __name__ == "__main__":
    print("\n" + "="*60)
    print("GSMT TEST SERVER")
    print("="*60)
    print("Starting test server on: http://localhost:8000")
    print("\nEndpoints to test:")
    print("  http://localhost:8000       - Main page")
    print("  http://localhost:8000/health - Health check")
    print("  http://localhost:8000/test   - Test endpoint")
    print("  http://localhost:8000/docs   - API docs")
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)