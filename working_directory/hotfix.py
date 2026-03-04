"""
TRUE HOTFIX v1.3.15.78 - Copy this ENTIRE file and run: python hotfix.py

This is a self-contained hotfix that restores your original 4-index chart.
Just run this file - no downloads needed if you already have it.
"""

# The complete fixed function to restore
FIXED_FUNCTION = '''def create_market_performance_chart(state):
    """Create intraday performance chart for major indices (market hours only, GMT timezone)"""
    import yfinance as yf
    import plotly.graph_objs as go
    import pytz
    from datetime import datetime, timedelta
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Market indices with their trading hours (in GMT)
    indices = {
        '^AORD': {
            'name': 'ASX All Ords', 
            'color': '#00CED1',
            'market_open': 23,
            'market_close': 5,
            'spans_midnight': True
        },
        '^GSPC': {
            'name': 'S&P 500', 
            'color': '#1E90FF',
            'market_open': 14,
            'market_close': 21,
            'spans_midnight': False
        },
        '^IXIC': {
            'name': 'NASDAQ', 
            'color': '#4CAF50',
            'market_open': 14,
            'market_close': 21,
            'spans_midnight': False
        },
        '^FTSE': {
            'name': 'FTSE 100', 
            'color': '#FF9800',
            'market_open': 8,
            'market_close': 16,
            'spans_midnight': False
        }
    }
    
    fig = go.Figure()
    gmt = pytz.timezone('GMT')
    now_gmt = datetime.now(gmt)
    
    try:
        for symbol, info in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='5d', interval='15m')
                
                if len(hist) > 0:
                    hist.index = hist.index.tz_convert(gmt)
                    current_date = now_gmt.date()
                    
                    market_open_hour = info['market_open']
                    market_close_hour = info['market_close']
                    spans_midnight = info.get('spans_midnight', False)
                    
                    if spans_midnight:
                        previous_date = current_date - timedelta(days=1)
                        mask = (
                            ((hist.index.date == previous_date) & (hist.index.hour >= market_open_hour)) |
                            ((hist.index.date == current_date) & (hist.index.hour < market_close_hour + 1))
                        )
                    else:
                        mask = (
                            (hist.index.date == current_date) &
                            (hist.index.hour >= market_open_hour) &
                            (hist.index.hour <= market_close_hour)
                        )
                    
                    market_hours_data = hist[mask]
                    
                    if len(market_hours_data) > 0:
                        try:
                            ticker_info = ticker.info
                            official_prev_close = ticker_info.get('regularMarketPreviousClose', ticker_info.get('previousClose'))
                            if official_prev_close and official_prev_close > 0:
                                previous_close = official_prev_close
                            else:
                                previous_close = market_hours_data['Close'].iloc[0]
                        except:
                            previous_close = market_hours_data['Close'].iloc[0]
                        
                        pct_changes = []
                        times = []
                        for idx, row in market_hours_data.iterrows():
                            pct_change = ((row['Close'] - previous_close) / previous_close) * 100
                            pct_changes.append(pct_change)
                            times.append(idx)
                        
                        fig.add_trace(go.Scatter(
                            x=times,
                            y=pct_changes,
                            mode='lines',
                            name=info['name'],
                            line=dict(color=info['color'], width=2),
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
    
    fig.update_layout(
        plot_bgcolor='#1e1e1e',
        paper_bgcolor='#1e1e1e',
        font={'color': '#ffffff', 'size': 11},
        xaxis={
            'showgrid': False,
            'showline': True,
            'linecolor': '#444',
            'tickfont': {'size': 10, 'color': '#999'},
            'tickformat': '%H:%M',
            'dtick': 3600000,
            'title': {'text': 'Time (GMT)', 'font': {'size': 10, 'color': '#666'}}
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

'''

if __name__ == '__main__':
    import os
    import re
    import shutil
    from datetime import datetime as dt
    
    print('🚨 TRUE HOTFIX v1.3.15.78 - Immediate Repair')
    print('=' * 60)
    
    if not os.path.exists('unified_trading_dashboard.py'):
        print('❌ ERROR: Run from your COMPLETE_SYSTEM folder!')
        input('Press Enter...')
        exit(1)
    
    # Backup
    backup = f'unified_trading_dashboard.py.BACKUP_{dt.now().strftime("%H%M%S")}'
    shutil.copy2('unified_trading_dashboard.py', backup)
    print(f'✅ Backup: {backup}')
    
    # Read
    with open('unified_trading_dashboard.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace
    pattern = r'def create_market_performance_chart\(state\):.*?(?=\ndef [a-zA-Z_]|\n@app\.callback|\nclass )'
    new_content = re.sub(pattern, FIXED_FUNCTION, content, flags=re.DOTALL)
    
    if new_content == content:
        print('❌ ERROR: Could not find function')
        input('Press Enter...')
        exit(1)
    
    # Write
    with open('unified_trading_dashboard.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('✅ HOTFIX APPLIED!')
    print('✅ All 4 indices restored: AORD, FTSE, S&P, NASDAQ')
    print('\nNEXT: Run START.bat')
    input('Press Enter...')
