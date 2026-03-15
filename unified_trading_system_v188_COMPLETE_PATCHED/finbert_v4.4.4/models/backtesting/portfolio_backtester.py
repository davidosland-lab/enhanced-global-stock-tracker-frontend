"""
Portfolio Backtest Orchestrator
================================

Coordinates portfolio backtesting across multiple stocks with walk-forward validation.

Combines:
- Data loading for multiple symbols
- Prediction generation for each stock
- Portfolio-level capital allocation
- Performance tracking and analysis

Author: FinBERT v4.0
Date: November 2025
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .data_loader import HistoricalDataLoader
from .prediction_engine import BacktestPredictionEngine
from .portfolio_engine import PortfolioBacktestEngine

logger = logging.getLogger(__name__)


class PortfolioBacktester:
    """
    Orchestrates portfolio backtesting across multiple stocks
    
    Manages data loading, prediction generation, and portfolio execution
    for multi-stock backtesting with proper walk-forward validation.
    """
    
    def __init__(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        initial_capital: float = 10000.0,
        model_type: str = 'ensemble',
        allocation_strategy: str = 'equal',
        custom_allocations: Optional[Dict[str, float]] = None,
        confidence_threshold: float = 0.6,
        lookback_days: int = 60,
        prediction_frequency: str = 'daily',
        rebalance_frequency: str = 'monthly',
        commission_rate: float = 0.001,
        slippage_rate: float = 0.0005,
        use_cache: bool = True
    ):
        """
        Initialize portfolio backtester
        
        Args:
            symbols: List of stock ticker symbols
            start_date: Backtest start date (YYYY-MM-DD)
            end_date: Backtest end date (YYYY-MM-DD)
            initial_capital: Starting capital
            model_type: Prediction model ('lstm', 'technical', 'momentum', 'ensemble')
            allocation_strategy: 'equal', 'risk_parity', or 'custom'
            custom_allocations: Custom allocation weights (symbol -> weight)
            confidence_threshold: Minimum confidence for signals
            lookback_days: Historical data window for predictions
            prediction_frequency: 'daily', 'weekly', or 'monthly'
            rebalance_frequency: 'never', 'weekly', 'monthly', 'quarterly'
            commission_rate: Commission as fraction
            slippage_rate: Slippage as fraction
            use_cache: Use data caching
        """
        self.symbols = [s.upper() for s in symbols]
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.model_type = model_type
        self.allocation_strategy = allocation_strategy
        self.custom_allocations = custom_allocations or {}
        self.confidence_threshold = confidence_threshold
        self.lookback_days = lookback_days
        self.prediction_frequency = prediction_frequency
        self.rebalance_frequency = rebalance_frequency
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.use_cache = use_cache
        
        logger.info(
            f"Portfolio backtester initialized: {len(symbols)} stocks, "
            f"{start_date} to {end_date}, {allocation_strategy} allocation"
        )
    
    def run_backtest(self) -> Dict:
        """
        Run complete portfolio backtest
        
        Returns:
            Dictionary with backtest results and performance metrics
        """
        logger.info("Starting portfolio backtest...")
        
        try:
            # Step 1: Load historical data for all symbols
            logger.info(f"Loading data for {len(self.symbols)} symbols...")
            historical_data = self._load_all_data()
            
            if not historical_data:
                return {'error': 'Failed to load data for any symbols'}
            
            logger.info(f"Successfully loaded data for {len(historical_data)} symbols")
            
            # Step 2: Generate predictions for each symbol
            logger.info("Generating predictions for all symbols...")
            predictions_by_symbol = self._generate_predictions(historical_data)
            
            if not predictions_by_symbol:
                return {'error': 'Failed to generate predictions'}
            
            # Step 3: Calculate historical returns for risk-parity (if needed)
            historical_returns = None
            if self.allocation_strategy == 'risk_parity':
                historical_returns = self._calculate_historical_returns(historical_data)
            
            # Step 4: Initialize portfolio engine
            portfolio_engine = PortfolioBacktestEngine(
                initial_capital=self.initial_capital,
                allocation_strategy=self.allocation_strategy,
                custom_allocations=self.custom_allocations,
                rebalance_frequency=self.rebalance_frequency,
                commission_rate=self.commission_rate,
                slippage_rate=self.slippage_rate
            )
            
            # Step 5: Calculate target allocations
            target_allocations = portfolio_engine.calculate_target_allocations(
                symbols=list(predictions_by_symbol.keys()),
                historical_returns=historical_returns
            )
            
            logger.info(f"Target allocations: {target_allocations}")
            
            # Step 6: Execute portfolio backtest
            logger.info("Executing portfolio trades...")
            execution_results = self._execute_portfolio_backtest(
                portfolio_engine=portfolio_engine,
                predictions_by_symbol=predictions_by_symbol,
                historical_data=historical_data,
                target_allocations=target_allocations
            )
            
            # Step 7: Calculate portfolio metrics
            logger.info("Calculating portfolio metrics...")
            portfolio_metrics = portfolio_engine.calculate_portfolio_metrics()
            
            # Step 8: Calculate correlation and diversification metrics
            correlation_matrix = portfolio_engine.calculate_correlation_matrix(
                historical_returns or self._calculate_historical_returns(historical_data)
            )
            
            diversification_metrics = portfolio_engine.calculate_diversification_metrics(
                correlation_matrix=correlation_matrix,
                allocations=target_allocations
            )
            
            # Step 9: Compile results
            results = {
                'status': 'success',
                'backtest_config': {
                    'symbols': self.symbols,
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'initial_capital': self.initial_capital,
                    'model_type': self.model_type,
                    'allocation_strategy': self.allocation_strategy,
                    'prediction_frequency': self.prediction_frequency,
                    'rebalance_frequency': self.rebalance_frequency
                },
                'portfolio_metrics': portfolio_metrics,
                'target_allocations': target_allocations,
                'diversification': diversification_metrics,
                'correlation_matrix': correlation_matrix.to_dict() if not correlation_matrix.empty else {},
                'symbols_loaded': list(historical_data.keys()),
                'total_predictions': sum(len(preds) for preds in predictions_by_symbol.values()),
                'execution_summary': execution_results
            }
            
            logger.info("Portfolio backtest complete!")
            return results
            
        except Exception as e:
            logger.error(f"Error in portfolio backtest: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}
    
    def _load_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load historical data for all symbols"""
        return HistoricalDataLoader.load_multiple_symbols(
            symbols=self.symbols,
            start_date=self.start_date,
            end_date=self.end_date,
            interval='1d',
            use_cache=self.use_cache
        )
    
    def _generate_predictions(
        self,
        historical_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate predictions for each symbol
        
        Args:
            historical_data: Dictionary mapping symbol to historical data
        
        Returns:
            Dictionary mapping symbol to predictions DataFrame
        """
        predictions_by_symbol = {}
        
        for symbol, data in historical_data.items():
            try:
                logger.info(f"Generating predictions for {symbol}...")
                
                # Create prediction engine for this symbol
                predictor = BacktestPredictionEngine(
                    model_type=self.model_type,
                    confidence_threshold=self.confidence_threshold
                )
                
                # Generate predictions
                predictions_df = predictor.walk_forward_backtest(
                    data=data,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    prediction_frequency=self.prediction_frequency,
                    lookback_days=self.lookback_days
                )
                
                if not predictions_df.empty:
                    predictions_by_symbol[symbol] = predictions_df
                    logger.info(
                        f"Generated {len(predictions_df)} predictions for {symbol}"
                    )
                else:
                    logger.warning(f"No predictions generated for {symbol}")
                    
            except Exception as e:
                logger.error(f"Error generating predictions for {symbol}: {e}")
        
        return predictions_by_symbol
    
    def _calculate_historical_returns(
        self,
        historical_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.Series]:
        """Calculate historical returns for each symbol"""
        returns = {}
        
        for symbol, data in historical_data.items():
            if 'Close' in data.columns:
                returns[symbol] = data['Close'].pct_change().dropna()
        
        return returns
    
    def _execute_portfolio_backtest(
        self,
        portfolio_engine: PortfolioBacktestEngine,
        predictions_by_symbol: Dict[str, pd.DataFrame],
        historical_data: Dict[str, pd.DataFrame],
        target_allocations: Dict[str, float]
    ) -> Dict:
        """
        Execute portfolio backtest with all signals
        
        Args:
            portfolio_engine: Portfolio backtesting engine
            predictions_by_symbol: Predictions for each symbol
            historical_data: Historical price data
            target_allocations: Target allocation weights
        
        Returns:
            Execution summary
        """
        # Get all unique timestamps across all symbols
        all_timestamps = set()
        for predictions_df in predictions_by_symbol.values():
            timestamps = predictions_df['timestamp'].tolist()
            # Normalize timestamps to remove timezone info
            timestamps = [pd.to_datetime(ts).tz_localize(None) if hasattr(pd.to_datetime(ts), 'tz') and pd.to_datetime(ts).tz is not None else pd.to_datetime(ts) for ts in timestamps]
            all_timestamps.update(timestamps)
        
        # Sort timestamps
        sorted_timestamps = sorted(list(all_timestamps))
        
        logger.info(f"Executing {len(sorted_timestamps)} trading periods...")
        
        total_executions = 0
        total_buys = 0
        total_sells = 0
        
        for i, timestamp in enumerate(sorted_timestamps):
            if (i + 1) % 100 == 0:
                logger.info(f"Processing {i+1}/{len(sorted_timestamps)} periods...")
            
            # Get signals for all symbols at this timestamp
            signals = {}
            current_prices = {}
            
            for symbol, predictions_df in predictions_by_symbol.items():
                try:
                    # Normalize timestamp for comparison
                    norm_timestamp = pd.to_datetime(timestamp).tz_localize(None) if hasattr(pd.to_datetime(timestamp), 'tz') and pd.to_datetime(timestamp).tz is not None else pd.to_datetime(timestamp)
                    
                    # Normalize prediction timestamps
                    pred_timestamps = predictions_df['timestamp'].apply(lambda x: pd.to_datetime(x).tz_localize(None) if hasattr(pd.to_datetime(x), 'tz') and pd.to_datetime(x).tz is not None else pd.to_datetime(x))
                    
                    # Find prediction for this timestamp
                    matching_idx = pred_timestamps[pred_timestamps == norm_timestamp].index
                    
                    if len(matching_idx) > 0:
                        pred = predictions_df.iloc[matching_idx[0]]
                        signals[symbol] = {
                            'prediction': pred['prediction'],
                            'confidence': pred['confidence']
                        }
                        
                        # Get current price
                        if 'actual_price' in pred:
                            current_prices[symbol] = pred['actual_price']
                        elif 'current_price' in pred:
                            current_prices[symbol] = pred['current_price']
                        else:
                            # Fallback: get from historical data
                            data = historical_data[symbol]
                            # Ensure data index is timezone-naive
                            if data.index.tz is not None:
                                data.index = data.index.tz_localize(None)
                            price_data = data[data.index == norm_timestamp]
                            if not price_data.empty:
                                current_prices[symbol] = price_data['Close'].iloc[0]
                except Exception as e:
                    logger.warning(f"Error processing signal for {symbol} at {timestamp}: {e}")
            
            # Execute signals for this timestamp
            if signals and current_prices:
                execution_result = portfolio_engine.execute_portfolio_signals(
                    timestamp=timestamp,
                    signals=signals,
                    current_prices=current_prices,
                    target_allocations=target_allocations
                )
                
                # Count executions
                for symbol, exec_info in execution_result.get('executions', {}).items():
                    if exec_info.get('action') == 'BUY':
                        total_buys += 1
                        total_executions += 1
                    elif exec_info.get('action') == 'SELL':
                        total_sells += 1
                        total_executions += 1
        
        logger.info(
            f"Execution complete: {total_executions} total executions "
            f"({total_buys} buys, {total_sells} sells)"
        )
        
        return {
            'total_periods': len(sorted_timestamps),
            'total_executions': total_executions,
            'total_buys': total_buys,
            'total_sells': total_sells
        }


def run_portfolio_backtest(
    symbols: List[str],
    start_date: str,
    end_date: str,
    initial_capital: float = 10000.0,
    model_type: str = 'ensemble',
    allocation_strategy: str = 'equal',
    custom_allocations: Optional[Dict[str, float]] = None,
    **kwargs
) -> Dict:
    """
    Convenience function to run portfolio backtest
    
    Args:
        symbols: List of stock ticker symbols
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        initial_capital: Starting capital
        model_type: Prediction model
        allocation_strategy: Capital allocation strategy
        custom_allocations: Custom weights (if strategy='custom')
        **kwargs: Additional parameters for PortfolioBacktester
    
    Returns:
        Backtest results dictionary
    """
    backtester = PortfolioBacktester(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        model_type=model_type,
        allocation_strategy=allocation_strategy,
        custom_allocations=custom_allocations,
        **kwargs
    )
    
    return backtester.run_backtest()
