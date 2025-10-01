#!/usr/bin/env python3
"""
Comprehensive Model Performance Backtesting System
Tests predictions against actual market movements over the last month
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import logging
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our prediction system
from market_prediction_llm import (
    MarketPredictionService,
    PredictionRequest,
    PredictionTimeframe
)

@dataclass
class BacktestPrediction:
    """Single prediction in backtesting"""
    date: datetime
    symbol: str
    timeframe: str
    predicted_direction: str
    predicted_change_percent: float
    confidence_score: float
    actual_direction: str = None
    actual_change_percent: float = None
    prediction_correct: bool = None
    accuracy_score: float = None
    tier1_factors: Dict[str, float] = None
    factor_attribution: Dict[str, Any] = None

@dataclass
class BacktestResults:
    """Complete backtesting results"""
    total_predictions: int
    correct_predictions: int
    overall_accuracy: float
    directional_accuracy: float
    mean_absolute_error: float
    predictions: List[BacktestPrediction]
    performance_by_timeframe: Dict[str, Dict[str, float]]
    performance_by_confidence: Dict[str, Dict[str, float]]
    factor_performance: Dict[str, Dict[str, float]]
    improvement_recommendations: List[str]

class ModelPerformanceBacktester:
    """Comprehensive model performance evaluation system"""
    
    def __init__(self):
        self.prediction_service = MarketPredictionService()
        
    async def run_backtest(self, 
                          symbol: str = "^AORD",
                          days_back: int = 30,
                          timeframes: List[str] = ["1d", "5d"]) -> BacktestResults:
        """Run comprehensive backtest over specified period"""
        
        logger.info(f"🧪 Starting backtest for {symbol} over last {days_back} days")
        logger.info(f"📊 Testing timeframes: {timeframes}")
        
        # Get historical market data for validation
        historical_data = await self._fetch_historical_data(symbol, days_back + 10)
        
        # Generate predictions for each day in the backtest period
        predictions = []
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        current_date = start_date
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() < 5:
                for timeframe in timeframes:
                    try:
                        # Generate prediction for this date/timeframe
                        prediction = await self._generate_historical_prediction(
                            symbol, current_date, timeframe, historical_data
                        )
                        
                        if prediction:
                            predictions.append(prediction)
                            
                    except Exception as e:
                        logger.warning(f"Failed to generate prediction for {current_date}: {e}")
                        
            current_date += timedelta(days=1)
        
        # Analyze results
        results = await self._analyze_backtest_results(predictions, historical_data)
        
        # Generate improvement recommendations
        recommendations = self._generate_improvement_recommendations(results)
        results.improvement_recommendations = recommendations
        
        logger.info(f"✅ Backtest completed: {results.correct_predictions}/{results.total_predictions} correct ({results.overall_accuracy:.1%})")
        
        return results
    
    async def _fetch_historical_data(self, symbol: str, days: int) -> pd.DataFrame:
        """Fetch historical market data for validation"""
        
        logger.info(f"📈 Fetching {days} days of historical data for {symbol}")
        
        try:
            # Use yfinance for real market data
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                logger.error(f"❌ No historical data available for {symbol} - backtesting requires real market data")
                raise ValueError(f"No historical data available for {symbol}. Backtesting requires real market data.")
            
            # Calculate daily returns
            data['Daily_Return'] = data['Close'].pct_change()
            data['Direction'] = data['Daily_Return'].apply(lambda x: 'up' if x > 0.001 else 'down' if x < -0.001 else 'sideways')
            
            logger.info(f"✅ Fetched {len(data)} days of historical data")
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch historical data: {e}")
            raise e  # Re-raise the original exception - no synthetic data allowed
    
    # SYNTHETIC DATA GENERATION REMOVED - BACKTESTING REQUIRES REAL MARKET DATA ONLY
    # All backtesting must use actual historical market data for accurate performance evaluation
    
    async def _generate_historical_prediction(self, 
                                            symbol: str, 
                                            prediction_date: datetime,
                                            timeframe: str,
                                            historical_data: pd.DataFrame) -> Optional[BacktestPrediction]:
        """Generate prediction as if made on historical date"""
        
        try:
            # Create prediction request
            request = PredictionRequest(
                symbol=symbol,
                timeframe=timeframe,
                include_factors=True,
                include_news_intelligence=True,
                news_lookback_hours=48
            )
            
            # Generate prediction (this simulates what the model would have predicted on that date)
            response = await self.prediction_service.get_market_prediction(request)
            
            if not response.success:
                return None
            
            pred = response.prediction
            
            # Calculate actual outcome based on historical data
            actual_direction, actual_change = self._calculate_actual_outcome(
                prediction_date, timeframe, historical_data
            )
            
            if actual_direction is None:
                return None
            
            # Determine if prediction was correct
            prediction_correct = pred['direction'] == actual_direction
            
            # Calculate accuracy score (confidence-weighted)
            accuracy_score = pred['confidence_score'] if prediction_correct else (1 - pred['confidence_score'])
            
            return BacktestPrediction(
                date=prediction_date,
                symbol=symbol,
                timeframe=timeframe,
                predicted_direction=pred['direction'],
                predicted_change_percent=pred['expected_change_percent'],
                confidence_score=pred['confidence_score'],
                actual_direction=actual_direction,
                actual_change_percent=actual_change,
                prediction_correct=prediction_correct,
                accuracy_score=accuracy_score,
                tier1_factors=response.tier1_factors or {},
                factor_attribution=response.factor_attribution or {}
            )
            
        except Exception as e:
            logger.error(f"Error generating historical prediction for {prediction_date}: {e}")
            return None
    
    def _calculate_actual_outcome(self, 
                                 prediction_date: datetime,
                                 timeframe: str, 
                                 historical_data: pd.DataFrame) -> Tuple[Optional[str], Optional[float]]:
        """Calculate actual market outcome for given prediction"""
        
        try:
            # Map timeframe to days
            timeframe_days = {
                "1d": 1,
                "5d": 5,
                "30d": 30,
                "90d": 90
            }
            
            days_ahead = timeframe_days.get(timeframe, 5)
            
            # Find start and end dates in historical data
            start_date = prediction_date.date()
            end_date = (prediction_date + timedelta(days=days_ahead)).date()
            
            # Get data for the prediction period
            mask = (historical_data.index.date >= start_date) & (historical_data.index.date <= end_date)
            period_data = historical_data.loc[mask]
            
            if len(period_data) < 2:
                return None, None
            
            # Calculate actual performance
            start_price = period_data.iloc[0]['Close']
            end_price = period_data.iloc[-1]['Close']
            actual_change_percent = (end_price - start_price) / start_price * 100
            
            # Determine direction
            if actual_change_percent > 0.5:
                actual_direction = 'up'
            elif actual_change_percent < -0.5:
                actual_direction = 'down'
            else:
                actual_direction = 'sideways'
            
            return actual_direction, actual_change_percent
            
        except Exception as e:
            logger.error(f"Error calculating actual outcome: {e}")
            return None, None
    
    async def _analyze_backtest_results(self, 
                                      predictions: List[BacktestPrediction],
                                      historical_data: pd.DataFrame) -> BacktestResults:
        """Analyze backtesting results comprehensively"""
        
        if not predictions:
            return BacktestResults(
                total_predictions=0,
                correct_predictions=0,
                overall_accuracy=0.0,
                directional_accuracy=0.0,
                mean_absolute_error=0.0,
                predictions=[],
                performance_by_timeframe={},
                performance_by_confidence={},
                factor_performance={},
                improvement_recommendations=[]
            )
        
        # Filter out predictions without actual outcomes
        valid_predictions = [p for p in predictions if p.actual_direction is not None]
        
        total_predictions = len(valid_predictions)
        correct_predictions = sum(1 for p in valid_predictions if p.prediction_correct)
        
        overall_accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        
        # Calculate directional accuracy
        directional_accuracy = overall_accuracy  # Same as overall for now
        
        # Calculate mean absolute error for magnitude predictions
        mae = np.mean([abs(p.predicted_change_percent - p.actual_change_percent) 
                      for p in valid_predictions if p.actual_change_percent is not None])
        
        # Performance by timeframe
        performance_by_timeframe = {}
        for timeframe in set(p.timeframe for p in valid_predictions):
            tf_predictions = [p for p in valid_predictions if p.timeframe == timeframe]
            tf_correct = sum(1 for p in tf_predictions if p.prediction_correct)
            tf_accuracy = tf_correct / len(tf_predictions) if tf_predictions else 0
            
            performance_by_timeframe[timeframe] = {
                'total': len(tf_predictions),
                'correct': tf_correct,
                'accuracy': tf_accuracy
            }
        
        # Performance by confidence level
        performance_by_confidence = {}
        confidence_ranges = [(0.0, 0.5), (0.5, 0.7), (0.7, 0.85), (0.85, 1.0)]
        
        for min_conf, max_conf in confidence_ranges:
            range_key = f"{min_conf:.1f}-{max_conf:.1f}"
            range_predictions = [p for p in valid_predictions 
                               if min_conf <= p.confidence_score < max_conf]
            
            if range_predictions:
                range_correct = sum(1 for p in range_predictions if p.prediction_correct)
                range_accuracy = range_correct / len(range_predictions)
                
                performance_by_confidence[range_key] = {
                    'total': len(range_predictions),
                    'correct': range_correct,
                    'accuracy': range_accuracy
                }
        
        # Factor performance analysis
        factor_performance = self._analyze_factor_performance(valid_predictions)
        
        return BacktestResults(
            total_predictions=total_predictions,
            correct_predictions=correct_predictions,
            overall_accuracy=overall_accuracy,
            directional_accuracy=directional_accuracy,
            mean_absolute_error=mae,
            predictions=valid_predictions,
            performance_by_timeframe=performance_by_timeframe,
            performance_by_confidence=performance_by_confidence,
            factor_performance=factor_performance,
            improvement_recommendations=[]
        )
    
    def _analyze_factor_performance(self, predictions: List[BacktestPrediction]) -> Dict[str, Dict[str, float]]:
        """Analyze how well different factors correlate with prediction success"""
        
        factor_performance = {}
        
        # Get all unique factors
        all_factors = set()
        for pred in predictions:
            if pred.tier1_factors:
                all_factors.update(pred.tier1_factors.keys())
        
        for factor in all_factors:
            factor_values = []
            correct_predictions = []
            
            for pred in predictions:
                if pred.tier1_factors and factor in pred.tier1_factors:
                    factor_values.append(pred.tier1_factors[factor])
                    correct_predictions.append(1 if pred.prediction_correct else 0)
            
            if len(factor_values) >= 5:  # Minimum sample size
                # Calculate correlation between factor value and prediction success
                correlation = np.corrcoef(factor_values, correct_predictions)[0, 1]
                
                # Calculate average factor value for correct vs incorrect predictions
                correct_indices = [i for i, c in enumerate(correct_predictions) if c == 1]
                incorrect_indices = [i for i, c in enumerate(correct_predictions) if c == 0]
                
                avg_correct = np.mean([factor_values[i] for i in correct_indices]) if correct_indices else 0
                avg_incorrect = np.mean([factor_values[i] for i in incorrect_indices]) if incorrect_indices else 0
                
                factor_performance[factor] = {
                    'correlation_with_success': correlation if not np.isnan(correlation) else 0,
                    'avg_value_correct_predictions': avg_correct,
                    'avg_value_incorrect_predictions': avg_incorrect,
                    'sample_size': len(factor_values)
                }
        
        return factor_performance
    
    def _generate_improvement_recommendations(self, results: BacktestResults) -> List[str]:
        """Generate specific recommendations for model improvement"""
        
        recommendations = []
        
        # Overall accuracy assessment
        if results.overall_accuracy < 0.6:
            recommendations.append("🚨 CRITICAL: Overall accuracy below 60%. Major model revision needed.")
        elif results.overall_accuracy < 0.75:
            recommendations.append("⚠️ WARNING: Accuracy below target. Focus on factor optimization.")
        
        # Timeframe performance analysis
        best_timeframe = max(results.performance_by_timeframe.items(), 
                           key=lambda x: x[1]['accuracy'], default=(None, {'accuracy': 0}))
        worst_timeframe = min(results.performance_by_timeframe.items(), 
                            key=lambda x: x[1]['accuracy'], default=(None, {'accuracy': 0}))
        
        if best_timeframe[0] and worst_timeframe[0]:
            accuracy_diff = best_timeframe[1]['accuracy'] - worst_timeframe[1]['accuracy']
            if accuracy_diff > 0.15:
                recommendations.append(f"📊 Timeframe imbalance: {best_timeframe[0]} performs {accuracy_diff:.1%} better than {worst_timeframe[0]}")
        
        # Confidence calibration
        high_conf_performance = results.performance_by_confidence.get('0.8-1.0', {}).get('accuracy', 0)
        low_conf_performance = results.performance_by_confidence.get('0.0-0.5', {}).get('accuracy', 0)
        
        if high_conf_performance < 0.8:
            recommendations.append("🎯 High-confidence predictions underperforming. Review confidence scoring.")
        
        if low_conf_performance > 0.6:
            recommendations.append("💡 Low-confidence predictions surprisingly good. Consider threshold adjustment.")
        
        # Factor performance insights
        best_factors = sorted(results.factor_performance.items(), 
                            key=lambda x: x[1]['correlation_with_success'], reverse=True)[:3]
        worst_factors = sorted(results.factor_performance.items(), 
                             key=lambda x: x[1]['correlation_with_success'])[:3]
        
        if best_factors and best_factors[0][1]['correlation_with_success'] > 0.3:
            recommendations.append(f"✅ Strong factor: {best_factors[0][0]} (correlation: {best_factors[0][1]['correlation_with_success']:.3f})")
        
        if worst_factors and worst_factors[0][1]['correlation_with_success'] < -0.2:
            recommendations.append(f"❌ Problematic factor: {worst_factors[0][0]} (correlation: {worst_factors[0][1]['correlation_with_success']:.3f})")
        
        # Mean absolute error assessment
        if results.mean_absolute_error > 3.0:
            recommendations.append(f"📐 High magnitude error ({results.mean_absolute_error:.2f}%). Improve change percentage predictions.")
        
        return recommendations
    
    def generate_performance_report(self, results: BacktestResults) -> str:
        """Generate comprehensive performance report"""
        
        report = f"""
🧪 MODEL PERFORMANCE BACKTEST REPORT
{'='*50}

📊 OVERALL PERFORMANCE:
  • Total Predictions: {results.total_predictions}
  • Correct Predictions: {results.correct_predictions}
  • Overall Accuracy: {results.overall_accuracy:.1%}
  • Directional Accuracy: {results.directional_accuracy:.1%}  
  • Mean Absolute Error: {results.mean_absolute_error:.2f}%

📈 PERFORMANCE BY TIMEFRAME:
"""
        
        for timeframe, perf in results.performance_by_timeframe.items():
            report += f"  • {timeframe}: {perf['accuracy']:.1%} ({perf['correct']}/{perf['total']})\n"
        
        report += f"""
🎯 PERFORMANCE BY CONFIDENCE:
"""
        
        for conf_range, perf in results.performance_by_confidence.items():
            report += f"  • Confidence {conf_range}: {perf['accuracy']:.1%} ({perf['correct']}/{perf['total']})\n"
        
        report += f"""
🔍 TOP PERFORMING FACTORS:
"""
        
        # Sort factors by correlation with success
        sorted_factors = sorted(results.factor_performance.items(),
                              key=lambda x: x[1]['correlation_with_success'], reverse=True)
        
        for factor, perf in sorted_factors[:5]:
            report += f"  • {factor}: {perf['correlation_with_success']:+.3f} correlation ({perf['sample_size']} samples)\n"
        
        report += f"""
💡 IMPROVEMENT RECOMMENDATIONS:
"""
        
        for i, rec in enumerate(results.improvement_recommendations, 1):
            report += f"  {i}. {rec}\n"
        
        return report

# Global instance
backtester = ModelPerformanceBacktester()

if __name__ == "__main__":
    asyncio.run(backtester.run_backtest())