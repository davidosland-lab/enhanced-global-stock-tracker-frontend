#!/usr/bin/env python3
"""
Fixed ML Training Backend - Handles port conflicts
"""

import os
import sys
import socket
import logging
from datetime import datetime

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="ML Training Backend (Fixed)", version="1.0.1")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def is_port_free(port):
    """Check if a port is free"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('', port))
            return True
        except:
            return False

def find_free_port(start_port=8003, max_attempts=10):
    """Find a free port starting from start_port"""
    for i in range(max_attempts):
        port = start_port + i
        if is_port_free(port):
            return port
    return None

@app.get("/")
async def root():
    return {
        "message": "ML Training Backend (Fixed) is running",
        "status": "online",
        "version": "1.0.1",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ml-training-backend",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/ml/train")
async def train_model(request: dict):
    """Simplified training endpoint"""
    try:
        symbol = request.get("symbol", "AAPL")
        model_type = request.get("model_type", "lstm")
        
        # Simulated response for now
        return {
            "model_id": f"{symbol}_{model_type}_{datetime.now().timestamp()}",
            "status": "training_started",
            "message": f"Training {model_type} model for {symbol}",
            "estimated_time": "2-5 minutes"
        }
    except Exception as e:
        logger.error(f"Training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/status/{model_id}")
async def get_training_status(model_id: str):
    """Get training status"""
    return {
        "model_id": model_id,
        "status": "training",
        "progress": 45,
        "metrics": {
            "loss": 0.0234,
            "mae": 0.0156,
            "r2_score": 0.82
        }
    }

@app.get("/api/ml/models")
async def list_models():
    """List available models"""
    return [
        {
            "model_id": "AAPL_lstm_sample",
            "symbol": "AAPL",
            "model_type": "lstm",
            "created_at": datetime.now().isoformat(),
            "accuracy": 0.85
        }
    ]

@app.post("/api/ml/predict")
async def predict(request: dict):
    """Generate predictions"""
    model_id = request.get("model_id")
    days = request.get("days", 30)
    
    # Simulated prediction
    import random
    base_price = 150 + random.random() * 10
    
    predictions = []
    dates = []
    for i in range(days):
        price = base_price * (1 + (random.random() - 0.5) * 0.02)
        predictions.append(price)
        dates.append(f"2024-10-{6+i:02d}")
    
    return {
        "model_id": model_id,
        "dates": dates,
        "predicted": predictions,
        "actual": [base_price] * days
    }

if __name__ == "__main__":
    # Try to find a free port
    port = find_free_port(8003)
    
    if port is None:
        logger.error("No free ports available between 8003-8013")
        sys.exit(1)
    
    if port != 8003:
        logger.warning(f"Port 8003 was busy, using port {port} instead")
        print(f"\n⚠️  ML Backend running on different port: http://localhost:{port}")
        print(f"⚠️  Update your frontend to use port {port} instead of 8003\n")
    
    logger.info(f"Starting ML Training Backend on port {port}")
    
    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=port,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)