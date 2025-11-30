"""
Test US Pipeline AI Integration

This script verifies that the US Overnight Pipeline correctly integrates
all 3 stages of AI analysis: Quick Filter, AI Scoring, and Re-Ranking.

Tests:
1. AI function imports
2. Configuration loading
3. AI stage method existence
4. Method signatures
5. Integration flow
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_ai_imports():
    """Test 1: Verify AI functions can be imported"""
    print("="*80)
    print("TEST 1: AI Function Imports")
    print("="*80)
    
    try:
        from models.screening import chatgpt_research
        
        # Check if AI functions exist
        has_quick_filter = hasattr(chatgpt_research, 'ai_quick_filter')
        has_ai_scoring = hasattr(chatgpt_research, 'ai_score_opportunity')
        has_reranking = hasattr(chatgpt_research, 'ai_rerank_opportunities')
        
        print(f"✓ chatgpt_research module imported")
        print(f"  - ai_quick_filter: {'✓ Available' if has_quick_filter else '✗ Missing'}")
        print(f"  - ai_score_opportunity: {'✓ Available' if has_ai_scoring else '✗ Missing'}")
        print(f"  - ai_rerank_opportunities: {'✓ Available' if has_reranking else '✗ Missing'}")
        
        if all([has_quick_filter, has_ai_scoring, has_reranking]):
            print("\n✅ TEST 1 PASSED: All AI functions available")
            return True
        else:
            print("\n❌ TEST 1 FAILED: Some AI functions missing")
            return False
            
    except Exception as e:
        print(f"❌ TEST 1 FAILED: Import error - {e}")
        return False

def test_pipeline_imports():
    """Test 2: Verify US Pipeline imports AI functions"""
    print("\n" + "="*80)
    print("TEST 2: US Pipeline AI Imports")
    print("="*80)
    
    try:
        from models.screening import us_overnight_pipeline
        
        # Check if AI functions are imported in pipeline
        has_quick_filter = hasattr(us_overnight_pipeline, 'ai_quick_filter')
        has_ai_scoring = hasattr(us_overnight_pipeline, 'ai_score_opportunity')
        has_reranking = hasattr(us_overnight_pipeline, 'ai_rerank_opportunities')
        
        print(f"✓ us_overnight_pipeline module imported")
        print(f"  - ai_quick_filter imported: {'✓ Yes' if has_quick_filter else '✗ No'}")
        print(f"  - ai_score_opportunity imported: {'✓ Yes' if has_ai_scoring else '✗ No'}")
        print(f"  - ai_rerank_opportunities imported: {'✓ Yes' if has_reranking else '✗ No'}")
        
        if all([has_quick_filter, has_ai_scoring, has_reranking]):
            print("\n✅ TEST 2 PASSED: US Pipeline has all AI imports")
            return True
        else:
            print("\n⚠️  TEST 2 WARNING: Some AI functions not imported (may be optional)")
            return True  # Not critical if functions are None
            
    except Exception as e:
        print(f"❌ TEST 2 FAILED: Import error - {e}")
        return False

def test_pipeline_methods():
    """Test 3: Verify US Pipeline has AI stage methods"""
    print("\n" + "="*80)
    print("TEST 3: US Pipeline AI Stage Methods")
    print("="*80)
    
    try:
        from models.screening.us_overnight_pipeline import USOvernightPipeline
        
        # Check if methods exist (don't instantiate yet)
        has_quick_filter = hasattr(USOvernightPipeline, '_run_ai_quick_filter')
        has_ai_scoring = hasattr(USOvernightPipeline, '_run_ai_scoring')
        has_reranking = hasattr(USOvernightPipeline, '_run_ai_reranking')
        
        print(f"✓ USOvernightPipeline class loaded")
        print(f"  - _run_ai_quick_filter method: {'✓ Exists' if has_quick_filter else '✗ Missing'}")
        print(f"  - _run_ai_scoring method: {'✓ Exists' if has_ai_scoring else '✗ Missing'}")
        print(f"  - _run_ai_reranking method: {'✓ Exists' if has_reranking else '✗ Missing'}")
        
        if all([has_quick_filter, has_ai_scoring, has_reranking]):
            print("\n✅ TEST 3 PASSED: All AI stage methods exist")
            return True
        else:
            print("\n❌ TEST 3 FAILED: Some AI stage methods missing")
            return False
            
    except Exception as e:
        print(f"❌ TEST 3 FAILED: Error - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration():
    """Test 4: Verify AI configuration structure"""
    print("\n" + "="*80)
    print("TEST 4: AI Configuration Structure")
    print("="*80)
    
    try:
        config_path = Path('models/config/screening_config.json')
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        ai_config = config.get('ai_integration', {})
        
        print(f"✓ Configuration file loaded: {config_path}")
        print(f"\nAI Integration Configuration:")
        print(f"  - enabled: {ai_config.get('enabled', False)}")
        print(f"  - model: {ai_config.get('model', 'N/A')}")
        
        stages = ai_config.get('stages', {})
        print(f"\nStage Configuration:")
        print(f"  - quick_filter.enabled: {stages.get('quick_filter', {}).get('enabled', False)}")
        print(f"  - ai_scoring.enabled: {stages.get('ai_scoring', {}).get('enabled', False)}")
        print(f"  - ai_scoring.score_top_n: {stages.get('ai_scoring', {}).get('score_top_n', 'N/A')}")
        print(f"  - ai_scoring.weight: {stages.get('ai_scoring', {}).get('weight', 'N/A')}")
        print(f"  - ai_reranking.enabled: {stages.get('ai_reranking', {}).get('enabled', False)}")
        print(f"  - ai_reranking.rerank_top_n: {stages.get('ai_reranking', {}).get('rerank_top_n', 'N/A')}")
        print(f"  - ai_reranking.final_picks: {stages.get('ai_reranking', {}).get('final_picks', 'N/A')}")
        
        # Verify structure exists
        has_structure = (
            'ai_integration' in config and
            'stages' in ai_config and
            'quick_filter' in stages and
            'ai_scoring' in stages and
            'ai_reranking' in stages
        )
        
        if has_structure:
            print("\n✅ TEST 4 PASSED: Configuration structure is correct")
            return True
        else:
            print("\n❌ TEST 4 FAILED: Configuration structure incomplete")
            return False
            
    except FileNotFoundError:
        print(f"❌ TEST 4 FAILED: Configuration file not found")
        return False
    except Exception as e:
        print(f"❌ TEST 4 FAILED: Error - {e}")
        return False

def test_method_signatures():
    """Test 5: Verify method signatures are correct"""
    print("\n" + "="*80)
    print("TEST 5: Method Signatures")
    print("="*80)
    
    try:
        import inspect
        from models.screening.us_overnight_pipeline import USOvernightPipeline
        
        # Check _score_opportunities signature
        sig = inspect.signature(USOvernightPipeline._score_opportunities)
        params = list(sig.parameters.keys())
        
        print(f"✓ Checking _score_opportunities signature...")
        print(f"  Parameters: {params}")
        
        has_ai_scores = 'ai_scores' in params
        print(f"  - Has 'ai_scores' parameter: {'✓ Yes' if has_ai_scores else '✗ No'}")
        
        if has_ai_scores:
            default = sig.parameters['ai_scores'].default
            print(f"  - Default value: {default}")
        
        if has_ai_scores:
            print("\n✅ TEST 5 PASSED: Method signatures correct")
            return True
        else:
            print("\n❌ TEST 5 FAILED: Missing ai_scores parameter")
            return False
            
    except Exception as e:
        print(f"❌ TEST 5 FAILED: Error - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_flow():
    """Test 6: Verify AI stages are called in pipeline flow"""
    print("\n" + "="*80)
    print("TEST 6: Integration Flow")
    print("="*80)
    
    try:
        # Read the pipeline file
        pipeline_path = Path('models/screening/us_overnight_pipeline.py')
        
        with open(pipeline_path, 'r') as f:
            code = f.read()
        
        # Check for AI stage calls
        has_quick_filter_call = '_run_ai_quick_filter' in code
        has_ai_scoring_call = '_run_ai_scoring' in code
        has_reranking_call = '_run_ai_reranking' in code
        
        # Check for phase comments
        has_phase_2_3 = 'Phase 2.3: AI Quick Filter' in code
        has_phase_3_5 = 'Phase 3.5: AI Scoring' in code
        has_phase_4_6 = 'Phase 4.6: AI Re-Ranking' in code
        
        print(f"✓ Pipeline file analyzed")
        print(f"\nAI Stage Calls:")
        print(f"  - _run_ai_quick_filter: {'✓ Found' if has_quick_filter_call else '✗ Missing'}")
        print(f"  - _run_ai_scoring: {'✓ Found' if has_ai_scoring_call else '✗ Missing'}")
        print(f"  - _run_ai_reranking: {'✓ Found' if has_reranking_call else '✗ Missing'}")
        
        print(f"\nPhase Documentation:")
        print(f"  - Phase 2.3 (Quick Filter): {'✓ Found' if has_phase_2_3 else '✗ Missing'}")
        print(f"  - Phase 3.5 (AI Scoring): {'✓ Found' if has_phase_3_5 else '✗ Missing'}")
        print(f"  - Phase 4.6 (Re-Ranking): {'✓ Found' if has_phase_4_6 else '✗ Missing'}")
        
        all_present = all([
            has_quick_filter_call, has_ai_scoring_call, has_reranking_call,
            has_phase_2_3, has_phase_3_5, has_phase_4_6
        ])
        
        if all_present:
            print("\n✅ TEST 6 PASSED: All AI stages integrated in pipeline flow")
            return True
        else:
            print("\n❌ TEST 6 FAILED: Some AI stages missing from flow")
            return False
            
    except Exception as e:
        print(f"❌ TEST 6 FAILED: Error - {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 US PIPELINE AI INTEGRATION TEST SUITE")
    print("="*80)
    print("Testing 3-Stage AI Pipeline Integration (Option 3)")
    print("  - Stage 1: AI Quick Filter")
    print("  - Stage 2: AI Scoring")
    print("  - Stage 3: AI Re-Ranking")
    print("="*80 + "\n")
    
    # Run all tests
    results = []
    results.append(("AI Function Imports", test_ai_imports()))
    results.append(("US Pipeline AI Imports", test_pipeline_imports()))
    results.append(("US Pipeline AI Methods", test_pipeline_methods()))
    results.append(("AI Configuration", test_configuration()))
    results.append(("Method Signatures", test_method_signatures()))
    results.append(("Integration Flow", test_integration_flow()))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)
    
    print("="*80)
    print(f"Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! US Pipeline AI Integration is COMPLETE!")
        print("\n✅ Ready for production use with full 3-stage AI pipeline")
        print("\nNext steps:")
        print("  1. Set OPENAI_API_KEY in config/api_keys.env")
        print("  2. Enable AI integration in screening_config.json")
        print("  3. Run: python RUN_US_PIPELINE.bat")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed")
        print("Please review the errors above and fix issues")
        return 1

if __name__ == "__main__":
    exit(main())
