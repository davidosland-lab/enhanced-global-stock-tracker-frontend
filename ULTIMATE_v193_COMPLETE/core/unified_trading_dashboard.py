"""
Unified Paper Trading Dashboard
================================

Combined paper trading system with integrated dashboard and stock selection.

Features:
- Interactive stock selection via web interface
- Real-time paper trading with ML signals
- Live dashboard with portfolio tracking
- All-in-one: no need for separate terminals
- Easy stock selection: choose from UI or command line

Usage:
    python unified_trading_dashboard.py
    
    Or with pre-selected stocks:
    python unified_trading_dashboard.py --symbols RIO.AX,CBA.AX,BHP.AX --capital 100000
    
    Then open browser: http://localhost:8050
"""

# ============================================================================
# CRITICAL: Set offline mode BEFORE any imports to prevent HuggingFace checks
# ============================================================================
import os
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN'] = '1'

import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objs as go
from datetime import datetime, timedelta
import json
from pathlib import Path
import pandas as pd
import numpy as np
import logging
import threading
import time
import sys
from typing import Dict, List, Optional
import yfinance as yf
import pytz

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Create required directories
Path('logs').mkdir(exist_ok=True)
Path('state').mkdir(exist_ok=True)
Path('config').mkdir(exist_ok=True)

# Configure logging with UTF-8 encoding (v193.11.1: Fix UnicodeEncodeError on Windows)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/unified_trading.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import paper trading coordinator
try:
    from paper_trading_coordinator import PaperTradingCoordinator
    PAPER_TRADING_AVAILABLE = True
except ImportError as e:
    logger.error(f"Could not import PaperTradingCoordinator: {e}")
    PAPER_TRADING_AVAILABLE = False

# Import pipeline report loader (NEW v1.3.15.164)
try:
    from pipeline_report_loader import auto_load_pipeline_stocks
    PIPELINE_LOADER_AVAILABLE = True
    logger.info("[LOADER] Pipeline report loader available")
except ImportError as e:
    logger.warning(f"Could not import pipeline_report_loader: {e}")
    PIPELINE_LOADER_AVAILABLE = False

# Import market calendar
try:
    from ml_pipeline.market_calendar import MarketCalendar, Exchange, MarketStatus
    MARKET_CALENDAR_AVAILABLE = True
    market_calendar = MarketCalendar()
    logger.info("[CALENDAR] Market calendar initialized")
except ImportError as e:
    logger.error(f"Could not import MarketCalendar: {e}")
    MARKET_CALENDAR_AVAILABLE = False
    market_calendar = None

# Global trading system instance
trading_system = None
trading_thread = None
is_trading = False

# Global sentiment analyzer instance (v193.3: Cache to prevent repeated FinBERT initialization)
_sentiment_analyzer = None
_sentiment_analyzer_lock = threading.Lock()

# Initialize Dash app
app = dash.Dash(__name__, 
                meta_tags=[
                    {'http-equiv': 'Cache-Control', 'content': 'no-cache, no-store, must-revalidate'},
                    {'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'}
                ])
app.title = 'Unified Paper Trading Dashboard v1.3.3'

# Default stock options
STOCK_PRESETS = {
    'ASX Blue Chips': 'CBA.AX,BHP.AX,RIO.AX,WOW.AX,CSL.AX',
    'ASX Mining': 'RIO.AX,BHP.AX,FMG.AX,NCM.AX,S32.AX',
    'ASX Banks': 'CBA.AX,NAB.AX,WBC.AX,ANZ.AX',
    'US Tech Giants': 'AAPL,MSFT,GOOGL,NVDA,TSLA',
    'US Blue Chips': 'AAPL,JPM,JNJ,WMT,XOM',
    'US Growth': 'TSLA,NVDA,AMD,PLTR,SQ',
    'Global Mix': 'AAPL,MSFT,CBA.AX,BHP.AX,HSBA.L',
    'Custom': ''
}

# v193.3: Helper function to get cached sentiment analyzer
def get_sentiment_analyzer():
    """
    Get or create cached sentiment analyzer instance
    
    v193.3 FIX: Prevents repeated FinBERT initialization every 5 seconds
    Returns cached instance instead of creating new one
    """
    global _sentiment_analyzer
    
    # Double-checked locking pattern for thread safety
    if _sentiment_analyzer is None:
        with _sentiment_analyzer_lock:
            if _sentiment_analyzer is None:
                try:
                    # Import here to avoid circular imports
                    from core.sentiment_integration import IntegratedSentimentAnalyzer
                    logger.info("[DASHBOARD v193.3] Initializing cached sentiment analyzer...")
                    _sentiment_analyzer = IntegratedSentimentAnalyzer()
                    logger.info("[DASHBOARD v193.3] Cached sentiment analyzer initialized successfully")
                except Exception as e:
                    logger.error(f"[DASHBOARD v193.3] Failed to initialize sentiment analyzer: {e}")
                    return None
    
    return _sentiment_analyzer

# Create market status panel

def _load_gap_predictions():
    """
    Load gap predictions from overnight pipeline reports
    
    Returns:
        Dict with market -> gap_prediction data
    """
    predictions = {}
    report_base = Path(__file__).parent.parent / 'reports' / 'screening'
    
    for market in ['au', 'uk', 'us']:
        report_path = report_base / f'{market}_morning_report.json'
        
        if report_path.exists():
            try:
                with open(report_path, 'r') as f:
                    report = json.load(f)
                
                # Extract gap prediction from market_sentiment
                market_sentiment = report.get('market_sentiment', {})
                gap_prediction = market_sentiment.get('gap_prediction', {})
                
                if gap_prediction and 'predicted_gap_pct' in gap_prediction:
                    predictions[market] = {
                        'predicted_gap_pct': gap_prediction['predicted_gap_pct'],
                        'confidence': gap_prediction.get('confidence', 0),
                        'direction': gap_prediction.get('direction', 'NEUTRAL'),
                        'available': True
                    }
                    logger.debug(f"[DASHBOARD] Loaded {market.upper()} gap: {gap_prediction['predicted_gap_pct']:+.2f}%")
            except Exception as e:
                logger.debug(f"[DASHBOARD] Error loading {market.upper()} gap prediction: {e}")
    
    return predictions

def create_market_status_panel():
    """Create market status panel showing exchange hours, holidays, and gap predictions"""
    if not MARKET_CALENDAR_AVAILABLE or market_calendar is None:
        return html.Div()  # Return empty if calendar not available
    
    # Get status for all exchanges
    asx_info = market_calendar.get_market_status(Exchange.ASX)
    nyse_info = market_calendar.get_market_status(Exchange.NYSE)
    lse_info = market_calendar.get_market_status(Exchange.LSE)
    
    # Load gap predictions from morning reports
    gap_predictions = _load_gap_predictions()
    
    def format_status_card(info, gap_data=None):
        """Format individual exchange status card with gap prediction"""
        # Determine status color and icon
        if info.status == MarketStatus.OPEN:
            status_color = '#4CAF50'
            status_icon = '🟢'
            status_text = 'OPEN'
        elif info.status == MarketStatus.HOLIDAY:
            status_color = '#FF9800'
            status_icon = '🏖️'
            status_text = f'HOLIDAY - {info.holiday_name}'
        elif info.status == MarketStatus.WEEKEND:
            status_color = '#9E9E9E'
            status_icon = '📅'
            status_text = 'WEEKEND'
        elif info.status == MarketStatus.PRE_MARKET:
            status_color = '#2196F3'
            status_icon = '🔵'
            status_text = 'PRE-MARKET'
        elif info.status == MarketStatus.POST_MARKET:
            status_color = '#FF9800'
            status_icon = '🟡'
            status_text = 'POST-MARKET'
        else:
            status_color = '#F44336'
            status_icon = '🔴'
            status_text = 'CLOSED'
        
        # Format time information
        local_time_str = info.current_time.strftime('%H:%M %Z')
        
        # Calculate time to next event
        time_info = ""
        if info.status == MarketStatus.OPEN and info.time_to_close:
            hours = int(info.time_to_close.total_seconds() // 3600)
            minutes = int((info.time_to_close.total_seconds() % 3600) // 60)
            time_info = f"Closes in {hours}h {minutes}m"
        elif info.time_to_open:
            total_seconds = info.time_to_open.total_seconds()
            if total_seconds >= 86400:  # More than 24 hours
                days = int(total_seconds // 86400)
                hours = int((total_seconds % 86400) // 3600)
                time_info = f"Opens in {days}d {hours}h"
            else:
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                time_info = f"Opens in {hours}h {minutes}m"
        
        # Build gap prediction section if available
        gap_section = []
        if gap_data and gap_data.get('available', False):
            gap_pct = gap_data['predicted_gap_pct']
            confidence = gap_data.get('confidence', 0) * 100  # Convert to percentage
            direction = gap_data.get('direction', 'NEUTRAL')
            
            # Determine gap color and icon
            if gap_pct > 0.5:
                gap_color = '#4CAF50'  # Green for bullish
                gap_icon = '📈'
            elif gap_pct < -0.5:
                gap_color = '#F44336'  # Red for bearish
                gap_icon = '📉'
            else:
                gap_color = '#FF9800'  # Orange for neutral
                gap_icon = '➡️'
            
            gap_section = [
                html.Div([
                    html.Span(gap_icon, style={'marginRight': '5px'}),
                    html.Span(f"Gap: {gap_pct:+.2f}%", 
                             style={'color': gap_color, 'fontWeight': 'bold', 'fontSize': '13px'})
                ], style={'marginTop': '8px', 'marginBottom': '3px'}),
                html.P(f"{direction} • {confidence:.0f}% confidence", 
                      style={'color': '#888', 'fontSize': '10px', 'margin': '0'})
            ]
        
        return html.Div([
            html.Div([
                html.H4(info.exchange.value, 
                       style={'color': '#ffffff', 'margin': '0 0 5px 0', 'fontSize': '16px'}),
                html.Div([
                    html.Span(status_icon, style={'marginRight': '5px'}),
                    html.Span(status_text, 
                             style={'color': status_color, 'fontWeight': 'bold', 'fontSize': '14px'})
                ], style={'marginBottom': '5px'}),
                html.P(local_time_str, 
                      style={'color': '#ccc', 'fontSize': '12px', 'margin': '3px 0'}),
                html.P(time_info if time_info else '  ', 
                      style={'color': '#888', 'fontSize': '11px', 'margin': '3px 0', 'minHeight': '15px'}),
                *gap_section  # Add gap prediction if available
            ])
        ], style={
            'backgroundColor': '#1e1e1e',
            'padding': '15px',
            'borderRadius': '8px',
            'border': f'2px solid {status_color}',
            'flex': '1',
            'minWidth': '180px'
        })
    
    return html.Div([
        html.Div([
            html.H3('🕐 Market Hours & Gap Predictions', 
                   style={'color': '#2196F3', 'margin': '0 0 15px 0', 'fontSize': '18px'}),
            html.Div([
                format_status_card(asx_info, gap_predictions.get('au')),
                format_status_card(nyse_info, gap_predictions.get('us')),
                format_status_card(lse_info, gap_predictions.get('uk'))
            ], style={
                'display': 'flex',
                'gap': '15px',
                'flexWrap': 'wrap'
            })
        ])
    ], style={
        'backgroundColor': '#2a2a2a',
        'padding': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.2)'
    })

def create_ml_signals_panel(state):
    """Create ML signals and decisions panel"""
    
    # Get ML signals from state if available
    ml_signals = state.get('ml_signals', {})
    active_positions = state.get('positions', {}).get('open', [])
    latest_decisions = state.get('latest_decisions', [])
    
    # ML Component weights
    ml_components = [
        {'name': 'FinBERT Sentiment', 'weight': 25, 'color': '#2196F3'},
        {'name': 'LSTM Prediction', 'weight': 25, 'color': '#4CAF50'},
        {'name': 'Technical Analysis', 'weight': 25, 'color': '#FF9800'},
        {'name': 'Momentum', 'weight': 15, 'color': '#9C27B0'},
        {'name': 'Volume Analysis', 'weight': 10, 'color': '#F44336'}
    ]
    
    # Build component cards
    component_cards = []
    for comp in ml_components:
        # Get signal value from state (if available)
        signal_value = ml_signals.get(comp['name'].lower().replace(' ', '_'), 0)
        signal_status = "🟢 BULLISH" if signal_value > 0.5 else "🔴 BEARISH" if signal_value < -0.5 else "⚪ NEUTRAL"
        signal_color = '#4CAF50' if signal_value > 0.5 else '#F44336' if signal_value < -0.5 else '#888'
        
        component_cards.append(
            html.Div([
                html.Div([
                    html.Span(comp['name'], style={'fontWeight': 'bold', 'fontSize': '14px'}),
                    html.Span(f" {comp['weight']}%", style={'color': '#888', 'fontSize': '12px', 'marginLeft': '5px'})
                ]),
                html.Div([
                    html.Span(signal_status, style={'color': signal_color, 'fontSize': '13px', 'fontWeight': 'bold'}),
                    html.Span(f" ({signal_value:+.2f})" if signal_value != 0 else " (--)", 
                             style={'color': '#666', 'fontSize': '11px', 'marginLeft': '5px'})
                ], style={'marginTop': '5px'}),
                # Progress bar
                html.Div([
                    html.Div(style={
                        'width': f'{comp["weight"]}%',
                        'height': '4px',
                        'backgroundColor': comp['color'],
                        'borderRadius': '2px',
                        'marginTop': '8px'
                    })
                ], style={
                    'width': '100%',
                    'height': '4px',
                    'backgroundColor': '#1e1e1e',
                    'borderRadius': '2px'
                })
            ], style={
                'backgroundColor': '#2a2a2a',
                'padding': '12px',
                'borderRadius': '8px',
                'border': f'1px solid {comp["color"]}',
                'flex': '1',
                'minWidth': '150px'
            })
        )
    
    # Latest Decisions section
    decisions_content = []
    if latest_decisions:
        for decision in latest_decisions[-5:]:  # Show last 5 decisions
            action = decision.get('action', 'HOLD')
            symbol = decision.get('symbol', 'N/A')
            confidence = decision.get('confidence', 0)
            reason = decision.get('reason', 'Monitoring market conditions')
            timestamp = decision.get('timestamp', '')
            
            action_color = '#4CAF50' if action == 'BUY' else '#F44336' if action == 'SELL' else '#2196F3'
            action_icon = '[UP]' if action == 'BUY' else '[DN]' if action == 'SELL' else '⏸️'
            
            decisions_content.append(
                html.Div([
                    html.Div([
                        html.Span(action_icon, style={'marginRight': '8px'}),
                        html.Span(action, style={'color': action_color, 'fontWeight': 'bold', 'fontSize': '14px'}),
                        html.Span(f" {symbol}", style={'color': '#fff', 'marginLeft': '8px', 'fontSize': '14px'}),
                        html.Span(f" {confidence:.0f}%", style={'color': '#888', 'fontSize': '12px', 'marginLeft': '8px'})
                    ]),
                    html.Div(reason, style={'color': '#aaa', 'fontSize': '11px', 'marginTop': '4px'}),
                    html.Div(timestamp, style={'color': '#666', 'fontSize': '10px', 'marginTop': '2px'})
                ], style={
                    'backgroundColor': '#1e1e1e',
                    'padding': '10px',
                    'borderRadius': '6px',
                    'marginBottom': '8px',
                    'borderLeft': f'3px solid {action_color}'
                })
            )
    else:
        decisions_content = [
            html.Div([
                html.P('🤖 Monitoring markets...', style={'color': '#888', 'textAlign': 'center', 'margin': '20px 0'}),
                html.P('Waiting for trading signals', style={'color': '#666', 'textAlign': 'center', 'fontSize': '12px', 'margin': '0'})
            ])
        ]
    
    return html.Div([
        html.Div([
            html.H3('🤖 ML Analysis & Trading Decisions', 
                   style={'color': '#4CAF50', 'margin': '0 0 15px 0', 'fontSize': '18px'}),
            
            # ML Components Grid
            html.Div([
                html.H4('Component Signals', style={'color': '#fff', 'fontSize': '14px', 'marginBottom': '10px'}),
                html.Div(component_cards, style={
                    'display': 'flex',
                    'gap': '10px',
                    'flexWrap': 'wrap'
                })
            ], style={'marginBottom': '20px'}),
            
            # Latest Decisions
            html.Div([
                html.H4('Recent Trading Decisions', style={'color': '#fff', 'fontSize': '14px', 'marginBottom': '10px'}),
                html.Div(decisions_content, style={
                    'maxHeight': '300px',
                    'overflowY': 'auto'
                })
            ])
        ], style={
            'backgroundColor': '#1a1a1a',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)'
        })
    ])

def create_market_performance_chart(state):
    """Create intraday performance chart for major indices (market hours only, GMT timezone)"""
    
    from datetime import datetime, timedelta
    
    # Check if we're in weekend (Saturday/Sunday)
    # After US market closes on Friday (21:00 GMT Friday) until AU market opens Monday (23:00 GMT Sunday)
    gmt = pytz.timezone('GMT')
    current_time_gmt = datetime.now(gmt)
    current_weekday = current_time_gmt.weekday()  # Monday=0, Sunday=6
    current_hour = current_time_gmt.hour
    
    # Weekend period: Friday after 21:00 GMT until Sunday after 23:00 GMT
    is_weekend = (
        (current_weekday == 4 and current_hour >= 21) or  # Friday after 21:00 GMT
        (current_weekday == 5) or  # All day Saturday
        (current_weekday == 6 and current_hour < 23)  # Sunday before 23:00 GMT
    )
    
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
    
    try:
        for symbol, info in indices.items():
            try:
                # Fetch 5 days of data to ensure we have previous trading day (covers weekends/holidays)
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='5d', interval='15m')
                
                if len(hist) > 0:
                    # Convert index to GMT timezone
                    hist.index = hist.index.tz_convert(gmt)
                    
                    # FIX v1.3.15.116: Use 24-hour rolling window instead of single date filter
                    # This ensures the chart always shows last 24 hours of trading data
                    from datetime import timedelta
                    now_gmt = datetime.now(gmt)
                    cutoff_time = now_gmt - timedelta(hours=24)
                    
                    # Filter to last 24 hours of data
                    hist_24h = hist[hist.index >= cutoff_time]
                    
                    # For logging: get the date range being displayed
                    if len(hist_24h) > 0:
                        start_date = hist_24h.index[0].date()
                        end_date = hist_24h.index[-1].date()
                        date_range = f"{start_date} to {end_date}" if start_date != end_date else str(start_date)
                    else:
                        date_range = "No data"
                    
                    # Apply market hours filter to 24h window
                    market_open_hour = info['market_open']
                    market_close_hour = info['market_close']
                    spans_midnight = info.get('spans_midnight', False)
                    
                    # Create market hours filter (apply to any day in 24h window)
                    if spans_midnight:
                        # For markets that span midnight (e.g., ASX: 23:00 to 05:00)
                        # Include hours >= market_open (23:00+) OR hours <= market_close (00:00-05:00)
                        mask = (
                            (hist_24h.index.hour >= market_open_hour) |
                            (hist_24h.index.hour <= market_close_hour)
                        )
                    else:
                        # Normal market hours within single day
                        mask = (
                            (hist_24h.index.hour >= market_open_hour) &
                            (hist_24h.index.hour <= market_close_hour)
                        )
                    
                    market_hours_data = hist_24h[mask]
                    
                    # FIX v1.3.15.116: Updated logging to show 24-hour window
                    logger.info(f"[MARKET CHART] {symbol} ({info['name']}): "
                               f"Total data points: {len(hist)}, "
                               f"24h window data: {len(hist_24h)}, "
                               f"Market hours data: {len(market_hours_data)}, "
                               f"Date range: {date_range}, "
                               f"Spans midnight: {spans_midnight}")
                    
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
                        # FIX v1.3.15.117: Break line at day boundaries to prevent connecting across days
                        pct_changes = []
                        times = []
                        
                        # Track previous timestamp to detect gaps
                        prev_timestamp = None
                        gap_threshold_hours = 4  # Consider it a new day if gap > 4 hours
                        
                        for idx, row in market_hours_data.iterrows():
                            pct_change = ((row['Close'] - previous_close) / previous_close) * 100
                            
                            # Check if there's a large time gap (day boundary)
                            if prev_timestamp is not None:
                                time_gap = (idx - prev_timestamp).total_seconds() / 3600  # hours
                                if time_gap > gap_threshold_hours:
                                    # Insert None to break the line
                                    pct_changes.append(None)
                                    times.append(idx)
                            
                            pct_changes.append(pct_change)
                            times.append(idx)
                            prev_timestamp = idx
                        
                        # FIX v1.3.15.117: Enhanced logging for chart debugging
                        non_none_points = len([x for x in pct_changes if x is not None])
                        logger.info(f"[MARKET CHART] {symbol}: Adding trace with {non_none_points} points, "
                                   f"pct_change range: {min([x for x in pct_changes if x is not None]):.2f}% to {max([x for x in pct_changes if x is not None]):.2f}%")
                        
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
                            connectgaps=False,  # FIX v1.3.15.117: Don't connect across None values
                            hovertemplate=(
                                f"<b>{info['name']}</b><br>"
                                "Time (GMT): %{x|%H:%M}<br>"
                                "Change from Prev Close: %{y:.2f}%<br>"
                                "<extra></extra>"
                            )
                        ))
                    else:
                        logger.warning(f"[MARKET CHART] {symbol}: No market hours data to plot")
                    
            except Exception as e:
                logger.warning(f"Could not fetch data for {symbol}: {e}")
    
    except Exception as e:
        logger.error(f"Error creating market performance chart: {e}")
    
    # Calculate x-axis range to show only 24-hour period
    # Find the earliest and latest timestamps from all traces
    all_times = []
    for trace in fig.data:
        if hasattr(trace, 'x') and len(trace.x) > 0:
            all_times.extend(trace.x)
    
    # Set x-axis range if we have data
    xaxis_range = None
    if all_times:
        from datetime import datetime, timedelta
        import pandas as pd
        
        # Convert to datetime if needed
        if all_times:
            min_time = min(all_times)
            max_time = max(all_times)
            
            # Ensure we're showing exactly 24 hours
            # Round min_time down to nearest hour
            if isinstance(min_time, pd.Timestamp):
                min_time = min_time.replace(minute=0, second=0, microsecond=0)
                # Add 24 hours from start for max range
                range_end = min_time + timedelta(hours=24)
                # Use the actual max_time if it's less than 24 hours from start
                if max_time < range_end:
                    range_end = max_time + timedelta(minutes=30)  # Add small buffer
                xaxis_range = [min_time, range_end]
    
    # Create title with weekend indicator
    chart_title = None
    if is_weekend:
        chart_title = {
            'text': '24-Hour Market Performance (Last Trading Day - Markets Closed)',
            'font': {'size': 12, 'color': '#FF9800'},
            'x': 0.5,
            'xanchor': 'center'
        }
    
    # Update layout with GMT timezone
    fig.update_layout(
        plot_bgcolor='#1e1e1e',
        paper_bgcolor='#1e1e1e',
        font={'color': '#ffffff', 'size': 11},
        title=chart_title,
        xaxis={
            'showgrid': False,
            'showline': True,
            'linecolor': '#444',
            'tickfont': {'size': 10, 'color': '#999'},
            'tickformat': '%H:%M',  # 24-hour format for GMT
            'dtick': 3600000,  # Tick every hour (in milliseconds)
            'title': {
                'text': 'Time (GMT) - 24 Hour Period',
                'font': {'size': 10, 'color': '#666'}
            },
            'range': xaxis_range,  # Set explicit range to prevent extension
            'fixedrange': True  # Prevent zoom/pan that would extend axis
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
            'side': 'right',
            'fixedrange': True  # Prevent zoom/pan
        },
        height=280,
        width=None,
        autosize=True,
        margin={'l': 20, 'r': 50, 't': 40, 'b': 50},
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

# Load state function
def load_state():
    """Load current trading state with validation (STATE_VALIDATION_v85)"""
    state_file = 'state/paper_trading_state.json'
    
    try:
        if Path(state_file).exists():
            # Check if file is empty
            if Path(state_file).stat().st_size == 0:
                logger.warning("[STATE] State file is empty, using default")
                return get_default_state()
            
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            # Validate state structure
            required_keys = ['capital', 'positions', 'performance', 'market']
            if all(key in state for key in required_keys):
                logger.debug(f"[STATE] Loaded valid state ({Path(state_file).stat().st_size} bytes)")
                return state
            else:
                logger.warning("[STATE] Invalid state structure, using default")
                return get_default_state()
                
    except json.JSONDecodeError as e:
        logger.error(f"[STATE] JSON decode error: {e}, using default")
    except Exception as e:
        logger.error(f"[STATE] Error loading state: {e}, using default")
    
    # Return default empty state
    return get_default_state()

def get_default_state():
    """Get default state structure (STATE_VALIDATION_v85)"""
    return {
        'timestamp': datetime.now().isoformat(),
        'symbols': [],
        'capital': {
            'total': 0,
            'cash': 0,
            'invested': 0,
            'initial': 0,
            'total_return_pct': 0
        },
        'positions': {
            'count': 0,
            'open': [],
            'unrealized_pnl': 0
        },
        'performance': {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'realized_pnl': 0,
            'max_drawdown': 0
        },
        'market': {
            'sentiment': 50,
            'sentiment_class': 'neutral'
        },
        'intraday_alerts': [],
        'closed_trades': []
    }

# Mobile responsive CSS
MOBILE_CSS = """
/* Mobile Responsive CSS for Trading Dashboard */
@media only screen and (max-width: 768px) {
    /* Make containers stack vertically */
    body {
        font-size: 14px !important;
    }
    
    /* Adjust font sizes for mobile */
    h1 { font-size: 24px !important; }
    h2 { font-size: 20px !important; }
    h3 { font-size: 18px !important; }
    h4 { font-size: 16px !important; }
    
    /* Make charts responsive */
    .js-plotly-plot {
        width: 100% !important;
        height: auto !important;
        min-height: 250px !important;
    }
    
    /* Stack elements vertically */
    div[style*="display: flex"] {
        flex-direction: column !important;
    }
    
    /* Adjust padding for mobile */
    div[style*="padding: 20px"] {
        padding: 10px !important;
    }
    
    /* Make buttons full width on mobile */
    button {
        width: 100% !important;
        margin: 5px 0 !important;
        padding: 12px !important;
        min-height: 44px !important;
    }
    
    /* Make input fields full width */
    input, select, textarea {
        width: 100% !important;
        box-sizing: border-box !important;
        font-size: 16px !important; /* Prevent zoom on iOS */
    }
    
    /* Improve table readability */
    table {
        font-size: 12px !important;
        display: block !important;
        overflow-x: auto !important;
    }
    
    /* Improve touch targets */
    a, button, input[type="button"], input[type="submit"] {
        min-height: 44px !important;
        min-width: 44px !important;
    }
    
    /* Market status cards */
    div[style*="minWidth: 180px"] {
        min-width: 100% !important;
        margin-bottom: 10px !important;
    }
}

/* Tablet adjustments */
@media only screen and (min-width: 769px) and (max-width: 1024px) {
    .js-plotly-plot {
        min-height: 350px !important;
    }
    
    h1 { font-size: 28px !important; }
}

/* Prevent text selection on double-tap (mobile) */
.no-select {
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
}
"""

# Inject mobile CSS into app
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
''' + MOBILE_CSS + '''
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# App Layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1('[UP] Unified Paper Trading Dashboard', 
                style={'color': '#ffffff', 'margin': '0'}),
        html.P('All-in-One: Stock Selection + Paper Trading + Live Dashboard (v1.3.3)',
               style={'color': '#cccccc', 'margin': '5px 0 0 0'})
    ], style={
        'backgroundColor': '#1e1e1e',
        'padding': '20px',
        'marginBottom': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.2)'
    }),
    
    # Stock Selection Panel
    html.Div([
        html.Div([
            html.H3('[*] Select Stocks to Trade', style={'color': '#4CAF50', 'margin': '0 0 15px 0'}),
            
            # Preset dropdown
            html.Div([
                html.Label('Quick Presets:', style={'color': '#ffffff', 'display': 'block', 'marginBottom': '5px'}),
                dcc.Dropdown(
                    id='preset-dropdown',
                    options=[{'label': k, 'value': v} for k, v in STOCK_PRESETS.items()],
                    value='',
                    placeholder='Select a preset or enter custom symbols',
                    style={'width': '100%', 'marginBottom': '15px'}
                )
            ]),
            
            # Stock symbols input
            html.Div([
                html.Label('Stock Symbols (comma-separated):', style={'color': '#ffffff', 'display': 'block', 'marginBottom': '5px'}),
                dcc.Input(
                    id='symbols-input',
                    type='text',
                    placeholder='e.g., RIO.AX,CBA.AX,BHP.AX',
                    style={'width': '100%', 'padding': '10px', 'fontSize': '14px', 'marginBottom': '10px'},
                    value=''
                ),
                # NEW v1.3.15.164: Auto-load button
                html.Button(
                    '[LOAD] Auto-Load Top 50 from Pipeline Reports',
                    id='autoload-btn',
                    style={
                        'width': '100%',
                        'padding': '10px',
                        'fontSize': '14px',
                        'backgroundColor': '#2196F3',
                        'color': '#ffffff',
                        'border': 'none',
                        'borderRadius': '5px',
                        'cursor': 'pointer',
                        'marginBottom': '10px'
                    }
                ),
                html.Div(id='autoload-status', style={'fontSize': '12px', 'color': '#888', 'marginBottom': '10px'})
            ]),
            
            # Capital input
            html.Div([
                html.Label('Initial Capital ($):', style={'color': '#ffffff', 'display': 'block', 'marginBottom': '5px'}),
                dcc.Input(
                    id='capital-input',
                    type='number',
                    placeholder='100000',
                    value=100000,
                    style={'width': '100%', 'padding': '10px', 'fontSize': '14px', 'marginBottom': '15px'}
                )
            ]),
            
            
            # Trading Controls Panel (TRADING_CONTROLS_v86)
            html.Div([
                html.H4('⚙️ Trading Controls', style={'color': '#FFC107', 'margin': '0 0 15px 0'}),
                
                # Confidence Level Slider
                html.Div([
                    html.Label('Minimum Confidence Level:', style={'color': '#ffffff', 'display': 'block', 'marginBottom': '5px'}),
                    html.Div([
                        dcc.Slider(
                            id='confidence-slider',
                            min=45,
                            max=95,
                            step=5,
                            value=48,
                            marks={i: f'{i}%' for i in range(45, 100, 10)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                    ], style={'padding': '0 10px'}),
                    html.P(id='confidence-display', style={'color': '#888', 'fontSize': '12px', 'margin': '5px 0 0 0'})
                ], style={'marginBottom': '20px'}),
                
                # Stop Loss Input
                html.Div([
                    html.Label('Stop Loss (%):', style={'color': '#ffffff', 'display': 'block', 'marginBottom': '5px'}),
                    dcc.Input(
                        id='stop-loss-input',
                        type='number',
                        placeholder='10',
                        value=10,
                        min=1,
                        max=20,
                        step=1,
                        style={'width': '100%', 'padding': '8px', 'fontSize': '14px'}
                    ),
                    html.P('Set stop loss percentage (1-20%)', style={'color': '#888', 'fontSize': '11px', 'margin': '3px 0 0 0'})
                ], style={'marginBottom': '20px'}),
                
                # Force Trade Section (FIX v1.3.15.162: Add confidence and stop-loss inputs)
                html.Div([
                    html.Label('Force Trade:', style={'color': '#ffffff', 'display': 'block', 'marginBottom': '10px', 'fontSize': '14px', 'fontWeight': 'bold'}),
                    
                    # Symbol input
                    html.Div([
                        html.Label('Symbol:', style={'color': '#ffffff', 'fontSize': '12px', 'marginBottom': '5px', 'display': 'block'}),
                        dcc.Input(
                            id='force-trade-symbol',
                            type='text',
                            placeholder='e.g., AAPL, BP.L, BHP.AX',
                            style={'width': '100%', 'padding': '8px', 'fontSize': '13px', 'marginBottom': '10px', 
                                   'border': '1px solid #555', 'borderRadius': '4px', 'backgroundColor': '#2a2a2a', 'color': '#fff'}
                        ),
                    ]),
                    
                    # Confidence input (NEW)
                    html.Div([
                        html.Label('Confidence (%):', style={'color': '#ffffff', 'fontSize': '12px', 'marginBottom': '5px', 'display': 'block'}),
                        dcc.Input(
                            id='force-trade-confidence',
                            type='number',
                            placeholder='50-95',
                            value=70,
                            min=50,
                            max=95,
                            step=5,
                            style={'width': '100%', 'padding': '8px', 'fontSize': '13px', 'marginBottom': '10px',
                                   'border': '1px solid #555', 'borderRadius': '4px', 'backgroundColor': '#2a2a2a', 'color': '#fff'}
                        ),
                        html.P('Set confidence level (50-95%)', style={'color': '#888', 'fontSize': '11px', 'margin': '0 0 10px 0'})
                    ]),
                    
                    # Stop-loss input (NEW)
                    html.Div([
                        html.Label('Stop Loss (%):', style={'color': '#ffffff', 'fontSize': '12px', 'marginBottom': '5px', 'display': 'block'}),
                        dcc.Input(
                            id='force-trade-stop-loss',
                            type='number',
                            placeholder='-2 to -10',
                            value=-3,
                            min=-10,
                            max=-1,
                            step=0.5,
                            style={'width': '100%', 'padding': '8px', 'fontSize': '13px', 'marginBottom': '10px',
                                   'border': '1px solid #555', 'borderRadius': '4px', 'backgroundColor': '#2a2a2a', 'color': '#fff'}
                        ),
                        html.P('Set stop loss (-1% to -10%)', style={'color': '#888', 'fontSize': '11px', 'margin': '0 0 15px 0'})
                    ]),
                    
                    # Action buttons
                    html.Div([
                        html.Button('📈 Force BUY', id='force-buy-btn', n_clicks=0,
                                   style={'backgroundColor': '#4CAF50', 'color': 'white', 'padding': '10px 25px',
                                          'border': 'none', 'borderRadius': '5px', 'fontSize': '14px',
                                          'marginRight': '10px', 'cursor': 'pointer', 'fontWeight': 'bold'}),
                        html.Button('📉 Force SELL', id='force-sell-btn', n_clicks=0,
                                   style={'backgroundColor': '#F44336', 'color': 'white', 'padding': '10px 25px',
                                          'border': 'none', 'borderRadius': '5px', 'fontSize': '14px',
                                          'cursor': 'pointer', 'fontWeight': 'bold'})
                    ], style={'textAlign': 'center'}),
                    
                    # Status message
                    html.Div(id='force-trade-status', style={'color': '#FFC107', 'fontSize': '12px', 'marginTop': '15px', 
                                                             'padding': '10px', 'backgroundColor': '#1a1a1a', 'borderRadius': '4px',
                                                             'border': '1px solid #444', 'textAlign': 'center'})
                ], style={'marginBottom': '15px', 'padding': '20px', 'backgroundColor': '#1e1e1e', 'borderRadius': '8px', 'border': '2px solid #FFC107'}),
                
            ], style={'marginTop': '20px', 'padding': '20px', 'backgroundColor': '#252525', 'borderRadius': '8px', 'border': '1px solid #444'}),
            
            # Control buttons
            html.Div([
                html.Button('▶️ Start Trading', id='start-btn', n_clicks=0,
                           style={'backgroundColor': '#4CAF50', 'color': 'white', 'padding': '12px 30px',
                                  'border': 'none', 'borderRadius': '5px', 'fontSize': '16px',
                                  'marginRight': '10px', 'cursor': 'pointer'}),
                html.Button('⏸️ Stop Trading', id='stop-btn', n_clicks=0,
                           style={'backgroundColor': '#F44336', 'color': 'white', 'padding': '12px 30px',
                                  'border': 'none', 'borderRadius': '5px', 'fontSize': '16px',
                                  'cursor': 'pointer'})
            ], style={'marginTop': '10px'}),
            
            # Status message
            html.Div(id='status-message', 
                    style={'color': '#ffffff', 'marginTop': '15px', 'padding': '10px',
                           'backgroundColor': '#1e1e1e', 'borderRadius': '5px'})
            
        ], style={'flex': '1', 'marginRight': '20px'}),
        
        # 24-Hour Market Performance Chart
        html.Div([
            html.H3('[#] 24-Hour Market Performance', style={'color': '#2196F3', 'margin': '0 0 15px 0'}),
            dcc.Graph(
                id='market-performance-chart',
                config={
                    'displayModeBar': False,
                    'staticPlot': False,
                    'responsive': False
                },
                style={'width': '100%', 'height': '280px'}
            )
        ], style={'flex': '1', 'backgroundColor': '#1e1e1e', 'padding': '20px', 'borderRadius': '10px'})
        
    ], style={
        'backgroundColor': '#2a2a2a',
        'padding': '20px',
        'marginBottom': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
        'display': 'flex',
        'gap': '20px'
    }),
    
    # Auto-refresh
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # Update every 30 seconds (v193.3 - reduced to avoid Yahoo rate limiting)
        n_intervals=0
    ),
    
    # Current Trading Info
    html.Div(id='trading-info-panel', style={'marginBottom': '20px'}),
    
    # Market Status Panel
    html.Div(id='market-status-panel', style={'marginBottom': '20px'}),
    
    # ML Signals & Decisions Panel
    html.Div(id='ml-signals-panel', style={'marginBottom': '20px'}),
    
    # Top metrics row
    html.Div([
        # Total Capital
        html.Div([
            html.H3('Total Capital', style={'color': '#888', 'fontSize': '14px', 'margin': '0'}),
            html.H2(id='total-capital', style={'color': '#4CAF50', 'margin': '10px 0'}),
            html.P(id='total-return', style={'color': '#888', 'fontSize': '14px', 'margin': '0'})
        ], style={
            'backgroundColor': '#2a2a2a',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
            'flex': '1',
            'margin': '0 10px'
        }),
        
        # Open Positions
        html.Div([
            html.H3('Open Positions', style={'color': '#888', 'fontSize': '14px', 'margin': '0'}),
            html.H2(id='position-count', style={'color': '#2196F3', 'margin': '10px 0'}),
            html.P(id='unrealized-pnl', style={'color': '#888', 'fontSize': '14px', 'margin': '0'})
        ], style={
            'backgroundColor': '#2a2a2a',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
            'flex': '1',
            'margin': '0 10px'
        }),
        
        # Win Rate
        html.Div([
            html.H3('Win Rate', style={'color': '#888', 'fontSize': '14px', 'margin': '0'}),
            html.H2(id='win-rate', style={'color': '#FF9800', 'margin': '10px 0'}),
            html.P(id='total-trades', style={'color': '#888', 'fontSize': '14px', 'margin': '0'})
        ], style={
            'backgroundColor': '#2a2a2a',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
            'flex': '1',
            'margin': '0 10px'
        }),
        
        # Market Sentiment
        html.Div([
            html.H3('Market Sentiment', style={'color': '#888', 'fontSize': '14px', 'margin': '0'}),
            html.H2(id='market-sentiment', style={'color': '#9C27B0', 'margin': '10px 0'}),
            html.P(id='sentiment-class', style={'color': '#888', 'fontSize': '14px', 'margin': '0'})
        ], style={
            'backgroundColor': '#2a2a2a',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
            'flex': '1',
            'margin': '0 10px'
        })
    ], style={'display': 'flex', 'marginBottom': '20px'}),
    
    # FinBERT Sentiment Breakdown Panel
    html.Div([
        html.H3('FinBERT Sentiment Analysis', style={'color': '#ffffff', 'marginBottom': '15px'}),
        html.Div(id='finbert-sentiment-panel', style={'display': 'flex', 'justifyContent': 'space-around'}),
        html.Div(id='sentiment-gate-status', style={'marginTop': '15px', 'padding': '10px', 'borderRadius': '5px'})
    ], style={
        'backgroundColor': '#2a2a2a',
        'padding': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
        'marginBottom': '20px'
    }),
    
    # Charts and positions
    html.Div([
        # Portfolio chart
        html.Div([
            html.H3('Portfolio Value', style={'color': '#ffffff', 'marginBottom': '15px'}),
            dcc.Graph(
                id='portfolio-chart',
                config={
                    'displayModeBar': False,
                    'staticPlot': False,
                    'responsive': False
                },
                style={'width': '100%', 'height': '250px'}
            )
        ], style={
            'backgroundColor': '#2a2a2a',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
            'flex': '2',
            'margin': '0 10px',
            'minWidth': '500px',
            'maxWidth': '900px',
            'width': '66%'
        }),
        
        # Performance chart
        html.Div([
            html.H3('Performance', style={'color': '#ffffff', 'marginBottom': '15px'}),
            dcc.Graph(
                id='performance-chart',
                config={
                    'displayModeBar': False,
                    'staticPlot': False,
                    'responsive': False
                },
                style={'width': '100%', 'height': '250px'}
            )
        ], style={
            'backgroundColor': '#2a2a2a',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
            'flex': '1',
            'margin': '0 10px',
            'minWidth': '300px',
            'maxWidth': '450px',
            'width': '33%'
        })
    ], style={
        'display': 'flex', 
        'marginBottom': '20px',
        'width': '100%',
        'maxWidth': '1400px'
    }),
    
    # Positions list
    html.Div([
        html.H3('Open Positions', style={'color': '#ffffff', 'marginBottom': '15px'}),
        html.Div(id='positions-list')
    ], style={
        'backgroundColor': '#2a2a2a',
        'padding': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
        'marginBottom': '20px'
    }),
    
    # Tax Reports Panel
    html.Div([
        html.H3('[#] Tax Reports (ATO Compliant)', style={'color': '#ffffff', 'marginBottom': '15px'}),
        html.Div([
            # Financial Year Selector
            html.Div([
                html.Label('Financial Year:', style={'color': '#ffffff', 'display': 'block', 'marginBottom': '5px'}),
                dcc.Dropdown(
                    id='fy-dropdown',
                    options=[
                        {'label': 'FY 2024-25', 'value': '2024-25'},
                        {'label': 'FY 2025-26', 'value': '2025-26'},
                        {'label': 'FY 2026-27', 'value': '2026-27'},
                        {'label': 'Current FY', 'value': 'current'}
                    ],
                    value='current',
                    style={'width': '200px', 'marginBottom': '15px'}
                )
            ], style={'marginRight': '20px'}),
            
            # Generate Buttons
            html.Div([
                html.Button('📄 Generate ATO Report', id='generate-ato-btn', n_clicks=0,
                           style={'backgroundColor': '#2196F3', 'color': 'white', 'padding': '10px 20px',
                                  'border': 'none', 'borderRadius': '5px', 'fontSize': '14px',
                                  'marginRight': '10px', 'cursor': 'pointer'}),
                html.Button('💾 Export CSV', id='export-csv-btn', n_clicks=0,
                           style={'backgroundColor': '#4CAF50', 'color': 'white', 'padding': '10px 20px',
                                  'border': 'none', 'borderRadius': '5px', 'fontSize': '14px',
                                  'cursor': 'pointer'})
            ], style={'display': 'flex'}),
        ], style={'display': 'flex', 'alignItems': 'flex-end', 'marginBottom': '15px'}),
        
        # Tax Summary Display
        html.Div(id='tax-summary', style={'color': '#ffffff', 'padding': '15px', 
                                          'backgroundColor': '#1e1e1e', 'borderRadius': '5px',
                                          'marginTop': '15px'}),
        
        # Report Status
        html.Div(id='tax-report-status', style={'color': '#4CAF50', 'marginTop': '10px'})
        
    ], style={
        'backgroundColor': '#2a2a2a',
        'padding': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
        'marginBottom': '20px'
    }),
    
    # Footer
    html.Div([
        html.P(id='last-update', style={'color': '#888', 'textAlign': 'center', 'margin': '0'})
    ], style={
        'backgroundColor': '#1e1e1e',
        'padding': '15px',
        'borderRadius': '10px'
    })
    
], style={
    'backgroundColor': '#121212',
    'minHeight': '100vh',
    'padding': '20px',
    'fontFamily': 'Arial, sans-serif'
})

# Callbacks

# Update symbols input when preset selected
@app.callback(
    Output('symbols-input', 'value'),
    Input('preset-dropdown', 'value'),
    prevent_initial_call=True
)
def update_symbols_from_preset(preset_value):
    """Update symbols input when preset is selected"""
    if preset_value:
        return preset_value
    return ''

# NEW v1.3.15.164: Auto-load top stocks from pipeline reports
@app.callback(
    [Output('symbols-input', 'value', allow_duplicate=True),
     Output('autoload-status', 'children')],
    Input('autoload-btn', 'n_clicks'),
    prevent_initial_call=True
)
def autoload_pipeline_stocks(n_clicks):
    """
    Auto-load top 50 stocks from latest pipeline reports
    
    Loads stocks from AU/UK/US morning reports and populates
    the symbols input field with the top opportunities.
    """
    if not PIPELINE_LOADER_AVAILABLE:
        return '', html.Div(
            '[!] Pipeline loader not available',
            style={'color': '#FF9800'}
        )
    
    try:
        logger.info("[AUTOLOAD] Loading top 50 stocks from pipeline reports...")
        
        # Load top 50 stocks from all markets
        # Relaxed filters: confidence >= 20%, max age 168 hours (7 days)
        symbols, metadata = auto_load_pipeline_stocks(
            top_n=50,
            markets=['AU', 'UK', 'US'],
            min_confidence=20.0,
            max_age_hours=168
        )
        
        if not symbols:
            # No stocks found
            status_html = html.Div([
                html.Span('[!] No stocks loaded', style={'color': '#FF9800', 'fontWeight': 'bold'}),
                html.Br(),
                html.Span('Check if pipeline reports exist in reports/screening/', style={'fontSize': '11px'})
            ])
            return '', status_html
        
        # Create status message
        au_count = sum(1 for s in symbols if s.endswith('.AX'))
        uk_count = sum(1 for s in symbols if s.endswith('.L'))
        us_count = len(symbols) - au_count - uk_count
        
        status_html = html.Div([
            html.Span(f'[OK] Loaded {len(symbols)} stocks', style={'color': '#4CAF50', 'fontWeight': 'bold'}),
            html.Br(),
            html.Span(f'AU: {au_count}, UK: {uk_count}, US: {us_count}', style={'fontSize': '11px'})
        ])
        
        # Join symbols with commas
        symbols_str = ','.join(symbols)
        
        logger.info(f"[AUTOLOAD] Loaded {len(symbols)} stocks: AU={au_count}, UK={uk_count}, US={us_count}")
        
        return symbols_str, status_html
        
    except Exception as e:
        logger.error(f"[AUTOLOAD] Error: {e}")
        status_html = html.Div(
            f'[ERROR] Error: {str(e)[:100]}',
            style={'color': '#F44336'}
        )
        return '', status_html

# Start/Stop trading
@app.callback(
    Output('status-message', 'children'),
    [Input('start-btn', 'n_clicks'),
     Input('stop-btn', 'n_clicks')],
    [State('symbols-input', 'value'),
     State('capital-input', 'value'),
     State('confidence-slider', 'value'),
     State('stop-loss-input', 'value')],
    prevent_initial_call=True
)
def control_trading(start_clicks, stop_clicks, symbols_str, capital, min_confidence, stop_loss_pct):
    """Start or stop paper trading"""
    global trading_system, trading_thread, is_trading
    
    ctx = callback_context
    if not ctx.triggered:
        return "Ready to start"
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'start-btn':
        # Validation
        if not symbols_str or not symbols_str.strip():
            return html.Div("[ERROR] Please enter at least one stock symbol", 
                          style={'color': '#F44336'})
        
        if not capital or capital <= 0:
            return html.Div("[ERROR] Please enter a valid capital amount", 
                          style={'color': '#F44336'})
        
        # Parse symbols
        symbols = [s.strip().upper() for s in symbols_str.split(',') if s.strip()]
        
        if not symbols:
            return html.Div("[ERROR] No valid symbols found", 
                          style={'color': '#F44336'})
        
        # Stop existing trading if running
        if is_trading:
            is_trading = False
            if trading_thread and trading_thread.is_alive():
                trading_thread.join(timeout=2)
        
        # Create new trading system
        try:
            if not PAPER_TRADING_AVAILABLE:
                return html.Div("[ERROR] Paper trading module not available", 
                              style={'color': '#F44336'})
            
            trading_system = PaperTradingCoordinator(
                symbols=symbols,
                initial_capital=float(capital),
                use_real_swing_signals=True,
                min_confidence=min_confidence,      # FIX v1.3.15.160: Use UI slider
                default_stop_loss=stop_loss_pct    # FIX v1.3.15.160: Use UI input
            )
            
            # Start trading in background thread
            is_trading = True
            trading_thread = threading.Thread(
                target=run_trading_loop,
                args=(trading_system,),
                daemon=True
            )
            trading_thread.start()
            
            return html.Div([
                html.P("[OK] Trading Started!", style={'color': '#4CAF50', 'fontWeight': 'bold', 'margin': '0 0 5px 0'}),
                html.P(f"Symbols: {', '.join(symbols)}", style={'color': '#ffffff', 'margin': '0'}),
                html.P(f"Capital: ${capital:,.2f}", style={'color': '#ffffff', 'margin': '0'})
            ])
            
        except Exception as e:
            logger.error(f"Error starting trading: {e}")
            return html.Div(f"[ERROR] Starting trading: {str(e)}", 
                          style={'color': '#F44336'})
    
    elif button_id == 'stop-btn':
        if is_trading:
            is_trading = False
            if trading_thread and trading_thread.is_alive():
                trading_thread.join(timeout=2)
            
            return html.Div("⏸️ Trading Stopped", 
                          style={'color': '#FF9800', 'fontWeight': 'bold'})
        else:
            return html.Div("ℹ️ Trading is not running", 
                          style={'color': '#888'})
    
    return "Ready to start"

def run_trading_loop(system):
    """Run trading system in background"""
    global is_trading
    
    try:
        cycle = 0
        while is_trading:
            cycle += 1
            logger.info(f"[CYCLE] Trading cycle {cycle}")
            
            # Run one trading cycle
            system.run_single_cycle()
            
            # Save state
            system.save_state()
            
            # Wait before next cycle (60 seconds)
            for _ in range(60):
                if not is_trading:
                    break
                time.sleep(1)
                
    except Exception as e:
        logger.error(f"[ERROR] Error in trading loop: {e}")
        is_trading = False

# Update dashboard
@app.callback(
    [
        Output('trading-info-panel', 'children'),
        Output('market-status-panel', 'children'),
        Output('ml-signals-panel', 'children'),
        Output('market-performance-chart', 'figure'),
        Output('total-capital', 'children'),
        Output('total-return', 'children'),
        Output('position-count', 'children'),
        Output('unrealized-pnl', 'children'),
        Output('win-rate', 'children'),
        Output('total-trades', 'children'),
        Output('market-sentiment', 'children'),
        Output('sentiment-class', 'children'),
        Output('finbert-sentiment-panel', 'children'),
        Output('sentiment-gate-status', 'children'),
        Output('portfolio-chart', 'figure'),
        Output('performance-chart', 'figure'),
        Output('positions-list', 'children'),
        Output('last-update', 'children')
    ],
    Input('interval-component', 'n_intervals')
)
def update_dashboard(n):
    """Update all dashboard components"""
    try:
        logger.debug(f"[DASHBOARD] Update cycle {n} starting...")
        state = load_state()
        logger.debug(f"[DASHBOARD] State loaded successfully")
        
        # Market Status Panel - with error handling
        try:
            logger.debug("[DASHBOARD] Creating market status panel...")
            market_status_content = create_market_status_panel()
            logger.debug("[DASHBOARD] Market status panel created")
        except Exception as e:
            logger.error(f"Error creating market status panel: {e}", exc_info=True)
            market_status_content = html.Div("Market status unavailable", style={'color': '#888'})
        
        # ML Signals Panel
        try:
            logger.debug("[DASHBOARD] Creating ML signals panel...")
            ml_signals_content = create_ml_signals_panel(state)
            logger.debug("[DASHBOARD] ML signals panel created")
        except Exception as e:
            logger.error(f"Error creating ML signals panel: {e}", exc_info=True)
            ml_signals_content = html.Div("ML signals loading...", style={'color': '#888'})
        
        # Create 24-hour market performance chart
        try:
            logger.debug("[DASHBOARD] Creating market performance chart...")
            market_perf_fig = create_market_performance_chart(state)
            logger.debug("[DASHBOARD] Market performance chart created")
        except Exception as e:
            logger.error(f"Error creating market performance chart: {e}", exc_info=True)
            market_perf_fig = go.Figure()
            market_perf_fig.update_layout(plot_bgcolor='#1e1e1e', paper_bgcolor='#2a2a2a')
        
        # Trading info panel
        if state['symbols'] and len(state['symbols']) > 0:
            trading_info = html.Div([
                html.H3('[#] Currently Trading', style={'color': '#4CAF50', 'margin': '0 0 10px 0'}),
                html.P(', '.join(state['symbols']), 
                      style={'color': '#ffffff', 'fontSize': '18px', 'fontWeight': 'bold', 'margin': '0'})
            ], style={
                'backgroundColor': '#2a2a2a',
                'padding': '20px',
                'borderRadius': '10px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
                'textAlign': 'center'
            })
        else:
            trading_info = html.Div([
                html.P('No active trading session. Select stocks and click "Start Trading" above.', 
                      style={'color': '#888', 'textAlign': 'center'})
            ], style={
                'backgroundColor': '#2a2a2a',
                'padding': '20px',
                'borderRadius': '10px',
                'textAlign': 'center'
            })
        
        # v193.3 FIX: Calculate live total unrealized P&L from all positions
        live_unrealized_pnl = 0.0
        live_position_count = 0
        if state['positions']['open']:
            for pos in state['positions']['open']:
                try:
                    symbol = pos['symbol']
                    entry_price = pos['entry_price']
                    shares = pos['shares']
                    
                    # Fetch live price
                    ticker = yf.Ticker(symbol)
                    ticker_info = ticker.info
                    current_price = (ticker_info.get('currentPrice') or 
                                    ticker_info.get('regularMarketPrice') or
                                    ticker_info.get('previousClose') or
                                    entry_price)
                    
                    if current_price and current_price > 0:
                        position_pnl = (current_price - entry_price) * shares
                        live_unrealized_pnl += position_pnl
                        live_position_count += 1
                except Exception as e:
                    logger.debug(f"[DASHBOARD v193.3] Error calculating live P&L for {symbol}: {e}")
                    # Fallback to state value
                    live_unrealized_pnl += pos.get('unrealized_pnl', 0)
                    live_position_count += 1
        
        # Top metrics
        total_capital = f"${state['capital']['total']:,.2f}"
        total_return = f"Return: {state['capital']['total_return_pct']:+.2f}%"
        
        position_count = str(live_position_count if live_position_count > 0 else state['positions']['count'])
        unrealized_pnl = f"Unrealized P&L: ${live_unrealized_pnl:+,.2f}"
        
        win_rate = f"{state['performance']['win_rate']:.1f}%"
        total_trades = f"{state['performance']['total_trades']} trades"
        
        market_sentiment = f"{state['market']['sentiment']:.1f}"
        sentiment_class = state['market']['sentiment_class'].upper()
        
        # Market breakdown (if available)
        market_breakdown_display = ""
        if state['market'].get('breakdown') and len(state['market']['breakdown']) > 0:
            breakdown = state['market']['breakdown']
            source = state['market'].get('source', 'unknown')
            
            if source == 'global':
                # Multi-market view
                breakdown_parts = []
                if 'us' in breakdown:
                    breakdown_parts.append(f"US: {breakdown['us'].get('score', 0):.1f}")
                if 'uk' in breakdown:
                    breakdown_parts.append(f"UK: {breakdown['uk'].get('score', 0):.1f}")
                if 'au' in breakdown:
                    breakdown_parts.append(f"AU: {breakdown['au'].get('score', 0):.1f}")
                market_breakdown_display = f"({', '.join(breakdown_parts)})"
            else:
                # Single market
                market_name = list(breakdown.keys())[0].upper() if breakdown else 'UNKNOWN'
                market_breakdown_display = f"({market_name} Market)"
        
        # FinBERT Sentiment Panel - Load from morning report
        finbert_panel = html.Div("FinBERT data loading...", style={'color': '#888'})
        gate_status = html.Div()
        
        try:
            # Ensure we import from the correct location (not old installation)
            import sys
            from pathlib import Path
            current_dir = Path(__file__).parent
            if str(current_dir) not in sys.path:
                sys.path.insert(0, str(current_dir))
            
            # v193.3 FIX: Use cached sentiment analyzer instead of creating new one every 5 seconds
            sentiment_int = get_sentiment_analyzer()
            if sentiment_int is None:
                raise Exception("Sentiment analyzer not available")
            
            morning_sentiment = sentiment_int.load_morning_sentiment()
            
            if morning_sentiment and 'finbert_sentiment' in morning_sentiment:
                finbert = morning_sentiment['finbert_sentiment']
                scores = finbert.get('overall_scores', {})
                
                # v193.5 FIX: Normalize scores to sum to 100%
                # FinBERT scores may not sum to exactly 1.0 due to rounding/precision
                total = scores.get('negative', 0) + scores.get('neutral', 0) + scores.get('positive', 0)
                if total > 0:
                    scores_normalized = {
                        'negative': scores.get('negative', 0) / total,
                        'neutral': scores.get('neutral', 0) / total,
                        'positive': scores.get('positive', 0) / total
                    }
                    logger.info(f"[DASHBOARD v193.5] FinBERT scores normalized: {total:.3f} -> 1.000")
                else:
                    scores_normalized = {'negative': 0, 'neutral': 0, 'positive': 0}
                    logger.warning("[DASHBOARD v193.5] FinBERT scores all zero, using empty display")
                
                # Create sentiment breakdown bars
                finbert_panel = html.Div([
                    # Negative
                    html.Div([
                        html.Div('Negative', style={'color': '#888', 'fontSize': '12px', 'marginBottom': '5px'}),
                        html.Div(style={
                            'width': f"{scores_normalized.get('negative', 0) * 100}%",
                            'height': '30px',
                            'backgroundColor': '#f44336',
                            'borderRadius': '5px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'color': '#fff',
                            'fontWeight': 'bold'
                        }, children=f"{scores_normalized.get('negative', 0) * 100:.1f}%")
                    ], style={'flex': '1', 'margin': '0 10px'}),
                    
                    # Neutral
                    html.Div([
                        html.Div('Neutral', style={'color': '#888', 'fontSize': '12px', 'marginBottom': '5px'}),
                        html.Div(style={
                            'width': f"{scores_normalized.get('neutral', 0) * 100}%",
                            'height': '30px',
                            'backgroundColor': '#FFC107',
                            'borderRadius': '5px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'color': '#000',
                            'fontWeight': 'bold'
                        }, children=f"{scores_normalized.get('neutral', 0) * 100:.1f}%")
                    ], style={'flex': '1', 'margin': '0 10px'}),
                    
                    # Positive
                    html.Div([
                        html.Div('Positive', style={'color': '#888', 'fontSize': '12px', 'marginBottom': '5px'}),
                        html.Div(style={
                            'width': f"{scores_normalized.get('positive', 0) * 100}%",
                            'height': '30px',
                            'backgroundColor': '#4CAF50',
                            'borderRadius': '5px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'color': '#fff',
                            'fontWeight': 'bold'
                        }, children=f"{scores_normalized.get('positive', 0) * 100:.1f}%")
                    ], style={'flex': '1', 'margin': '0 10px'})
                ], style={'display': 'flex'})
                
                # Trading gate status - derived from morning sentiment
                # FIX v1.3.15.107: get_trading_gate() requires symbol parameter
                # Use morning sentiment data to determine general market gate
                overall_sentiment = morning_sentiment.get('overall_sentiment', 50)
                recommendation = morning_sentiment.get('recommendation', 'HOLD')
                risk_rating = morning_sentiment.get('risk_rating', 'MEDIUM')
                
                # Determine gate based on morning sentiment
                if overall_sentiment >= 70 and recommendation in ['BUY', 'STRONG_BUY']:
                    gate = 'ALLOW'
                    reason = f"Strong market sentiment ({overall_sentiment:.0f}/100)"
                elif overall_sentiment >= 50:
                    gate = 'CAUTION'
                    reason = f"Moderate market sentiment ({overall_sentiment:.0f}/100)"
                elif overall_sentiment >= 30:
                    gate = 'REDUCE'
                    reason = f"Weak market sentiment ({overall_sentiment:.0f}/100, Risk: {risk_rating})"
                else:
                    gate = 'BLOCK'
                    reason = f"Poor market sentiment ({overall_sentiment:.0f}/100, Risk: {risk_rating})"
                
                gate_colors = {
                    'BLOCK': '#f44336',
                    'REDUCE': '#FF9800',
                    'CAUTION': '#FFC107',
                    'ALLOW': '#4CAF50'
                }
                gate_status = html.Div([
                    html.Span(f"{gate}: ", style={'fontWeight': 'bold', 'color': gate_colors.get(gate, '#888')}),
                    html.Span(reason, style={'color': '#fff'})
                ], style={
                    'backgroundColor': '#1e1e1e',
                    'border': f"2px solid {gate_colors.get(gate, '#888')}"
                })
        except Exception as e:
            logger.error(f"Error loading FinBERT sentiment: {e}")
    
        # Portfolio chart
        portfolio_fig = go.Figure()
        
        # Generate 30-day history (simplified for now)
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        initial = state['capital']['initial'] if state['capital']['initial'] > 0 else 100000
        current = state['capital']['total'] if state['capital']['total'] > 0 else initial
        values = np.linspace(initial, current, 30)
        
        portfolio_fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#4CAF50', width=2),
            fill='tozeroy',
            fillcolor='rgba(76, 175, 80, 0.2)'
        ))
        
        portfolio_fig.update_layout(
            plot_bgcolor='#1e1e1e',
            paper_bgcolor='#2a2a2a',
            font=dict(color='#ffffff'),
            xaxis=dict(
                showgrid=False, 
                zeroline=False, 
                fixedrange=True,
                automargin=False
            ),
            yaxis=dict(
                showgrid=True, 
                gridcolor='#333', 
                zeroline=False,
                fixedrange=True,
                range=[initial * 0.95, max(current * 1.05, initial * 1.05)],
                automargin=False,
                tickformat='$,.0f'
            ),
            margin=dict(l=80, r=30, t=30, b=50, autoexpand=False),
            showlegend=False,
            height=250,
            width=650,
            autosize=False,
            hovermode='x unified',
            uirevision='portfolio_chart_v1'
        )
        
        # Performance chart
        perf = state['performance']
        
        performance_fig = go.Figure(data=[go.Pie(
            labels=['Wins', 'Losses', 'Open'],
            values=[
                perf['winning_trades'],
                perf['losing_trades'],
                state['positions']['count']
            ],
            marker=dict(colors=['#4CAF50', '#F44336', '#2196F3']),
            hole=0.4
        )])
        
        performance_fig.update_layout(
            plot_bgcolor='#1e1e1e',
            paper_bgcolor='#2a2a2a',
            font=dict(color='#ffffff'),
            margin=dict(l=20, r=20, t=20, b=20, autoexpand=False),
            showlegend=True,
            height=250,
            width=350,
            autosize=False,
            uirevision='performance_chart_v1'
        )
        
        # Positions list
        positions_children = []
        
        if state['positions']['open']:
            for pos in state['positions']['open']:
                symbol = pos['symbol']
                entry_price = pos['entry_price']
                shares = pos['shares']
                
                # v193.3 FIX: Fetch live current price for each position
                current_price = entry_price  # Fallback to entry price
                try:
                    ticker = yf.Ticker(symbol)
                    ticker_info = ticker.info
                    # Try multiple price fields in order of preference
                    live_price = (ticker_info.get('currentPrice') or 
                                 ticker_info.get('regularMarketPrice') or
                                 ticker_info.get('previousClose') or
                                 entry_price)
                    if live_price and live_price > 0:
                        current_price = live_price
                        logger.debug(f"[DASHBOARD v193.3] {symbol}: Live price ${current_price:.2f}")
                except Exception as e:
                    logger.warning(f"[DASHBOARD v193.3] Failed to fetch live price for {symbol}: {e}")
                    # Use price from state if available, otherwise entry price
                    current_price = pos.get('current_price', entry_price)
                
                # Calculate P&L with live price
                unrealized_pnl = (current_price - entry_price) * shares
                unrealized_pnl_pct = ((current_price - entry_price) / entry_price) * 100
                pnl_color = '#4CAF50' if unrealized_pnl_pct >= 0 else '#F44336'
                
                positions_children.append(
                    html.Div([
                        html.Div([
                            html.H4(symbol, style={'color': '#ffffff', 'margin': '0'}),
                            html.P(f"{shares} shares @ ${entry_price:.2f}", 
                                  style={'color': '#888', 'margin': '5px 0', 'fontSize': '13px'})
                        ], style={'flex': '1'}),
                        
                        html.Div([
                            html.H4(f"${current_price:.2f}", 
                                   style={'color': '#ffffff', 'margin': '0', 'textAlign': 'right'}),
                            html.P(f"{unrealized_pnl_pct:+.2f}%", 
                                  style={'color': pnl_color, 'margin': '5px 0', 'fontSize': '13px', 'textAlign': 'right'})
                        ], style={'flex': '1'})
                    ], style={
                        'backgroundColor': '#1e1e1e',
                        'padding': '15px',
                        'marginBottom': '10px',
                        'borderRadius': '5px',
                        'display': 'flex',
                        'borderLeft': f'4px solid {pnl_color}'
                    })
                )
        else:
            positions_children.append(
                html.Div("No open positions", 
                        style={'color': '#888', 'textAlign': 'center', 'padding': '20px'})
            )
        
        # Last update
        last_update = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return (
            trading_info,
            market_status_content,
            ml_signals_content,
            market_perf_fig,
            total_capital, total_return,
            position_count, unrealized_pnl,
            win_rate, total_trades,
            market_sentiment, f"{sentiment_class} {market_breakdown_display}",
            finbert_panel, gate_status,
            portfolio_fig, performance_fig,
            positions_children,
            last_update
        )
        
    except Exception as e:
        logger.error(f"Critical error in update_dashboard: {e}", exc_info=True)
        # Return safe defaults
        empty_fig = go.Figure()
        empty_fig.update_layout(plot_bgcolor='#1e1e1e', paper_bgcolor='#2a2a2a')
        
        return (
            html.Div("Dashboard updating...", style={'color': '#888'}),  # trading_info
            html.Div(),  # market_status
            html.Div(),  # ml_signals
            empty_fig,  # market_perf
            "$0.00", "Return: 0.00%",  # capital
            "0", "Unrealized P&L: $0.00",  # positions
            "0.0%", "0 trades",  # performance
            "0.0", "NEUTRAL",  # sentiment
            html.Div("Loading...", style={'color': '#888'}),  # finbert_panel
            html.Div(),  # gate_status
            empty_fig, empty_fig,  # charts
            [html.Div("Loading...")],  # positions list
            f"Error: {str(e)[:100]}"  # last_update
        )

# Tax report callbacks
@app.callback(
    [Output('tax-summary', 'children'),
     Output('tax-report-status', 'children')],
    [Input('generate-ato-btn', 'n_clicks'),
     Input('export-csv-btn', 'n_clicks'),
     Input('fy-dropdown', 'value')],
    prevent_initial_call=True
)
def handle_tax_reports(ato_clicks, csv_clicks, financial_year):
    """Handle tax report generation"""
    global trading_system
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if not trading_system or not hasattr(trading_system, 'tax_audit') or not trading_system.tax_audit:
        return (
            html.Div("Tax audit trail not available. Start trading to initialize.", 
                    style={'color': '#FF9800', 'textAlign': 'center'}),
            ""
        )
    
    fy = None if financial_year == 'current' else financial_year
    
    try:
        # Generate summary first
        summary = trading_system.get_tax_summary(fy)
        
        if not summary:
            summary_html = html.Div("No transactions recorded yet.", 
                                   style={'color': '#888', 'textAlign': 'center'})
        else:
            summary_html = html.Div([
                html.H4(f"Tax Summary - FY {summary['financial_year']}", 
                       style={'color': '#4CAF50', 'marginBottom': '10px'}),
                html.Div([
                    html.Div([
                        html.P('Net Capital Gain:', style={'color': '#888', 'margin': '5px 0'}),
                        html.P(f"${summary['net_capital_gain']:,.2f}", 
                              style={'color': '#4CAF50', 'fontSize': '18px', 'fontWeight': 'bold'})
                    ], style={'flex': '1'}),
                    html.Div([
                        html.P('CGT Discount:', style={'color': '#888', 'margin': '5px 0'}),
                        html.P(f"${summary['cgt_discount']:,.2f}", 
                              style={'color': '#2196F3', 'fontSize': '18px', 'fontWeight': 'bold'})
                    ], style={'flex': '1'}),
                    html.Div([
                        html.P('Net After Discount:', style={'color': '#888', 'margin': '5px 0'}),
                        html.P(f"${summary['net_after_discount']:,.2f}", 
                              style={'color': '#FF9800', 'fontSize': '18px', 'fontWeight': 'bold'})
                    ], style={'flex': '1'}),
                    html.Div([
                        html.P('Total Trades:', style={'color': '#888', 'margin': '5px 0'}),
                        html.P(f"{summary['trading_activity']['total_transactions']}", 
                              style={'color': '#9C27B0', 'fontSize': '18px', 'fontWeight': 'bold'})
                    ], style={'flex': '1'})
                ], style={'display': 'flex', 'gap': '20px', 'marginTop': '10px'})
            ])
        
        status = ""
        
        # Handle button clicks
        if trigger_id == 'generate-ato-btn':
            report_path = trading_system.generate_tax_report(fy)
            if report_path:
                status = f"[OK] ATO Report generated: {report_path}"
            else:
                status = "[!] Failed to generate ATO report"
        
        elif trigger_id == 'export-csv-btn':
            export_path = trading_system.export_tax_records(fy, format='csv')
            if export_path:
                status = f"[OK] Transactions exported: {export_path}"
            else:
                status = "[!] Failed to export transactions"
        
        return summary_html, status
        
    except Exception as e:
        logger.error(f"Tax report error: {e}")
        return (
            html.Div(f"Error: {str(e)}", style={'color': '#F44336', 'textAlign': 'center'}),
            "[!] Error generating tax reports"
        )


# ============================================================================
# Trading Controls Callbacks (TRADING_CONTROLS_v86)
# ============================================================================

@app.callback(
    Output('confidence-display', 'children'),
    [Input('confidence-slider', 'value')]
)
def update_confidence_display(confidence):
    """Update confidence level display"""
    if not confidence:
        return "Current: 65% (default)"
    return f"Current: {confidence}% - Only trades with {confidence}%+ confidence will execute"


@app.callback(
    [Output('force-trade-status', 'children'),
     Output('force-trade-symbol', 'value')],
    [Input('force-buy-btn', 'n_clicks'),
     Input('force-sell-btn', 'n_clicks')],
    [State('force-trade-symbol', 'value'),
     State('force-trade-confidence', 'value'),  # FIX v1.3.15.162: Use Force Trade-specific input
     State('force-trade-stop-loss', 'value')]   # FIX v1.3.15.162: Use Force Trade-specific input
)
def handle_force_trade(buy_clicks, sell_clicks, symbol, confidence, stop_loss):
    """Handle force trade button clicks"""
    ctx = callback_context
    
    if not ctx.triggered:
        return "", symbol
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if not symbol or symbol.strip() == "":
        return "⚠️ Please enter a symbol", symbol
    
    symbol = symbol.strip().upper()
    
    # FIX v1.3.15.162: Validate confidence and stop-loss inputs
    if not confidence or confidence < 50 or confidence > 95:
        return "⚠️ Confidence must be between 50% and 95%", symbol
    
    if not stop_loss or stop_loss > -1 or stop_loss < -10:
        return "⚠️ Stop loss must be between -1% and -10% (negative values)", symbol
    
    # Determine action
    if button_id == 'force-buy-btn' and buy_clicks > 0:
        action = "BUY"
        color_code = "🟢"
    elif button_id == 'force-sell-btn' and sell_clicks > 0:
        action = "SELL"
        color_code = "🔴"
    else:
        return "", symbol
    
    # Log the force trade
    timestamp = datetime.now().strftime('%H:%M:%S')
    logger.info(f"[FORCE TRADE] {action} {symbol} - Confidence: {confidence}%, Stop Loss: {stop_loss}%")
    
    # Execute force trade via trading system
    global trading_system
    if trading_system:
        try:
            if action == "BUY":
                # Force buy logic
                result = execute_force_buy(trading_system, symbol, confidence, stop_loss)
            else:
                # Force sell logic
                result = execute_force_sell(trading_system, symbol)
            
            if result:
                return f"{color_code} {action} order placed for {symbol} at {timestamp}", ""
            else:
                return f"⚠️ Failed to execute {action} for {symbol}", symbol
        except Exception as e:
            logger.error(f"Force trade error: {e}")
            return f"❌ Error: {str(e)}", symbol
    else:
        return "⚠️ Trading system not initialized. Start trading first.", symbol


def execute_force_buy(system, symbol, confidence, stop_loss):
    """Execute a forced buy trade"""
    try:
        # Get current price (FIX v1.3.15.161: Better error handling)
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        
        # Try multiple methods to get price
        current_price = None
        error_details = []
        
        # Method 1: regularMarketPrice from info
        try:
            current_price = ticker.info.get('regularMarketPrice')
            if current_price and current_price > 0:
                logger.info(f"[OK] {symbol} price from info: ${current_price:.2f}")
        except Exception as e:
            error_details.append(f"info failed: {e}")
        
        # Method 2: Latest close from history
        if not current_price:
            try:
                hist = ticker.history(period='1d')
                if not hist.empty and 'Close' in hist.columns:
                    current_price = hist['Close'].iloc[-1]
                    logger.info(f"[OK] {symbol} price from history: ${current_price:.2f}")
                else:
                    error_details.append("history returned empty or no Close column")
            except Exception as e:
                error_details.append(f"history failed: {e}")
        
        # Method 3: Try 5-day history for less liquid stocks
        if not current_price:
            try:
                hist = ticker.history(period='5d')
                if not hist.empty and 'Close' in hist.columns:
                    current_price = hist['Close'].iloc[-1]
                    logger.info(f"[OK] {symbol} price from 5d history: ${current_price:.2f}")
                else:
                    error_details.append("5d history returned empty")
            except Exception as e:
                error_details.append(f"5d history failed: {e}")
        
        if not current_price or current_price <= 0:
            error_msg = f"Could not get valid price for {symbol}. Errors: {'; '.join(error_details)}"
            logger.error(error_msg)
            return False
        
        # Calculate position size (simple: use 5% of available cash)
        position_size = int((system.cash * 0.05) / current_price)
        
        if position_size < 1:
            logger.warning(f"Insufficient cash for {symbol}")
            return False
        
        # Execute buy
        cost = position_size * current_price
        
        if cost > system.cash:
            logger.warning(f"Insufficient cash: need ${cost:.2f}, have ${system.cash:.2f}")
            return False
        
        # Create position
        system.cash -= cost
        system.invested += cost
        
        position = {
            'symbol': symbol,
            'entry_price': current_price,
            'quantity': position_size,
            'entry_time': datetime.now().isoformat(),
            'stop_loss': stop_loss,
            'confidence': confidence,
            'force_trade': True
        }
        
        system.positions[symbol] = position
        
        logger.info(f"[OK] FORCE BUY: {position_size} shares of {symbol} @ ${current_price:.2f}")
        logger.info(f"   Cost: ${cost:.2f}, Remaining cash: ${system.cash:.2f}")
        
        # Save state
        system.save_state()
        
        return True
        
    except Exception as e:
        logger.error(f"Force buy failed: {e}")
        return False


def execute_force_sell(system, symbol):
    """Execute a forced sell trade"""
    try:
        if symbol not in system.positions:
            logger.warning(f"No position for {symbol} to sell")
            return False
        
        position = system.positions[symbol]
        
        # Get current price
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        current_price = ticker.info.get('regularMarketPrice', ticker.history(period='1d')['Close'].iloc[-1])
        
        if not current_price:
            logger.error(f"Could not get price for {symbol}")
            return False
        
        # Calculate sale
        quantity = position['quantity']
        entry_price = position['entry_price']
        sale_value = quantity * current_price
        cost_basis = quantity * entry_price
        pnl = sale_value - cost_basis
        pnl_pct = (pnl / cost_basis) * 100
        
        # Update capital
        system.cash += sale_value
        system.invested -= cost_basis
        
        # Remove position
        del system.positions[symbol]
        
        logger.info(f"[OK] FORCE SELL: {quantity} shares of {symbol} @ ${current_price:.2f}")
        logger.info(f"   P&L: ${pnl:+.2f} ({pnl_pct:+.1f}%), Cash: ${system.cash:.2f}")
        
        # Save state
        system.save_state()
        
        return True
        
    except Exception as e:
        logger.error(f"Force sell failed: {e}")
        return False



if __name__ == '__main__':
    logger.info("Starting Unified Paper Trading Dashboard...")
    logger.info("Open browser to: http://localhost:8050")
    
    # Run app
    app.run(
        debug=False,
        host='0.0.0.0',
        port=8050,
        load_dotenv=False
    )
