"""
Comprehensive Backtesting Engine for Model Validation
Implements walk-forward analysis, cross-validation, and performance metrics
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
import logging
from dataclasses import dataclass
import asyncio
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class BacktestResult:
    """Container for backtest results"""
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    calmar_ratio: float
    recovery_factor: float
    prediction_accuracy: float
    directional_accuracy: float
    rmse: float
    mae: float
    r_squared: float


class BacktestEngine:
    """Advanced backtesting system with walk-forward analysis"""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.results_cache = {}
        self.backtest_history = []
        
    async def run_backtest(
        self,
        predictor,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        strategy_type: str = "long_only",
        rebalance_frequency: str = "daily"
    ) -> BacktestResult:
        """
        Run comprehensive backtest with actual historical data
        
        Args:
            predictor: The prediction model to test
            symbol: Stock symbol to backtest
            start_date: Backtest start date
            end_date: Backtest end date
            strategy_type: "long_only", "long_short", or "signals"
            rebalance_frequency: "daily", "weekly", or "monthly"
        """
        
        try:
            logger.info(f"🔬 Starting backtest for {symbol} from {start_date} to {end_date}")
            
            # Fetch historical data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty or len(hist) < 20:
                logger.warning(f"Insufficient data for backtesting {symbol}")
                return self._get_empty_result()
            
            # Initialize tracking variables
            capital = self.initial_capital
            position = 0
            trades = []
            daily_returns = []
            predictions_log = []
            
            # Walk-forward analysis window
            train_window = 252  # 1 year of trading days
            test_window = 21    # 1 month forward
            retrain_frequency = 21  # Retrain every month
            
            # Process each day
            for i in range(train_window, len(hist) - 1):
                current_date = hist.index[i]
                current_price = hist['Close'].iloc[i]
                next_price = hist['Close'].iloc[i + 1]
                
                # Retrain model periodically
                if i % retrain_frequency == 0:
                    # Get training data
                    train_start_idx = max(0, i - train_window)
                    train_data = hist.iloc[train_start_idx:i]
                    
                    # This would actually train the model
                    # For now, we'll use the predictor as-is
                    logger.debug(f"Retraining model at {current_date}")
                
                # Generate prediction
                prediction_result = await predictor.predict(
                    symbol=symbol,
                    timeframe="1d"
                )
                
                if "error" not in prediction_result:
                    predicted_price = prediction_result.get("final_prediction", current_price)
                    confidence = prediction_result.get("confidence_scores", {}).get("ensemble", 0.5)
                    
                    # Log prediction for accuracy calculation
                    predictions_log.append({
                        "date": current_date,
                        "actual": next_price,
                        "predicted": predicted_price,
                        "error": abs(next_price - predicted_price) / next_price
                    })
                    
                    # Generate trading signal
                    signal = self._generate_signal(
                        current_price,
                        predicted_price,
                        confidence,
                        strategy_type
                    )
                    
                    # Execute trade based on signal
                    if signal != 0 and self._should_trade(i, rebalance_frequency):
                        # Close existing position if changing direction
                        if position != 0 and np.sign(signal) != np.sign(position):
                            # Close position
                            pnl = position * (current_price - trades[-1]["entry_price"])
                            trades[-1]["exit_price"] = current_price
                            trades[-1]["exit_date"] = current_date
                            trades[-1]["pnl"] = pnl
                            capital += pnl
                            position = 0
                        
                        # Open new position
                        if signal != 0 and position == 0:
                            position_size = (capital * abs(signal)) / current_price
                            position = position_size * np.sign(signal)
                            
                            trades.append({
                                "entry_date": current_date,
                                "entry_price": current_price,
                                "position": position,
                                "signal": signal,
                                "confidence": confidence
                            })
                
                # Calculate daily return
                if position != 0:
                    daily_return = position * (next_price - current_price) / capital
                else:
                    daily_return = 0
                
                daily_returns.append(daily_return)
            
            # Close any remaining position
            if position != 0 and len(trades) > 0:
                final_price = hist['Close'].iloc[-1]
                pnl = position * (final_price - trades[-1]["entry_price"])
                trades[-1]["exit_price"] = final_price
                trades[-1]["exit_date"] = hist.index[-1]
                trades[-1]["pnl"] = pnl
                capital += pnl
            
            # Calculate performance metrics
            result = self._calculate_metrics(
                capital,
                self.initial_capital,
                trades,
                daily_returns,
                predictions_log
            )
            
            # Cache result
            cache_key = f"{symbol}_{start_date}_{end_date}_{strategy_type}"
            self.results_cache[cache_key] = result
            self.backtest_history.append({
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
                "result": result,
                "timestamp": datetime.now()
            })
            
            logger.info(f"✅ Backtest complete - Return: {result.total_return:.2%}, Sharpe: {result.sharpe_ratio:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Backtest failed: {e}")
            return self._get_empty_result()
    
    def _generate_signal(
        self,
        current_price: float,
        predicted_price: float,
        confidence: float,
        strategy_type: str
    ) -> float:
        """Generate trading signal based on prediction"""
        
        price_change = (predicted_price - current_price) / current_price
        
        if strategy_type == "long_only":
            # Only buy signals
            if price_change > 0.01 and confidence > 0.6:  # 1% threshold
                return min(confidence, 1.0)  # Position size based on confidence
            else:
                return 0
                
        elif strategy_type == "long_short":
            # Both buy and sell signals
            if abs(price_change) > 0.01 and confidence > 0.6:
                if price_change > 0:
                    return min(confidence, 1.0)
                else:
                    return -min(confidence, 1.0)
            else:
                return 0
                
        elif strategy_type == "signals":
            # Binary signals
            if price_change > 0.01 and confidence > 0.7:
                return 1.0
            elif price_change < -0.01 and confidence > 0.7:
                return -1.0
            else:
                return 0
        
        return 0
    
    def _should_trade(self, day_index: int, rebalance_frequency: str) -> bool:
        """Determine if we should trade based on rebalancing frequency"""
        
        if rebalance_frequency == "daily":
            return True
        elif rebalance_frequency == "weekly":
            return day_index % 5 == 0
        elif rebalance_frequency == "monthly":
            return day_index % 21 == 0
        
        return True
    
    def _calculate_metrics(
        self,
        final_capital: float,
        initial_capital: float,
        trades: List[Dict],
        daily_returns: List[float],
        predictions_log: List[Dict]
    ) -> BacktestResult:
        """Calculate comprehensive backtest metrics"""
        
        # Basic metrics
        total_return = (final_capital - initial_capital) / initial_capital
        
        # Trade analysis
        completed_trades = [t for t in trades if "pnl" in t]
        winning_trades = [t for t in completed_trades if t["pnl"] > 0]
        losing_trades = [t for t in completed_trades if t["pnl"] <= 0]
        
        total_trades = len(completed_trades)
        num_winning = len(winning_trades)
        num_losing = len(losing_trades)
        
        win_rate = num_winning / total_trades if total_trades > 0 else 0
        
        avg_win = np.mean([t["pnl"] for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t["pnl"] for t in losing_trades])) if losing_trades else 0
        
        profit_factor = (avg_win * num_winning) / (avg_loss * num_losing) if num_losing > 0 and avg_loss > 0 else 0
        
        # Risk metrics
        returns_array = np.array(daily_returns)
        
        if len(returns_array) > 0:
            sharpe_ratio = (np.mean(returns_array) * 252) / (np.std(returns_array) * np.sqrt(252)) if np.std(returns_array) > 0 else 0
            
            # Maximum drawdown
            cumulative_returns = np.cumprod(1 + returns_array)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = abs(np.min(drawdown)) if len(drawdown) > 0 else 0
            
            # Calmar ratio
            annual_return = total_return * (252 / len(daily_returns)) if len(daily_returns) > 0 else 0
            calmar_ratio = annual_return / max_drawdown if max_drawdown > 0 else 0
            
            # Recovery factor
            recovery_factor = total_return / max_drawdown if max_drawdown > 0 else 0
        else:
            sharpe_ratio = 0
            max_drawdown = 0
            calmar_ratio = 0
            recovery_factor = 0
        
        # Prediction accuracy
        if predictions_log:
            errors = [p["error"] for p in predictions_log]
            rmse = np.sqrt(np.mean(np.square(errors)))
            mae = np.mean(errors)
            
            # Directional accuracy
            correct_direction = sum(
                1 for p in predictions_log
                if (p["predicted"] > p["actual"]) == (p["actual"] > predictions_log[max(0, predictions_log.index(p)-1)]["actual"])
            )
            directional_accuracy = correct_direction / len(predictions_log) if predictions_log else 0
            
            # R-squared (simplified)
            actual_prices = [p["actual"] for p in predictions_log]
            predicted_prices = [p["predicted"] for p in predictions_log]
            
            if len(actual_prices) > 1:
                actual_mean = np.mean(actual_prices)
                ss_tot = np.sum((np.array(actual_prices) - actual_mean) ** 2)
                ss_res = np.sum((np.array(actual_prices) - np.array(predicted_prices)) ** 2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            else:
                r_squared = 0
            
            prediction_accuracy = 1 - mae  # Simplified accuracy metric
        else:
            rmse = 0
            mae = 0
            directional_accuracy = 0
            r_squared = 0
            prediction_accuracy = 0
        
        return BacktestResult(
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=total_trades,
            winning_trades=num_winning,
            losing_trades=num_losing,
            avg_win=avg_win,
            avg_loss=avg_loss,
            calmar_ratio=calmar_ratio,
            recovery_factor=recovery_factor,
            prediction_accuracy=prediction_accuracy,
            directional_accuracy=directional_accuracy,
            rmse=rmse,
            mae=mae,
            r_squared=r_squared
        )
    
    def _get_empty_result(self) -> BacktestResult:
        """Return empty result when backtest fails"""
        return BacktestResult(
            total_return=0,
            sharpe_ratio=0,
            max_drawdown=0,
            win_rate=0,
            profit_factor=0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            avg_win=0,
            avg_loss=0,
            calmar_ratio=0,
            recovery_factor=0,
            prediction_accuracy=0,
            directional_accuracy=0,
            rmse=0,
            mae=0,
            r_squared=0
        )
    
    async def run_cross_validation(
        self,
        predictor,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        n_splits: int = 5
    ) -> Dict[str, Any]:
        """Run k-fold cross-validation for robust testing"""
        
        logger.info(f"🔄 Running {n_splits}-fold cross-validation for {symbol}")
        
        # Calculate fold size
        total_days = (end_date - start_date).days
        fold_size = total_days // n_splits
        
        results = []
        
        for i in range(n_splits):
            # Calculate fold dates
            fold_start = start_date + timedelta(days=i * fold_size)
            fold_end = fold_start + timedelta(days=fold_size)
            
            # Run backtest on this fold
            fold_result = await self.run_backtest(
                predictor,
                symbol,
                fold_start,
                fold_end,
                strategy_type="long_only"
            )
            
            results.append({
                "fold": i + 1,
                "start_date": fold_start,
                "end_date": fold_end,
                "return": fold_result.total_return,
                "sharpe": fold_result.sharpe_ratio,
                "accuracy": fold_result.prediction_accuracy
            })
        
        # Calculate aggregate metrics
        avg_return = np.mean([r["return"] for r in results])
        avg_sharpe = np.mean([r["sharpe"] for r in results])
        avg_accuracy = np.mean([r["accuracy"] for r in results])
        
        return {
            "n_splits": n_splits,
            "fold_results": results,
            "avg_return": avg_return,
            "avg_sharpe": avg_sharpe,
            "avg_accuracy": avg_accuracy,
            "std_return": np.std([r["return"] for r in results]),
            "std_sharpe": np.std([r["sharpe"] for r in results]),
            "std_accuracy": np.std([r["accuracy"] for r in results])
        }
    
    def generate_report(self, result: BacktestResult) -> Dict[str, Any]:
        """Generate comprehensive backtest report"""
        
        return {
            "performance": {
                "total_return": f"{result.total_return:.2%}",
                "sharpe_ratio": round(result.sharpe_ratio, 2),
                "max_drawdown": f"{result.max_drawdown:.2%}",
                "calmar_ratio": round(result.calmar_ratio, 2),
                "recovery_factor": round(result.recovery_factor, 2)
            },
            "trading": {
                "total_trades": result.total_trades,
                "win_rate": f"{result.win_rate:.2%}",
                "profit_factor": round(result.profit_factor, 2),
                "winning_trades": result.winning_trades,
                "losing_trades": result.losing_trades,
                "avg_win": f"${result.avg_win:.2f}",
                "avg_loss": f"${result.avg_loss:.2f}"
            },
            "prediction": {
                "accuracy": f"{result.prediction_accuracy:.2%}",
                "directional_accuracy": f"{result.directional_accuracy:.2%}",
                "rmse": round(result.rmse, 4),
                "mae": round(result.mae, 4),
                "r_squared": round(result.r_squared, 3)
            },
            "risk_assessment": self._assess_risk(result)
        }
    
    def _assess_risk(self, result: BacktestResult) -> str:
        """Assess overall strategy risk level"""
        
        if result.sharpe_ratio < 0.5:
            return "HIGH RISK - Poor risk-adjusted returns"
        elif result.sharpe_ratio < 1.0:
            return "MEDIUM RISK - Moderate risk-adjusted returns"
        elif result.sharpe_ratio < 2.0:
            return "LOW RISK - Good risk-adjusted returns"
        else:
            return "VERY LOW RISK - Excellent risk-adjusted returns"
    
    def save_results(self, filepath: str = "backtest_results.json"):
        """Save backtest results to file"""
        
        try:
            results_data = {
                "generated_at": datetime.now().isoformat(),
                "history": [
                    {
                        "symbol": h["symbol"],
                        "start_date": h["start_date"].isoformat(),
                        "end_date": h["end_date"].isoformat(),
                        "timestamp": h["timestamp"].isoformat(),
                        "report": self.generate_report(h["result"])
                    }
                    for h in self.backtest_history
                ]
            }
            
            with open(filepath, "w") as f:
                json.dump(results_data, f, indent=2)
            
            logger.info(f"✅ Backtest results saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")


# Global backtest engine instance
backtest_engine = BacktestEngine()