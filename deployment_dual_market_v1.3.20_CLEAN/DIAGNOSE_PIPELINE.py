"""
Comprehensive Pipeline Diagnostics

This script checks all components needed for the pipeline to work.
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_directories():
    """Check if required directories exist"""
    print("="*80)
    print("1. CHECKING DIRECTORIES")
    print("="*80)
    
    required_dirs = [
        'models/config',
        'models/screening',
        'logs/screening',
        'reports/morning_reports',
        'reports/pipeline_state',
        'reports/chatgpt_research'
    ]
    
    all_good = True
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} (MISSING)")
            all_good = False
            # Try to create it
            try:
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"    → Created: {dir_path}")
                all_good = True
            except Exception as e:
                print(f"    → Failed to create: {e}")
    
    return all_good

def check_config():
    """Check if configuration file exists and is valid"""
    print("\n" + "="*80)
    print("2. CHECKING CONFIGURATION")
    print("="*80)
    
    config_path = project_root / 'models' / 'config' / 'screening_config.json'
    
    if not config_path.exists():
        print(f"  ✗ Config file not found: {config_path}")
        return False
    
    print(f"  ✓ Config file exists: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print("  ✓ Config file is valid JSON")
        
        # Check for required sections
        required_sections = ['screening', 'reporting', 'ai_integration', 'research']
        for section in required_sections:
            if section in config:
                print(f"  ✓ Section '{section}' found")
            else:
                print(f"  ✗ Section '{section}' MISSING")
        
        # Check AI integration
        if 'ai_integration' in config:
            ai_config = config['ai_integration']
            enabled = ai_config.get('enabled', False)
            model = ai_config.get('model', 'N/A')
            print(f"\n  AI Integration:")
            print(f"    Enabled: {enabled}")
            print(f"    Model: {model}")
        
        # Check research config
        if 'research' in config:
            research_config = config['research']
            enabled = research_config.get('enabled', False)
            print(f"\n  ChatGPT Research:")
            print(f"    Enabled: {enabled}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error reading config: {e}")
        return False

def check_api_key():
    """Check if OpenAI API key is configured"""
    print("\n" + "="*80)
    print("3. CHECKING API KEY")
    print("="*80)
    
    env_path = project_root / 'config' / 'api_keys.env'
    
    if not env_path.exists():
        print(f"  ⚠ API key file not found: {env_path}")
        print("  → AI features will be disabled")
        return False
    
    print(f"  ✓ API key file exists: {env_path}")
    
    try:
        with open(env_path, 'r') as f:
            content = f.read()
        
        if 'OPENAI_API_KEY=' in content:
            # Extract key
            for line in content.split('\n'):
                if line.startswith('OPENAI_API_KEY='):
                    key = line.split('=', 1)[1].strip()
                    if key and len(key) > 20:
                        print(f"  ✓ API key found (length: {len(key)} chars)")
                        if key.startswith('sk-proj-'):
                            print("  ✓ Key format looks correct (sk-proj-...)")
                            return True
                        else:
                            print("  ⚠ Key doesn't start with 'sk-proj-' (might be old format)")
                            return False
            
        print("  ✗ OPENAI_API_KEY not found in file")
        return False
        
    except Exception as e:
        print(f"  ✗ Error reading API key: {e}")
        return False

def check_imports():
    """Check if all required modules can be imported"""
    print("\n" + "="*80)
    print("4. CHECKING MODULE IMPORTS")
    print("="*80)
    
    modules_to_test = [
        ('models.screening.overnight_pipeline', 'OvernightPipeline'),
        ('models.screening.us_overnight_pipeline', 'USOvernightPipeline'),
        ('models.screening.report_generator', 'ReportGenerator'),
        ('models.screening.batch_predictor', 'BatchPredictor'),
        ('models.screening.opportunity_scorer', 'OpportunityScorer'),
    ]
    
    all_good = True
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"  ✓ {module_name}.{class_name}")
        except Exception as e:
            print(f"  ✗ {module_name}.{class_name}: {e}")
            all_good = False
    
    # Check optional AI modules
    print("\n  Optional AI modules:")
    try:
        from models.screening.chatgpt_research import (
            ai_quick_filter,
            ai_score_opportunity,
            ai_rerank_opportunities
        )
        print("  ✓ chatgpt_research (AI functions available)")
    except Exception as e:
        print(f"  ⚠ chatgpt_research: {e}")
        print("    → AI features will be disabled")
    
    return all_good

def check_recent_errors():
    """Check for recent error logs"""
    print("\n" + "="*80)
    print("5. CHECKING RECENT ERRORS")
    print("="*80)
    
    error_dir = project_root / 'logs' / 'screening' / 'errors'
    
    if not error_dir.exists():
        print("  ✓ No error directory (no errors recorded)")
        return True
    
    error_files = sorted(error_dir.glob('error_*.json'), reverse=True)
    
    if not error_files:
        print("  ✓ No error files found")
        return True
    
    print(f"  ⚠ Found {len(error_files)} error file(s)")
    
    # Show most recent error
    latest_error = error_files[0]
    print(f"\n  Most recent error: {latest_error.name}")
    
    try:
        with open(latest_error, 'r') as f:
            error_data = json.load(f)
        
        print(f"  Timestamp: {error_data.get('timestamp', 'N/A')}")
        print(f"  Error: {error_data.get('error', 'N/A')[:200]}")
        
    except Exception as e:
        print(f"  Could not read error file: {e}")
    
    return False

def check_pipeline_state():
    """Check for recent pipeline state"""
    print("\n" + "="*80)
    print("6. CHECKING PIPELINE STATE")
    print("="*80)
    
    state_dir = project_root / 'reports' / 'pipeline_state'
    
    if not state_dir.exists():
        print(f"  ⚠ State directory doesn't exist: {state_dir}")
        print("  → Pipeline has never run successfully")
        return False
    
    state_files = sorted(state_dir.glob('*_pipeline_state.json'), reverse=True)
    
    if not state_files:
        print("  ⚠ No pipeline state files found")
        print("  → Pipeline has never completed successfully")
        return False
    
    print(f"  ✓ Found {len(state_files)} state file(s)")
    
    latest_state = state_files[0]
    print(f"  Most recent: {latest_state.name}")
    
    try:
        with open(latest_state, 'r') as f:
            state_data = json.load(f)
        
        print(f"  Stocks processed: {state_data.get('total_processed', 'N/A')}")
        print(f"  Report path: {state_data.get('report_path', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"  Could not read state file: {e}")
        return False

def main():
    """Run all diagnostic checks"""
    print("\n")
    print("█" * 80)
    print("PIPELINE DIAGNOSTICS")
    print("█" * 80)
    print()
    
    results = {
        'Directories': check_directories(),
        'Configuration': check_config(),
        'API Key': check_api_key(),
        'Module Imports': check_imports(),
        'Recent Errors': check_recent_errors(),
        'Pipeline State': check_pipeline_state()
    }
    
    print("\n" + "="*80)
    print("DIAGNOSTIC SUMMARY")
    print("="*80)
    
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {check:20s} {status}")
    
    print("="*80)
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✅ All checks passed! System is ready.")
        print("\nNext steps:")
        print("  1. Run: python RUN_PIPELINE.bat (ASX)")
        print("  2. Run: python RUN_US_PIPELINE.bat (US)")
        print("  3. Check: reports/morning_reports/ for HTML reports")
    else:
        print("\n⚠️ Some checks failed. Please review the issues above.")
        print("\nCommon fixes:")
        print("  1. Missing directories: They should be auto-created")
        print("  2. API key issues: Check config/api_keys.env")
        print("  3. Import errors: Run 'pip install -r requirements.txt'")
        print("  4. Pipeline state missing: Run the pipeline at least once")
    
    print()

if __name__ == "__main__":
    main()
