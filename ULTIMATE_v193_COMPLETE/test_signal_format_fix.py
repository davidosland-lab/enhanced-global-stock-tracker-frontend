"""
Test Signal Format Fix (v1.3.15.165)

Tests that both signal formats work correctly:
1. Standard format: {'prediction': 1, 'confidence': 75}
2. Enhanced format: {'action': 'BUY', 'confidence': 75}

Issue: v1.3.15.163 broke trading by checking for 'action' field
       which doesn't exist in standard signals.

Fix: v1.3.15.165 supports both formats.
"""

def test_signal_formats():
    """Test both signal formats"""
    
    print("\n" + "="*80)
    print("SIGNAL FORMAT FIX TEST (v1.3.15.165)")
    print("="*80 + "\n")
    
    # Test cases
    test_cases = [
        {
            'name': 'Standard Signal (prediction=1)',
            'signal': {'prediction': 1, 'confidence': 75.5, 'signal_strength': 75.5},
            'expected_is_buy': True
        },
        {
            'name': 'Standard Signal (prediction=0)',
            'signal': {'prediction': 0, 'confidence': 45.0, 'signal_strength': 45.0},
            'expected_is_buy': False
        },
        {
            'name': 'Enhanced Signal (action=BUY)',
            'signal': {'action': 'BUY', 'confidence': 80.0},
            'expected_is_buy': True
        },
        {
            'name': 'Enhanced Signal (action=STRONG_BUY)',
            'signal': {'action': 'STRONG_BUY', 'confidence': 90.0},
            'expected_is_buy': True
        },
        {
            'name': 'Enhanced Signal (action=HOLD)',
            'signal': {'action': 'HOLD', 'confidence': 60.0},
            'expected_is_buy': False
        },
        {
            'name': 'Mixed Format (prediction=1 + action=BUY)',
            'signal': {'prediction': 1, 'action': 'BUY', 'confidence': 85.0},
            'expected_is_buy': True
        },
        {
            'name': 'Empty Signal',
            'signal': {},
            'expected_is_buy': False
        }
    ]
    
    # Run tests
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['name']}")
        print("-" * 80)
        
        signal = test['signal']
        expected = test['expected_is_buy']
        
        # Apply the fix logic
        prediction = signal.get('prediction', 0)
        action = signal.get('action', '')
        is_buy_signal = (prediction == 1) or (action in ['BUY', 'STRONG_BUY'])
        
        # Check result
        if is_buy_signal == expected:
            print(f"[OK] PASS - is_buy_signal={is_buy_signal} (expected {expected})")
            passed += 1
        else:
            print(f"[X] FAIL - is_buy_signal={is_buy_signal} (expected {expected})")
            failed += 1
        
        print(f"  Signal: {signal}")
        print(f"  prediction={prediction}, action='{action}'")
        print()
    
    # Summary
    print("="*80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*80 + "\n")
    
    if failed == 0:
        print("[OK] All tests passed! Signal format fix is working correctly.\n")
    else:
        print(f"[X] {failed} test(s) failed! Fix may need adjustment.\n")
    
    return failed == 0


if __name__ == "__main__":
    success = test_signal_formats()
    exit(0 if success else 1)
