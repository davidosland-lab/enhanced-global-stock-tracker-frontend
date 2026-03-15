"""
Manual Paper Trading Platform
=============================

YOU control all trades via simple Python commands.

Usage:
    python manual_paper_trading.py
    
Commands in Python console:
    buy('AAPL', 100)  # Buy 100 shares of AAPL
    sell('AAPL')      # Sell all AAPL shares
    status()          # Show portfolio
    positions()       # Show open positions
"""

from unified_trading_platform import UnifiedTradingPlatform, PaperTradingEngine
import yfinance as yf

class ManualTradingPlatform(UnifiedTradingPlatform):
    """Manual trading - YOU control everything"""
    
    def __init__(self, initial_capital=100000):
        super().__init__(
            initial_capital=initial_capital,
            paper_trading=True
        )
        
        print("\n" + "="*70)
        print("MANUAL PAPER TRADING PLATFORM")
        print("="*70)
        print("\nCommands:")
        print("  buy('SYMBOL', quantity)  - Buy shares")
        print("  sell('SYMBOL')           - Sell all shares")
        print("  status()                 - Show portfolio")
        print("  positions()              - Show open positions")
        print("\nDashboard: http://localhost:5000")
        print("="*70 + "\n")
    
    def buy(self, symbol: str, quantity: int, price: float = None):
        """
        Buy shares
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            quantity: Number of shares
            price: Price (if None, fetches current price)
        """
        try:
            # Get current price if not provided
            if price is None:
                ticker = yf.Ticker(symbol)
                price = ticker.info.get('currentPrice', ticker.info.get('regularMarketPrice', 0))
                if price == 0:
                    print(f"❌ Could not fetch price for {symbol}")
                    return False
            
            # Calculate cost
            total_cost = price * quantity
            
            if total_cost > self.engine.current_capital:
                print(f"❌ Insufficient capital! Need ${total_cost:,.2f}, have ${self.engine.current_capital:,.2f}")
                return False
            
            # Create manual position (bypass normal entry logic)
            from unified_trading_platform import Position
            from datetime import datetime
            
            position = Position(
                symbol=symbol,
                entry_date=datetime.now().isoformat(),
                entry_price=price,
                shares=quantity,
                stop_loss=price * 0.95,  # 5% stop
                take_profit=price * 1.15,  # 15% target
                position_type='manual',
                entry_sentiment=70
            )
            
            self.engine.positions[symbol] = position
            self.engine.current_capital -= total_cost
            
            print(f"✅ Bought {quantity} shares of {symbol} @ ${price:.2f}")
            print(f"   Total cost: ${total_cost:,.2f}")
            print(f"   Remaining cash: ${self.engine.current_capital:,.2f}")
            
            self.add_alert('position_opened', f'Manually opened {symbol} @ ${price:.2f} x {quantity}', symbol, 'success')
            
            return True
            
        except Exception as e:
            print(f"❌ Error buying {symbol}: {e}")
            return False
    
    def sell(self, symbol: str, price: float = None):
        """
        Sell all shares of a symbol
        
        Args:
            symbol: Stock symbol
            price: Exit price (if None, fetches current price)
        """
        try:
            if symbol not in self.engine.positions:
                print(f"❌ No position found for {symbol}")
                return False
            
            # Get current price if not provided
            if price is None:
                ticker = yf.Ticker(symbol)
                price = ticker.info.get('currentPrice', ticker.info.get('regularMarketPrice', 0))
                if price == 0:
                    print(f"❌ Could not fetch price for {symbol}")
                    return False
            
            # Exit position
            trade = self.engine.exit_position(symbol, price, "Manual exit")
            
            if trade:
                print(f"✅ Sold {trade.shares} shares of {symbol} @ ${price:.2f}")
                print(f"   P&L: ${trade.pnl:+,.2f} ({trade.pnl_pct:+.2f}%)")
                print(f"   New cash balance: ${self.engine.current_capital:,.2f}")
                
                self.add_alert('position_closed', f'Manually closed {symbol} | P&L: ${trade.pnl:+,.2f}', symbol, 'success' if trade.pnl > 0 else 'warning')
            
            return True
            
        except Exception as e:
            print(f"❌ Error selling {symbol}: {e}")
            return False
    
    def status(self):
        """Show portfolio status"""
        status = self.engine.get_portfolio_status()
        
        print("\n" + "="*70)
        print("PORTFOLIO STATUS")
        print("="*70)
        print(f"Total Value:    ${status['capital']['total_value']:>15,.2f}")
        print(f"Cash:           ${status['capital']['current_cash']:>15,.2f}")
        print(f"Invested:       ${status['capital']['invested']:>15,.2f}")
        print(f"Total Return:   {status['capital']['total_return_pct']:>15.2f}%")
        print(f"\nOpen Positions: {status['positions']['count']:>15}")
        print(f"Total Trades:   {status['performance']['total_trades']:>15}")
        print(f"Win Rate:       {status['performance']['win_rate']:>15.1f}%")
        print(f"Total P&L:      ${status['performance']['total_realized_pnl']:>15,.2f}")
        print(f"Max Drawdown:   {status['performance']['max_drawdown']:>15.2f}%")
        print("="*70 + "\n")
    
    def positions(self):
        """Show open positions"""
        if not self.engine.positions:
            print("\n❌ No open positions\n")
            return
        
        print("\n" + "="*70)
        print("OPEN POSITIONS")
        print("="*70)
        print(f"{'Symbol':<8} {'Shares':<8} {'Entry $':<12} {'Current $':<12} {'P&L':<12}")
        print("-"*70)
        
        for symbol, pos in self.engine.positions.items():
            try:
                # Fetch current price
                ticker = yf.Ticker(symbol)
                current = ticker.info.get('currentPrice', ticker.info.get('regularMarketPrice', pos.entry_price))
                
                pnl = (current - pos.entry_price) * pos.shares
                pnl_pct = ((current - pos.entry_price) / pos.entry_price) * 100
                
                print(f"{symbol:<8} {pos.shares:<8} ${pos.entry_price:<11.2f} ${current:<11.2f} ${pnl:>+10,.2f} ({pnl_pct:+.2f}%)")
            except:
                print(f"{symbol:<8} {pos.shares:<8} ${pos.entry_price:<11.2f} {'N/A':<12} {'N/A':<12}")
        
        print("="*70 + "\n")
    
    def run(self):
        """Override auto-trading - manual mode only"""
        print("\n✅ Manual trading mode active")
        print("Dashboard running at: http://localhost:5000")
        print("\nUse buy(), sell(), status(), positions() commands")
        print("Press Ctrl+C to exit\n")
        
        try:
            import code
            code.interact(local=locals())
        except KeyboardInterrupt:
            print("\n\nShutting down...")
            self.shutdown()


if __name__ == "__main__":
    # Create platform
    platform = ManualTradingPlatform(initial_capital=100000)
    
    # Make functions available globally
    import __main__
    __main__.buy = platform.buy
    __main__.sell = platform.sell
    __main__.status = platform.status
    __main__.positions = platform.positions
    
    # Start (manual mode)
    platform.run()
