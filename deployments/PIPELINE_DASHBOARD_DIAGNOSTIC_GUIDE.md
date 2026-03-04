# Pipeline-to-Dashboard Signal Flow Diagnostic

**Script**: `scripts/test_pipeline_to_dashboard_flow.py`  
**Purpose**: Validate complete flow from overnight pipeline → trading dashboard signals  
**Version**: v1.3.15.158  
**Date**: 2026-02-17

---

## 🎯 **What This Tests**

This diagnostic validates the **critical assumption** that overnight pipeline outputs can generate actionable BUY/SELL signals for the trading dashboard.

### **Signal Flow**:
```
Overnight Pipeline
      ↓
Morning Report JSON (reports/screening/au_morning_report.json)
      ↓
EnhancedPipelineSignalAdapter (scripts/pipeline_signal_adapter_v3.py)
      ↓
ML Swing Signal Generator (ml_pipeline/swing_signal_generator.py)
      ↓
Combined Trading Signals (BUY/SELL with position sizing)
      ↓
Unified Trading Dashboard (core/unified_trading_dashboard.py)
```

---

## 🧪 **Test Suite**

### **Test 1: Pipeline Morning Reports Exist**
- ✅ Checks for `au_morning_report.json`, `uk_morning_report.json`, `us_morning_report.json`
- ✅ Validates file age (warns if >24 hours old)
- ✅ Reports path: `reports/screening/`

### **Test 2: Report Format Validation**
- ✅ Valid JSON structure
- ✅ Required fields present:
  - `timestamp`
  - `market`
  - `overall_sentiment` (0-100 score)
  - `recommendation` (BUY/HOLD/SELL)
  - `confidence` (LOW/MODERATE/HIGH)
  - `risk_rating` (Low/Moderate/High)

### **Test 3: Signal Adapter Initialization**
- ✅ `EnhancedPipelineSignalAdapter` can be imported
- ✅ Adapter initializes with ML enabled
- ✅ Weight configuration (60% ML, 40% sentiment)

### **Test 4: Overnight Sentiment Loading**
- ✅ `get_overnight_sentiment(market)` returns data
- ✅ Sentiment score extracted correctly
- ✅ Confidence and risk ratings available
- ✅ Top opportunities list included

### **Test 5: ML Signal Generation**
- ✅ `get_ml_signal(symbol)` works
- ✅ Historical data fetched (252 days)
- ✅ ML prediction generated
- ✅ Signal type determined (BUY/SELL/HOLD)
- ✅ Confidence score calculated

### **Test 6: Trading Signal Generation**
- ✅ `generate_signals(market)` produces signals
- ✅ BUY signals identified
- ✅ Position sizing calculated (5-30%)
- ✅ Combined score computed (ML + sentiment)
- ✅ Multiple markets supported

### **Test 7: Dashboard Signal Format**
- ✅ All required fields present:
  - `symbol`
  - `action` (BUY/SELL)
  - `position_size` (%)
  - `confidence` (%)
  - `entry_price` ($)
  - `stop_loss` ($)
  - `take_profit` ($)
- ✅ Signals ready for dashboard execution

---

## 🚀 **Usage**

### **Basic Test** (All Markets)
```powershell
cd "C:\Users\david\REgime trading V4 restored\unified_trading_system_v1.3.15.129_COMPLETE"
python scripts\test_pipeline_to_dashboard_flow.py
```

### **Test Specific Markets**
```powershell
# Test only AU market
python scripts\test_pipeline_to_dashboard_flow.py --markets AU

# Test AU and UK
python scripts\test_pipeline_to_dashboard_flow.py --markets AU UK
```

### **Save Diagnostic Report**
```powershell
python scripts\test_pipeline_to_dashboard_flow.py --save-report
```

This creates: `reports/diagnostics/signal_flow_diagnostic_YYYYMMDD_HHMMSS.json`

### **Custom Base Path**
```powershell
python scripts\test_pipeline_to_dashboard_flow.py --base-path "C:\path\to\trading\system"
```

---

## 📊 **Expected Output**

### **Successful Test**:
```
================================================================================
PIPELINE → DASHBOARD SIGNAL FLOW DIAGNOSTIC
================================================================================
Testing markets: AU, UK, US
Base path: C:\Users\david\REgime trading V4 restored\...
Reports path: C:\Users\david\...\reports\screening
================================================================================

================================================================================
TEST 1: Pipeline Morning Reports
================================================================================
✅ Report Exists: AU: Found at ...\au_morning_report.json (age: 2.3h)
✅ Report Exists: UK: Found at ...\uk_morning_report.json (age: 3.1h)
✅ Report Exists: US: Found at ...\us_morning_report.json (age: 4.5h)

================================================================================
TEST 2: Report Format - AU
================================================================================
✅ Report Format: AU: Valid format - Sentiment: 65.0, Confidence: MODERATE, Recommendation: CAUTIOUSLY_OPTIMISTIC

================================================================================
TEST 3: Signal Adapter Initialization
================================================================================
✅ Signal Adapter Init: Initialized (ML: True, ML weight: 60%)

================================================================================
TEST 4: Overnight Sentiment Loading - AU
================================================================================
✅ Overnight Sentiment: AU: Loaded - Score: 65.0/100, Confidence: MODERATE, Risk: Moderate

================================================================================
TEST 5: ML Signal Generation - CBA.AX
================================================================================
✅ ML Signal: CBA.AX: Generated - Signal: BUY, Prediction: 0.72, Confidence: 68%

================================================================================
TEST 6: Trading Signal Generation - AU
================================================================================
✅ Trading Signals: AU: Generated 3 signals (BUY: 3, SELL: 0)
✅ Signal Structure: CBA.AX: BUY @ 15.0% (confidence: 72%, score: 0.68)
✅ Signal Structure: BHP.AX: BUY @ 12.0% (confidence: 65%, score: 0.62)
✅ Signal Structure: NAB.AX: BUY @ 10.0% (confidence: 58%, score: 0.55)

================================================================================
TEST 7: Dashboard Signal Format
================================================================================
✅ Dashboard Ready: CBA.AX: All required fields present - BUY @ $105.50
✅ Dashboard Ready: BHP.AX: All required fields present - BUY @ $45.20
✅ Dashboard Ready: NAB.AX: All required fields present - BUY @ $28.30
✅ Dashboard Format Summary: Valid: 3/3 signals

================================================================================
DIAGNOSTIC SUMMARY
================================================================================
Total Tests: 21
✅ Passed: 21
❌ Failed: 0
⚠️  Warned: 0
Success Rate: 100.0%

✅ PASS - Pipeline → Dashboard signal flow is working
================================================================================
```

---

## ❌ **Failure Scenarios**

### **Scenario 1: No Pipeline Reports**
```
❌ Report Exists: AU: Missing: ...\au_morning_report.json
❌ Report Exists: UK: Missing: ...\uk_morning_report.json
❌ Report Exists: US: Missing: ...\us_morning_report.json

❌ FAIL - Critical issues blocking signal generation
Success Rate: 0.0%
```

**Fix**: Run overnight pipeline first:
```powershell
python pipelines\run_au_pipeline.py --mode full
```

### **Scenario 2: Reports Too Old**
```
⚠️ Report Exists: AU: Found at ...\au_morning_report.json (age: 26.5h)
```

**Fix**: Reports older than 24 hours should be regenerated. Run pipeline again.

### **Scenario 3: Invalid Report Format**
```
❌ Report Format: AU: Missing fields: overall_sentiment, recommendation
```

**Fix**: Pipeline output format changed. Check overnight_pipeline.py report generation.

### **Scenario 4: Signal Adapter Fails**
```
❌ Signal Adapter Init: Cannot import EnhancedPipelineSignalAdapter
```

**Fix**: Check imports and dependencies:
```powershell
python -c "from scripts.pipeline_signal_adapter_v3 import EnhancedPipelineSignalAdapter; print('OK')"
```

### **Scenario 5: No Signals Generated**
```
⚠️ Trading Signals: AU: No signals generated (may be expected if no BUY opportunities)
```

**Not necessarily an error** - indicates market conditions don't favor BUY signals currently.

---

## 🔍 **What Gets Validated**

### **Pipeline Output Quality**
- ✅ Reports are recent (<24h)
- ✅ Sentiment scores are reasonable (0-100)
- ✅ Recommendations are valid (BUY/HOLD/SELL)
- ✅ Confidence levels assigned

### **Signal Generation Pipeline**
- ✅ Overnight sentiment can be read
- ✅ ML models can generate predictions
- ✅ Signals are properly weighted (60% ML, 40% sentiment)
- ✅ BUY/SELL decisions are made

### **Dashboard Integration**
- ✅ Signals have all required fields
- ✅ Position sizes calculated (5-30%)
- ✅ Entry/stop/target prices set
- ✅ Confidence scores provided

---

## 📈 **Success Criteria**

| Success Rate | Verdict | Action |
|--------------|---------|--------|
| **≥80%** | ✅ PASS | Pipeline → Dashboard flow working |
| **50-79%** | ⚠️ PARTIAL | Some issues, but usable |
| **<50%** | ❌ FAIL | Critical problems, fix required |

---

## 🛠️ **Troubleshooting**

### **Problem: Import Errors**

**Symptom**:
```
❌ Cannot import EnhancedPipelineSignalAdapter
```

**Solution**:
```powershell
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify file exists
dir scripts\pipeline_signal_adapter_v3.py
```

### **Problem: No ML Signals**

**Symptom**:
```
⚠️ ML Signal: CBA.AX: get_ml_signal() returned None
```

**Solution**:
```powershell
# Check yfinance
python -c "import yfinance as yf; print('OK')"

# Check ML generator
python -c "from ml_pipeline.swing_signal_generator import SwingSignalGenerator; print('OK')"
```

### **Problem: Reports Not Found**

**Symptom**:
```
❌ Report file not found
```

**Solution**:
```powershell
# Run overnight pipeline
python pipelines\run_au_pipeline.py --mode test

# Check reports were created
dir reports\screening\*.json
```

---

## 📊 **Diagnostic Report Output**

When run with `--save-report`, creates JSON at:
```
reports/diagnostics/signal_flow_diagnostic_20260217_120530.json
```

**Report Structure**:
```json
{
  "timestamp": "2026-02-17T12:05:30.123456",
  "tests": [
    {
      "test": "Report Exists: AU",
      "status": "PASS",
      "details": "Found at ...",
      "data": {
        "path": "...",
        "age_hours": 2.3
      }
    },
    ...
  ],
  "summary": {
    "total_tests": 21,
    "passed": 21,
    "failed": 0,
    "warned": 0,
    "success_rate": 100.0
  }
}
```

---

## 🎯 **Use Cases**

### **1. Verify Pipeline Integration After Installation**
```powershell
# After installing v1.3.15.158
python scripts\test_pipeline_to_dashboard_flow.py --save-report
```

### **2. Debug Signal Generation Issues**
```powershell
# Test only problematic market
python scripts\test_pipeline_to_dashboard_flow.py --markets AU
```

### **3. Pre-Production Validation**
```powershell
# Before going live
python scripts\test_pipeline_to_dashboard_flow.py --markets AU UK US --save-report
```

### **4. Continuous Integration**
```powershell
# In CI/CD pipeline
python scripts\test_pipeline_to_dashboard_flow.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Signal flow tests passed"
} else {
    Write-Host "❌ Signal flow tests failed"
    exit 1
}
```

---

## 📝 **Exit Codes**

| Code | Meaning | Success Rate |
|------|---------|--------------|
| **0** | All tests passed | ≥80% |
| **1** | Partial success | 50-79% |
| **2** | Tests failed | <50% |

---

## 🎉 **Expected Results After v1.3.15.158**

With all fixes applied:

- ✅ **21/21 tests pass** (100% success rate)
- ✅ **3-5 BUY signals per market** (depending on conditions)
- ✅ **All signals dashboard-ready** (complete fields)
- ✅ **No import errors**
- ✅ **No format errors**

**This diagnostic proves the pipeline → dashboard integration is working end-to-end!** 🚀
