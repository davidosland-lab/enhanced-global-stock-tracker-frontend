"""
Event Guard Report HTML Generator

Generates beautiful HTML visualization for Event Risk Guard results.
Integrates seamlessly with existing report_generator.py
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

# Modern, clean CSS styling
REPORT_CSS = """
<style>
  .evwrap {
    font-family: Inter, system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif;
    margin: 0 auto;
    max-width: 1200px;
    padding: 24px;
    background: #f9fafb;
  }
  
  .evh1 {
    font-size: 24px;
    font-weight: 700;
    margin: 0 0 8px 0;
    color: #111827;
  }
  
  .evdate {
    color: #6b7280;
    font-size: 13px;
    margin-bottom: 20px;
  }
  
  .evsummary {
    background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
    color: white;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 24px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
  }
  
  .evstat {
    text-align: center;
  }
  
  .evstat-value {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 4px;
  }
  
  .evstat-label {
    font-size: 12px;
    opacity: 0.9;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .evtable {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 8px;
  }
  
  .evtable th {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #6b7280;
    text-align: left;
    padding: 8px 12px;
    background: transparent;
    font-weight: 600;
  }
  
  .evrow {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    transition: all 0.2s ease;
  }
  
  .evrow:hover {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transform: translateY(-1px);
  }
  
  .evrow.skip {
    border-left: 4px solid #dc2626;
    background: #fef2f2;
  }
  
  .evrow.high-risk {
    border-left: 4px solid #f59e0b;
    background: #fffbeb;
  }
  
  .evcell {
    padding: 12px;
    font-size: 14px;
    vertical-align: middle;
  }
  
  .evcell:first-child {
    border-top-left-radius: 12px;
    border-bottom-left-radius: 12px;
  }
  
  .evcell:last-child {
    border-top-right-radius: 12px;
    border-bottom-right-radius: 12px;
  }
  
  .pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    border: 1px solid #e5e7eb;
    background: #f9fafb;
    font-size: 11px;
    font-weight: 600;
  }
  
  .pill.regulatory {
    background: #fef2f2;
    border-color: #fecaca;
    color: #991b1b;
  }
  
  .pill.earnings {
    background: #fef3c7;
    border-color: #fde68a;
    color: #92400e;
  }
  
  .pill.dividend {
    background: #dbeafe;
    border-color: #bfdbfe;
    color: #1e3a8a;
  }
  
  .sub {
    color: #6b7280;
    font-size: 12px;
    margin-top: 2px;
  }
  
  .legend {
    display: flex;
    gap: 16px;
    align-items: center;
    margin-top: 20px;
    padding: 16px;
    background: white;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
  }
  
  .dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
  }
  
  .badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    font-weight: 700;
    font-size: 14px;
  }
  
  .badge.low {
    background: #d1fae5;
    color: #065f46;
  }
  
  .badge.watch {
    background: #fef3c7;
    color: #92400e;
  }
  
  .badge.amber {
    background: #fed7aa;
    color: #9a3412;
  }
  
  .badge.red {
    background: #fecaca;
    color: #991b1b;
  }
  
  .code {
    font-family: ui-monospace, 'SF Mono', Menlo, Consolas, monospace;
    background: #f3f4f6;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 2px 6px;
    font-size: 12px;
  }
  
  .ticker-name {
    font-weight: 700;
    font-size: 15px;
    color: #111827;
  }
  
  .warning-icon {
    margin-right: 6px;
  }
  
  .empty-state {
    text-align: center;
    padding: 60px 20px;
    background: white;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
  }
  
  .empty-state-icon {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.3;
  }
  
  .empty-state-text {
    color: #6b7280;
    font-size: 16px;
  }
</style>
"""


def badge_html(risk_score: float, skip: bool) -> str:
    """Generate risk badge HTML"""
    if skip:
        return '<div class="badge red">⚠️</div>'
    elif risk_score >= 0.7:
        return '<div class="badge amber">⚡</div>'
    elif risk_score >= 0.4:
        return '<div class="badge watch">👁️</div>'
    else:
        return '<div class="badge low">✓</div>'


def event_pill_html(event_type: str) -> str:
    """Generate event type pill HTML"""
    if not event_type or event_type == '—':
        return '<span class="pill">None</span>'
    
    event_lower = event_type.lower()
    
    if 'basel' in event_lower or 'pillar' in event_lower or 'regulatory' in event_lower:
        return f'<span class="pill regulatory">🚨 {event_type.title()}</span>'
    elif 'earnings' in event_lower:
        return f'<span class="pill earnings">📊 {event_type.title()}</span>'
    elif 'dividend' in event_lower:
        return f'<span class="pill dividend">💰 {event_type.title()}</span>'
    else:
        return f'<span class="pill">{event_type.title()}</span>'


def render_event_guard_section(df: pd.DataFrame, title: str = "Event-Aware Risk Guard") -> str:
    """
    Render Event Risk Guard results as beautiful HTML section.
    
    Args:
        df: DataFrame with columns:
            - ticker, event_type, days_to_event, sentiment_72h, vol_spike,
              risk_score, weight_haircut, skip_trading, hedge_beta, warning
        title: Section title
    
    Returns:
        HTML string ready to embed in report
    """
    
    # Handle empty DataFrame
    if df.empty:
        return f"""
        {REPORT_CSS}
        <section class="evwrap">
          <h2 class="evh1">{title}</h2>
          <div class="evdate">Generated {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}</div>
          <div class="empty-state">
            <div class="empty-state-icon">✅</div>
            <div class="empty-state-text">
              No upcoming events detected. All stocks cleared for trading.
            </div>
          </div>
        </section>
        """
    
    # Ensure required columns exist
    required = [
        'ticker', 'event_type', 'days_to_event', 'sentiment_72h',
        'vol_spike', 'risk_score', 'weight_haircut', 'skip_trading',
        'hedge_beta', 'warning'
    ]
    
    for col in required:
        if col not in df.columns:
            df[col] = None
    
    # Convert types
    sdf = df.copy()
    sdf['risk_score'] = pd.to_numeric(sdf['risk_score'], errors='coerce').fillna(0.0)
    sdf['weight_haircut'] = pd.to_numeric(sdf['weight_haircut'], errors='coerce').fillna(0.0)
    sdf['days_to_event'] = pd.to_numeric(sdf['days_to_event'], errors='coerce')
    sdf['sentiment_72h'] = pd.to_numeric(sdf['sentiment_72h'], errors='coerce')
    
    # Sort: skip first, then by risk score
    sdf['skip_trading'] = sdf['skip_trading'].fillna(False).astype(bool)
    sdf = sdf.sort_values(['skip_trading', 'risk_score'], ascending=[False, False])
    
    # Calculate summary stats
    total_stocks = len(sdf)
    skip_count = int(sdf['skip_trading'].sum())
    high_risk = int((sdf['risk_score'] >= 0.7).sum())
    avg_risk = float(sdf['risk_score'].mean())
    
    # Build summary section
    summary_html = f"""
    <div class="evsummary">
      <div class="evstat">
        <div class="evstat-value">{total_stocks}</div>
        <div class="evstat-label">Stocks Monitored</div>
      </div>
      <div class="evstat">
        <div class="evstat-value" style="color: #fecaca;">{skip_count}</div>
        <div class="evstat-label">Sit-Out Recommendations</div>
      </div>
      <div class="evstat">
        <div class="evstat-value" style="color: #fed7aa;">{high_risk}</div>
        <div class="evstat-label">High Risk Events</div>
      </div>
      <div class="evstat">
        <div class="evstat-value">{avg_risk:.2f}</div>
        <div class="evstat-label">Average Risk Score</div>
      </div>
    </div>
    """
    
    # Build table rows
    rows_html = []
    
    for _, r in sdf.iterrows():
        # Risk badge
        badge = badge_html(r['risk_score'], r['skip_trading'])
        
        # Event type pill
        evt_pill = event_pill_html(r['event_type'])
        
        # Days to event
        dte = "—" if pd.isna(r['days_to_event']) else f"{int(r['days_to_event'])}d"
        
        # Sentiment
        sent = "—" if pd.isna(r['sentiment_72h']) else f"{float(r['sentiment_72h']):+.2f}"
        sent_color = ""
        if not pd.isna(r['sentiment_72h']):
            if r['sentiment_72h'] < -0.1:
                sent_color = "color: #dc2626;"
            elif r['sentiment_72h'] > 0.1:
                sent_color = "color: #16a34a;"
        
        # Volatility spike
        vol = "Yes ⚡" if r['vol_spike'] else "No"
        vol_color = "color: #f59e0b;" if r['vol_spike'] else ""
        
        # Risk score with color
        risk_val = float(r['risk_score'])
        risk_color = ""
        if risk_val >= 0.7:
            risk_color = "color: #dc2626; font-weight: 700;"
        elif risk_val >= 0.4:
            risk_color = "color: #f59e0b; font-weight: 600;"
        
        # Haircut
        hc = f"{float(r['weight_haircut']) * 100:.0f}%"
        hc_display = f'<span class="code">{hc}</span>' if r['weight_haircut'] > 0 else "—"
        
        # Beta
        beta = "—" if pd.isna(r['hedge_beta']) else f"{float(r['hedge_beta']):.2f}"
        
        # Warning message
        warning = str(r['warning']) if pd.notna(r['warning']) and r['warning'] != '—' else ""
        
        # Row class (for styling)
        row_class = "evrow"
        if r['skip_trading']:
            row_class += " skip"
        elif risk_val >= 0.7:
            row_class += " high-risk"
        
        rows_html.append(f"""
          <tr class="{row_class}">
            <td class="evcell">
              <span class="ticker-name">{r['ticker']}</span>
            </td>
            <td class="evcell">{badge}</td>
            <td class="evcell">{evt_pill}</td>
            <td class="evcell"><span class="pill">in {dte}</span></td>
            <td class="evcell" style="{sent_color}">{sent}</td>
            <td class="evcell" style="{vol_color}">{vol}</td>
            <td class="evcell" style="{risk_color}">{risk_val:.2f}</td>
            <td class="evcell">{hc_display}</td>
            <td class="evcell">{beta}</td>
            <td class="evcell"><small class="sub">{warning}</small></td>
          </tr>
        """)
    
    # Legend
    legend = """
      <div class="legend">
        <div><span class="dot" style="background:#16a34a;"></span><span class="sub">Green (low risk)</span></div>
        <div><span class="dot" style="background:#f2d022;"></span><span class="sub">Yellow (watch)</span></div>
        <div><span class="dot" style="background:#ff8c00;"></span><span class="sub">Amber (elevated)</span></div>
        <div><span class="dot" style="background:#e02424;"></span><span class="sub">Red (sit-out)</span></div>
      </div>
    """
    
    # Combine all sections
    section = f"""
    {REPORT_CSS}
    <section class="evwrap">
      <h2 class="evh1">{title}</h2>
      <div class="evdate">Generated {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}</div>
      
      {summary_html}
      
      <table class="evtable">
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Risk</th>
            <th>Event Type</th>
            <th>Timing</th>
            <th>Sentiment<br/>(72h)</th>
            <th>Vol<br/>Spike</th>
            <th>Risk<br/>Score</th>
            <th>Haircut</th>
            <th>β vs<br/>XJO</th>
            <th>Warning / Notes</th>
          </tr>
        </thead>
        <tbody>
          {''.join(rows_html)}
        </tbody>
      </table>
      
      {legend}
    </section>
    """
    
    return section


def generate_standalone_report(df: pd.DataFrame, output_path: str = None) -> str:
    """
    Generate standalone HTML report file.
    
    Args:
        df: DataFrame with event guard results
        output_path: Path to save HTML file (optional)
    
    Returns:
        HTML content string
    """
    
    section = render_event_guard_section(df)
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Event Risk Guard Report - {datetime.utcnow().strftime("%Y-%m-%d")}</title>
</head>
<body style="margin:0;padding:0;background:#f9fafb;">
    {section}
</body>
</html>
"""
    
    if output_path:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"Event guard report saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
    
    return html


# -----------------------------
# Test / Example usage
# -----------------------------
if __name__ == "__main__":
    # Create example data
    example_data = [
        {
            'ticker': 'CBA.AX',
            'event_type': 'basel_iii',
            'days_to_event': 2,
            'sentiment_72h': -0.25,
            'vol_spike': True,
            'risk_score': 0.85,
            'weight_haircut': 0.70,
            'skip_trading': True,
            'hedge_beta': 0.95,
            'warning': '🚨 REGULATORY REPORT in 2d - HIGH RISK (Basel III/Pillar 3)'
        },
        {
            'ticker': 'ANZ.AX',
            'event_type': 'earnings',
            'days_to_event': 5,
            'sentiment_72h': -0.15,
            'vol_spike': False,
            'risk_score': 0.55,
            'weight_haircut': 0.35,
            'skip_trading': False,
            'hedge_beta': 0.88,
            'warning': '⚠️ Negative sentiment (-0.15) detected in recent news'
        },
        {
            'ticker': 'NAB.AX',
            'event_type': 'dividend',
            'days_to_event': 1,
            'sentiment_72h': 0.10,
            'vol_spike': False,
            'risk_score': 0.25,
            'weight_haircut': 0.20,
            'skip_trading': True,
            'hedge_beta': 0.92,
            'warning': '📅 Dividend in 1d - within 1d buffer'
        },
        {
            'ticker': 'WBC.AX',
            'event_type': None,
            'days_to_event': None,
            'sentiment_72h': 0.05,
            'vol_spike': False,
            'risk_score': 0.10,
            'weight_haircut': 0.0,
            'skip_trading': False,
            'hedge_beta': 0.90,
            'warning': '—'
        }
    ]
    
    df = pd.DataFrame(example_data)
    
    # Generate and save report
    html = generate_standalone_report(df, 'event_guard_test_report.html')
    
    print("✅ Test report generated: event_guard_test_report.html")
    print(f"   Total stocks: {len(df)}")
    print(f"   Sit-out recommendations: {df['skip_trading'].sum()}")
    print(f"   High risk (≥0.7): {(df['risk_score'] >= 0.7).sum()}")
