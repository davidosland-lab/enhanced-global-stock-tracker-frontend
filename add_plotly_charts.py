#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plotly Chart Addition Module - Adds professional charts to existing system
This is an ADDITION to the existing unified_stock_professional.py, not a replacement
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

def generate_plotly_chart(data, chart_type='candlestick', include_indicators=True):
    """
    Generate a Plotly chart from stock data
    Returns HTML string that can be embedded in the page
    """
    
    # Create figure with secondary y-axis for volume
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'{data.get("symbol", "Stock")} Price', 'Volume'),
        row_width=[0.2, 0.7]
    )
    
    # Prepare data
    dates = data.get('dates', [])
    prices = data.get('prices', [])
    volumes = data.get('volume', [])
    opens = data.get('open', [])
    highs = data.get('high', [])
    lows = data.get('low', [])
    
    # Add main price chart
    if chart_type == 'candlestick' and opens and highs and lows:
        fig.add_trace(
            go.Candlestick(
                x=dates,
                open=opens,
                high=highs,
                low=lows,
                close=prices,
                name='Price',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ),
            row=1, col=1
        )
    elif chart_type == 'line':
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=prices,
                mode='lines',
                name='Price',
                line=dict(color='#2962FF', width=2)
            ),
            row=1, col=1
        )
    elif chart_type == 'area':
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=prices,
                mode='lines',
                name='Price',
                fill='tozeroy',
                line=dict(color='#2962FF', width=2),
                fillcolor='rgba(41, 98, 255, 0.3)'
            ),
            row=1, col=1
        )
    else:  # Default to line if candlestick data not available
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=prices,
                mode='lines',
                name='Price',
                line=dict(color='#2962FF', width=2)
            ),
            row=1, col=1
        )
    
    # Add volume bars
    if volumes:
        colors = ['red' if i > 0 and prices[i] < prices[i-1] else 'green' 
                  for i in range(len(prices))]
        
        fig.add_trace(
            go.Bar(
                x=dates,
                y=volumes,
                name='Volume',
                marker_color=colors,
                opacity=0.5
            ),
            row=2, col=1
        )
    
    # Add technical indicators if requested
    if include_indicators and len(prices) >= 20:
        # Simple Moving Average
        sma_20 = [sum(prices[max(0, i-19):i+1]) / len(prices[max(0, i-19):i+1]) 
                   for i in range(len(prices))]
        
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=sma_20,
                mode='lines',
                name='SMA(20)',
                line=dict(color='orange', width=1, dash='dash'),
                visible='legendonly'
            ),
            row=1, col=1
        )
        
        # Bollinger Bands
        if len(prices) >= 20:
            bb_window = 20
            bb_std = 2
            
            sma = [sum(prices[max(0, i-bb_window+1):i+1]) / min(bb_window, i+1) 
                   for i in range(len(prices))]
            
            std_dev = []
            for i in range(len(prices)):
                window = prices[max(0, i-bb_window+1):i+1]
                if len(window) > 1:
                    mean = sum(window) / len(window)
                    variance = sum((x - mean) ** 2 for x in window) / len(window)
                    std_dev.append(variance ** 0.5)
                else:
                    std_dev.append(0)
            
            upper_band = [sma[i] + bb_std * std_dev[i] for i in range(len(sma))]
            lower_band = [sma[i] - bb_std * std_dev[i] for i in range(len(sma))]
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=upper_band,
                    mode='lines',
                    name='BB Upper',
                    line=dict(color='rgba(250,128,114,0.3)', width=1),
                    visible='legendonly'
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=lower_band,
                    mode='lines',
                    name='BB Lower',
                    line=dict(color='rgba(250,128,114,0.3)', width=1),
                    fill='tonexty',
                    fillcolor='rgba(250,128,114,0.1)',
                    visible='legendonly'
                ),
                row=1, col=1
            )
    
    # Update layout
    fig.update_layout(
        title=f"{data.get('symbol', 'Stock')} - ${data.get('current_price', 0):.2f} | "
              f"Change: {data.get('change', 0):.2f} ({data.get('change_percent', 0):.2f}%)",
        yaxis_title='Price ($)',
        xaxis_rangeslider_visible=False,
        height=600,
        template='plotly_white',
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update axes
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    
    # Convert to HTML
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': f'{data.get("symbol", "chart")}_{chart_type}',
            'height': 600,
            'width': 1200,
            'scale': 1
        }
    }
    
    html_str = fig.to_html(
        include_plotlyjs='cdn',
        config=config,
        div_id="plotly-chart"
    )
    
    return html_str

def generate_indicator_chart(prices, indicators, symbol="Stock"):
    """
    Generate a separate chart for technical indicators
    Returns HTML string
    """
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=('Price with Indicators', 'RSI', 'MACD'),
        row_heights=[0.5, 0.25, 0.25]
    )
    
    # Create x-axis (indices)
    x_values = list(range(len(prices)))
    
    # Price line
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=prices,
            mode='lines',
            name='Price',
            line=dict(color='#2962FF', width=2)
        ),
        row=1, col=1
    )
    
    # RSI if available
    if 'RSI' in indicators and indicators['RSI'] is not None:
        rsi_values = [indicators['RSI']] * min(14, len(prices))
        fig.add_trace(
            go.Scatter(
                x=x_values[-len(rsi_values):],
                y=rsi_values,
                mode='lines',
                name='RSI',
                line=dict(color='purple', width=2)
            ),
            row=2, col=1
        )
        
        # Add RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
        fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.3, row=2, col=1)
    
    # MACD if available
    if 'MACD' in indicators and indicators['MACD'] is not None:
        macd_values = [indicators['MACD']] * min(26, len(prices))
        signal_values = [indicators.get('MACD_signal', indicators['MACD'])] * min(26, len(prices))
        
        fig.add_trace(
            go.Scatter(
                x=x_values[-len(macd_values):],
                y=macd_values,
                mode='lines',
                name='MACD',
                line=dict(color='blue', width=2)
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=x_values[-len(signal_values):],
                y=signal_values,
                mode='lines',
                name='Signal',
                line=dict(color='red', width=1, dash='dash')
            ),
            row=3, col=1
        )
    
    # Update layout
    fig.update_layout(
        title=f"{symbol} - Technical Indicators",
        height=700,
        template='plotly_white',
        showlegend=True,
        hovermode='x unified'
    )
    
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1)
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    fig.update_xaxes(title_text="Time Period", row=3, col=1)
    
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
    }
    
    html_str = fig.to_html(
        include_plotlyjs='cdn',
        config=config,
        div_id="plotly-indicators"
    )
    
    return html_str

# Add this to the existing Flask app as new endpoints
def add_plotly_endpoints(app):
    """Add Plotly chart endpoints to existing Flask app"""
    
    @app.route("/api/plotly-chart", methods=["POST"])
    def api_plotly_chart():
        """Generate Plotly chart from data"""
        try:
            data = request.json
            chart_type = data.get('chart_type', 'candlestick')
            include_indicators = data.get('include_indicators', True)
            stock_data = data.get('stock_data', {})
            
            if not stock_data or not stock_data.get('prices'):
                return jsonify({'error': 'No data provided'}), 400
            
            html_chart = generate_plotly_chart(stock_data, chart_type, include_indicators)
            
            return jsonify({'chart_html': html_chart})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route("/api/plotly-indicators", methods=["POST"])
    def api_plotly_indicators():
        """Generate indicator chart"""
        try:
            data = request.json
            prices = data.get('prices', [])
            indicators = data.get('indicators', {})
            symbol = data.get('symbol', 'Stock')
            
            if not prices:
                return jsonify({'error': 'No price data provided'}), 400
            
            html_chart = generate_indicator_chart(prices, indicators, symbol)
            
            return jsonify({'chart_html': html_chart})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app

if __name__ == "__main__":
    # Test the chart generation
    test_data = {
        'symbol': 'TEST',
        'prices': [100 + i * 0.5 + (i % 3) for i in range(50)],
        'dates': [f'2024-01-{i+1:02d}' for i in range(50)],
        'volume': [1000000 + i * 10000 for i in range(50)],
        'open': [100 + i * 0.4 for i in range(50)],
        'high': [101 + i * 0.5 for i in range(50)],
        'low': [99 + i * 0.4 for i in range(50)],
        'current_price': 125.50,
        'change': 5.50,
        'change_percent': 4.58
    }
    
    html = generate_plotly_chart(test_data, 'candlestick')
    
    # Save test chart
    with open('/home/user/webapp/test_plotly_chart.html', 'w') as f:
        f.write(html)
    
    print("Test chart saved to test_plotly_chart.html")
    print("To integrate: import this module and call add_plotly_endpoints(app)")