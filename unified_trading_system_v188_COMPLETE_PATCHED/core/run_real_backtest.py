#!/usr/bin/env python3
"""
Real Historical Backtest Runner
================================

Runs real historical backtests using the FinBERT v4.4.4 backtest module
integrated into the unified trading system.

Features:
- Real Yahoo Finance data (no synthetic data)
- Walk-forward validation (no look-ahead bias)
- Three prediction models: LSTM, Technical, Momentum, Ensemble
- Portfolio-level management
- Realistic execution costs

Usage:
    # Single stock backtest
    python run_real_backtest.py --symbol AAPL --start 2024-02-27 --end 2025-02-27
    
    # Portfolio backtest (multiple stocks)
    python run_real_backtest.py \
        --symbols AAPL,MSFT,GOOGL,CBA.AX,BHP.AX \
        --start 2024-02-27 \
        --end 2025-02-27 \
        --capital 100000 \
        --model ensemble \
        --confidence 0.48
    
    # 30-stock portfolio (AU, UK, US)
    python run_real_backtest.py --preset 30stocks --start 2024-02-27 --end 2025-02-27

Version: 1.0.0
Date: February 28, 2026
"""

import os
import sys
from pathlib import Path
import argparse
import logging
from datetime import datetime
import json
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import backtesting components
from core.backtesting import (
    HistoricalDataLoader,
    BacktestPredictionEngine,
    PortfolioBacktester,
    TradingSimulator
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/real_backtest.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Stock presets
PRESETS = {
    '30stocks': [
        # Australia (10)
        'CBA.AX', 'BHP.AX', 'NAB.AX', 'WBC.AX', 'ANZ.AX',
        'WES.AX', 'CSL.AX', 'RIO.AX', 'TLS.AX', 'WOW.AX',
        # UK (10)
        'BP.L', 'HSBA.L', 'SHEL.L', 'ULVR.L', 'AZN.L',
        'GSK.L', 'DGE.L', 'VOD.L', 'BATS.L', 'RIO.L',
        # US (10)
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
        'TSLA', 'NVDA', 'JPM', 'V', 'JNJ'
    ],
    'us_tech': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA'],
    'au_banks': ['CBA.AX', 'NAB.AX', 'WBC.AX', 'ANZ.AX'],
    'uk_blue_chip': ['BP.L', 'HSBA.L', 'SHEL.L', 'ULVR.L', 'AZN.L']
}


def run_single_stock_backtest(
    symbol: str,
    start_date: str,
    end_date: str,
    initial_capital: float,
    model_type: str,
    confidence_threshold: float,
    output_dir: str = 'backtest_results'
):
    """
    Run backtest for a single stock
    
    Args:
        symbol: Stock ticker symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        initial_capital: Starting capital
        model_type: 'lstm', 'technical', 'momentum', or 'ensemble'
        confidence_threshold: Minimum confidence for signals (0-1)
        output_dir: Directory to save results
    
    Returns:
        Dictionary with backtest results
    """
    logger.info("=" * 80)
    logger.info(f"SINGLE STOCK BACKTEST: {symbol}")
    logger.info(f"Period: {start_date} to {end_date}")
    logger.info(f"Capital: ${initial_capital:,.2f}")
    logger.info(f"Model: {model_type}, Confidence: {confidence_threshold}")
    logger.info("=" * 80)
    
    try:
        # Step 1: Load historical data
        logger.info("Loading historical data...")
        loader = HistoricalDataLoader(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            use_cache=True
        )
        data = loader.load_price_data()
        
        if data.empty:
            logger.error(f"No data loaded for {symbol}")
            return None
        
        logger.info(f"Loaded {len(data)} days of data")
        
        # Step 2: Generate predictions
        logger.info("Generating predictions with walk-forward validation...")
        predictor = BacktestPredictionEngine(
            model_type=model_type,
            confidence_threshold=confidence_threshold
        )
        predictions_df = predictor.walk_forward_backtest(
            data=data,
            start_date=start_date,
            end_date=end_date,
            prediction_frequency='daily',
            lookback_days=60
        )
        
        if predictions_df.empty:
            logger.error("No predictions generated")
            return None
        
        logger.info(f"Generated {len(predictions_df)} predictions")
        
        # Step 3: Simulate trading
        logger.info("Simulating trading...")
        simulator = TradingSimulator(
            initial_capital=initial_capital,
            commission_rate=0.001,  # 0.1%
            slippage_rate=0.0005,   # 0.05%
            max_position_size=0.25  # 25% max
        )
        
        # Execute all predictions
        for _, row in predictions_df.iterrows():
            simulator.process_signal(
                timestamp=row['timestamp'],
                symbol=symbol,
                signal=row['prediction'],
                confidence=row['confidence'],
                current_price=row.get('actual_price', row['current_price'])
            )
        
        # Get performance metrics
        performance = simulator.get_performance_metrics()
        
        # Save results
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save predictions
        pred_file = output_path / f'backtest_{symbol}_{timestamp}_predictions.csv'
        predictions_df.to_csv(pred_file, index=False)
        logger.info(f"Saved predictions to {pred_file}")
        
        # Save performance metrics
        perf_file = output_path / f'backtest_{symbol}_{timestamp}_performance.json'
        with open(perf_file, 'w') as f:
            json.dump(performance, f, indent=2)
        logger.info(f"Saved performance to {perf_file}")
        
        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("BACKTEST RESULTS SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Symbol: {symbol}")
        logger.info(f"Period: {start_date} to {end_date}")
        logger.info(f"Initial Capital: ${performance.get('initial_capital', 0):,.2f}")
        logger.info(f"Final Equity: ${performance.get('final_equity', 0):,.2f}")
        logger.info(f"Total Return: {performance.get('total_return_pct', 0):.2f}%")
        logger.info(f"Total Trades: {performance.get('total_trades', 0)}")
        logger.info(f"Win Rate: {performance.get('win_rate', 0):.2f}%")
        logger.info(f"Profit Factor: {performance.get('profit_factor', 0):.2f}")
        logger.info(f"Sharpe Ratio: {performance.get('sharpe_ratio', 0):.2f}")
        logger.info(f"Max Drawdown: {performance.get('max_drawdown_pct', 0):.2f}%")
        logger.info("=" * 80)
        
        return {
            'symbol': symbol,
            'predictions': predictions_df,
            'performance': performance
        }
        
    except Exception as e:
        logger.error(f"Error in backtest: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_portfolio_backtest_wrapper(
    symbols: list,
    start_date: str,
    end_date: str,
    initial_capital: float,
    model_type: str,
    confidence_threshold: float,
    allocation_strategy: str = 'equal',
    output_dir: str = 'backtest_results'
):
    """
    Run portfolio backtest for multiple stocks
    
    Args:
        symbols: List of stock ticker symbols
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        initial_capital: Starting capital
        model_type: 'lstm', 'technical', 'momentum', or 'ensemble'
        confidence_threshold: Minimum confidence for signals (0-1)
        allocation_strategy: 'equal', 'risk_parity', or 'custom'
        output_dir: Directory to save results
    
    Returns:
        Dictionary with backtest results
    """
    logger.info("=" * 80)
    logger.info(f"PORTFOLIO BACKTEST: {len(symbols)} stocks")
    logger.info(f"Symbols: {', '.join(symbols)}")
    logger.info(f"Period: {start_date} to {end_date}")
    logger.info(f"Capital: ${initial_capital:,.2f}")
    logger.info(f"Model: {model_type}, Confidence: {confidence_threshold}")
    logger.info(f"Allocation: {allocation_strategy}")
    logger.info("=" * 80)
    
    try:
        # Run portfolio backtest
        backtester = PortfolioBacktester(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            model_type=model_type,
            allocation_strategy=allocation_strategy,
            confidence_threshold=confidence_threshold,
            lookback_days=60,
            prediction_frequency='daily',
            commission_rate=0.001,
            slippage_rate=0.0005,
            use_cache=True
        )
        
        results = backtester.run_backtest()
        
        if results.get('status') != 'success':
            logger.error(f"Backtest failed: {results.get('error', 'Unknown error')}")
            return None
        
        # Save results
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save full results
        results_file = output_path / f'portfolio_backtest_{timestamp}.json'
        with open(results_file, 'w') as f:
            # Convert DataFrames to dict for JSON serialization
            results_copy = results.copy()
            if 'correlation_matrix' in results_copy and isinstance(results_copy['correlation_matrix'], dict):
                results_copy['correlation_matrix'] = str(results_copy['correlation_matrix'])
            json.dump(results_copy, f, indent=2, default=str)
        logger.info(f"Saved results to {results_file}")
        
        # Print summary
        metrics = results.get('portfolio_metrics', {})
        logger.info("\n" + "=" * 80)
        logger.info("PORTFOLIO BACKTEST RESULTS")
        logger.info("=" * 80)
        logger.info(f"Symbols: {len(symbols)} stocks")
        logger.info(f"Period: {start_date} to {end_date}")
        logger.info(f"Initial Capital: ${metrics.get('initial_capital', 0):,.2f}")
        logger.info(f"Final Value: ${metrics.get('final_value', 0):,.2f}")
        logger.info(f"Total Return: {metrics.get('total_return_pct', 0):.2f}%")
        logger.info(f"Total Trades: {metrics.get('total_trades', 0)}")
        logger.info(f"Win Rate: {metrics.get('win_rate', 0):.2f}%")
        logger.info(f"Profit Factor: {metrics.get('profit_factor', 0):.2f}")
        logger.info(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
        logger.info(f"Max Drawdown: {metrics.get('max_drawdown_pct', 0):.2f}%")
        logger.info(f"Commission Paid: ${metrics.get('total_commission_paid', 0):,.2f}")
        logger.info("=" * 80)
        
        return results
        
    except Exception as e:
        logger.error(f"Error in portfolio backtest: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Run real historical backtests with Yahoo Finance data'
    )
    
    # Stock selection
    parser.add_argument('--symbol', type=str, help='Single stock symbol (e.g., AAPL)')
    parser.add_argument('--symbols', type=str, help='Multiple symbols comma-separated (e.g., AAPL,MSFT,GOOGL)')
    parser.add_argument('--preset', type=str, choices=list(PRESETS.keys()), 
                       help='Use stock preset (30stocks, us_tech, au_banks, uk_blue_chip)')
    
    # Date range
    parser.add_argument('--start', type=str, required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, required=True, help='End date (YYYY-MM-DD)')
    
    # Trading parameters
    parser.add_argument('--capital', type=float, default=100000, help='Initial capital (default: 100000)')
    parser.add_argument('--model', type=str, default='ensemble', 
                       choices=['lstm', 'technical', 'momentum', 'ensemble'],
                       help='Prediction model (default: ensemble)')
    parser.add_argument('--confidence', type=float, default=0.48, 
                       help='Confidence threshold (default: 0.48)')
    parser.add_argument('--allocation', type=str, default='equal',
                       choices=['equal', 'risk_parity', 'custom'],
                       help='Portfolio allocation strategy (default: equal)')
    
    # Output
    parser.add_argument('--output', type=str, default='backtest_results',
                       help='Output directory (default: backtest_results)')
    
    args = parser.parse_args()
    
    # Determine symbols
    symbols = None
    if args.preset:
        symbols = PRESETS[args.preset]
        logger.info(f"Using preset '{args.preset}' with {len(symbols)} stocks")
    elif args.symbols:
        symbols = [s.strip() for s in args.symbols.split(',')]
    elif args.symbol:
        symbols = [args.symbol]
    else:
        parser.error("Must specify --symbol, --symbols, or --preset")
    
    # Run backtest
    if len(symbols) == 1:
        # Single stock backtest
        result = run_single_stock_backtest(
            symbol=symbols[0],
            start_date=args.start,
            end_date=args.end,
            initial_capital=args.capital,
            model_type=args.model,
            confidence_threshold=args.confidence,
            output_dir=args.output
        )
    else:
        # Portfolio backtest
        result = run_portfolio_backtest_wrapper(
            symbols=symbols,
            start_date=args.start,
            end_date=args.end,
            initial_capital=args.capital,
            model_type=args.model,
            confidence_threshold=args.confidence,
            allocation_strategy=args.allocation,
            output_dir=args.output
        )
    
    if result:
        logger.info("\n✅ Backtest completed successfully!")
        logger.info(f"Results saved to {args.output}/")
    else:
        logger.error("\n❌ Backtest failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
