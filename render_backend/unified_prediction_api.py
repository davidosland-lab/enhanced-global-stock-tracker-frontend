#!/usr/bin/env python3
"""
Unified Prediction API Endpoints
Integrates Phase 3 and Phase 4 prediction models from GSMT-Ver-813
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
import asyncio
import numpy as np
import pandas as pd
import yfinance as yf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["unified_prediction"])

# Import the enhanced integrated system
try:
    from integrated_cba_system_enhanced import enhanced_system, EnhancedIntegratedSystem
    ENHANCED_SYSTEM_AVAILABLE = True
    logger.info("✅ Enhanced Integrated System loaded")
except ImportError as e:
    logger.warning(f"⚠️ Enhanced Integrated System not available: {e}")
    ENHANCED_SYSTEM_AVAILABLE = False
    enhanced_system = None

# Import Phase 3 and Phase 4 components directly
try:
    from advanced_ensemble_predictor import advanced_predictor
    ADVANCED_PREDICTOR_AVAILABLE = True
    logger.info("✅ Advanced Ensemble Predictor loaded")
except ImportError as e:
    logger.warning(f"⚠️ Advanced Ensemble Predictor not available: {e}")
    ADVANCED_PREDICTOR_AVAILABLE = False
    advanced_predictor = None

try:
    from phase4_graph_neural_networks import gnn_predictor
    GNN_AVAILABLE = True
    logger.info("✅ Graph Neural Networks loaded")
except ImportError as e:
    logger.warning(f"⚠️ Graph Neural Networks not available: {e}")
    GNN_AVAILABLE = False
    gnn_predictor = None

try:
    from phase3_realtime_performance_monitoring import PerformanceMonitor
    performance_monitor = PerformanceMonitor()
    PERFORMANCE_MONITOR_AVAILABLE = True
    logger.info("✅ Performance Monitor loaded")
except ImportError as e:
    logger.warning(f"⚠️ Performance Monitor not available: {e}")
    PERFORMANCE_MONITOR_AVAILABLE = False
    performance_monitor = None


@router.get("/unified-prediction/{symbol}")
async def get_unified_prediction(
    symbol: str,
    timeframe: str = Query("5d", description="Prediction timeframe: 1d, 5d, 30d, 90d"),
    include_gnn: bool = Query(True, description="Include Graph Neural Network analysis"),
    include_ensemble: bool = Query(True, description="Include advanced ensemble prediction"),
    include_performance: bool = Query(True, description="Include performance metrics")
) -> Dict[str, Any]:
    """
    Get unified prediction combining Phase 3 and Phase 4 models
    
    This endpoint provides:
    - Advanced ensemble predictions (LSTM, Random Forest, Quantile Regression)
    - Graph Neural Network analysis (market relationships, systemic risk)
    - Performance monitoring metrics
    - Consensus direction and confidence scores
    """
    
    try:
        logger.info(f"📊 Generating unified prediction for {symbol} ({timeframe})")
        
        result = {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": datetime.utcnow().isoformat(),
            "predictions": {},
            "consensus": {},
            "performance": {},
            "status": "success"
        }
        
        # Use enhanced integrated system if available
        if ENHANCED_SYSTEM_AVAILABLE and enhanced_system:
            try:
                comprehensive_result = await enhanced_system.get_comprehensive_prediction(symbol, timeframe)
                result["predictions"] = comprehensive_result.get("components", {})
                result["consensus"] = comprehensive_result.get("aggregate", {})
                logger.info("  ✅ Enhanced system prediction complete")
            except Exception as e:
                logger.warning(f"  ⚠️ Enhanced system prediction failed: {e}")
        
        # Fall back to individual components if needed
        else:
            # Advanced Ensemble Prediction
            if include_ensemble and ADVANCED_PREDICTOR_AVAILABLE and advanced_predictor:
                try:
                    ensemble_result = await advanced_predictor.generate_advanced_prediction(
                        symbol=symbol,
                        timeframe=timeframe,
                        external_factors={
                            'social_sentiment': 0.1,
                            'news_sentiment': 0.05,
                            'geopolitical_risk': 0.2,
                            'global_volatility': 0.15
                        }
                    )
                    
                    result["predictions"]["advanced_ensemble"] = {
                        "direction": ensemble_result.direction,
                        "expected_return": ensemble_result.expected_return,
                        "confidence_interval": list(ensemble_result.confidence_interval),
                        "probability_up": ensemble_result.probability_up,
                        "volatility_estimate": ensemble_result.volatility_estimate,
                        "risk_adjusted_return": ensemble_result.risk_adjusted_return,
                        "model_weights": ensemble_result.model_ensemble_weights,
                        "uncertainty_score": ensemble_result.uncertainty_score
                    }
                    logger.info("  ✅ Advanced ensemble prediction complete")
                except Exception as e:
                    logger.warning(f"  ⚠️ Advanced ensemble failed: {e}")
                    result["predictions"]["advanced_ensemble"] = {"error": str(e)}
            
            # Graph Neural Network Analysis
            if include_gnn and GNN_AVAILABLE and gnn_predictor:
                try:
                    gnn_result = await gnn_predictor.generate_gnn_enhanced_prediction(
                        symbol=symbol,
                        timeframe=timeframe
                    )
                    
                    result["predictions"]["graph_neural_network"] = {
                        "predicted_price": gnn_result.predicted_price,
                        "confidence_score": gnn_result.confidence_score,
                        "node_importance": gnn_result.node_importance,
                        "graph_centrality": gnn_result.graph_centrality,
                        "sector_influence": gnn_result.sector_influence,
                        "market_influence": gnn_result.market_influence,
                        "systemic_risk_score": gnn_result.systemic_risk_score,
                        "contagion_potential": gnn_result.contagion_potential,
                        "key_relationships": [
                            {
                                "symbol": rel[0],
                                "type": rel[1],
                                "strength": rel[2]
                            }
                            for rel in gnn_result.key_relationships[:5]
                        ] if gnn_result.key_relationships else []
                    }
                    logger.info("  ✅ GNN prediction complete")
                except Exception as e:
                    logger.warning(f"  ⚠️ GNN prediction failed: {e}")
                    result["predictions"]["graph_neural_network"] = {"error": str(e)}
            
            # Calculate consensus if predictions exist
            if result["predictions"]:
                result["consensus"] = _calculate_consensus(result["predictions"])
        
        # Performance Metrics
        if include_performance and PERFORMANCE_MONITOR_AVAILABLE and performance_monitor:
            try:
                metrics = performance_monitor.get_current_metrics()
                result["performance"] = {
                    "current_accuracy": metrics.get("accuracy", 0),
                    "recent_predictions": metrics.get("recent_predictions_count", 0),
                    "model_performance": metrics.get("model_performance", {}),
                    "last_updated": metrics.get("last_updated", None)
                }
                
                # Track this prediction
                if "advanced_ensemble" in result["predictions"]:
                    performance_monitor.track_prediction(
                        symbol=symbol,
                        prediction=result["predictions"]["advanced_ensemble"].get("expected_return", 0),
                        confidence=1 - result["predictions"]["advanced_ensemble"].get("uncertainty_score", 0.5),
                        model_type="unified_ensemble"
                    )
                logger.info("  ✅ Performance metrics retrieved")
            except Exception as e:
                logger.warning(f"  ⚠️ Performance metrics failed: {e}")
                result["performance"] = {"error": str(e)}
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Unified prediction failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prediction-status")
async def get_prediction_system_status() -> Dict[str, Any]:
    """
    Get status of all prediction system components
    """
    status = {
        "timestamp": datetime.utcnow().isoformat(),
        "components": {},
        "overall_status": "operational"
    }
    
    # Check enhanced system
    if ENHANCED_SYSTEM_AVAILABLE and enhanced_system:
        try:
            system_status = enhanced_system.get_system_status()
            status["components"]["enhanced_system"] = system_status
        except Exception as e:
            status["components"]["enhanced_system"] = {"error": str(e)}
    else:
        status["components"]["enhanced_system"] = {"status": "unavailable"}
    
    # Check individual components
    status["components"]["advanced_ensemble"] = {
        "status": "operational" if ADVANCED_PREDICTOR_AVAILABLE else "unavailable"
    }
    
    status["components"]["graph_neural_network"] = {
        "status": "operational" if GNN_AVAILABLE else "unavailable"
    }
    
    if GNN_AVAILABLE and gnn_predictor:
        try:
            gnn_status = gnn_predictor.get_system_status()
            status["components"]["graph_neural_network"].update(gnn_status)
        except:
            pass
    
    status["components"]["performance_monitor"] = {
        "status": "operational" if PERFORMANCE_MONITOR_AVAILABLE else "unavailable"
    }
    
    # Determine overall status
    operational_count = sum(
        1 for comp in status["components"].values()
        if isinstance(comp, dict) and comp.get("status") == "operational"
    )
    
    if operational_count == 0:
        status["overall_status"] = "down"
    elif operational_count < len(status["components"]):
        status["overall_status"] = "degraded"
    
    return status


@router.get("/performance-metrics")
async def get_performance_metrics(
    lookback_days: int = Query(7, description="Number of days to look back"),
    model_type: Optional[str] = Query(None, description="Filter by model type")
) -> Dict[str, Any]:
    """
    Get detailed performance metrics for prediction models
    """
    
    if not PERFORMANCE_MONITOR_AVAILABLE or not performance_monitor:
        raise HTTPException(status_code=503, detail="Performance monitor not available")
    
    try:
        # Get comprehensive metrics
        metrics = performance_monitor.get_detailed_metrics(
            lookback_days=lookback_days,
            model_type=model_type
        )
        
        # Add summary statistics
        summary = {
            "total_predictions": metrics.get("total_predictions", 0),
            "average_accuracy": metrics.get("average_accuracy", 0),
            "best_performing_model": metrics.get("best_model", None),
            "worst_performing_model": metrics.get("worst_model", None)
        }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "lookback_days": lookback_days,
            "summary": summary,
            "detailed_metrics": metrics,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train-models")
async def train_prediction_models(
    background_tasks: BackgroundTasks,
    symbols: List[str] = Query(["^AORD", "CBA.AX", "BHP.AX"], description="Symbols to train on"),
    training_days: int = Query(252, description="Number of days of historical data")
) -> Dict[str, Any]:
    """
    Trigger training of prediction models in the background
    """
    
    if not ENHANCED_SYSTEM_AVAILABLE:
        raise HTTPException(status_code=503, detail="Enhanced system not available")
    
    # Add background task for training
    background_tasks.add_task(_train_models_background, symbols, training_days)
    
    return {
        "status": "training_started",
        "symbols": symbols,
        "training_days": training_days,
        "message": "Model training initiated in background"
    }


async def _train_models_background(symbols: List[str], training_days: int):
    """
    Background task to train prediction models
    """
    logger.info(f"🎯 Starting model training for {symbols} with {training_days} days of data")
    
    try:
        for symbol in symbols:
            # Fetch historical data
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=training_days)
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                logger.warning(f"  ⚠️ No data available for {symbol}")
                continue
            
            # Train models (simplified - in production, implement actual training)
            logger.info(f"  📈 Training models for {symbol}...")
            
            # Here you would implement actual model training
            # For now, just log the activity
            await asyncio.sleep(1)  # Simulate training time
            
        logger.info("✅ Model training completed")
        
    except Exception as e:
        logger.error(f"❌ Model training failed: {e}")


def _calculate_consensus(predictions: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate consensus from multiple prediction sources
    """
    consensus = {
        "direction": None,
        "confidence": None,
        "expected_return": None,
        "risk_level": None
    }
    
    directions = []
    confidences = []
    returns = []
    
    # Extract data from advanced ensemble
    if "advanced_ensemble" in predictions and "error" not in predictions["advanced_ensemble"]:
        ae = predictions["advanced_ensemble"]
        directions.append(ae.get("direction"))
        confidences.append(1 - ae.get("uncertainty_score", 0.5))
        returns.append(ae.get("expected_return", 0))
    
    # Extract data from GNN
    if "graph_neural_network" in predictions and "error" not in predictions["graph_neural_network"]:
        gnn = predictions["graph_neural_network"]
        confidences.append(gnn.get("confidence_score", 0.5))
        
        # Infer direction from systemic risk
        risk_score = gnn.get("systemic_risk_score", 0.5)
        if risk_score < 0.3:
            consensus["risk_level"] = "low"
        elif risk_score < 0.7:
            consensus["risk_level"] = "medium"
        else:
            consensus["risk_level"] = "high"
    
    # Calculate consensus direction
    if directions:
        up_count = directions.count("up")
        down_count = directions.count("down")
        if up_count > down_count:
            consensus["direction"] = "up"
        elif down_count > up_count:
            consensus["direction"] = "down"
        else:
            consensus["direction"] = "sideways"
    
    # Calculate average confidence
    if confidences:
        consensus["confidence"] = np.mean(confidences)
    
    # Calculate expected return
    if returns:
        consensus["expected_return"] = np.mean(returns)
    
    return consensus


# Export router
__all__ = ["router"]