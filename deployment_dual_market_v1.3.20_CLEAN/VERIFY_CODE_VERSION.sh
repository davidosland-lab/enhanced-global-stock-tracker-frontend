#!/bin/bash
# ============================================================================
# CODE VERSION VERIFICATION - Dual Market Screening System v1.3.20.1
# ============================================================================
#
# This script verifies that you're running the latest code version by
# checking for specific fixes in key files.
#
# ============================================================================

echo ""
echo "============================================================================"
echo "  CODE VERSION VERIFICATION - v1.3.20.1"
echo "============================================================================"
echo ""

ERRORS=0
WARNINGS=0

# Check 1: US Pipeline CSV Export Fix
echo "[CHECK 1/4] Verifying US Pipeline CSV Export Fix..."
if grep -q "us_sentiment" models/screening/us_overnight_pipeline.py 2>/dev/null; then
    if grep -q "export_screening_results(scored_stocks, sentiment)" models/screening/us_overnight_pipeline.py 2>/dev/null; then
        echo "  ❌ FAIL: OLD CODE detected - still using 'sentiment' instead of 'us_sentiment'"
        ((ERRORS++))
    else
        echo "  ✓ PASS: US Pipeline CSV export fix verified"
    fi
else
    echo "  ❌ FAIL: US Pipeline CSV export fix NOT found"
    echo "  Expected: 'us_sentiment' in us_overnight_pipeline.py"
    ((ERRORS++))
fi

echo ""

# Check 2: HMM Covariance Fix
echo "[CHECK 2/4] Verifying HMM Covariance Fix..."
if grep -q "StandardScaler" models/screening/us_market_regime_engine.py 2>/dev/null; then
    if grep -q 'covariance_type="diag"' models/screening/us_market_regime_engine.py 2>/dev/null; then
        echo "  ✓ PASS: HMM covariance fix verified"
    else
        echo "  ⚠️  WARNING: HMM may still use 'full' covariance (should be 'diag')"
        ((WARNINGS++))
    fi
else
    echo "  ❌ FAIL: HMM scaling fix NOT found"
    echo "  Expected: 'StandardScaler' in us_market_regime_engine.py"
    ((ERRORS++))
fi

echo ""

# Check 3: Python Cache
echo "[CHECK 3/4] Checking for Python cache files..."
CACHE_FOUND=$(find . -type d -name __pycache__ 2>/dev/null | wc -l)

if [ "$CACHE_FOUND" -gt 0 ]; then
    echo "  ⚠️  WARNING: Python cache found ($CACHE_FOUND directories) - may cause old code to run"
    echo "  Run ./CLEAR_PYTHON_CACHE.sh to fix this"
    ((WARNINGS++))
else
    echo "  ✓ PASS: No Python cache files found"
fi

echo ""

# Check 4: Email Notification Fix (ASX)
echo "[CHECK 4/4] Verifying ASX Email Notification..."
if grep -q "self.notifier.send_morning_report(" models/screening/overnight_pipeline.py 2>/dev/null; then
    if grep -q "self.notifier.send_morning_report()(" models/screening/overnight_pipeline.py 2>/dev/null; then
        echo "  ❌ FAIL: Double parentheses detected in email notification"
        ((ERRORS++))
    else
        echo "  ✓ PASS: Email notification code looks correct"
    fi
else
    echo "  ❌ FAIL: Email notification code not found"
    ((ERRORS++))
fi

echo ""
echo "============================================================================"
echo "  VERIFICATION RESULTS"
echo "============================================================================"
echo ""
echo "  Critical Errors: $ERRORS"
echo "  Warnings: $WARNINGS"
echo ""

if [ $ERRORS -gt 0 ]; then
    echo "  ❌ CODE VERSION IS OUT OF DATE OR CORRUPTED"
    echo ""
    echo "  ACTION REQUIRED:"
    echo "  1. Re-extract the latest deployment package"
    echo "  2. Run ./CLEAR_PYTHON_CACHE.sh"
    echo "  3. Run this verification again"
    echo ""
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo "  ⚠️  WARNINGS DETECTED - Review Above"
    echo ""
    echo "  RECOMMENDED ACTIONS:"
    if [ "$CACHE_FOUND" -gt 0 ]; then
        echo "  - Run ./CLEAR_PYTHON_CACHE.sh to remove old cache files"
    fi
    echo "  - Review the warnings above"
    echo "  - Run ./QUICK_TEST.sh to verify functionality"
    echo ""
    exit 0
else
    echo "  ✅ ALL CHECKS PASSED"
    echo ""
    echo "  Your code version is up to date with v1.3.20.1"
    echo "  You can proceed with running the screening system."
    echo ""
    echo "  Next Steps:"
    echo "  1. Run ./QUICK_TEST.sh to verify functionality"
    echo "  2. Or run ./RUN_BOTH_MARKETS.sh for full screening"
    echo ""
    exit 0
fi
