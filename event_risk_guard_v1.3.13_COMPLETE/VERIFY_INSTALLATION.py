"""
Event Risk Guard v1.3.14 - Installation Verification Script
============================================================
This script verifies that all critical components are properly installed.
Run this after extracting and installing dependencies.

Usage:
    python VERIFY_INSTALLATION.py
"""

import sys
from pathlib import Path
import importlib

def print_header(text):
    print("\n" + "="*70)
    print(text)
    print("="*70)

def print_result(test_name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"         {details}")

def verify_file_structure():
    """Verify critical files and directories exist"""
    print_header("1. FILE STRUCTURE VERIFICATION")
    
    base_path = Path(__file__).parent
    
    critical_files = [
        "models/screening/overnight_pipeline.py",
        "models/screening/lstm_trainer.py",
        "models/screening/batch_predictor.py",
        "models/screening/event_risk_guard.py",
        "models/screening/market_regime_engine.py",
        "models/screening/regime_detector.py",
        "models/screening/finbert_bridge.py",
        "models/config/screening_config.json",
        "finbert_v4.4.4/models/finbert_sentiment.py",
        "finbert_v4.4.4/models/lstm_predictor.py",
        "finbert_v4.4.4/models/news_sentiment_real.py",
        "finbert_v4.4.4/models/train_lstm.py",
    ]
    
    all_passed = True
    for file_path in critical_files:
        full_path = base_path / file_path
        passed = full_path.exists()
        all_passed = all_passed and passed
        print_result(file_path, passed, f"Path: {full_path}")
    
    return all_passed

def verify_python_packages():
    """Verify required Python packages are installed"""
    print_header("2. PYTHON PACKAGES VERIFICATION")
    
    required_packages = [
        ("pandas", "Data manipulation"),
        ("numpy", "Numerical computing"),
        ("yfinance", "Stock data fetching"),
        ("tensorflow", "LSTM neural networks"),
        ("transformers", "FinBERT sentiment analysis"),
        ("torch", "FinBERT backend"),
        ("scikit-learn", "Machine learning utilities"),
        ("hmmlearn", "Hidden Markov Models for regime detection"),
        ("arch", "GARCH volatility forecasting"),
        ("beautifulsoup4", "News scraping"),
        ("flask", "Web UI"),
        ("jinja2", "Web UI templates"),
    ]
    
    all_passed = True
    for package_name, description in required_packages:
        try:
            # Handle package name differences
            import_name = package_name
            if package_name == "beautifulsoup4":
                import_name = "bs4"
            elif package_name == "scikit-learn":
                import_name = "sklearn"
            
            importlib.import_module(import_name)
            passed = True
            version = ""
            try:
                mod = sys.modules[import_name]
                if hasattr(mod, '__version__'):
                    version = f"v{mod.__version__}"
            except:
                pass
            print_result(f"{package_name} ({description})", passed, version)
        except ImportError:
            passed = False
            all_passed = False
            print_result(f"{package_name} ({description})", passed, "NOT INSTALLED!")
    
    return all_passed

def verify_finbert_bridge():
    """Verify FinBERT Bridge integration"""
    print_header("3. FINBERT BRIDGE VERIFICATION")
    
    try:
        # Add paths
        base_path = Path(__file__).parent
        sys.path.insert(0, str(base_path))
        sys.path.insert(0, str(base_path / 'models'))
        sys.path.insert(0, str(base_path / 'models' / 'screening'))
        
        from models.screening.finbert_bridge import get_finbert_bridge
        
        bridge = get_finbert_bridge()
        availability = bridge.is_available()
        
        print_result("FinBERT Bridge Import", True)
        print_result("LSTM Component", availability['lstm_available'], 
                    "Can load and run LSTM predictions")
        print_result("Sentiment Component", availability['sentiment_available'],
                    "Can analyze text with FinBERT transformer")
        print_result("News Component", availability['news_available'],
                    "Can scrape news from Yahoo Finance/Finviz")
        
        # Get component info
        info = bridge.get_component_info()
        print(f"\n   FinBERT Path: {info['finbert_path']}")
        print(f"   LSTM Model Path: {info['lstm']['model_path']}")
        print(f"   Sentiment Model: {info['sentiment']['model_name']}")
        
        return all(availability.values())
        
    except Exception as e:
        print_result("FinBERT Bridge", False, f"Error: {str(e)}")
        return False

def verify_configuration():
    """Verify screening configuration is correct"""
    print_header("4. CONFIGURATION VERIFICATION")
    
    try:
        import json
        base_path = Path(__file__).parent
        config_path = base_path / 'models' / 'config' / 'screening_config.json'
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check LSTM training config
        lstm_config = config.get('lstm_training', {})
        max_models = lstm_config.get('max_models_per_night', 0)
        enabled = lstm_config.get('enabled', False)
        train_all = lstm_config.get('train_all_scanned_stocks', False)
        
        print_result("Config File Loaded", True, f"Path: {config_path}")
        print_result("LSTM Training Enabled", enabled, 
                    f"lstm_training.enabled = {enabled}")
        print_result("Max Models Per Night", max_models == 100,
                    f"Value: {max_models} (expected: 100)")
        print_result("Train All Scanned Stocks", train_all,
                    f"train_all_scanned_stocks = {train_all}")
        
        return enabled and max_models == 100
        
    except Exception as e:
        print_result("Configuration", False, f"Error: {str(e)}")
        return False

def verify_phase_45_exists():
    """Verify PHASE 4.5 LSTM training code exists"""
    print_header("5. PHASE 4.5 CODE VERIFICATION")
    
    try:
        base_path = Path(__file__).parent
        pipeline_path = base_path / 'models' / 'screening' / 'overnight_pipeline.py'
        
        with open(pipeline_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for critical code
        checks = [
            ('_train_lstm_models method', 'def _train_lstm_models('),
            ('PHASE 4.5 header', 'PHASE 4.5: LSTM MODEL TRAINING'),
            ('Training queue creation', 'create_training_queue'),
            ('Batch training call', 'train_batch('),
            ('Config loading in __init__', 'with open(config_path'),
        ]
        
        all_passed = True
        for check_name, search_str in checks:
            passed = search_str in content
            all_passed = all_passed and passed
            print_result(check_name, passed)
        
        return all_passed
        
    except Exception as e:
        print_result("Phase 4.5 Code", False, f"Error: {str(e)}")
        return False

def verify_regime_engine():
    """Verify Market Regime Engine integration"""
    print_header("6. MARKET REGIME ENGINE VERIFICATION")
    
    try:
        base_path = Path(__file__).parent
        guard_path = base_path / 'models' / 'screening' / 'event_risk_guard.py'
        
        with open(guard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('MarketRegimeEngine import', 'from .market_regime_engine import MarketRegimeEngine'),
            ('_get_regime_crash_risk method', 'def _get_regime_crash_risk('),
            ('Regime engine initialization', 'self.regime_engine = MarketRegimeEngine()'),
            ('Crash risk calculation', 'crash_risk_score'),
        ]
        
        all_passed = True
        for check_name, search_str in checks:
            passed = search_str in content
            all_passed = all_passed and passed
            print_result(check_name, passed)
        
        return all_passed
        
    except Exception as e:
        print_result("Regime Engine", False, f"Error: {str(e)}")
        return False

def main():
    print("\n" + "="*70)
    print("EVENT RISK GUARD v1.3.14 - INSTALLATION VERIFICATION")
    print("="*70)
    print("\nThis will verify that all critical components are properly installed.")
    print("Please wait...\n")
    
    results = {
        "File Structure": verify_file_structure(),
        "Python Packages": verify_python_packages(),
        "FinBERT Bridge": verify_finbert_bridge(),
        "Configuration": verify_configuration(),
        "Phase 4.5 Code": verify_phase_45_exists(),
        "Regime Engine": verify_regime_engine(),
    }
    
    # Final Summary
    print_header("VERIFICATION SUMMARY")
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        print_result(test_name, passed)
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED - Installation is complete and correct!")
        print("="*70)
        print("\nYou can now run the pipeline:")
        print("  Test mode:  RUN_PIPELINE.bat --test")
        print("  Full mode:  RUN_PIPELINE.bat")
        print("\nExpected log indicators:")
        print("  - 'PHASE 4.5: LSTM MODEL TRAINING'")
        print("  - 'Market Regime Engine: ENABLED'")
        print("  - 'FinBERT LSTM Available: True'")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Please review the errors above")
        print("="*70)
        print("\nTroubleshooting:")
        print("  1. Run: INSTALL.bat (Windows) or ./install.sh (Linux/Mac)")
        print("  2. Check installation logs for errors")
        print("  3. Verify Python 3.8+ is installed")
        print("  4. Ensure all files were extracted correctly")
        return 1

if __name__ == "__main__":
    sys.exit(main())
