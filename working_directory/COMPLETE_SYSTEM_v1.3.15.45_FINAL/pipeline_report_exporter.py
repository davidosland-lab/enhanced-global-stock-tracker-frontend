"""
Pipeline Report Exporter
========================

Shared module for exporting pipeline results to JSON format
compatible with the trading integration system.

Usage:
    from pipeline_report_exporter import PipelineReportExporter
    
    exporter = PipelineReportExporter()
    exporter.save_morning_report(results, market='US')
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PipelineReportExporter:
    """Exports pipeline results to JSON format for trading integration"""
    
    def __init__(self, reports_dir: Optional[Path] = None):
        """
        Initialize exporter
        
        Args:
            reports_dir: Directory for saving reports (default: reports/screening)
        """
        self.reports_dir = reports_dir or Path('reports/screening')
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def save_morning_report(
        self,
        results: Dict[str, Any],
        market: str,
        sentiment_score: Optional[float] = None,
        recommendation: Optional[str] = None
    ) -> Path:
        """
        Save morning report in format compatible with trading integration
        
        Args:
            results: Pipeline execution results
            market: Market code ('AU', 'US', 'UK')
            sentiment_score: Override sentiment score (0-100)
            recommendation: Override recommendation
            
        Returns:
            Path to saved report
        """
        # Extract or calculate sentiment
        if sentiment_score is None:
            sentiment_score = self._extract_sentiment_score(results)
        
        if recommendation is None:
            recommendation = self._determine_recommendation(sentiment_score)
        
        # Build morning report
        morning_report = {
            'timestamp': datetime.now().isoformat(),
            'market': market.upper(),
            'market_sentiment': {
                'score': sentiment_score,
                'recommendation': recommendation,
                'confidence': self._determine_confidence(results, sentiment_score),
                'predicted_gap_pct': self._extract_predicted_gap(results)
            },
            'volatility': {
                'level': self._extract_volatility_level(results)
            },
            'risk': {
                'rating': self._extract_risk_rating(results)
            },
            'top_opportunities': self._extract_top_opportunities(results),
            'regime_data': self._extract_regime_data(results),
            'statistics': self._extract_statistics(results),
            'full_results': results  # Include full results for reference
        }
        
        # Save to file
        report_path = self.reports_dir / f'{market.lower()}_morning_report.json'
        
        with open(report_path, 'w') as f:
            json.dump(morning_report, f, indent=2, default=str)
        
        logger.info(f"[OK] Morning report saved: {report_path}")
        logger.info(f"  Market: {market}")
        logger.info(f"  Sentiment: {sentiment_score:.1f}/100")
        logger.info(f"  Recommendation: {recommendation}")
        logger.info(f"  Top Opportunities: {len(morning_report['top_opportunities'])}")
        
        return report_path
    
    def _extract_sentiment_score(self, results: Dict) -> float:
        """Extract sentiment score from results"""
        # Try various possible keys
        if 'sentiment_score' in results:
            return float(results['sentiment_score'])
        elif 'market_sentiment' in results:
            ms = results['market_sentiment']
            if isinstance(ms, dict) and 'score' in ms:
                return float(ms['score'])
            elif isinstance(ms, (int, float)):
                return float(ms)
        elif 'summary' in results and 'spi_sentiment_score' in results['summary']:
            return float(results['summary']['spi_sentiment_score'])
        
        # Default to neutral
        logger.warning("Could not extract sentiment score, defaulting to 50")
        return 50.0
    
    def _determine_recommendation(self, sentiment_score: float) -> str:
        """Determine recommendation from sentiment score"""
        if sentiment_score >= 70:
            return 'STRONG_BUY'
        elif sentiment_score >= 60:
            return 'BUY'
        elif sentiment_score >= 55:
            return 'NEUTRAL'
        elif sentiment_score >= 40:
            return 'HOLD'
        elif sentiment_score >= 30:
            return 'REDUCE'
        else:
            return 'STRONG_SELL'
    
    def _determine_confidence(self, results: Dict, sentiment_score: float) -> str:
        """Determine confidence level"""
        # Check if results have confidence
        if 'confidence' in results:
            conf = results['confidence']
            if isinstance(conf, str):
                return conf
            elif isinstance(conf, (int, float)):
                if conf >= 0.7:
                    return 'HIGH'
                elif conf >= 0.5:
                    return 'MODERATE'
                else:
                    return 'LOW'
        
        # Check regime confidence
        regime_data = results.get('regime_data', {})
        if 'confidence' in regime_data:
            conf = regime_data['confidence']
            if conf >= 0.7:
                return 'HIGH'
            elif conf >= 0.5:
                return 'MODERATE'
            else:
                return 'LOW'
        
        # Default based on sentiment extremity
        if sentiment_score >= 70 or sentiment_score <= 30:
            return 'HIGH'
        elif sentiment_score >= 60 or sentiment_score <= 40:
            return 'MODERATE'
        else:
            return 'LOW'
    
    def _extract_predicted_gap(self, results: Dict) -> float:
        """Extract predicted gap percentage"""
        if 'predicted_gap' in results:
            return float(results['predicted_gap'])
        elif 'gap_prediction' in results:
            gap = results['gap_prediction']
            if isinstance(gap, dict) and 'predicted_gap_pct' in gap:
                return float(gap['predicted_gap_pct'])
            elif isinstance(gap, (int, float)):
                return float(gap)
        
        return 0.0
    
    def _extract_volatility_level(self, results: Dict) -> str:
        """Extract volatility level"""
        # Check various possible locations
        if 'volatility' in results:
            vol = results['volatility']
            if isinstance(vol, dict) and 'level' in vol:
                return vol['level']
            elif isinstance(vol, str):
                return vol
        
        if 'market_data' in results:
            md = results['market_data']
            if 'vix_level' in md:
                vix = md['vix_level']
                if isinstance(vix, str):
                    return vix
        
        return 'Normal'
    
    def _extract_risk_rating(self, results: Dict) -> str:
        """Extract risk rating"""
        if 'risk' in results:
            risk = results['risk']
            if isinstance(risk, dict) and 'rating' in risk:
                return risk['rating']
            elif isinstance(risk, str):
                return risk
        
        if 'risk_rating' in results:
            return results['risk_rating']
        
        return 'Moderate'
    
    def _extract_top_opportunities(self, results: Dict) -> list:
        """Extract top opportunities from results"""
        opportunities = []
        
        # Try to find opportunities in results
        if 'top_opportunities' in results:
            opps = results['top_opportunities']
            if isinstance(opps, list):
                opportunities = opps[:10]  # Top 10
        elif 'opportunities' in results:
            opps = results['opportunities']
            if isinstance(opps, list):
                # Sort by opportunity_score if available
                sorted_opps = sorted(
                    opps,
                    key=lambda x: x.get('opportunity_score', 0),
                    reverse=True
                )
                opportunities = sorted_opps[:10]
        
        # Ensure each opportunity has required fields
        formatted_opps = []
        for opp in opportunities:
            formatted_opp = {
                'symbol': opp.get('symbol', 'UNKNOWN'),
                'opportunity_score': opp.get('opportunity_score', 0),
                'prediction': opp.get('prediction', 'HOLD'),
                'confidence': opp.get('confidence', 0),
                'price': opp.get('price', 0),
                'sector': opp.get('sector', 'Unknown')
            }
            
            # Add optional fields if present
            if 'event_risk_score' in opp:
                formatted_opp['event_risk_score'] = opp['event_risk_score']
            if 'event_warning' in opp:
                formatted_opp['event_warning'] = opp['event_warning']
            if 'finbert_sentiment' in opp:
                formatted_opp['finbert_sentiment'] = opp['finbert_sentiment']
            
            formatted_opps.append(formatted_opp)
        
        return formatted_opps
    
    def _extract_regime_data(self, results: Dict) -> Dict:
        """Extract regime data"""
        if 'regime_data' in results:
            regime = results['regime_data']
            if isinstance(regime, dict):
                return {
                    'primary_regime': regime.get('primary_regime', 'UNKNOWN'),
                    'regime_strength': regime.get('regime_strength', 0),
                    'confidence': regime.get('confidence', 0),
                    'regime_explanation': regime.get('regime_explanation', ''),
                    'sector_impacts': regime.get('sector_impacts', {})
                }
        
        # Check for regime in results
        if 'regime' in results:
            return {
                'primary_regime': str(results['regime']),
                'regime_strength': results.get('strength', 0),
                'confidence': results.get('confidence', 0),
                'regime_explanation': results.get('explanation', '')
            }
        
        return {
            'primary_regime': 'UNKNOWN',
            'regime_strength': 0,
            'confidence': 0,
            'regime_explanation': 'No regime data available'
        }
    
    def _extract_statistics(self, results: Dict) -> Dict:
        """Extract execution statistics"""
        stats = {}
        
        if 'statistics' in results:
            return results['statistics']
        
        # Build from available fields
        if 'summary' in results:
            summary = results['summary']
            stats['total_stocks_scanned'] = summary.get('total_stocks', 0)
            stats['opportunities_found'] = summary.get('opportunities_count', 0)
            stats['high_confidence_count'] = summary.get('high_confidence_count', 0)
        
        if 'execution_time_minutes' in results:
            stats['execution_time_minutes'] = results['execution_time_minutes']
        
        return stats


# Convenience function for quick exports
def export_pipeline_results(results: Dict, market: str, reports_dir: Optional[Path] = None) -> Path:
    """
    Quick export function
    
    Args:
        results: Pipeline results
        market: Market code
        reports_dir: Optional custom reports directory
        
    Returns:
        Path to saved report
    """
    exporter = PipelineReportExporter(reports_dir)
    return exporter.save_morning_report(results, market)


if __name__ == "__main__":
    # Test with mock data
    mock_results = {
        'sentiment_score': 72.5,
        'confidence': 0.85,
        'regime_data': {
            'primary_regime': 'US_TECH_RISK_ON',
            'regime_strength': 0.65,
            'confidence': 0.82,
            'regime_explanation': 'Strong tech sector rally'
        },
        'top_opportunities': [
            {'symbol': 'AAPL', 'opportunity_score': 88.5, 'prediction': 'BUY', 'confidence': 87.2, 'price': 182.45, 'sector': 'Technology'},
            {'symbol': 'MSFT', 'opportunity_score': 85.3, 'prediction': 'BUY', 'confidence': 84.1, 'price': 378.90, 'sector': 'Technology'},
            {'symbol': 'GOOGL', 'opportunity_score': 79.6, 'prediction': 'BUY', 'confidence': 76.2, 'price': 142.35, 'sector': 'Technology'}
        ],
        'statistics': {
            'total_stocks_scanned': 240,
            'opportunities_found': 15,
            'high_confidence_count': 8,
            'execution_time_minutes': 42.5
        }
    }
    
    print("Testing Pipeline Report Exporter...")
    print("="*60)
    
    exporter = PipelineReportExporter()
    report_path = exporter.save_morning_report(mock_results, 'US')
    
    print(f"\n[OK] Test report saved: {report_path}")
    print("\nReport contents:")
    with open(report_path, 'r') as f:
        report = json.load(f)
    print(json.dumps(report, indent=2, default=str)[:500] + "...")
