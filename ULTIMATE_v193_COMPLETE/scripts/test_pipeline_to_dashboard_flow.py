#!/usr/bin/env python3
"""
Pipeline-to-Dashboard Signal Flow Diagnostic
=============================================

Tests the complete flow from overnight pipeline output to trading dashboard signals:

1. Pipeline Output -> Morning Report JSON
2. Morning Report -> Signal Adapter
3. Signal Adapter -> Trading Signals (BUY/SELL)
4. Trading Signals -> Dashboard Execution

This diagnostic validates:
- Pipeline report format and data
- Signal adapter can read reports
- ML swing signals can be generated
- BUY/SELL signals are properly created
- Position sizing is calculated
- Dashboard-ready signals are produced

Author: Trading System v1.3.15.158
Date: 2026-02-17
"""

import json
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import traceback

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import signal adapter
try:
    from scripts.pipeline_signal_adapter_v3 import EnhancedPipelineSignalAdapter
    ADAPTER_AVAILABLE = True
except ImportError as e:
    ADAPTER_AVAILABLE = False
    logger.error(f"[X] Cannot import signal adapter: {e}")


class PipelineToDashboardDiagnostic:
    """
    Diagnostic tool to test pipeline -> dashboard signal flow
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize diagnostic"""
        self.base_path = base_path or Path(__file__).parent.parent
        self.reports_path = self.base_path / 'reports' / 'screening'
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'summary': {}
        }
    
    def log_test(self, test_name: str, status: str, details: str, data: Optional[Dict] = None):
        """Log a test result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'data': data or {}
        }
        self.results['tests'].append(result)
        
        icon = {
            'PASS': '[OK]',
            'FAIL': '[ERROR]',
            'WARN': '[!]',
            'INFO': '[U+2139]'
        }.get(status, '*')
        
        logger.info(f"{icon} {test_name}: {details}")
    
    def test_pipeline_reports_exist(self) -> Dict[str, bool]:
        """Test 1: Check if pipeline morning reports exist"""
        logger.info("\n" + "="*80)
        logger.info("TEST 1: Pipeline Morning Reports")
        logger.info("="*80)
        
        markets = {'AU': 'au_morning_report.json',
                   'UK': 'uk_morning_report.json',
                   'US': 'us_morning_report.json'}
        
        report_status = {}
        
        for market, filename in markets.items():
            report_path = self.reports_path / filename
            exists = report_path.exists()
            report_status[market] = exists
            
            if exists:
                # Check age
                mod_time = datetime.fromtimestamp(report_path.stat().st_mtime)
                age_hours = (datetime.now() - mod_time).total_seconds() / 3600
                
                self.log_test(
                    f"Report Exists: {market}",
                    "PASS",
                    f"Found at {report_path} (age: {age_hours:.1f}h)",
                    {'path': str(report_path), 'age_hours': age_hours}
                )
            else:
                self.log_test(
                    f"Report Exists: {market}",
                    "FAIL",
                    f"Missing: {report_path}",
                    {'path': str(report_path)}
                )
        
        return report_status
    
    def test_report_format(self, market: str) -> Optional[Dict]:
        """Test 2: Validate report JSON format and required fields"""
        logger.info("\n" + "="*80)
        logger.info(f"TEST 2: Report Format - {market}")
        logger.info("="*80)
        
        report_path = self.reports_path / f'{market.lower()}_morning_report.json'
        
        if not report_path.exists():
            self.log_test(
                f"Report Format: {market}",
                "FAIL",
                "Report file not found"
            )
            return None
        
        try:
            with open(report_path, 'r') as f:
                report = json.load(f)
            
            # Required fields
            required_fields = [
                'timestamp',
                'market',
                'overall_sentiment',
                'recommendation',
                'confidence',
                'risk_rating'
            ]
            
            missing_fields = [f for f in required_fields if f not in report]
            
            if missing_fields:
                self.log_test(
                    f"Report Format: {market}",
                    "FAIL",
                    f"Missing fields: {', '.join(missing_fields)}",
                    {'missing': missing_fields}
                )
                return None
            
            # Check field values
            sentiment = report.get('overall_sentiment', 0)
            confidence = report.get('confidence', 'UNKNOWN')
            recommendation = report.get('recommendation', 'UNKNOWN')
            
            self.log_test(
                f"Report Format: {market}",
                "PASS",
                f"Valid format - Sentiment: {sentiment}, Confidence: {confidence}, Recommendation: {recommendation}",
                {
                    'sentiment': sentiment,
                    'confidence': confidence,
                    'recommendation': recommendation,
                    'timestamp': report.get('timestamp')
                }
            )
            
            return report
            
        except json.JSONDecodeError as e:
            self.log_test(
                f"Report Format: {market}",
                "FAIL",
                f"Invalid JSON: {e}"
            )
            return None
        except Exception as e:
            self.log_test(
                f"Report Format: {market}",
                "FAIL",
                f"Error reading report: {e}"
            )
            return None
    
    def test_signal_adapter_init(self) -> Optional[EnhancedPipelineSignalAdapter]:
        """Test 3: Initialize signal adapter"""
        logger.info("\n" + "="*80)
        logger.info("TEST 3: Signal Adapter Initialization")
        logger.info("="*80)
        
        if not ADAPTER_AVAILABLE:
            self.log_test(
                "Signal Adapter Init",
                "FAIL",
                "Cannot import EnhancedPipelineSignalAdapter"
            )
            return None
        
        try:
            adapter = EnhancedPipelineSignalAdapter(
                pipeline_base_path=self.base_path,
                use_ml_signals=True,
                ml_weight=0.60,
                sentiment_weight=0.40
            )
            
            self.log_test(
                "Signal Adapter Init",
                "PASS",
                f"Initialized (ML: {adapter.use_ml_signals}, ML weight: {adapter.ml_weight:.0%})",
                {
                    'ml_enabled': adapter.use_ml_signals,
                    'ml_weight': adapter.ml_weight,
                    'sentiment_weight': adapter.sentiment_weight
                }
            )
            
            return adapter
            
        except Exception as e:
            self.log_test(
                "Signal Adapter Init",
                "FAIL",
                f"Initialization failed: {e}"
            )
            traceback.print_exc()
            return None
    
    def test_overnight_sentiment_loading(self, adapter: EnhancedPipelineSignalAdapter, market: str) -> Optional[Dict]:
        """Test 4: Load overnight sentiment from report"""
        logger.info("\n" + "="*80)
        logger.info(f"TEST 4: Overnight Sentiment Loading - {market}")
        logger.info("="*80)
        
        try:
            sentiment = adapter.get_overnight_sentiment(market)
            
            if sentiment is None:
                self.log_test(
                    f"Overnight Sentiment: {market}",
                    "FAIL",
                    "get_overnight_sentiment() returned None"
                )
                return None
            
            # Check required sentiment fields
            required = ['sentiment_score', 'confidence', 'risk_rating', 'recommendation']
            missing = [f for f in required if f not in sentiment]
            
            if missing:
                self.log_test(
                    f"Overnight Sentiment: {market}",
                    "WARN",
                    f"Missing fields: {', '.join(missing)}",
                    sentiment
                )
            else:
                self.log_test(
                    f"Overnight Sentiment: {market}",
                    "PASS",
                    f"Loaded - Score: {sentiment['sentiment_score']:.1f}/100, Confidence: {sentiment['confidence']}, Risk: {sentiment['risk_rating']}",
                    sentiment
                )
            
            return sentiment
            
        except Exception as e:
            self.log_test(
                f"Overnight Sentiment: {market}",
                "FAIL",
                f"Error loading sentiment: {e}"
            )
            traceback.print_exc()
            return None
    
    def test_ml_signal_generation(self, adapter: EnhancedPipelineSignalAdapter, symbol: str) -> Optional[Dict]:
        """Test 5: Generate ML swing signal for a symbol"""
        logger.info("\n" + "="*80)
        logger.info(f"TEST 5: ML Signal Generation - {symbol}")
        logger.info("="*80)
        
        if not adapter.use_ml_signals:
            self.log_test(
                f"ML Signal: {symbol}",
                "WARN",
                "ML signals disabled in adapter"
            )
            return None
        
        try:
            ml_signal = adapter.get_ml_signal(symbol, lookback_days=252)
            
            if ml_signal is None:
                self.log_test(
                    f"ML Signal: {symbol}",
                    "WARN",
                    "get_ml_signal() returned None (may be expected if no data)"
                )
                return None
            
            # Check signal structure
            expected_fields = ['prediction', 'confidence', 'signal']
            has_fields = all(f in ml_signal for f in expected_fields)
            
            if has_fields:
                self.log_test(
                    f"ML Signal: {symbol}",
                    "PASS",
                    f"Generated - Signal: {ml_signal['signal']}, Prediction: {ml_signal.get('prediction', 0):.2f}, Confidence: {ml_signal.get('confidence', 0):.0%}",
                    ml_signal
                )
            else:
                self.log_test(
                    f"ML Signal: {symbol}",
                    "WARN",
                    f"Incomplete signal structure",
                    ml_signal
                )
            
            return ml_signal
            
        except Exception as e:
            self.log_test(
                f"ML Signal: {symbol}",
                "FAIL",
                f"Error generating ML signal: {e}"
            )
            traceback.print_exc()
            return None
    
    def test_trading_signal_generation(self, adapter: EnhancedPipelineSignalAdapter, market: str) -> List[Dict]:
        """Test 6: Generate complete trading signals"""
        logger.info("\n" + "="*80)
        logger.info(f"TEST 6: Trading Signal Generation - {market}")
        logger.info("="*80)
        
        try:
            signals = adapter.generate_signals(market, max_signals=5, use_ml=True)
            
            if not signals:
                self.log_test(
                    f"Trading Signals: {market}",
                    "WARN",
                    "No signals generated (may be expected if no BUY opportunities)"
                )
                return []
            
            # Analyze signals
            buy_signals = [s for s in signals if s.get('action') == 'BUY']
            sell_signals = [s for s in signals if s.get('action') == 'SELL']
            
            self.log_test(
                f"Trading Signals: {market}",
                "PASS",
                f"Generated {len(signals)} signals (BUY: {len(buy_signals)}, SELL: {len(sell_signals)})",
                {
                    'total': len(signals),
                    'buy': len(buy_signals),
                    'sell': len(sell_signals),
                    'symbols': [s.get('symbol') for s in signals]
                }
            )
            
            # Validate signal structure
            for signal in signals[:3]:  # Check first 3
                required = ['symbol', 'action', 'position_size', 'confidence', 'combined_score']
                missing = [f for f in required if f not in signal]
                
                if missing:
                    self.log_test(
                        f"Signal Structure: {signal.get('symbol', 'UNKNOWN')}",
                        "WARN",
                        f"Missing fields: {', '.join(missing)}"
                    )
                else:
                    self.log_test(
                        f"Signal Structure: {signal['symbol']}",
                        "PASS",
                        f"{signal['action']} @ {signal['position_size']:.1%} (confidence: {signal['confidence']:.0%}, score: {signal['combined_score']:.2f})"
                    )
            
            return signals
            
        except Exception as e:
            self.log_test(
                f"Trading Signals: {market}",
                "FAIL",
                f"Error generating signals: {e}"
            )
            traceback.print_exc()
            return []
    
    def test_dashboard_signal_format(self, signals: List[Dict]) -> bool:
        """Test 7: Validate signals are dashboard-ready"""
        logger.info("\n" + "="*80)
        logger.info("TEST 7: Dashboard Signal Format")
        logger.info("="*80)
        
        if not signals:
            self.log_test(
                "Dashboard Format",
                "WARN",
                "No signals to validate"
            )
            return False
        
        # Required fields for dashboard
        dashboard_required = [
            'symbol',
            'action',
            'position_size',
            'confidence',
            'entry_price',
            'stop_loss',
            'take_profit'
        ]
        
        valid_count = 0
        invalid_count = 0
        
        for signal in signals:
            missing = [f for f in dashboard_required if f not in signal]
            
            if missing:
                invalid_count += 1
                self.log_test(
                    f"Dashboard Ready: {signal.get('symbol', 'UNKNOWN')}",
                    "FAIL",
                    f"Missing fields: {', '.join(missing)}"
                )
            else:
                valid_count += 1
                self.log_test(
                    f"Dashboard Ready: {signal['symbol']}",
                    "PASS",
                    f"All required fields present - {signal['action']} @ USD{signal.get('entry_price', 0):.2f}"
                )
        
        success = valid_count > 0
        self.log_test(
            "Dashboard Format Summary",
            "PASS" if success else "FAIL",
            f"Valid: {valid_count}/{len(signals)} signals",
            {'valid': valid_count, 'invalid': invalid_count, 'total': len(signals)}
        )
        
        return success
    
    def run_full_diagnostic(self, markets: List[str] = ['AU', 'UK', 'US']) -> Dict:
        """Run complete diagnostic test suite"""
        logger.info("\n" + "="*80)
        logger.info("PIPELINE -> DASHBOARD SIGNAL FLOW DIAGNOSTIC")
        logger.info("="*80)
        logger.info(f"Testing markets: {', '.join(markets)}")
        logger.info(f"Base path: {self.base_path}")
        logger.info(f"Reports path: {self.reports_path}")
        logger.info("="*80 + "\n")
        
        # Test 1: Check reports exist
        report_status = self.test_pipeline_reports_exist()
        
        # Test 2: Validate report formats
        valid_reports = {}
        for market in markets:
            if report_status.get(market, False):
                report = self.test_report_format(market)
                if report:
                    valid_reports[market] = report
        
        # Test 3: Initialize signal adapter
        adapter = self.test_signal_adapter_init()
        
        if not adapter:
            logger.error("\n[ERROR] CRITICAL: Cannot initialize signal adapter - stopping diagnostic")
            return self.generate_summary()
        
        # Test 4-7: For each valid report
        all_signals = []
        for market in valid_reports.keys():
            # Test 4: Load overnight sentiment
            sentiment = self.test_overnight_sentiment_loading(adapter, market)
            
            if not sentiment:
                continue
            
            # Test 5: Generate ML signal for one symbol
            test_symbols = {
                'AU': 'CBA.AX',
                'UK': 'HSBA.L',
                'US': 'AAPL'
            }
            test_symbol = test_symbols.get(market)
            if test_symbol:
                ml_signal = self.test_ml_signal_generation(adapter, test_symbol)
            
            # Test 6: Generate trading signals
            signals = self.test_trading_signal_generation(adapter, market)
            all_signals.extend(signals)
        
        # Test 7: Validate dashboard format
        if all_signals:
            self.test_dashboard_signal_format(all_signals)
        
        # Generate summary
        return self.generate_summary()
    
    def generate_summary(self) -> Dict:
        """Generate diagnostic summary"""
        logger.info("\n" + "="*80)
        logger.info("DIAGNOSTIC SUMMARY")
        logger.info("="*80)
        
        total_tests = len(self.results['tests'])
        passed = sum(1 for t in self.results['tests'] if t['status'] == 'PASS')
        failed = sum(1 for t in self.results['tests'] if t['status'] == 'FAIL')
        warned = sum(1 for t in self.results['tests'] if t['status'] == 'WARN')
        
        self.results['summary'] = {
            'total_tests': total_tests,
            'passed': passed,
            'failed': failed,
            'warned': warned,
            'success_rate': (passed / total_tests * 100) if total_tests > 0 else 0
        }
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"[OK] Passed: {passed}")
        logger.info(f"[ERROR] Failed: {failed}")
        logger.info(f"[!]  Warned: {warned}")
        logger.info(f"Success Rate: {self.results['summary']['success_rate']:.1f}%")
        
        # Overall verdict
        if failed == 0 and passed > 0:
            verdict = "[OK] PASS - Pipeline -> Dashboard signal flow is working"
        elif failed > 0 and passed > failed:
            verdict = "[!] PARTIAL - Some issues detected, but core flow works"
        else:
            verdict = "[ERROR] FAIL - Critical issues blocking signal generation"
        
        logger.info(f"\n{verdict}")
        logger.info("="*80 + "\n")
        
        return self.results
    
    def save_report(self, output_path: Optional[Path] = None):
        """Save diagnostic report to JSON"""
        output_path = output_path or (self.base_path / 'reports' / 'diagnostics' / f'signal_flow_diagnostic_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info(f"[DOC] Diagnostic report saved: {output_path}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test pipeline -> dashboard signal flow'
    )
    parser.add_argument(
        '--markets',
        nargs='+',
        default=['AU', 'UK', 'US'],
        help='Markets to test (default: AU UK US)'
    )
    parser.add_argument(
        '--base-path',
        type=str,
        help='Base path to trading system (default: parent directory)'
    )
    parser.add_argument(
        '--save-report',
        action='store_true',
        help='Save diagnostic report to JSON'
    )
    
    args = parser.parse_args()
    
    # Initialize diagnostic
    base_path = Path(args.base_path) if args.base_path else None
    diagnostic = PipelineToDashboardDiagnostic(base_path)
    
    # Run diagnostic
    results = diagnostic.run_full_diagnostic(markets=args.markets)
    
    # Save report if requested
    if args.save_report:
        diagnostic.save_report()
    
    # Exit with appropriate code
    success_rate = results['summary']['success_rate']
    if success_rate >= 80:
        sys.exit(0)  # Success
    elif success_rate >= 50:
        sys.exit(1)  # Partial success
    else:
        sys.exit(2)  # Failure


if __name__ == "__main__":
    main()
