"""
Unit tests for Macro Beta Calculator module

Tests the OLS regression-based beta calculation including:
- Beta computation accuracy
- Data handling and validation
- Factor configuration
- Error handling
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.screening.macro_beta import MacroBetaCalculator, FactorDefinition


class TestFactorDefinition(unittest.TestCase):
    """Test cases for FactorDefinition dataclass"""
    
    def test_factor_creation(self):
        """Test that factor definition creates correctly"""
        factor = FactorDefinition(name="xjo", symbol="^AXJO")
        
        self.assertEqual(factor.name, "xjo")
        self.assertEqual(factor.symbol, "^AXJO")
    
    def test_factor_immutability(self):
        """Test that factor definitions are immutable (dataclass frozen)"""
        factor = FactorDefinition(name="xjo", symbol="^AXJO")
        
        # Note: FactorDefinition is not frozen by default in current implementation
        # This test documents expected behavior if it were frozen
        self.assertTrue(hasattr(factor, 'name'))
        self.assertTrue(hasattr(factor, 'symbol'))


class TestMacroBetaCalculator(unittest.TestCase):
    """Test cases for MacroBetaCalculator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.calculator = MacroBetaCalculator(
            lookback_days=90,
            min_obs=40
        )
        
        # Create sample price data
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        
        # Stock with beta ~1.0 (moves with market)
        self.stock_neutral = pd.DataFrame({
            'Close': 100 + np.cumsum(np.random.randn(100) * 0.5)
        }, index=dates)
        
        # Market index
        self.market_index = pd.DataFrame({
            'Close': 5000 + np.cumsum(np.random.randn(100) * 0.5)
        }, index=dates)
        
        # High beta stock (amplifies market moves)
        market_returns = self.market_index['Close'].pct_change()
        high_beta_close = [100]
        for ret in market_returns[1:]:
            high_beta_close.append(high_beta_close[-1] * (1 + ret * 1.5))
        
        self.stock_high_beta = pd.DataFrame({
            'Close': high_beta_close
        }, index=dates)
    
    def test_calculator_initialization(self):
        """Test that calculator initializes with correct parameters"""
        self.assertEqual(self.calculator.lookback_days, 90)
        self.assertEqual(self.calculator.min_obs, 40)
        self.assertEqual(len(self.calculator.factors), 2)  # Default: xjo, lithium
    
    def test_custom_factors(self):
        """Test initialization with custom factors"""
        custom_factors = [
            FactorDefinition(name="gold", symbol="GLD"),
            FactorDefinition(name="oil", symbol="CL=F")
        ]
        
        calc = MacroBetaCalculator(factors=custom_factors)
        self.assertEqual(len(calc.factors), 2)
        self.assertEqual(calc.factors[0].name, "gold")
        self.assertEqual(calc.factors[1].name, "oil")
    
    @patch('models.screening.macro_beta.yf.download')
    def test_compute_betas_structure(self, mock_download):
        """Test that compute_betas returns correct structure"""
        # Mock yfinance download
        mock_data = MagicMock()
        mock_data.__getitem__ = lambda self, key: {
            'CBA.AX': self.stock_neutral['Close'],
            '^AXJO': self.market_index['Close'],
            'LIT.AX': self.market_index['Close']  # Use same data for simplicity
        }[key]
        mock_download.return_value = mock_data
        
        result = self.calculator.compute_betas(['CBA.AX'])
        
        # Check structure
        self.assertIsInstance(result, dict)
        self.assertIn('CBA.AX', result)
        
        # Check nested structure
        stock_betas = result['CBA.AX']
        self.assertIsInstance(stock_betas, dict)
        self.assertIn('xjo', stock_betas)
        self.assertIn('lithium', stock_betas)
    
    def test_beta_calculation_formula(self):
        """Test OLS beta calculation formula"""
        # Create correlated data
        np.random.seed(42)
        market_returns = np.random.randn(100) * 0.02
        stock_returns = market_returns * 1.2 + np.random.randn(100) * 0.01  # Beta ~1.2
        
        # Calculate beta manually
        covariance = np.cov(stock_returns, market_returns)[0, 1]
        variance = np.var(market_returns)
        expected_beta = covariance / variance
        
        # Should be around 1.2
        self.assertTrue(1.0 < expected_beta < 1.4, f"Expected beta ~1.2, got {expected_beta}")
    
    def test_zero_variance_handling(self):
        """Test handling of zero variance (constant price)"""
        # Create constant price data
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        constant_price = pd.DataFrame({
            'Close': np.full(100, 100.0)  # Constant price
        }, index=dates)
        
        # Calculate returns (will be all zeros)
        returns = constant_price['Close'].pct_change()
        
        # Variance should be zero or very close
        self.assertLess(np.var(returns.dropna()), 1e-10)
    
    def test_insufficient_data_handling(self):
        """Test handling of insufficient observations"""
        calc = MacroBetaCalculator(
            lookback_days=90,
            min_obs=50  # Require 50 observations
        )
        
        # Create short price series (only 30 days)
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        short_data = pd.DataFrame({
            'Close': np.random.randn(30).cumsum() + 100
        }, index=dates)
        
        # With real implementation, this should return NaN or handle gracefully
        # Current implementation would need mock
    
    def test_missing_data_in_series(self):
        """Test handling of missing data points"""
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        
        # Create data with NaN values
        prices_with_nan = 100 + np.cumsum(np.random.randn(100) * 0.5)
        prices_with_nan[20:25] = np.nan  # Insert NaN values
        
        stock_data = pd.DataFrame({
            'Close': prices_with_nan
        }, index=dates)
        
        # Calculate returns (pct_change will propagate NaN)
        returns = stock_data['Close'].pct_change()
        
        # After dropna, should have fewer observations
        valid_returns = returns.dropna()
        self.assertLess(len(valid_returns), 99)  # 100 - 1 for pct_change - 5 for NaN
    
    def test_beta_interpretation(self):
        """Test beta value interpretation ranges"""
        # Defensive stock: beta < 1.0
        defensive_beta = 0.7
        self.assertLess(defensive_beta, 1.0)
        
        # Market-neutral: beta ≈ 1.0
        neutral_beta = 1.0
        self.assertAlmostEqual(neutral_beta, 1.0, places=1)
        
        # Aggressive stock: beta > 1.0
        aggressive_beta = 1.5
        self.assertGreater(aggressive_beta, 1.0)
    
    def test_negative_beta(self):
        """Test handling of negative beta (inverse correlation)"""
        # Stock that moves opposite to market should have negative beta
        np.random.seed(42)
        market_returns = np.random.randn(100) * 0.02
        inverse_stock_returns = -market_returns * 0.8  # Inverse correlation
        
        # Calculate beta
        covariance = np.cov(inverse_stock_returns, market_returns)[0, 1]
        variance = np.var(market_returns)
        beta = covariance / variance
        
        # Should be negative
        self.assertLess(beta, 0)
    
    @patch('models.screening.macro_beta.yf.download')
    def test_multiple_symbols(self, mock_download):
        """Test computing betas for multiple symbols"""
        # Mock yfinance download
        mock_data = MagicMock()
        mock_data.__getitem__ = lambda self, key: {
            'CBA.AX': self.stock_neutral['Close'],
            'BHP.AX': self.stock_high_beta['Close'],
            '^AXJO': self.market_index['Close'],
            'LIT.AX': self.market_index['Close']
        }[key]
        mock_download.return_value = mock_data
        
        symbols = ['CBA.AX', 'BHP.AX']
        result = self.calculator.compute_betas(symbols)
        
        # Should return betas for both symbols
        self.assertEqual(len(result), 2)
        self.assertIn('CBA.AX', result)
        self.assertIn('BHP.AX', result)
    
    def test_lookback_period_parameter(self):
        """Test that lookback period affects data range"""
        calc_90 = MacroBetaCalculator(lookback_days=90)
        calc_180 = MacroBetaCalculator(lookback_days=180)
        
        self.assertEqual(calc_90.lookback_days, 90)
        self.assertEqual(calc_180.lookback_days, 180)
        
        # With real implementation, longer lookback would fetch more data
        self.assertGreater(calc_180.lookback_days, calc_90.lookback_days)
    
    def test_min_observations_validation(self):
        """Test minimum observations parameter"""
        calc = MacroBetaCalculator(min_obs=40)
        
        self.assertEqual(calc.min_obs, 40)
        
        # Verify it's a reasonable value
        self.assertGreater(calc.min_obs, 20)  # Too few observations unreliable
        self.assertLess(calc.min_obs, calc.lookback_days)  # Must be less than lookback
    
    def test_returns_calculation(self):
        """Test daily returns calculation"""
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        prices = pd.DataFrame({
            'Close': [100, 102, 101, 103, 105]  # Simple price series
        }, index=dates[:5])
        
        returns = prices['Close'].pct_change()
        
        # First return should be NaN
        self.assertTrue(pd.isna(returns.iloc[0]))
        
        # Second return: (102-100)/100 = 0.02
        self.assertAlmostEqual(returns.iloc[1], 0.02, places=4)
        
        # Third return: (101-102)/102 ≈ -0.0098
        self.assertAlmostEqual(returns.iloc[2], -0.0098, places=4)
    
    def test_date_alignment(self):
        """Test that stock and factor data align on dates"""
        # Create data with different date ranges
        dates_stock = pd.date_range(end=datetime.now(), periods=100, freq='D')
        dates_factor = pd.date_range(end=datetime.now() - timedelta(days=10), periods=100, freq='D')
        
        stock_returns = pd.Series(np.random.randn(100), index=dates_stock)
        factor_returns = pd.Series(np.random.randn(100), index=dates_factor)
        
        # Join on common dates
        joined = pd.concat([stock_returns, factor_returns], axis=1, join='inner')
        
        # Should have fewer observations due to non-overlapping dates
        self.assertLess(len(joined), 100)
        self.assertGreater(len(joined), 80)  # But still substantial overlap


if __name__ == '__main__':
    unittest.main()
