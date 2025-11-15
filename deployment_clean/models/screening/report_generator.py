"""
Report Generator Module

Generates professional HTML morning reports with screening results.
Creates comprehensive reports with market overview, top opportunities,
sector analysis, and system performance metrics.

Features:
- HTML report generation with professional styling
- Market sentiment summary
- Top opportunities ranking
- Sector breakdown and analysis
- Interactive charts preparation
- Email-ready formatting
- Historical report archiving
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import pytz

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates professional HTML morning reports from screening results.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize Report Generator
        
        Args:
            config_path: Path to screening_config.json
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "screening_config.json"
        
        self.config = self._load_config(config_path)
        self.report_config = self.config['reporting']
        self.timezone = pytz.timezone('Australia/Sydney')
        
        # Ensure report directory exists
        self.report_dir = Path(self.report_config['report_path'])
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Report Generator initialized")
        logger.info(f"  Report Path: {self.report_dir}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load screening configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def generate_morning_report(
        self,
        opportunities: List[Dict],
        spi_sentiment: Dict,
        sector_summary: Dict,
        system_stats: Dict
    ) -> str:
        """
        Generate complete morning report
        
        Args:
            opportunities: List of scored opportunities
            spi_sentiment: SPI market sentiment data
            sector_summary: Sector performance summary
            system_stats: System performance statistics
            
        Returns:
            Path to generated HTML report
        """
        logger.info("Generating morning report...")
        
        # Generate report timestamp
        now = datetime.now(self.timezone)
        report_date = now.strftime('%Y-%m-%d')
        report_time = now.strftime('%I:%M %p %Z')
        
        # Build HTML content
        html_content = self._build_html_report(
            report_date=report_date,
            report_time=report_time,
            opportunities=opportunities,
            spi_sentiment=spi_sentiment,
            sector_summary=sector_summary,
            system_stats=system_stats
        )
        
        # Save report
        report_filename = f"{report_date}_market_report.html"
        report_path = self.report_dir / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Report saved: {report_path}")
        
        # Also save JSON data
        if self.report_config.get('save_to_disk', True):
            self._save_json_data(
                report_date=report_date,
                opportunities=opportunities,
                spi_sentiment=spi_sentiment,
                sector_summary=sector_summary,
                system_stats=system_stats
            )
        
        return str(report_path)
    
    def _build_html_report(
        self,
        report_date: str,
        report_time: str,
        opportunities: List[Dict],
        spi_sentiment: Dict,
        sector_summary: Dict,
        system_stats: Dict
    ) -> str:
        """Build complete HTML report"""
        
        # Get top opportunities
        top_opportunities = opportunities[:self.report_config['max_stocks_in_report']]
        
        # Build sections
        header_html = self._build_header(report_date, report_time)
        market_overview_html = self._build_market_overview(spi_sentiment)
        opportunities_html = self._build_opportunities_section(top_opportunities)
        sector_html = self._build_sector_section(sector_summary)
        watchlist_html = self._build_watchlist_section(opportunities)
        warnings_html = self._build_warnings_section(opportunities)
        performance_html = self._build_performance_section(system_stats)
        
        # Combine all sections
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASX Morning Report - {report_date}</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    {header_html}
    {market_overview_html}
    {opportunities_html}
    {sector_html}
    {watchlist_html}
    {warnings_html}
    {performance_html}
    {self._build_footer()}
</body>
</html>
"""
        return html
    
    def _get_css_styles(self) -> str:
        """Get CSS styling for report"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            color: #2d3748;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .section {
            background: white;
            padding: 30px;
            margin-bottom: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .section h2 {
            color: #1e3a8a;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #3b82f6;
            padding-bottom: 10px;
        }
        
        .market-overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .metric-card {
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
            background: #f8fafc;
        }
        
        .metric-label {
            font-weight: 600;
            color: #64748b;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        
        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #1e293b;
        }
        
        .metric-change {
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        .positive {
            color: #10b981;
        }
        
        .negative {
            color: #ef4444;
        }
        
        .neutral {
            color: #6b7280;
        }
        
        .opportunity-card {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        
        .opportunity-card:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }
        
        .opportunity-card.high-confidence {
            border-left: 5px solid #10b981;
        }
        
        .opportunity-card.medium-confidence {
            border-left: 5px solid #f59e0b;
        }
        
        .opportunity-card.low-confidence {
            border-left: 5px solid #ef4444;
        }
        
        .opportunity-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .opportunity-title {
            font-size: 1.4em;
            font-weight: bold;
            color: #1e293b;
        }
        
        .opportunity-score {
            font-size: 1.5em;
            font-weight: bold;
            padding: 5px 15px;
            border-radius: 20px;
            background: #10b981;
            color: white;
        }
        
        .opportunity-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .detail-item {
            padding: 10px;
            background: #f8fafc;
            border-radius: 5px;
        }
        
        .detail-label {
            font-size: 0.85em;
            color: #64748b;
            margin-bottom: 3px;
        }
        
        .detail-value {
            font-size: 1.1em;
            font-weight: 600;
            color: #1e293b;
        }
        
        .opportunity-analysis {
            margin-top: 15px;
            padding: 15px;
            background: #f1f5f9;
            border-radius: 5px;
            font-size: 0.95em;
            line-height: 1.8;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        th {
            background: #f1f5f9;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #475569;
            border-bottom: 2px solid #cbd5e1;
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid #e2e8f0;
        }
        
        tr:hover {
            background: #f8fafc;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .badge-success {
            background: #d1fae5;
            color: #065f46;
        }
        
        .badge-warning {
            background: #fef3c7;
            color: #92400e;
        }
        
        .badge-danger {
            background: #fee2e2;
            color: #991b1b;
        }
        
        .badge-info {
            background: #dbeafe;
            color: #1e40af;
        }
        
        .watchlist-item {
            padding: 15px;
            margin-bottom: 10px;
            background: #f8fafc;
            border-left: 3px solid #3b82f6;
            border-radius: 5px;
        }
        
        .warning-item {
            padding: 15px;
            margin-bottom: 10px;
            background: #fef2f2;
            border-left: 3px solid #ef4444;
            border-radius: 5px;
        }
        
        .footer {
            text-align: center;
            padding: 30px;
            color: #64748b;
            font-size: 0.9em;
            border-top: 2px solid #e2e8f0;
            margin-top: 40px;
        }
        
        .emoji {
            font-size: 1.2em;
        }
        
        @media print {
            body {
                background: white;
            }
            
            .section {
                box-shadow: none;
                break-inside: avoid;
            }
        }
        """
    
    def _build_header(self, report_date: str, report_time: str) -> str:
        """Build report header"""
        return f"""
    <div class="header">
        <h1><span class="emoji">📊</span> ASX Morning Report</h1>
        <p>{report_date} | Generated at {report_time}</p>
    </div>
    <div class="container">
"""
    
    def _build_market_overview(self, spi_sentiment: Dict) -> str:
        """Build market overview section"""
        gap = spi_sentiment.get('gap_prediction', {})
        predicted_gap = gap.get('predicted_gap_pct', 0)
        sentiment_score = spi_sentiment.get('sentiment_score', 50)
        recommendation = spi_sentiment.get('recommendation', {})
        
        # Determine direction emoji and color
        if predicted_gap > 0.3:
            gap_emoji = "🟢"
            gap_text = f"UP {predicted_gap:.2f}%"
            gap_class = "positive"
        elif predicted_gap < -0.3:
            gap_emoji = "🔴"
            gap_text = f"DOWN {abs(predicted_gap):.2f}%"
            gap_class = "negative"
        else:
            gap_emoji = "🟡"
            gap_text = "FLAT"
            gap_class = "neutral"
        
        # US markets data
        us_markets = spi_sentiment.get('us_markets', {})
        us_summary = []
        for market, data in us_markets.items():
            change = data.get('change_pct', 0)
            sign = '+' if change >= 0 else ''
            us_summary.append(f"{market}: {sign}{change:.2f}%")
        us_text = " | ".join(us_summary) if us_summary else "N/A"
        
        # Sentiment stars
        stars = "⭐" * int(sentiment_score / 20)
        
        return f"""
    <div class="section">
        <h2><span class="emoji">📈</span> Market Overview</h2>
        <div class="market-overview-grid">
            <div class="metric-card">
                <div class="metric-label">Expected ASX 200 Open</div>
                <div class="metric-value {gap_class}">{gap_emoji} {gap_text}</div>
                <div class="metric-change">Confidence: {gap.get('confidence', 0)}%</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Market Sentiment</div>
                <div class="metric-value">{recommendation.get('stance', 'NEUTRAL')}</div>
                <div class="metric-change">{stars} ({sentiment_score:.1f}/100)</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Overnight US Markets</div>
                <div class="metric-value" style="font-size: 1.2em;">{us_text}</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Trading Recommendation</div>
                <div class="metric-value" style="font-size: 1.2em;">{recommendation.get('message', 'N/A')}</div>
                <div class="metric-change">Risk: {recommendation.get('risk_level', 'MEDIUM')}</div>
            </div>
        </div>
    </div>
"""
    
    def _build_opportunities_section(self, opportunities: List[Dict]) -> str:
        """Build top opportunities section"""
        if not opportunities:
            return """
    <div class="section">
        <h2><span class="emoji">🎯</span> Top Opportunities</h2>
        <p>No opportunities identified at this time.</p>
    </div>
"""
        
        # Filter BUY signals
        buy_opportunities = [o for o in opportunities if o.get('prediction') == 'BUY']
        
        if not buy_opportunities:
            buy_opportunities = opportunities[:10]  # Show top 10 regardless
        
        cards_html = ""
        for i, opp in enumerate(buy_opportunities[:10], 1):
            cards_html += self._build_opportunity_card(i, opp)
        
        return f"""
    <div class="section">
        <h2><span class="emoji">🎯</span> Top {len(buy_opportunities[:10])} Opportunities</h2>
        {cards_html}
    </div>
"""
    
    def _build_opportunity_card(self, rank: int, opp: Dict) -> str:
        """Build individual opportunity card"""
        symbol = opp.get('symbol', 'N/A')
        name = opp.get('name', 'Unknown')
        score = opp.get('opportunity_score', 0)
        prediction = opp.get('prediction', 'HOLD')
        confidence = opp.get('confidence', 0)
        price = opp.get('price', 0)
        
        # Confidence class
        if confidence >= 70:
            conf_class = "high-confidence"
            conf_badge = "badge-success"
        elif confidence >= 50:
            conf_class = "medium-confidence"
            conf_badge = "badge-warning"
        else:
            conf_class = "low-confidence"
            conf_badge = "badge-danger"
        
        # Score color
        if score >= 80:
            score_color = "#10b981"
        elif score >= 65:
            score_color = "#f59e0b"
        else:
            score_color = "#6b7280"
        
        # Get technical data
        technical = opp.get('technical', {})
        rsi = technical.get('rsi', 50)
        
        # Get score breakdown
        breakdown = opp.get('score_breakdown', {})
        
        return f"""
        <div class="opportunity-card {conf_class}">
            <div class="opportunity-header">
                <div class="opportunity-title">
                    {rank}. {symbol} - {name}
                </div>
                <div class="opportunity-score" style="background: {score_color};">
                    {score:.1f}/100
                </div>
            </div>
            
            <div class="opportunity-details">
                <div class="detail-item">
                    <div class="detail-label">Signal</div>
                    <div class="detail-value">
                        <span class="badge {conf_badge}">{prediction}</span>
                    </div>
                </div>
                
                <div class="detail-item">
                    <div class="detail-label">Confidence</div>
                    <div class="detail-value">{confidence:.1f}%</div>
                </div>
                
                <div class="detail-item">
                    <div class="detail-label">Current Price</div>
                    <div class="detail-value">${price:.2f}</div>
                </div>
                
                <div class="detail-item">
                    <div class="detail-label">RSI</div>
                    <div class="detail-value">{rsi:.1f}</div>
                </div>
                
                <div class="detail-item">
                    <div class="detail-label">Market Cap</div>
                    <div class="detail-value">${opp.get('market_cap', 0)/1e9:.2f}B</div>
                </div>
                
                <div class="detail-item">
                    <div class="detail-label">Beta</div>
                    <div class="detail-value">{opp.get('beta', 1.0):.2f}</div>
                </div>
            </div>
            
            <div class="opportunity-analysis">
                <strong>Analysis:</strong> 
                {self._generate_analysis_text(opp)}
            </div>
        </div>
"""
    
    def _generate_analysis_text(self, opp: Dict) -> str:
        """Generate analysis text for opportunity"""
        symbol = opp.get('symbol', 'Stock')
        prediction = opp.get('prediction', 'HOLD')
        confidence = opp.get('confidence', 0)
        technical = opp.get('technical', {})
        rsi = technical.get('rsi', 50)
        
        analysis_parts = []
        
        # Prediction strength
        if prediction == 'BUY':
            analysis_parts.append(f"<strong>Strong buy signal</strong> with {confidence:.1f}% confidence.")
        elif prediction == 'SELL':
            analysis_parts.append(f"Sell signal detected with {confidence:.1f}% confidence.")
        else:
            analysis_parts.append(f"Neutral position with {confidence:.1f}% confidence.")
        
        # RSI analysis
        if rsi < 30:
            analysis_parts.append("RSI indicates <strong>oversold conditions</strong> - potential buying opportunity.")
        elif rsi > 70:
            analysis_parts.append("RSI indicates <strong>overbought conditions</strong> - caution advised.")
        else:
            analysis_parts.append(f"RSI at {rsi:.1f} shows balanced market conditions.")
        
        # Price vs MA
        price_vs_ma20 = technical.get('price_vs_ma20', 0)
        if price_vs_ma20 > 2:
            analysis_parts.append("Trading <strong>above 20-day MA</strong>, showing upward momentum.")
        elif price_vs_ma20 < -2:
            analysis_parts.append("Trading <strong>below 20-day MA</strong>, potential support level.")
        
        return " ".join(analysis_parts)
    
    def _build_sector_section(self, sector_summary: Dict) -> str:
        """Build sector performance section"""
        if not sector_summary:
            return ""
        
        rows = ""
        for sector, data in sector_summary.items():
            count = data.get('total_stocks', 0)
            avg_score = data.get('avg_score', 0)
            
            # Outlook
            if avg_score >= 75:
                outlook = '<span class="badge badge-success">🟢 Strong</span>'
            elif avg_score >= 60:
                outlook = '<span class="badge badge-info">🟡 Moderate</span>'
            else:
                outlook = '<span class="badge badge-warning">🟠 Weak</span>'
            
            rows += f"""
                <tr>
                    <td><strong>{sector}</strong></td>
                    <td>{count}</td>
                    <td>{avg_score:.1f}</td>
                    <td>{outlook}</td>
                </tr>
"""
        
        return f"""
    <div class="section">
        <h2><span class="emoji">📊</span> Sector Performance</h2>
        <table>
            <thead>
                <tr>
                    <th>Sector</th>
                    <th>Opportunities</th>
                    <th>Avg Score</th>
                    <th>Outlook</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
"""
    
    def _build_watchlist_section(self, opportunities: List[Dict]) -> str:
        """Build watchlist section for near-buy signals"""
        # Filter stocks with scores 55-65 (near buy threshold)
        watchlist = [o for o in opportunities 
                     if 55 <= o.get('opportunity_score', 0) < 65][:5]
        
        if not watchlist:
            return ""
        
        items = ""
        for stock in watchlist:
            symbol = stock.get('symbol', 'N/A')
            score = stock.get('opportunity_score', 0)
            technical = stock.get('technical', {})
            rsi = technical.get('rsi', 50)
            
            reason = ""
            if rsi < 35:
                reason = "RSI entering oversold territory"
            elif 60 <= score < 65:
                reason = f"Near buy threshold (Score: {score:.1f})"
            else:
                reason = "Approaching key technical level"
            
            items += f"""
            <div class="watchlist-item">
                <strong>{symbol}</strong> - {stock.get('name', 'Unknown')} | {reason}
            </div>
"""
        
        return f"""
    <div class="section">
        <h2><span class="emoji">👀</span> Watch List (Near Buy Signals)</h2>
        {items}
    </div>
"""
    
    def _build_warnings_section(self, opportunities: List[Dict]) -> str:
        """Build warnings section for sell signals"""
        # Filter SELL signals
        warnings = [o for o in opportunities if o.get('prediction') == 'SELL'][:5]
        
        if not warnings:
            return ""
        
        items = ""
        for stock in warnings:
            symbol = stock.get('symbol', 'N/A')
            confidence = stock.get('confidence', 0)
            
            items += f"""
            <div class="warning-item">
                <strong>{symbol}</strong> - {stock.get('name', 'Unknown')} | 
                Sell signal (Confidence: {confidence:.1f}%)
            </div>
"""
        
        return f"""
    <div class="section">
        <h2><span class="emoji">⚠️</span> Caution Stocks (Sell Signals)</h2>
        {items}
    </div>
"""
    
    def _build_performance_section(self, system_stats: Dict) -> str:
        """Build system performance section"""
        total_scanned = system_stats.get('total_scanned', 0)
        processing_time = system_stats.get('processing_time_seconds', 0)
        buy_count = system_stats.get('buy_signals', 0)
        sell_count = system_stats.get('sell_signals', 0)
        
        # Convert seconds to readable format
        hours = int(processing_time / 3600)
        minutes = int((processing_time % 3600) / 60)
        time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        
        return f"""
    <div class="section">
        <h2><span class="emoji">⚙️</span> System Performance</h2>
        <table>
            <tr>
                <td><strong>Stocks Scanned</strong></td>
                <td>{total_scanned}</td>
            </tr>
            <tr>
                <td><strong>Buy Signals Generated</strong></td>
                <td><span class="badge badge-success">{buy_count}</span></td>
            </tr>
            <tr>
                <td><strong>Sell Signals Generated</strong></td>
                <td><span class="badge badge-danger">{sell_count}</span></td>
            </tr>
            <tr>
                <td><strong>Processing Time</strong></td>
                <td>{time_str}</td>
            </tr>
            <tr>
                <td><strong>LSTM Models Status</strong></td>
                <td>{system_stats.get('lstm_status', 'Not Available')}</td>
            </tr>
        </table>
    </div>
"""
    
    def _build_footer(self) -> str:
        """Build report footer"""
        return """
    <div class="footer">
        <p><strong>Disclaimer:</strong> This report is generated by automated AI/ML models and should not be considered financial advice. 
        Always conduct your own research and consult a licensed financial advisor before making investment decisions.</p>
        <p style="margin-top: 10px;">
            <em>Generated by FinBERT Overnight Stock Screening System v2.0</em>
        </p>
    </div>
    </div>
"""
    
    def _save_json_data(
        self,
        report_date: str,
        opportunities: List[Dict],
        spi_sentiment: Dict,
        sector_summary: Dict,
        system_stats: Dict
    ):
        """Save JSON data for programmatic access"""
        data = {
            'report_date': report_date,
            'generated_at': datetime.now(self.timezone).isoformat(),
            'opportunities': opportunities,
            'spi_sentiment': spi_sentiment,
            'sector_summary': sector_summary,
            'system_stats': system_stats
        }
        
        json_filename = f"{report_date}_data.json"
        json_path = self.report_dir / json_filename
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"JSON data saved: {json_path}")


# ============================================================================
# TEST HARNESS
# ============================================================================

def test_report_generator():
    """Test the report generator"""
    print("\n" + "="*80)
    print("REPORT GENERATOR TEST")
    print("="*80 + "\n")
    
    # Initialize generator
    generator = ReportGenerator()
    
    # Sample data
    opportunities = [
        {
            'symbol': 'ANZ.AX',
            'name': 'ANZ Group Holdings Limited',
            'price': 37.00,
            'market_cap': 110400000000,
            'beta': 1.1,
            'prediction': 'BUY',
            'confidence': 75,
            'opportunity_score': 82.5,
            'technical': {
                'rsi': 57.8,
                'ma_20': 36.5,
                'ma_50': 36.0,
                'price_vs_ma20': 1.37
            },
            'score_breakdown': {}
        },
        {
            'symbol': 'CBA.AX',
            'name': 'Commonwealth Bank of Australia',
            'price': 178.57,
            'market_cap': 298540000000,
            'beta': 1.0,
            'prediction': 'HOLD',
            'confidence': 68,
            'opportunity_score': 75.3,
            'technical': {
                'rsi': 68.4,
                'ma_20': 177.0,
                'ma_50': 175.0,
                'price_vs_ma20': 0.89
            },
            'score_breakdown': {}
        }
    ]
    
    spi_sentiment = {
        'sentiment_score': 65.0,
        'gap_prediction': {
            'predicted_gap_pct': 0.5,
            'confidence': 75,
            'direction': 'bullish'
        },
        'us_markets': {
            'SP500': {'change_pct': 0.8},
            'Nasdaq': {'change_pct': 1.2},
            'Dow': {'change_pct': 0.5}
        },
        'recommendation': {
            'stance': 'BUY',
            'message': 'Bullish sentiment. Favor long positions.',
            'risk_level': 'MEDIUM'
        }
    }
    
    sector_summary = {
        'Financials': {'total_stocks': 5, 'avg_score': 75.0},
        'Materials': {'total_stocks': 3, 'avg_score': 68.5}
    }
    
    system_stats = {
        'total_scanned': 240,
        'buy_signals': 15,
        'sell_signals': 8,
        'processing_time_seconds': 300,
        'lstm_status': 'Not Available'
    }
    
    print("Generating morning report...\n")
    
    # Generate report
    report_path = generator.generate_morning_report(
        opportunities=opportunities,
        spi_sentiment=spi_sentiment,
        sector_summary=sector_summary,
        system_stats=system_stats
    )
    
    print(f"✓ Report generated: {report_path}")
    print(f"✓ File size: {Path(report_path).stat().st_size / 1024:.1f} KB")
    print(f"\nOpen the report in a browser to view:")
    print(f"  file://{report_path}")


if __name__ == "__main__":
    test_report_generator()
