"""
Parameter Optimizer for Backtesting Framework

This module provides parameter optimization capabilities to find the best
configuration settings for trading strategies.

Features:
- Grid search (exhaustive testing of all combinations)
- Random search (efficient sampling of parameter space)
- Train-test split validation
- Performance ranking and analysis
- Overfitting prevention

Author: AI Assistant
Date: November 2025
"""

import itertools
import random
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ParameterOptimizer:
    """
    Optimize backtest parameters to find best configuration
    
    Supports:
    - Grid search (test all combinations)
    - Random search (sample parameter space)
    - Train-test split validation
    - Multiple optimization metrics
    """
    
    def __init__(
        self,
        backtest_function,
        parameter_grid: Dict[str, List],
        optimization_metric: str = 'total_return_pct',
        train_test_split: float = 0.75,
        embargo_days: int = 3
    ):
        """
        Initialize parameter optimizer
        
        Args:
            backtest_function: Function that runs backtest with parameters
            parameter_grid: Dict of parameter names and values to test
            optimization_metric: Metric to optimize ('total_return_pct', 'sharpe_ratio', etc.)
            train_test_split: Proportion of data for training (0.75 = 75% train, 25% test)
            embargo_days: Gap between train and test periods to prevent look-ahead bias (default 3 days)
        """
        self.backtest_function = backtest_function
        self.parameter_grid = parameter_grid
        self.optimization_metric = optimization_metric
        self.embargo_days = embargo_days
        self.train_test_split = train_test_split
        self.results = []
        
    def grid_search(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        **fixed_params
    ) -> Tuple[Dict, pd.DataFrame]:
        """
        Perform exhaustive grid search over all parameter combinations
        
        Args:
            symbol: Stock symbol to test
            start_date: Backtest start date
            end_date: Backtest end date
            **fixed_params: Additional fixed parameters for backtest
        
        Returns:
            best_params: Best parameter configuration
            results_df: DataFrame with all test results
        """
        logger.info(f"Starting grid search optimization for {symbol}")
        
        # Generate all combinations
        param_names = list(self.parameter_grid.keys())
        param_values = [self.parameter_grid[name] for name in param_names]
        combinations = list(itertools.product(*param_values))
        
        total_tests = len(combinations)
        logger.info(f"Testing {total_tests} parameter combinations")
        
        # Calculate train/test split dates
        train_end, test_start = self._calculate_split_dates(start_date, end_date)
        
        # Test each combination
        self.results = []
        for i, combo in enumerate(combinations):
            # Create parameter dict
            params = dict(zip(param_names, combo))
            
            # Progress logging
            if (i + 1) % max(1, total_tests // 10) == 0:
                logger.info(f"Progress: {i+1}/{total_tests} ({(i+1)/total_tests*100:.1f}%)")
            
            # Run on training period
            train_result = self._run_backtest_with_params(
                symbol=symbol,
                start_date=start_date,
                end_date=train_end,
                params=params,
                fixed_params=fixed_params
            )
            
            # Run on test period (validation)
            test_result = self._run_backtest_with_params(
                symbol=symbol,
                start_date=test_start,
                end_date=end_date,
                params=params,
                fixed_params=fixed_params
            )
            
            # Store results
            self.results.append({
                'params': params,
                'train_return': train_result.get('total_return_pct', 0),
                'train_sharpe': train_result.get('sharpe_ratio', 0),
                'train_drawdown': train_result.get('max_drawdown_pct', 0),
                'train_win_rate': train_result.get('win_rate', 0),
                'test_return': test_result.get('total_return_pct', 0),
                'test_sharpe': test_result.get('sharpe_ratio', 0),
                'test_drawdown': test_result.get('max_drawdown_pct', 0),
                'test_win_rate': test_result.get('win_rate', 0),
                'overfit_score': self._calculate_overfit_score(train_result, test_result)
            })
        
        # Find best parameters
        results_df = pd.DataFrame(self.results)
        best_params = self._select_best_params(results_df)
        
        logger.info(f"Grid search complete. Best params: {best_params}")
        
        return best_params, results_df
    
    def random_search(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        n_iterations: int = 100,
        **fixed_params
    ) -> Tuple[Dict, pd.DataFrame]:
        """
        Perform random search by sampling parameter space
        
        Args:
            symbol: Stock symbol to test
            start_date: Backtest start date
            end_date: Backtest end date
            n_iterations: Number of random combinations to test
            **fixed_params: Additional fixed parameters for backtest
        
        Returns:
            best_params: Best parameter configuration
            results_df: DataFrame with all test results
        """
        logger.info(f"Starting random search optimization for {symbol} ({n_iterations} iterations)")
        
        # Calculate train/test split dates
        train_end, test_start = self._calculate_split_dates(start_date, end_date)
        
        # Test random combinations
        self.results = []
        for i in range(n_iterations):
            # Generate random parameter combination
            params = self._generate_random_params()
            
            # Progress logging
            if (i + 1) % max(1, n_iterations // 10) == 0:
                logger.info(f"Progress: {i+1}/{n_iterations} ({(i+1)/n_iterations*100:.1f}%)")
            
            # Run on training period
            train_result = self._run_backtest_with_params(
                symbol=symbol,
                start_date=start_date,
                end_date=train_end,
                params=params,
                fixed_params=fixed_params
            )
            
            # Run on test period (validation)
            test_result = self._run_backtest_with_params(
                symbol=symbol,
                start_date=test_start,
                end_date=end_date,
                params=params,
                fixed_params=fixed_params
            )
            
            # Store results
            self.results.append({
                'params': params,
                'train_return': train_result.get('total_return_pct', 0),
                'train_sharpe': train_result.get('sharpe_ratio', 0),
                'train_drawdown': train_result.get('max_drawdown_pct', 0),
                'train_win_rate': train_result.get('win_rate', 0),
                'test_return': test_result.get('total_return_pct', 0),
                'test_sharpe': test_result.get('sharpe_ratio', 0),
                'test_drawdown': test_result.get('max_drawdown_pct', 0),
                'test_win_rate': test_result.get('win_rate', 0),
                'overfit_score': self._calculate_overfit_score(train_result, test_result)
            })
        
        # Find best parameters
        results_df = pd.DataFrame(self.results)
        best_params = self._select_best_params(results_df)
        
        logger.info(f"Random search complete. Best params: {best_params}")
        
        return best_params, results_df
    
    def _calculate_split_dates(
        self,
        start_date: str,
        end_date: str
    ) -> Tuple[str, str]:
        """Calculate train/test split dates with embargo period"""
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        total_days = (end - start).days
        train_days = int(total_days * self.train_test_split)
        
        train_end = start + timedelta(days=train_days)
        
        # Add embargo period - gap between train and test to prevent look-ahead bias
        test_start = train_end + timedelta(days=self.embargo_days)
        
        # Verify we have enough data for test period
        if test_start >= end:
            raise ValueError(
                f"Not enough data for {self.embargo_days}-day embargo. "
                f"Train ends {train_end.strftime('%Y-%m-%d')}, "
                f"test would start {test_start.strftime('%Y-%m-%d')}, "
                f"but data ends {end_date}"
            )
        
        logger.info(
            f"Train: {start_date} to {train_end.strftime('%Y-%m-%d')}, "
            f"Embargo: {self.embargo_days} days, "
            f"Test: {test_start.strftime('%Y-%m-%d')} to {end_date}"
        )
        
        return train_end.strftime('%Y-%m-%d'), test_start.strftime('%Y-%m-%d')
    
    def _generate_random_params(self) -> Dict:
        """Generate random parameter combination"""
        params = {}
        for param_name, param_values in self.parameter_grid.items():
            params[param_name] = random.choice(param_values)
        return params
    
    def _run_backtest_with_params(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        params: Dict,
        fixed_params: Dict
    ) -> Dict:
        """Run backtest with given parameters"""
        try:
            # Merge params
            all_params = {**fixed_params, **params, 'symbol': symbol, 'start_date': start_date, 'end_date': end_date}
            
            # Run backtest
            result = self.backtest_function(**all_params)
            
            # Extract metrics
            if 'performance' in result:
                return result['performance']
            return result
            
        except Exception as e:
            logger.error(f"Backtest failed with params {params}: {e}")
            return {
                'total_return_pct': -999,
                'sharpe_ratio': -999,
                'max_drawdown_pct': -999,
                'win_rate': 0
            }
    
    def _calculate_overfit_score(
        self,
        train_result: Dict,
        test_result: Dict
    ) -> float:
        """
        Calculate overfitting score (lower is better)
        
        Measures performance degradation from train to test period
        """
        train_metric = train_result.get(self.optimization_metric, 0)
        test_metric = test_result.get(self.optimization_metric, 0)
        
        if train_metric == 0:
            return 999.0  # Avoid division by zero
        
        # Calculate percentage drop from train to test
        degradation = (train_metric - test_metric) / abs(train_metric) * 100
        
        return max(0, degradation)  # Non-negative
    
    def _select_best_params(self, results_df: pd.DataFrame) -> Dict:
        """
        Select best parameters based on optimization metric
        
        Considers both performance and overfitting
        """
        if results_df.empty:
            return {}
        
        # Filter out extreme overfitting (>30% degradation)
        valid_results = results_df[results_df['overfit_score'] < 30].copy()
        
        if valid_results.empty:
            logger.warning("All configurations overfit. Using best train performance.")
            valid_results = results_df
        
        # Sort by test performance (out-of-sample)
        metric_col = f'test_{self.optimization_metric.replace("_pct", "").replace("total_", "")}'
        
        if metric_col not in valid_results.columns:
            # Fallback to train metric
            metric_col = f'train_{self.optimization_metric.replace("_pct", "").replace("total_", "")}'
        
        # For drawdown, lower is better
        if 'drawdown' in metric_col:
            best_idx = valid_results[metric_col].idxmin()
        else:
            best_idx = valid_results[metric_col].idxmax()
        
        return valid_results.loc[best_idx, 'params']
    
    def get_top_n_configs(self, n: int = 10) -> pd.DataFrame:
        """Get top N parameter configurations"""
        if not self.results:
            return pd.DataFrame()
        
        results_df = pd.DataFrame(self.results)
        
        # Sort by test performance
        metric_col = f'test_{self.optimization_metric.replace("_pct", "").replace("total_", "")}'
        
        if metric_col in results_df.columns:
            if 'drawdown' in metric_col:
                sorted_df = results_df.sort_values(metric_col, ascending=True)
            else:
                sorted_df = results_df.sort_values(metric_col, ascending=False)
        else:
            sorted_df = results_df
        
        return sorted_df.head(n)
    
    def generate_summary_report(self) -> Dict:
        """Generate optimization summary report"""
        if not self.results:
            return {'error': 'No optimization results available'}
        
        results_df = pd.DataFrame(self.results)
        
        # Calculate statistics
        summary = {
            'total_configurations_tested': len(results_df),
            'best_params': self._select_best_params(results_df),
            'avg_train_return': results_df['train_return'].mean(),
            'avg_test_return': results_df['test_return'].mean(),
            'avg_overfit_score': results_df['overfit_score'].mean(),
            'best_train_return': results_df['train_return'].max(),
            'best_test_return': results_df['test_return'].max(),
            'worst_overfit': results_df['overfit_score'].max(),
            'configurations_with_low_overfit': len(results_df[results_df['overfit_score'] < 15]),
            'top_10_configs': self.get_top_n_configs(10).to_dict('records')
        }
        
        return summary


# Default parameter grids
DEFAULT_PARAMETER_GRID = {
    'confidence_threshold': [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80],
    'lookback_days': [30, 45, 60, 75, 90, 105, 120],
    'max_position_size': [0.05, 0.10, 0.15, 0.20, 0.25],
    'stop_loss_pct': [0.02, 0.03, 0.05],  # 2%, 3%, 5% stop loss
    'take_profit_pct': [0.05, 0.10, 0.15]  # 5%, 10%, 15% take profit
}

QUICK_PARAMETER_GRID = {
    'confidence_threshold': [0.65],  # Fixed at optimal value (was 3 values)
    'lookback_days': [60, 75],  # Keep 2 best-performing values
    'max_position_size': [0.15, 0.20],  # Keep 2 safe values
    'stop_loss_pct': [0.03],  # Fixed at industry standard
    'take_profit_pct': [0.10]  # Fixed at optimal risk/reward ratio
}
# Total combinations: 1 × 2 × 2 × 1 × 1 = 4 (was 240, then 12!)
# Completes in ~2 minutes even with 13+ months of data

PORTFOLIO_PARAMETER_GRID = {
    'confidence_threshold': [0.55, 0.60, 0.65, 0.70],
    'lookback_days': [60, 75, 90],
    'allocation_strategy': ['equal', 'risk_parity'],
    'rebalance_frequency': ['monthly', 'quarterly', 'never']
}
