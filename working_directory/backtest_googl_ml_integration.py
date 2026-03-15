#!/usr/bin/env python3
"""
ML Integration Historical Backtest - GOOGL
==========================================

Tests ML-enhanced signal generation and decision making using historical GOOGL data.
Evaluates:
- Signal accuracy
- Win rate
- Risk-adjusted returns
- ML vs Technical-only performance
"""

import sys
import os
import json
from datetime import datetime, timedelta
import random

print("=" * 100)
print("🧪 ML INTEGRATION HISTORICAL BACKTEST - GOOGL")
print("=" * 100)
print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# HISTORICAL DATA GENERATION (Simulated realistic GOOGL price action)
# ============================================================================

def generate_historical_googl_data(days=252):
    """
    Generate realistic GOOGL-like historical data
    Based on GOOGL typical characteristics:
    - Price range: $120-$150
    - Average daily volume: 20-30M
    - Volatility: ~1-2% daily moves
    - Trends: Mix of uptrends, downtrends, sideways
    """
    print("📊 Generating Historical GOOGL Data...")
    print(f"   • Period: {days} trading days (~1 year)")
    
    data = []
    base_price = 135.0  # Starting price
    current_price = base_price
    
    # Define market regimes for realistic simulation
    regimes = [
        {'name': 'Bull Trend', 'days': 60, 'drift': 0.003, 'volatility': 0.012},
        {'name': 'Consolidation', 'days': 40, 'drift': 0.0, 'volatility': 0.008},
        {'name': 'Bear Correction', 'days': 30, 'drift': -0.004, 'volatility': 0.018},
        {'name': 'Recovery', 'days': 50, 'drift': 0.002, 'volatility': 0.010},
        {'name': 'Bull Trend 2', 'days': 72, 'drift': 0.0025, 'volatility': 0.011}
    ]
    
    day_counter = 0
    regime_idx = 0
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i)
        
        # Switch regime if needed
        if day_counter >= regimes[regime_idx]['days']:
            regime_idx = (regime_idx + 1) % len(regimes)
            day_counter = 0
        
        regime = regimes[regime_idx]
        
        # Generate price movement based on regime
        daily_return = random.gauss(regime['drift'], regime['volatility'])
        current_price *= (1 + daily_return)
        
        # Add some noise and realistic patterns
        intraday_volatility = random.uniform(0.005, 0.015)
        high = current_price * (1 + intraday_volatility)
        low = current_price * (1 - intraday_volatility)
        open_price = random.uniform(low, high)
        
        # Volume with some variation
        base_volume = random.uniform(20e6, 30e6)
        volume = base_volume * random.uniform(0.7, 1.3)
        
        # Add earnings spike every ~90 days
        if i % 90 == 0 and i > 0:
            volume *= random.uniform(1.5, 2.5)
            current_price *= random.uniform(0.97, 1.05)  # Earnings surprise
        
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(current_price, 2),
            'volume': int(volume),
            'regime': regime['name']
        })
        
        day_counter += 1
    
    print(f"   ✅ Generated {len(data)} days of data")
    print(f"   • Starting price: ${data[0]['close']:.2f}")
    print(f"   • Ending price: ${data[-1]['close']:.2f}")
    print(f"   • Total return: {((data[-1]['close'] / data[0]['close']) - 1) * 100:.2f}%")
    
    return data

# ============================================================================
# TECHNICAL INDICATORS
# ============================================================================

def calculate_technical_indicators(data):
    """Calculate technical indicators for signal generation"""
    print("\n📈 Calculating Technical Indicators...")
    
    for i in range(len(data)):
        # RSI calculation (simplified 14-period)
        if i >= 14:
            gains = []
            losses = []
            for j in range(i-13, i+1):
                change = data[j]['close'] - data[j-1]['close']
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            avg_gain = sum(gains) / 14
            avg_loss = sum(losses) / 14
            
            if avg_loss == 0:
                data[i]['rsi'] = 100
            else:
                rs = avg_gain / avg_loss
                data[i]['rsi'] = 100 - (100 / (1 + rs))
        else:
            data[i]['rsi'] = 50  # Neutral
        
        # Moving Averages
        if i >= 19:
            data[i]['sma20'] = sum(d['close'] for d in data[i-19:i+1]) / 20
        else:
            data[i]['sma20'] = data[i]['close']
        
        if i >= 49:
            data[i]['sma50'] = sum(d['close'] for d in data[i-49:i+1]) / 50
        else:
            data[i]['sma50'] = data[i]['close']
        
        # Price momentum
        if i >= 5:
            data[i]['momentum_5d'] = ((data[i]['close'] / data[i-5]['close']) - 1) * 100
        else:
            data[i]['momentum_5d'] = 0
        
        # Volume trend
        if i >= 20:
            avg_volume = sum(d['volume'] for d in data[i-19:i+1]) / 20
            data[i]['volume_ratio'] = data[i]['volume'] / avg_volume
        else:
            data[i]['volume_ratio'] = 1.0
        
        # ATR (Average True Range) - simplified
        if i >= 14:
            true_ranges = []
            for j in range(i-13, i+1):
                tr = max(
                    data[j]['high'] - data[j]['low'],
                    abs(data[j]['high'] - data[j-1]['close']),
                    abs(data[j]['low'] - data[j-1]['close'])
                )
                true_ranges.append(tr)
            data[i]['atr'] = sum(true_ranges) / 14
        else:
            data[i]['atr'] = data[i]['high'] - data[i]['low']
    
    print(f"   ✅ Calculated RSI, SMA20, SMA50, Momentum, Volume Ratio, ATR")
    return data

# ============================================================================
# SIGNAL GENERATION - TECHNICAL ONLY
# ============================================================================

def generate_technical_signal(data, index):
    """Generate signal using ONLY technical analysis (Phase 3 methodology)"""
    if index < 50:  # Need sufficient history
        return {'signal': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data'}
    
    d = data[index]
    score = 0
    max_score = 100
    reasons = []
    
    # 1. Momentum Analysis (30% weight)
    momentum_score = 0
    if d['rsi'] < 30:
        momentum_score += 30
        reasons.append("RSI oversold (<30)")
    elif d['rsi'] < 40:
        momentum_score += 20
        reasons.append("RSI low (<40)")
    elif d['rsi'] > 70:
        momentum_score -= 20
        reasons.append("RSI overbought (>70)")
    elif 40 <= d['rsi'] <= 60:
        momentum_score += 15
        reasons.append("RSI neutral")
    
    if d['momentum_5d'] > 2:
        momentum_score += 10
        reasons.append("Strong momentum")
    elif d['momentum_5d'] < -2:
        momentum_score -= 10
    
    # 2. Trend Analysis (35% weight)
    trend_score = 0
    if d['close'] > d['sma20'] > d['sma50']:
        trend_score += 35
        reasons.append("Strong uptrend (Price > SMA20 > SMA50)")
    elif d['close'] > d['sma20']:
        trend_score += 20
        reasons.append("Above SMA20")
    elif d['close'] < d['sma20'] < d['sma50']:
        trend_score -= 20
        reasons.append("Downtrend")
    
    # 3. Volume Analysis (20% weight)
    volume_score = 0
    if d['volume_ratio'] > 1.5:
        volume_score += 20
        reasons.append("High volume (1.5x avg)")
    elif d['volume_ratio'] > 1.2:
        volume_score += 10
        reasons.append("Above avg volume")
    elif d['volume_ratio'] < 0.8:
        volume_score -= 10
    
    # 4. Volatility Analysis (15% weight)
    volatility_score = 0
    atr_pct = (d['atr'] / d['close']) * 100
    if atr_pct < 1.5:
        volatility_score += 15
        reasons.append("Low volatility")
    elif atr_pct > 3:
        volatility_score -= 10
        reasons.append("High volatility")
    
    # Calculate total score
    total_score = momentum_score + trend_score + volume_score + volatility_score
    confidence = max(0, min(100, total_score))
    
    # Determine signal
    if confidence >= 60:
        signal = 'BUY'
    elif confidence <= 40:
        signal = 'SELL'
    else:
        signal = 'HOLD'
    
    return {
        'signal': signal,
        'confidence': confidence,
        'reasons': reasons[:3],  # Top 3 reasons
        'components': {
            'momentum': momentum_score,
            'trend': trend_score,
            'volume': volume_score,
            'volatility': volatility_score
        }
    }

# ============================================================================
# SIGNAL GENERATION - ML ENHANCED
# ============================================================================

def generate_ml_enhanced_signal(data, index):
    """Generate signal using ML + Technical analysis (50/50 blend)"""
    if index < 50:
        return {'signal': 'HOLD', 'confidence': 0, 'reason': 'Insufficient data'}
    
    # Get technical signal first
    tech_signal = generate_technical_signal(data, index)
    
    # Simulate ML predictions (based on patterns in data)
    d = data[index]
    
    # ML Model 1: LSTM (pattern recognition)
    lstm_score = 50  # Base
    if index >= 60:
        # Look for recent trend
        recent_trend = (data[index]['close'] - data[index-10]['close']) / data[index-10]['close']
        if recent_trend > 0.03:
            lstm_score += 25
        elif recent_trend < -0.03:
            lstm_score -= 25
        
        # Look for reversal patterns
        if data[index-1]['close'] < data[index-1]['sma20'] and d['close'] > d['sma20']:
            lstm_score += 15  # Bullish crossover
    
    # ML Model 2: Transformer (multi-factor pattern)
    transformer_score = 50
    if d['rsi'] < 35 and d['close'] < d['sma20'] and d['volume_ratio'] > 1.2:
        transformer_score += 20  # Oversold with volume - bullish
    elif d['rsi'] > 65 and d['close'] > d['sma20'] and d['volume_ratio'] > 1.2:
        transformer_score -= 20  # Overbought with volume - bearish
    
    # ML Model 3: Ensemble (XGBoost, LightGBM, etc.)
    ensemble_score = 50
    # Combine multiple factors
    if d['momentum_5d'] > 0 and d['close'] > d['sma20']:
        ensemble_score += 15
    if d['volume_ratio'] > 1.3:
        ensemble_score += 10
    if (d['atr'] / d['close']) < 0.02:  # Low volatility
        ensemble_score += 10
    
    # ML Model 4: GNN (market correlation - simplified)
    gnn_score = 50
    # Simulate market correlation effects
    if index >= 10:
        market_momentum = sum((data[i]['close'] - data[i-1]['close']) for i in range(index-9, index+1))
        if market_momentum > 0:
            gnn_score += 15
        else:
            gnn_score -= 10
    
    # ML Model 5: RL (trading signal optimization)
    rl_score = 50
    # Simulate RL learned behavior
    if tech_signal['confidence'] > 70:
        rl_score += 20  # High confidence signals get boost
    elif tech_signal['confidence'] < 30:
        rl_score -= 20
    
    # ML Model 6: Sentiment (FinBERT/Keyword-based)
    sentiment_score = 50
    # Simulate sentiment based on price action and volume
    if d['volume_ratio'] > 1.5 and d['momentum_5d'] > 2:
        sentiment_score += 20  # Positive sentiment
    elif d['volume_ratio'] > 1.5 and d['momentum_5d'] < -2:
        sentiment_score -= 20  # Negative sentiment
    
    # Average all ML models
    ml_score = (lstm_score + transformer_score + ensemble_score + 
                gnn_score + rl_score + sentiment_score) / 6
    
    # Combine: 50% Technical + 50% ML
    combined_confidence = (tech_signal['confidence'] * 0.5) + (ml_score * 0.5)
    
    # Determine signal
    if combined_confidence >= 60:
        signal = 'BUY'
    elif combined_confidence <= 40:
        signal = 'SELL'
    else:
        signal = 'HOLD'
    
    return {
        'signal': signal,
        'confidence': combined_confidence,
        'tech_confidence': tech_signal['confidence'],
        'ml_confidence': ml_score,
        'ml_models': {
            'lstm': lstm_score,
            'transformer': transformer_score,
            'ensemble': ensemble_score,
            'gnn': gnn_score,
            'rl': rl_score,
            'sentiment': sentiment_score
        },
        'reasons': tech_signal['reasons']
    }

# ============================================================================
# BACKTESTING ENGINE
# ============================================================================

def run_backtest(data, signal_type='ml_enhanced'):
    """Run backtest with given signal type"""
    print(f"\n🔄 Running {signal_type.upper()} Backtest...")
    
    capital = 100000  # Starting capital
    position = None  # Current position
    trades = []
    equity_curve = [capital]
    
    for i in range(50, len(data)):  # Start after warm-up period
        current_price = data[i]['close']
        
        # Generate signal
        if signal_type == 'ml_enhanced':
            signal_data = generate_ml_enhanced_signal(data, i)
        else:
            signal_data = generate_technical_signal(data, i)
        
        signal = signal_data['signal']
        confidence = signal_data['confidence']
        
        # Execute trades
        if position is None and signal == 'BUY' and confidence >= 65:
            # Enter position
            shares = int(capital / current_price)
            if shares > 0:
                position = {
                    'entry_date': data[i]['date'],
                    'entry_price': current_price,
                    'shares': shares,
                    'entry_confidence': confidence,
                    'entry_index': i
                }
        
        elif position is not None:
            # Check exit conditions
            holding_days = i - position['entry_index']
            unrealized_pnl_pct = ((current_price / position['entry_price']) - 1) * 100
            
            should_exit = False
            exit_reason = ""
            
            # Exit on SELL signal with high confidence
            if signal == 'SELL' and confidence <= 35:
                should_exit = True
                exit_reason = "Sell signal"
            
            # Take profit at 15%
            elif unrealized_pnl_pct >= 15:
                should_exit = True
                exit_reason = "Take profit (15%)"
            
            # Stop loss at -5%
            elif unrealized_pnl_pct <= -5:
                should_exit = True
                exit_reason = "Stop loss (-5%)"
            
            # Max holding period 30 days
            elif holding_days >= 30:
                should_exit = True
                exit_reason = "Max holding period"
            
            if should_exit:
                # Exit position
                exit_value = position['shares'] * current_price
                pnl = exit_value - (position['shares'] * position['entry_price'])
                pnl_pct = ((current_price / position['entry_price']) - 1) * 100
                
                capital = exit_value
                
                trades.append({
                    'entry_date': position['entry_date'],
                    'exit_date': data[i]['date'],
                    'entry_price': position['entry_price'],
                    'exit_price': current_price,
                    'shares': position['shares'],
                    'holding_days': holding_days,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'exit_reason': exit_reason,
                    'entry_confidence': position['entry_confidence']
                })
                
                position = None
        
        # Update equity curve
        if position is not None:
            current_equity = position['shares'] * current_price
        else:
            current_equity = capital
        equity_curve.append(current_equity)
    
    # Close any open position at end
    if position is not None:
        exit_price = data[-1]['close']
        exit_value = position['shares'] * exit_price
        pnl = exit_value - (position['shares'] * position['entry_price'])
        pnl_pct = ((exit_price / position['entry_price']) - 1) * 100
        
        trades.append({
            'entry_date': position['entry_date'],
            'exit_date': data[-1]['date'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'shares': position['shares'],
            'holding_days': len(data) - position['entry_index'],
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'exit_reason': 'End of test',
            'entry_confidence': position['entry_confidence']
        })
        
        capital = exit_value
    
    return {
        'trades': trades,
        'final_capital': capital,
        'equity_curve': equity_curve
    }

# ============================================================================
# RESULTS ANALYSIS
# ============================================================================

def analyze_results(results, signal_type):
    """Analyze backtest results"""
    print(f"\n{'=' * 100}")
    print(f"📊 {signal_type.upper().replace('_', ' ')} RESULTS")
    print(f"{'=' * 100}\n")
    
    trades = results['trades']
    
    if len(trades) == 0:
        print("⚠️  No trades executed")
        return
    
    # Calculate metrics
    winning_trades = [t for t in trades if t['pnl'] > 0]
    losing_trades = [t for t in trades if t['pnl'] <= 0]
    
    win_rate = (len(winning_trades) / len(trades)) * 100
    avg_win = sum(t['pnl_pct'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
    avg_loss = sum(t['pnl_pct'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
    
    total_return = ((results['final_capital'] / 100000) - 1) * 100
    
    # Print summary
    print(f"📈 PERFORMANCE SUMMARY:")
    print(f"   • Total Trades: {len(trades)}")
    print(f"   • Winning Trades: {len(winning_trades)} ({win_rate:.1f}%)")
    print(f"   • Losing Trades: {len(losing_trades)} ({100-win_rate:.1f}%)")
    print(f"   • Win Rate: {win_rate:.1f}%")
    print(f"   • Average Win: +{avg_win:.2f}%")
    print(f"   • Average Loss: {avg_loss:.2f}%")
    print(f"   • Total Return: {total_return:.2f}%")
    print(f"   • Final Capital: ${results['final_capital']:,.2f}")
    
    # Calculate risk metrics
    if len(trades) > 1:
        returns = [t['pnl_pct'] for t in trades]
        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5
        sharpe = (avg_return / std_dev) if std_dev > 0 else 0
        
        print(f"\n📉 RISK METRICS:")
        print(f"   • Average Return per Trade: {avg_return:.2f}%")
        print(f"   • Standard Deviation: {std_dev:.2f}%")
        print(f"   • Sharpe Ratio: {sharpe:.2f}")
        print(f"   • Max Win: +{max(t['pnl_pct'] for t in trades):.2f}%")
        print(f"   • Max Loss: {min(t['pnl_pct'] for t in trades):.2f}%")
    
    # Print trade details
    print(f"\n📋 TRADE DETAILS:")
    print(f"{'─' * 100}")
    print(f"{'Entry Date':<12} {'Exit Date':<12} {'Days':<6} {'Entry $':<10} {'Exit $':<10} {'P&L %':<10} {'Reason':<20}")
    print(f"{'─' * 100}")
    
    for i, trade in enumerate(trades[:10]):  # Show first 10 trades
        print(f"{trade['entry_date']:<12} {trade['exit_date']:<12} {trade['holding_days']:<6} "
              f"${trade['entry_price']:<9.2f} ${trade['exit_price']:<9.2f} "
              f"{trade['pnl_pct']:>+8.2f}% {trade['exit_reason']:<20}")
    
    if len(trades) > 10:
        print(f"{'─' * 100}")
        print(f"... and {len(trades) - 10} more trades")
    
    print(f"{'─' * 100}\n")
    
    return {
        'win_rate': win_rate,
        'total_return': total_return,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'num_trades': len(trades)
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    # Generate historical data
    historical_data = generate_historical_googl_data(days=252)
    
    # Calculate technical indicators
    historical_data = calculate_technical_indicators(historical_data)
    
    # Run backtests
    print("\n" + "=" * 100)
    print("🧪 RUNNING BACKTESTS")
    print("=" * 100)
    
    # 1. Technical-only backtest
    tech_results = run_backtest(historical_data, signal_type='technical')
    tech_metrics = analyze_results(tech_results, 'Technical Only')
    
    # 2. ML-enhanced backtest
    ml_results = run_backtest(historical_data, signal_type='ml_enhanced')
    ml_metrics = analyze_results(ml_results, 'ML Enhanced')
    
    # Comparison
    print("\n" + "=" * 100)
    print("🏆 COMPARISON: ML ENHANCED vs TECHNICAL ONLY")
    print("=" * 100)
    print()
    
    comparison = [
        ("Win Rate", f"{tech_metrics['win_rate']:.1f}%", f"{ml_metrics['win_rate']:.1f}%"),
        ("Total Return", f"{tech_metrics['total_return']:.2f}%", f"{ml_metrics['total_return']:.2f}%"),
        ("Avg Win", f"+{tech_metrics['avg_win']:.2f}%", f"+{ml_metrics['avg_win']:.2f}%"),
        ("Avg Loss", f"{tech_metrics['avg_loss']:.2f}%", f"{ml_metrics['avg_loss']:.2f}%"),
        ("Number of Trades", f"{tech_metrics['num_trades']}", f"{ml_metrics['num_trades']}")
    ]
    
    print(f"{'Metric':<20} {'Technical Only':>20} {'ML Enhanced':>20} {'Winner':>15}")
    print(f"{'─' * 80}")
    
    for metric, tech_val, ml_val in comparison:
        # Determine winner
        if metric == "Win Rate":
            winner = "ML Enhanced" if ml_metrics['win_rate'] > tech_metrics['win_rate'] else "Technical"
        elif metric == "Total Return":
            winner = "ML Enhanced" if ml_metrics['total_return'] > tech_metrics['total_return'] else "Technical"
        elif metric == "Avg Win":
            winner = "ML Enhanced" if ml_metrics['avg_win'] > tech_metrics['avg_win'] else "Technical"
        elif metric == "Avg Loss":
            winner = "ML Enhanced" if ml_metrics['avg_loss'] > tech_metrics['avg_loss'] else "Technical"
        else:
            winner = "-"
        
        winner_mark = "🏆" if winner == "ML Enhanced" else "✓" if winner == "Technical" else ""
        print(f"{metric:<20} {tech_val:>20} {ml_val:>20} {winner:>10} {winner_mark}")
    
    print(f"{'─' * 80}\n")
    
    # Calculate improvement
    win_rate_improvement = ml_metrics['win_rate'] - tech_metrics['win_rate']
    return_improvement = ml_metrics['total_return'] - tech_metrics['total_return']
    
    print(f"📈 IMPROVEMENT WITH ML:")
    print(f"   • Win Rate: {win_rate_improvement:+.1f} percentage points")
    print(f"   • Total Return: {return_improvement:+.2f} percentage points")
    
    if win_rate_improvement > 0 and return_improvement > 0:
        print(f"\n🎉 CONCLUSION: ML Enhanced signals outperformed Technical-only signals!")
    elif win_rate_improvement > 0 or return_improvement > 0:
        print(f"\n✅ CONCLUSION: ML Enhanced signals showed improvement in some metrics")
    else:
        print(f"\n⚠️  CONCLUSION: Results are mixed - further tuning may be needed")
    
    print("\n" + "=" * 100)
    print("✅ BACKTEST COMPLETE")
    print("=" * 100)
    print(f"\n📝 Note: This test used simulated GOOGL-like data with realistic price action.")
    print(f"   Real performance may vary. Always validate with live paper trading first.\n")

if __name__ == "__main__":
    main()
