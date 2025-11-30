#!/usr/bin/env python3
"""
Quick Installation Verification for Event Risk Guard v1.3.20
Checks critical files and configuration without loading heavy dependencies
"""

import sys
import json
from pathlib import Path

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")

def print_section(title):
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}{title}{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")

def check_files():
    """Check essential files exist"""
    print_section("1. FILE STRUCTURE CHECK")
    
    required_files = [
        'models/screening/overnight_pipeline.py',
        'models/screening/event_risk_guard.py',
        'models/screening/finbert_bridge.py',
        'models/screening/market_regime_engine.py',
        'models/screening/regime_detector.py',
        'models/config/screening_config.json',
        'finbert_v4.4.4/__init__.py',
        'finbert_v4.4.4/models/__init__.py',
        'finbert_v4.4.4/models/finbert_sentiment.py',
        'finbert_v4.4.4/models/lstm_predictor.py',
        'requirements.txt'
    ]
    
    all_found = True
    for file_path in required_files:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print_success(f"Found: {file_path}")
        else:
            print_error(f"Missing: {file_path}")
            all_found = False
    
    return all_found

def check_requirements():
    """Check requirements.txt has hmmlearn enabled"""
    print_section("2. REQUIREMENTS CHECK")
    
    req_file = Path(__file__).parent / 'requirements.txt'
    
    try:
        with open(req_file, 'r') as f:
            content = f.read()
        
        # Check if hmmlearn is present and NOT commented
        hmmlearn_active = False
        for line in content.split('\n'):
            line = line.strip()
            if 'hmmlearn' in line.lower() and not line.startswith('#'):
                hmmlearn_active = True
                print_success(f"hmmlearn enabled in requirements.txt: {line}")
                break
        
        if not hmmlearn_active:
            print_error("hmmlearn is commented out or missing in requirements.txt")
            print_warning("Run: pip install hmmlearn>=0.3.0")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Failed to read requirements.txt: {e}")
        return False

def check_config():
    """Check screening_config.json has regime_detector enabled"""
    print_section("3. CONFIGURATION CHECK")
    
    config_path = Path(__file__).parent / 'models' / 'config' / 'screening_config.json'
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check LSTM training enabled
        lstm_enabled = config.get('lstm_training', {}).get('enabled', False)
        if lstm_enabled:
            print_success("LSTM Training: ENABLED")
        else:
            print_warning("LSTM Training: DISABLED")
        
        # Check max models
        max_models = config.get('lstm_training', {}).get('max_models_per_night', 0)
        if max_models >= 100:
            print_success(f"Max models per night: {max_models}")
        else:
            print_warning(f"Max models per night: {max_models} (recommended: 100)")
        
        # Check regime detector enabled
        regime_enabled = config.get('regime_detector', {}).get('enabled', False)
        if regime_enabled:
            print_success("Regime Detector: ENABLED")
        else:
            print_error("Regime Detector: DISABLED")
            return False
        
        # Check regime states
        states = config.get('regime_detector', {}).get('state_names', [])
        if states:
            print_success(f"Regime States: {', '.join(states)}")
        else:
            print_warning("Regime States: Not configured")
        
        # Check FinBERT integration
        finbert_enabled = config.get('finbert_integration', {}).get('enabled', False)
        if finbert_enabled:
            print_success("FinBERT Integration: ENABLED")
        else:
            print_warning("FinBERT Integration: DISABLED")
        
        return regime_enabled
        
    except Exception as e:
        print_error(f"Failed to read config: {e}")
        return False

def check_package_structure():
    """Check Python package structure"""
    print_section("4. PACKAGE STRUCTURE CHECK")
    
    init_files = [
        'finbert_v4.4.4/__init__.py',
        'finbert_v4.4.4/models/__init__.py',
        'models/__init__.py',
        'models/screening/__init__.py',
        'models/config/__init__.py'
    ]
    
    all_found = True
    for init_file in init_files:
        full_path = Path(__file__).parent / init_file
        if full_path.exists():
            print_success(f"Found: {init_file}")
        else:
            print_error(f"Missing: {init_file}")
            all_found = False
    
    return all_found

def check_code():
    """Check critical code sections"""
    print_section("5. CRITICAL CODE CHECK")
    
    # Check PHASE 4.5 in overnight_pipeline.py
    pipeline_file = Path(__file__).parent / 'models' / 'screening' / 'overnight_pipeline.py'
    
    try:
        with open(pipeline_file, 'r') as f:
            content = f.read()
        
        if 'PHASE 4.5' in content:
            print_success("PHASE 4.5 (LSTM Training) code present")
        else:
            print_error("PHASE 4.5 (LSTM Training) code missing")
            return False
        
        if 'regime_available' in content or 'Market Regime Engine' in content:
            print_success("Regime Engine integration present")
        else:
            print_warning("Regime Engine integration not found")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to check overnight_pipeline.py: {e}")
        return False

def main():
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}EVENT RISK GUARD v1.3.20 - QUICK VERIFICATION{RESET}")
    print(f"{BOLD}{'='*80}{RESET}")
    
    results = []
    
    # Run checks
    results.append(('File Structure', check_files()))
    results.append(('Requirements', check_requirements()))
    results.append(('Configuration', check_config()))
    results.append(('Package Structure', check_package_structure()))
    results.append(('Critical Code', check_code()))
    
    # Summary
    print_section("VERIFICATION SUMMARY")
    
    all_passed = True
    for check_name, passed in results:
        if passed:
            print_success(f"{check_name}: PASSED")
        else:
            print_error(f"{check_name}: FAILED")
            all_passed = False
    
    print(f"\n{BOLD}{'='*80}{RESET}")
    
    if all_passed:
        print(f"{GREEN}{BOLD}✓ ALL CHECKS PASSED - Ready to run pipeline{RESET}")
        print(f"\nNext steps:")
        print(f"1. Run: RUN_PIPELINE_TEST.bat (Windows) or ./run_pipeline_test.sh (Linux)")
        print(f"2. Check for: 'Market Regime Engine: [STATE] (enabled)'")
        print(f"3. View reports: START_WEB_UI.bat or python3 web_ui.py")
        return 0
    else:
        print(f"{RED}{BOLD}✗ SOME CHECKS FAILED - Fix issues before running pipeline{RESET}")
        print(f"\nCommon fixes:")
        print(f"1. Install hmmlearn: pip install hmmlearn>=0.3.0")
        print(f"2. Check regime_detector.enabled = true in models/config/screening_config.json")
        print(f"3. Ensure all files were extracted from ZIP")
        return 1

if __name__ == '__main__':
    sys.exit(main())
