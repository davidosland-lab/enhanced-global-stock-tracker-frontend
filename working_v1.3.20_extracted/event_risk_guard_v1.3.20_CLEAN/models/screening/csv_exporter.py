"""
CSV Exporter Module

Exports screening results to CSV format with comprehensive event risk data.
Includes all stock fundamentals, predictions, opportunity scores, and event risk assessments.

Features:
- Enhanced CSV export with 50+ columns
- Event risk assessment fields (Basel III, earnings, dividends)
- Position sizing recommendations
- Risk score and haircut calculations
- Sortable by multiple criteria
- Excel-compatible formatting
"""

import csv
import logging
from typing import Dict, List
from datetime import datetime
from pathlib import Path
import pytz

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CSVExporter:
    """
    Exports screening results to CSV format with event risk data.
    """
    
    def __init__(self, output_dir: str = None):
        """
        Initialize CSV Exporter
        
        Args:
            output_dir: Directory to save CSV files (default: reports/csv)
        """
        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / "reports" / "csv"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timezone = pytz.timezone('Australia/Sydney')
        
        logger.info("CSV Exporter initialized")
        logger.info(f"  Output Directory: {self.output_dir}")
    
    def export_screening_results(
        self,
        opportunities: List[Dict],
        spi_sentiment: Dict = None,
        filename: str = None
    ) -> str:
        """
        Export screening results to CSV
        
        Args:
            opportunities: List of scored opportunities with event risk data
            spi_sentiment: Market sentiment data (optional)
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to generated CSV file
        """
        logger.info(f"Exporting {len(opportunities)} opportunities to CSV...")
        
        # Generate filename if not provided
        if filename is None:
            date_str = datetime.now(self.timezone).strftime('%Y-%m-%d')
            filename = f"{date_str}_screening_results.csv"
        
        csv_path = self.output_dir / filename
        
        # Define CSV columns (comprehensive schema)
        columns = self._get_csv_columns()
        
        # Write CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
            writer.writeheader()
            
            for opp in opportunities:
                row = self._prepare_csv_row(opp, spi_sentiment)
                writer.writerow(row)
        
        logger.info(f"✓ CSV exported: {csv_path}")
        logger.info(f"  File size: {csv_path.stat().st_size / 1024:.1f} KB")
        logger.info(f"  Rows: {len(opportunities) + 1} (including header)")
        
        return str(csv_path)
    
    def _get_csv_columns(self) -> List[str]:
        """
        Define comprehensive CSV column schema
        
        Returns 50+ columns including:
        - Stock fundamentals (symbol, name, price, market_cap, etc.)
        - Technical indicators (RSI, MA, volume, etc.)
        - Predictions (signal, confidence, predicted_return)
        - Opportunity scores (total score, breakdown)
        - Event risk fields (risk_score, event_type, days_to_event, etc.)
        - Position sizing (weight_haircut, suggested_hedge)
        """
        return [
            # Basic Stock Info
            'symbol',
            'name',
            'sector',
            'price',
            'market_cap',
            'volume',
            'avg_volume',
            'beta',
            
            # Technical Indicators
            'rsi',
            'ma_20',
            'ma_50',
            'ma_200',
            'price_vs_ma20',
            'price_vs_ma50',
            'macd',
            'macd_signal',
            'bb_position',
            'volatility_30d',
            'volume_ratio',
            
            # Prediction & Signal
            'prediction',
            'confidence',
            'predicted_return',
            'prediction_source',  # 'LSTM', 'FinBERT', or 'Hybrid'
            
            # Opportunity Scoring
            'opportunity_score',
            'score_rank',
            'technical_score',
            'sentiment_score',
            'momentum_score',
            'value_score',
            
            # Event Risk Assessment (🆕 Enhanced)
            'event_risk_score',              # 0-1 scale (1=highest risk)
            'event_type',                    # 'basel_iii', 'earnings', 'dividend', 'regulatory'
            'has_upcoming_event',            # True/False
            'days_to_event',                 # Integer (days until event)
            'event_title',                   # Event description
            'event_url',                     # Source URL
            'event_skip_trading',            # True if recommended to skip
            'event_warning',                 # Warning message
            'event_weight_haircut',          # 0-0.70 (fraction to reduce position)
            'event_avg_sentiment_72h',       # -1 to 1 (FinBERT sentiment)
            'event_vol_spike',               # True if volatility spike detected
            'event_suggested_hedge_beta',    # Beta for hedge calculation
            'event_suggested_hedge_ratio',   # Suggested hedge ratio
            
            # Market Sentiment
            'market_sentiment_score',
            'market_gap_prediction',
            'market_recommendation',
            
            # Metadata
            'analysis_timestamp',
            'data_source',
            'notes'
        ]
    
    def _prepare_csv_row(self, opp: Dict, spi_sentiment: Dict = None) -> Dict:
        """
        Prepare CSV row from opportunity dictionary
        
        Args:
            opp: Opportunity dictionary
            spi_sentiment: Market sentiment data
            
        Returns:
            Dictionary with CSV column values
        """
        # Get technical data
        technical = opp.get('technical', {})
        
        # Get score breakdown
        breakdown = opp.get('score_breakdown', {})
        
        # Prepare base row
        row = {
            # Basic Stock Info
            'symbol': opp.get('symbol', ''),
            'name': opp.get('name', ''),
            'sector': opp.get('sector', ''),
            'price': self._format_float(opp.get('price', 0), 2),
            'market_cap': self._format_int(opp.get('market_cap', 0)),
            'volume': self._format_int(opp.get('volume', 0)),
            'avg_volume': self._format_int(opp.get('avg_volume', 0)),
            'beta': self._format_float(opp.get('beta', 0), 2),
            
            # Technical Indicators
            'rsi': self._format_float(technical.get('rsi', 0), 2),
            'ma_20': self._format_float(technical.get('ma_20', 0), 2),
            'ma_50': self._format_float(technical.get('ma_50', 0), 2),
            'ma_200': self._format_float(technical.get('ma_200', 0), 2),
            'price_vs_ma20': self._format_float(technical.get('price_vs_ma20', 0), 2),
            'price_vs_ma50': self._format_float(technical.get('price_vs_ma50', 0), 2),
            'macd': self._format_float(technical.get('macd', 0), 4),
            'macd_signal': self._format_float(technical.get('macd_signal', 0), 4),
            'bb_position': self._format_float(technical.get('bb_position', 0), 2),
            'volatility_30d': self._format_float(technical.get('volatility_30d', 0), 4),
            'volume_ratio': self._format_float(technical.get('volume_ratio', 0), 2),
            
            # Prediction & Signal
            'prediction': opp.get('prediction', 'HOLD'),
            'confidence': self._format_float(opp.get('confidence', 0), 1),
            'predicted_return': self._format_float(opp.get('predicted_return', 0), 2),
            'prediction_source': opp.get('prediction_source', 'Hybrid'),
            
            # Opportunity Scoring
            'opportunity_score': self._format_float(opp.get('opportunity_score', 0), 1),
            'score_rank': opp.get('score_rank', ''),
            'technical_score': self._format_float(breakdown.get('technical_score', 0), 1),
            'sentiment_score': self._format_float(breakdown.get('sentiment_score', 0), 1),
            'momentum_score': self._format_float(breakdown.get('momentum_score', 0), 1),
            'value_score': self._format_float(breakdown.get('value_score', 0), 1),
            
            # Event Risk Assessment (🆕 Enhanced)
            'event_risk_score': self._format_float(opp.get('event_risk_score', 0), 3),
            'event_type': opp.get('event_type', ''),
            'has_upcoming_event': self._format_bool(opp.get('event_type', '') != ''),
            'days_to_event': self._format_int(opp.get('days_to_event')) if opp.get('days_to_event') is not None else '',
            'event_title': opp.get('event_title', ''),
            'event_url': opp.get('event_url', ''),
            'event_skip_trading': self._format_bool(opp.get('event_skip_trading', False)),
            'event_warning': opp.get('event_warning', ''),
            'event_weight_haircut': self._format_float(opp.get('event_weight_haircut', 0), 2),
            'event_avg_sentiment_72h': self._format_float(opp.get('event_avg_sentiment_72h', 0), 3),
            'event_vol_spike': self._format_bool(opp.get('event_vol_spike', False)),
            'event_suggested_hedge_beta': self._format_float(opp.get('event_suggested_hedge_beta', 0), 2),
            'event_suggested_hedge_ratio': self._format_float(opp.get('event_suggested_hedge_ratio', 0), 2),
            
            # Market Sentiment
            'market_sentiment_score': '',
            'market_gap_prediction': '',
            'market_recommendation': '',
            
            # Metadata
            'analysis_timestamp': datetime.now(self.timezone).isoformat(),
            'data_source': 'FinBERT Overnight Screener v2.0',
            'notes': opp.get('skip_reason', '')  # Add skip reason if present
        }
        
        # Add market sentiment if available
        if spi_sentiment:
            row['market_sentiment_score'] = self._format_float(spi_sentiment.get('sentiment_score', 0), 1)
            gap = spi_sentiment.get('gap_prediction', {})
            row['market_gap_prediction'] = self._format_float(gap.get('predicted_gap_pct', 0), 2)
            rec = spi_sentiment.get('recommendation', {})
            row['market_recommendation'] = rec.get('stance', '')
        
        return row
    
    def _format_float(self, value, decimals: int = 2) -> str:
        """Format float value with specified decimals"""
        try:
            if value is None or value == '' or (isinstance(value, float) and (value != value)):  # Check for NaN
                return ''
            return f"{float(value):.{decimals}f}"
        except (ValueError, TypeError):
            return ''
    
    def _format_int(self, value=None) -> str:
        """Format integer value"""
        try:
            if value is None or value == '':
                return ''
            return str(int(value))
        except (ValueError, TypeError):
            return ''
    
    def _format_bool(self, value) -> str:
        """Format boolean value"""
        if value is None or value == '':
            return 'FALSE'
        return 'TRUE' if value else 'FALSE'
    
    def export_event_risk_summary(self, opportunities: List[Dict], filename: str = None) -> str:
        """
        Export event risk summary CSV (focused on stocks with events)
        
        Args:
            opportunities: List of opportunities
            filename: Output filename
            
        Returns:
            Path to generated CSV file
        """
        # Filter stocks with upcoming events
        event_stocks = [
            opp for opp in opportunities
            if opp.get('event_type') or opp.get('event_risk_score', 0) > 0
        ]
        
        if not event_stocks:
            logger.info("No stocks with upcoming events found")
            return None
        
        logger.info(f"Exporting {len(event_stocks)} stocks with event risk to CSV...")
        
        # Generate filename
        if filename is None:
            date_str = datetime.now(self.timezone).strftime('%Y-%m-%d')
            filename = f"{date_str}_event_risk_summary.csv"
        
        csv_path = self.output_dir / filename
        
        # Define event risk columns
        columns = [
            'symbol',
            'name',
            'price',
            'prediction',
            'confidence',
            'opportunity_score',
            'event_risk_score',
            'event_type',
            'days_to_event',
            'event_title',
            'event_skip_trading',
            'event_weight_haircut',
            'event_warning',
            'event_avg_sentiment_72h',
            'event_vol_spike',
            'suggested_action'
        ]
        
        # Write CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            
            for opp in sorted(event_stocks, key=lambda x: x.get('event_risk_score', 0), reverse=True):
                row = {
                    'symbol': opp.get('symbol', ''),
                    'name': opp.get('name', ''),
                    'price': self._format_float(opp.get('price', 0), 2),
                    'prediction': opp.get('prediction', 'HOLD'),
                    'confidence': self._format_float(opp.get('confidence', 0), 1),
                    'opportunity_score': self._format_float(opp.get('opportunity_score', 0), 1),
                    'event_risk_score': self._format_float(opp.get('event_risk_score', 0), 3),
                    'event_type': opp.get('event_type', ''),
                    'days_to_event': self._format_int(opp.get('days_to_event')),
                    'event_title': opp.get('event_title', ''),
                    'event_skip_trading': self._format_bool(opp.get('event_skip_trading', False)),
                    'event_weight_haircut': self._format_float(opp.get('event_weight_haircut', 0), 2),
                    'event_warning': opp.get('event_warning', ''),
                    'event_avg_sentiment_72h': self._format_float(opp.get('event_avg_sentiment_72h', 0), 3),
                    'event_vol_spike': self._format_bool(opp.get('event_vol_spike', False)),
                    'suggested_action': self._get_suggested_action(opp)
                }
                writer.writerow(row)
        
        logger.info(f"✓ Event risk summary exported: {csv_path}")
        return str(csv_path)
    
    def _get_suggested_action(self, opp: Dict) -> str:
        """Generate suggested action based on event risk"""
        if opp.get('event_skip_trading', False):
            return 'SKIP - Sit out event window'
        
        risk_score = opp.get('event_risk_score', 0)
        haircut = opp.get('event_weight_haircut', 0)
        
        if risk_score >= 0.7:
            return f'REDUCE - Apply {haircut*100:.0f}% position haircut'
        elif risk_score >= 0.5:
            return f'CAUTION - Reduce size by {haircut*100:.0f}%'
        elif risk_score >= 0.25:
            return 'MONITOR - Small position reduction advised'
        else:
            return 'NORMAL - Standard position sizing'


# ============================================================================
# TEST HARNESS
# ============================================================================

def test_csv_exporter():
    """Test the CSV exporter"""
    print("\n" + "="*80)
    print("CSV EXPORTER TEST")
    print("="*80 + "\n")
    
    # Initialize exporter
    exporter = CSVExporter()
    
    # Sample opportunities with event risk data
    opportunities = [
        {
            'symbol': 'CBA.AX',
            'name': 'Commonwealth Bank of Australia',
            'sector': 'Financials',
            'price': 178.57,
            'market_cap': 298540000000,
            'volume': 3500000,
            'avg_volume': 3200000,
            'beta': 1.0,
            'technical': {
                'rsi': 68.4,
                'ma_20': 177.0,
                'ma_50': 175.0,
                'price_vs_ma20': 0.89,
                'volatility_30d': 0.025
            },
            'prediction': 'HOLD',
            'confidence': 45.0,  # Reduced by event risk
            'predicted_return': 0.5,
            'opportunity_score': 58.3,
            'score_breakdown': {
                'technical_score': 65,
                'sentiment_score': 50,
                'momentum_score': 60
            },
            # Event Risk Fields
            'event_risk_score': 0.85,
            'event_type': 'basel_iii',
            'days_to_event': 2,
            'event_title': 'September Quarter 2024 Basel III Pillar 3 Disclosure',
            'event_url': 'https://www.asx.com.au/...',
            'event_skip_trading': True,
            'event_warning': '⚠️ REGULATORY: Basel III report in 2 days (risk: 0.85). Recommend SKIP.',
            'event_weight_haircut': 0.70,
            'event_avg_sentiment_72h': -0.15,
            'event_vol_spike': True,
            'event_suggested_hedge_beta': 1.0,
            'event_suggested_hedge_ratio': 0.8
        },
        {
            'symbol': 'ANZ.AX',
            'name': 'ANZ Group Holdings Limited',
            'sector': 'Financials',
            'price': 37.00,
            'market_cap': 110400000000,
            'volume': 5000000,
            'avg_volume': 4800000,
            'beta': 1.1,
            'technical': {
                'rsi': 57.8,
                'ma_20': 36.5,
                'ma_50': 36.0,
                'price_vs_ma20': 1.37,
                'volatility_30d': 0.020
            },
            'prediction': 'BUY',
            'confidence': 65.0,  # Reduced from 75
            'predicted_return': 3.2,
            'opportunity_score': 75.5,
            'score_breakdown': {
                'technical_score': 78,
                'sentiment_score': 72,
                'momentum_score': 76
            },
            # Event Risk Fields
            'event_risk_score': 0.45,
            'event_type': 'earnings',
            'days_to_event': 5,
            'event_title': 'Q1 2025 Trading Update',
            'event_url': 'https://www.asx.com.au/...',
            'event_skip_trading': False,
            'event_warning': '⚡ CAUTION: Earnings in 5 days (risk: 0.45). Position haircut: 45%.',
            'event_weight_haircut': 0.45,
            'event_avg_sentiment_72h': 0.05,
            'event_vol_spike': False,
            'event_suggested_hedge_beta': 1.1,
            'event_suggested_hedge_ratio': 0.5
        }
    ]
    
    spi_sentiment = {
        'sentiment_score': 65.0,
        'gap_prediction': {
            'predicted_gap_pct': 0.5,
            'direction': 'bullish'
        },
        'recommendation': {
            'stance': 'BUY'
        }
    }
    
    print("Exporting full screening results...\n")
    csv_path = exporter.export_screening_results(opportunities, spi_sentiment)
    print(f"✓ Full results: {csv_path}\n")
    
    print("Exporting event risk summary...\n")
    event_csv_path = exporter.export_event_risk_summary(opportunities)
    print(f"✓ Event risk summary: {event_csv_path}\n")
    
    print("="*80)
    print("CSV Export Test Complete!")
    print("="*80)


if __name__ == "__main__":
    test_csv_exporter()
