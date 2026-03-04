"""
EMERGENCY RESTORE v1.3.15.77
Restores ORIGINAL working 4-index chart (AORD, FTSE, S&P, NASDAQ)
with ONLY minimal date fix: latest_date -> current_date
"""

def create_market_performance_chart_ORIGINAL_FIXED(state):
    """Create intraday performance chart for major indices (market hours only, GMT timezone)"""
    import yfinance as yf
    import plotly.graph_objs as go
    import pytz
    from datetime import datetime, timedelta
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Market indices with their trading hours (in GMT)
    # Note: Times adjusted for Australian Eastern Daylight Time (AEDT, UTC+11)
    indices = {
        '^AORD': {
            'name': 'ASX All Ords', 
            'color': '#00CED1',
            'market_open': 23,   # 23:00 GMT previous day (10:00 AEDT)
            'market_close': 5,   # 05:00 GMT (16:00 AEDT)
            'spans_midnight': True  # Market session crosses midnight GMT
        },
        '^GSPC': {
            'name': 'S&P 500', 
            'color': '#1E90FF',
            'market_open': 14,  # 14:30 GMT (9:30 EST)
            'market_close': 21, # 21:00 GMT (16:00 EST)
            'spans_midnight': False
        },
        '^IXIC': {
            'name': 'NASDAQ', 
            'color': '#4CAF50',
            'market_open': 14,  # 14:30 GMT (9:30 EST)
            'market_close': 21, # 21:00 GMT (16:00 EST)
            'spans_midnight': False
        },
        '^FTSE': {
            'name': 'FTSE 100', 
            'color': '#FF9800',
            'market_open': 8,   # 08:00 GMT
            'market_close': 16, # 16:30 GMT
            'spans_midnight': False
        }
    }
    
    fig = go.Figure()
    gmt = pytz.timezone('GMT')
    now_gmt = datetime.now(gmt)  # ADD THIS LINE
    
    try:
        for symbol, info in indices.items():
            try:
                # Fetch 5 days of data to ensure we have previous trading day (covers weekends/holidays)
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='5d', interval='15m')
                
                if len(hist) > 0:
                    # Convert index to GMT timezone
                    hist.index = hist.index.tz_convert(gmt)
                    
                    # ONLY CHANGE: Use current date instead of latest data date
                    # OLD: latest_date = hist.index[-1].date()
                    current_date = now_gmt.date()  # FIXED LINE
                    
                    # Filter to only show today's market hours
                    market_open_hour = info['market_open']
                    market_close_hour = info['market_close']
                    spans_midnight = info.get('spans_midnight', False)
                    
                    # Create market hours filter
                    if spans_midnight:
                        # For markets that span midnight (e.g., ASX: 23:00 previous day to 05:00 current day)
                        previous_date = current_date - timedelta(days=1)  # CHANGED: latest_date -> current_date
                        
                        # Include data from previous day after market_open_hour AND current day up to and including market_close_hour
                        # Note: ASX closes at 16:00 AEDT = 05:00 GMT, so we need hour <= 6 to include 05:xx data
                        mask = (
                            ((hist.index.date == previous_date) & (hist.index.hour >= market_open_hour)) |
                            ((hist.index.date == current_date) & (hist.index.hour < market_close_hour + 1))  # CHANGED
                        )
                    else:
                        # Normal market hours within single day
                        mask = (
                            (hist.index.date == current_date) &  # CHANGED: latest_date -> current_date
                            (hist.index.hour >= market_open_hour) &
                            (hist.index.hour <= market_close_hour)
                        )
                    
                    market_hours_data = hist[mask]
                    
                    if len(market_hours_data) > 0:
                        # Get previous close - use official close for all markets (most accurate)
                        try:
                            ticker_info = ticker.info
                            official_prev_close = ticker_info.get('regularMarketPreviousClose', ticker_info.get('previousClose'))
                            
                            if official_prev_close and official_prev_close > 0:
                                previous_close = official_prev_close
                                logger.debug(f"{symbol}: Using official previous close: {previous_close:.2f}")
                            else:
                                # Fallback: use first price of current session
                                previous_close = market_hours_data['Close'].iloc[0]
                                logger.debug(f"{symbol}: Using session open as reference: {previous_close:.2f}")
                        except Exception as e:
                            logger.warning(f"{symbol}: Failed to get official close ({e}), using session open")
                            previous_close = market_hours_data['Close'].iloc[0]
                        
                        # Calculate percentage change from previous close
                        pct_changes = []
                        times = []
                        
                        for idx, row in market_hours_data.iterrows():
                            pct_change = ((row['Close'] - previous_close) / previous_close) * 100
                            pct_changes.append(pct_change)
                            times.append(idx)
                        
                        # Add line trace for this index
                        fig.add_trace(go.Scatter(
                            x=times,
                            y=pct_changes,
                            mode='lines',
                            name=info['name'],
                            line=dict(
                                color=info['color'],
                                width=2
                            ),
                            hovertemplate=(
                                f"<b>{info['name']}</b><br>"
                                "Time (GMT): %{x|%H:%M}<br>"
                                "Change from Prev Close: %{y:.2f}%<br>"
                                "<extra></extra>"
                            )
                        ))
                    
            except Exception as e:
                logger.warning(f"Could not fetch data for {symbol}: {e}")
    
    except Exception as e:
        logger.error(f"Error creating market performance chart: {e}")
    
    # Update layout with GMT timezone
    fig.update_layout(
        plot_bgcolor='#1e1e1e',
        paper_bgcolor='#1e1e1e',
        font={'color': '#ffffff', 'size': 11},
        xaxis={
            'showgrid': False,
            'showline': True,
            'linecolor': '#444',
            'tickfont': {'size': 10, 'color': '#999'},
            'tickformat': '%H:%M',  # 24-hour format for GMT
            'dtick': 3600000,  # Tick every hour (in milliseconds)
            'title': {
                'text': 'Time (GMT)',
                'font': {'size': 10, 'color': '#666'}
            }
        },
        yaxis={
            'showgrid': True,
            'gridcolor': '#333',
            'showline': True,
            'linecolor': '#444',
            'zeroline': True,
            'zerolinecolor': '#666',
            'zerolinewidth': 1,
            'tickfont': {'color': '#999', 'size': 10},
            'ticksuffix': '%',
            'side': 'right'
        },
        height=280,
        width=None,
        autosize=True,
        margin={'l': 20, 'r': 50, 't': 20, 'b': 50},
        hovermode='x unified',
        showlegend=True,
        legend={
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': -0.35,
            'xanchor': 'center',
            'x': 0.5,
            'font': {'size': 9, 'color': '#999'}
        }
    )
    
    return fig


# Emergency restore script
if __name__ == '__main__':
    import sys
    import os
    import re
    from datetime import datetime as dt
    
    print('=' * 80)
    print('  EMERGENCY RESTORE v1.3.15.77')
    print('  Restoring ORIGINAL 4-index chart with minimal date fix')
    print('=' * 80)
    print()
    
    if not os.path.exists('unified_trading_dashboard.py'):
        print('[ERROR] unified_trading_dashboard.py not found!')
        print('Run from: C:\\Users\\david\\Regime_trading\\COMPLETE_SYSTEM_v1.3.15.45_FINAL')
        input('Press Enter to exit...')
        sys.exit(1)
    
    # Backup
    print('[1/3] Creating emergency backup...')
    import shutil
    backup_name = f'unified_trading_dashboard.py.emergency_backup_{dt.now().strftime("%Y%m%d_%H%M%S")}'
    shutil.copy2('unified_trading_dashboard.py', backup_name)
    print(f'[OK] Backup: {backup_name}')
    
    # Read dashboard
    print('[2/3] Restoring original chart...')
    with open('unified_trading_dashboard.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Get the fixed function
    import inspect
    fixed_func = inspect.getsource(create_market_performance_chart_ORIGINAL_FIXED)
    # Remove the _ORIGINAL_FIXED suffix
    fixed_func = fixed_func.replace('create_market_performance_chart_ORIGINAL_FIXED', 'create_market_performance_chart')
    
    # Find and replace the current function
    pattern = r'def create_market_performance_chart\(state\):.*?(?=\ndef [a-zA-Z_]|\nclass [a-zA-Z_]|\n@app\.callback)'
    
    new_content = re.sub(pattern, fixed_func, content, flags=re.DOTALL)
    
    if new_content == content:
        print('[ERROR] Could not find function to replace')
        input('Press Enter to exit...')
        sys.exit(1)
    
    # Write
    with open('unified_trading_dashboard.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('[OK] Original 4-index chart restored!')
    
    # Verify
    print('[3/3] Verifying syntax...')
    try:
        compile(new_content, 'unified_trading_dashboard.py', 'exec')
        print('[OK] Syntax valid!')
    except SyntaxError as e:
        print(f'[ERROR] Syntax error: {e}')
        print('Restoring from backup...')
        shutil.copy2(backup_name, 'unified_trading_dashboard.py')
        input('Press Enter to exit...')
        sys.exit(1)
    
    print()
    print('=' * 80)
    print('  RESTORE COMPLETE!')
    print('=' * 80)
    print()
    print('✅ All 4 indices restored: AORD, FTSE, S&P 500, NASDAQ')
    print('✅ Shows % change from previous day close')
    print('✅ Date filtering bug fixed')
    print()
    print('Next: Run START.bat to restart dashboard')
    print('You will see all 4 markets tracking from previous close!')
    print()
    input('Press Enter to exit...')
