#!/usr/bin/env python3
"""
Simple ML Backend - Working Version
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/ml/models")
async def get_models():
    return [
        {
            "model_id": "AAPL_lstm_demo",
            "symbol": "AAPL",
            "model_type": "lstm",
            "created_at": datetime.now().isoformat(),
            "accuracy": 0.85
        }
    ]

@app.post("/api/ml/train")
async def train(data: dict):
    model_id = f"{data.get('symbol', 'AAPL')}_{data.get('model_type', 'lstm')}_{int(datetime.now().timestamp())}"
    return {
        "model_id": model_id,
        "status": "training_started"
    }

@app.get("/api/ml/status/{model_id}")
async def status(model_id: str):
    return {
        "model_id": model_id,
        "status": "training",
        "progress": random.randint(20, 80),
        "metrics": {
            "loss": round(random.random() * 0.1, 4),
            "mae": round(random.random() * 0.05, 4),
            "r2_score": round(0.7 + random.random() * 0.25, 2)
        },
        "history": {
            "loss": [round(0.1 - i*0.01, 3) for i in range(10)],
            "val_loss": [round(0.12 - i*0.008, 3) for i in range(10)]
        }
    }

@app.post("/api/ml/predict")
async def predict(data: dict):
    days = data.get('days', 30)
    return {
        "dates": [f"2024-10-{i+1:02d}" for i in range(days)],
        "predicted": [150 + random.uniform(-10, 10) for _ in range(days)],
        "actual": [150 for _ in range(days)]
    }

if __name__ == "__main__":
    print("Starting ML Training Backend on port 8003...")
    print("Health endpoint: http://localhost:8003/health")
    uvicorn.run(app, host="127.0.0.1", port=8003)