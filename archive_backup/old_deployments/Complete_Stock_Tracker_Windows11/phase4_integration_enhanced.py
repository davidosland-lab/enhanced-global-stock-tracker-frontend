#!/usr/bin/env python3
"""
Phase 4 Integration Module - Enhanced with Real Training and Continuous Learning
Connects enhanced predictor and backtester with real-time feedback loop
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import json

# Import enhanced components
try:
    from advanced_ensemble_predictor_enhanced import EnhancedEnsemblePredictor
    from advanced_ensemble_backtester_enhanced import EnhancedEnsembleBacktester
    ENHANCED_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Enhanced modules not available: {e}")
    ENHANCED_AVAILABLE = False

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Phase4EnhancedSystem:
    """Complete Phase 4 system with real training and continuous learning"""
    
    def __init__(self):
        if ENHANCED_AVAILABLE:
            self.predictor = EnhancedEnsemblePredictor()
            self.backtester = EnhancedEnsembleBacktester()
            # Share predictor instance with backtester
            self.backtester.predictor = self.predictor
        else:
            self.predictor = None
            self.backtester = None
        
        # System state
        self.is_training = False
        self.training_queue = []
        self.performance_metrics = {}
        self.active_symbols = set()
        
        # Background training task
        self.training_task = None
        
    async def initialize_system(self):
        """Initialize the system with baseline models"""
        
        logger.info("🚀 Initializing Phase 4 Enhanced System")
        
        if not ENHANCED_AVAILABLE:
            logger.error("Enhanced modules not available")
            return False
        
        try:
            # Load any saved model states
            try:
                self.backtester.load_backtest_results("latest_model_state.pkl")
                logger.info("✅ Loaded previous model state")
            except:
                logger.info("📝 No previous model state found, starting fresh")
            
            # Start background training task
            self.training_task = asyncio.create_task(self._background_training_loop())
            
            logger.info("✅ Phase 4 system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            return False
    
    async def _background_training_loop(self):
        """Background loop for continuous model training"""
        
        while True:
            try:
                if self.training_queue:
                    # Process training queue
                    task = self.training_queue.pop(0)
                    await self._process_training_task(task)
                
                # Periodic model evaluation
                if len(self.active_symbols) > 0:
                    for symbol in self.active_symbols:
                        # Run mini-backtest for recent performance
                        await self._evaluate_recent_performance(symbol)
                
                # Sleep before next iteration
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Background training error: {e}")
                await asyncio.sleep(60)
    
    async def _process_training_task(self, task: Dict):
        """Process a single training task"""
        
        try:
            symbol = task['symbol']
            data = task['data']
            
            logger.info(f"📚 Processing training task for {symbol}")
            
            # Incremental training
            result = await self.predictor.incremental_train(symbol, data)
            
            if result['success']:
                logger.info(f"✅ Training completed for {symbol}")
            
        except Exception as e:
            logger.error(f"Training task failed: {e}")
    
    async def _evaluate_recent_performance(self, symbol: str):
        """Evaluate recent model performance for a symbol"""
        
        try:
            # Get last 10 days of data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=10)
            
            # Run mini backtest
            results = await self.backtester.run_enhanced_backtest(
                symbol=symbol,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                continuous_learning=True
            )
            
            # Update performance metrics
            self.performance_metrics[symbol] = {
                'accuracy': results['metrics']['accuracy'],
                'last_evaluated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Performance evaluation failed for {symbol}: {e}")
    
    async def generate_prediction_with_learning(self, 
                                               symbol: str,
                                               timeframe: str = "5d",
                                               enable_learning: bool = True) -> Dict[str, Any]:
        """Generate prediction with optional continuous learning"""
        
        if not self.predictor:
            return {
                "error": "Predictor not available",
                "suggestion": "Initialize system first"
            }
        
        try:
            # Add symbol to active tracking
            self.active_symbols.add(symbol)
            
            # Fetch recent market data
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(period="3mo", interval="1d")
            
            if hist_data.empty:
                raise ValueError(f"No data available for {symbol}")
            
            current_price = hist_data['Close'].iloc[-1]
            
            # Prepare features for prediction
            features = self.predictor._prepare_features(hist_data)
            
            # Get predictions from all trained models
            predictions = {}
            for model_name, model in self.predictor.models.items():
                try:
                    if 'lstm' in model_name:
                        X = features[-1:].reshape((1, 1, features.shape[1]))
                        pred = model.predict(X, verbose=0)[0][0] if hasattr(model, 'predict') else 0.5
                    else:
                        pred = model.predict(features[-1:].reshape(1, -1))[0] if hasattr(model, 'predict') else 0.5
                    predictions[model_name] = float(pred)
                except:
                    predictions[model_name] = 0.5
            
            # Calculate weighted ensemble prediction
            weighted_pred = sum(
                predictions.get(model, 0.5) * self.predictor.model_weights.get(model.split('_')[0], 0.25)
                for model in predictions
            )
            
            # Calculate predicted price
            predicted_return = (weighted_pred - 0.5) * 0.1  # Scale to reasonable return
            predicted_price = current_price * (1 + predicted_return)
            
            # If learning enabled, queue for training
            if enable_learning:
                self.training_queue.append({
                    'symbol': symbol,
                    'data': hist_data,
                    'timestamp': datetime.now()
                })
            
            result = {
                "success": True,
                "symbol": symbol,
                "timeframe": timeframe,
                "current_price": float(current_price),
                "predicted_price": float(predicted_price),
                "predicted_return": float(predicted_return),
                "confidence": float(abs(weighted_pred - 0.5) * 2),
                "direction": "up" if weighted_pred > 0.5 else "down",
                "model_predictions": predictions,
                "model_weights": dict(self.predictor.model_weights),
                "learning_enabled": enable_learning,
                "performance_metrics": self.performance_metrics.get(symbol, {}),
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed for {symbol}: {e}")
            return {
                "success": False,
                "error": str(e),
                "symbol": symbol
            }
    
    async def run_backtest_with_training(self,
                                        symbol: str,
                                        period: str = "3m") -> Dict[str, Any]:
        """Run backtest with continuous model training"""
        
        if not self.backtester:
            return {
                "error": "Backtester not available",
                "suggestion": "Initialize system first"
            }
        
        try:
            # Parse period
            period_map = {
                "1m": 30,
                "3m": 90,
                "6m": 180,
                "1y": 365
            }
            days = period_map.get(period, 90)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Run enhanced backtest with learning
            results = await self.backtester.run_enhanced_backtest(
                symbol=symbol,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                continuous_learning=True
            )
            
            # Save updated model state
            self.backtester.save_backtest_results("latest_model_state.pkl")
            
            return results
            
        except Exception as e:
            logger.error(f"Backtest failed for {symbol}: {e}")
            return {
                "success": False,
                "error": str(e),
                "symbol": symbol
            }
    
    async def batch_train_symbols(self, symbols: List[str], period: str = "6m") -> Dict[str, Any]:
        """Train models for multiple symbols in batch"""
        
        if not self.predictor:
            return {
                "error": "Predictor not available",
                "suggestion": "Initialize system first"
            }
        
        try:
            logger.info(f"📦 Starting batch training for {len(symbols)} symbols")
            
            # Prepare training batch
            training_batch = []
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period=period)
                    
                    if not data.empty:
                        training_batch.append({
                            'symbol': symbol,
                            'period': period,
                            'data': data
                        })
                except Exception as e:
                    logger.warning(f"Failed to fetch data for {symbol}: {e}")
            
            # Batch train
            result = await self.predictor.batch_train_models(training_batch)
            
            # Run parallel backtests to evaluate
            backtest_results = await self.backtester.parallel_symbol_backtest(symbols, 90)
            
            return {
                "success": True,
                "symbols_trained": len(training_batch),
                "training_result": result,
                "backtest_summary": backtest_results,
                "model_weights": dict(self.predictor.model_weights),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Batch training failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and metrics"""
        
        status = {
            "system_available": ENHANCED_AVAILABLE,
            "is_training": self.is_training,
            "training_queue_size": len(self.training_queue),
            "active_symbols": list(self.active_symbols),
            "performance_metrics": self.performance_metrics,
            "model_summary": None,
            "timestamp": datetime.now().isoformat()
        }
        
        if self.predictor:
            status["model_summary"] = self.predictor.get_training_summary()
        
        return status
    
    async def optimize_model_weights(self) -> Dict[str, Any]:
        """Optimize model weights based on recent performance"""
        
        if not self.backtester or not self.predictor:
            return {
                "error": "System components not available",
                "suggestion": "Initialize system first"
            }
        
        try:
            # Get recent performance for all active symbols
            performances = {}
            
            for symbol in self.active_symbols:
                # Run quick backtest
                results = await self.backtester.run_enhanced_backtest(
                    symbol=symbol,
                    start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                    end_date=datetime.now().strftime('%Y-%m-%d'),
                    continuous_learning=False  # Just evaluate, don't train
                )
                
                performances[symbol] = results['metrics']['accuracy']
            
            # Calculate optimal weights based on performance
            if performances:
                avg_performance = np.mean(list(performances.values()))
                
                # Update weights based on performance
                backtest_results = {
                    "overall_accuracy": avg_performance,
                    "model_performance": {
                        model: {"dominant_accuracy": weight * (1 + (avg_performance - 0.5))}
                        for model, weight in self.predictor.model_weights.items()
                    }
                }
                
                await self.predictor.update_weights_from_backtest(backtest_results)
                
                return {
                    "success": True,
                    "average_performance": avg_performance,
                    "updated_weights": dict(self.predictor.model_weights),
                    "performances_by_symbol": performances,
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "success": False,
                "message": "No active symbols to optimize"
            }
            
        except Exception as e:
            logger.error(f"Weight optimization failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global system instance
phase4_system = Phase4EnhancedSystem()

# FastAPI endpoints
app = FastAPI(title="Phase 4 Enhanced API")

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    await phase4_system.initialize_system()

@app.post("/api/phase4/predict")
async def predict(symbol: str, timeframe: str = "5d", enable_learning: bool = True):
    """Generate prediction with optional learning"""
    return await phase4_system.generate_prediction_with_learning(symbol, timeframe, enable_learning)

@app.post("/api/phase4/backtest")
async def backtest(symbol: str, period: str = "3m"):
    """Run backtest with continuous training"""
    return await phase4_system.run_backtest_with_training(symbol, period)

@app.post("/api/phase4/train")
async def train(symbols: List[str], period: str = "6m"):
    """Batch train models for multiple symbols"""
    return await phase4_system.batch_train_symbols(symbols, period)

@app.get("/api/phase4/status")
async def status():
    """Get system status"""
    return phase4_system.get_system_status()

@app.post("/api/phase4/optimize")
async def optimize():
    """Optimize model weights"""
    return await phase4_system.optimize_model_weights()

if __name__ == "__main__":
    async def test():
        print("🚀 Testing Phase 4 Enhanced System")
        
        # Initialize
        await phase4_system.initialize_system()
        
        # Test prediction with learning
        prediction = await phase4_system.generate_prediction_with_learning("AAPL", "5d", True)
        print(f"📊 Prediction: {json.dumps(prediction, indent=2)}")
        
        # Test backtest with training
        backtest = await phase4_system.run_backtest_with_training("AAPL", "3m")
        print(f"📈 Backtest Accuracy: {backtest.get('metrics', {}).get('accuracy', 0):.2%}")
        
        # Get status
        status = phase4_system.get_system_status()
        print(f"🔍 System Status: {json.dumps(status, indent=2)}")
    
    asyncio.run(test())