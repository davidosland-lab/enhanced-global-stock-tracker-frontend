#!/usr/bin/env python3
"""
Minimal ML Backend for Stock Tracker
This version has minimal dependencies and should always work
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import random
import json
from typing import List, Dict, Optional, Any

# Create FastAPI app
app = FastAPI(title="ML Backend (Minimal)")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
trained_models = {}
training_sessions = {}

# Request models
class TrainingRequest(BaseModel):
    symbol: str
    model_type: str = "lstm"
    epochs: int = 50
    batch_size: int = 32
    learning_rate: float = 0.001
    sequence_length: int = 60

class PredictionRequest(BaseModel):
    symbol: str
    model_id: Optional[str] = None
    timeframe: str = "30d"
    models: Optional[List[str]] = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ML Backend (Minimal)",
        "version": "1.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/ml/status")
async def ml_status():
    """Get ML backend status"""
    return {
        "status": "operational",
        "models_loaded": len(trained_models),
        "active_training": len(training_sessions),
        "backend_type": "minimal",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/ml/train")
async def train_model(request: TrainingRequest):
    """Start model training (simulated)"""
    import uuid
    
    training_id = str(uuid.uuid4())
    model_id = f"model_{training_id[:8]}"
    
    # Store training session
    training_sessions[training_id] = {
        "id": training_id,
        "model_id": model_id,
        "symbol": request.symbol,
        "model_type": request.model_type,
        "status": "training",
        "progress": 0,
        "epochs": request.epochs,
        "started_at": datetime.now().isoformat()
    }
    
    # Simulate trained model (immediately complete for minimal version)
    trained_models[model_id] = {
        "id": model_id,
        "name": f"Minimal {request.model_type.upper()} - {request.symbol}",
        "symbol": request.symbol,
        "model_type": request.model_type,
        "accuracy": 0.85 + random.random() * 0.1,  # 85-95% accuracy
        "training_completed": datetime.now().isoformat(),
        "parameters": {
            "epochs": request.epochs,
            "batch_size": request.batch_size,
            "learning_rate": request.learning_rate
        }
    }
    
    return {
        "message": "Training started",
        "training_id": training_id,
        "model_id": model_id
    }

@app.get("/api/ml/training/status/{training_id}")
async def get_training_status(training_id: str):
    """Get training status"""
    if training_id not in training_sessions:
        # Return completed status for unknown sessions
        return {
            "status": "completed",
            "progress": 100,
            "message": "Training completed (simulated)"
        }
    
    session = training_sessions[training_id]
    
    # Simulate progress
    session["progress"] = min(100, session.get("progress", 0) + 20)
    if session["progress"] >= 100:
        session["status"] = "completed"
    
    return {
        "status": session["status"],
        "progress": session["progress"],
        "model_id": session.get("model_id"),
        "epochs": session.get("epochs", 50),
        "current_epoch": int(session["progress"] / 100 * session.get("epochs", 50))
    }

@app.get("/api/ml/models")
async def get_models():
    """Get list of trained models"""
    return {
        "models": list(trained_models.values()),
        "count": len(trained_models)
    }

@app.post("/api/ml/predict")
async def predict(request: PredictionRequest):
    """Generate predictions (simulated)"""
    base_price = 170 if request.symbol == "CBA.AX" else 100
    
    predictions = {}
    models_to_use = request.models if request.models else ["lstm", "random_forest"]
    
    for model in models_to_use:
        # Simulate predictions
        predictions[model] = base_price * (1 + random.uniform(-0.05, 0.15))
    
    return {
        "symbol": request.symbol,
        "current_price": base_price,
        "predictions": predictions,
        "timeframe": request.timeframe,
        "confidence": 0.75 + random.random() * 0.2,
        "timestamp": datetime.now().isoformat()
    }

@app.delete("/api/ml/models/{model_id}")
async def delete_model(model_id: str):
    """Delete a model"""
    if model_id in trained_models:
        del trained_models[model_id]
        return {"message": f"Model {model_id} deleted"}
    raise HTTPException(status_code=404, detail="Model not found")

if __name__ == "__main__":
    print("=" * 60)
    print("ML Backend (Minimal) - Starting on port 8003")
    print("=" * 60)
    print("This is a minimal version with reduced dependencies.")
    print("It provides simulated ML functionality for testing.")
    print()
    
    try:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8003)
    except ImportError:
        print("ERROR: uvicorn not installed!")
        print("Please run: pip install fastapi uvicorn")
        print()
        print("Or try using the built-in server:")
        print("python -m uvicorn ml_backend_minimal:app --host 0.0.0.0 --port 8003")