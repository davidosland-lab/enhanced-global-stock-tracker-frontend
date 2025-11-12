# 🚀 Trading Platform - Quick Start Guide

## ⚡ Getting Started in 5 Minutes

This guide shows you how to use the trading platform backend right now, even without the UI.

---

## 📋 Prerequisites

```bash
# Already installed if you have FinBERT v4.0
✅ Python 3.8+
✅ yfinance library
✅ All FinBERT dependencies
```

---

## 🎯 Quick Example

Create a file `test_trading.py`:

```python
"""
Quick test of trading platform
"""

from models.trading import (
    PaperTradingEngine,
    OrderManager,
    PositionManager,
    PortfolioManager,
    RiskManager
)

# Initialize trading engine
print("🏦 Initializing trading platform...")
engine = PaperTradingEngine("my_trading.db")

# Initialize managers
order_mgr = OrderManager(engine)
position_mgr = PositionManager(engine)
portfolio_mgr = PortfolioManager(engine)
risk_mgr = RiskManager(engine)

print("✅ Trading platform ready!")
print()

# Reset account to $10,000
print("💰 Resetting account to $10,000...")
engine.db.reset_account(initial_capital=10000)
account = engine.db.get_account()
print(f"   Cash balance: ${account['cash_balance']:,.2f}")
print()

# Example 1: Buy stock with automatic stop-loss
print("📈 Example 1: Buy AAPL with stop-loss")
print("─" * 50)

# Calculate optimal position size
current_price = engine.get_current_price('AAPL')
print(f"   Current price: ${current_price:.2f}")

shares, size_info = risk_mgr.calculate_position_size('AAPL', current_price)
print(f"   Recommended shares: {shares}")
print(f"   Position value: ${size_info['position_value']:,.2f}")
print(f"   Risk amount: ${size_info['risk_amount']:.2f}")

# Execute buy with automatic stop-loss
success, msg, trade_info = order_mgr.quick_buy('AAPL', shares, set_stop_loss=True)
print(f"   {msg}")
print(f"   Total cost: ${trade_info['total_cost']:.2f}")
print()

# Example 2: View portfolio
print("💼 Example 2: Portfolio Summary")
print("─" * 50)

summary = portfolio_mgr.get_portfolio_summary()
account = summary['account']
positions = summary['positions']

print(f"   Total value: ${account['total_value']:,.2f}")
print(f"   Cash: ${account['cash_balance']:,.2f}")
print(f"   Positions: {len(positions)}")

for pos in positions:
    print(f"   • {pos['symbol']}: {pos['quantity']} shares @ ${pos['avg_cost']:.2f}")
    if pos['unrealized_pnl']:
        pnl_sign = "+" if pos['unrealized_pnl'] > 0 else ""
        print(f"     P&L: {pnl_sign}${pos['unrealized_pnl']:.2f} ({pnl_sign}{pos['unrealized_pnl_percent']:.2f}%)")
print()

# Example 3: Set take-profit
print("🎯 Example 3: Set Take-Profit")
print("─" * 50)

success, msg = position_mgr.set_position_take_profit('AAPL', take_profit_percent=0.10)
print(f"   {msg}")
print()

# Example 4: Check risk
print("🛡️ Example 4: Risk Analysis")
print("─" * 50)

risk = risk_mgr.get_portfolio_risk_summary()
print(f"   Risk level: {risk['risk_level']}")
print(f"   Total risk: ${risk['total_portfolio_risk']:.2f}")
print(f"   Positions: {risk['total_positions']}/{risk['max_positions']}")

if risk['warnings']:
    print("   Warnings:")
    for warning in risk['warnings']:
        print(f"   {warning}")
else:
    print("   ✅ No risk violations")
print()

# Example 5: View position details
print("📊 Example 5: Position Details")
print("─" * 50)

position = position_mgr.get_position_details('AAPL')
if position:
    print(f"   Symbol: {position['symbol']}")
    print(f"   Quantity: {position['quantity']} shares")
    print(f"   Avg cost: ${position['avg_cost']:.2f}")
    print(f"   Current price: ${position['current_price']:.2f}")
    print(f"   Market value: ${position['market_value']:.2f}")
    print(f"   Unrealized P&L: ${position['unrealized_pnl']:.2f} ({position['unrealized_pnl_percent']:.2f}%)")
    if position['stop_loss_price']:
        print(f"   Stop-loss: ${position['stop_loss_price']:.2f}")
    if position['take_profit_price']:
        print(f"   Take-profit: ${position['take_profit_price']:.2f}")
print()

# Example 6: Performance metrics
print("📈 Example 6: Performance Metrics")
print("─" * 50)

metrics = portfolio_mgr.get_performance_metrics()
print(f"   Total trades: {metrics['total_trades']}")
print(f"   Win rate: {metrics['win_rate']:.1f}%")
print(f"   Total return: ${metrics['total_return']:.2f} ({metrics['total_return_percent']:.2f}%)")

print()
print("=" * 50)
print("🎉 Trading platform test complete!")
print("=" * 50)
```

---

## 🎬 Run the Example

```bash
# Navigate to FinBERT directory
cd C:\Users\david\AOPT\FinBERT_v4.0_Windows11_ENHANCED

# Activate virtual environment
venv\Scripts\activate

# Run the test
python test_trading.py
```

---

## 📖 Common Operations

### **1. Buy Stock**

```python
from models.trading import PaperTradingEngine, OrderManager

engine = PaperTradingEngine()
order_mgr = OrderManager(engine)

# Quick buy (market order with auto stop-loss)
success, msg, info = order_mgr.quick_buy(
    symbol='AAPL',
    quantity=10,
    set_stop_loss=True,
    stop_loss_percent=0.03  # 3% stop-loss
)

print(msg)
```

### **2. Sell Stock**

```python
# Quick sell (close entire position)
success, msg, info = order_mgr.quick_sell('AAPL')

# Or sell specific quantity
success, msg, info = order_mgr.place_order(
    symbol='AAPL',
    order_type='MARKET',
    side='SELL',
    quantity=5
)
```

### **3. Place Limit Order**

```python
# Buy at specific price
success, msg, info = order_mgr.place_order(
    symbol='AAPL',
    order_type='LIMIT',
    side='BUY',
    quantity=10,
    limit_price=175.00  # Only buy if price <= $175
)

# Order will execute automatically when price condition is met
order_mgr.start_monitoring()  # Start background monitoring
```

### **4. Set Stop-Loss**

```python
from models.trading import PositionManager

position_mgr = PositionManager(engine)

# Set 3% stop-loss
position_mgr.set_position_stop_loss('AAPL', stop_loss_percent=0.03)

# Or set specific price
position_mgr.set_position_stop_loss('AAPL', stop_loss_price=170.00)
```

### **5. View Portfolio**

```python
from models.trading import PortfolioManager

portfolio_mgr = PortfolioManager(engine)

# Get complete summary
summary = portfolio_mgr.get_portfolio_summary()

print(f"Total value: ${summary['account']['total_value']:.2f}")
print(f"Cash: ${summary['account']['cash_balance']:.2f}")
print(f"Positions: {len(summary['positions'])}")
```

### **6. Check Risk**

```python
from models.trading import RiskManager

risk_mgr = RiskManager(engine)

# Get risk summary
risk = risk_mgr.get_portfolio_risk_summary()

print(f"Risk level: {risk['risk_level']}")
print(f"Total risk: ${risk['total_portfolio_risk']:.2f}")
```

### **7. View Performance**

```python
# Get performance metrics
metrics = portfolio_mgr.get_performance_metrics()

print(f"Total return: {metrics['total_return_percent']:.2f}%")
print(f"Win rate: {metrics['win_rate']:.1f}%")
print(f"Sharpe ratio: {metrics['sharpe_ratio']:.2f}")
print(f"Max drawdown: {metrics['max_drawdown']:.2f}%")
```

---

## 🎨 Complete Trading Workflow

```python
"""
Complete trading workflow example
"""

from models.trading import *

# 1. Initialize
engine = PaperTradingEngine("live_trading.db")
order_mgr = OrderManager(engine)
position_mgr = PositionManager(engine)
portfolio_mgr = PortfolioManager(engine)
risk_mgr = RiskManager(engine)

# 2. Start with fresh account
engine.db.reset_account(10000)

# 3. Calculate position size
symbol = 'AAPL'
price = engine.get_current_price(symbol)
shares, info = risk_mgr.calculate_position_size(symbol, price)

print(f"Buying {shares} shares of {symbol}")

# 4. Execute buy
success, msg, trade = order_mgr.quick_buy(symbol, shares, set_stop_loss=True)
print(msg)

# 5. Set take-profit
position_mgr.set_position_take_profit(symbol, take_profit_percent=0.10)

# 6. Monitor (runs in background)
order_mgr.start_monitoring()

# 7. Check status anytime
position = position_mgr.get_position_details(symbol)
print(f"Current P&L: ${position['unrealized_pnl']:.2f}")

# 8. Get portfolio performance
metrics = portfolio_mgr.get_performance_metrics()
print(f"Portfolio return: {metrics['total_return_percent']:.2f}%")

# 9. Close position when ready
success, msg, trade = order_mgr.quick_sell(symbol)
print(msg)
print(f"Trade P&L: ${trade['pnl']:.2f}")

# 10. View final stats
stats = engine.db.get_trade_statistics()
print(f"Total trades: {stats['total_trades']}")
print(f"Win rate: {stats['win_rate']:.1f}%")
```

---

## 📊 Database Location

Your trading data is stored in SQLite database:

```
Default: trading.db (same directory as script)

Custom: PaperTradingEngine("path/to/my_trading.db")
```

**Tables**:
- `trades` - All trade history
- `portfolio` - Current positions
- `orders` - Order history
- `account` - Account balance

---

## ⚙️ Configuration

```python
# Custom commission and slippage
engine = PaperTradingEngine(
    db_path="trading.db",
    commission_rate=0.001,  # 0.1% (default)
    slippage_rate=0.0005    # 0.05% (default)
)

# Custom risk limits
risk_mgr = RiskManager(
    engine,
    max_position_size=0.20,    # 20% max per position
    max_portfolio_risk=0.02,   # 2% max risk per trade
    max_positions=10           # Max 10 positions
)
```

---

## 🐛 Troubleshooting

### **"No price data for symbol"**
**Cause**: Symbol doesn't exist or market closed  
**Solution**: Check symbol spelling, try during market hours

### **"Insufficient buying power"**
**Cause**: Not enough cash in account  
**Solution**: Reset account or close some positions

### **"No position in SYMBOL"**
**Cause**: Trying to sell stock you don't own  
**Solution**: Buy stock first before selling

---

## 📚 Next Steps

1. **Try the examples** - Run test_trading.py
2. **Experiment** - Try different symbols and quantities
3. **Check Phase 3** - UI will be added next
4. **Read documentation** - See TRADING_PLATFORM_DESIGN.md

---

## 🎯 Quick Reference

### **Import All Managers**
```python
from models.trading import (
    PaperTradingEngine,
    OrderManager,
    PositionManager,
    PortfolioManager,
    RiskManager
)
```

### **Initialize Everything**
```python
engine = PaperTradingEngine()
order_mgr = OrderManager(engine)
position_mgr = PositionManager(engine)
portfolio_mgr = PortfolioManager(engine)
risk_mgr = RiskManager(engine)
```

### **Common Commands**
```python
# Buy
order_mgr.quick_buy('AAPL', 10)

# Sell
order_mgr.quick_sell('AAPL')

# Portfolio
portfolio_mgr.get_portfolio_summary()

# Risk
risk_mgr.get_portfolio_risk_summary()

# Performance
portfolio_mgr.get_performance_metrics()
```

---

*Quick Start Guide v1.0*  
*Trading Platform Backend*  
*Ready to Use!*
