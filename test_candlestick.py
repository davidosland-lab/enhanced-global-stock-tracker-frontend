#!/usr/bin/env python3
"""Test candlestick chart generation"""

import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Fetch CBA data
symbol = 'CBA.AX'
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
df = yf.download(symbol, start=start_date, end=end_date, progress=False, auto_adjust=True)

# Handle MultiIndex
if hasattr(df.columns, 'levels'):
    df.columns = df.columns.droplevel(1)

print(f"Data fetched for {symbol}")
print(f"Date range: {df.index[0]} to {df.index[-1]}")
print(f"Last 3 days OHLC:")
for i in range(-3, 0):
    print(f"  {df.index[i].date()}: O={df['Open'].iloc[i]:.2f} H={df['High'].iloc[i]:.2f} L={df['Low'].iloc[i]:.2f} C={df['Close'].iloc[i]:.2f}")

# Create candlestick chart
fig = go.Figure()

# Add candlestick with explicit configuration
fig.add_trace(go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close'],
    name='CBA.AX',
    increasing_line_color='green',
    decreasing_line_color='red'
))

# Update layout
fig.update_layout(
    title='CBA.AX Candlestick Chart Test',
    yaxis_title='Price ($)',
    xaxis_title='Date',
    height=600,
    template='plotly_white',
    xaxis_rangeslider_visible=False
)

# Save as HTML
output_file = '/home/user/webapp/test_candlestick.html'
fig.write_html(output_file)
print(f"\nChart saved to: {output_file}")

# Also generate JSON to check data structure
import json
chart_json = fig.to_json()
chart_data = json.loads(chart_json)
print(f"\nChart data structure:")
print(f"  Number of traces: {len(chart_data['data'])}")
if chart_data['data']:
    trace = chart_data['data'][0]
    print(f"  Trace type: {trace.get('type', 'unknown')}")
    print(f"  X values count: {len(trace.get('x', []))}")
    print(f"  Open values sample: {trace.get('open', [])[:3] if 'open' in trace else 'N/A'}")