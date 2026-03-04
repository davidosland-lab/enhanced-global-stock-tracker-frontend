#!/usr/bin/env python3
"""
Backtest Visualization Charts
==============================

Creates comprehensive trading charts showing:
1. Equity Curve with Entry/Exit Points
2. Individual Trade P&L Chart
3. Cumulative P&L Over Time
4. Win/Loss Distribution

Author: FinBERT v4.4.4
Date: 2026-02-28
Version: v1.3.15.191.1
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import sys

# Set style for professional charts
plt.style.use('seaborn-v0_8-darkgrid')

def load_backtest_data():
    """Load backtest results from CSV files"""
    try:
        trades_df = pd.read_csv('backtest_trades_20260228_074642.csv')
        equity_df = pd.read_csv('backtest_equity_20260228_074642.csv')
        
        # Convert dates to datetime
        trades_df['entry_date'] = pd.to_datetime(trades_df['entry_date'])
        trades_df['exit_date'] = pd.to_datetime(trades_df['exit_date'])
        equity_df['date'] = pd.to_datetime(equity_df['date'], format='mixed')
        
        return trades_df, equity_df
    except FileNotFoundError as e:
        print(f"ERROR: Could not find backtest files: {e}")
        sys.exit(1)


def create_equity_curve_with_trades(trades_df, equity_df):
    """Create equity curve chart with entry/exit markers"""
    fig, ax = plt.subplots(figsize=(16, 9))
    
    # Plot equity curve
    ax.plot(equity_df['date'], equity_df['equity'], 
            linewidth=2.5, color='#2E86AB', label='Portfolio Equity', zorder=1)
    
    # Add entry points (green triangles pointing up)
    entry_dates = trades_df['entry_date']
    entry_values = []
    for date in entry_dates:
        # Find closest equity value
        closest_idx = (equity_df['date'] - date).abs().idxmin()
        entry_values.append(equity_df.loc[closest_idx, 'equity'])
    
    ax.scatter(entry_dates, entry_values, 
              marker='^', s=150, color='#06D6A0', 
              edgecolors='darkgreen', linewidth=1.5,
              label='Entry Points', zorder=3, alpha=0.8)
    
    # Add exit points - color by win/loss
    wins = trades_df[trades_df['result'] == 'WIN']
    losses = trades_df[trades_df['result'] == 'LOSS']
    
    # Winning exits (green circles)
    win_exit_dates = wins['exit_date']
    win_exit_values = []
    for date in win_exit_dates:
        closest_idx = (equity_df['date'] - date).abs().idxmin()
        win_exit_values.append(equity_df.loc[closest_idx, 'equity'])
    
    ax.scatter(win_exit_dates, win_exit_values,
              marker='o', s=150, color='#06D6A0',
              edgecolors='darkgreen', linewidth=1.5,
              label='Winning Exits', zorder=3, alpha=0.8)
    
    # Losing exits (red circles)
    loss_exit_dates = losses['exit_date']
    loss_exit_values = []
    for date in loss_exit_dates:
        closest_idx = (equity_df['date'] - date).abs().idxmin()
        loss_exit_values.append(equity_df.loc[closest_idx, 'equity'])
    
    ax.scatter(loss_exit_dates, loss_exit_values,
              marker='o', s=150, color='#EF476F',
              edgecolors='darkred', linewidth=1.5,
              label='Losing Exits', zorder=3, alpha=0.8)
    
    # Formatting
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Portfolio Value ($)', fontsize=12, fontweight='bold')
    ax.set_title('6-Month Backtest: Equity Curve with Entry/Exit Points\nv1.3.15.191.1',
                fontsize=16, fontweight='bold', pad=20)
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45, ha='right')
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Add legend
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    
    # Add summary stats box
    initial = equity_df['equity'].iloc[0]
    final = equity_df['equity'].iloc[-1]
    pnl = final - initial
    pnl_pct = (pnl / initial) * 100
    
    stats_text = f'Initial: ${initial:,.0f}\nFinal: ${final:,.0f}\nP&L: ${pnl:+,.0f} ({pnl_pct:+.1f}%)'
    ax.text(0.98, 0.02, stats_text,
           transform=ax.transAxes,
           fontsize=11,
           verticalalignment='bottom',
           horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('backtest_equity_curve_with_trades.png', dpi=300, bbox_inches='tight')
    print("✅ Created: backtest_equity_curve_with_trades.png")
    plt.close()


def create_trade_pnl_chart(trades_df):
    """Create chart showing P&L for each trade over time"""
    fig, ax = plt.subplots(figsize=(16, 9))
    
    # Sort trades by exit date
    trades_sorted = trades_df.sort_values('exit_date')
    
    # Create bar chart
    colors = ['#06D6A0' if result == 'WIN' else '#EF476F' 
              for result in trades_sorted['result']]
    
    bars = ax.bar(range(len(trades_sorted)), trades_sorted['pnl'],
                  color=colors, edgecolor='black', linewidth=0.5, alpha=0.8)
    
    # Add stock symbols as labels
    ax.set_xticks(range(len(trades_sorted)))
    ax.set_xticklabels([f"{row['symbol']}\n{row['exit_date'].strftime('%m/%d')}" 
                        for _, row in trades_sorted.iterrows()],
                       rotation=90, fontsize=8)
    
    # Formatting
    ax.set_xlabel('Trade (Symbol & Exit Date)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Profit/Loss ($)', fontsize=12, fontweight='bold')
    ax.set_title('Individual Trade Performance (Chronological Order)\nv1.3.15.191.1',
                fontsize=16, fontweight='bold', pad=20)
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Add zero line
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='y')
    
    # Add summary stats
    total_pnl = trades_sorted['pnl'].sum()
    wins = len(trades_sorted[trades_sorted['result'] == 'WIN'])
    losses = len(trades_sorted[trades_sorted['result'] == 'LOSS'])
    win_rate = wins / len(trades_sorted) * 100
    
    stats_text = (f'Total Trades: {len(trades_sorted)}\n'
                 f'Winners: {wins} | Losers: {losses}\n'
                 f'Win Rate: {win_rate:.1f}%\n'
                 f'Total P&L: ${total_pnl:+,.0f}')
    
    ax.text(0.98, 0.98, stats_text,
           transform=ax.transAxes,
           fontsize=11,
           verticalalignment='top',
           horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('backtest_trade_pnl.png', dpi=300, bbox_inches='tight')
    print("✅ Created: backtest_trade_pnl.png")
    plt.close()


def create_cumulative_pnl_chart(trades_df):
    """Create cumulative P&L chart over time"""
    fig, ax = plt.subplots(figsize=(16, 9))
    
    # Sort trades by exit date
    trades_sorted = trades_df.sort_values('exit_date')
    
    # Calculate cumulative P&L
    trades_sorted['cumulative_pnl'] = trades_sorted['pnl'].cumsum()
    
    # Plot cumulative P&L
    ax.plot(trades_sorted['exit_date'], trades_sorted['cumulative_pnl'],
           linewidth=2.5, color='#2E86AB', marker='o', markersize=6,
           markerfacecolor='white', markeredgewidth=1.5, markeredgecolor='#2E86AB')
    
    # Fill area under curve
    ax.fill_between(trades_sorted['exit_date'], 0, trades_sorted['cumulative_pnl'],
                    alpha=0.3, color='#2E86AB')
    
    # Add markers for wins/losses
    wins = trades_sorted[trades_sorted['result'] == 'WIN']
    losses = trades_sorted[trades_sorted['result'] == 'LOSS']
    
    ax.scatter(wins['exit_date'], wins['cumulative_pnl'],
              s=100, color='#06D6A0', edgecolors='darkgreen', 
              linewidth=1.5, zorder=3, label='After Win')
    
    ax.scatter(losses['exit_date'], losses['cumulative_pnl'],
              s=100, color='#EF476F', edgecolors='darkred',
              linewidth=1.5, zorder=3, label='After Loss')
    
    # Formatting
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cumulative P&L ($)', fontsize=12, fontweight='bold')
    ax.set_title('Cumulative Profit/Loss Over Time\nv1.3.15.191.1',
                fontsize=16, fontweight='bold', pad=20)
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45, ha='right')
    
    # Add zero line
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Add legend
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    
    # Add final P&L annotation
    final_pnl = trades_sorted['cumulative_pnl'].iloc[-1]
    ax.annotate(f'Final P&L: ${final_pnl:+,.0f}',
               xy=(trades_sorted['exit_date'].iloc[-1], final_pnl),
               xytext=(10, 10), textcoords='offset points',
               fontsize=12, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8),
               arrowprops=dict(arrowstyle='->', lw=1.5))
    
    plt.tight_layout()
    plt.savefig('backtest_cumulative_pnl.png', dpi=300, bbox_inches='tight')
    print("✅ Created: backtest_cumulative_pnl.png")
    plt.close()


def create_win_loss_distribution(trades_df):
    """Create win/loss distribution chart"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # Chart 1: Win/Loss Count
    win_loss_counts = trades_df['result'].value_counts()
    colors_pie = ['#06D6A0', '#EF476F']
    
    wedges, texts, autotexts = ax1.pie(win_loss_counts.values,
                                        labels=['Winning Trades', 'Losing Trades'],
                                        colors=colors_pie,
                                        autopct='%1.1f%%',
                                        startangle=90,
                                        explode=(0.05, 0.05),
                                        textprops={'fontsize': 12, 'fontweight': 'bold'})
    
    ax1.set_title('Win/Loss Distribution\n(Trade Count)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Chart 2: P&L Distribution Histogram
    wins = trades_df[trades_df['result'] == 'WIN']['pnl']
    losses = trades_df[trades_df['result'] == 'LOSS']['pnl']
    
    ax2.hist(wins, bins=15, color='#06D6A0', alpha=0.7, 
            edgecolor='darkgreen', linewidth=1.5, label='Wins')
    ax2.hist(losses, bins=15, color='#EF476F', alpha=0.7,
            edgecolor='darkred', linewidth=1.5, label='Losses')
    
    ax2.set_xlabel('P&L per Trade ($)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Number of Trades', fontsize=12, fontweight='bold')
    ax2.set_title('P&L Distribution\n(Amount per Trade)',
                 fontsize=14, fontweight='bold', pad=20)
    
    # Format x-axis as currency
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Add zero line
    ax2.axvline(x=0, color='black', linestyle='-', linewidth=1.5)
    
    # Add legend
    ax2.legend(fontsize=11, framealpha=0.9)
    
    # Add grid
    ax2.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Add stats
    avg_win = wins.mean()
    avg_loss = losses.mean()
    stats_text = (f'Avg Win: ${avg_win:,.0f}\n'
                 f'Avg Loss: ${avg_loss:,.0f}\n'
                 f'Win/Loss Ratio: {abs(avg_win/avg_loss):.2f}')
    
    ax2.text(0.98, 0.98, stats_text,
            transform=ax2.transAxes,
            fontsize=11,
            verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('backtest_win_loss_distribution.png', dpi=300, bbox_inches='tight')
    print("✅ Created: backtest_win_loss_distribution.png")
    plt.close()


def create_pnl_timeline_chart(trades_df):
    """Create P&L chart with dates on X-axis and P&L on Y-axis"""
    fig, ax = plt.subplots(figsize=(18, 10))
    
    # Sort trades by exit date
    trades_sorted = trades_df.sort_values('exit_date')
    
    # Separate wins and losses
    wins = trades_sorted[trades_sorted['result'] == 'WIN']
    losses = trades_sorted[trades_sorted['result'] == 'LOSS']
    
    # Plot winning trades
    ax.scatter(wins['exit_date'], wins['pnl'],
              s=200, marker='o', color='#06D6A0',
              edgecolors='darkgreen', linewidth=2,
              label='Winning Trades', zorder=3, alpha=0.8)
    
    # Plot losing trades
    ax.scatter(losses['exit_date'], losses['pnl'],
              s=200, marker='o', color='#EF476F',
              edgecolors='darkred', linewidth=2,
              label='Losing Trades', zorder=3, alpha=0.8)
    
    # Add connecting line
    ax.plot(trades_sorted['exit_date'], trades_sorted['pnl'],
           linestyle='-', linewidth=1, color='gray', alpha=0.4, zorder=1)
    
    # Add stock labels for significant trades
    for _, row in trades_sorted.iterrows():
        if abs(row['pnl']) > 1000:  # Label trades > $1000 P&L
            ax.annotate(row['symbol'],
                       xy=(row['exit_date'], row['pnl']),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, alpha=0.7)
    
    # Add zero line
    ax.axhline(y=0, color='black', linestyle='-', linewidth=2, zorder=2)
    
    # Formatting
    ax.set_xlabel('Trade Exit Date', fontsize=14, fontweight='bold')
    ax.set_ylabel('Profit/Loss per Trade ($)', fontsize=14, fontweight='bold')
    ax.set_title('Trade Performance Timeline: Entry/Exit Points with P&L\nv1.3.15.191.1',
                fontsize=18, fontweight='bold', pad=20)
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=45, ha='right')
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Add legend
    ax.legend(loc='upper left', fontsize=12, framealpha=0.9)
    
    # Add summary statistics box
    total_trades = len(trades_sorted)
    win_count = len(wins)
    loss_count = len(losses)
    win_rate = (win_count / total_trades) * 100
    avg_win = wins['pnl'].mean()
    avg_loss = losses['pnl'].mean()
    total_pnl = trades_sorted['pnl'].sum()
    
    stats_text = (f'Total Trades: {total_trades}\n'
                 f'Winners: {win_count} ({win_rate:.1f}%)\n'
                 f'Losers: {loss_count} ({100-win_rate:.1f}%)\n'
                 f'Avg Win: ${avg_win:,.0f}\n'
                 f'Avg Loss: ${avg_loss:,.0f}\n'
                 f'Total P&L: ${total_pnl:+,.0f}')
    
    ax.text(0.02, 0.98, stats_text,
           transform=ax.transAxes,
           fontsize=12,
           verticalalignment='top',
           horizontalalignment='left',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    plt.tight_layout()
    plt.savefig('backtest_pnl_timeline.png', dpi=300, bbox_inches='tight')
    print("✅ Created: backtest_pnl_timeline.png")
    plt.close()


def main():
    """Generate all backtest charts"""
    print("\n" + "="*80)
    print("📊 GENERATING BACKTEST VISUALIZATION CHARTS")
    print("="*80)
    
    # Load data
    print("\n📂 Loading backtest data...")
    trades_df, equity_df = load_backtest_data()
    print(f"✅ Loaded {len(trades_df)} trades and {len(equity_df)} equity points")
    
    # Create charts
    print("\n🎨 Creating charts...")
    print("-"*80)
    
    create_pnl_timeline_chart(trades_df)
    create_equity_curve_with_trades(trades_df, equity_df)
    create_trade_pnl_chart(trades_df)
    create_cumulative_pnl_chart(trades_df)
    create_win_loss_distribution(trades_df)
    
    print("-"*80)
    print("\n✅ ALL CHARTS CREATED SUCCESSFULLY!")
    print("\n📁 Generated Files:")
    print("   1. backtest_pnl_timeline.png - Main P&L timeline (REQUESTED)")
    print("   2. backtest_equity_curve_with_trades.png - Equity curve with markers")
    print("   3. backtest_trade_pnl.png - Individual trade performance")
    print("   4. backtest_cumulative_pnl.png - Cumulative P&L growth")
    print("   5. backtest_win_loss_distribution.png - Win/Loss analysis")
    
    print("\n" + "="*80)
    print("✅ CHART GENERATION COMPLETE")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
