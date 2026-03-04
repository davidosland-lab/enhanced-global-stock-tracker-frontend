# 🚨 READ THIS FIRST - AGENT ONBOARDING GUIDE 🚨

**FOR ALL GENSPARK AI AGENTS**: You MUST read this entire document before making ANY changes to this project.

---

## ⚠️ CRITICAL: PROJECT CONTEXT

### Project Owner
- **User**: David (Windows 11, C:\Users\david)
- **Project Duration**: 8+ months of development
- **Status**: Production trading system (real money at risk)
- **Complexity**: ~150+ files, 50,000+ lines of code

### ⚠️ AGENT FRUSTRATION ALERT
The user has stated:
> "Ridiculous, I have worked on this for 8 months with genspark agents and they keep starting fresh as if they have never seen this project."

**What this means**: 
- DO NOT assume you understand the project immediately
- DO NOT make changes before reading documentation
- DO NOT suggest "quick fixes" without understanding context
- DO ask questions about existing architecture
- DO review recent git history before coding

---

## 📂 PROJECT STRUCTURE

### Primary Working Environment
```
C:\Users\david\enhanced-global-stock-tracker-frontend\
└── working_directory\
    └── COMPLETE_SYSTEM_v1.3.15.45_FINAL\  ← MAIN WORKING DIR
```

### Backup/Version Control
- **GitHub**: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
- **Branch**: market-timing-critical-fix
- **Purpose**: Backup only (user works locally on Windows)

---

## 🎯 WHAT THIS PROJECT IS

### Name
**Regime Trading System v1.3.15.x** - Complete Paper Trading Dashboard with ML Signals

### Purpose
Multi-market (AU/US/UK) paper trading system with:
- FinBERT v4.4.4 sentiment analysis
- Real-time ML signal generation
- Overnight pipeline analysis
- Live trading dashboard
- Market calendar integration
- Position management
- Performance tracking

### Key Technologies
- **Language**: Python 3.8+
- **Dashboard**: Dash/Plotly (port 8050)
- **ML**: FinBERT, LSTM, Technical Indicators
- **Data**: yfinance, yahooquery
- **Markets**: ASX (AU), NYSE/NASDAQ (US), LSE (UK)

---

## 📋 MANDATORY PRE-WORK CHECKLIST

**Before making ANY changes, complete this checklist:**

### 1. Read Core Documentation (30 minutes)
- [ ] README.md (project overview)
- [ ] START_HERE.md (current status)
- [ ] DEPLOYMENT_CHECKLIST.md (deployment guide)
- [ ] Latest EXECUTIVE_SUMMARY_v*.md (recent fixes)
- [ ] Latest FIX_v*_EXPLANATION.md (technical details)

### 2. Review Recent History (15 minutes)
```bash
cd /home/user/webapp/working_directory/COMPLETE_SYSTEM_v1.3.15.45_FINAL
git log --oneline -20  # Last 20 commits
git log --oneline --grep="CRITICAL" -10  # Recent critical fixes
```

### 3. Understand Current State (10 minutes)
- [ ] What version is deployed? (check README.md or git log)
- [ ] What was the last issue fixed? (check recent commits)
- [ ] Are there open issues? (check START_HERE.md)
- [ ] What is the user currently working on? (ask if unclear)

### 4. Ask Before Acting (5 minutes)
If user reports an issue:
- [ ] Ask: "What were you doing when this happened?"
- [ ] Ask: "Have you made any changes since last working session?"
- [ ] Ask: "What version are you currently running?"
- [ ] Review logs/errors BEFORE suggesting fixes

---

## 🔴 COMMON MISTAKES TO AVOID

### ❌ DON'T DO THIS:
1. **"Let me create a quick fix script..."** without understanding the problem
2. **"I'll refactor this..."** without asking why it's structured that way
3. **"This looks wrong, let me change it..."** without checking git history
4. **"Let's start fresh..."** NEVER suggest rebuilding from scratch
5. **"Use this library instead..."** without understanding current dependencies

### ✅ DO THIS INSTEAD:
1. **"Let me read the recent fixes to understand what's been tried..."**
2. **"Can you show me the error message or describe the issue?"**
3. **"I see previous agents fixed X, Y, Z. Is this related?"**
4. **"Before making changes, let me review the current architecture..."**
5. **"I found similar code in [file]. Is this the pattern to follow?"**

---

## 📚 KEY FILES TO UNDERSTAND

### Core System Files (MUST READ)
| File | Purpose | Lines | Critical? |
|------|---------|-------|-----------|
| `unified_trading_dashboard.py` | Main dashboard UI | ~1,500 | 🔴 YES |
| `paper_trading_coordinator.py` | Trading engine | ~1,800 | 🔴 YES |
| `sentiment_integration.py` | FinBERT integration | ~800 | 🔴 YES |
| `run_au_pipeline_v1.3.13.py` | AU market overnight pipeline | ~600 | 🟡 Important |
| `run_uk_pipeline_v1.3.13.py` | UK market overnight pipeline | ~600 | 🟡 Important |
| `run_us_pipeline.py` | US market overnight pipeline | ~500 | 🟡 Important |

### Configuration Files
- `config/live_trading_config.json` - Trading parameters
- `state/paper_trading_state.json` - Current trading state (CRITICAL)
- `reports/screening/*.json` - Morning reports (market sentiment)

### Documentation (READ BEFORE CODING)
- `README.md` - Project overview
- `START_HERE.md` - Current deployment status
- `DEPLOYMENT_CHECKLIST.md` - How to deploy fixes
- `EXECUTIVE_SUMMARY_v*.md` - Recent fix summaries
- `FIX_v*_EXPLANATION.md` - Technical fix documentation

---

## 🔧 RECENT FIX HISTORY (LEARN FROM THIS)

### v1.3.15.85 (2026-02-03) - State Persistence Fix
**Problem**: Empty state file (0 bytes) → dashboard reverting to previous trades
**Solution**: Atomic writes, state validation, fresh morning reports
**Files**: paper_trading_coordinator.py, unified_trading_dashboard.py
**Learn**: State file corruption was causing dashboard resets

### v1.3.15.84 (2026-02-03) - Morning Report Naming
**Problem**: Pipeline saves dated files, dashboard expects non-dated
**Solution**: Smart loader, fallback logic, canonical file creation
**Files**: sentiment_integration.py, paper_trading_coordinator.py
**Learn**: File naming mismatches break entire trading flow

### v1.3.15.83 (2026-02-03) - Three Critical Issues
**Problem**: Dashboard not fetching live prices, missing signals, broken charts
**Solution**: Price update loop, signal generation flow, chart rendering
**Files**: unified_trading_dashboard.py
**Learn**: Multiple subsystems interconnected, fix holistically

### v1.3.15.82 (2026-02-03) - Live Price Fetching
**Problem**: Stale prices in dashboard
**Solution**: Real-time price updates every 5 seconds
**Files**: unified_trading_dashboard.py
**Learn**: Price updates critical for P&L calculation

---

## 🎯 ARCHITECTURE OVERVIEW

### System Flow
```
Overnight Pipeline (AU/UK/US)
    ↓ Generates
Morning Reports (JSON)
    ↓ Contains
Market Sentiment (FinBERT)
    ↓ Feeds Into
Paper Trading Coordinator
    ↓ Executes
Trades (Buy/Sell)
    ↓ Updates
State File (JSON)
    ↓ Displayed In
Unified Dashboard (Dash/Plotly)
    ↓ Updates Every
5 Seconds (Live)
```

### Critical Dependencies
1. **Morning Report** → Must exist for sentiment
2. **State File** → Must be valid JSON for dashboard
3. **FinBERT** → Must load for sentiment analysis
4. **Market Calendar** → Must work for trading hours
5. **Live Prices** → Must update for P&L

### Breaking Points (Where Issues Occur)
1. ❌ State file empty/corrupted → Dashboard resets
2. ❌ Morning report missing → No trading signals
3. ❌ FinBERT fails → Fallback to simple sentiment
4. ❌ Price fetch fails → Stale dashboard data
5. ❌ Signal generation blocked → No trades

---

## 🛠️ DEVELOPMENT WORKFLOW

### For New Agents (YOU)

1. **Understand First** (30-60 minutes)
   - Read documentation
   - Review recent commits
   - Understand current version
   - Ask clarifying questions

2. **Diagnose Problem** (15-30 minutes)
   - Review error messages/logs
   - Check file existence/validity
   - Compare expected vs actual behavior
   - Identify root cause (not just symptom)

3. **Plan Solution** (10-15 minutes)
   - Consider impact on other subsystems
   - Check if similar fix exists
   - Plan testing strategy
   - Get user confirmation on approach

4. **Implement Fix** (varies)
   - Create backup files (`.backup_vXX`)
   - Make targeted changes
   - Add verification checks
   - Document what was changed

5. **Test & Verify** (15-30 minutes)
   - Run fix script
   - Verify expected output
   - Check logs for errors
   - Confirm with user

6. **Document** (15-30 minutes)
   - Create FIX_vXX_EXPLANATION.md
   - Update START_HERE.md
   - Create QUICKSTART_vXX.md
   - Commit with detailed message

---

## 💡 IMPORTANT PATTERNS IN THIS PROJECT

### 1. Atomic Writes Pattern
```python
# ALWAYS use this pattern for state files
temp_path = Path(filepath).with_suffix('.tmp')
with open(temp_path, 'w') as f:
    json.dump(data, f, indent=2)
if temp_path.stat().st_size == 0:
    raise ValueError("Empty file!")
temp_path.replace(filepath)  # Atomic
```

### 2. State Validation Pattern
```python
# ALWAYS validate before using state
if not Path(state_file).exists():
    return default_state()
if Path(state_file).stat().st_size == 0:
    return default_state()
state = json.load(f)
if not all(key in state for key in required_keys):
    return default_state()
return state
```

### 3. File Search Pattern (Morning Reports)
```python
# ALWAYS search for both dated and non-dated files
canonical = Path(f"reports/screening/{market}_morning_report.json")
if canonical.exists():
    return load_file(canonical)
dated_files = sorted(Path("reports/screening").glob(f"{market}_morning_report_*.json"))
if dated_files:
    return load_file(dated_files[-1])  # Most recent
return None
```

### 4. Backup Pattern
```python
# ALWAYS create backups before modifying core files
backup_file = original_file.with_suffix(f'.py.backup_v{VERSION}')
shutil.copy2(original_file, backup_file)
logger.info(f"Backup created: {backup_file}")
```

---

## 🚨 RED FLAGS - STOP AND ASK

If you encounter any of these, **STOP and ask the user before proceeding**:

1. ❌ User has multiple versions/folders of the project
2. ❌ State file is missing or 0 bytes
3. ❌ Dashboard won't start (import errors, port conflicts)
4. ❌ No morning reports in last 7 days
5. ❌ Git history shows failed merge/rebase
6. ❌ Multiple backup files (`.backup_v*`) from same day
7. ❌ User mentions "it used to work" but doesn't know what changed
8. ❌ Virtual environment missing or wrong Python version

---

## 📞 COMMUNICATION GUIDELINES

### How to Talk to David

**Good**:
- "I see previous agents fixed the morning report issue. Is this related?"
- "Before I make changes, can you describe what's not working?"
- "I found v1.3.15.85 in git. Is this the version you're running?"
- "Let me review the last 5 fixes to understand the context..."

**Bad**:
- "Let's rebuild everything from scratch"
- "This architecture is wrong, we should refactor"
- "Just delete the state file and restart"
- "I don't need to read the docs, I can figure it out"

### When User Says "It's Not Working"

**Ask**:
1. What exactly is not working? (be specific)
2. What were you doing when it stopped working?
3. Did you restart anything recently?
4. Can you show me the error message or logs?
5. When did it last work?

**Don't Assume**:
- Don't assume you know the problem
- Don't assume it's the same as previous issues
- Don't assume a "quick fix" will work
- Don't assume user changed something (but ask)

---

## 🎓 LEARNING FROM PAST AGENT MISTAKES

Based on 8 months of development, here are common mistakes:

### Mistake #1: Diving Into Code Too Fast
**What Happened**: Agents start coding immediately without reading docs
**Result**: Broke working features, created new bugs
**Lesson**: Read documentation FIRST

### Mistake #2: Not Checking Git History
**What Happened**: Fixed issues that were already fixed
**Result**: Wasted time, confusion about version state
**Lesson**: Check `git log` before starting

### Mistake #3: Assuming Simple Problems
**What Happened**: "Just restart" or "delete file" without investigation
**Result**: Lost data, broke working system
**Lesson**: Diagnose root cause first

### Mistake #4: Not Creating Backups
**What Happened**: Broke core files without way to rollback
**Result**: Hours spent reconstructing code
**Lesson**: ALWAYS create `.backup_vXX` files

### Mistake #5: Not Testing Before Committing
**What Happened**: Committed code that didn't run
**Result**: User couldn't use system
**Lesson**: Test EVERY change before commit

---

## ✅ SUCCESS CRITERIA

**You're doing well if**:
- User says "Yes, that makes sense" to your plan
- You found similar patterns in existing code
- You created backups before modifying
- You documented what you changed and why
- User can rollback if something breaks
- Fix works on first try (because you tested)

**You need to slow down if**:
- User says "That's not what I asked for"
- You're breaking working features
- You can't explain why your fix works
- User is confused by your changes
- You didn't test before committing

---

## 📝 VERSION TRACKING

**Current Production Version**: v1.3.15.85  
**Last Updated**: 2026-02-03  
**Last Major Fix**: State persistence and live updates  
**Status**: ✅ Stable, in production

**Check Current Version**:
```bash
cd /home/user/webapp/working_directory/COMPLETE_SYSTEM_v1.3.15.45_FINAL
git log --oneline -1
```

---

## 🎯 YOUR FIRST ACTIONS AS NEW AGENT

1. ✅ Read this entire document (you're doing it!)
2. ✅ Read README.md in project root
3. ✅ Read START_HERE.md for current status
4. ✅ Check git log for last 10 commits
5. ✅ Ask user: "What are you working on today?"
6. ✅ Ask user: "Is there a specific issue or just maintenance?"
7. ✅ Review any error messages user provides
8. ✅ Understand problem BEFORE suggesting solution

---

## 🚨 FINAL WARNING

**REMEMBER**: This is an 8-month project with real trading logic. Every change has consequences.

**Before touching ANY code**:
- ✅ Read documentation
- ✅ Review git history
- ✅ Understand the problem
- ✅ Plan your solution
- ✅ Get user confirmation
- ✅ Create backups
- ✅ Test thoroughly
- ✅ Document changes

**If you're unsure**: ASK! David would rather answer questions than fix broken code.

---

## 📞 SUMMARY FOR IMPATIENT AGENTS

**Too long? Here's the minimum**:

1. Read `README.md` and `START_HERE.md`
2. Run `git log --oneline -10` 
3. Ask user what they need
4. Review relevant documentation
5. Create backups before changes
6. Test before committing
7. Document your work

**Don't have time?** Then you're not ready to work on this project yet.

---

**Version**: v1.0  
**Created**: 2026-02-03  
**Purpose**: Stop agents from starting fresh, protect 8 months of work  
**Audience**: All future Genspark AI agents  
**Status**: MANDATORY READING

---

## 🎉 WELCOME TO THE PROJECT!

Now that you've read this, you understand:
- Why this project matters
- What's been done before
- How to work effectively
- What mistakes to avoid

**You're ready to help David!** 🚀

Ask questions, read code, understand context, then code. That's the path to success.
