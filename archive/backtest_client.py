#!/usr/bin/env python3
"""
Backtesting Client - Run from your personal computer
This script allows you to run backtests and training from your local machine
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
import matplotlib.pyplot as plt

class BacktestClient:
    """Client for running backtests from your personal computer"""
    
    def __init__(self, api_url: str = "https://8000-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev"):
        """
        Initialize the backtest client
        
        Args:
            api_url: The URL of the running backend API
        """
        self.api_url = api_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def train_models(self, symbols: List[str], training_days: int = 730) -> Dict[str, Any]:
        """
        Train models for specified symbols
        
        Args:
            symbols: List of stock symbols to train
            training_days: Number of days of historical data to use
            
        Returns:
            Training results
        """
        print(f"🚀 Training models for {symbols}...")
        
        response = self.session.post(
            f"{self.api_url}/api/train-models",
            json={"symbols": symbols, "training_days": training_days}
        )
        
        if response.status_code == 200:
            print("✅ Training initiated successfully")
            return response.json()
        else:
            print(f"❌ Training failed: {response.status_code}")
            return {"error": response.text}
    
    def run_backtest(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        strategy_type: str = "long_only"
    ) -> Dict[str, Any]:
        """
        Run a backtest for a symbol
        
        Args:
            symbol: Stock symbol to backtest
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            strategy_type: Trading strategy ("long_only", "long_short", "signals")
            
        Returns:
            Backtest results and metrics
        """
        print(f"📊 Running backtest for {symbol} from {start_date} to {end_date}")
        
        response = self.session.post(
            f"{self.api_url}/api/backtest",
            json={
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
                "strategy_type": strategy_type
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            self._print_backtest_results(result)
            return result
        else:
            print(f"❌ Backtest failed: {response.status_code}")
            return {"error": response.text}
    
    def run_cross_validation(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        n_splits: int = 5
    ) -> Dict[str, Any]:
        """
        Run cross-validation for a symbol
        
        Args:
            symbol: Stock symbol to test
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            n_splits: Number of cross-validation folds
            
        Returns:
            Cross-validation results
        """
        print(f"🔄 Running {n_splits}-fold cross-validation for {symbol}")
        
        response = self.session.post(
            f"{self.api_url}/api/cross-validation",
            json={
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
                "n_splits": n_splits
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            self._print_cv_results(result)
            return result
        else:
            print(f"❌ Cross-validation failed: {response.status_code}")
            return {"error": response.text}
    
    def get_model_performance(self, symbol: str) -> Dict[str, Any]:
        """
        Get performance metrics for trained models
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Model performance metrics
        """
        print(f"📈 Getting model performance for {symbol}")
        
        response = self.session.get(f"{self.api_url}/api/model-performance/{symbol}")
        
        if response.status_code == 200:
            result = response.json()
            self._print_model_performance(result)
            return result
        else:
            print(f"❌ Failed to get performance: {response.status_code}")
            return {"error": response.text}
    
    def batch_backtest(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        strategy_type: str = "long_only"
    ) -> Dict[str, Any]:
        """
        Run backtests for multiple symbols
        
        Args:
            symbols: List of stock symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            strategy_type: Trading strategy
            
        Returns:
            Results for all symbols
        """
        results = {}
        
        for symbol in symbols:
            print(f"\n{'='*50}")
            results[symbol] = self.run_backtest(symbol, start_date, end_date, strategy_type)
        
        # Summary
        self._print_batch_summary(results)
        return results
    
    def _print_backtest_results(self, result: Dict[str, Any]):
        """Pretty print backtest results"""
        if "report" in result:
            report = result["report"]
            
            print("\n📊 BACKTEST RESULTS")
            print("="*50)
            
            # Performance metrics
            perf = report.get("performance", {})
            print("\n💰 Performance:")
            print(f"  Total Return: {perf.get('total_return', 'N/A')}")
            print(f"  Sharpe Ratio: {perf.get('sharpe_ratio', 'N/A')}")
            print(f"  Max Drawdown: {perf.get('max_drawdown', 'N/A')}")
            print(f"  Calmar Ratio: {perf.get('calmar_ratio', 'N/A')}")
            
            # Trading metrics
            trade = report.get("trading", {})
            print("\n📈 Trading:")
            print(f"  Total Trades: {trade.get('total_trades', 'N/A')}")
            print(f"  Win Rate: {trade.get('win_rate', 'N/A')}")
            print(f"  Profit Factor: {trade.get('profit_factor', 'N/A')}")
            print(f"  Avg Win: {trade.get('avg_win', 'N/A')}")
            print(f"  Avg Loss: {trade.get('avg_loss', 'N/A')}")
            
            # Prediction metrics
            pred = report.get("prediction", {})
            print("\n🎯 Prediction:")
            print(f"  Accuracy: {pred.get('accuracy', 'N/A')}")
            print(f"  Directional Accuracy: {pred.get('directional_accuracy', 'N/A')}")
            print(f"  RMSE: {pred.get('rmse', 'N/A')}")
            print(f"  R-Squared: {pred.get('r_squared', 'N/A')}")
            
            # Risk assessment
            print(f"\n⚠️ Risk Assessment: {report.get('risk_assessment', 'N/A')}")
    
    def _print_cv_results(self, result: Dict[str, Any]):
        """Pretty print cross-validation results"""
        if "cross_validation" in result:
            cv = result["cross_validation"]
            
            print("\n🔄 CROSS-VALIDATION RESULTS")
            print("="*50)
            
            print(f"Number of Folds: {cv.get('n_splits', 'N/A')}")
            print(f"Avg Return: {cv.get('avg_return', 'N/A'):.2%}")
            print(f"Avg Sharpe: {cv.get('avg_sharpe', 'N/A'):.2f}")
            print(f"Avg Accuracy: {cv.get('avg_accuracy', 'N/A'):.2%}")
            
            print("\nFold Details:")
            for fold in cv.get("fold_results", []):
                print(f"  Fold {fold['fold']}: Return={fold['return']:.2%}, Sharpe={fold['sharpe']:.2f}")
    
    def _print_model_performance(self, result: Dict[str, Any]):
        """Pretty print model performance"""
        if "performance" in result:
            print("\n🎯 MODEL PERFORMANCE")
            print("="*50)
            
            for model, metrics in result["performance"].items():
                print(f"\n{model}:")
                print(f"  Test MSE: {metrics.get('test_mse', 'N/A')}")
                print(f"  Test MAE: {metrics.get('test_mae', 'N/A')}")
                print(f"  Test R²: {metrics.get('test_r2', 'N/A')}")
                print(f"  Trained At: {metrics.get('trained_at', 'N/A')}")
    
    def _print_batch_summary(self, results: Dict[str, Any]):
        """Print summary of batch backtest results"""
        print("\n" + "="*50)
        print("📊 BATCH BACKTEST SUMMARY")
        print("="*50)
        
        summary_data = []
        
        for symbol, result in results.items():
            if "report" in result:
                perf = result["report"].get("performance", {})
                trade = result["report"].get("trading", {})
                
                summary_data.append({
                    "Symbol": symbol,
                    "Return": perf.get("total_return", "N/A"),
                    "Sharpe": perf.get("sharpe_ratio", "N/A"),
                    "Win Rate": trade.get("win_rate", "N/A"),
                    "Trades": trade.get("total_trades", "N/A")
                })
        
        if summary_data:
            df = pd.DataFrame(summary_data)
            print(df.to_string(index=False))


def main():
    """Example usage of the backtest client"""
    
    # Initialize client with your API URL
    # Replace this with your actual API URL
    client = BacktestClient("https://8000-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev")
    
    # Example 1: Train models
    print("\n🎓 EXAMPLE 1: Training Models")
    # client.train_models(["AAPL", "GOOGL"], training_days=730)
    
    # Example 2: Run single backtest
    print("\n📈 EXAMPLE 2: Single Backtest")
    client.run_backtest(
        symbol="AAPL",
        start_date="2023-01-01",
        end_date="2024-01-01",
        strategy_type="long_only"
    )
    
    # Example 3: Run cross-validation
    print("\n🔄 EXAMPLE 3: Cross-Validation")
    client.run_cross_validation(
        symbol="AAPL",
        start_date="2023-01-01",
        end_date="2024-01-01",
        n_splits=5
    )
    
    # Example 4: Batch backtest
    print("\n📊 EXAMPLE 4: Batch Backtest")
    client.batch_backtest(
        symbols=["AAPL", "GOOGL", "MSFT"],
        start_date="2023-06-01",
        end_date="2024-01-01",
        strategy_type="long_only"
    )
    
    # Example 5: Check model performance
    print("\n🎯 EXAMPLE 5: Model Performance")
    client.get_model_performance("AAPL")


if __name__ == "__main__":
    # Run examples
    main()
    
    # Or use interactively:
    # client = BacktestClient("https://8000-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev")
    # result = client.run_backtest("AAPL", "2023-01-01", "2024-01-01")