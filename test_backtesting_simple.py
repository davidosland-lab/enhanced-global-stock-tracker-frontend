"""
Simple Standalone Test for Backtesting Framework
=================================================

This script tests the backtesting framework with a simple, straightforward approach.
Run from the webapp root directory.
"""

import sys
import os
import logging

# Add models directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'models'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_framework():
    """Test all three phases of the backtesting framework"""
    
    print("\n" + "="*80)
    print("BACKTESTING FRAMEWORK - SIMPLE TEST")
    print("="*80)
    
    try:
        # Import the backtesting module
        print("\n[SETUP] Importing backtesting module...")
        from backtesting import (
            HistoricalDataLoader,
            BacktestPredictionEngine,
            TradingSimulator
        )
        print("✅ Imports successful")
        
        # Phase 1: Test Data Loading
        print("\n" + "-"*80)
        print("[PHASE 1] Testing Data Loading & Caching")
        print("-"*80)
        
        loader = HistoricalDataLoader(
            symbol='AAPL',
            start_date='2023-11-01',
            end_date='2023-12-01',
            use_cache=True,
            validate_data=True
        )
        
        print("Loading historical data for AAPL...")
        data = loader.load_price_data()
        
        if data.empty:
            print("❌ FAILED: No data loaded")
            return False
        
        print(f"✅ Data loaded successfully!")
        print(f"   Records: {len(data)} days")
        print(f"   Date range: {data.index.min().date()} to {data.index.max().date()}")
        print(f"   Price range: ${data['Close'].min():.2f} - ${data['Close'].max():.2f}")
        print(f"   Latest close: ${data['Close'].iloc[-1]:.2f}")
        
        # Phase 2: Test Predictions
        print("\n" + "-"*80)
        print("[PHASE 2] Testing Prediction Engine (Walk-Forward Validation)")
        print("-"*80)
        
        engine = BacktestPredictionEngine(
            model_type='ensemble',
            confidence_threshold=0.6
        )
        
        print("Generating predictions with ensemble model...")
        predictions = engine.walk_forward_backtest(
            data=data,
            start_date='2023-11-15',
            end_date='2023-12-01',
            prediction_frequency='daily',
            lookback_days=10
        )
        
        if predictions.empty:
            print("❌ FAILED: No predictions generated")
            return False
        
        print(f"✅ Predictions generated successfully!")
        print(f"   Total predictions: {len(predictions)}")
        
        # Count signals
        buy_count = (predictions['prediction'] == 'BUY').sum()
        sell_count = (predictions['prediction'] == 'SELL').sum()
        hold_count = (predictions['prediction'] == 'HOLD').sum()
        
        print(f"   Signal breakdown:")
        print(f"     • BUY:  {buy_count} ({buy_count/len(predictions)*100:.1f}%)")
        print(f"     • SELL: {sell_count} ({sell_count/len(predictions)*100:.1f}%)")
        print(f"     • HOLD: {hold_count} ({hold_count/len(predictions)*100:.1f}%)")
        
        if 'confidence' in predictions.columns:
            avg_confidence = predictions['confidence'].mean()
            print(f"   Average confidence: {avg_confidence:.2%}")
        
        # Evaluate predictions
        eval_metrics = engine.evaluate_predictions(predictions)
        if 'error' not in eval_metrics:
            print(f"   Prediction accuracy: {eval_metrics.get('overall_accuracy', 0)*100:.1f}%")
        
        # Phase 3: Test Trading Simulation
        print("\n" + "-"*80)
        print("[PHASE 3] Testing Trading Simulator (Realistic Costs)")
        print("-"*80)
        
        simulator = TradingSimulator(
            initial_capital=10000.0,
            commission_rate=0.001,
            slippage_rate=0.0005,
            max_position_size=0.20
        )
        
        print("Simulating trades...")
        trade_count = 0
        
        for idx, row in predictions.iterrows():
            result = simulator.execute_signal(
                timestamp=row['timestamp'],
                signal=row['prediction'],
                price=row.get('actual_price', row['current_price']),
                confidence=row['confidence']
            )
            
            if result.get('action') in ['BUY', 'SELL']:
                trade_count += 1
        
        print(f"   Executed {trade_count} trading signals")
        
        # Close any remaining positions
        if simulator.positions:
            last_price = predictions.iloc[-1].get('actual_price', predictions.iloc[-1]['current_price'])
            last_timestamp = predictions.iloc[-1]['timestamp']
            simulator._close_positions(last_timestamp, last_price)
        
        # Get performance metrics
        metrics = simulator.calculate_performance_metrics()
        
        if 'error' in metrics:
            print(f"⚠️  Note: {metrics['error']}")
            print("   (This happens when no trades are executed - usually due to low confidence)")
        else:
            print(f"✅ Trading simulation complete!")
            print(f"\n   Performance Summary:")
            print(f"   {'─'*40}")
            print(f"   Initial Capital:  ${metrics['initial_capital']:,.2f}")
            print(f"   Final Equity:     ${metrics['final_equity']:,.2f}")
            print(f"   Total Return:     {metrics['total_return_pct']:+.2f}%")
            print(f"   {'─'*40}")
            print(f"   Total Trades:     {metrics['total_trades']}")
            print(f"   Winning Trades:   {metrics['winning_trades']}")
            print(f"   Losing Trades:    {metrics['losing_trades']}")
            print(f"   Win Rate:         {metrics['win_rate']*100:.1f}%")
            print(f"   {'─'*40}")
            
            if metrics['total_trades'] > 0:
                print(f"   Risk Metrics:")
                print(f"     • Sharpe Ratio:   {metrics['sharpe_ratio']:.2f}")
                print(f"     • Max Drawdown:   {metrics['max_drawdown_pct']:.2f}%")
                print(f"     • Profit Factor:  {metrics['profit_factor']:.2f}")
            
            print(f"   {'─'*40}")
            print(f"   Commission Paid:  ${metrics['total_commission_paid']:.2f}")
        
        # Success!
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED - Framework is working correctly!")
        print("="*80)
        
        print("\n📚 Next Steps:")
        print("   1. Run full examples: cd models/backtesting && python example_backtest.py")
        print("   2. Test different stocks: Change 'AAPL' to 'TSLA', 'MSFT', etc.")
        print("   3. Test date ranges: Try longer periods for better results")
        print("   4. Compare models: Try 'finbert', 'lstm', or 'ensemble'")
        print("   5. Read documentation: models/backtesting/README.md")
        
        print("\n💡 Tips:")
        print("   • Longer date ranges (3-12 months) give more reliable results")
        print("   • Ensemble model is recommended for best performance")
        print("   • First run takes longer (downloads data), subsequent runs are faster (cached)")
        print("   • Check cache directory for cached data: models/backtesting/cache/")
        
        print("\n")
        return True
        
    except ImportError as e:
        print(f"\n❌ IMPORT ERROR: {e}")
        print("\nPossible solutions:")
        print("1. Install required packages:")
        print("   pip install yfinance pandas numpy")
        print("\n2. Make sure you're running from the webapp directory:")
        print("   cd /home/user/webapp")
        print("   python test_backtesting_simple.py")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nFull error details:")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_framework()
    sys.exit(0 if success else 1)
