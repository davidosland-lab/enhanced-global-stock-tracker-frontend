"""
VERIFY_INSTALLATION.py - Comprehensive Installation Verification

Checks:
1. File structure (all critical files present)
2. Python packages (torch, transformers, tensorflow, etc.)
3. FinBERT Bridge functional
4. Configuration correct (max_models=100, enabled=true)
5. PHASE 4.5 code exists in overnight_pipeline.py
6. Regime Engine integration exists in event_risk_guard.py

Run this BEFORE running the pipeline to catch issues early.
"""

import sys
import os
from pathlib import Path
import json

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_section(title):
    """Print formatted section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}\n")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")

def check_file_structure():
    """Check that all critical files exist"""
    print_section("1. FILE STRUCTURE CHECK")
    
    base_path = Path(__file__).parent
    
    critical_files = [
        'models/screening/overnight_pipeline.py',
        'models/screening/event_risk_guard.py',
        'models/screening/finbert_bridge.py',
        'models/screening/lstm_trainer.py',
        'models/screening/market_regime_engine.py',
        'models/config/screening_config.json',
        'finbert_v4.4.4/models/finbert_sentiment.py',
        'finbert_v4.4.4/models/lstm_predictor.py',
        'finbert_v4.4.4/models/news_sentiment_real.py',
    ]
    
    all_exist = True
    for file_path in critical_files:
        full_path = base_path / file_path
        if full_path.exists():
            print_success(f"Found: {file_path}")
        else:
            print_error(f"Missing: {file_path}")
            all_exist = False
    
    return all_exist

def check_python_packages():
    """Check that required Python packages are installed"""
    print_section("2. PYTHON PACKAGES CHECK")
    
    required_packages = {
        'torch': 'PyTorch (FinBERT backend)',
        'transformers': 'HuggingFace Transformers (FinBERT)',
        'tensorflow': 'TensorFlow (LSTM neural networks)',
        'sklearn': 'scikit-learn (data preprocessing)',
        'yfinance': 'Yahoo Finance API',
        'pandas': 'Data manipulation',
        'numpy': 'Numerical computing',
        'arch': 'GARCH volatility modeling'
    }
    
    all_installed = True
    for package, description in required_packages.items():
        try:
            __import__(package)
            print_success(f"{package:15s} - {description}")
        except ImportError:
            print_error(f"{package:15s} - NOT INSTALLED ({description})")
            all_installed = False
    
    return all_installed

def check_finbert_bridge():
    """Check that FinBERT Bridge is functional"""
    print_section("3. FINBERT BRIDGE CHECK")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from models.screening.finbert_bridge import get_finbert_bridge
        
        bridge = get_finbert_bridge()
        status = bridge.is_available()
        
        if status['lstm_available']:
            print_success("LSTM Predictor: Available")
        else:
            print_error("LSTM Predictor: NOT AVAILABLE")
        
        if status['sentiment_available']:
            print_success("Sentiment Analyzer: Available")
        else:
            print_error("Sentiment Analyzer: NOT AVAILABLE")
        
        if status['news_available']:
            print_success("News Scraping: Available")
        else:
            print_error("News Scraping: NOT AVAILABLE")
        
        trained_count = bridge.get_trained_models_count()
        print_success(f"Pre-trained LSTM models: {trained_count}")
        
        return all(status.values())
        
    except Exception as e:
        print_error(f"FinBERT Bridge initialization failed: {e}")
        return False

def check_configuration():
    """Check that configuration is correct"""
    print_section("4. CONFIGURATION CHECK")
    
    config_path = Path(__file__).parent / 'models' / 'config' / 'screening_config.json'
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        lstm_config = config.get('lstm_training', {})
        
        # Check enabled
        enabled = lstm_config.get('enabled', False)
        if enabled:
            print_success(f"LSTM Training Enabled: {enabled}")
        else:
            print_error(f"LSTM Training Enabled: {enabled} (SHOULD BE TRUE)")
        
        # Check max_models
        max_models = lstm_config.get('max_models_per_night', 0)
        if max_models == 100:
            print_success(f"Max Models Per Night: {max_models}")
        else:
            print_error(f"Max Models Per Night: {max_models} (SHOULD BE 100)")
        
        # Check train_all_scanned_stocks
        train_all = lstm_config.get('train_all_scanned_stocks', False)
        if train_all:
            print_success(f"Train All Scanned Stocks: {train_all}")
        else:
            print_warning(f"Train All Scanned Stocks: {train_all} (Optional, but recommended)")
        
        return enabled and max_models == 100
        
    except Exception as e:
        print_error(f"Configuration check failed: {e}")
        return False

def check_phase45_code():
    """Check that PHASE 4.5 code exists in overnight_pipeline.py"""
    print_section("5. PHASE 4.5 CODE CHECK")
    
    pipeline_path = Path(__file__).parent / 'models' / 'screening' / 'overnight_pipeline.py'
    
    try:
        with open(pipeline_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key indicators of PHASE 4.5
        indicators = [
            ('_train_lstm_models', '_train_lstm_models() method exists'),
            ('PHASE 4.5', 'PHASE 4.5 logging exists'),
            ('lstm_training_results = self._train_lstm_models', 'PHASE 4.5 is called in pipeline'),
            ('Training queue created', 'Training queue creation logic exists')
        ]
        
        all_present = True
        for indicator, description in indicators:
            if indicator in content:
                print_success(description)
            else:
                print_error(f"{description} - NOT FOUND")
                all_present = False
        
        return all_present
        
    except Exception as e:
        print_error(f"Pipeline code check failed: {e}")
        return False

def check_regime_engine_integration():
    """Check that Regime Engine integration exists in event_risk_guard.py"""
    print_section("6. REGIME ENGINE INTEGRATION CHECK")
    
    guard_path = Path(__file__).parent / 'models' / 'screening' / 'event_risk_guard.py'
    
    try:
        with open(guard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key indicators of Regime Engine integration
        indicators = [
            ('from .market_regime_engine import MarketRegimeEngine', 'MarketRegimeEngine imported'),
            ('self.regime_engine = MarketRegimeEngine()', 'Regime Engine initialized'),
            ('_get_regime_crash_risk', '_get_regime_crash_risk() method exists'),
            ('regime_label, regime_crash_risk = self._get_regime_crash_risk()', 'Regime Engine called in assess_batch()'),
            ('Market Regime:', 'Regime logging exists')
        ]
        
        all_present = True
        for indicator, description in indicators:
            if indicator in content:
                print_success(description)
            else:
                print_error(f"{description} - NOT FOUND")
                all_present = False
        
        return all_present
        
    except Exception as e:
        print_error(f"Regime Engine integration check failed: {e}")
        return False

def main():
    """Run all verification checks"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}OVERNIGHT SCREENER v1.3.14 - INSTALLATION VERIFICATION{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
    
    results = []
    
    results.append(('File Structure', check_file_structure()))
    results.append(('Python Packages', check_python_packages()))
    results.append(('FinBERT Bridge', check_finbert_bridge()))
    results.append(('Configuration', check_configuration()))
    results.append(('PHASE 4.5 Code', check_phase45_code()))
    results.append(('Regime Engine Integration', check_regime_engine_integration()))
    
    # Summary
    print_section("VERIFICATION SUMMARY")
    
    all_passed = True
    for check_name, passed in results:
        if passed:
            print_success(f"{check_name}: PASSED")
        else:
            print_error(f"{check_name}: FAILED")
            all_passed = False
    
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED - Installation is complete!{Colors.ENDC}")
        print(f"\nYou can now run the pipeline with: {Colors.BOLD}RUN_PIPELINE.bat{Colors.ENDC}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME CHECKS FAILED - Please fix issues before running pipeline{Colors.ENDC}")
        print(f"\nRefer to INSTALLATION_ISSUES_EXPLAINED.md for troubleshooting.")
    
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    # PAUSE - Wait for user input before closing
    try:
        input("Press Enter to close...")
    except:
        pass  # Handle cases where input() might fail
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
