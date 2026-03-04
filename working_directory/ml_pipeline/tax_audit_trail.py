"""
Tax Audit Trail System for Australian Trading
Complies with ATO CGT record-keeping requirements
Author: Phase 3 Trading System
Date: January 1, 2026

ATO Requirements Compliance:
- 5-year record retention period
- Cost base including brokerage fees
- Capital gains/losses calculation
- CGT discount eligibility (12+ months holding)
- FIFO/LIFO/Specific parcel identification
"""

import logging
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
import pandas as pd

logger = logging.getLogger(__name__)

class TransactionType(Enum):
    """Transaction types for tax recording"""
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class TaxEvent:
    """Tax event record for ATO compliance"""
    # Transaction Identification
    transaction_id: str
    transaction_type: str  # 'BUY' or 'SELL'
    
    # Asset Details
    symbol: str
    exchange: str  # ASX, NYSE, LSE
    asset_description: str
    
    # Trade Details
    trade_date: str  # ISO format YYYY-MM-DD
    settlement_date: str  # T+2 for ASX
    quantity: Decimal
    price_per_unit: Decimal
    
    # Cost Base Components (ATO Requirements)
    gross_amount: Decimal  # quantity * price
    brokerage_fee: Decimal  # Must be included in cost base
    exchange_fee: Decimal
    gst_on_fees: Decimal
    total_cost: Decimal  # Including all fees
    
    # Tax Year
    financial_year: str  # e.g., "2025-26"
    
    # Parcel Tracking (for identification method)
    parcel_id: str
    
    # Additional Info
    notes: str = ""
    
    # For SELL transactions (optional fields with defaults)
    cost_base: Optional[Decimal] = None  # Original purchase cost
    capital_proceeds: Optional[Decimal] = None  # Sale proceeds after fees
    capital_gain_loss: Optional[Decimal] = None
    holding_period_days: Optional[int] = None
    cgt_discount_eligible: bool = False  # 50% discount if held >12 months
    acquisition_date: Optional[str] = None  # For sells, link to buy
    

@dataclass
class TaxSummary:
    """Tax summary for a financial year"""
    financial_year: str
    
    # Capital Gains/Losses
    total_capital_gains: Decimal
    total_capital_losses: Decimal
    net_capital_gain_loss: Decimal
    
    # CGT Discount
    total_discountable_gains: Decimal
    cgt_discount_amount: Decimal  # 50% of discountable gains
    net_gain_after_discount: Decimal
    
    # Trade Statistics
    total_trades: int
    buy_trades: int
    sell_trades: int
    
    # By Exchange
    asx_trades: int
    nyse_trades: int
    lse_trades: int
    
    # Holding Periods
    short_term_trades: int  # < 12 months
    long_term_trades: int  # >= 12 months
    
    # Amounts
    total_purchase_value: Decimal
    total_sale_proceeds: Decimal
    total_brokerage_paid: Decimal


class TaxAuditTrail:
    """
    Tax Audit Trail System - ATO Compliant
    
    Maintains comprehensive records for CGT purposes including:
    - Complete transaction history
    - Cost base calculations with fees
    - Capital gains/losses
    - CGT discount eligibility
    - 5-year record retention
    """
    
    # ATO Requirements
    RECORD_RETENTION_YEARS = 5
    CGT_DISCOUNT_HOLDING_DAYS = 365  # 12 months for 50% discount
    SETTLEMENT_DAYS = 2  # T+2 for most exchanges
    
    # Brokerage assumptions (configurable)
    DEFAULT_BROKERAGE_RATE = Decimal('0.0010')  # 0.10%
    MIN_BROKERAGE = Decimal('10.00')
    GST_RATE = Decimal('0.10')  # 10% GST on brokerage
    
    def __init__(self, base_path: str = "tax_records", audit_dir: str = None):
        """Initialize tax audit trail (base_path and audit_dir are synonyms)"""
        # Support both parameter names
        if audit_dir is None:
            audit_dir = base_path
        
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.audit_dir / "transactions").mkdir(exist_ok=True)
        (self.audit_dir / "summaries").mkdir(exist_ok=True)
        (self.audit_dir / "reports").mkdir(exist_ok=True)
        (self.audit_dir / "exports").mkdir(exist_ok=True)
        
        # Parcel tracking for cost base matching
        self.open_parcels = {}  # symbol -> list of parcels
        
        logger.info("[TAX] Tax Audit Trail initialized - ATO compliant")
    
    def record_transaction(
        self,
        symbol: str,
        transaction_type,  # TransactionType enum or str
        quantity: float,
        price: float,
        brokerage: float = 0.0,
        transaction_date: datetime = None
    ) -> TaxEvent:
        """
        Convenience method to record a transaction
        Compatible with paper trading coordinator
        
        Args:
            symbol: Stock symbol
            transaction_type: TransactionType.BUY/SELL or 'BUY'/'SELL'
            quantity: Number of shares
            price: Price per share
            brokerage: Brokerage fee (calculated if 0)
            transaction_date: Transaction datetime
        """
        # Handle TransactionType enum
        if hasattr(transaction_type, 'value'):
            tx_type = transaction_type.value
        else:
            tx_type = str(transaction_type).upper()
        
        if transaction_date is None:
            transaction_date = datetime.now()
        
        # Generate transaction ID
        tx_id = f"TX{datetime.now().strftime('%Y%m%d%H%M%S')}"
        trade_date = transaction_date.strftime('%Y-%m-%d %H:%M:%S')
        
        # Convert to Decimal
        quantity_dec = Decimal(str(quantity))
        price_dec = Decimal(str(price))
        
        if tx_type == 'BUY':
            return self.record_buy_transaction(
                transaction_id=tx_id,
                symbol=symbol,
                trade_date=trade_date,
                quantity=quantity_dec,
                price_per_unit=price_dec,
                notes="Auto-recorded from paper trading"
            )
        elif tx_type == 'SELL':
            return self.record_sell_transaction(
                transaction_id=tx_id,
                symbol=symbol,
                trade_date=trade_date,
                quantity=quantity_dec,
                price_per_unit=price_dec,
                notes="Auto-recorded from paper trading"
            )
        else:
            raise ValueError(f"Invalid transaction type: {tx_type}")
    
    def get_financial_year(self, date_str: str) -> str:
        """
        Get Australian financial year (July 1 - June 30)
        e.g., "2025-26" for dates between 01-Jul-2025 and 30-Jun-2026
        """
        dt = datetime.fromisoformat(date_str)
        if dt.month >= 7:
            return f"{dt.year}-{str(dt.year + 1)[-2:]}"
        else:
            return f"{dt.year - 1}-{str(dt.year)[-2:]}"
    
    def calculate_brokerage(self, trade_value: Decimal) -> Tuple[Decimal, Decimal, Decimal]:
        """
        Calculate brokerage fees including GST
        Returns: (brokerage, gst, total_fee)
        """
        # Calculate brokerage
        brokerage = max(trade_value * self.DEFAULT_BROKERAGE_RATE, self.MIN_BROKERAGE)
        brokerage = brokerage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Calculate GST on brokerage
        gst = (brokerage * self.GST_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Total fee
        total_fee = brokerage + gst
        
        return brokerage, gst, total_fee
    
    def get_exchange_from_symbol(self, symbol: str) -> str:
        """Determine exchange from symbol"""
        symbol_upper = symbol.upper()
        if symbol_upper.endswith('.AX'):
            return 'ASX'
        elif symbol_upper.endswith('.L'):
            return 'LSE'
        else:
            return 'NYSE'
    
    def record_buy_transaction(
        self,
        transaction_id: str,
        symbol: str,
        trade_date: str,
        quantity: Decimal,
        price_per_unit: Decimal,
        notes: str = ""
    ) -> TaxEvent:
        """
        Record a BUY transaction
        Cost base = purchase price + brokerage + fees (ATO requirement)
        """
        # Convert to Decimal
        quantity = Decimal(str(quantity))
        price_per_unit = Decimal(str(price_per_unit))
        
        # Calculate gross amount
        gross_amount = quantity * price_per_unit
        gross_amount = gross_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Calculate fees
        brokerage, gst, total_brokerage = self.calculate_brokerage(gross_amount)
        exchange_fee = Decimal('0.00')  # Simplification
        
        # Total cost (cost base)
        total_cost = gross_amount + total_brokerage + exchange_fee
        
        # Settlement date (T+2)
        trade_dt = datetime.fromisoformat(trade_date)
        settlement_dt = trade_dt + timedelta(days=self.SETTLEMENT_DAYS)
        settlement_date = settlement_dt.strftime('%Y-%m-%d')
        
        # Exchange and financial year
        exchange = self.get_exchange_from_symbol(symbol)
        financial_year = self.get_financial_year(trade_date)
        
        # Create parcel ID
        parcel_id = f"{symbol}_{trade_date}_{transaction_id}"
        
        # Create tax event
        tax_event = TaxEvent(
            transaction_id=transaction_id,
            transaction_type='BUY',
            symbol=symbol,
            exchange=exchange,
            asset_description=f"{symbol} - {exchange} Listed Security",
            trade_date=trade_date,
            settlement_date=settlement_date,
            quantity=quantity,
            price_per_unit=price_per_unit,
            gross_amount=gross_amount,
            brokerage_fee=brokerage,
            exchange_fee=exchange_fee,
            gst_on_fees=gst,
            total_cost=total_cost,
            financial_year=financial_year,
            parcel_id=parcel_id,
            notes=notes
        )
        
        # Store open parcel
        if symbol not in self.open_parcels:
            self.open_parcels[symbol] = []
        
        self.open_parcels[symbol].append({
            'parcel_id': parcel_id,
            'acquisition_date': trade_date,
            'quantity': quantity,
            'cost_base_per_unit': total_cost / quantity,
            'total_cost_base': total_cost
        })
        
        # Save transaction
        self._save_tax_event(tax_event)
        
        logger.info(f"[TAX] BUY recorded: {symbol} x{quantity} @ ${price_per_unit} "
                   f"(Cost base: ${total_cost})")
        
        return tax_event
    
    def record_sell_transaction(
        self,
        transaction_id: str,
        symbol: str,
        trade_date: str,
        quantity: Decimal,
        price_per_unit: Decimal,
        method: str = 'FIFO',
        notes: str = ""
    ) -> TaxEvent:
        """
        Record a SELL transaction with CGT calculation
        
        Methods:
        - FIFO: First In First Out (default, ATO acceptable)
        - LIFO: Last In First Out (ATO acceptable)
        - SPECIFIC: Specific parcel identification (requires parcel_id)
        """
        # Convert to Decimal
        quantity = Decimal(str(quantity))
        price_per_unit = Decimal(str(price_per_unit))
        
        # Calculate gross proceeds
        gross_amount = quantity * price_per_unit
        gross_amount = gross_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Calculate fees (reduce proceeds)
        brokerage, gst, total_brokerage = self.calculate_brokerage(gross_amount)
        exchange_fee = Decimal('0.00')
        
        # Capital proceeds (sale price minus costs)
        capital_proceeds = gross_amount - total_brokerage - exchange_fee
        
        # Settlement date
        trade_dt = datetime.fromisoformat(trade_date)
        settlement_dt = trade_dt + timedelta(days=self.SETTLEMENT_DAYS)
        settlement_date = settlement_dt.strftime('%Y-%m-%d')
        
        # Exchange and financial year
        exchange = self.get_exchange_from_symbol(symbol)
        financial_year = self.get_financial_year(trade_date)
        
        # Match with acquisition parcels to calculate cost base
        cost_base, acquisition_date, holding_days = self._match_parcel(
            symbol, quantity, trade_date, method
        )
        
        # Calculate capital gain/loss
        capital_gain_loss = capital_proceeds - cost_base
        
        # Check CGT discount eligibility (held > 12 months)
        cgt_discount_eligible = holding_days >= self.CGT_DISCOUNT_HOLDING_DAYS
        
        # Create parcel ID
        parcel_id = f"{symbol}_{trade_date}_{transaction_id}"
        
        # Create tax event
        tax_event = TaxEvent(
            transaction_id=transaction_id,
            transaction_type='SELL',
            symbol=symbol,
            exchange=exchange,
            asset_description=f"{symbol} - {exchange} Listed Security",
            trade_date=trade_date,
            settlement_date=settlement_date,
            quantity=quantity,
            price_per_unit=price_per_unit,
            gross_amount=gross_amount,
            brokerage_fee=brokerage,
            exchange_fee=exchange_fee,
            gst_on_fees=gst,
            total_cost=capital_proceeds,  # For sells, this is proceeds after fees
            cost_base=cost_base,
            capital_proceeds=capital_proceeds,
            capital_gain_loss=capital_gain_loss,
            holding_period_days=holding_days,
            cgt_discount_eligible=cgt_discount_eligible,
            financial_year=financial_year,
            parcel_id=parcel_id,
            acquisition_date=acquisition_date,
            notes=notes
        )
        
        # Save transaction
        self._save_tax_event(tax_event)
        
        # Log
        gain_loss_str = "GAIN" if capital_gain_loss >= 0 else "LOSS"
        discount_str = " (CGT discount eligible)" if cgt_discount_eligible else ""
        logger.info(f"[TAX] SELL recorded: {symbol} x{quantity} @ ${price_per_unit} "
                   f"-> ${capital_gain_loss:+,.2f} {gain_loss_str}{discount_str}")
        
        return tax_event
    
    def _match_parcel(
        self,
        symbol: str,
        quantity: Decimal,
        sell_date: str,
        method: str = 'FIFO'
    ) -> Tuple[Decimal, str, int]:
        """
        Match sell with buy parcels to determine cost base
        Returns: (cost_base, acquisition_date, holding_days)
        """
        if symbol not in self.open_parcels or not self.open_parcels[symbol]:
            # No matching parcels - shouldn't happen
            logger.warning(f"[TAX] No open parcels for {symbol} - using zero cost base")
            return Decimal('0.00'), sell_date, 0
        
        parcels = self.open_parcels[symbol]
        
        # Sort parcels based on method
        if method == 'FIFO':
            parcels.sort(key=lambda p: p['acquisition_date'])
        elif method == 'LIFO':
            parcels.sort(key=lambda p: p['acquisition_date'], reverse=True)
        
        # Match quantity with parcels
        remaining_qty = quantity
        total_cost_base = Decimal('0.00')
        acquisition_date = parcels[0]['acquisition_date']  # Use first matched parcel
        
        parcels_to_remove = []
        
        for i, parcel in enumerate(parcels):
            if remaining_qty <= 0:
                break
            
            parcel_qty = parcel['quantity']
            
            if parcel_qty <= remaining_qty:
                # Use entire parcel
                total_cost_base += parcel['total_cost_base']
                remaining_qty -= parcel_qty
                parcels_to_remove.append(i)
            else:
                # Use partial parcel
                used_qty = remaining_qty
                cost_per_unit = parcel['cost_base_per_unit']
                total_cost_base += used_qty * cost_per_unit
                
                # Update parcel
                parcels[i]['quantity'] = parcel_qty - used_qty
                parcels[i]['total_cost_base'] = (parcel_qty - used_qty) * cost_per_unit
                
                remaining_qty = Decimal('0.00')
        
        # Remove fully used parcels
        for idx in reversed(parcels_to_remove):
            parcels.pop(idx)
        
        # Calculate holding period
        acq_date = datetime.fromisoformat(acquisition_date)
        sell_dt = datetime.fromisoformat(sell_date)
        holding_days = (sell_dt - acq_date).days
        
        return total_cost_base.quantize(Decimal('0.01')), acquisition_date, holding_days
    
    def _save_tax_event(self, tax_event: TaxEvent):
        """Save tax event to file"""
        fy_dir = self.audit_dir / "transactions" / tax_event.financial_year
        fy_dir.mkdir(exist_ok=True)
        
        filename = fy_dir / f"{tax_event.transaction_id}.json"
        
        with open(filename, 'w') as f:
            json.dump(asdict(tax_event), f, indent=2, default=str)
    
    def generate_tax_summary(self, financial_year: str) -> TaxSummary:
        """
        Generate tax summary for a financial year
        Complies with ATO CGT reporting requirements
        """
        transactions = self._load_transactions_for_year(financial_year)
        
        total_capital_gains = Decimal('0.00')
        total_capital_losses = Decimal('0.00')
        total_discountable_gains = Decimal('0.00')
        
        total_trades = len(transactions)
        buy_trades = 0
        sell_trades = 0
        
        asx_trades = 0
        nyse_trades = 0
        lse_trades = 0
        
        short_term_trades = 0
        long_term_trades = 0
        
        total_purchase_value = Decimal('0.00')
        total_sale_proceeds = Decimal('0.00')
        total_brokerage_paid = Decimal('0.00')
        
        for tx in transactions:
            # Count trades
            if tx.transaction_type == 'BUY':
                buy_trades += 1
                total_purchase_value += tx.total_cost
            elif tx.transaction_type == 'SELL':
                sell_trades += 1
                total_sale_proceeds += tx.capital_proceeds or Decimal('0.00')
                
                # Capital gains/losses
                if tx.capital_gain_loss:
                    if tx.capital_gain_loss > 0:
                        total_capital_gains += tx.capital_gain_loss
                        if tx.cgt_discount_eligible:
                            total_discountable_gains += tx.capital_gain_loss
                    else:
                        total_capital_losses += abs(tx.capital_gain_loss)
                
                # Holding period
                if tx.holding_period_days:
                    if tx.holding_period_days >= self.CGT_DISCOUNT_HOLDING_DAYS:
                        long_term_trades += 1
                    else:
                        short_term_trades += 1
            
            # Exchange counts
            if tx.exchange == 'ASX':
                asx_trades += 1
            elif tx.exchange == 'NYSE':
                nyse_trades += 1
            elif tx.exchange == 'LSE':
                lse_trades += 1
            
            # Brokerage
            total_brokerage_paid += tx.brokerage_fee + tx.gst_on_fees
        
        # Calculate net position
        net_capital_gain_loss = total_capital_gains - total_capital_losses
        
        # Apply CGT discount (50% for assets held > 12 months)
        cgt_discount_amount = total_discountable_gains * Decimal('0.50')
        net_gain_after_discount = net_capital_gain_loss - cgt_discount_amount
        
        summary = TaxSummary(
            financial_year=financial_year,
            total_capital_gains=total_capital_gains,
            total_capital_losses=total_capital_losses,
            net_capital_gain_loss=net_capital_gain_loss,
            total_discountable_gains=total_discountable_gains,
            cgt_discount_amount=cgt_discount_amount,
            net_gain_after_discount=net_gain_after_discount,
            total_trades=total_trades,
            buy_trades=buy_trades,
            sell_trades=sell_trades,
            asx_trades=asx_trades,
            nyse_trades=nyse_trades,
            lse_trades=lse_trades,
            short_term_trades=short_term_trades,
            long_term_trades=long_term_trades,
            total_purchase_value=total_purchase_value,
            total_sale_proceeds=total_sale_proceeds,
            total_brokerage_paid=total_brokerage_paid
        )
        
        # Save summary
        summary_file = self.audit_dir / "summaries" / f"{financial_year}_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(asdict(summary), f, indent=2, default=str)
        
        return summary
    
    def get_financial_year_summary(self, financial_year: str = None) -> Dict:
        """
        Get financial year tax summary as dictionary
        Convenience method for dashboard/API use
        
        Args:
            financial_year: Financial year (e.g., '2026-27'), defaults to current
        
        Returns:
            Dictionary with tax summary
        """
        if financial_year is None:
            financial_year = self.get_financial_year(datetime.now().strftime('%Y-%m-%d'))
        
        summary = self.generate_tax_summary(financial_year)
        
        return {
            'financial_year': summary.financial_year,
            'net_capital_gain': float(summary.net_capital_gain_loss),
            'cgt_discount': float(summary.cgt_discount_amount),
            'net_after_discount': float(summary.net_gain_after_discount),
            'trading_activity': {
                'total_transactions': summary.total_trades,
                'buy_transactions': summary.buy_trades,
                'sell_transactions': summary.sell_trades,
                'short_term': summary.short_term_trades,
                'long_term': summary.long_term_trades
            },
            'exchange_breakdown': {
                'ASX': summary.asx_trades,
                'NYSE': summary.nyse_trades,
                'LSE': summary.lse_trades
            },
            'financial_totals': {
                'total_purchases': float(summary.total_purchase_value),
                'total_sales': float(summary.total_sale_proceeds),
                'total_brokerage': float(summary.total_brokerage_paid)
            }
        }
    
    def _load_transactions_for_year(self, financial_year: str) -> List[TaxEvent]:
        """Load all transactions for a financial year"""
        fy_dir = self.audit_dir / "transactions" / financial_year
        
        if not fy_dir.exists():
            return []
        
        transactions = []
        for file in fy_dir.glob("*.json"):
            with open(file, 'r') as f:
                data = json.load(f)
                # Convert strings back to Decimal
                for key in ['quantity', 'price_per_unit', 'gross_amount', 'brokerage_fee',
                           'exchange_fee', 'gst_on_fees', 'total_cost', 'cost_base',
                           'capital_proceeds', 'capital_gain_loss']:
                    if key in data and data[key] is not None:
                        data[key] = Decimal(str(data[key]))
                
                tax_event = TaxEvent(**data)
                transactions.append(tax_event)
        
        # Sort by trade date
        transactions.sort(key=lambda tx: tx.trade_date)
        
        return transactions
    
    def export_to_csv(self, financial_year: str) -> str:
        """Export transactions to CSV for accountant/ATO"""
        transactions = self._load_transactions_for_year(financial_year)
        
        csv_file = self.audit_dir / "exports" / f"{financial_year}_transactions.csv"
        
        with open(csv_file, 'w', newline='') as f:
            if transactions:
                # Use first transaction to get field names
                fieldnames = list(asdict(transactions[0]).keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for tx in transactions:
                    writer.writerow(asdict(tx))
        
        logger.info(f"[TAX] Exported {len(transactions)} transactions to {csv_file}")
        return str(csv_file)
    
    def export_transactions(self, financial_year: str = None, format: str = 'csv') -> str:
        """
        Export transactions for a financial year
        
        Args:
            financial_year: Financial year (e.g., '2026-27'), defaults to current
            format: Export format ('csv' or 'json')
        
        Returns:
            Path to exported file
        """
        if financial_year is None:
            financial_year = self.get_financial_year(datetime.now().strftime('%Y-%m-%d'))
        
        if format.lower() == 'csv':
            return self.export_to_csv(financial_year)
        elif format.lower() == 'json':
            # Export as JSON
            transactions = self._load_transactions_for_year(financial_year)
            json_file = self.audit_dir / "exports" / f"{financial_year}_transactions.json"
            
            with open(json_file, 'w') as f:
                json.dump([asdict(tx) for tx in transactions], f, indent=2, default=str)
            
            logger.info(f"[TAX] Exported {len(transactions)} transactions to {json_file}")
            return str(json_file)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def generate_ato_report(self, financial_year: str = None) -> str:
        """
        Generate ATO-ready Capital Gains Tax report
        
        Args:
            financial_year: Financial year (e.g., '2026-27'), defaults to current
        """
        if financial_year is None:
            financial_year = self.get_financial_year(datetime.now().strftime('%Y-%m-%d'))
        
        summary = self.generate_tax_summary(financial_year)
        transactions = self._load_transactions_for_year(financial_year)
        
        report_file = self.audit_dir / "reports" / f"{financial_year}_ATO_Report.txt"
        
        with open(report_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write(f"CAPITAL GAINS TAX REPORT - FINANCIAL YEAR {financial_year}\n")
            f.write("Australian Taxation Office (ATO) Compliant\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Financial Year: {financial_year} (1 July - 30 June)\n\n")
            
            f.write("SUMMARY OF CAPITAL GAINS AND LOSSES\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total Capital Gains:              ${summary.total_capital_gains:>15,.2f}\n")
            f.write(f"Total Capital Losses:             ${summary.total_capital_losses:>15,.2f}\n")
            f.write(f"Net Capital Gain/(Loss):          ${summary.net_capital_gain_loss:>15,.2f}\n\n")
            
            f.write("CGT DISCOUNT (50% for assets held > 12 months)\n")
            f.write("-" * 80 + "\n")
            f.write(f"Gains Eligible for Discount:      ${summary.total_discountable_gains:>15,.2f}\n")
            f.write(f"CGT Discount Amount (50%):        ${summary.cgt_discount_amount:>15,.2f}\n")
            f.write(f"Net Gain After Discount:          ${summary.net_gain_after_discount:>15,.2f}\n\n")
            
            f.write("TRADING ACTIVITY\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total Transactions:               {summary.total_trades:>15}\n")
            f.write(f"  - Buy Transactions:             {summary.buy_trades:>15}\n")
            f.write(f"  - Sell Transactions:            {summary.sell_trades:>15}\n\n")
            
            f.write(f"Short Term Trades (< 12 months):  {summary.short_term_trades:>15}\n")
            f.write(f"Long Term Trades (>= 12 months):  {summary.long_term_trades:>15}\n\n")
            
            f.write("EXCHANGE BREAKDOWN\n")
            f.write("-" * 80 + "\n")
            f.write(f"ASX Trades:                       {summary.asx_trades:>15}\n")
            f.write(f"NYSE Trades:                      {summary.nyse_trades:>15}\n")
            f.write(f"LSE Trades:                       {summary.lse_trades:>15}\n\n")
            
            f.write("FINANCIAL TOTALS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total Purchase Value:             ${summary.total_purchase_value:>15,.2f}\n")
            f.write(f"Total Sale Proceeds:              ${summary.total_sale_proceeds:>15,.2f}\n")
            f.write(f"Total Brokerage Paid:             ${summary.total_brokerage_paid:>15,.2f}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("DETAILED TRANSACTION LIST\n")
            f.write("=" * 80 + "\n\n")
            
            # Sell transactions only (for CGT)
            sell_transactions = [tx for tx in transactions if tx.transaction_type == 'SELL']
            
            for tx in sell_transactions:
                f.write(f"Transaction ID: {tx.transaction_id}\n")
                f.write(f"Symbol: {tx.symbol} ({tx.exchange})\n")
                f.write(f"Sale Date: {tx.trade_date}\n")
                f.write(f"Acquisition Date: {tx.acquisition_date}\n")
                f.write(f"Holding Period: {tx.holding_period_days} days\n")
                f.write(f"Quantity: {tx.quantity}\n")
                f.write(f"Sale Price per Unit: ${tx.price_per_unit:.2f}\n")
                f.write(f"Capital Proceeds: ${tx.capital_proceeds:.2f}\n")
                f.write(f"Cost Base: ${tx.cost_base:.2f}\n")
                f.write(f"Capital Gain/(Loss): ${tx.capital_gain_loss:+,.2f}\n")
                f.write(f"CGT Discount Eligible: {'YES' if tx.cgt_discount_eligible else 'NO'}\n")
                f.write("-" * 80 + "\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("NOTES FOR ATO LODGEMENT\n")
            f.write("=" * 80 + "\n\n")
            f.write("1. Include Net Capital Gain After Discount in your tax return\n")
            f.write("2. Attach this report as supporting documentation\n")
            f.write("3. Records retained for 5 years as per ATO requirements\n")
            f.write("4. Cost base includes purchase price + brokerage + GST\n")
            f.write("5. Capital proceeds = sale price - brokerage - GST\n")
            f.write("6. CGT discount applies to assets held for 12+ months\n\n")
            
            f.write("This report has been generated by Phase 3 Trading System\n")
            f.write("and complies with ATO record-keeping requirements.\n\n")
        
        logger.info(f"[TAX] Generated ATO report: {report_file}")
        return str(report_file)


def test_tax_audit():
    """Test tax audit trail"""
    print("\n" + "="*80)
    print("TAX AUDIT TRAIL TEST")
    print("="*80 + "\n")
    
    audit = TaxAuditTrail("test_tax_records")
    
    # Test buy
    print("Recording BUY transaction...")
    buy_event = audit.record_buy_transaction(
        transaction_id="TX001",
        symbol="CBA.AX",
        trade_date="2025-08-15",
        quantity=Decimal('100'),
        price_per_unit=Decimal('125.50'),
        notes="Initial purchase"
    )
    print(f"  Cost Base: ${buy_event.total_cost:.2f}")
    print(f"  Brokerage: ${buy_event.brokerage_fee:.2f}")
    print(f"  GST: ${buy_event.gst_on_fees:.2f}")
    print()
    
    # Test sell (after 12 months - CGT discount eligible)
    print("Recording SELL transaction (14 months later)...")
    sell_event = audit.record_sell_transaction(
        transaction_id="TX002",
        symbol="CBA.AX",
        trade_date="2026-10-20",
        quantity=Decimal('100'),
        price_per_unit=Decimal('145.75'),
        method='FIFO',
        notes="Take profit"
    )
    print(f"  Capital Proceeds: ${sell_event.capital_proceeds:.2f}")
    print(f"  Cost Base: ${sell_event.cost_base:.2f}")
    print(f"  Capital Gain: ${sell_event.capital_gain_loss:+,.2f}")
    print(f"  Holding Period: {sell_event.holding_period_days} days")
    print(f"  CGT Discount Eligible: {sell_event.cgt_discount_eligible}")
    print()
    
    # Generate summary
    print("Generating tax summary for FY 2026-27...")
    summary = audit.generate_tax_summary("2026-27")
    print(f"  Net Capital Gain: ${summary.net_capital_gain_loss:,.2f}")
    print(f"  CGT Discount: ${summary.cgt_discount_amount:,.2f}")
    print(f"  Net After Discount: ${summary.net_gain_after_discount:,.2f}")
    print()
    
    # Export
    csv_file = audit.export_to_csv("2026-27")
    print(f"Exported to: {csv_file}")
    
    # Generate ATO report
    report_file = audit.generate_ato_report("2026-27")
    print(f"ATO Report: {report_file}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    test_tax_audit()
