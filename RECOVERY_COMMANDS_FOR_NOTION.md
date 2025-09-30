# 🚨 CRITICAL RECOVERY COMMANDS - SAVE TO NOTION

## 📌 Quick Recovery (Copy These First!)

### Immediate Recovery Commands
```bash
# 1. STOP all broken services
pkill -f "python.*backend"
pkill -f "python.*enhanced"
pkill -f "http.server"

# 2. RESTORE working backend
cp /home/user/webapp/protected_working_code/PROTECTED_backend_fixed_v1.py /home/user/webapp/backend_fixed.py

# 3. RESTORE working dashboard
cp /home/user/webapp/protected_working_code/PROTECTED_dashboard_v1.html /home/user/webapp/simple_working_dashboard.html

# 4. START the fixed backend
cd /home/user/webapp && python backend_fixed.py &

# 5. VERIFY it's working
python /home/user/webapp/verify_integrity.py
```

## ✅ Verified Working Configuration

### Backend Status (WORKING)
- **File**: `/home/user/webapp/backend_fixed.py`
- **Port**: 8002
- **All Ordinaries**: 9,135.90 points, **-0.14% change** ✅
- **Key Feature**: Uses `hist['Close'].iloc[-2]` for accurate previous close
- **NO synthetic data** - Real Yahoo Finance only

### Protected Files Location
```
/home/user/webapp/protected_working_code/
├── PROTECTED_backend_fixed_v1.py     # Working backend
├── PROTECTED_dashboard_v1.html       # Working dashboard  
├── checksums.md5                     # File integrity
└── README.md                         # Documentation
```

## 🔍 Verification Commands

### Check Data Accuracy
```bash
# Quick check - should show -0.14% for All Ordinaries
curl -s http://localhost:8002/api/indices | python3 -c "
import json, sys
data = json.load(sys.stdin)
aord = data['indices']['^AORD']
print(f'All Ords: {aord[\"price\"]:.2f} ({aord[\"changePercent\"]:.2f}%)')
"
```

### Full System Verification
```bash
# Run comprehensive checks
python /home/user/webapp/verify_integrity.py
```

### Check for Synthetic Data
```bash
# Should return EMPTY (no synthetic data)
grep -r "Math.random" /home/user/webapp/*.py /home/user/webapp/*.html
```

## 🛠️ Git Recovery Points

### Restore from Git Tags
```bash
# View available recovery points
git tag -l

# Restore to working version
git checkout working-backend-v1 -- backend_fixed.py
git checkout working-dashboard-v1 -- simple_working_dashboard.html
```

### File Checksums (For Verification)
```
a81fa746b1d51e8f766e0ede44b3fc9b  backend_fixed.py
d5ab10daa999affd4ea1a41cbee94776  simple_working_dashboard.html
```

## 🚫 Critical Rules - NEVER VIOLATE

1. **NO SYNTHETIC DATA** - Never use Math.random() or mock data
2. **REAL DATA ONLY** - Always use Yahoo Finance API (yfinance)
3. **CORRECT CALCULATIONS** - Previous close from `hist['Close'].iloc[-2]`
4. **PROTECT WORKING CODE** - Never modify without backup
5. **VERIFY BEFORE DEPLOY** - Run verify_integrity.py

## 📊 Current Running Services

### Clean Slate Commands
```bash
# View all Python processes
ps aux | grep python

# Kill specific services by port
lsof -ti:8002 | xargs kill -9  # Kill backend on 8002
lsof -ti:8090 | xargs kill -9  # Kill server on 8090
lsof -ti:3001 | xargs kill -9  # Kill server on 3001

# Kill all Python HTTP servers
pkill -f "python.*http.server"
```

## 🔧 Development Workflow (To Prevent Regression)

### Safe Development Process
```bash
# 1. Create backup before ANY changes
cp backend_fixed.py backend_fixed.py.backup

# 2. Test new versions on different port
cp backend_fixed.py backend_test.py
# Edit backend_test.py to use port 8003
python backend_test.py

# 3. Verify new version
curl http://localhost:8003/api/indices | grep "History-based"

# 4. Only replace if verification passes
python verify_integrity.py
```

## 📝 AI Tool Instructions (Copy to Notion)

### For Cursor/Aider/Copilot
```
CRITICAL REQUIREMENTS:
1. NEVER modify files in protected_working_code/
2. NEVER use Math.random() or synthetic data
3. ALWAYS use yfinance for real market data
4. ALWAYS verify All Ordinaries shows -0.14%
5. ALWAYS use hist['Close'].iloc[-2] for previous close
6. ALWAYS test on different port before replacing working version
```

## 🔄 Emergency Rollback Procedure

```bash
# Complete emergency recovery sequence
cd /home/user/webapp

# 1. Stop everything
pkill -f python

# 2. Restore from protected versions
cp protected_working_code/PROTECTED_backend_fixed_v1.py backend_fixed.py
cp protected_working_code/PROTECTED_dashboard_v1.html simple_working_dashboard.html

# 3. Restart backend
python backend_fixed.py &

# 4. Wait 5 seconds for startup
sleep 5

# 5. Verify recovery
python verify_integrity.py

# 6. Check specific value
curl -s http://localhost:8002/api/indices | grep -o '"^AORD".*changePercent":[^,]*' 
```

## 💾 Backup Commands

### Create Full Backup
```bash
cd /home/user/webapp
tar -czf market_tracker_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    backend_fixed.py \
    simple_working_dashboard.html \
    protected_working_code/ \
    verify_integrity.py \
    FILE_PROTECTION_STRATEGY.md
```

### Restore from Backup
```bash
# Extract backup
tar -xzf market_tracker_backup_*.tar.gz

# Restore and verify
python verify_integrity.py
```

## 📋 Checklist After Any AI Modification

- [ ] All Ordinaries shows -0.14% change
- [ ] No Math.random() in code
- [ ] Using hist['Close'].iloc[-2] for previous close
- [ ] Backend running on port 8002
- [ ] verify_integrity.py passes all checks
- [ ] Protected files unchanged
- [ ] Git commit created with tag

## 🎯 Current Working State (2025-09-30)

- **Backend**: Running on port 8002 ✅
- **All Ordinaries**: 9,135.90 points, -0.14% ✅
- **Data Source**: Yahoo Finance (History-based) ✅
- **Protected Version**: v1 saved and tagged ✅
- **Verification Script**: Available and working ✅

---

**SAVE THIS ENTIRE DOCUMENT TO NOTION IMMEDIATELY**

Keep this as your emergency recovery reference. The protected versions are your guaranteed working baseline.