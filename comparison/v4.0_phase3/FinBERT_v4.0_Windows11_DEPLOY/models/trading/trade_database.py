"""
Trading Database Manager
Handles all database operations for the trading platform
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os

logger = logging.getLogger(__name__)


class TradingDatabase:
    """Manages trading database operations"""
    
    def __init__(self, db_path: str = "trading.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                entry_date TEXT NOT NULL,
                exit_date TEXT,
                commission REAL DEFAULT 0,
                slippage REAL DEFAULT 0,
                pnl REAL,
                pnl_percent REAL,
                status TEXT DEFAULT 'OPEN',
                strategy TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Portfolio table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                position_id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                quantity INTEGER NOT NULL,
                avg_cost REAL NOT NULL,
                current_price REAL,
                market_value REAL,
                unrealized_pnl REAL,
                unrealized_pnl_percent REAL,
                stop_loss_price REAL,
                take_profit_price REAL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                order_type TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                limit_price REAL,
                stop_price REAL,
                filled_quantity INTEGER DEFAULT 0,
                avg_fill_price REAL,
                status TEXT DEFAULT 'PENDING',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                filled_at TEXT,
                cancelled_at TEXT
            )
        ''')
        
        # Account table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account (
                account_id INTEGER PRIMARY KEY DEFAULT 1,
                cash_balance REAL NOT NULL DEFAULT 10000,
                portfolio_value REAL DEFAULT 0,
                total_value REAL DEFAULT 10000,
                buying_power REAL DEFAULT 10000,
                initial_capital REAL DEFAULT 10000,
                total_pnl REAL DEFAULT 0,
                total_pnl_percent REAL DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Initialize account if doesn't exist
        cursor.execute('SELECT COUNT(*) FROM account')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO account (account_id, cash_balance, initial_capital, buying_power)
                VALUES (1, 10000, 10000, 10000)
            ''')
        
        conn.commit()
        conn.close()
        logger.info("Trading database initialized")
    
    # ========== ACCOUNT OPERATIONS ==========
    
    def get_account(self) -> Dict:
        """Get account summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM account WHERE account_id = 1')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'account_id': row[0],
                'cash_balance': row[1],
                'portfolio_value': row[2],
                'total_value': row[3],
                'buying_power': row[4],
                'initial_capital': row[5],
                'total_pnl': row[6],
                'total_pnl_percent': row[7],
                'updated_at': row[8]
            }
        return None
    
    def update_account(self, **kwargs):
        """Update account values"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        values = []
        for key, value in kwargs.items():
            updates.append(f"{key} = ?")
            values.append(value)
        
        updates.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(1)  # account_id
        
        query = f"UPDATE account SET {', '.join(updates)} WHERE account_id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()
    
    def reset_account(self, initial_capital: float = 10000):
        """Reset account to initial state"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear all data
        cursor.execute('DELETE FROM trades')
        cursor.execute('DELETE FROM portfolio')
        cursor.execute('DELETE FROM orders')
        
        # Reset account
        cursor.execute('''
            UPDATE account SET
                cash_balance = ?,
                portfolio_value = 0,
                total_value = ?,
                buying_power = ?,
                initial_capital = ?,
                total_pnl = 0,
                total_pnl_percent = 0,
                updated_at = ?
            WHERE account_id = 1
        ''', (initial_capital, initial_capital, initial_capital, initial_capital, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        logger.info(f"Account reset with ${initial_capital} capital")
    
    # ========== TRADE OPERATIONS ==========
    
    def create_trade(self, symbol: str, side: str, quantity: int, entry_price: float,
                    commission: float = 0, slippage: float = 0, strategy: str = None,
                    notes: str = None) -> int:
        """Create new trade"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (symbol, side, quantity, entry_price, entry_date, 
                              commission, slippage, status, strategy, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, ?)
        ''', (symbol, side, quantity, entry_price, datetime.now().isoformat(),
              commission, slippage, strategy, notes))
        
        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Created trade #{trade_id}: {side} {quantity} {symbol} @ ${entry_price}")
        return trade_id
    
    def close_trade(self, trade_id: int, exit_price: float, commission: float = 0,
                   slippage: float = 0):
        """Close trade and calculate P&L"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get trade details
        cursor.execute('SELECT * FROM trades WHERE trade_id = ?', (trade_id,))
        trade = cursor.fetchone()
        
        if trade:
            side = trade[2]
            quantity = trade[3]
            entry_price = trade[4]
            
            # Calculate P&L
            if side == 'BUY':
                pnl = (exit_price - entry_price) * quantity - commission - slippage
            else:  # SELL (short)
                pnl = (entry_price - exit_price) * quantity - commission - slippage
            
            pnl_percent = (pnl / (entry_price * quantity)) * 100 if entry_price * quantity > 0 else 0
            
            # Update trade
            cursor.execute('''
                UPDATE trades SET
                    exit_price = ?,
                    exit_date = ?,
                    pnl = ?,
                    pnl_percent = ?,
                    status = 'CLOSED'
                WHERE trade_id = ?
            ''', (exit_price, datetime.now().isoformat(), pnl, pnl_percent, trade_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Closed trade #{trade_id}: P&L ${pnl:.2f} ({pnl_percent:.2f}%)")
            return pnl, pnl_percent
        
        conn.close()
        return 0, 0
    
    def get_trades(self, status: str = None, symbol: str = None, limit: int = 100) -> List[Dict]:
        """Get trade history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM trades WHERE 1=1'
        params = []
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        if symbol:
            query += ' AND symbol = ?'
            params.append(symbol)
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        trades = []
        for row in rows:
            trades.append({
                'trade_id': row[0],
                'symbol': row[1],
                'side': row[2],
                'quantity': row[3],
                'entry_price': row[4],
                'exit_price': row[5],
                'entry_date': row[6],
                'exit_date': row[7],
                'commission': row[8],
                'slippage': row[9],
                'pnl': row[10],
                'pnl_percent': row[11],
                'status': row[12],
                'strategy': row[13],
                'notes': row[14],
                'created_at': row[15]
            })
        
        return trades
    
    # ========== POSITION OPERATIONS ==========
    
    def upsert_position(self, symbol: str, quantity: int, avg_cost: float,
                       stop_loss: float = None, take_profit: float = None):
        """Create or update position"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM portfolio WHERE symbol = ?', (symbol,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing position
            old_qty = existing[2]
            old_cost = existing[3]
            new_qty = old_qty + quantity
            new_avg_cost = ((old_qty * old_cost) + (quantity * avg_cost)) / new_qty if new_qty > 0 else 0
            
            cursor.execute('''
                UPDATE portfolio SET
                    quantity = ?,
                    avg_cost = ?,
                    stop_loss_price = ?,
                    take_profit_price = ?,
                    updated_at = ?
                WHERE symbol = ?
            ''', (new_qty, new_avg_cost, stop_loss, take_profit, datetime.now().isoformat(), symbol))
        else:
            # Create new position
            cursor.execute('''
                INSERT INTO portfolio (symbol, quantity, avg_cost, stop_loss_price, take_profit_price)
                VALUES (?, ?, ?, ?, ?)
            ''', (symbol, quantity, avg_cost, stop_loss, take_profit))
        
        conn.commit()
        conn.close()
        logger.info(f"Updated position: {symbol} - {quantity} shares @ ${avg_cost}")
    
    def update_position_prices(self, symbol: str, current_price: float):
        """Update current price and P&L for position"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM portfolio WHERE symbol = ?', (symbol,))
        position = cursor.fetchone()
        
        if position:
            quantity = position[2]
            avg_cost = position[3]
            market_value = current_price * quantity
            unrealized_pnl = (current_price - avg_cost) * quantity
            unrealized_pnl_percent = ((current_price - avg_cost) / avg_cost) * 100 if avg_cost > 0 else 0
            
            cursor.execute('''
                UPDATE portfolio SET
                    current_price = ?,
                    market_value = ?,
                    unrealized_pnl = ?,
                    unrealized_pnl_percent = ?,
                    updated_at = ?
                WHERE symbol = ?
            ''', (current_price, market_value, unrealized_pnl, unrealized_pnl_percent,
                  datetime.now().isoformat(), symbol))
            
            conn.commit()
        
        conn.close()
    
    def remove_position(self, symbol: str):
        """Remove position from portfolio"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM portfolio WHERE symbol = ?', (symbol,))
        conn.commit()
        conn.close()
        logger.info(f"Removed position: {symbol}")
    
    def get_positions(self) -> List[Dict]:
        """Get all current positions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM portfolio ORDER BY symbol')
        rows = cursor.fetchall()
        conn.close()
        
        positions = []
        for row in rows:
            positions.append({
                'position_id': row[0],
                'symbol': row[1],
                'quantity': row[2],
                'avg_cost': row[3],
                'current_price': row[4],
                'market_value': row[5],
                'unrealized_pnl': row[6],
                'unrealized_pnl_percent': row[7],
                'stop_loss_price': row[8],
                'take_profit_price': row[9],
                'updated_at': row[10]
            })
        
        return positions
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get specific position"""
        positions = self.get_positions()
        for pos in positions:
            if pos['symbol'] == symbol:
                return pos
        return None
    
    # ========== ORDER OPERATIONS ==========
    
    def create_order(self, symbol: str, order_type: str, side: str, quantity: int,
                    limit_price: float = None, stop_price: float = None) -> int:
        """Create new order"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO orders (symbol, order_type, side, quantity, limit_price, stop_price, status)
            VALUES (?, ?, ?, ?, ?, ?, 'PENDING')
        ''', (symbol, order_type, side, quantity, limit_price, stop_price))
        
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Created order #{order_id}: {side} {quantity} {symbol} ({order_type})")
        return order_id
    
    def update_order_status(self, order_id: int, status: str, filled_qty: int = None,
                           avg_fill_price: float = None):
        """Update order status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = {'status': status}
        if filled_qty is not None:
            updates['filled_quantity'] = filled_qty
        if avg_fill_price is not None:
            updates['avg_fill_price'] = avg_fill_price
        
        if status == 'FILLED':
            updates['filled_at'] = datetime.now().isoformat()
        elif status == 'CANCELLED':
            updates['cancelled_at'] = datetime.now().isoformat()
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [order_id]
        
        cursor.execute(f'UPDATE orders SET {set_clause} WHERE order_id = ?', values)
        conn.commit()
        conn.close()
        
        logger.info(f"Order #{order_id} status: {status}")
    
    def get_orders(self, status: str = None, symbol: str = None) -> List[Dict]:
        """Get orders"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM orders WHERE 1=1'
        params = []
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        if symbol:
            query += ' AND symbol = ?'
            params.append(symbol)
        
        query += ' ORDER BY created_at DESC'
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        orders = []
        for row in rows:
            orders.append({
                'order_id': row[0],
                'symbol': row[1],
                'order_type': row[2],
                'side': row[3],
                'quantity': row[4],
                'limit_price': row[5],
                'stop_price': row[6],
                'filled_quantity': row[7],
                'avg_fill_price': row[8],
                'status': row[9],
                'created_at': row[10],
                'filled_at': row[11],
                'cancelled_at': row[12]
            })
        
        return orders
    
    # ========== STATISTICS ==========
    
    def get_trade_statistics(self) -> Dict:
        """Calculate trading statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get closed trades
        cursor.execute('SELECT pnl, pnl_percent FROM trades WHERE status = "CLOSED"')
        closed_trades = cursor.fetchall()
        conn.close()
        
        if not closed_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_pnl': 0,
                'largest_win': 0,
                'largest_loss': 0,
                'profit_factor': 0
            }
        
        wins = [pnl for pnl, _ in closed_trades if pnl > 0]
        losses = [pnl for pnl, _ in closed_trades if pnl <= 0]
        
        total_pnl = sum([pnl for pnl, _ in closed_trades])
        total_wins = sum(wins) if wins else 0
        total_losses = abs(sum(losses)) if losses else 0
        
        return {
            'total_trades': len(closed_trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': (len(wins) / len(closed_trades)) * 100 if closed_trades else 0,
            'total_pnl': total_pnl,
            'avg_pnl': total_pnl / len(closed_trades) if closed_trades else 0,
            'largest_win': max(wins) if wins else 0,
            'largest_loss': min(losses) if losses else 0,
            'profit_factor': total_wins / total_losses if total_losses > 0 else 0
        }
