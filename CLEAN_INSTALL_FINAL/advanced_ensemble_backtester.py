#!/usr/bin/env python3
"""
Advanced Ensemble Predictor Backtesting System
Comprehensive validation of LSTM + Random Forest + ARIMA + Quantile Regression models
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging
import json
import yfinance as yf
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the advanced ensemble predictor
from advanced_ensemble_predictor import (
    AdvancedEnsemblePredictor,
    PredictionHorizon,
    PredictionResult
)

from multi_source_data_service import multi_source_aggregator

@dataclass
class EnsembleBacktestResult:
    """Single ensemble prediction backtest result"""
    date: datetime
    symbol: str
    timeframe: str
    horizon: PredictionHorizon
    
    # Predictions
    predicted_direction: str
    predicted_return: float
    confidence_score: float
    risk_adjusted_return: float
    volatility_estimate: float
    
    # Model ensemble weights
    lstm_weight: float
    random_forest_weight: float
    arima_weight: float
    quantile_weight: float
    
    # Actual outcomes
    actual_direction: Optional[str] = None
    actual_return: Optional[float] = None
    
    # Performance metrics
    direction_correct: Optional[bool] = None
    return_error: Optional[float] = None
    confidence_calibration: Optional[float] = None
    
    # Feature importance
    feature_importance: Optional[Dict[str, float]] = None
    uncertainty_score: float = 0.0

@dataclass
class EnsembleBacktestSummary:
    """Complete ensemble backtesting summary"""
    total_predictions: int
    timeframe_performance: Dict[str, Dict[str, float]]
    model_performance: Dict[str, Dict[str, float]]
    
    # Overall metrics
    overall_accuracy: float
    mean_return_error: float
    rmse_return: float
    sharpe_ratio: float
    
    # Confidence calibration
    confidence_reliability: float
    overconfidence_ratio: float
    
    # Model ensemble analysis
    best_performing_model: str
    model_weight_stability: Dict[str, float]
    
    # Risk assessment accuracy
    volatility_prediction_accuracy: float
    drawdown_prediction_accuracy: float
    
    # Recommendations
    improvement_recommendations: List[str]

class AdvancedEnsembleBacktester:
    """Comprehensive backtesting for the advanced ensemble predictor"""
    
    def __init__(self):
        self.predictor = AdvancedEnsemblePredictor()
        
    async def run_comprehensive_backtest(self, 
                                       symbol: str = "^AORD",
                                       days_back: int = 60,
                                       test_horizons: List[str] = ["1d", "5d", "30d"]) -> EnsembleBacktestSummary:
        """Run comprehensive backtesting of the ensemble predictor"""
        
        logger.info(f"🧪 Starting comprehensive ensemble backtest for {symbol}")
        logger.info(f"📊 Testing {days_back} days across horizons: {test_horizons}")
        
        # Get historical market data
        historical_data = await self._fetch_comprehensive_historical_data(symbol, days_back + 30)
        
        # Run predictions for each day/horizon combination
        all_results = []
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        current_date = start_date
        prediction_count = 0
        
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() < 5:
                for timeframe in test_horizons:
                    try:
                        result = await self._generate_ensemble_backtest_prediction(
                            symbol, current_date, timeframe, historical_data
                        )
                        
                        if result:
                            all_results.append(result)
                            prediction_count += 1
                            
                            if prediction_count % 10 == 0:
                                logger.info(f"🔄 Generated {prediction_count} predictions...")
                                
                    except Exception as e:
                        logger.warning(f"Failed ensemble prediction for {current_date} ({timeframe}): {e}")
                        
            current_date += timedelta(days=1)
        
        logger.info(f"✅ Generated {len(all_results)} ensemble predictions")
        
        # Calculate actual outcomes
        await self._calculate_actual_outcomes(all_results, historical_data)
        
        # Analyze comprehensive results
        summary = await self._analyze_ensemble_performance(all_results)
        
        # Generate improvement recommendations
        summary.improvement_recommendations = self._generate_ensemble_recommendations(all_results, summary)
        
        logger.info(f"📈 Ensemble Backtest Complete: {summary.overall_accuracy:.1%} accuracy")
        
        return summary
    
    async def _fetch_comprehensive_historical_data(self, symbol: str, days: int) -> pd.DataFrame:
        """Fetch comprehensive historical data for backtesting"""
        
        logger.info(f"📈 Fetching {days} days of comprehensive market data...")
        
        try:
            # Use yfinance for reliable historical data
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get detailed OHLCV data
            data = ticker.history(start=start_date, end=end_date, interval='1d')
            
            if data.empty:
                logger.error(f"❌ No real historical data available for {symbol} - cannot perform backtesting without real data")
                raise ValueError(f"No historical data available for {symbol}. Backtesting requires real market data.")
            
            # Calculate technical indicators for backtesting
            data['Daily_Return'] = data['Close'].pct_change()
            data['Volatility_20d'] = data['Daily_Return'].rolling(20).std()
            data['SMA_20'] = data['Close'].rolling(20).mean()
            data['SMA_50'] = data['Close'].rolling(50).mean()
            data['RSI'] = self._calculate_rsi(data['Close'])
            
            # Classify directions
            data['Direction'] = data['Daily_Return'].apply(
                lambda x: 'up' if x > 0.005 else 'down' if x < -0.005 else 'sideways'
            )
            
            logger.info(f"✅ Loaded {len(data)} days of comprehensive market data")
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch historical data: {e}")
            raise e  # Re-raise the original exception - no synthetic data allowed
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate RSI technical indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    # SYNTHETIC DATA GENERATION REMOVED - LIVE DATA ONLY POLICY
    # Backtesting requires real historical market data for accurate results
    
    async def _generate_ensemble_backtest_prediction(self,
                                                   symbol: str,
                                                   prediction_date: datetime,
                                                   timeframe: str,
                                                   historical_data: pd.DataFrame) -> Optional[EnsembleBacktestResult]:
        """Generate ensemble prediction for backtesting"""
        
        try:
            # Convert timeframe to horizon
            horizon_map = {
                "1d": PredictionHorizon.INTRADAY,
                "5d": PredictionHorizon.SHORT_TERM,
                "30d": PredictionHorizon.MEDIUM_TERM,
                "90d": PredictionHorizon.LONG_TERM
            }
            
            horizon = horizon_map.get(timeframe, PredictionHorizon.SHORT_TERM)
            
            # Simulate historical market data context up to prediction date
            context_data = historical_data[historical_data.index.date <= prediction_date.date()]
            
            if len(context_data) < 20:  # Need minimum context
                return None
            
            # Convert to format expected by predictor
            market_data_dict = {
                "data_points": [
                    {
                        "timestamp": row.name.isoformat(),
                        "open": float(row['Open']),
                        "high": float(row['High']),
                        "low": float(row['Low']),
                        "close": float(row['Close']),
                        "volume": int(row['Volume'])
                    }
                    for _, row in context_data.tail(100).iterrows()  # Last 100 days context
                ]
            }
            
            # Generate ensemble prediction
            result = await self.predictor.generate_advanced_prediction(
                symbol=symbol,
                timeframe=timeframe,
                market_data=market_data_dict,
                external_factors={}
            )
            
            # Extract model weights
            model_weights = result.model_ensemble_weights
            
            return EnsembleBacktestResult(
                date=prediction_date,
                symbol=symbol,
                timeframe=timeframe,
                horizon=horizon,
                predicted_direction=result.direction,
                predicted_return=result.expected_return,
                confidence_score=1.0 - result.uncertainty_score,
                risk_adjusted_return=result.risk_adjusted_return,
                volatility_estimate=result.volatility_estimate,
                lstm_weight=model_weights.get('lstm', 0.0),
                random_forest_weight=model_weights.get('random_forest', 0.0),
                arima_weight=model_weights.get('arima', 0.0),
                quantile_weight=model_weights.get('quantile_regression', 0.0),
                feature_importance=result.feature_importance,
                uncertainty_score=result.uncertainty_score
            )
            
        except Exception as e:
            logger.error(f"Error generating ensemble backtest prediction: {e}")
            return None
    
    async def _calculate_actual_outcomes(self, results: List[EnsembleBacktestResult], historical_data: pd.DataFrame):
        """Calculate actual market outcomes for all predictions"""
        
        logger.info("📊 Calculating actual market outcomes...")
        
        timeframe_days = {"1d": 1, "5d": 5, "30d": 30, "90d": 90}
        
        for result in results:
            try:
                days_ahead = timeframe_days.get(result.timeframe, 5)
                
                start_date = result.date.date()
                end_date = (result.date + timedelta(days=days_ahead)).date()
                
                # Get actual price movement
                mask = (historical_data.index.date >= start_date) & (historical_data.index.date <= end_date)
                period_data = historical_data.loc[mask]
                
                if len(period_data) >= 2:
                    start_price = period_data.iloc[0]['Close']
                    end_price = period_data.iloc[-1]['Close']
                    actual_return = (end_price - start_price) / start_price
                    
                    # Determine direction
                    if actual_return > 0.005:
                        actual_direction = 'up'
                    elif actual_return < -0.005:
                        actual_direction = 'down'
                    else:
                        actual_direction = 'sideways'
                    
                    # Update result
                    result.actual_direction = actual_direction
                    result.actual_return = actual_return
                    result.direction_correct = (result.predicted_direction == actual_direction)
                    result.return_error = abs(result.predicted_return - actual_return)
                    
                    # Confidence calibration (higher confidence should correlate with accuracy)
                    if result.direction_correct:
                        result.confidence_calibration = result.confidence_score
                    else:
                        result.confidence_calibration = 1.0 - result.confidence_score
                        
            except Exception as e:
                logger.warning(f"Failed to calculate actual outcome for {result.date}: {e}")
    
    async def _analyze_ensemble_performance(self, results: List[EnsembleBacktestResult]) -> EnsembleBacktestSummary:
        """Analyze comprehensive ensemble performance"""
        
        # Filter valid results
        valid_results = [r for r in results if r.actual_direction is not None]
        
        if not valid_results:
            return EnsembleBacktestSummary(
                total_predictions=0,
                timeframe_performance={},
                model_performance={},
                overall_accuracy=0.0,
                mean_return_error=0.0,
                rmse_return=0.0,
                sharpe_ratio=0.0,
                confidence_reliability=0.0,
                overconfidence_ratio=0.0,
                best_performing_model="unknown",
                model_weight_stability={},
                volatility_prediction_accuracy=0.0,
                drawdown_prediction_accuracy=0.0,
                improvement_recommendations=[]
            )
        
        # Overall metrics
        correct_predictions = sum(1 for r in valid_results if r.direction_correct)
        overall_accuracy = correct_predictions / len(valid_results)
        
        return_errors = [r.return_error for r in valid_results if r.return_error is not None]
        mean_return_error = np.mean(return_errors) if return_errors else 0.0
        rmse_return = np.sqrt(np.mean([e**2 for e in return_errors])) if return_errors else 0.0
        
        # Calculate Sharpe-like ratio for predictions
        predicted_returns = [r.predicted_return for r in valid_results]
        actual_returns = [r.actual_return for r in valid_results if r.actual_return is not None]
        
        if predicted_returns and actual_returns:
            pred_mean = np.mean(predicted_returns)
            pred_std = np.std(predicted_returns)
            sharpe_ratio = pred_mean / pred_std if pred_std > 0 else 0.0
        else:
            sharpe_ratio = 0.0
        
        # Performance by timeframe
        timeframe_performance = {}
        for timeframe in set(r.timeframe for r in valid_results):
            tf_results = [r for r in valid_results if r.timeframe == timeframe]
            tf_correct = sum(1 for r in tf_results if r.direction_correct)
            tf_accuracy = tf_correct / len(tf_results)
            tf_return_error = np.mean([r.return_error for r in tf_results if r.return_error is not None])
            
            timeframe_performance[timeframe] = {
                'accuracy': tf_accuracy,
                'return_error': tf_return_error,
                'sample_size': len(tf_results)
            }
        
        # Model performance analysis
        model_performance = {}
        models = ['lstm', 'random_forest', 'arima', 'quantile']
        
        for model in models:
            # Weight analysis
            weights = [getattr(r, f'{model}_weight') for r in valid_results]
            avg_weight = np.mean(weights) if weights else 0.0
            weight_stability = 1.0 - (np.std(weights) if len(weights) > 1 else 0.0)
            
            # Performance when this model dominates
            dominant_results = [r for r in valid_results if getattr(r, f'{model}_weight') > 0.5]
            if dominant_results:
                dominant_accuracy = sum(1 for r in dominant_results if r.direction_correct) / len(dominant_results)
            else:
                dominant_accuracy = 0.0
            
            model_performance[model] = {
                'average_weight': avg_weight,
                'weight_stability': weight_stability,
                'dominant_accuracy': dominant_accuracy,
                'dominant_samples': len(dominant_results)
            }
        
        # Find best performing model
        best_model = max(model_performance.items(), key=lambda x: x[1]['dominant_accuracy'])[0]
        
        # Confidence calibration
        calibration_scores = [r.confidence_calibration for r in valid_results if r.confidence_calibration is not None]
        confidence_reliability = np.mean(calibration_scores) if calibration_scores else 0.0
        
        # Overconfidence analysis
        high_conf_results = [r for r in valid_results if r.confidence_score > 0.8]
        if high_conf_results:
            high_conf_accuracy = sum(1 for r in high_conf_results if r.direction_correct) / len(high_conf_results)
            overconfidence_ratio = 0.8 / high_conf_accuracy if high_conf_accuracy > 0 else float('inf')
        else:
            overconfidence_ratio = 1.0
        
        # Model weight stability
        model_weight_stability = {
            model: model_performance[model]['weight_stability'] for model in models
        }
        
        return EnsembleBacktestSummary(
            total_predictions=len(valid_results),
            timeframe_performance=timeframe_performance,
            model_performance=model_performance,
            overall_accuracy=overall_accuracy,
            mean_return_error=mean_return_error,
            rmse_return=rmse_return,
            sharpe_ratio=sharpe_ratio,
            confidence_reliability=confidence_reliability,
            overconfidence_ratio=overconfidence_ratio,
            best_performing_model=best_model,
            model_weight_stability=model_weight_stability,
            volatility_prediction_accuracy=0.8,  # Placeholder - would need more complex analysis
            drawdown_prediction_accuracy=0.75,  # Placeholder - would need more complex analysis
            improvement_recommendations=[]
        )
    
    def _generate_ensemble_recommendations(self, 
                                         results: List[EnsembleBacktestResult],
                                         summary: EnsembleBacktestSummary) -> List[str]:
        """Generate specific recommendations for ensemble improvement"""
        
        recommendations = []
        
        # Overall accuracy assessment
        if summary.overall_accuracy < 0.6:
            recommendations.append("🚨 CRITICAL: Ensemble accuracy below 60%. Major revision needed.")
        elif summary.overall_accuracy < 0.75:
            recommendations.append("⚠️ WARNING: Accuracy below target. Optimize model weights.")
        else:
            recommendations.append("✅ GOOD: Accuracy above 75%. Fine-tune for optimization.")
        
        # Model-specific recommendations
        best_model_perf = summary.model_performance[summary.best_performing_model]
        if best_model_perf['average_weight'] < 0.3:
            recommendations.append(f"📈 Increase weight for {summary.best_performing_model} model (currently {best_model_perf['average_weight']:.1%})")
        
        # Timeframe recommendations
        worst_timeframe = min(summary.timeframe_performance.items(), key=lambda x: x[1]['accuracy'])
        if worst_timeframe[1]['accuracy'] < 0.6:
            recommendations.append(f"🎯 Focus on {worst_timeframe[0]} predictions (accuracy: {worst_timeframe[1]['accuracy']:.1%})")
        
        # Confidence calibration
        if summary.confidence_reliability < 0.7:
            recommendations.append("🎲 Improve confidence calibration - predictions not well-calibrated")
        
        if summary.overconfidence_ratio > 1.2:
            recommendations.append("😤 Reduce overconfidence - high confidence predictions underperforming")
        
        # Return prediction accuracy
        if summary.mean_return_error > 0.03:  # 3% average error
            recommendations.append(f"📐 Improve return magnitude predictions (current error: {summary.mean_return_error:.1%})")
        
        return recommendations
    
    def generate_comprehensive_report(self, summary: EnsembleBacktestSummary) -> str:
        """Generate comprehensive ensemble performance report"""
        
        report = f"""
🤖 ADVANCED ENSEMBLE PREDICTOR BACKTEST REPORT
{'='*60}

📊 OVERALL PERFORMANCE:
  • Total Predictions: {summary.total_predictions}
  • Overall Accuracy: {summary.overall_accuracy:.1%}
  • Mean Return Error: {summary.mean_return_error:.2%}
  • RMSE Return: {summary.rmse_return:.2%}
  • Sharpe Ratio: {summary.sharpe_ratio:.3f}

🎯 CONFIDENCE ANALYSIS:
  • Confidence Reliability: {summary.confidence_reliability:.1%}
  • Overconfidence Ratio: {summary.overconfidence_ratio:.2f}

🏆 MODEL ENSEMBLE ANALYSIS:
  • Best Performing Model: {summary.best_performing_model.upper()}
"""
        
        for model, perf in summary.model_performance.items():
            report += f"  • {model.upper()}: {perf['average_weight']:.1%} avg weight, {perf['dominant_accuracy']:.1%} accuracy when dominant\n"
        
        report += f"""
📈 PERFORMANCE BY TIMEFRAME:
"""
        
        for timeframe, perf in summary.timeframe_performance.items():
            report += f"  • {timeframe}: {perf['accuracy']:.1%} accuracy, {perf['return_error']:.2%} return error ({perf['sample_size']} samples)\n"
        
        report += f"""
💡 IMPROVEMENT RECOMMENDATIONS:
"""
        
        for i, rec in enumerate(summary.improvement_recommendations, 1):
            report += f"  {i}. {rec}\n"
        
        report += f"""
🔬 MODEL WEIGHT STABILITY:
"""
        for model, stability in summary.model_weight_stability.items():
            report += f"  • {model.upper()}: {stability:.1%} stability\n"
        
        return report

# Global instance
ensemble_backtester = AdvancedEnsembleBacktester()

if __name__ == "__main__":
    async def main():
        print("🚀 Starting Advanced Ensemble Backtesting")
        
        # Run comprehensive backtest
        summary = await ensemble_backtester.run_comprehensive_backtest(
            symbol="^AORD",
            days_back=30,  # Test last 30 days
            test_horizons=["1d", "5d", "30d"]
        )
        
        # Generate and display report
        report = ensemble_backtester.generate_comprehensive_report(summary)
        print(report)
        
        # Save results
        results_file = f"ensemble_backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert to JSON-serializable format
        results_dict = {
            'timestamp': datetime.now().isoformat(),
            'overall_accuracy': summary.overall_accuracy,
            'mean_return_error': summary.mean_return_error,
            'model_performance': summary.model_performance,
            'timeframe_performance': summary.timeframe_performance,
            'recommendations': summary.improvement_recommendations
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_dict, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")
        print(f"🎯 Final Score: {summary.overall_accuracy:.1%} accuracy with {summary.mean_return_error:.2%} return error")
        
    asyncio.run(main())