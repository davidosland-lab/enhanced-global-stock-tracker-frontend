# Session Restore Guide - Quick Start for Next Session

## 🚀 Quick Start Commands

### 1. Check Backend Status
```bash
# Check if backend is running
ps aux | grep backend_fixed

# If not running, start it
cd /home/user/webapp/working_directory
python backend_fixed.py &
```

### 2. Start Frontend Server
```bash
cd /home/user/webapp/working_directory
python3 -m http.server 8080 &
```

### 3. Get Service URLs
```bash
# Backend API
curl https://8002-[sandbox-id].e2b.dev/

# Frontend
# Visit: https://8080-[sandbox-id].e2b.dev/main.html
```

## 📊 Current Chart Versions

### PRIMARY: Fixed Timeline Chart
**URL**: `/modules/market-tracking/fixed_timeline_chart.html`
**Status**: ✅ WORKING
**Features**:
- 24-hour timeline (00:00-23:59 AEST)
- Market-aligned data points
- No synthetic data

### Key Files to Remember
1. `backend_fixed.py` - DO NOT MODIFY (working correctly)
2. `fixed_timeline_chart.html` - Latest working version
3. `CRITICAL_PROJECT_REQUIREMENTS.md` - Absolute rules

## 🔴 Critical Reminders

### NEVER DO:
- Add synthetic/mock data (NO Math.random())
- Modify backend_fixed.py
- Use localhost in sandbox (use sandbox URL)
- Create separate cards (use ONE chart)

### ALWAYS DO:
- Use real Yahoo Finance data
- Maintain colors: ASX red, FTSE blue, S&P purple
- Keep Y-axis at ±0.6%
- Use AEST timezone

## 📁 Project Structure
```
working_directory/
├── backend_fixed.py          # Backend server (port 8002)
├── main.html                 # Dashboard
└── modules/market-tracking/
    └── fixed_timeline_chart.html  # Current best version
```

## 🎯 Current State Summary

### What's Working:
- ✅ Real Yahoo Finance data flowing
- ✅ Three markets on one chart
- ✅ Proper 24-hour timeline
- ✅ Data aligned to market hours
- ✅ Backend connection in sandbox

### Next Priorities:
1. Real-time updates during market hours
2. Historical data analysis features
3. Additional markets
4. Performance optimizations

## 🔧 Troubleshooting

### If "Backend not found" error:
1. Check backend is running: `ps aux | grep backend`
2. Use sandbox URL, not localhost
3. Check CORS is enabled in backend

### If "Invalid Date" on chart:
- Data format issue (Close vs close)
- Already fixed in current version

### If no lines showing:
- Markets are closed (expected behavior)
- Check backend is returning data
- Verify time alignment logic

## 📝 Git Commands

```bash
# Check status
git status

# View recent commits
git log --oneline -10

# Push changes
git add -A
git commit -m "Your message"
git push origin main
```

## 🌐 Repository
**GitHub**: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
**Branch**: main

---
**Last Updated**: October 2, 2024
**Session Ready**: YES