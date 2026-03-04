"""
Pipeline Report Loader (v1.3.15.164)

Automatically loads top 50 stocks from overnight pipeline reports
and provides them to the dashboard for paper trading.

Purpose: Address user request:
"Is there a way to get the top 50 stock symbols from each pipeline run 
into the list of stocks that the dashboard will send to the paper trading coordinator"

Features:
- Loads latest AU/UK/US pipeline reports
- Extracts top 50 stocks by opportunity_score
- Filters by minimum confidence threshold
- Combines multi-market watchlists
- Integrates with dashboard startup

Author: GenSpark AI Developer
Date: 2026-02-18
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class PipelineReportLoader:
    """
    Loads top stocks from overnight pipeline reports.
    
    Searches for latest reports from AU/UK/US pipelines and extracts
    the top 50 stocks by opportunity score for paper trading.
    """
    
    def __init__(self, base_path: Path = None):
        """
        Initialize Pipeline Report Loader
        
        Args:
            base_path: Base path to project (default: auto-detect)
        """
        if base_path is None:
            # Auto-detect: look for reports directory
            base_path = Path(__file__).parent.parent
        
        self.base_path = Path(base_path)
        self.report_dir = self.base_path / 'reports' / 'screening'
        
        logger.info(f"[LOADER] Pipeline Report Loader initialized")
        logger.info(f"[LOADER] Report directory: {self.report_dir}")
    
    def load_top_stocks(
        self,
        top_n: int = 50,
        markets: List[str] = None,
        min_confidence: float = 60.0,
        max_age_hours: int = 48
    ) -> Tuple[List[str], Dict]:
        """
        Load top N stocks from latest pipeline reports
        
        Args:
            top_n: Number of top stocks to return (default: 50)
            markets: Markets to load from ['AU', 'UK', 'US'], None = all
            min_confidence: Minimum prediction confidence (default: 60%)
            max_age_hours: Maximum report age in hours (default: 48)
            
        Returns:
            Tuple of (symbols_list, report_metadata)
            - symbols_list: List of stock symbols (e.g., ['RIO.AX', 'BHP.AX', ...])
            - report_metadata: Dict with report info per market
        """
        if markets is None:
            markets = ['AU', 'UK', 'US']
        
        logger.info(f"[LOADER] Loading top {top_n} stocks from {markets} markets")
        logger.info(f"[LOADER] Filters: confidence >={min_confidence}%, age <{max_age_hours}h")
        
        all_opportunities = []
        metadata = {}
        
        for market in markets:
            try:
                opportunities, report_info = self._load_market_report(
                    market=market,
                    max_age_hours=max_age_hours
                )
                
                if opportunities:
                    # Filter by confidence
                    filtered = [
                        opp for opp in opportunities 
                        if opp.get('confidence', 0) >= min_confidence
                    ]
                    
                    logger.info(f"[LOADER] {market}: {len(filtered)}/{len(opportunities)} stocks passed confidence filter")
                    
                    all_opportunities.extend(filtered)
                    metadata[market] = {
                        'report_found': True,
                        'report_path': report_info.get('path'),
                        'report_age_hours': report_info.get('age_hours'),
                        'stocks_loaded': len(filtered),
                        'stocks_total': len(opportunities)
                    }
                else:
                    logger.warning(f"[LOADER] {market}: No opportunities found in report")
                    metadata[market] = {
                        'report_found': False,
                        'error': 'No opportunities in report'
                    }
                    
            except Exception as e:
                logger.error(f"[LOADER] {market}: Error loading report: {e}")
                metadata[market] = {
                    'report_found': False,
                    'error': str(e)
                }
        
        if not all_opportunities:
            logger.warning("[LOADER] No opportunities loaded from any market")
            return [], metadata
        
        # Sort by opportunity_score (descending)
        all_opportunities.sort(
            key=lambda x: x.get('opportunity_score', 0),
            reverse=True
        )
        
        # Take top N
        top_opportunities = all_opportunities[:top_n]
        
        # Extract symbols
        symbols = [opp.get('symbol') for opp in top_opportunities if opp.get('symbol')]
        
        logger.info(f"[LOADER] Loaded {len(symbols)} top symbols from {len(metadata)} markets")
        
        # Log top 10 for verification
        if symbols:
            top_10 = top_opportunities[:10]
            logger.info("[LOADER] Top 10 stocks:")
            for i, opp in enumerate(top_10, 1):
                symbol = opp.get('symbol', 'N/A')
                score = opp.get('opportunity_score', 0)
                conf = opp.get('confidence', 0)
                pred = opp.get('prediction', 'N/A')
                logger.info(f"  {i:2d}. {symbol:10s} Score: {score:5.1f} Conf: {conf:5.1f}% Pred: {pred}")
        
        return symbols, metadata
    
    def _load_market_report(
        self,
        market: str,
        max_age_hours: int
    ) -> Tuple[List[Dict], Dict]:
        """
        Load report for specific market
        
        Args:
            market: Market code ('AU', 'UK', 'US')
            max_age_hours: Maximum age in hours
            
        Returns:
            Tuple of (opportunities, report_info)
        """
        market_lower = market.lower()
        
        # Look for report files (multiple possible names)
        report_patterns = [
            f'{market_lower}_morning_report.json',
            f'{market_lower}_morning_report_*.json',
            f'*{market_lower}*report*.json'
        ]
        
        report_file = None
        
        # Try to find report
        if self.report_dir.exists():
            for pattern in report_patterns:
                files = list(self.report_dir.glob(pattern))
                if files:
                    # Get most recent
                    report_file = max(files, key=lambda p: p.stat().st_mtime)
                    break
        
        if not report_file or not report_file.exists():
            raise FileNotFoundError(f"No report found for {market} in {self.report_dir}")
        
        # Check age
        file_mtime = datetime.fromtimestamp(report_file.stat().st_mtime)
        age_hours = (datetime.now() - file_mtime).total_seconds() / 3600
        
        if age_hours > max_age_hours:
            logger.warning(f"[LOADER] {market}: Report is {age_hours:.1f}h old (max {max_age_hours}h)")
            # Don't raise error, just warn and continue
        
        # Load JSON
        with open(report_file, 'r') as f:
            data = json.load(f)
        
        # Extract opportunities (may be in different keys)
        opportunities = []
        
        # Try different possible keys
        if 'opportunities' in data:
            opportunities = data['opportunities']
        elif 'top_opportunities' in data:
            opportunities = data['top_opportunities']
        elif 'stocks' in data:
            opportunities = data['stocks']
        elif 'scored_stocks' in data:
            opportunities = data['scored_stocks']
        
        report_info = {
            'path': str(report_file),
            'age_hours': age_hours,
            'timestamp': data.get('timestamp', data.get('generated_at', 'unknown'))
        }
        
        logger.info(f"[LOADER] {market}: Loaded {len(opportunities)} opportunities from {report_file.name} (age: {age_hours:.1f}h)")
        
        return opportunities, report_info
    
    def get_report_summary(self) -> Dict:
        """
        Get summary of available reports
        
        Returns:
            Dict with report status for each market
        """
        summary = {}
        
        for market in ['AU', 'UK', 'US']:
            try:
                _, report_info = self._load_market_report(market, max_age_hours=999999)
                summary[market] = {
                    'available': True,
                    'path': report_info['path'],
                    'age_hours': report_info['age_hours'],
                    'timestamp': report_info['timestamp']
                }
            except Exception as e:
                summary[market] = {
                    'available': False,
                    'error': str(e)
                }
        
        return summary


def auto_load_pipeline_stocks(
    top_n: int = 50,
    markets: List[str] = None,
    min_confidence: float = 60.0,
    max_age_hours: int = 48,
    base_path: Path = None
) -> Tuple[List[str], Dict]:
    """
    Convenience function to auto-load top stocks from pipeline reports
    
    Args:
        top_n: Number of top stocks (default: 50)
        markets: Markets to load ['AU', 'UK', 'US'] (default: all)
        min_confidence: Minimum confidence % (default: 60%)
        max_age_hours: Maximum report age (default: 48h)
        base_path: Project base path (default: auto-detect)
        
    Returns:
        Tuple of (symbols, metadata)
        
    Example:
        symbols, metadata = auto_load_pipeline_stocks(top_n=50, markets=['AU', 'UK'])
        # symbols = ['RIO.AX', 'BHP.AX', 'BP.L', 'HSBA.L', ...]
    """
    loader = PipelineReportLoader(base_path=base_path)
    return loader.load_top_stocks(
        top_n=top_n,
        markets=markets,
        min_confidence=min_confidence,
        max_age_hours=max_age_hours
    )


# ============================================================================
# TEST HARNESS
# ============================================================================

def test_pipeline_report_loader():
    """Test the pipeline report loader"""
    print("\n" + "="*80)
    print("PIPELINE REPORT LOADER TEST")
    print("="*80 + "\n")
    
    # Initialize loader
    loader = PipelineReportLoader()
    
    # Get report summary
    print("Report Summary:")
    print("-" * 80)
    summary = loader.get_report_summary()
    for market, info in summary.items():
        if info.get('available'):
            print(f"{market:3s}: [OK] Available (age: {info['age_hours']:.1f}h)")
            print(f"     {info['path']}")
        else:
            print(f"{market:3s}: ✗ Not available - {info.get('error', 'Unknown')}")
    print()
    
    # Load top 50 stocks
    print("Loading Top 50 Stocks (multi-market):")
    print("-" * 80)
    
    symbols, metadata = loader.load_top_stocks(
        top_n=50,
        markets=['AU', 'UK', 'US'],
        min_confidence=60.0,
        max_age_hours=48
    )
    
    print(f"\nLoaded {len(symbols)} symbols:")
    print()
    
    # Group by market
    au_symbols = [s for s in symbols if s.endswith('.AX')]
    uk_symbols = [s for s in symbols if s.endswith('.L')]
    us_symbols = [s for s in symbols if not (s.endswith('.AX') or s.endswith('.L'))]
    
    print(f"AU Stocks ({len(au_symbols)}): {', '.join(au_symbols[:10])}{'...' if len(au_symbols) > 10 else ''}")
    print(f"UK Stocks ({len(uk_symbols)}): {', '.join(uk_symbols[:10])}{'...' if len(uk_symbols) > 10 else ''}")
    print(f"US Stocks ({len(us_symbols)}): {', '.join(us_symbols[:10])}{'...' if len(us_symbols) > 10 else ''}")
    print()
    
    # Metadata
    print("Metadata:")
    print("-" * 80)
    for market, info in metadata.items():
        if info.get('report_found'):
            print(f"{market}: {info['stocks_loaded']} stocks loaded (age: {info['report_age_hours']:.1f}h)")
        else:
            print(f"{market}: {info.get('error', 'Unknown error')}")
    print()
    
    print("="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")
    
    return symbols, metadata


if __name__ == "__main__":
    # Run test
    test_pipeline_report_loader()
