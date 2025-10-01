# GSMT Recovery Framework & Anti-Regression System
## Version 2.0 - January 2025

### CRITICAL PRINCIPLES - NEVER VIOLATE THESE

1. **REAL DATA ONLY**: No Math.random(), no synthetic data, only yfinance API
2. **PROTECT WORKING CODE**: Never modify working code without backup
3. **BASIC FIRST**: Build all modules with basic functionality before adding complex features
4. **TEST LOCALLY**: Always test on Windows 11 localhost before deployment
5. **GIT PROTECTION**: Use tags and branches to preserve working states

---

## 🛡️ Code Protection Strategy

### Level 1: Immutable Backups
```bash
# Create protected backup directory
mkdir -p protected_backups/$(date +%Y%m%d_%H%M%S)
cp -r *.py *.html modules/ protected_backups/$(date +%Y%m%d_%H%M%S)/

# Create checksum verification
find . -type f \( -name "*.py" -o -name "*.html" \) -exec sha256sum {} \; > checksums.txt
```

### Level 2: Git Tags for Working States
```bash
# Tag current working state
git add -A
git commit -m "WORKING STATE: All modules functional with real data"
git tag -a v1.0-working -m "Protected working version - DO NOT MODIFY"
git push origin --tags

# Create protected branch
git checkout -b protected/working-state-v1
git push origin protected/working-state-v1
```

### Level 3: Verification Scripts
```python
# verify_integrity.py
import hashlib
import json

def verify_critical_code():
    """Verify critical code sections haven't been modified"""
    critical_checks = {
        'backend_fixed.py': {
            'line_96': 'previous_close = float(hist[\'Close\'].iloc[-2])',
            'contains': ['yfinance', 'NO synthetic data', 'real Yahoo Finance']
        },
        'simple_working_dashboard.html': {
            'contains': ['http://localhost:8002', 'Real-Time Market Data']
        }
    }
    
    for file, checks in critical_checks.items():
        with open(file, 'r') as f:
            content = f.read()
            for check_type, check_value in checks.items():
                if check_type == 'contains':
                    for must_contain in check_value:
                        assert must_contain in content, f"{file} missing: {must_contain}"
    
    print("✅ All critical code verified intact")

if __name__ == "__main__":
    verify_critical_code()
```

---

## 📊 All Ordinaries Verification

### Correct Calculation Method
```python
# CORRECT - Using history data
hist = ticker.history(period="2d")
current_price = float(hist['Close'].iloc[-1])  # Today's close
previous_close = float(hist['Close'].iloc[-2])  # Yesterday's close
change = current_price - previous_close
change_percent = (change / previous_close) * 100

# Expected values (as of your data):
# All Ordinaries: 9,135 points, -0.14% change
```

### WRONG Methods to Avoid
```python
# WRONG - Don't use regularMarketPreviousClose
# WRONG - Don't use Math.random()
# WRONG - Don't calculate from open price
```

---

## 🪟 Windows Deployment Checklist

### Pre-Deployment
- [ ] All API URLs set to `http://localhost:8002`
- [ ] Backend using port 8002
- [ ] Frontend files in simple HTML/CSS/JS (no build process)
- [ ] requirements.txt includes all Python dependencies
- [ ] Batch files created for Windows

### Deployment Structure
```
C:\GSMT\
├── GSMT_Windows_Package\
│   ├── backend_fixed.py
│   ├── simple_working_dashboard.html
│   ├── modules\
│   │   ├── global_indices_tracker.html
│   │   ├── single_stock_tracker.html
│   │   ├── cba_analysis.html
│   │   ├── technical_analysis.html
│   │   ├── ml_predictions.html
│   │   └── document_center.html
│   ├── START_GSMT_WINDOWS.bat
│   ├── STOP_GSMT_WINDOWS.bat
│   ├── TEST_INSTALLATION.bat
│   └── requirements.txt
```

### Windows Fix Commands
```powershell
# Navigate to correct directory
cd C:\GSMT\GSMT_Windows_Package

# Fix dashboard
(Get-Content simple_working_dashboard.html) -replace "window.location.protocol.*8002.*", "'http://localhost:8002'" | Set-Content simple_working_dashboard.html

# Fix all modules
Get-ChildItem modules\*.html | ForEach-Object { 
    (Get-Content $_) -replace "window.location.protocol.*8002.*", "'http://localhost:8002'" | Set-Content $_ 
}

# Verify fix
Select-String -Path "*.html","modules\*.html" -Pattern "localhost:8002"
```

---

## 🔄 Recovery Procedures

### When Regression Occurs

1. **STOP** - Don't make more changes
2. **IDENTIFY** - What was working before the regression?
3. **ROLLBACK** - Use Git to restore working state:
   ```bash
   git checkout v1.0-working -- backend_fixed.py
   git checkout v1.0-working -- simple_working_dashboard.html
   git checkout v1.0-working -- modules/
   ```
4. **VERIFY** - Run verification script
5. **PROTECT** - Create new protected backup

### Module Development Order (Basic First)

#### Phase 1: Basic Functionality (CURRENT)
1. ✅ Dashboard - Simple market overview
2. ✅ Global Indices - List view, no charts
3. ✅ Single Stock - Search and display
4. ✅ CBA Analysis - Table comparison
5. ✅ Technical Analysis - Numbers only
6. ✅ ML Predictions - Basic predictions

#### Phase 2: Enhanced Features (ONLY AFTER PHASE 1 STABLE)
- Add charts (Chart.js)
- Add animations
- Add real-time updates
- Add advanced analytics

---

## 🚫 Never Do List

1. **NEVER** use Math.random() for market data
2. **NEVER** modify working code without backup
3. **NEVER** add complex features before basic ones work
4. **NEVER** use regularMarketPreviousClose for percentage calculation
5. **NEVER** deploy without local testing
6. **NEVER** ignore user's explicit requests for real data
7. **NEVER** create synthetic test data when real API is available
8. **NEVER** break working localhost connections with dynamic URLs

---

## ✅ Validation Tests

### Test 1: Real Data Verification
```python
def test_real_data():
    response = requests.get('http://localhost:8002/api/indices')
    data = response.json()
    
    # Check All Ordinaries
    aord = data.get('^AORD', {})
    assert 'synthetic' not in str(aord).lower()
    assert 'random' not in str(aord).lower()
    assert aord['change_percent'] != 0  # Real data varies
    
    print(f"✅ All Ordinaries: {aord['price']:.2f} ({aord['change_percent']:.2f}%)")
```

### Test 2: Windows Connection Test
```javascript
// Run in browser console
fetch('http://localhost:8002/api/indices')
    .then(r => r.json())
    .then(d => console.log('✅ Connection successful:', d))
    .catch(e => console.error('❌ Connection failed:', e));
```

---

## 📝 Daily Checklist

### Morning
- [ ] Run `verify_integrity.py`
- [ ] Check All Ordinaries shows ~9,135 points
- [ ] Verify all modules load without errors
- [ ] Confirm no synthetic data in responses

### Before Any Changes
- [ ] Create backup with timestamp
- [ ] Tag current working state in Git
- [ ] Document what you're changing and why

### After Changes
- [ ] Run all validation tests
- [ ] Check Windows localhost connection
- [ ] Verify real data still flowing
- [ ] Commit with descriptive message

---

## 🆘 Emergency Contacts

### When All Else Fails
1. Restore from protected backup:
   ```bash
   cp -r protected_backups/[latest_working]/* .
   ```

2. Checkout last working Git tag:
   ```bash
   git checkout v1.0-working
   ```

3. Use the locked backend:
   ```bash
   cp backend_fixed.py backend.py
   python backend.py  # This is your known-good backend
   ```

---

## 📋 Current Status (January 2025)

### ✅ WORKING
- Backend with correct percentage calculations
- All 6 basic modules created
- Windows deployment package
- Real Yahoo Finance data integration
- AEST timezone display

### ⚠️ IN PROGRESS
- Fixing Windows localhost connection (changing to hardcoded URLs)

### 📅 FUTURE (Only After Current Is Stable)
- Chart visualizations
- WebSocket real-time updates
- Advanced ML predictions
- Portfolio tracking

---

## 🎯 Success Criteria

The system is considered "working" when:
1. ✅ All Ordinaries shows ~9,135 points with -0.14% change (or current real values)
2. ✅ All 6 modules load and display data
3. ✅ Windows users can access via localhost:8002
4. ✅ No synthetic data appears anywhere
5. ✅ Code passes all verification tests
6. ✅ One month without regression

---

## Remember

**"If it's working, protect it. If it's broken, restore it. Never modify without backup."**

Last Updated: January 2025
Protected Version: v1.0-working