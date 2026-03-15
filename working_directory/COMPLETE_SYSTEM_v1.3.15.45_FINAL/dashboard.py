"""
Real-Time Paper Trading Dashboard
==================================

Interactive dashboard for monitoring paper trading activity:
- Live portfolio value and P&L
- Open positions with real-time updates
- Intraday alerts feed
- Performance metrics
- Trade history
- Market sentiment gauge

Usage:
    python dashboard.py

Then open: http://localhost:8050
"""

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import json
from pathlib import Path
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(__name__, update_title='Paper Trading Dashboard', 
                meta_tags=[{'http-equiv': 'Cache-Control', 'content': 'no-cache, no-store, must-revalidate'}])
app.title = 'Phase 3 Paper Trading Dashboard v1.3.2'

# Load state
def load_state():
    """Load current trading state"""
    state_file = 'state/paper_trading_state.json'
    
    try:
        if Path(state_file).exists():
            with open(state_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading state: {e}")
    
    # Return default empty state
    return {
        'timestamp': datetime.now().isoformat(),
        'capital': {
            'total': 100000,
            'cash': 100000,
            'invested': 0,
            'initial': 100000,
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

# Layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1('[UP] Phase 3 Paper Trading Dashboard', 
                style={'color': '#ffffff', 'margin': '0'}),
        html.P('Real-Time Swing Trading + Intraday Monitoring (v1.3.2 - Chart Stability Fixed)',
               style={'color': '#cccccc', 'margin': '5px 0 0 0'})
    ], style={
        'backgroundColor': '#1e1e1e',
        'padding': '20px',
        'marginBottom': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.2)'
    }),
    
    # Stock Selection Info Panel
    html.Div([
        html.Div([
            html.H3('[#] Currently Trading', style={'color': '#4CAF50', 'margin': '0 0 10px 0', 'fontSize': '18px'}),
            html.P(id='active-symbols', style={'color': '#ffffff', 'fontSize': '16px', 'margin': '5px 0', 'fontWeight': 'bold'}),
            html.P([
                html.Span('To change stocks, restart with: ', style={'color': '#888'}),
                html.Code('python paper_trading_coordinator.py --symbols YOUR,STOCKS --capital 100000 --real-signals', 
                         style={'backgroundColor': '#1e1e1e', 'padding': '5px 10px', 'borderRadius': '5px', 'color': '#4CAF50', 'fontSize': '12px'})
            ], style={'margin': '10px 0 0 0'}),
        ], style={'flex': '2'}),
        
        html.Div([
            html.H3('[i] Quick Examples', style={'color': '#2196F3', 'margin': '0 0 10px 0', 'fontSize': '18px'}),
            html.Div([
                html.P([html.Strong('ASX: '), 'RIO.AX,CBA.AX,BHP.AX'], 
                       style={'color': '#ccc', 'margin': '3px 0', 'fontSize': '13px'}),
                html.P([html.Strong('US Tech: '), 'AAPL,MSFT,GOOGL,NVDA'], 
                       style={'color': '#ccc', 'margin': '3px 0', 'fontSize': '13px'}),
                html.P([html.Strong('Banks: '), 'CBA.AX,NAB.AX,WBC.AX,ANZ.AX'], 
                       style={'color': '#ccc', 'margin': '3px 0', 'fontSize': '13px'}),
            ])
        ], style={'flex': '1'}),
        
        html.Div([
            html.H3('[*] Symbol Format', style={'color': '#FF9800', 'margin': '0 0 10px 0', 'fontSize': '18px'}),
            html.Div([
                html.P([html.Strong('ASX: '), 'SYMBOL.AX'], 
                       style={'color': '#ccc', 'margin': '3px 0', 'fontSize': '13px'}),
                html.P([html.Strong('US: '), 'SYMBOL'], 
                       style={'color': '#ccc', 'margin': '3px 0', 'fontSize': '13px'}),
                html.P([html.Strong('UK: '), 'SYMBOL.L'], 
                       style={'color': '#ccc', 'margin': '3px 0', 'fontSize': '13px'}),
            ])
        ], style={'flex': '1'}),
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
        interval=5*1000,  # Update every 5 seconds
        n_intervals=0
    ),
    
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
    
    # Charts row
    html.Div([
        # Portfolio value chart
        html.Div([
            html.H3('Portfolio Value', style={'color': '#ffffff', 'marginBottom': '15px'}),
            dcc.Graph(id='portfolio-chart')
        ], style={
            'backgroundColor': '#2a2a2a',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
            'flex': '2',
            'margin': '0 10px'
        }),
        
        # Performance metrics
        html.Div([
            html.H3('Performance', style={'color': '#ffffff', 'marginBottom': '15px'}),
            dcc.Graph(id='performance-chart')
        ], style={
            'backgroundColor': '#2a2a2a',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
            'flex': '1',
            'margin': '0 10px'
        })
    ], style={'display': 'flex', 'marginBottom': '20px'}),
    
    # Positions and alerts row
    html.Div([
        # Open positions
        html.Div([
            html.H3('Open Positions', style={'color': '#ffffff', 'marginBottom': '15px'}),
            html.Div(id='positions-list')
        ], style={
            'backgroundColor': '#2a2a2a',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
            'flex': '1',
            'margin': '0 10px',
            'maxHeight': '400px',
            'overflowY': 'auto'
        }),
        
        # Intraday alerts
        html.Div([
            html.H3('Intraday Alerts', style={'color': '#ffffff', 'marginBottom': '15px'}),
            html.Div(id='alerts-feed')
        ], style={
            'backgroundColor': '#2a2a2a',
            'padding': '20px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
            'flex': '1',
            'margin': '0 10px',
            'maxHeight': '400px',
            'overflowY': 'auto'
        })
    ], style={'display': 'flex', 'marginBottom': '20px'}),
    
    # Recent trades
    html.Div([
        html.H3('Recent Trades', style={'color': '#ffffff', 'marginBottom': '15px'}),
        html.Div(id='trades-list')
    ], style={
        'backgroundColor': '#2a2a2a',
        'padding': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.2)',
        'marginBottom': '20px',
        'maxHeight': '300px',
        'overflowY': 'auto'
    }),
    
    # Footer
    html.Div([
        html.P(id='last-update', style={'color': '#888', 'fontSize': '12px', 'margin': '0', 'textAlign': 'center'})
    ], style={'padding': '10px'})
    
], style={
    'backgroundColor': '#121212',
    'minHeight': '100vh',
    'padding': '20px',
    'fontFamily': 'Arial, sans-serif'
})

# Callbacks
@app.callback(
    [
        Output('total-capital', 'children'),
        Output('total-return', 'children'),
        Output('position-count', 'children'),
        Output('unrealized-pnl', 'children'),
        Output('win-rate', 'children'),
        Output('total-trades', 'children'),
        Output('market-sentiment', 'children'),
        Output('sentiment-class', 'children'),
        Output('portfolio-chart', 'figure'),
        Output('performance-chart', 'figure'),
        Output('positions-list', 'children'),
        Output('alerts-feed', 'children'),
        Output('trades-list', 'children'),
        Output('last-update', 'children'),
        Output('active-symbols', 'children')  # Add active symbols output
    ],
    Input('interval-component', 'n_intervals')
)
def update_dashboard(n):
    """Update all dashboard components"""
    state = load_state()
    
    # Extract active symbols
    if 'symbols' in state and state['symbols']:
        active_symbols_text = ', '.join(state['symbols'])
    else:
        # Fallback: extract from open positions
        if state['positions']['open']:
            unique_symbols = list(set([p['symbol'] for p in state['positions']['open']]))
            active_symbols_text = ', '.join(unique_symbols)
        else:
            active_symbols_text = 'No active stocks (start paper trading to see symbols)'
    
    # Top metrics
    total_capital = f"${state['capital']['total']:,.2f}"
    total_return = f"Return: {state['capital']['total_return_pct']:+.2f}%"
    
    position_count = str(state['positions']['count'])
    unrealized_pnl = f"Unrealized P&L: ${state['positions']['unrealized_pnl']:+,.2f}"
    
    win_rate_val = state['performance']['win_rate']
    win_rate = f"{win_rate_val:.1f}%"
    total_trades = f"{state['performance']['total_trades']} trades"
    
    sentiment_val = state['market']['sentiment']
    market_sentiment = f"{sentiment_val:.0f}/100"
    sentiment_class = state['market']['sentiment_class'].replace('_', ' ').title()
    
    # Portfolio chart
    # For demo, show simple trend
    portfolio_fig = go.Figure()
    
    # Create mock portfolio value history
    initial = state['capital']['initial']
    current = state['capital']['total']
    
    dates = [datetime.now() - timedelta(days=i) for i in range(30, -1, -1)]
    
    # Linear interpolation for demo
    values = [initial + (current - initial) * (i / 30) for i in range(31)]
    
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
        xaxis=dict(showgrid=False, zeroline=False, fixedrange=True),
        yaxis=dict(
            showgrid=True, 
            gridcolor='#333', 
            zeroline=False,
            fixedrange=True,
            range=[initial * 0.95, max(current * 1.05, initial * 1.05)],
            automargin=False  # Disable auto-margin
        ),
        margin=dict(l=70, r=30, t=30, b=50, autoexpand=False),
        showlegend=False,
        height=250,
        autosize=False,
        hovermode='x unified'
    )
    
    # Performance chart (pie chart)
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
        autosize=False
    )
    
    # Positions list
    positions_children = []
    
    if state['positions']['open']:
        for pos in state['positions']['open']:
            pnl_pct = pos['unrealized_pnl_pct']
            pnl_color = '#4CAF50' if pnl_pct >= 0 else '#F44336'
            
            positions_children.append(
                html.Div([
                    html.Div([
                        html.Strong(pos['symbol'], style={'color': '#ffffff', 'fontSize': '16px'}),
                        html.Span(f" {pos['shares']} shares", style={'color': '#888', 'fontSize': '12px'})
                    ]),
                    html.Div([
                        html.Span(f"Entry: ${pos['entry_price']:.2f}", style={'color': '#888', 'fontSize': '12px'}),
                        html.Span(f" → Current: ${pos['current_price']:.2f}", style={'color': '#888', 'fontSize': '12px'})
                    ]),
                    html.Div([
                        html.Span(f"P&L: {pnl_pct:+.2f}%", style={'color': pnl_color, 'fontSize': '14px', 'fontWeight': 'bold'}),
                        html.Span(f" (${pos['unrealized_pnl']:+,.2f})", style={'color': pnl_color, 'fontSize': '12px'})
                    ]),
                    html.Div([
                        html.Span(f"Regime: {pos['regime']}", style={'color': '#888', 'fontSize': '11px'}),
                        html.Span(f" | Confidence: {pos['entry_confidence']:.0f}%", style={'color': '#888', 'fontSize': '11px'})
                    ])
                ], style={
                    'backgroundColor': '#1e1e1e',
                    'padding': '15px',
                    'marginBottom': '10px',
                    'borderRadius': '5px',
                    'borderLeft': f'4px solid {pnl_color}'
                })
            )
    else:
        positions_children.append(
            html.Div("No open positions", style={'color': '#888', 'textAlign': 'center', 'padding': '20px'})
        )
    
    # Alerts feed
    alerts_children = []
    
    if state['intraday_alerts']:
        for alert in reversed(state['intraday_alerts'][-10:]):
            alert_time = datetime.fromisoformat(alert['timestamp']).strftime('%H:%M:%S')
            alert_type = alert['type']
            alert_color = '#4CAF50' if 'BULLISH' in alert_type else '#F44336'
            
            alerts_children.append(
                html.Div([
                    html.Div([
                        html.Strong(alert['symbol'], style={'color': '#ffffff'}),
                        html.Span(f" {alert_time}", style={'color': '#888', 'fontSize': '11px', 'float': 'right'})
                    ]),
                    html.Div(
                        alert_type.replace('_', ' '),
                        style={'color': alert_color, 'fontSize': '12px', 'fontWeight': 'bold'}
                    ),
                    html.Div([
                        html.Span(f"Strength: {alert['strength']:.0f}", style={'color': '#888', 'fontSize': '11px'}),
                        html.Span(f" | Price: {alert['price_change_pct']:+.2f}%", style={'color': '#888', 'fontSize': '11px'}),
                        html.Span(f" | Vol: {alert['volume_ratio']:.1f}x", style={'color': '#888', 'fontSize': '11px'})
                    ])
                ], style={
                    'backgroundColor': '#1e1e1e',
                    'padding': '10px',
                    'marginBottom': '8px',
                    'borderRadius': '5px',
                    'borderLeft': f'3px solid {alert_color}'
                })
            )
    else:
        alerts_children.append(
            html.Div("No recent alerts", style={'color': '#888', 'textAlign': 'center', 'padding': '20px'})
        )
    
    # Trades list
    trades_children = []
    
    if state['closed_trades']:
        for trade in reversed(state['closed_trades'][-10:]):
            entry_date = datetime.fromisoformat(trade['entry_date']).strftime('%m/%d')
            exit_date = datetime.fromisoformat(trade['exit_date']).strftime('%m/%d')
            pnl_pct = trade['pnl_pct']
            pnl_color = '#4CAF50' if pnl_pct >= 0 else '#F44336'
            
            trades_children.append(
                html.Div([
                    html.Div([
                        html.Strong(trade['symbol'], style={'color': '#ffffff'}),
                        html.Span(f" {entry_date} → {exit_date}", style={'color': '#888', 'fontSize': '11px', 'marginLeft': '10px'}),
                        html.Span(f" ({trade['holding_days']}d)", style={'color': '#888', 'fontSize': '11px'})
                    ]),
                    html.Div([
                        html.Span(f"${trade['entry_price']:.2f} → ${trade['exit_price']:.2f}", style={'color': '#888', 'fontSize': '12px'}),
                        html.Span(f" | {pnl_pct:+.2f}%", style={'color': pnl_color, 'fontSize': '12px', 'fontWeight': 'bold', 'marginLeft': '10px'}),
                        html.Span(f" (${trade['pnl']:+,.2f})", style={'color': pnl_color, 'fontSize': '11px'})
                    ]),
                    html.Div(
                        f"Exit: {trade['exit_reason']}",
                        style={'color': '#888', 'fontSize': '11px'}
                    )
                ], style={
                    'backgroundColor': '#1e1e1e',
                    'padding': '10px',
                    'marginBottom': '8px',
                    'borderRadius': '5px',
                    'borderLeft': f'3px solid {pnl_color}'
                })
            )
    else:
        trades_children.append(
            html.Div("No closed trades yet", style={'color': '#888', 'textAlign': 'center', 'padding': '20px'})
        )
    
    # Last update
    last_update = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return (
        total_capital, total_return,
        position_count, unrealized_pnl,
        win_rate, total_trades,
        market_sentiment, sentiment_class,
        portfolio_fig, performance_fig,
        positions_children, alerts_children, trades_children,
        last_update,
        active_symbols_text  # Add active symbols to return
    )

if __name__ == '__main__':
    logger.info("Starting Paper Trading Dashboard...")
    logger.info("Open browser to: http://localhost:8050")
    
    # Use app.run() for newer Dash versions (app.run_server is obsolete)
    # Set load_dotenv=False to avoid .env encoding errors
    app.run(
        debug=False,
        host='0.0.0.0',
        port=8050,
        load_dotenv=False
    )
