#!/usr/bin/env python3
"""
Dashboard API Endpoints for Performance Tracking and Monitoring
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import numpy as np
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# Import performance tracker if available
try:
    from enhanced_performance_tracker import performance_tracker
    TRACKER_AVAILABLE = True
except ImportError:
    logger.warning("Enhanced performance tracker not available")
    TRACKER_AVAILABLE = False


@router.get("/comprehensive-data")
async def get_comprehensive_dashboard_data(
    timeframe: str = Query("24h", description="Timeframe: 1h, 24h, 7d, 30d"),
    model_filter: str = Query("all", description="Filter by model type")
) -> Dict[str, Any]:
    """
    Get comprehensive dashboard data including predictions, performance metrics, and learning progress
    """
    
    # Convert timeframe to hours
    timeframe_hours = {
        "1h": 1,
        "24h": 24,
        "7d": 168,
        "30d": 720
    }.get(timeframe, 24)
    
    # Generate sample data (in production, fetch from database)
    current_time = datetime.utcnow()
    
    # Model performance data
    models = ["lstm", "gru", "transformer", "ensemble", "gnn", "advanced_ensemble"]
    if model_filter != "all":
        models = [m for m in models if model_filter.lower() in m.lower()]
    
    model_performance = {}
    for model in models:
        model_performance[model] = {
            "accuracy": random.uniform(0.65, 0.85),
            "precision": random.uniform(0.60, 0.82),
            "recall": random.uniform(0.58, 0.80),
            "f1_score": random.uniform(0.62, 0.81),
            "total_predictions": random.randint(100, 1000),
            "correct_predictions": random.randint(60, 850),
            "confidence_calibration": random.uniform(0.70, 0.95)
        }
    
    # Recent predictions
    recent_predictions = []
    symbols = ["CBA.AX", "BHP.AX", "WBC.AX", "ANZ.AX", "CSL.AX", "RIO.AX"]
    
    for i in range(20):
        pred_time = current_time - timedelta(minutes=i * 30)
        recent_predictions.append({
            "timestamp": pred_time.isoformat(),
            "symbol": random.choice(symbols),
            "model": random.choice(models),
            "predicted_direction": random.choice(["up", "down", "sideways"]),
            "actual_direction": random.choice(["up", "down", "sideways", None]),
            "confidence": random.uniform(0.5, 0.95),
            "error": random.uniform(0, 5) if random.random() > 0.3 else None,
            "correct": random.choice([True, False, None])
        })
    
    # Accuracy over time
    accuracy_timeline = []
    for i in range(24):  # 24 data points
        time_point = current_time - timedelta(hours=timeframe_hours * (1 - i/24))
        accuracy_timeline.append({
            "timestamp": time_point.isoformat(),
            "accuracy": random.uniform(0.60, 0.85),
            "predictions_count": random.randint(5, 50)
        })
    
    # Model comparison
    model_comparison = []
    for model in models:
        model_comparison.append({
            "model": model,
            "accuracy": random.uniform(0.65, 0.85),
            "avg_confidence": random.uniform(0.60, 0.90),
            "total_predictions": random.randint(100, 1000),
            "mse": random.uniform(0.001, 0.05),
            "mae": random.uniform(0.01, 0.1)
        })
    
    # Summary statistics
    total_predictions = sum(m["total_predictions"] for m in model_performance.values())
    total_correct = sum(m["correct_predictions"] for m in model_performance.values())
    overall_accuracy = total_correct / total_predictions if total_predictions > 0 else 0
    
    # Get real performance data if tracker is available
    if TRACKER_AVAILABLE and performance_tracker:
        try:
            real_performance = performance_tracker.get_comparative_analysis()
            if real_performance and real_performance != {'status': 'no_data'}:
                model_performance.update(real_performance.get('model_comparison', {}))
                overall_accuracy = real_performance.get('best_accuracy', overall_accuracy)
        except Exception as e:
            logger.warning(f"Could not get real performance data: {e}")
    
    return {
        "timestamp": current_time.isoformat(),
        "timeframe": timeframe,
        "summary": {
            "total_predictions": total_predictions,
            "overall_accuracy": overall_accuracy,
            "active_models": len(models),
            "best_model": max(model_performance.keys(), 
                            key=lambda k: model_performance[k].get('accuracy', 0)),
            "avg_confidence": np.mean([m.get('confidence_calibration', 0.8) 
                                      for m in model_performance.values()])
        },
        "model_performance": model_performance,
        "recent_predictions": recent_predictions,
        "accuracy_timeline": accuracy_timeline,
        "model_comparison": model_comparison,
        "status": "success"
    }


@router.get("/learning-progress")
async def get_learning_progress(
    episodes: int = Query(50, description="Number of episodes to retrieve")
) -> Dict[str, Any]:
    """
    Get reinforcement learning progress data
    """
    
    # Generate sample RL learning progress
    learning_data = []
    base_performance = 0.5
    
    for episode in range(episodes):
        # Simulate improving performance
        performance = base_performance + (0.4 * (1 - np.exp(-episode / 20)))
        performance += random.uniform(-0.05, 0.05)  # Add noise
        
        learning_data.append({
            "episode": episode + 1,
            "reward": random.uniform(-10, 50),
            "performance": min(0.95, max(0.4, performance)),
            "exploration_rate": max(0.01, 1.0 * np.exp(-episode / 15)),
            "loss": max(0.01, 0.5 * np.exp(-episode / 10) + random.uniform(0, 0.1))
        })
    
    # Model weights evolution
    model_weights = {
        "lstm": [],
        "gru": [],
        "transformer": [],
        "ensemble": [],
        "gnn": []
    }
    
    for episode in range(0, episodes, 5):
        weights = np.random.dirichlet(np.ones(5))
        for i, model in enumerate(model_weights.keys()):
            model_weights[model].append({
                "episode": episode + 1,
                "weight": float(weights[i])
            })
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "total_episodes": episodes,
        "learning_curve": learning_data,
        "model_weights_evolution": model_weights,
        "current_performance": learning_data[-1]["performance"] if learning_data else 0,
        "convergence_status": "converged" if episodes > 30 else "training",
        "status": "success"
    }


@router.get("/real-time-metrics")
async def get_real_time_metrics() -> Dict[str, Any]:
    """
    Get real-time performance metrics
    """
    
    current_metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "active_predictions": random.randint(5, 20),
        "models_online": random.randint(4, 6),
        "avg_latency_ms": random.uniform(100, 500),
        "throughput_per_min": random.randint(10, 50),
        "error_rate": random.uniform(0, 0.05),
        "cache_hit_rate": random.uniform(0.7, 0.95)
    }
    
    # Add real tracker data if available
    if TRACKER_AVAILABLE and performance_tracker:
        try:
            performance = performance_tracker.get_model_performance()
            current_metrics["tracked_models"] = list(performance.keys())
            current_metrics["total_tracked_predictions"] = sum(
                m.get('total_predictions', 0) for m in performance.values() 
                if isinstance(m, dict)
            )
        except Exception as e:
            logger.warning(f"Could not get tracker metrics: {e}")
    
    return current_metrics


@router.get("/alerts")
async def get_system_alerts() -> Dict[str, Any]:
    """
    Get system alerts and notifications
    """
    
    alerts = []
    
    # Generate sample alerts
    if random.random() > 0.7:
        alerts.append({
            "level": "warning",
            "message": "Model accuracy below threshold",
            "details": "LSTM model accuracy dropped to 62%",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    if random.random() > 0.8:
        alerts.append({
            "level": "info",
            "message": "New model training completed",
            "details": "GNN model retrained with latest data",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    return {
        "alerts": alerts,
        "total_alerts": len(alerts),
        "status": "success"
    }


# Export router
__all__ = ["router"]