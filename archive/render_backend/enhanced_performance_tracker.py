#!/usr/bin/env python3
"""
Enhanced Performance Tracker for Phase 3 and Phase 4 Models
Tracks and analyzes prediction accuracy across all model types
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
import json
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import asyncio
import yfinance as yf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PredictionRecord:
    """Record of a single prediction for tracking"""
    symbol: str
    timestamp: datetime
    model_type: str  # e.g., 'ensemble', 'gnn', 'lstm', etc.
    predicted_value: float
    predicted_direction: str  # 'up', 'down', 'sideways'
    confidence: float
    timeframe: str  # '1d', '5d', '30d', '90d'
    actual_value: Optional[float] = None
    actual_direction: Optional[str] = None
    error: Optional[float] = None
    squared_error: Optional[float] = None
    direction_correct: Optional[bool] = None
    evaluated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class EnhancedPerformanceTracker:
    """
    Tracks performance of all prediction models including Phase 3 and Phase 4
    """
    
    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self.predictions: deque = deque(maxlen=max_history)
        self.model_metrics: Dict[str, Dict] = defaultdict(lambda: {
            'total_predictions': 0,
            'correct_directions': 0,
            'cumulative_error': 0,
            'cumulative_squared_error': 0,
            'best_prediction': None,
            'worst_prediction': None,
            'confidence_calibration': []
        })
        self.symbol_metrics: Dict[str, Dict] = defaultdict(dict)
        self.last_evaluation = datetime.now()
        logger.info("🎯 Enhanced Performance Tracker initialized")
    
    def track_prediction(self, 
                        symbol: str,
                        model_type: str,
                        predicted_value: float,
                        predicted_direction: str,
                        confidence: float,
                        timeframe: str,
                        metadata: Optional[Dict] = None) -> str:
        """
        Track a new prediction
        
        Returns:
            Prediction ID for future reference
        """
        prediction = PredictionRecord(
            symbol=symbol,
            timestamp=datetime.now(),
            model_type=model_type,
            predicted_value=predicted_value,
            predicted_direction=predicted_direction,
            confidence=confidence,
            timeframe=timeframe,
            metadata=metadata or {}
        )
        
        self.predictions.append(prediction)
        self.model_metrics[model_type]['total_predictions'] += 1
        
        # Generate prediction ID
        pred_id = f"{symbol}_{model_type}_{prediction.timestamp.isoformat()}"
        logger.info(f"📊 Tracked prediction: {pred_id} - {predicted_direction} ({confidence:.2%} confidence)")
        
        return pred_id
    
    async def evaluate_predictions(self, lookback_hours: int = 24):
        """
        Evaluate predictions against actual market data
        """
        logger.info(f"🔍 Evaluating predictions from last {lookback_hours} hours")
        
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
        predictions_to_evaluate = [
            p for p in self.predictions 
            if p.timestamp >= cutoff_time and p.actual_value is None
        ]
        
        # Group by symbol for efficient data fetching
        symbol_predictions = defaultdict(list)
        for pred in predictions_to_evaluate:
            symbol_predictions[pred.symbol].append(pred)
        
        evaluation_results = []
        
        for symbol, preds in symbol_predictions.items():
            try:
                # Fetch actual market data
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=f"{lookback_hours}h", interval="1h")
                
                if hist.empty:
                    logger.warning(f"No market data available for {symbol}")
                    continue
                
                current_price = float(hist['Close'].iloc[-1])
                
                for pred in preds:
                    # Determine actual outcome based on timeframe
                    actual_value, actual_direction = await self._get_actual_outcome(
                        symbol, pred.timestamp, pred.timeframe, current_price
                    )
                    
                    if actual_value is not None:
                        # Calculate errors
                        pred.actual_value = actual_value
                        pred.actual_direction = actual_direction
                        pred.error = abs(pred.predicted_value - actual_value)
                        pred.squared_error = pred.error ** 2
                        pred.direction_correct = (pred.predicted_direction == actual_direction)
                        pred.evaluated_at = datetime.now()
                        
                        # Update model metrics
                        self._update_model_metrics(pred)
                        
                        evaluation_results.append({
                            'symbol': symbol,
                            'model': pred.model_type,
                            'direction_correct': pred.direction_correct,
                            'error': pred.error,
                            'confidence': pred.confidence
                        })
                        
                        logger.info(f"  ✅ Evaluated {symbol} prediction: "
                                  f"{'✓' if pred.direction_correct else '✗'} "
                                  f"(error: {pred.error:.4f})")
                        
            except Exception as e:
                logger.error(f"Failed to evaluate predictions for {symbol}: {e}")
        
        self.last_evaluation = datetime.now()
        return evaluation_results
    
    async def _get_actual_outcome(self, symbol: str, prediction_time: datetime, 
                                  timeframe: str, current_price: float) -> Tuple[Optional[float], Optional[str]]:
        """
        Get actual market outcome for a prediction
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get price at prediction time
            hist_at_prediction = ticker.history(
                start=prediction_time - timedelta(hours=1),
                end=prediction_time + timedelta(hours=1),
                interval="1h"
            )
            
            if hist_at_prediction.empty:
                return None, None
            
            base_price = float(hist_at_prediction['Close'].iloc[0])
            
            # Calculate change
            price_change_pct = ((current_price - base_price) / base_price) * 100
            
            # Determine direction
            if price_change_pct > 0.5:
                direction = "up"
            elif price_change_pct < -0.5:
                direction = "down"
            else:
                direction = "sideways"
            
            return current_price, direction
            
        except Exception as e:
            logger.error(f"Error getting actual outcome: {e}")
            return None, None
    
    def _update_model_metrics(self, prediction: PredictionRecord):
        """
        Update metrics for a specific model based on evaluation
        """
        model = prediction.model_type
        metrics = self.model_metrics[model]
        
        if prediction.direction_correct:
            metrics['correct_directions'] += 1
        
        metrics['cumulative_error'] += prediction.error
        metrics['cumulative_squared_error'] += prediction.squared_error
        
        # Track best and worst predictions
        if metrics['best_prediction'] is None or prediction.error < metrics['best_prediction']['error']:
            metrics['best_prediction'] = {
                'symbol': prediction.symbol,
                'error': prediction.error,
                'timestamp': prediction.timestamp
            }
        
        if metrics['worst_prediction'] is None or prediction.error > metrics['worst_prediction']['error']:
            metrics['worst_prediction'] = {
                'symbol': prediction.symbol,
                'error': prediction.error,
                'timestamp': prediction.timestamp
            }
        
        # Confidence calibration
        metrics['confidence_calibration'].append({
            'confidence': prediction.confidence,
            'correct': prediction.direction_correct
        })
    
    def get_model_performance(self, model_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance metrics for a specific model or all models
        """
        if model_type:
            return self._calculate_model_stats(model_type)
        
        # Return stats for all models
        all_stats = {}
        for model in self.model_metrics.keys():
            all_stats[model] = self._calculate_model_stats(model)
        
        return all_stats
    
    def _calculate_model_stats(self, model_type: str) -> Dict[str, Any]:
        """
        Calculate comprehensive statistics for a model
        """
        metrics = self.model_metrics[model_type]
        total = metrics['total_predictions']
        
        if total == 0:
            return {'status': 'no_predictions'}
        
        # Calculate accuracy and errors
        evaluated = len([p for p in self.predictions 
                        if p.model_type == model_type and p.actual_value is not None])
        
        if evaluated == 0:
            return {
                'total_predictions': total,
                'evaluated': 0,
                'status': 'pending_evaluation'
            }
        
        direction_accuracy = metrics['correct_directions'] / evaluated if evaluated > 0 else 0
        mae = metrics['cumulative_error'] / evaluated if evaluated > 0 else 0
        rmse = np.sqrt(metrics['cumulative_squared_error'] / evaluated) if evaluated > 0 else 0
        
        # Confidence calibration
        if metrics['confidence_calibration']:
            calibration_data = pd.DataFrame(metrics['confidence_calibration'])
            confidence_correlation = calibration_data.corr().iloc[0, 1] if len(calibration_data) > 1 else 0
        else:
            confidence_correlation = 0
        
        return {
            'model_type': model_type,
            'total_predictions': total,
            'evaluated_predictions': evaluated,
            'direction_accuracy': direction_accuracy,
            'mean_absolute_error': mae,
            'root_mean_squared_error': rmse,
            'confidence_correlation': confidence_correlation,
            'best_prediction': metrics['best_prediction'],
            'worst_prediction': metrics['worst_prediction'],
            'last_updated': self.last_evaluation.isoformat()
        }
    
    def get_comparative_analysis(self) -> Dict[str, Any]:
        """
        Get comparative analysis across all models
        """
        model_stats = self.get_model_performance()
        
        if not model_stats:
            return {'status': 'no_data'}
        
        # Find best performing model
        best_model = None
        best_accuracy = 0
        
        for model, stats in model_stats.items():
            if isinstance(stats, dict) and 'direction_accuracy' in stats:
                if stats['direction_accuracy'] > best_accuracy:
                    best_accuracy = stats['direction_accuracy']
                    best_model = model
        
        # Calculate ensemble performance
        ensemble_predictions = defaultdict(list)
        for pred in self.predictions:
            if pred.actual_value is not None:
                key = f"{pred.symbol}_{pred.timestamp}"
                ensemble_predictions[key].append(pred)
        
        ensemble_correct = 0
        ensemble_total = 0
        
        for key, preds in ensemble_predictions.items():
            if len(preds) > 1:
                # Majority vote
                directions = [p.predicted_direction for p in preds]
                majority = max(set(directions), key=directions.count)
                actual = preds[0].actual_direction
                if majority == actual:
                    ensemble_correct += 1
                ensemble_total += 1
        
        ensemble_accuracy = ensemble_correct / ensemble_total if ensemble_total > 0 else 0
        
        return {
            'best_model': best_model,
            'best_accuracy': best_accuracy,
            'ensemble_accuracy': ensemble_accuracy,
            'model_comparison': model_stats,
            'total_models': len(model_stats),
            'total_predictions': sum(
                s.get('total_predictions', 0) 
                for s in model_stats.values() 
                if isinstance(s, dict)
            )
        }
    
    def export_metrics(self, filepath: str = "performance_metrics.json"):
        """
        Export performance metrics to file
        """
        try:
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'model_performance': self.get_model_performance(),
                'comparative_analysis': self.get_comparative_analysis(),
                'recent_predictions': [
                    {
                        'symbol': p.symbol,
                        'model': p.model_type,
                        'direction': p.predicted_direction,
                        'confidence': p.confidence,
                        'timestamp': p.timestamp.isoformat()
                    }
                    for p in list(self.predictions)[-100:]  # Last 100 predictions
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"📁 Exported metrics to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            return False


# Global instance
performance_tracker = EnhancedPerformanceTracker()

# Test function
async def test_performance_tracker():
    """Test the enhanced performance tracker"""
    print("🧪 Testing Enhanced Performance Tracker")
    print("=" * 50)
    
    # Track some test predictions
    test_predictions = [
        ("CBA.AX", "ensemble", 85.5, "up", 0.75),
        ("CBA.AX", "gnn", 84.8, "up", 0.82),
        ("CBA.AX", "lstm", 86.0, "up", 0.65),
        ("BHP.AX", "ensemble", 42.3, "down", 0.68),
        ("BHP.AX", "gnn", 41.9, "down", 0.71),
    ]
    
    for symbol, model, value, direction, confidence in test_predictions:
        pred_id = performance_tracker.track_prediction(
            symbol=symbol,
            model_type=model,
            predicted_value=value,
            predicted_direction=direction,
            confidence=confidence,
            timeframe="5d"
        )
        print(f"✅ Tracked: {pred_id}")
    
    # Simulate evaluation
    print("\n📊 Model Performance:")
    performance = performance_tracker.get_model_performance()
    for model, stats in performance.items():
        print(f"\n{model}:")
        if isinstance(stats, dict):
            for key, value in stats.items():
                print(f"  {key}: {value}")
    
    # Comparative analysis
    print("\n🔍 Comparative Analysis:")
    comparison = performance_tracker.get_comparative_analysis()
    print(f"  Best Model: {comparison.get('best_model')}")
    print(f"  Total Predictions: {comparison.get('total_predictions')}")
    
    print("\n✅ Performance tracker testing completed!")

if __name__ == "__main__":
    asyncio.run(test_performance_tracker())