#!/usr/bin/env python3
"""
Parameter Optimization Module - Week 2 Features
Optimize regime_weight and other parameters for best performance

Author: Trading System v1.3.13 - REGIME EDITION (Week 2)
Date: January 6, 2026
"""

import logging
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import pandas as pd
    import numpy as np
    from itertools import product
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    logger.warning("Required packages not available")


class ParameterOptimizer:
    """
    Parameter optimization for regime-aware trading
    
    Features:
    - Grid search for regime_weight
    - Cross-validation across regimes
    - Optimal weight by regime type
    - Confidence threshold tuning
    - Sector weight optimization
    """
    
    def __init__(self):
        """Initialize parameter optimizer"""
        self.results = {}
        self.best_params = {}
        
        logger.info("[OK] ParameterOptimizer initialized")
    
    def grid_search_regime_weight(
        self,
        backtester,
        stocks_data: Dict,
        regime_data: pd.DataFrame,
        weights: List[float] = None
    ) -> Dict:
        """
        Grid search for optimal regime_weight
        
        Args:
            backtester: RegimeBacktester instance
            stocks_data: Dict of stock data
            regime_data: DataFrame with regime classifications
            weights: List of weights to test (default: 0.0 to 0.6 by 0.1)
            
        Returns:
            Dict with results for each weight
        """
        if weights is None:
            weights = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        
        logger.info(f"🔍 Grid search for regime_weight: {weights}")
        
        results = {}
        
        for weight in weights:
            logger.info(f"   Testing weight={weight:.1f}...")
            
            # Run backtest with this weight
            backtest_results = backtester.backtest_strategy(
                stocks_data,
                regime_data,
                use_regime=(weight > 0),
                regime_weight=weight
            )
            
            # Store results
            results[weight] = {
                'total_return': backtest_results['total_return'],
                'final_value': backtest_results['final_value'],
                'num_trades': backtest_results['num_trades'],
                'regime_performance': backtest_results.get('regime_performance', {})
            }
            
            logger.info(f"      Return: {backtest_results['total_return']:+.2f}%")
        
        # Find best weight
        best_weight = max(results.keys(), key=lambda w: results[w]['total_return'])
        best_return = results[best_weight]['total_return']
        
        logger.info(f"[OK] Best weight: {best_weight:.1f} (return: {best_return:+.2f}%)")
        
        self.best_params['regime_weight'] = best_weight
        self.results['grid_search'] = results
        
        return results
    
    def optimize_by_regime(
        self,
        backtester,
        stocks_data: Dict,
        regime_data: pd.DataFrame
    ) -> Dict:
        """
        Find optimal regime_weight for each regime type
        
        Args:
            backtester: RegimeBacktester instance
            stocks_data: Dict of stock data
            regime_data: DataFrame with regime classifications
            
        Returns:
            Dict with optimal weights by regime
        """
        logger.info("[*] Optimizing weights by regime type...")
        
        # Get unique regimes
        regimes = regime_data['regime'].unique()
        
        optimal_weights = {}
        
        for regime in regimes:
            # Filter data for this regime
            regime_dates = regime_data[regime_data['regime'] == regime].index
            
            if len(regime_dates) < 10:  # Skip if too few days
                logger.info(f"   {regime}: Too few days ({len(regime_dates)}), skipping")
                continue
            
            logger.info(f"   {regime}: Testing weights on {len(regime_dates)} days...")
            
            # Test different weights
            weights = [0.0, 0.2, 0.4, 0.6, 0.8]
            best_weight = 0.0
            best_return = -float('inf')
            
            for weight in weights:
                # Simplified: use overall backtest but focus on regime days
                backtest_results = backtester.backtest_strategy(
                    stocks_data,
                    regime_data,
                    use_regime=(weight > 0),
                    regime_weight=weight
                )
                
                # Get performance for this regime
                regime_perf = backtest_results.get('regime_performance', {}).get(regime, {})
                regime_return = regime_perf.get('total_return', 0)
                
                if regime_return > best_return:
                    best_return = regime_return
                    best_weight = weight
            
            optimal_weights[regime] = {
                'optimal_weight': best_weight,
                'expected_return': best_return
            }
            
            logger.info(f"      Optimal weight: {best_weight:.1f} (return: {best_return:+.2f}%)")
        
        self.results['regime_optimal_weights'] = optimal_weights
        
        return optimal_weights
    
    def optimize_confidence_threshold(
        self,
        regime_confidences: List[float],
        regime_accuracies: List[float]
    ) -> float:
        """
        Find optimal confidence threshold for regime classification
        
        Args:
            regime_confidences: List of confidence scores (0-1)
            regime_accuracies: List of actual accuracies (0-1)
            
        Returns:
            Optimal confidence threshold
        """
        logger.info("[#] Optimizing confidence threshold...")
        
        if not regime_confidences or not regime_accuracies:
            logger.warning("[!] No data provided")
            return 0.5
        
        # Test thresholds from 0.3 to 0.9
        thresholds = np.arange(0.3, 0.95, 0.05)
        
        results = {}
        
        for threshold in thresholds:
            # Filter by threshold
            mask = np.array(regime_confidences) >= threshold
            
            if mask.sum() == 0:  # No data above threshold
                continue
            
            filtered_accuracies = np.array(regime_accuracies)[mask]
            
            # Metrics
            avg_accuracy = filtered_accuracies.mean()
            coverage = mask.sum() / len(mask)
            
            # Score: balance accuracy and coverage
            score = avg_accuracy * (coverage ** 0.5)  # Penalize low coverage
            
            results[threshold] = {
                'avg_accuracy': avg_accuracy,
                'coverage': coverage,
                'score': score
            }
        
        # Find best threshold
        if results:
            best_threshold = max(results.keys(), key=lambda t: results[t]['score'])
            logger.info(f"[OK] Optimal threshold: {best_threshold:.2f}")
            logger.info(f"   Accuracy: {results[best_threshold]['avg_accuracy']:.1%}")
            logger.info(f"   Coverage: {results[best_threshold]['coverage']:.1%}")
            
            self.best_params['confidence_threshold'] = best_threshold
            self.results['confidence_optimization'] = results
            
            return best_threshold
        else:
            return 0.5
    
    def optimize_sector_weights(
        self,
        regime_performance: Dict[str, Dict],
        sectors: List[str]
    ) -> Dict[str, float]:
        """
        Optimize sector allocation weights based on regime performance
        
        Args:
            regime_performance: Performance by regime {regime: {sector: metrics}}
            sectors: List of sector names
            
        Returns:
            Dict of optimal sector weights
        """
        logger.info("[*] Optimizing sector weights...")
        
        sector_scores = {sector: [] for sector in sectors}
        
        # Collect performance across regimes
        for regime, perf in regime_performance.items():
            for sector in sectors:
                if sector in perf:
                    score = perf[sector].get('total_return', 0)
                    sector_scores[sector].append(score)
        
        # Calculate average performance
        sector_weights = {}
        total_score = 0
        
        for sector in sectors:
            if sector_scores[sector]:
                avg_score = np.mean(sector_scores[sector])
                # Convert to positive weight (shift and scale)
                weight = max(0, avg_score + 10)  # Shift by 10 to make positive
                sector_weights[sector] = weight
                total_score += weight
            else:
                sector_weights[sector] = 1.0
                total_score += 1.0
        
        # Normalize to sum to 1.0
        if total_score > 0:
            sector_weights = {s: w/total_score for s, w in sector_weights.items()}
        
        logger.info(f"[OK] Sector weights optimized:")
        for sector, weight in sector_weights.items():
            logger.info(f"   {sector}: {weight:.1%}")
        
        self.best_params['sector_weights'] = sector_weights
        
        return sector_weights
    
    def cross_validate(
        self,
        backtester,
        stocks_data: Dict,
        regime_data: pd.DataFrame,
        n_folds: int = 5
    ) -> Dict:
        """
        Cross-validation for regime-aware strategy
        
        Args:
            backtester: RegimeBacktester instance
            stocks_data: Dict of stock data
            regime_data: DataFrame with regime classifications
            n_folds: Number of folds
            
        Returns:
            Dict with cross-validation results
        """
        logger.info(f"[~] Cross-validation ({n_folds} folds)...")
        
        # Split data into folds
        n_samples = len(regime_data)
        fold_size = n_samples // n_folds
        
        fold_results = []
        
        for fold in range(n_folds):
            # Define train/test split
            test_start = fold * fold_size
            test_end = (fold + 1) * fold_size if fold < n_folds - 1 else n_samples
            
            test_dates = regime_data.index[test_start:test_end]
            
            logger.info(f"   Fold {fold + 1}/{n_folds}: {len(test_dates)} days")
            
            # Get test data
            test_regime_data = regime_data.loc[test_dates]
            
            # Backtest on test fold
            results = backtester.backtest_strategy(
                stocks_data,
                test_regime_data,
                use_regime=True,
                regime_weight=self.best_params.get('regime_weight', 0.4)
            )
            
            fold_results.append({
                'fold': fold + 1,
                'total_return': results['total_return'],
                'num_trades': results['num_trades']
            })
            
            logger.info(f"      Return: {results['total_return']:+.2f}%")
        
        # Calculate statistics
        returns = [r['total_return'] for r in fold_results]
        
        cv_stats = {
            'mean_return': np.mean(returns),
            'std_return': np.std(returns),
            'min_return': np.min(returns),
            'max_return': np.max(returns),
            'fold_results': fold_results
        }
        
        logger.info(f"[OK] Cross-validation complete:")
        logger.info(f"   Mean return: {cv_stats['mean_return']:+.2f}%")
        logger.info(f"   Std return: {cv_stats['std_return']:.2f}%")
        
        self.results['cross_validation'] = cv_stats
        
        return cv_stats
    
    def generate_report(self) -> str:
        """
        Generate optimization report
        
        Returns:
            Formatted report string
        """
        lines = []
        lines.append("\n" + "="*80)
        lines.append("PARAMETER OPTIMIZATION REPORT")
        lines.append("="*80)
        
        # Best parameters
        if self.best_params:
            lines.append(f"\n[*] OPTIMAL PARAMETERS:")
            for param, value in self.best_params.items():
                if isinstance(value, dict):
                    lines.append(f"\n   {param}:")
                    for k, v in value.items():
                        lines.append(f"      {k}: {v}")
                else:
                    lines.append(f"   {param}: {value}")
        
        # Grid search results
        if 'grid_search' in self.results:
            lines.append(f"\n[#] REGIME WEIGHT GRID SEARCH:")
            for weight, result in sorted(self.results['grid_search'].items()):
                lines.append(f"   Weight {weight:.1f}: {result['total_return']:+.2f}% return")
        
        # Regime-specific weights
        if 'regime_optimal_weights' in self.results:
            lines.append(f"\n[*] OPTIMAL WEIGHTS BY REGIME:")
            for regime, result in self.results['regime_optimal_weights'].items():
                lines.append(f"   {regime}: weight={result['optimal_weight']:.1f}, return={result['expected_return']:+.2f}%")
        
        # Cross-validation
        if 'cross_validation' in self.results:
            cv = self.results['cross_validation']
            lines.append(f"\n[~] CROSS-VALIDATION RESULTS:")
            lines.append(f"   Mean Return: {cv['mean_return']:+.2f}%")
            lines.append(f"   Std Return: {cv['std_return']:.2f}%")
            lines.append(f"   Min Return: {cv['min_return']:+.2f}%")
            lines.append(f"   Max Return: {cv['max_return']:+.2f}%")
        
        lines.append("\n" + "="*80 + "\n")
        
        return "\n".join(lines)
    
    def save_results(self, filepath: str):
        """
        Save optimization results to JSON file
        
        Args:
            filepath: Path to save results
        """
        output = {
            'best_params': self.best_params,
            'results': {
                k: v for k, v in self.results.items() 
                if k not in ['cross_validation']  # Skip complex objects
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        logger.info(f"[OK] Results saved to {filepath}")


def test_optimizer():
    """Test parameter optimizer"""
    
    print("\n" + "="*80)
    print("TESTING PARAMETER OPTIMIZATION")
    print("="*80)
    
    if not DEPENDENCIES_AVAILABLE:
        print("[X] Required packages not available")
        return
    
    # Import backtester
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from regime_backtester import RegimeBacktester
    except ImportError:
        print("[X] Could not import RegimeBacktester")
        return
    
    # Create instances
    backtester = RegimeBacktester(start_date="2024-01-01", end_date="2025-12-31")
    optimizer = ParameterOptimizer()
    
    # Generate sample data
    dates = pd.date_range(start='2024-01-01', end='2025-12-31', freq='D')
    
    np.random.seed(42)
    market_data = pd.DataFrame({
        'sp500': 4500 + np.cumsum(np.random.randn(len(dates)) * 20),
        'nasdaq': 14000 + np.cumsum(np.random.randn(len(dates)) * 50),
        'oil': 80 + np.cumsum(np.random.randn(len(dates)) * 2),
        'iron_ore': 100 + np.cumsum(np.random.randn(len(dates)) * 3)
    }, index=dates)
    
    regime_data = backtester.reconstruct_historical_regimes(market_data)
    
    stocks_data = {}
    for symbol in ['BHP.AX', 'CBA.AX', 'CSL.AX', 'RIO.AX']:
        stocks_data[symbol] = pd.DataFrame({
            'close': 30 + np.cumsum(np.random.randn(len(dates)) * 0.5),
            'volume': 1000000 + np.random.randint(-100000, 100000, len(dates))
        }, index=dates)
    
    # Grid search
    print("\n1️⃣ Running grid search for regime_weight...")
    grid_results = optimizer.grid_search_regime_weight(
        backtester,
        stocks_data,
        regime_data,
        weights=[0.0, 0.2, 0.4, 0.6]
    )
    
    # Optimize by regime
    print("\n2️⃣ Optimizing weights by regime type...")
    regime_weights = optimizer.optimize_by_regime(
        backtester,
        stocks_data,
        regime_data
    )
    
    # Confidence threshold (simulated data)
    print("\n3️⃣ Optimizing confidence threshold...")
    confidences = np.random.uniform(0.5, 1.0, 100)
    accuracies = confidences * 0.8 + np.random.normal(0, 0.1, 100)
    accuracies = np.clip(accuracies, 0, 1)
    
    threshold = optimizer.optimize_confidence_threshold(
        confidences.tolist(),
        accuracies.tolist()
    )
    
    # Cross-validation
    print("\n4️⃣ Running cross-validation...")
    cv_results = optimizer.cross_validate(
        backtester,
        stocks_data,
        regime_data,
        n_folds=3
    )
    
    # Generate report
    report = optimizer.generate_report()
    print(report)
    
    return optimizer


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test
    test_optimizer()
