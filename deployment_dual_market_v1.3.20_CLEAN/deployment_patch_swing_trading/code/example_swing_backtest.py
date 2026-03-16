"""
Example: 5-Day Swing Trading Backtest with Real Sentiment
===========================================================

Demonstrates how to run the new swing trading backtest module.

Usage:
    python example_swing_backtest.py

Author: FinBERT v4.4.4 Enhanced
Date: December 2025
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime
import pandas as pd
from swing_trader_engine import SwingTraderEngine
from news_sentiment_fetcher import NewsSentimentFetcher
from data_loader import HistoricalDataLoader


def run_example_swing_backtest():
    """Run a complete example of 5-day swing trading backtest"""
    
    print("=" * 80)
    print("5-DAY SWING TRADING BACKTEST WITH REAL SENTIMENT")
    print("=" * 80)
    
    # Configuration
    symbol = 'AAPL'
    start_date = '2024-01-01'
    end_date = '2024-12-31'
    
    print(f"\nSymbol: {symbol}")
    print(f"Period: {start_date} to {end_date}")
    print(f"Strategy: 5-day hold period with sentiment analysis")
    
    # Step 1: Load historical price data
    print("\n" + "-" * 80)
    print("STEP 1: Loading Historical Price Data")
    print("-" * 80)
    
    loader = HistoricalDataLoader(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        use_cache=True
    )
    
    price_data = loader.load_price_data(interval='1d')
    
    if price_data.empty:
        print(f"ERROR: No price data available for {symbol}")
        return
    
    print(f"✓ Loaded {len(price_data)} days of price data")
    print(f"  Date range: {price_data.index[0].date()} to {price_data.index[-1].date()}")
    print(f"  Price range: ${price_data['Close'].min():.2f} - ${price_data['Close'].max():.2f}")
    
    # Step 2: Fetch historical news sentiment
    print("\n" + "-" * 80)
    print("STEP 2: Fetching Historical News Sentiment")
    print("-" * 80)
    
    fetcher = NewsSentimentFetcher(use_finbert=True)
    
    news_data = fetcher.get_historical_sentiment(
        symbol=symbol,
        start_date=datetime.strptime(start_date, '%Y-%m-%d'),
        end_date=datetime.strptime(end_date, '%Y-%m-%d'),
        lookback_days=7
    )
    
    if news_data.empty:
        print("⚠️  No news data found (will use technical signals only)")
    else:
        print(f"✓ Loaded {len(news_data)} news articles with sentiment")
        
        # Show sentiment distribution
        sentiment_counts = news_data['sentiment_label'].value_counts()
        print("\nSentiment Distribution:")
        for label, count in sentiment_counts.items():
            pct = (count / len(news_data)) * 100
            print(f"  {label}: {count} ({pct:.1f}%)")
        
        avg_sentiment = news_data['sentiment_score'].mean()
        print(f"\nAverage Sentiment Score: {avg_sentiment:.3f}")
    
    # Step 3: Initialize swing trading engine
    print("\n" + "-" * 80)
    print("STEP 3: Initializing Swing Trading Engine")
    print("-" * 80)
    
    engine = SwingTraderEngine(
        initial_capital=100000.0,
        holding_period_days=5,
        stop_loss_percent=3.0,
        sentiment_weight=0.30,  # 30% sentiment
        technical_weight=0.35,   # 35% technical
        momentum_weight=0.20,    # 20% momentum
        volume_weight=0.15,      # 15% volume
        confidence_threshold=0.65,
        max_position_size=0.25,  # 25% per position
        use_real_sentiment=True,
        sentiment_lookback_days=3
    )
    
    print("✓ Engine initialized with parameters:")
    print(f"  Initial Capital: ${engine.initial_capital:,.2f}")
    print(f"  Holding Period: {engine.holding_period_days} days")
    print(f"  Stop Loss: {engine.stop_loss_percent}%")
    print(f"  Model Weights: Sentiment={engine.sentiment_weight:.0%}, "
          f"Technical={engine.technical_weight:.0%}, "
          f"Momentum={engine.momentum_weight:.0%}, "
          f"Volume={engine.volume_weight:.0%}")
    print(f"  Confidence Threshold: {engine.confidence_threshold:.0%}")
    print(f"  Max Position Size: {engine.max_position_size:.0%}")
    
    # Step 4: Run backtest
    print("\n" + "-" * 80)
    print("STEP 4: Running Backtest")
    print("-" * 80)
    
    results = engine.run_backtest(
        symbol=symbol,
        price_data=price_data,
        start_date=start_date,
        end_date=end_date,
        news_data=news_data if not news_data.empty else None
    )
    
    # Step 5: Display results
    print("\n" + "=" * 80)
    print("BACKTEST RESULTS")
    print("=" * 80)
    
    if 'error' in results:
        print(f"ERROR: {results['error']}")
        return
    
    # Performance Summary
    print("\nPERFORMANCE SUMMARY:")
    print("-" * 80)
    print(f"Strategy: {results['strategy']}")
    print(f"Symbol: {results['symbol']}")
    print(f"Period: {results['start_date']} to {results['end_date']}")
    print()
    print(f"Initial Capital: ${results['initial_capital']:,.2f}")
    print(f"Final Capital:   ${results['final_capital']:,.2f}")
    print(f"Total Return:    {results['total_return_pct']:+.2f}%")
    print(f"Total P&L:       ${results['total_pnl']:+,.2f}")
    
    # Trade Statistics
    print("\nTRADE STATISTICS:")
    print("-" * 80)
    print(f"Total Trades:    {results['total_trades']}")
    print(f"Winning Trades:  {results['winning_trades']}")
    print(f"Losing Trades:   {results['losing_trades']}")
    print(f"Win Rate:        {results['win_rate']:.2f}%")
    print()
    print(f"Average Win:     ${results['avg_win']:,.2f}")
    print(f"Average Loss:    ${results['avg_loss']:,.2f}")
    print(f"Largest Win:     ${results['largest_win']:,.2f}")
    print(f"Largest Loss:    ${results['largest_loss']:,.2f}")
    print(f"Profit Factor:   {results['profit_factor']:.2f}")
    
    # Risk Metrics
    print("\nRISK METRICS:")
    print("-" * 80)
    print(f"Sharpe Ratio:    {results['sharpe_ratio']:.2f}")
    print(f"Max Drawdown:    {results['max_drawdown']:.2f}%")
    print(f"Avg Days Held:   {results['avg_days_held']:.1f} days")
    
    # Exit Reasons
    print("\nEXIT REASONS:")
    print("-" * 80)
    for reason, count in results['exit_reasons'].items():
        pct = (count / results['total_trades']) * 100
        print(f"{reason}: {count} ({pct:.1f}%)")
    
    # Sentiment Correlation
    if 'sentiment_correlation' in results and results['sentiment_correlation'] != 0:
        print("\nSENTIMENT ANALYSIS:")
        print("-" * 80)
        corr = results['sentiment_correlation']
        print(f"Sentiment-Performance Correlation: {corr:.3f}")
        if abs(corr) > 0.3:
            direction = "POSITIVE" if corr > 0 else "NEGATIVE"
            strength = "STRONG" if abs(corr) > 0.5 else "MODERATE"
            print(f"→ {strength} {direction} correlation between sentiment and trade outcomes")
        else:
            print("→ WEAK correlation between sentiment and trade outcomes")
    
    # Individual Trades
    print("\n" + "=" * 80)
    print("INDIVIDUAL TRADES (Last 10)")
    print("=" * 80)
    
    trades = results['trades'][-10:]  # Last 10 trades
    
    print(f"\n{'Entry Date':<12} {'Exit Date':<12} {'Days':<5} {'Entry $':<10} {'Exit $':<10} "
          f"{'P&L $':<12} {'P&L %':<10} {'Exit Reason':<15}")
    print("-" * 105)
    
    for trade in trades:
        entry_date = pd.to_datetime(trade['entry_date']).strftime('%Y-%m-%d')
        exit_date = pd.to_datetime(trade['exit_date']).strftime('%Y-%m-%d')
        days = trade['days_held']
        entry_price = trade['entry_price']
        exit_price = trade['exit_price']
        pnl = trade['pnl']
        pnl_pct = trade['pnl_percent']
        exit_reason = trade['exit_reason']
        
        pnl_str = f"${pnl:+,.2f}" if pnl < 0 else f"${pnl:,.2f}"
        pnl_pct_str = f"{pnl_pct:+.2f}%"
        
        print(f"{entry_date:<12} {exit_date:<12} {days:<5} ${entry_price:<9.2f} ${exit_price:<9.2f} "
              f"{pnl_str:<12} {pnl_pct_str:<10} {exit_reason:<15}")
    
    print("\n" + "=" * 80)
    print("BACKTEST COMPLETE")
    print("=" * 80)
    
    # Comparison with current backtest
    print("\nCOMPARISON WITH CURRENT BACKTEST:")
    print("-" * 80)
    print("Current Module (Fake LSTM):")
    print("  • Daily predictions with lagging indicators")
    print("  • NO sentiment data")
    print("  • Typical results: -0.86% to -2.61% return, 20-45% win rate")
    print()
    print("New Swing Module (Real Strategy):")
    print(f"  • 5-day hold period with REAL sentiment")
    print(f"  • Combines 4 components (sentiment + technical + momentum + volume)")
    print(f"  • Results: {results['total_return_pct']:+.2f}% return, {results['win_rate']:.1f}% win rate")
    
    improvement = results['total_return_pct'] - (-0.86)
    print(f"\nImprovement: {improvement:+.2f} percentage points!")


if __name__ == '__main__':
    try:
        run_example_swing_backtest()
    except KeyboardInterrupt:
        print("\n\nBacktest interrupted by user")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
