"""
Example Backtesting Integration
================================

Demonstrates how to use all three phases of the backtesting framework together:
1. Load historical data with caching
2. Generate predictions with walk-forward validation
3. Simulate trading with realistic costs

This example can be customized for different symbols, date ranges, and models.

Author: FinBERT v4.0
Date: October 2024
"""

import logging
import pandas as pd
from datetime import datetime, timedelta

# Import backtesting components
from data_loader import HistoricalDataLoader
from prediction_engine import BacktestPredictionEngine
from trading_simulator import TradingSimulator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def run_complete_backtest(
    symbol: str,
    start_date: str,
    end_date: str,
    model_type: str = 'ensemble',
    initial_capital: float = 10000.0,
    lookback_days: int = 60,
    prediction_frequency: str = 'daily'
):
    """
    Run a complete backtest pipeline
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA', 'CBA.AX')
        start_date: Backtest start date (YYYY-MM-DD)
        end_date: Backtest end date (YYYY-MM-DD)
        model_type: 'finbert', 'lstm', or 'ensemble'
        initial_capital: Starting capital for trading
        lookback_days: Days of history for each prediction
        prediction_frequency: 'daily', 'weekly', or 'monthly'
    
    Returns:
        Dictionary with results and performance metrics
    """
    logger.info("=" * 80)
    logger.info(f"STARTING COMPLETE BACKTEST: {symbol}")
    logger.info(f"Period: {start_date} to {end_date}")
    logger.info(f"Model: {model_type}, Capital: ${initial_capital:,.2f}")
    logger.info("=" * 80)
    
    # =========================================================================
    # PHASE 1: Load Historical Data
    # =========================================================================
    logger.info("\n[PHASE 1] Loading historical data...")
    
    # Calculate required start date (need extra data for lookback)
    backtest_start = pd.to_datetime(start_date)
    data_start = (backtest_start - timedelta(days=lookback_days + 30)).strftime('%Y-%m-%d')
    
    # Initialize data loader
    loader = HistoricalDataLoader(
        symbol=symbol,
        start_date=data_start,
        end_date=end_date,
        use_cache=True,
        validate_data=True
    )
    
    # Load price data
    historical_data = loader.load_price_data(interval='1d')
    
    if historical_data.empty:
        logger.error("Failed to load historical data")
        return None
    
    logger.info(f"Loaded {len(historical_data)} days of historical data")
    logger.info(f"Date range: {historical_data.index.min()} to {historical_data.index.max()}")
    logger.info(f"Price range: ${historical_data['Close'].min():.2f} - ${historical_data['Close'].max():.2f}")
    
    # =========================================================================
    # PHASE 2: Generate Predictions
    # =========================================================================
    logger.info("\n[PHASE 2] Generating predictions with walk-forward validation...")
    
    # Initialize prediction engine
    engine = BacktestPredictionEngine(
        model_type=model_type,
        confidence_threshold=0.6
    )
    
    # Run walk-forward backtest
    predictions_df = engine.walk_forward_backtest(
        data=historical_data,
        start_date=start_date,
        end_date=end_date,
        prediction_frequency=prediction_frequency,
        lookback_days=lookback_days
    )
    
    if predictions_df.empty:
        logger.error("Failed to generate predictions")
        return None
    
    logger.info(f"Generated {len(predictions_df)} predictions")
    
    # Evaluate prediction accuracy
    eval_metrics = engine.evaluate_predictions(predictions_df)
    logger.info("\nPrediction Evaluation:")
    logger.info(f"  Total predictions: {eval_metrics.get('total_predictions', 0)}")
    logger.info(f"  Actionable signals: {eval_metrics.get('actionable_predictions', 0)}")
    logger.info(f"  Buy signals: {eval_metrics.get('buy_signals', 0)}")
    logger.info(f"  Sell signals: {eval_metrics.get('sell_signals', 0)}")
    logger.info(f"  Overall accuracy: {eval_metrics.get('overall_accuracy', 0)*100:.2f}%")
    logger.info(f"  Buy accuracy: {eval_metrics.get('buy_accuracy', 0)*100:.2f}%")
    logger.info(f"  Sell accuracy: {eval_metrics.get('sell_accuracy', 0)*100:.2f}%")
    
    # =========================================================================
    # PHASE 3: Simulate Trading
    # =========================================================================
    logger.info("\n[PHASE 3] Simulating trading with realistic costs...")
    
    # Initialize trading simulator
    simulator = TradingSimulator(
        initial_capital=initial_capital,
        commission_rate=0.001,   # 0.1%
        slippage_rate=0.0005,    # 0.05%
        max_position_size=0.20   # 20% max
    )
    
    # Execute predictions as trades
    for idx, row in predictions_df.iterrows():
        timestamp = row['timestamp']
        prediction = row['prediction']
        confidence = row['confidence']
        actual_price = row.get('actual_price', row['current_price'])
        
        # Execute signal
        result = simulator.execute_signal(
            timestamp=timestamp,
            signal=prediction,
            price=actual_price,
            confidence=confidence,
            actual_price=actual_price
        )
        
        # Update equity curve
        simulator.update_equity(timestamp, {symbol: actual_price})
    
    # Close any remaining positions at end of backtest
    if simulator.positions:
        last_price = predictions_df.iloc[-1]['actual_price']
        last_timestamp = predictions_df.iloc[-1]['timestamp']
        simulator._close_positions(last_timestamp, last_price)
    
    # =========================================================================
    # Calculate Performance Metrics
    # =========================================================================
    logger.info("\n[RESULTS] Calculating performance metrics...")
    
    performance = simulator.calculate_performance_metrics()
    
    logger.info("\n" + "=" * 80)
    logger.info("BACKTEST RESULTS")
    logger.info("=" * 80)
    logger.info(f"\nCapital:")
    logger.info(f"  Initial: ${performance['initial_capital']:,.2f}")
    logger.info(f"  Final:   ${performance['final_equity']:,.2f}")
    logger.info(f"  Return:  {performance['total_return_pct']:.2f}%")
    
    logger.info(f"\nTrades:")
    logger.info(f"  Total:   {performance['total_trades']}")
    logger.info(f"  Winners: {performance['winning_trades']} ({performance['win_rate']*100:.2f}%)")
    logger.info(f"  Losers:  {performance['losing_trades']}")
    logger.info(f"  Avg Win: ${performance['avg_win']:.2f}")
    logger.info(f"  Avg Loss: ${performance['avg_loss']:.2f}")
    logger.info(f"  Profit Factor: {performance['profit_factor']:.2f}")
    
    logger.info(f"\nRisk Metrics:")
    logger.info(f"  Sharpe Ratio:  {performance['sharpe_ratio']:.2f}")
    logger.info(f"  Sortino Ratio: {performance['sortino_ratio']:.2f}")
    logger.info(f"  Max Drawdown:  {performance['max_drawdown_pct']:.2f}%")
    
    logger.info(f"\nCosts:")
    logger.info(f"  Total Commission: ${performance['total_commission_paid']:.2f}")
    logger.info(f"  Avg Hold Time:    {performance['avg_hold_time_days']:.1f} days")
    
    logger.info("\n" + "=" * 80)
    
    # Return complete results
    return {
        'symbol': symbol,
        'backtest_period': {
            'start': start_date,
            'end': end_date
        },
        'model_type': model_type,
        'predictions': predictions_df,
        'prediction_metrics': eval_metrics,
        'trading_performance': performance,
        'equity_curve': simulator.get_equity_curve_df(),
        'trades': simulator.get_trades_df()
    }


def compare_models(
    symbol: str,
    start_date: str,
    end_date: str,
    initial_capital: float = 10000.0
):
    """
    Compare performance of different models
    
    Args:
        symbol: Stock ticker symbol
        start_date: Backtest start date
        end_date: Backtest end date
        initial_capital: Starting capital
    
    Returns:
        Dictionary comparing all models
    """
    logger.info("\n" + "=" * 80)
    logger.info("MODEL COMPARISON")
    logger.info("=" * 80)
    
    models = ['finbert', 'lstm', 'ensemble']
    results = {}
    
    for model in models:
        logger.info(f"\n\nTesting {model.upper()} model...")
        result = run_complete_backtest(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            model_type=model,
            initial_capital=initial_capital
        )
        
        if result:
            results[model] = result
    
    # Compare results
    logger.info("\n\n" + "=" * 80)
    logger.info("MODEL COMPARISON SUMMARY")
    logger.info("=" * 80)
    
    comparison_df = pd.DataFrame({
        model: {
            'Total Return %': results[model]['trading_performance']['total_return_pct'],
            'Win Rate %': results[model]['trading_performance']['win_rate'] * 100,
            'Sharpe Ratio': results[model]['trading_performance']['sharpe_ratio'],
            'Max Drawdown %': results[model]['trading_performance']['max_drawdown_pct'],
            'Total Trades': results[model]['trading_performance']['total_trades'],
            'Profit Factor': results[model]['trading_performance']['profit_factor']
        }
        for model in results
    })
    
    logger.info("\n" + comparison_df.to_string())
    
    return results


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == '__main__':
    # Example 1: Single backtest
    logger.info("EXAMPLE 1: Single Model Backtest")
    
    result = run_complete_backtest(
        symbol='AAPL',
        start_date='2023-01-01',
        end_date='2024-01-01',
        model_type='ensemble',
        initial_capital=10000.0,
        lookback_days=60,
        prediction_frequency='daily'
    )
    
    if result:
        # Save results to CSV
        result['predictions'].to_csv('backtest_predictions.csv')
        result['trades'].to_csv('backtest_trades.csv')
        result['equity_curve'].to_csv('backtest_equity_curve.csv')
        logger.info("\nResults saved to CSV files")
    
    # Example 2: Compare models
    logger.info("\n\nEXAMPLE 2: Model Comparison")
    
    comparison_results = compare_models(
        symbol='AAPL',
        start_date='2023-01-01',
        end_date='2024-01-01',
        initial_capital=10000.0
    )
    
    # Example 3: Australian stock (CBA.AX)
    logger.info("\n\nEXAMPLE 3: Australian Stock Backtest")
    
    cba_result = run_complete_backtest(
        symbol='CBA.AX',
        start_date='2023-01-01',
        end_date='2024-01-01',
        model_type='ensemble',
        initial_capital=10000.0
    )
