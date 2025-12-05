"""
Phase 1 & 2 Implementation Example
==================================

Demonstrates the enhanced backtest engine with:
- Phase 1: Stop-loss orders
- Phase 2: Risk-based position sizing and take-profit orders

This example shows how to use the updated PortfolioBacktestEngine
with risk management features enabled.

Author: FinBERT v4.4.4 Enhanced
Date: December 2025
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backtest_engine import PortfolioBacktestEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def demo_phase1_stop_loss():
    """
    Demonstrate Phase 1: Basic stop-loss implementation
    
    Compares backtest with and without stop-loss protection
    """
    logger.info("=" * 80)
    logger.info("PHASE 1 DEMO: Stop-Loss Protection")
    logger.info("=" * 80)
    
    # Scenario: Stock drops 40% after entry
    initial_capital = 100000.0
    entry_price = 50.0
    shares = 400  # $20,000 position (20% of capital)
    
    # Simulate price drop
    prices = [50.0, 48.0, 46.0, 44.0, 42.0, 40.0, 38.0, 36.0, 34.0, 32.0, 30.0]  # -40% drop
    
    # WITHOUT Stop-Loss
    logger.info("\n--- Without Stop-Loss (Current System) ---")
    no_stop_value = initial_capital - (shares * entry_price)  # Cash after buying
    no_stop_value += shares * prices[-1]  # Final position value
    no_stop_loss = initial_capital - no_stop_value
    no_stop_pct = (no_stop_loss / initial_capital) * 100
    
    logger.info(f"Initial Capital: ${initial_capital:,.2f}")
    logger.info(f"Position: {shares} shares @ ${entry_price:.2f} = ${shares * entry_price:,.2f}")
    logger.info(f"Final Price: ${prices[-1]:.2f} (-40%)")
    logger.info(f"Final Portfolio Value: ${no_stop_value:,.2f}")
    logger.info(f"Loss: ${no_stop_loss:,.2f} ({no_stop_pct:.1f}% of capital)")
    logger.info("❌ CATASTROPHIC LOSS!")
    
    # WITH Stop-Loss (2%)
    logger.info("\n--- With Stop-Loss @ 2% (Phase 1) ---")
    stop_loss_price = entry_price * 0.98  # 2% stop
    
    # Find when stop-loss triggers
    stop_triggered_price = None
    for price in prices:
        if price <= stop_loss_price:
            stop_triggered_price = price
            break
    
    if stop_triggered_price:
        with_stop_value = initial_capital - (shares * entry_price)  # Cash after buying
        with_stop_value += shares * stop_triggered_price  # Exit at stop-loss
        with_stop_loss = initial_capital - with_stop_value
        with_stop_pct = (with_stop_loss / initial_capital) * 100
        
        logger.info(f"Initial Capital: ${initial_capital:,.2f}")
        logger.info(f"Position: {shares} shares @ ${entry_price:.2f} = ${shares * entry_price:,.2f}")
        logger.info(f"Stop-Loss Price: ${stop_loss_price:.2f}")
        logger.info(f"Stop-Loss Triggered @ ${stop_triggered_price:.2f}")
        logger.info(f"Final Portfolio Value: ${with_stop_value:,.2f}")
        logger.info(f"Loss: ${with_stop_loss:,.2f} ({with_stop_pct:.1f}% of capital)")
        logger.info("✅ LOSS CONTROLLED!")
        
        # Calculate improvement
        improvement = ((no_stop_loss - with_stop_loss) / no_stop_loss) * 100
        logger.info(f"\n💡 Improvement: {improvement:.1f}% less damage to account")
    
    logger.info("\n" + "=" * 80)


def demo_phase2_risk_based_sizing():
    """
    Demonstrate Phase 2: Risk-based position sizing + take-profit
    
    Shows how position size adapts to stop-loss distance
    """
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 2 DEMO: Risk-Based Position Sizing")
    logger.info("=" * 80)
    
    initial_capital = 100000.0
    risk_per_trade = 1.0  # 1% risk per trade
    max_risk = initial_capital * (risk_per_trade / 100.0)  # $1,000
    
    logger.info(f"\nInitial Capital: ${initial_capital:,.2f}")
    logger.info(f"Risk Per Trade: {risk_per_trade}% = ${max_risk:,.2f}")
    logger.info("")
    
    # Compare different stop-loss distances
    scenarios = [
        {"stock": "Stock A", "entry": 50.0, "stop_pct": 2.0},  # Tight stop
        {"stock": "Stock B", "entry": 100.0, "stop_pct": 4.0},  # Wide stop
        {"stock": "Stock C", "entry": 25.0, "stop_pct": 1.0},  # Very tight stop
    ]
    
    logger.info("Traditional Allocation (20% of capital):")
    logger.info("-" * 50)
    for scenario in scenarios:
        position_value = initial_capital * 0.20  # 20% allocation
        shares = position_value / scenario['entry']
        stop_price = scenario['entry'] * (1 - scenario['stop_pct'] / 100.0)
        risk = shares * (scenario['entry'] - stop_price)
        
        logger.info(f"{scenario['stock']}: ${position_value:,.0f} position, {shares:.0f} shares")
        logger.info(f"  Entry: ${scenario['entry']:.2f}, Stop: ${stop_price:.2f}")
        logger.info(f"  Risk: ${risk:,.0f} ({risk/initial_capital*100:.2f}% of capital)")
    
    logger.info("\n" + "=" * 50)
    logger.info("Risk-Based Sizing (1% risk per trade):")
    logger.info("-" * 50)
    for scenario in scenarios:
        stop_price = scenario['entry'] * (1 - scenario['stop_pct'] / 100.0)
        risk_per_share = scenario['entry'] - stop_price
        
        # Calculate shares based on fixed risk
        shares = max_risk / risk_per_share
        position_value = shares * scenario['entry']
        
        logger.info(f"{scenario['stock']}: ${position_value:,.0f} position, {shares:.0f} shares")
        logger.info(f"  Entry: ${scenario['entry']:.2f}, Stop: ${stop_price:.2f}")
        logger.info(f"  Risk: ${max_risk:,.0f} ({risk_per_trade}% of capital) ✅")
    
    logger.info("\n💡 Key Insight: Risk-based sizing ensures consistent dollar risk")
    logger.info("   regardless of stop-loss distance or entry price!")
    logger.info("\n" + "=" * 80)


def demo_take_profit():
    """
    Demonstrate Phase 2: Take-profit orders with risk:reward ratios
    """
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 2 DEMO: Take-Profit Orders")
    logger.info("=" * 80)
    
    entry_price = 50.0
    stop_loss_pct = 2.0
    risk_reward_ratio = 2.0
    
    # Calculate levels
    stop_loss_price = entry_price * (1 - stop_loss_pct / 100.0)
    risk_per_share = entry_price - stop_loss_price
    reward_per_share = risk_per_share * risk_reward_ratio
    take_profit_price = entry_price + reward_per_share
    
    logger.info(f"\nEntry Price: ${entry_price:.2f}")
    logger.info(f"Stop-Loss: ${stop_loss_price:.2f} (-{stop_loss_pct}%)")
    logger.info(f"Take-Profit: ${take_profit_price:.2f} (+{(take_profit_price-entry_price)/entry_price*100:.1f}%)")
    logger.info(f"Risk:Reward Ratio: {risk_reward_ratio}:1")
    
    # Show win rate break-even
    logger.info(f"\n💡 With {risk_reward_ratio}:1 R:R, you can be profitable with <50% win rate!")
    
    win_rates = [30, 35, 40, 45, 50]
    logger.info("\nExpectancy Analysis:")
    logger.info("-" * 50)
    logger.info(f"{'Win Rate':<10} {'Avg Win':<12} {'Avg Loss':<12} {'Expectancy':<12} {'Result'}")
    logger.info("-" * 50)
    
    for wr in win_rates:
        avg_win = 200.0 * risk_reward_ratio  # $200 risk × 2 = $400 win
        avg_loss = 200.0
        expectancy = (wr/100.0 * avg_win) - ((1-wr/100.0) * avg_loss)
        result = "✅ Profitable" if expectancy > 0 else "❌ Losing"
        
        logger.info(
            f"{wr}%       ${avg_win:<10.2f}  ${avg_loss:<10.2f}  ${expectancy:<10.2f}  {result}"
        )
    
    logger.info("\n" + "=" * 80)


def demo_portfolio_heat():
    """
    Demonstrate Phase 2: Portfolio heat management
    """
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 2 DEMO: Portfolio Heat Management")
    logger.info("=" * 80)
    
    initial_capital = 100000.0
    risk_per_trade = 1.0  # 1%
    max_portfolio_heat = 6.0  # 6%
    
    max_risk_per_trade = initial_capital * (risk_per_trade / 100.0)
    max_total_risk = initial_capital * (max_portfolio_heat / 100.0)
    
    logger.info(f"\nInitial Capital: ${initial_capital:,.2f}")
    logger.info(f"Risk Per Trade: {risk_per_trade}% = ${max_risk_per_trade:,.2f}")
    logger.info(f"Max Portfolio Heat: {max_portfolio_heat}% = ${max_total_risk:,.2f}")
    logger.info(f"Max Simultaneous Positions: {int(max_portfolio_heat / risk_per_trade)}")
    
    # Simulate opening positions
    logger.info("\n" + "-" * 50)
    logger.info("Opening Positions:")
    logger.info("-" * 50)
    
    current_heat = 0.0
    positions = 0
    
    for i in range(1, 11):
        new_heat = current_heat + max_risk_per_trade
        new_heat_pct = (new_heat / initial_capital) * 100
        
        if new_heat <= max_total_risk:
            current_heat = new_heat
            positions += 1
            logger.info(
                f"Position {positions}: Risk ${max_risk_per_trade:,.0f} | "
                f"Total Heat: ${current_heat:,.0f} ({new_heat_pct:.1f}%) ✅"
            )
        else:
            logger.info(
                f"Position {i}: Risk ${max_risk_per_trade:,.0f} | "
                f"Would exceed limit: ${new_heat:,.0f} ({new_heat_pct:.1f}%) ❌ BLOCKED"
            )
    
    logger.info(f"\n💡 Portfolio heat limit prevents overexposure!")
    logger.info(f"   Maximum {positions} positions at risk simultaneously")
    logger.info("\n" + "=" * 80)


def demo_complete_example():
    """
    Complete example using the enhanced backtest engine
    """
    logger.info("\n" + "=" * 80)
    logger.info("COMPLETE EXAMPLE: Enhanced Backtest Engine")
    logger.info("=" * 80)
    
    # Initialize engine with Phase 1 & 2 features
    logger.info("\n[1] Initializing Enhanced Backtest Engine...")
    
    engine = PortfolioBacktestEngine(
        initial_capital=100000.0,
        allocation_strategy='risk_based',  # Phase 2: Risk-based sizing
        commission_rate=0.001,
        slippage_rate=0.0005,
        # Phase 1: Stop-loss
        enable_stop_loss=True,
        stop_loss_percent=2.0,
        # Phase 2: Take-profit
        enable_take_profit=True,
        risk_reward_ratio=2.0,
        # Phase 2: Risk management
        risk_per_trade_percent=1.0,
        max_portfolio_heat=6.0,
        max_position_size_percent=20.0
    )
    
    logger.info("✅ Engine initialized with risk management enabled")
    
    # Simulate trades
    logger.info("\n[2] Simulating Trading Scenario...")
    
    timestamp = datetime.now()
    
    # BUY signal
    signals = {
        'AAPL': {'prediction': 'BUY', 'confidence': 0.8},
        'TSLA': {'prediction': 'BUY', 'confidence': 0.7},
        'MSFT': {'prediction': 'BUY', 'confidence': 0.9}
    }
    
    prices = {
        'AAPL': 150.0,
        'TSLA': 200.0,
        'MSFT': 300.0
    }
    
    allocations = {
        'AAPL': 0.33,
        'TSLA': 0.33,
        'MSFT': 0.34
    }
    
    # Execute signals
    result = engine.execute_portfolio_signals(
        timestamp=timestamp,
        signals=signals,
        current_prices=prices,
        target_allocations=allocations
    )
    
    logger.info(f"✅ Positions opened: {result['positions']}")
    logger.info(f"   Portfolio value: ${result['portfolio_value']:,.2f}")
    logger.info(f"   Cash remaining: ${result['cash']:,.2f}")
    
    # Show positions with stop-loss and take-profit
    logger.info("\n[3] Active Positions:")
    logger.info("-" * 70)
    for symbol, pos in engine.positions.items():
        logger.info(f"{symbol}:")
        logger.info(f"  Shares: {pos.shares:.2f} @ ${pos.entry_price:.2f}")
        logger.info(f"  Stop-Loss: ${pos.stop_loss_price:.2f} (-{engine.stop_loss_percent}%)")
        logger.info(f"  Take-Profit: ${pos.take_profit_price:.2f} (+{(pos.take_profit_price-pos.entry_price)/pos.entry_price*100:.1f}%)")
        logger.info(f"  Risk: ${pos.risk_amount:,.2f}")
    
    logger.info(f"\nTotal Portfolio Heat: ${engine.current_portfolio_heat:,.2f}")
    
    # Simulate price drops (trigger stop-losses)
    logger.info("\n[4] Simulating Market Drop...")
    
    # AAPL drops below stop-loss
    new_prices = {
        'AAPL': 145.0,  # Triggers stop-loss
        'TSLA': 195.0,  # Triggers stop-loss
        'MSFT': 305.0   # Rises (no trigger)
    }
    
    result = engine.execute_portfolio_signals(
        timestamp=timestamp + timedelta(days=1),
        signals={},  # No new signals
        current_prices=new_prices,
        target_allocations={}
    )
    
    logger.info(f"✅ Stop-losses executed: {engine.stop_loss_exits}")
    logger.info(f"   Active positions: {result['positions']}")
    logger.info(f"   Portfolio value: ${result['portfolio_value']:,.2f}")
    
    # Calculate metrics
    logger.info("\n[5] Performance Metrics:")
    metrics = engine.calculate_portfolio_metrics()
    
    logger.info("-" * 70)
    logger.info(f"Total Return: {metrics['total_return_pct']:.2f}%")
    logger.info(f"Total Trades: {metrics['total_trades']}")
    logger.info(f"Stop-Loss Exits: {metrics['stop_loss_exits']}")
    logger.info(f"Take-Profit Exits: {metrics['take_profit_exits']}")
    logger.info(f"Stop-Loss Rate: {metrics['stop_loss_rate']:.1f}%")
    logger.info(f"Win Rate: {metrics['win_rate']:.1f}%")
    logger.info(f"Expectancy: ${metrics['expectancy']:.2f}/trade")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ Phase 1 & 2 Implementation Complete!")
    logger.info("=" * 80)


def main():
    """Run all Phase 1 & 2 demonstrations"""
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 1 & 2 IMPLEMENTATION DEMONSTRATION")
    logger.info("=" * 80)
    
    # Run all demos
    demo_phase1_stop_loss()
    demo_phase2_risk_based_sizing()
    demo_take_profit()
    demo_portfolio_heat()
    demo_complete_example()
    
    logger.info("\n" + "=" * 80)
    logger.info("ALL DEMONSTRATIONS COMPLETE")
    logger.info("=" * 80)
    logger.info("\n✅ Phase 1: Stop-Loss Protection - IMPLEMENTED")
    logger.info("✅ Phase 2: Risk-Based Sizing + Take-Profit - IMPLEMENTED")
    logger.info("\nNext Steps:")
    logger.info("1. Test on historical data (2023-2024)")
    logger.info("2. Compare metrics with original engine")
    logger.info("3. Tune risk parameters (stop-loss %, risk per trade, etc.)")
    logger.info("4. Deploy to production")
    logger.info("\n" + "=" * 80)


if __name__ == '__main__':
    main()
