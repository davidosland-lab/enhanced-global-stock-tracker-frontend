#!/usr/bin/env python3
"""
Stock Analysis System - Complete Version with Alpha Vantage Integration
Includes Yahoo Finance + Alpha Vantage fallback
"""

import yfinance as yf
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import requests
import time
from typing import Optional, Dict, Any, Tuple

app = Flask(__name__)
CORS(app)

# Alpha Vantage Configuration
ALPHA_VANTAGE_API_KEY = "68ZFANK047DL0KSR"
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

class StockDataFetcher:
    """Unified data fetcher with Yahoo Finance primary and Alpha Vantage fallback"""
    
    def __init__(self):
        self.av_api_key = ALPHA_VANTAGE_API_KEY
        self.au_stocks = ['CBA', 'BHP', 'CSL', 'NAB', 'ANZ', 'WBC', 'WES', 'MQG', 'TLS', 'WOW', 
                         'CWN', 'RIO', 'FMG', 'NCM', 'ALL', 'SUN', 'QAN', 'WPL', 'TCL', 'COL']
    
    def _add_au_suffix(self, symbol: str) -> str:
        """Add .AX suffix for Australian stocks"""
        symbol_upper = symbol.upper().replace('.AX', '')
        if symbol_upper in self.au_stocks and not symbol.endswith('.AX'):
            return f"{symbol_upper}.AX"
        return symbol
    
    def fetch_yahoo_data(self, symbol: str, period: str = '1mo') -> Optional[pd.DataFrame]:
        """Fetch data from Yahoo Finance"""
        try:
            symbol = self._add_au_suffix(symbol)
            ticker = yf.Ticker(symbol)
            
            # Map period to appropriate parameters
            period_map = {
                '1d': ('5d', '5m'),
                '5d': ('5d', '30m'),
                '1mo': ('1mo', '1d'),
                '3mo': ('3mo', '1d'),
                '6mo': ('6mo', '1d'),
                '1y': ('1y', '1d'),
                '5y': ('5y', '1wk')
            }
            
            yf_period, interval = period_map.get(period, ('1mo', '1d'))
            
            if period == '1d':
                # Get intraday data
                df = ticker.history(period=yf_period, interval=interval)
                # Filter to today only
                today = datetime.now().date()
                df = df[df.index.date == today] if len(df) > 0 else ticker.history(period='1d', interval='5m')
            else:
                df = ticker.history(period=yf_period, interval=interval)
            
            if df.empty:
                print(f"Yahoo Finance: No data for {symbol}")
                return None
                
            return df
            
        except Exception as e:
            print(f"Yahoo Finance error for {symbol}: {str(e)}")
            return None
    
    def fetch_alpha_vantage_data(self, symbol: str, period: str = '1mo') -> Optional[pd.DataFrame]:
        """Fetch data from Alpha Vantage as fallback"""
        try:
            symbol = self._add_au_suffix(symbol).replace('.AX', '.AUS')  # Alpha Vantage uses .AUS for Australian stocks
            
            # Determine function based on period
            if period in ['1d', '5d']:
                # Use intraday data
                function = 'TIME_SERIES_INTRADAY'
                interval = '5min' if period == '1d' else '30min'
                params = {
                    'function': function,
                    'symbol': symbol,
                    'interval': interval,
                    'apikey': self.av_api_key,
                    'outputsize': 'full'
                }
            else:
                # Use daily data
                function = 'TIME_SERIES_DAILY_ADJUSTED'
                params = {
                    'function': function,
                    'symbol': symbol,
                    'apikey': self.av_api_key,
                    'outputsize': 'full'
                }
            
            response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=10)
            data = response.json()
            
            # Check for errors
            if 'Error Message' in data:
                print(f"Alpha Vantage error: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                print(f"Alpha Vantage API limit reached")
                return None
            
            # Parse the time series data
            if period in ['1d', '5d']:
                time_series_key = f'Time Series ({interval})'
            else:
                time_series_key = 'Time Series (Daily)'
            
            if time_series_key not in data:
                print(f"Alpha Vantage: No time series data for {symbol}")
                return None
            
            # Convert to DataFrame
            time_series = data[time_series_key]
            df_data = []
            
            for timestamp, values in time_series.items():
                df_data.append({
                    'Date': pd.to_datetime(timestamp),
                    'Open': float(values.get('1. open', values.get('1. adjusted open', 0))),
                    'High': float(values.get('2. high', values.get('2. adjusted high', 0))),
                    'Low': float(values.get('3. low', values.get('3. adjusted low', 0))),
                    'Close': float(values.get('4. close', values.get('4. adjusted close', 0))),
                    'Volume': int(values.get('5. volume', values.get('6. volume', 0)))
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)
            
            # Filter based on period
            now = datetime.now()
            period_days = {
                '1d': 1, '5d': 5, '1mo': 30, '3mo': 90,
                '6mo': 180, '1y': 365, '5y': 1825
            }
            
            days = period_days.get(period, 30)
            cutoff_date = now - timedelta(days=days)
            df = df[df.index >= cutoff_date]
            
            return df if not df.empty else None
            
        except Exception as e:
            print(f"Alpha Vantage error for {symbol}: {str(e)}")
            return None
    
    def fetch_data(self, symbol: str, period: str = '1mo') -> Tuple[Optional[pd.DataFrame], str]:
        """Fetch data with automatic fallback"""
        # Try Yahoo Finance first
        df = self.fetch_yahoo_data(symbol, period)
        if df is not None and not df.empty:
            return df, "Yahoo Finance"
        
        # Fallback to Alpha Vantage
        print(f"Falling back to Alpha Vantage for {symbol}")
        df = self.fetch_alpha_vantage_data(symbol, period)
        if df is not None and not df.empty:
            return df, "Alpha Vantage"
        
        return None, "None"

# Global data fetcher instance
data_fetcher = StockDataFetcher()

def calculate_technical_indicators(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate all technical indicators"""
    indicators = {}
    
    # RSI
    if len(df) >= 14:
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / (loss + 1e-10)
        indicators['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    if len(df) >= 26:
        ema12 = df['Close'].ewm(span=12).mean()
        ema26 = df['Close'].ewm(span=26).mean()
        indicators['macd_line'] = ema12 - ema26
        indicators['signal_line'] = indicators['macd_line'].ewm(span=9).mean()
        indicators['macd_histogram'] = indicators['macd_line'] - indicators['signal_line']
    
    # Bollinger Bands
    if len(df) >= 20:
        sma20 = df['Close'].rolling(20).mean()
        std20 = df['Close'].rolling(20).std()
        indicators['bb_upper'] = sma20 + (std20 * 2)
        indicators['bb_lower'] = sma20 - (std20 * 2)
        indicators['bb_middle'] = sma20
    
    # Moving Averages
    if len(df) >= 20:
        indicators['sma_20'] = df['Close'].rolling(20).mean()
    if len(df) >= 50:
        indicators['sma_50'] = df['Close'].rolling(50).mean()
    if len(df) >= 200:
        indicators['sma_200'] = df['Close'].rolling(200).mean()
    
    # EMA
    if len(df) >= 12:
        indicators['ema_12'] = df['Close'].ewm(span=12).mean()
    if len(df) >= 26:
        indicators['ema_26'] = df['Close'].ewm(span=26).mean()
    
    # ATR (Average True Range)
    if len(df) >= 14:
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        indicators['atr'] = true_range.rolling(14).mean()
    
    # Stochastic Oscillator
    if len(df) >= 14:
        lowest_low = df['Low'].rolling(14).min()
        highest_high = df['High'].rolling(14).max()
        indicators['stoch_k'] = 100 * ((df['Close'] - lowest_low) / (highest_high - lowest_low + 1e-10))
        indicators['stoch_d'] = indicators['stoch_k'].rolling(3).mean()
    
    return indicators

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """API endpoint for raw stock data"""
    try:
        period = request.args.get('period', '1mo')
        df, source = data_fetcher.fetch_data(symbol, period)
        
        if df is None:
            return jsonify({'error': f'No data available for {symbol}'}), 404
        
        # Calculate indicators
        indicators = calculate_technical_indicators(df)
        
        # Convert to JSON-friendly format
        data = {
            'dates': [d.strftime('%Y-%m-%d %H:%M:%S') for d in df.index],
            'open': [float(p) for p in df['Open'].values],
            'high': [float(p) for p in df['High'].values],
            'low': [float(p) for p in df['Low'].values],
            'close': [float(p) for p in df['Close'].values],
            'volume': [int(v) for v in df['Volume'].values],
            'current_price': float(df['Close'].iloc[-1]),
            'min_price': float(df['Low'].min()),
            'max_price': float(df['High'].max()),
            'data_points': len(df),
            'data_source': source,
            'indicators': {
                key: value.tolist() if hasattr(value, 'tolist') else value
                for key, value in indicators.items()
            }
        }
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart', methods=['POST'])
def generate_chart():
    """Generate interactive chart with all technical indicators"""
    try:
        data = request.json
        symbol = data.get('symbol', 'AAPL')
        period = data.get('period', '1mo')
        chart_type = data.get('chart_type', 'candlestick')
        show_indicators = data.get('show_indicators', True)
        
        # Fetch data
        df, source = data_fetcher.fetch_data(symbol, period)
        
        if df is None:
            return jsonify({'error': f'No data available for {symbol}', 'success': False}), 404
        
        # Calculate indicators
        indicators = calculate_technical_indicators(df)
        
        # Create subplots - more rows if showing all indicators
        if show_indicators:
            fig = make_subplots(
                rows=5, cols=1,
                row_heights=[0.4, 0.15, 0.15, 0.15, 0.15],
                subplot_titles=['Price', 'Volume', 'RSI', 'MACD', 'Stochastic'],
                vertical_spacing=0.03,
                specs=[[{"secondary_y": False}]] * 5
            )
        else:
            fig = make_subplots(
                rows=2, cols=1,
                row_heights=[0.7, 0.3],
                subplot_titles=['Price', 'Volume'],
                vertical_spacing=0.05
            )
        
        # Price chart
        if chart_type == 'candlestick':
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='OHLC',
                increasing=dict(line=dict(color='#26a69a'), fillcolor='#26a69a'),
                decreasing=dict(line=dict(color='#ef5350'), fillcolor='#ef5350')
            ), row=1, col=1)
            
            # Add Bollinger Bands
            if 'bb_upper' in indicators:
                fig.add_trace(go.Scatter(
                    x=df.index, y=indicators['bb_upper'],
                    line=dict(color='rgba(150, 150, 150, 0.5)', width=1),
                    name='BB Upper', showlegend=False
                ), row=1, col=1)
                
                fig.add_trace(go.Scatter(
                    x=df.index, y=indicators['bb_lower'],
                    line=dict(color='rgba(150, 150, 150, 0.5)', width=1),
                    name='BB Lower', fill='tonexty',
                    fillcolor='rgba(150, 150, 150, 0.1)', showlegend=False
                ), row=1, col=1)
                
                fig.add_trace(go.Scatter(
                    x=df.index, y=indicators['bb_middle'],
                    line=dict(color='orange', width=1, dash='dash'),
                    name='BB Middle'
                ), row=1, col=1)
        else:
            # Line or Area chart
            fig.add_trace(go.Scatter(
                x=df.index, y=df['Close'],
                mode='lines',
                name='Close',
                line=dict(color='#2196F3', width=2),
                fill='tozeroy' if chart_type == 'area' else None,
                fillcolor='rgba(33, 150, 243, 0.3)' if chart_type == 'area' else None
            ), row=1, col=1)
        
        # Add moving averages
        if 'sma_20' in indicators:
            fig.add_trace(go.Scatter(
                x=df.index, y=indicators['sma_20'],
                mode='lines', name='SMA 20',
                line=dict(color='orange', width=1)
            ), row=1, col=1)
        
        if 'sma_50' in indicators:
            fig.add_trace(go.Scatter(
                x=df.index, y=indicators['sma_50'],
                mode='lines', name='SMA 50',
                line=dict(color='red', width=1)
            ), row=1, col=1)
        
        # Volume
        volume_colors = ['#26a69a' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ef5350' 
                        for i in range(len(df))]
        fig.add_trace(go.Bar(
            x=df.index, y=df['Volume'],
            marker_color=volume_colors,
            showlegend=False, name='Volume'
        ), row=2, col=1)
        
        if show_indicators:
            # RSI
            if 'rsi' in indicators:
                fig.add_trace(go.Scatter(
                    x=df.index, y=indicators['rsi'],
                    mode='lines', name='RSI',
                    line=dict(color='purple', width=2)
                ), row=3, col=1)
                fig.add_hline(y=70, line_dash="dash", line_color="red", 
                            opacity=0.3, row=3, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", 
                            opacity=0.3, row=3, col=1)
            
            # MACD
            if 'macd_line' in indicators:
                fig.add_trace(go.Scatter(
                    x=df.index, y=indicators['macd_line'],
                    mode='lines', name='MACD',
                    line=dict(color='blue', width=1.5)
                ), row=4, col=1)
                
                fig.add_trace(go.Scatter(
                    x=df.index, y=indicators['signal_line'],
                    mode='lines', name='Signal',
                    line=dict(color='red', width=1.5)
                ), row=4, col=1)
                
                hist_colors = ['green' if h >= 0 else 'red' for h in indicators['macd_histogram']]
                fig.add_trace(go.Bar(
                    x=df.index, y=indicators['macd_histogram'],
                    marker_color=hist_colors,
                    showlegend=False, name='Histogram',
                    opacity=0.4
                ), row=4, col=1)
            
            # Stochastic
            if 'stoch_k' in indicators:
                fig.add_trace(go.Scatter(
                    x=df.index, y=indicators['stoch_k'],
                    mode='lines', name='%K',
                    line=dict(color='blue', width=1.5)
                ), row=5, col=1)
                
                fig.add_trace(go.Scatter(
                    x=df.index, y=indicators['stoch_d'],
                    mode='lines', name='%D',
                    line=dict(color='red', width=1.5)
                ), row=5, col=1)
                
                fig.add_hline(y=80, line_dash="dash", line_color="red", 
                            opacity=0.3, row=5, col=1)
                fig.add_hline(y=20, line_dash="dash", line_color="green", 
                            opacity=0.3, row=5, col=1)
        
        # Calculate proper price range
        price_min = df[['Open', 'High', 'Low', 'Close']].min().min()
        price_max = df[['Open', 'High', 'Low', 'Close']].max().max()
        price_range = price_max - price_min
        price_padding = price_range * 0.1
        
        # Update layout
        height = 1000 if show_indicators else 600
        fig.update_layout(
            title=dict(
                text=f'{symbol.upper()} - {period.upper()} - {chart_type.title()} | Source: {source}',
                font=dict(size=20, color='#333')
            ),
            height=height,
            showlegend=True,
            hovermode='x unified',
            xaxis_rangeslider_visible=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif', size=12),
            margin=dict(t=80, b=80, l=80, r=80)
        )
        
        # Update y-axes
        fig.update_yaxes(
            title_text="Price ($)",
            range=[price_min - price_padding, price_max + price_padding],
            gridcolor='#e0e0e0', row=1, col=1
        )
        fig.update_yaxes(title_text="Volume", gridcolor='#e0e0e0', row=2, col=1)
        
        if show_indicators:
            fig.update_yaxes(title_text="RSI", range=[0, 100], gridcolor='#e0e0e0', row=3, col=1)
            fig.update_yaxes(title_text="MACD", gridcolor='#e0e0e0', row=4, col=1)
            fig.update_yaxes(title_text="Stoch %", range=[0, 100], gridcolor='#e0e0e0', row=5, col=1)
        
        # Update x-axes
        for i in range(1, (6 if show_indicators else 3)):
            fig.update_xaxes(gridcolor='#e0e0e0', row=i, col=1)
        
        # Return chart data
        return jsonify({
            'success': True,
            'chart': json.loads(fig.to_json()),
            'stats': {
                'symbol': symbol.upper(),
                'period': period,
                'chart_type': chart_type,
                'min_price': float(price_min),
                'max_price': float(price_max),
                'current_price': float(df['Close'].iloc[-1]),
                'price_change': float(df['Close'].iloc[-1] - df['Close'].iloc[0]),
                'price_change_pct': float((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100),
                'data_points': len(df),
                'data_source': source,
                'last_updated': df.index[-1].strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/')
def index():
    """Main interface with complete features"""
    html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Stock Analysis System - Complete Edition</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1800px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #333;
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 16px;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 10px;
        }
        
        .status-yahoo { background: #4CAF50; color: white; }
        .status-alpha { background: #FF9800; color: white; }
        
        .controls-panel {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .controls-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .control-group {
            display: flex;
            flex-direction: column;
        }
        
        .control-group label {
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .control-group input,
        .control-group select {
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s;
            background: white;
        }
        
        .control-group input:focus,
        .control-group select:focus {
            border-color: #667eea;
            outline: none;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            margin-top: 10px;
        }
        
        .checkbox-group input[type="checkbox"] {
            width: 20px;
            height: 20px;
            margin-right: 10px;
        }
        
        .buttons {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        button {
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        
        button.secondary {
            background: linear-gradient(135deg, #4CAF50, #45a049);
        }
        
        button.warning {
            background: linear-gradient(135deg, #FF9800, #F57C00);
        }
        
        .chart-container {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            min-height: 500px;
        }
        
        #chart {
            width: 100%;
            height: 100%;
            min-height: 600px;
        }
        
        #loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 400px;
            color: #999;
            font-size: 18px;
            flex-direction: column;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        .stat-label {
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: bold;
            color: #333;
        }
        
        .stat-change {
            font-size: 14px;
            margin-top: 5px;
        }
        
        .positive { color: #4CAF50; }
        .negative { color: #f44336; }
        
        .popular-stocks {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        .stock-btn {
            padding: 8px 16px;
            background: #f5f5f5;
            border: 1px solid #e0e0e0;
            border-radius: 20px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .stock-btn:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        .indicators-panel {
            background: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .indicators-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }
        
        .indicator-item {
            padding: 10px;
            background: #f5f5f5;
            border-radius: 8px;
            text-align: center;
        }
        
        .indicator-name {
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }
        
        .indicator-value {
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }
        
        @media (max-width: 768px) {
            .controls-grid {
                grid-template-columns: 1fr;
            }
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Stock Analysis System - Complete Edition
                <span id="dataSource" class="status-badge status-yahoo">Yahoo Finance</span>
            </h1>
            <p>Professional market analysis with Yahoo Finance + Alpha Vantage fallback</p>
        </div>
        
        <div class="controls-panel">
            <div class="controls-grid">
                <div class="control-group">
                    <label>Stock Symbol</label>
                    <input type="text" id="symbol" value="AAPL" placeholder="Enter symbol (e.g., AAPL, CBA)">
                </div>
                
                <div class="control-group">
                    <label>Time Period</label>
                    <select id="period">
                        <option value="1d">1 Day (Intraday)</option>
                        <option value="5d">5 Days</option>
                        <option value="1mo" selected>1 Month</option>
                        <option value="3mo">3 Months</option>
                        <option value="6mo">6 Months</option>
                        <option value="1y">1 Year</option>
                        <option value="5y">5 Years</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label>Chart Type</label>
                    <select id="chartType">
                        <option value="candlestick">Candlestick (OHLC)</option>
                        <option value="line">Line Chart</option>
                        <option value="area">Area Chart</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label>Options</label>
                    <div class="checkbox-group">
                        <input type="checkbox" id="showIndicators" checked>
                        <label for="showIndicators">Show All Indicators</label>
                    </div>
                </div>
            </div>
            
            <div class="buttons">
                <button onclick="loadChart()">🔄 Generate Chart</button>
                <button class="secondary" onclick="fetchRawData()">📊 Get Raw Data</button>
                <button class="warning" onclick="testDataSources()">🧪 Test Data Sources</button>
                <button onclick="autoRefresh()" id="autoRefreshBtn">⏰ Auto Refresh: OFF</button>
            </div>
            
            <div class="popular-stocks">
                <span style="color: #666; margin-right: 10px;">Quick Access:</span>
                <span class="stock-btn" onclick="quickLoad('AAPL')">AAPL</span>
                <span class="stock-btn" onclick="quickLoad('GOOGL')">GOOGL</span>
                <span class="stock-btn" onclick="quickLoad('MSFT')">MSFT</span>
                <span class="stock-btn" onclick="quickLoad('TSLA')">TSLA</span>
                <span class="stock-btn" onclick="quickLoad('AMZN')">AMZN</span>
                <span class="stock-btn" onclick="quickLoad('CBA')">CBA.AX</span>
                <span class="stock-btn" onclick="quickLoad('BHP')">BHP.AX</span>
                <span class="stock-btn" onclick="quickLoad('CSL')">CSL.AX</span>
                <span class="stock-btn" onclick="quickLoad('NAB')">NAB.AX</span>
            </div>
        </div>
        
        <div id="statsContainer" class="stats-grid"></div>
        
        <div id="indicatorsPanel" class="indicators-panel" style="display: none;">
            <h3>Technical Indicators</h3>
            <div id="indicatorsGrid" class="indicators-grid"></div>
        </div>
        
        <div class="chart-container">
            <div id="chart">
                <div id="loading">Select options and click "Generate Chart" to begin</div>
            </div>
        </div>
    </div>
    
    <script>
        let autoRefreshInterval = null;
        let lastIndicators = {};
        
        function quickLoad(symbol) {
            document.getElementById('symbol').value = symbol;
            loadChart();
        }
        
        async function testDataSources() {
            const symbol = document.getElementById('symbol').value;
            alert('Testing data sources for ' + symbol + '...\\nThis will check Yahoo Finance and Alpha Vantage availability.');
            
            try {
                const response = await fetch(`/api/stock/${symbol}?period=1mo`);
                const data = await response.json();
                
                if (data.error) {
                    alert('Error: Both data sources failed!\\n' + data.error);
                } else {
                    alert(`Data Source Test Results:\\n` +
                          `Symbol: ${symbol}\\n` +
                          `Active Source: ${data.data_source}\\n` +
                          `Data Points: ${data.data_points}\\n` +
                          `Current Price: $${data.current_price.toFixed(2)}\\n\\n` +
                          `The system will automatically use Alpha Vantage if Yahoo Finance fails.`);
                }
            } catch (error) {
                alert('Test failed: ' + error.message);
            }
        }
        
        async function fetchRawData() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            
            try {
                const response = await fetch(`/api/stock/${symbol}?period=${period}`);
                const data = await response.json();
                
                if (data.error) {
                    alert('Error: ' + data.error);
                    return;
                }
                
                console.log('Raw Data:', data);
                
                // Store indicators
                lastIndicators = data.indicators || {};
                
                alert(`Data fetched successfully!\\n` +
                      `Symbol: ${symbol}\\n` +
                      `Source: ${data.data_source}\\n` +
                      `Data Points: ${data.data_points}\\n` +
                      `Current Price: $${data.current_price.toFixed(2)}\\n` +
                      `Price Range: $${data.min_price.toFixed(2)} - $${data.max_price.toFixed(2)}\\n\\n` +
                      `Check console for full data including indicators.`);
            } catch (error) {
                alert('Error fetching data: ' + error.message);
            }
        }
        
        async function loadChart() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            const chartType = document.getElementById('chartType').value;
            const showIndicators = document.getElementById('showIndicators').checked;
            
            if (!symbol) {
                alert('Please enter a stock symbol');
                return;
            }
            
            document.getElementById('chart').innerHTML = '<div id="loading"><div class="spinner"></div>Loading chart data...</div>';
            
            try {
                const response = await fetch('/api/chart', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        symbol: symbol,
                        period: period,
                        chart_type: chartType,
                        show_indicators: showIndicators
                    })
                });
                
                const result = await response.json();
                
                if (!result.success) {
                    throw new Error(result.error || 'Failed to generate chart');
                }
                
                // Update data source badge
                const badge = document.getElementById('dataSource');
                badge.textContent = result.stats.data_source;
                badge.className = 'status-badge ' + 
                    (result.stats.data_source === 'Yahoo Finance' ? 'status-yahoo' : 'status-alpha');
                
                // Adjust chart height based on indicators
                const chartDiv = document.getElementById('chart');
                chartDiv.style.minHeight = showIndicators ? '1000px' : '600px';
                
                // Render chart
                const config = {
                    responsive: true,
                    displayModeBar: true,
                    displaylogo: false,
                    modeBarButtonsToRemove: ['lasso2d', 'select2d']
                };
                
                Plotly.newPlot('chart', result.chart.data, result.chart.layout, config);
                
                // Update stats
                if (result.stats) {
                    updateStats(result.stats);
                }
                
                // Fetch and display indicators
                fetchIndicatorValues(symbol, period);
                
            } catch (error) {
                document.getElementById('chart').innerHTML = 
                    `<div id="loading">❌ Error: ${error.message}</div>`;
            }
        }
        
        async function fetchIndicatorValues(symbol, period) {
            try {
                const response = await fetch(`/api/stock/${symbol}?period=${period}`);
                const data = await response.json();
                
                if (data.indicators) {
                    displayIndicators(data.indicators);
                }
            } catch (error) {
                console.error('Error fetching indicators:', error);
            }
        }
        
        function displayIndicators(indicators) {
            const panel = document.getElementById('indicatorsPanel');
            const grid = document.getElementById('indicatorsGrid');
            
            if (!indicators || Object.keys(indicators).length === 0) {
                panel.style.display = 'none';
                return;
            }
            
            panel.style.display = 'block';
            grid.innerHTML = '';
            
            // Display latest values for key indicators
            const displayItems = [
                { name: 'RSI', key: 'rsi', format: (v) => v.toFixed(2) },
                { name: 'MACD', key: 'macd_line', format: (v) => v.toFixed(4) },
                { name: 'Signal', key: 'signal_line', format: (v) => v.toFixed(4) },
                { name: 'SMA 20', key: 'sma_20', format: (v) => '$' + v.toFixed(2) },
                { name: 'SMA 50', key: 'sma_50', format: (v) => '$' + v.toFixed(2) },
                { name: 'ATR', key: 'atr', format: (v) => v.toFixed(2) },
                { name: 'Stoch %K', key: 'stoch_k', format: (v) => v.toFixed(2) },
                { name: 'Stoch %D', key: 'stoch_d', format: (v) => v.toFixed(2) }
            ];
            
            displayItems.forEach(item => {
                if (indicators[item.key] && Array.isArray(indicators[item.key])) {
                    const values = indicators[item.key].filter(v => !isNaN(v));
                    if (values.length > 0) {
                        const latestValue = values[values.length - 1];
                        const div = document.createElement('div');
                        div.className = 'indicator-item';
                        div.innerHTML = `
                            <div class="indicator-name">${item.name}</div>
                            <div class="indicator-value">${item.format(latestValue)}</div>
                        `;
                        grid.appendChild(div);
                    }
                }
            });
        }
        
        function updateStats(stats) {
            const changeClass = stats.price_change >= 0 ? 'positive' : 'negative';
            const changeSymbol = stats.price_change >= 0 ? '▲' : '▼';
            
            document.getElementById('statsContainer').innerHTML = `
                <div class="stat-card">
                    <div class="stat-label">Current Price</div>
                    <div class="stat-value">$${stats.current_price.toFixed(2)}</div>
                    <div class="stat-change ${changeClass}">
                        ${changeSymbol} $${Math.abs(stats.price_change).toFixed(2)} 
                        (${stats.price_change_pct >= 0 ? '+' : ''}${stats.price_change_pct.toFixed(2)}%)
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Price Range</div>
                    <div class="stat-value">$${stats.min_price.toFixed(2)} - $${stats.max_price.toFixed(2)}</div>
                    <div class="stat-change" style="color: #666;">
                        Period: ${stats.period.toUpperCase()}
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Data Points</div>
                    <div class="stat-value">${stats.data_points}</div>
                    <div class="stat-change" style="color: #666;">
                        Chart: ${stats.chart_type}
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Data Source</div>
                    <div class="stat-value" style="font-size: 18px;">${stats.data_source}</div>
                    <div class="stat-change" style="color: #666;">
                        Symbol: ${stats.symbol}
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Last Updated</div>
                    <div class="stat-value" style="font-size: 16px;">${stats.last_updated}</div>
                    <div class="stat-change" style="color: #666;">
                        Live Data
                    </div>
                </div>
            `;
        }
        
        function autoRefresh() {
            const btn = document.getElementById('autoRefreshBtn');
            
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
                autoRefreshInterval = null;
                btn.textContent = '⏰ Auto Refresh: OFF';
                btn.style.background = '';
            } else {
                autoRefreshInterval = setInterval(() => {
                    loadChart();
                }, 30000);
                btn.textContent = '⏰ Auto Refresh: ON';
                btn.style.background = 'linear-gradient(135deg, #4CAF50, #45a049)';
                alert('Auto-refresh enabled: Chart will update every 30 seconds');
            }
        }
        
        // Load initial chart
        window.addEventListener('load', () => {
            setTimeout(() => {
                loadChart();
            }, 500);
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                loadChart();
            }
        });
    </script>
</body>
</html>
    '''
    return render_template_string(html)

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests"""
    return '', 204

if __name__ == '__main__':
    print("=" * 70)
    print("STOCK ANALYSIS SYSTEM - COMPLETE EDITION")
    print("=" * 70)
    print("Features:")
    print("✅ Yahoo Finance with Alpha Vantage fallback")
    print("✅ Alpha Vantage API Key: Integrated")
    print("✅ 12 Technical Indicators")
    print("✅ Professional candlestick/line/area charts")
    print("✅ Australian stocks auto-detection")
    print("✅ Intraday and historical data")
    print("✅ Real-time auto-refresh capability")
    print("=" * 70)
    print("Starting server at: http://localhost:8000")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=8000, debug=False)