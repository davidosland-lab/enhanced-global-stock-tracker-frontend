# Framework for AI-Assisted Development of Multi-Module Finance Software

Based on research of current best practices in 2024-2025 for AI development workflows.

## 1. RECOMMENDED DEVELOPMENT STACK

### AI Coding Assistants (Choose One):
- **Cursor IDE** - Full IDE with AI integration, context-aware code generation
- **Aider** - Terminal-based, excellent Git integration, automatic commits
- **GitHub Copilot** - Multi-model support, integrated with GitHub

### Version Control Strategy:
- **Monorepo Architecture** - All modules in single repository
- **Feature Branch Workflow** - Each feature/fix in separate branch
- **Semantic Versioning** - v1.0.0 format with clear releases

### Project Structure:
```
financial-app/
├── .github/
│   ├── workflows/        # CI/CD pipelines
│   └── CODEOWNERS        # Module ownership
├── packages/             # Monorepo modules
│   ├── core/            # Shared utilities
│   ├── market-tracker/  # Module 1
│   ├── cba-analyzer/    # Module 2
│   ├── technical/       # Module 3
│   └── predictions/     # Module 4
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEVELOPMENT.md
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .aider.conf.yml      # Aider configuration
├── .cursorrules         # Cursor IDE rules
└── STATE.json           # Project state tracking
```

## 2. AI DEVELOPMENT WORKFLOW

### Phase 1: Planning & Context
```yaml
# .cursorrules or .aider.conf.yml
project_rules:
  - NEVER use synthetic/demo data
  - ALWAYS test before claiming complete
  - PRESERVE working code (never modify without backup)
  - USE real Yahoo Finance API only
  
module_status:
  market_tracker: stable
  cba_analyzer: in_development
  technical_charts: broken
  
data_sources:
  - endpoint: http://localhost:8000/api
  - type: real_time
  - no_mock_data: true
```

### Phase 2: Development Process

#### Using Aider (Recommended for Your Case):
```bash
# Start with Git repo
git init
aider --model claude-3-opus

# Aider automatically:
# - Creates commits for each change
# - Writes descriptive commit messages
# - Maintains Git history
# - Allows easy rollback

# Work on specific module
aider packages/market-tracker/

# Test changes
npm test packages/market-tracker/

# If tests pass, continue; if not, rollback
git reset --hard HEAD~1
```

#### Using Cursor IDE:
```javascript
// .cursor/prompts/module_development.md
Context: Financial app with real Yahoo Finance data
Module: Market Tracker
Requirements:
- Use ONLY real data from localhost:8000
- Test all changes before committing
- Never break working modules

Current State:
- Backend: Working on port 8000
- Frontend: Broken links
- Data: Real Yahoo Finance

Task: Fix frontend without touching backend
```

## 3. VERSION CONTROL BEST PRACTICES

### Git Workflow:
```bash
# Main branch protection
main (production-ready)
├── develop (integration)
├── feature/market-tracker-fix
├── feature/add-all-ordinaries
└── hotfix/real-data-only

# Commit Strategy
git add packages/market-tracker/
git commit -m "fix(market-tracker): use real Yahoo Finance data

- Remove all synthetic data generation
- Connect to localhost:8000 API
- Add All Ordinaries index
- Fix timezone to AEST

Closes #123"
```

### GitHub Integration:

#### GitHub Actions CI/CD:
```yaml
# .github/workflows/test.yml
name: Test & Deploy
on:
  pull_request:
    paths:
      - 'packages/**'
      
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Test changed packages
        run: |
          # Only test modified packages
          npm test --since main
      
  validate-data:
    runs-on: ubuntu-latest
    steps:
      - name: Verify no synthetic data
        run: |
          # Scan for mock/demo data patterns
          ! grep -r "mockData\|demoPrice\|Math.random" packages/
```

## 4. STATE MANAGEMENT & MEMORY

### Project State Tracking:
```json
// STATE.json - Updated by CI/CD
{
  "version": "9.4.0",
  "modules": {
    "market_tracker": {
      "status": "working",
      "last_working_commit": "abc123",
      "test_coverage": 85,
      "uses_real_data": true
    },
    "cba_analyzer": {
      "status": "broken",
      "issue": "links not working",
      "last_working_commit": "def456"
    }
  },
  "data_sources": {
    "yahoo_finance": "active",
    "mock_data": "disabled"
  },
  "last_verified": "2025-09-30T12:00:00Z"
}
```

### AI Context Preservation:
```markdown
# CONTEXT.md - Read by AI on each session
## DO NOT MODIFY RULES
1. Backend on port 8000 is WORKING - DO NOT TOUCH
2. Use ONLY real Yahoo Finance data
3. Test before claiming fixed

## Working Versions
- Backend: commit abc123 (2025-09-29)
- Market Tracker: commit def456 (2025-09-28)

## Current Issues
- Dashboard links broken
- CBA module not loading
- Technical analysis errors

## Test Commands
```bash
curl http://localhost:8000/api/indices  # Should return real data
npm test packages/market-tracker/       # Should pass
```
```

## 5. TESTING STRATEGY

### Automated Testing:
```javascript
// tests/integration/real-data.test.js
describe('Real Data Validation', () => {
  it('should never use synthetic data', async () => {
    const response = await fetch('http://localhost:8000/api/indices');
    const data = await response.json();
    
    // Check against known market behavior
    expect(data['^AORD'].changePercent).toBeCloseTo(-0.14, 1);
    expect(data['^GSPC'].lastClose).toBeCloseTo(0.26, 1);
    
    // Ensure no perfect round numbers (sign of fake data)
    expect(data['^AORD'].price % 1).not.toBe(0);
  });
  
  it('should have all module links working', async () => {
    const links = [
      '/market-tracker',
      '/cba-analyzer',
      '/technical-analysis'
    ];
    
    for (const link of links) {
      const response = await fetch(`http://localhost:3001${link}`);
      expect(response.status).toBe(200);
    }
  });
});
```

## 6. DEPLOYMENT & ROLLBACK

### Deployment Strategy:
```yaml
# Canary Deployment
stages:
  - test: Run all tests
  - backup: Save current working version
  - deploy: Deploy to 10% of users
  - validate: Check error rates
  - rollout: Full deployment
  - rollback: If errors > threshold
```

### Rollback Procedure:
```bash
# Quick rollback to last working version
git tag -l "working-*"  # List all working versions
git checkout working-v9.3
npm install
npm start

# Create restore point before changes
git tag working-$(date +%Y%m%d-%H%M%S)
git push --tags
```

## 7. RECOMMENDED APPROACH FOR YOUR PROJECT

### Immediate Actions:

1. **Setup Aider** (for automatic Git commits):
```bash
pip install aider-chat
cd /home/user/webapp
git init
aider --model claude-3.5-sonnet
```

2. **Create Immutable Base**:
```bash
# Save working backend
cp enhanced_market_backend.py WORKING_BACKEND_DO_NOT_MODIFY.py
git add -A
git commit -m "checkpoint: working backend with real data"
git tag working-backend-v1
```

3. **Module-by-Module Fix**:
```bash
# Fix one module at a time
aider packages/market-tracker/
# Test immediately
npm test packages/market-tracker/
# If working, commit and tag
git tag working-market-tracker-v1
```

4. **Use Feature Branches**:
```bash
git checkout -b fix/market-tracker-real-data
# Make changes
# Test thoroughly
git checkout main
git merge --no-ff fix/market-tracker-real-data
```

## 8. PREVENTING REGRESSION

### Pre-commit Hooks:
```bash
# .git/hooks/pre-commit
#!/bin/bash
# Prevent synthetic data
if grep -r "Math.random\|mockData\|demoPrice" packages/; then
  echo "ERROR: Synthetic data detected!"
  exit 1
fi

# Run tests
npm test || exit 1
```

### Protected Files:
```gitignore
# .gitignore
WORKING_*
*_DO_NOT_MODIFY.*
STATE.json.lock
```

## 9. COST OPTIMIZATION

### Reduce AI Token Usage:
1. **Smaller, focused prompts**: "Fix dashboard links" not "Fix everything"
2. **Provide context files**: CONTEXT.md, STATE.json
3. **Use git diff**: Show only what changed
4. **Test locally first**: Before asking AI to verify

### Incremental Development:
```bash
# Instead of:
"Build complete financial application"

# Use:
"Fix the dashboard link to market-tracker module"
"Add All Ordinaries to the indices list"
"Change data source from mock to API"
```

## 10. RECOVERY PLAN

If everything breaks:
```bash
# 1. Find last working version
git log --oneline --grep="working"

# 2. Create fresh start
git checkout -b recovery
cp WORKING_BACKEND_DO_NOT_MODIFY.py backend.py

# 3. Build minimal working version
echo "Create simple HTML that fetches and displays real data"

# 4. Test thoroughly
curl http://localhost:8000/api/indices

# 5. Only then add features
git add -A
git commit -m "recovery: minimal working version"
git tag working-minimal-v1
```

---

## SUMMARY FOR YOUR SITUATION

1. **Use Aider** - Automatic Git commits will preserve your progress
2. **Monorepo structure** - Keep all modules in one repo for easier management
3. **Feature branches** - Never work directly on main
4. **STATE.json** - Track what works and what doesn't
5. **Test before claiming fixed** - Automated tests prevent false "fixed" claims
6. **Incremental fixes** - One module at a time
7. **Protected working files** - Never modify files marked as working

This framework ensures:
- No loss of working code
- Real data only
- Trackable progress
- Easy rollback
- Lower costs through focused development