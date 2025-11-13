"""
Data Validator for Historical Stock Data
=========================================

Validates historical stock data quality and detects anomalies.

Key Features:
- Missing trading days detection
- Price outlier detection (z-score method)
- Stock split detection
- Data adjustment verification
- Comprehensive statistics calculation

Author: FinBERT v4.0
Date: October 2024
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates quality and integrity of historical stock data"""
    
    def __init__(self, outlier_threshold: float = 3.0):
        """
        Initialize data validator
        
        Args:
            outlier_threshold: Z-score threshold for outlier detection
        """
        self.outlier_threshold = outlier_threshold
        logger.info(f"Data validator initialized (outlier_threshold={outlier_threshold})")
    
    def validate_data_quality(self, data: pd.DataFrame, symbol: str) -> Dict:
        """
        Comprehensive data quality validation
        
        Args:
            data: DataFrame with OHLCV data
            symbol: Stock ticker symbol
        
        Returns:
            Dictionary with validation results
        """
        logger.info(f"Validating data quality for {symbol}")
        
        validation_results = {
            'symbol': symbol,
            'is_valid': True,
            'issues': [],
            'warnings': [],
            'statistics': {}
        }
        
        try:
            # Check for empty data
            if data.empty:
                validation_results['is_valid'] = False
                validation_results['issues'].append("No data available")
                return validation_results
            
            # Check for required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                validation_results['is_valid'] = False
                validation_results['issues'].append(f"Missing columns: {missing_columns}")
                return validation_results
            
            # Check for missing days
            missing_days = self._check_missing_days(data)
            if missing_days > 0:
                validation_results['warnings'].append(
                    f"Found {missing_days} missing trading days"
                )
            
            # Check for price anomalies
            outliers, outlier_dates = self._detect_price_outliers(data)
            if outliers > 0:
                validation_results['warnings'].append(
                    f"Found {outliers} potential price outliers: {outlier_dates[:5]}"
                )
            
            # Check for potential stock splits
            split_candidates = self._detect_potential_splits(data)
            if split_candidates:
                validation_results['warnings'].append(
                    f"Found {len(split_candidates)} potential stock splits: {split_candidates[:3]}"
                )
            
            # Check for zero/negative prices
            zero_prices = self._check_invalid_prices(data)
            if zero_prices > 0:
                validation_results['is_valid'] = False
                validation_results['issues'].append(
                    f"Found {zero_prices} records with zero or negative prices"
                )
            
            # Calculate statistics
            validation_results['statistics'] = self._calculate_statistics(data)
            
            # Set overall validity
            if len(validation_results['issues']) == 0:
                validation_results['is_valid'] = True
                logger.info(f"Data validation passed for {symbol}")
            else:
                logger.warning(
                    f"Data validation failed for {symbol}: "
                    f"{len(validation_results['issues'])} issues found"
                )
            
        except Exception as e:
            logger.error(f"Error during validation: {e}")
            validation_results['is_valid'] = False
            validation_results['issues'].append(f"Validation error: {str(e)}")
        
        return validation_results
    
    def _check_missing_days(self, data: pd.DataFrame) -> int:
        """Check for missing trading days"""
        try:
            # Generate expected business days
            date_range = pd.bdate_range(
                start=data.index.min(),
                end=data.index.max()
            )
            
            # Count missing days
            missing_days = len(date_range) - len(data)
            
            return max(0, missing_days)
            
        except Exception as e:
            logger.error(f"Error checking missing days: {e}")
            return 0
    
    def _detect_price_outliers(self, data: pd.DataFrame) -> Tuple[int, List[str]]:
        """
        Detect price outliers using z-score method
        
        Returns:
            Tuple of (outlier_count, list_of_dates)
        """
        try:
            # Calculate daily returns
            returns = data['Close'].pct_change().dropna()
            
            # Calculate z-scores
            z_scores = np.abs((returns - returns.mean()) / returns.std())
            
            # Find outliers
            outliers = z_scores[z_scores > self.outlier_threshold]
            outlier_dates = outliers.index.strftime('%Y-%m-%d').tolist()
            
            return len(outliers), outlier_dates
            
        except Exception as e:
            logger.error(f"Error detecting outliers: {e}")
            return 0, []
    
    def _detect_potential_splits(self, data: pd.DataFrame) -> List[str]:
        """
        Detect potential stock splits
        
        Stock splits typically show:
        - Large negative returns (>40%)
        - Volume spike
        """
        try:
            splits = []
            
            # Calculate returns and volume changes
            returns = data['Close'].pct_change()
            volume_ratio = data['Volume'] / data['Volume'].rolling(20).mean()
            
            # Find split candidates
            for i in range(len(data)):
                if i == 0:
                    continue
                
                daily_return = returns.iloc[i]
                vol_ratio = volume_ratio.iloc[i]
                
                # Check for split conditions
                if daily_return < -0.4 and vol_ratio > 2.0:
                    date = data.index[i].strftime('%Y-%m-%d')
                    splits.append(date)
            
            return splits
            
        except Exception as e:
            logger.error(f"Error detecting splits: {e}")
            return []
    
    def _check_invalid_prices(self, data: pd.DataFrame) -> int:
        """Check for zero or negative prices"""
        try:
            price_columns = ['Open', 'High', 'Low', 'Close']
            invalid_count = 0
            
            for col in price_columns:
                invalid_count += (data[col] <= 0).sum()
            
            return invalid_count
            
        except Exception as e:
            logger.error(f"Error checking invalid prices: {e}")
            return 0
    
    def _calculate_statistics(self, data: pd.DataFrame) -> Dict:
        """Calculate comprehensive statistics"""
        try:
            stats = {
                'record_count': len(data),
                'date_range': {
                    'start': data.index.min().strftime('%Y-%m-%d'),
                    'end': data.index.max().strftime('%Y-%m-%d'),
                    'days': (data.index.max() - data.index.min()).days
                },
                'price_range': {
                    'min': float(data['Close'].min()),
                    'max': float(data['Close'].max()),
                    'mean': float(data['Close'].mean()),
                    'std': float(data['Close'].std())
                },
                'volume': {
                    'mean': float(data['Volume'].mean()),
                    'std': float(data['Volume'].std()),
                    'total': int(data['Volume'].sum())
                }
            }
            
            # Calculate returns statistics
            returns = data['Close'].pct_change().dropna()
            stats['returns'] = {
                'mean_daily': float(returns.mean()),
                'std_daily': float(returns.std()),
                'min': float(returns.min()),
                'max': float(returns.max())
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {}
    
    def adjust_for_splits(self, data: pd.DataFrame, split_dates: List[str]) -> pd.DataFrame:
        """
        Adjust historical data for stock splits
        
        Args:
            data: DataFrame with OHLCV data
            split_dates: List of split dates (YYYY-MM-DD)
        
        Returns:
            Adjusted DataFrame
        """
        try:
            adjusted_data = data.copy()
            
            for split_date in split_dates:
                split_dt = pd.to_datetime(split_date)
                
                # Find the split ratio
                if split_dt in data.index and split_dt > data.index.min():
                    prev_close = data.loc[:split_dt].iloc[-2]['Close']
                    split_close = data.loc[split_dt, 'Close']
                    split_ratio = prev_close / split_close
                    
                    # Adjust prices before split
                    mask = adjusted_data.index < split_dt
                    adjusted_data.loc[mask, ['Open', 'High', 'Low', 'Close']] /= split_ratio
                    adjusted_data.loc[mask, 'Volume'] *= split_ratio
                    
                    logger.info(
                        f"Adjusted for {split_ratio:.2f}:1 split on {split_date}"
                    )
            
            return adjusted_data
            
        except Exception as e:
            logger.error(f"Error adjusting for splits: {e}")
            return data
