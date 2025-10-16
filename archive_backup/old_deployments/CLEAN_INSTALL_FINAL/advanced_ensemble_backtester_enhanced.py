#!/usr/bin/env python3
"""
Enhanced Ensemble Backtester with Real Training Integration
Implements continuous learning from backtesting results
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import logging
import json
import yfinance as yf
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error
import warnings
import pickle
import os

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Import enhanced predictor
try:
    from advanced_ensemble_predictor_enhanced import EnhancedEnsemblePredictor
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False
    logger.warning("Enhanced predictor not available")

@dataclass
class TrainingFeedback:
    """Feedback from backtesting to improve models"""
    timestamp: datetime
    symbol: str
    timeframe: str
    
    # Performance metrics
    accuracy_improvement: float
    error_reduction: float
    
    # Model-specific feedback
    model_adjustments: Dict[str, float]
    
    # Feature importance updates
    feature_importance_changes: Dict[str, float]
    
    # Recommendations
    recommendations: List[str]

class EnhancedEnsembleBacktester:
    """Enhanced backtester with real-time model training"""
    
    def __init__(self):
        if ENHANCED_AVAILABLE:
            self.predictor = EnhancedEnsemblePredictor()
        else:
            self.predictor = None
            
        # Performance tracking
        self.performance_history = []
        self.training_feedback_history = []
        
        # Model improvement tracking
        self.baseline_performance = {}
        self.current_performance = {}
        
        # Training configuration
        self.training_config = {
            "min_samples_for_training": 100,
            "retrain_frequency": 50,  # Retrain every 50 predictions
            "performance_threshold": 0.6,  # Minimum accuracy threshold
            "improvement_target": 0.02  # Target 2% improvement per iteration
        }
        
        # Cache for faster backtesting
        self.data_cache = {}
        self.results_cache = {}
        
    async def run_enhanced_backtest(self,
                                   symbol: str,
                                   start_date: str,
                                   end_date: str,
                                   continuous_learning: bool = True) -> Dict[str, Any]:
        """Run enhanced backtest with continuous learning"""
        
        logger.info(f"🚀 Starting enhanced backtest for {symbol}")
        logger.info(f"   Period: {start_date} to {end_date}")
        logger.info(f"   Continuous Learning: {'ENABLED' if continuous_learning else 'DISABLED'}")
        
        try:
            # Fetch historical data
            historical_data = await self._fetch_historical_data(symbol, start_date, end_date)
            
            if historical_data.empty:
                raise ValueError(f"No data available for {symbol}")
            
            # Initialize results
            predictions = []
            actuals = []
            training_points = []
            
            # Split data for walk-forward analysis
            train_size = int(len(historical_data) * 0.7)
            initial_train = historical_data.iloc[:train_size]
            test_data = historical_data.iloc[train_size:]
            
            # Initial model training with real data
            if continuous_learning and self.predictor:
                logger.info("📚 Initial model training with historical data...")
                await self._train_models_with_data(initial_train, symbol)
            
            # Walk-forward backtesting
            predictions_made = 0
            correct_predictions = 0
            
            for i in range(len(test_data) - 1):
                current_data = test_data.iloc[:i+1]
                current_point = test_data.iloc[i]
                next_point = test_data.iloc[i+1]
                
                # Make prediction
                prediction = await self._make_enhanced_prediction(
                    symbol, current_data, current_point
                )
                
                # Calculate actual outcome
                actual_return = (next_point['Close'] - current_point['Close']) / current_point['Close']
                actual_direction = 1 if actual_return > 0 else 0
                
                predictions.append(prediction['predicted_direction'])
                actuals.append(actual_direction)
                
                predictions_made += 1
                if prediction['predicted_direction'] == actual_direction:
                    correct_predictions += 1
                
                # Continuous learning: retrain periodically
                if continuous_learning and predictions_made % self.training_config['retrain_frequency'] == 0:
                    accuracy = correct_predictions / predictions_made
                    
                    # Generate training feedback
                    feedback = self._generate_training_feedback(
                        predictions[-50:], actuals[-50:], symbol, accuracy
                    )
                    
                    # Update model weights based on performance
                    await self._update_model_weights(feedback)
                    
                    # Incremental training with recent data
                    if self.predictor:
                        recent_data = historical_data.iloc[max(0, i-100):i+1]
                        await self.predictor.incremental_train(symbol, recent_data)
                    
                    logger.info(f"📈 Retraining at {predictions_made} predictions. Accuracy: {accuracy:.2%}")
            
            # Calculate final metrics
            final_accuracy = accuracy_score(actuals, predictions)
            mae = mean_absolute_error(actuals, predictions)
            rmse = np.sqrt(mean_squared_error(actuals, predictions))
            
            # Calculate improvement from baseline
            improvement = 0
            if symbol in self.baseline_performance:
                improvement = final_accuracy - self.baseline_performance[symbol]
            else:
                self.baseline_performance[symbol] = final_accuracy
            
            self.current_performance[symbol] = final_accuracy
            
            # Generate comprehensive results
            results = {
                "success": True,
                "symbol": symbol,
                "period": f"{start_date} to {end_date}",
                "total_predictions": predictions_made,
                "correct_predictions": correct_predictions,
                "metrics": {
                    "accuracy": final_accuracy,
                    "mae": mae,
                    "rmse": rmse,
                    "improvement_from_baseline": improvement
                },
                "learning_enabled": continuous_learning,
                "training_iterations": len(self.training_feedback_history),
                "final_model_weights": self.predictor.model_weights if self.predictor else {},
                "performance_trend": self._calculate_performance_trend(),
                "recommendations": self._generate_recommendations(final_accuracy, improvement)
            }
            
            # Store results in history
            self.performance_history.append({
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "accuracy": final_accuracy,
                "improvement": improvement
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Enhanced backtest failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "symbol": symbol
            }
    
    async def _fetch_historical_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch historical data with caching"""
        
        cache_key = f"{symbol}_{start_date}_{end_date}"
        
        # Check cache first
        if cache_key in self.data_cache:
            logger.info(f"📦 Using cached data for {symbol}")
            return self.data_cache[cache_key]
        
        try:
            # Fetch from Yahoo Finance
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            # Cache the data
            self.data_cache[cache_key] = data
            
            logger.info(f"📊 Fetched {len(data)} data points for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def _train_models_with_data(self, data: pd.DataFrame, symbol: str):
        """Train models with real historical data"""
        
        if not self.predictor:
            return
        
        try:
            # Prepare training batch
            training_batch = [{
                'symbol': symbol,
                'period': 'historical',
                'data': data
            }]
            
            # Batch train models
            result = await self.predictor.batch_train_models(training_batch)
            
            if result['success']:
                logger.info(f"✅ Trained {result['models_trained']} models with {result['total_samples']} samples")
            else:
                logger.warning(f"⚠️ Training failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Training failed: {e}")
    
    async def _make_enhanced_prediction(self, 
                                       symbol: str, 
                                       historical_data: pd.DataFrame,
                                       current_point: pd.Series) -> Dict[str, Any]:
        """Make prediction using enhanced predictor"""
        
        try:
            if self.predictor and hasattr(self.predictor, 'models'):
                # Use real trained models
                features = self.predictor._prepare_features(historical_data.tail(100))
                
                if len(features) > 0:
                    # Get predictions from all models
                    predictions = {}
                    for model_name, model in self.predictor.models.items():
                        try:
                            if 'lstm' in model_name and hasattr(model, 'predict'):
                                # LSTM prediction
                                X = features[-1:].reshape((1, 1, features.shape[1]))
                                pred = model.predict(X, verbose=0)[0][0]
                            else:
                                # Sklearn model prediction
                                pred = model.predict(features[-1:].reshape(1, -1))[0]
                            
                            predictions[model_name] = pred
                        except:
                            predictions[model_name] = 0.5
                    
                    # Weighted ensemble prediction
                    weighted_pred = sum(
                        predictions.get(model, 0.5) * self.predictor.model_weights.get(model.split('_')[0], 0.25)
                        for model in predictions
                    )
                    
                    return {
                        'predicted_direction': 1 if weighted_pred > 0.5 else 0,
                        'confidence': abs(weighted_pred - 0.5) * 2,
                        'model_predictions': predictions
                    }
            
            # Fallback to simple prediction
            return {
                'predicted_direction': 1 if np.random.random() > 0.5 else 0,
                'confidence': 0.5,
                'model_predictions': {}
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                'predicted_direction': 0,
                'confidence': 0.5,
                'model_predictions': {}
            }
    
    def _generate_training_feedback(self, 
                                   recent_predictions: List[int],
                                   recent_actuals: List[int],
                                   symbol: str,
                                   current_accuracy: float) -> TrainingFeedback:
        """Generate feedback for model improvement"""
        
        # Calculate recent performance
        recent_accuracy = accuracy_score(recent_actuals, recent_predictions) if recent_predictions else 0
        
        # Determine model adjustments
        model_adjustments = {}
        if self.predictor and hasattr(self.predictor, 'model_weights'):
            for model, weight in self.predictor.model_weights.items():
                # Increase weight for better performing models
                if recent_accuracy > current_accuracy:
                    model_adjustments[model] = weight * 1.1
                else:
                    model_adjustments[model] = weight * 0.95
        
        # Generate recommendations
        recommendations = []
        if recent_accuracy < self.training_config['performance_threshold']:
            recommendations.append("Increase training data size")
            recommendations.append("Adjust feature engineering")
        if current_accuracy < 0.55:
            recommendations.append("Consider different model architectures")
        
        feedback = TrainingFeedback(
            timestamp=datetime.now(),
            symbol=symbol,
            timeframe="recent_50",
            accuracy_improvement=recent_accuracy - current_accuracy,
            error_reduction=0,  # Could calculate if tracking errors
            model_adjustments=model_adjustments,
            feature_importance_changes={},  # Could track feature importance
            recommendations=recommendations
        )
        
        self.training_feedback_history.append(feedback)
        return feedback
    
    async def _update_model_weights(self, feedback: TrainingFeedback):
        """Update model weights based on feedback"""
        
        if not self.predictor:
            return
        
        try:
            # Create backtest results format for weight update
            backtest_results = {
                "overall_accuracy": 0.5 + feedback.accuracy_improvement,
                "model_performance": {
                    model: {"dominant_accuracy": adj_weight}
                    for model, adj_weight in feedback.model_adjustments.items()
                }
            }
            
            # Update weights in predictor
            await self.predictor.update_weights_from_backtest(backtest_results)
            
            logger.info(f"📊 Updated model weights based on feedback")
            
        except Exception as e:
            logger.error(f"Failed to update weights: {e}")
    
    def _calculate_performance_trend(self) -> str:
        """Calculate performance trend over time"""
        
        if len(self.performance_history) < 2:
            return "insufficient_data"
        
        recent = self.performance_history[-5:] if len(self.performance_history) >= 5 else self.performance_history
        
        accuracies = [p['accuracy'] for p in recent]
        
        # Simple trend detection
        if all(accuracies[i] <= accuracies[i+1] for i in range(len(accuracies)-1)):
            return "improving"
        elif all(accuracies[i] >= accuracies[i+1] for i in range(len(accuracies)-1)):
            return "declining"
        else:
            return "stable"
    
    def _generate_recommendations(self, accuracy: float, improvement: float) -> List[str]:
        """Generate recommendations based on performance"""
        
        recommendations = []
        
        if accuracy < 0.55:
            recommendations.append("🚨 Critical: Accuracy below 55%, major model revision needed")
        elif accuracy < 0.65:
            recommendations.append("⚠️ Warning: Accuracy below 65%, consider feature engineering")
        else:
            recommendations.append("✅ Good performance, continue monitoring")
        
        if improvement > 0.05:
            recommendations.append("📈 Excellent improvement! Current approach is working")
        elif improvement > 0:
            recommendations.append("📊 Positive improvement trend")
        else:
            recommendations.append("📉 No improvement, consider adjusting learning rate")
        
        # Model-specific recommendations
        if self.predictor and hasattr(self.predictor, 'model_weights'):
            best_model = max(self.predictor.model_weights.items(), key=lambda x: x[1])
            recommendations.append(f"🏆 Best model: {best_model[0]} (weight: {best_model[1]:.2f})")
        
        return recommendations
    
    async def parallel_symbol_backtest(self, symbols: List[str], period_days: int = 90) -> Dict[str, Any]:
        """Run backtests for multiple symbols in parallel"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Run parallel backtests using predictor's parallel capability
        if self.predictor:
            results = await self.predictor.parallel_backtest(
                symbols, 
                f"{period_days}d"
            )
        else:
            results = []
        
        # Aggregate results
        summary = {
            "total_symbols": len(symbols),
            "successful_backtests": len([r for r in results if r.get('success', False)]),
            "average_accuracy": np.mean([r.get('accuracy', 0) for r in results]),
            "best_performer": max(results, key=lambda x: x.get('accuracy', 0)) if results else None,
            "worst_performer": min(results, key=lambda x: x.get('accuracy', 0)) if results else None,
            "results_by_symbol": {r['symbol']: r for r in results}
        }
        
        return summary
    
    def save_backtest_results(self, filename: str = None):
        """Save backtest results and model state"""
        
        if filename is None:
            filename = f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        
        state = {
            "performance_history": self.performance_history,
            "training_feedback_history": [
                {
                    "timestamp": f.timestamp.isoformat(),
                    "symbol": f.symbol,
                    "accuracy_improvement": f.accuracy_improvement,
                    "recommendations": f.recommendations
                }
                for f in self.training_feedback_history
            ],
            "baseline_performance": self.baseline_performance,
            "current_performance": self.current_performance,
            "model_weights": self.predictor.model_weights if self.predictor else {}
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(state, f)
        
        logger.info(f"💾 Saved backtest results to {filename}")
        return filename
    
    def load_backtest_results(self, filename: str):
        """Load previous backtest results and model state"""
        
        try:
            with open(filename, 'rb') as f:
                state = pickle.load(f)
            
            self.performance_history = state.get('performance_history', [])
            self.baseline_performance = state.get('baseline_performance', {})
            self.current_performance = state.get('current_performance', {})
            
            if self.predictor and 'model_weights' in state:
                self.predictor.model_weights = state['model_weights']
            
            logger.info(f"📂 Loaded backtest results from {filename}")
            
        except Exception as e:
            logger.error(f"Failed to load results: {e}")

# Global instance
enhanced_backtester = EnhancedEnsembleBacktester()

if __name__ == "__main__":
    async def test():
        print("🚀 Testing Enhanced Backtester with Continuous Learning")
        
        # Run enhanced backtest with continuous learning
        results = await enhanced_backtester.run_enhanced_backtest(
            symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-10-01",
            continuous_learning=True
        )
        
        print(f"📊 Backtest Results:")
        print(f"   Accuracy: {results['metrics']['accuracy']:.2%}")
        print(f"   Improvement: {results['metrics']['improvement_from_baseline']:.2%}")
        print(f"   Performance Trend: {results['performance_trend']}")
        
        # Save results
        filename = enhanced_backtester.save_backtest_results()
        print(f"💾 Results saved to {filename}")
        
    asyncio.run(test())