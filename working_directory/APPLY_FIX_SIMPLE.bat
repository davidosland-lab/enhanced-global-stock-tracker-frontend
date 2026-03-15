@echo off
REM ===========================================================================
REM  MARKET CHART PATCH v1.3.15.72 - SIMPLE & RELIABLE
REM  Directly replaces the chart function with fixed version
REM ===========================================================================

chcp 65001 > nul 2>&1
setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo   MARKET CHART PATCH v1.3.15.72 - SIMPLE METHOD
echo ============================================================================
echo.
echo This patch will fix the 24-Hour Market Performance Chart
echo.
pause

REM Check if dashboard exists
if not exist "unified_trading_dashboard.py" (
    echo.
    echo [ERROR] unified_trading_dashboard.py not found!
    echo.
    echo Please run this patch from:
    echo   C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL
    echo.
    pause
    exit /b 1
)

echo.
echo [1/4] Creating backup...
copy /Y "unified_trading_dashboard.py" "unified_trading_dashboard.py.backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%" > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Backup failed!
    pause
    exit /b 1
)
echo [OK] Backup created

echo.
echo [2/4] Creating patch script...
(
echo import re
echo import sys
echo.
echo # Read the dashboard file
echo with open^('unified_trading_dashboard.py', 'r', encoding='utf-8'^) as f:
echo     content = f.read^(^)
echo.
echo # Define the pattern to find the old function
echo pattern = r'def create_market_performance_chart\(state\):.*?(?=\ndef [a-zA-Z_]|\nclass [a-zA-Z_]|\napp\.callback|\Z^)'
echo.
echo # The new function code
echo new_function = '''def create_market_performance_chart^(state^):
echo     """Create intraday performance chart - FIXED VERSION with proper date handling"""
echo     import yfinance as yf
echo     import plotly.graph_objs as go
echo     import pytz
echo     from datetime import datetime, timedelta
echo     import logging
echo     
echo     logger = logging.getLogger^(__name__^)
echo     
echo     # Market indices with their trading hours ^(in GMT^)
echo     indices = {
echo         '^AORD': {
echo             'name': 'ASX All Ords', 
echo             'color': '#00CED1',
echo             'market_open': 23,   # 23:00 GMT previous day ^(10:00 AEDT^)
echo             'market_close': 6,   # 06:00 GMT ^(17:00 AEDT^) - extended to capture end of day
echo             'spans_midnight': True
echo         },
echo         '^GSPC': {
echo             'name': 'S^&P 500', 
echo             'color': '#1E90FF',
echo             'market_open': 14,  # 14:30 GMT ^(9:30 EST^)
echo             'market_close': 21, # 21:00 GMT ^(16:00 EST^)
echo             'spans_midnight': False
echo         },
echo         '^IXIC': {
echo             'name': 'NASDAQ', 
echo             'color': '#4CAF50',
echo             'market_open': 14,  # 14:30 GMT ^(9:30 EST^)
echo             'market_close': 21, # 21:00 GMT ^(16:00 EST^)
echo             'spans_midnight': False
echo         },
echo         '^FTSE': {
echo             'name': 'FTSE 100', 
echo             'color': '#FF9800',
echo             'market_open': 8,   # 08:00 GMT
echo             'market_close': 16, # 16:30 GMT
echo             'spans_midnight': False
echo         }
echo     }
echo     
echo     fig = go.Figure^(^)
echo     gmt = pytz.timezone^('GMT'^)
echo     now_gmt = datetime.now^(gmt^)
echo     
echo     logger.info^(f"[MARKET CHART] Current time ^(GMT^): {now_gmt.strftime^('%%Y-%%m-%%d %%H:%%M:%%S'^)}"^)
echo     
echo     try:
echo         for symbol, info in indices.items^(^):
echo             try:
echo                 logger.info^(f"[MARKET CHART] Fetching {symbol} ^({info['name']}^)..."^)
echo                 
echo                 ticker = yf.Ticker^(symbol^)
echo                 hist = ticker.history^(period='1d', interval='5m'^)
echo                 
echo                 if len^(hist^) == 0:
echo                     logger.warning^(f"[MARKET CHART] No 1d data for {symbol}, trying 5d..."^)
echo                     hist = ticker.history^(period='5d', interval='15m'^)
echo                 
echo                 if len^(hist^) ^> 0:
echo                     hist.index = hist.index.tz_convert^(gmt^)
echo                     current_date = now_gmt.date^(^)
echo                     current_hour = now_gmt.hour
echo                     
echo                     logger.info^(f"[MARKET CHART] {symbol}: Latest: {hist.index[-1].strftime^('%%Y-%%m-%%d %%H:%%M:%%S GMT'^)}"^)
echo                     
echo                     market_open_hour = info['market_open']
echo                     market_close_hour = info['market_close']
echo                     spans_midnight = info.get^('spans_midnight', False^)
echo                     
echo                     if spans_midnight:
echo                         if current_hour ^< market_close_hour:
echo                             session_date = current_date
echo                             previous_date = current_date - timedelta^(days=1^)
echo                             mask = ^(
echo                                 ^(^(hist.index.date == previous_date^) ^& ^(hist.index.hour ^>= market_open_hour^)^) ^|
echo                                 ^(^(hist.index.date == session_date^) ^& ^(hist.index.hour ^<= market_close_hour^)^)
echo                             ^)
echo                         else:
echo                             if current_hour ^>= market_open_hour:
echo                                 session_date = ^(current_date + timedelta^(days=1^)^)
echo                                 previous_date = current_date
echo                                 mask = ^(
echo                                     ^(^(hist.index.date == previous_date^) ^& ^(hist.index.hour ^>= market_open_hour^)^) ^|
echo                                     ^(^(hist.index.date == session_date^) ^& ^(hist.index.hour ^<= market_close_hour^)^)
echo                                 ^)
echo                             else:
echo                                 session_date = current_date
echo                                 previous_date = current_date - timedelta^(days=1^)
echo                                 mask = ^(
echo                                     ^(^(hist.index.date == previous_date^) ^& ^(hist.index.hour ^>= market_open_hour^)^) ^|
echo                                     ^(^(hist.index.date == session_date^) ^& ^(hist.index.hour ^<= market_close_hour^)^)
echo                                 ^)
echo                     else:
echo                         if current_hour ^>= market_close_hour:
echo                             target_date = current_date
echo                         elif current_hour ^< market_open_hour:
echo                             target_date = current_date - timedelta^(days=1^)
echo                             while target_date.weekday^(^) ^>= 5:
echo                                 target_date -= timedelta^(days=1^)
echo                         else:
echo                             target_date = current_date
echo                         
echo                         mask = ^(
echo                             ^(hist.index.date == target_date^) ^&
echo                             ^(hist.index.hour ^>= market_open_hour^) ^&
echo                             ^(hist.index.hour ^<= market_close_hour^)
echo                         ^)
echo                     
echo                     market_hours_data = hist[mask]
echo                     logger.info^(f"[MARKET CHART] {symbol}: Filtered to {len^(market_hours_data^)} points"^)
echo                     
echo                     if len^(market_hours_data^) ^> 0:
echo                         try:
echo                             ticker_info = ticker.info
echo                             official_prev_close = ticker_info.get^('regularMarketPreviousClose', 
echo                                                                   ticker_info.get^('previousClose'^)^)
echo                             if official_prev_close and official_prev_close ^> 0:
echo                                 previous_close = official_prev_close
echo                             else:
echo                                 previous_close = market_hours_data['Close'].iloc[0]
echo                         except:
echo                             previous_close = market_hours_data['Close'].iloc[0]
echo                         
echo                         pct_changes = []
echo                         times = []
echo                         for idx, row in market_hours_data.iterrows^(^):
echo                             pct_change = ^(^(row['Close'] - previous_close^) / previous_close^) * 100
echo                             pct_changes.append^(pct_change^)
echo                             times.append^(idx^)
echo                         
echo                         fig.add_trace^(go.Scatter^(
echo                             x=times,
echo                             y=pct_changes,
echo                             mode='lines',
echo                             name=info['name'],
echo                             line=dict^(color=info['color'], width=2^),
echo                             hovertemplate=^(
echo                                 f"^<b^>{info['name']}^</b^>^<br^>"
echo                                 "Time ^(GMT^): %%{x^|%%H:%%M}^<br^>"
echo                                 "Change: %%{y:.2f}%%^<br^>"
echo                                 "^<extra^>^</extra^>"
echo                             ^)
echo                         ^)^)
echo                         logger.info^(f"[MARKET CHART] {symbol}: Added successfully"^)
echo             except Exception as e:
echo                 logger.error^(f"[MARKET CHART] Error fetching {symbol}: {e}"^)
echo     except Exception as e:
echo         logger.error^(f"[MARKET CHART] Critical error: {e}"^)
echo     
echo     fig.update_layout^(
echo         plot_bgcolor='#1e1e1e',
echo         paper_bgcolor='#1e1e1e',
echo         font={'color': '#ffffff', 'size': 11},
echo         margin={'l': 40, 'r': 20, 't': 30, 'b': 40},
echo         height=280,
echo         showlegend=True,
echo         legend={'x': 0.02, 'y': 0.98, 'bgcolor': 'rgba^(0,0,0,0.5^)', 'bordercolor': '#444', 'borderwidth': 1},
echo         xaxis={
echo             'showgrid': False, 'showline': True, 'linecolor': '#444',
echo             'tickfont': {'size': 10, 'color': '#999'},
echo             'tickformat': '%%H:%%M', 'dtick': 3600000,
echo             'title': {'text': f'Time ^(GMT^) - Updated: {now_gmt.strftime^("%%H:%%M:%%S"^)}', 'font': {'size': 10, 'color': '#666'}}
echo         },
echo         yaxis={
echo             'showgrid': True, 'gridcolor': '#333',
echo             'zeroline': True, 'zerolinecolor': '#666', 'zerolinewidth': 1,
echo             'ticksuffix': '%%', 'tickfont': {'size': 10, 'color': '#999'},
echo             'title': {'text': 'Change from Previous Close', 'font': {'size': 10, 'color': '#666'}}
echo         },
echo         hovermode='x unified'
echo     ^)
echo     return fig
echo '''
echo.
echo # Replace the function
echo new_content = re.sub^(pattern, new_function + '\n\n', content, flags=re.DOTALL^)
echo.
echo # Write back
echo with open^('unified_trading_dashboard.py', 'w', encoding='utf-8'^) as f:
echo     f.write^(new_content^)
echo.
echo print^('[OK] Patch applied successfully!'^)
) > _patch_script.py

echo [OK] Patch script created

echo.
echo [3/4] Applying patch...
python _patch_script.py 2>&1
if errorlevel 1 (
    echo [ERROR] Patch failed!
    echo Rolling back...
    copy /Y "unified_trading_dashboard.py.backup_*" "unified_trading_dashboard.py" > nul 2>&1
    del _patch_script.py > nul 2>&1
    pause
    exit /b 1
)

echo.
echo [4/4] Cleaning up...
del _patch_script.py > nul 2>&1
echo [OK] Cleanup complete

echo.
echo ============================================================================
echo   PATCH COMPLETE!
echo ============================================================================
echo.
echo The 24-Hour Market Performance Chart has been fixed!
echo.
echo Next step: Restart the dashboard
echo   1) Press Ctrl+C in the dashboard window (if running)
echo   2) Run START.bat
echo   3) Open http://localhost:8050
echo.
echo The chart should now show CURRENT data with real-time updates!
echo.
echo ============================================================================
echo.
pause
