# FILE PROTECTION STRATEGY

## Three-Layer Protection System

### Layer 1: Protected Directory
- **Location**: `/home/user/webapp/protected_working_code/`
- **Purpose**: Immutable copies of verified working code
- **Naming**: `PROTECTED_[module]_v[version].py`
- **Access**: READ-ONLY reference copies

### Layer 2: Git Tags for Working Versions
```bash
# Tag working versions immediately after verification
git tag -a "working-backend-v1" -m "Backend with correct -0.14% for All Ords"
git tag -a "working-dashboard-v1" -m "Dashboard using real Yahoo Finance data"
```

### Layer 3: Checksums for Integrity
```bash
# Generate checksums for critical files
md5sum backend_fixed.py > checksums.md5
md5sum simple_working_dashboard.html >> checksums.md5

# Verify integrity before any changes
md5sum -c checksums.md5
```

## Development Rules to Prevent Regression

### Rule 1: Never Modify Working Files Directly
- Copy to new file with version suffix (e.g., `backend_v2.py`)
- Test new version on different port
- Only replace after verification

### Rule 2: Mandatory Testing Before Replacement
```python
# Test checklist for backend changes:
assert all_ordinaries_change == -0.14  # Must match real data
assert "Math.random" not in code  # No synthetic data
assert uses_history_data == True  # Must use hist['Close'].iloc[-2]
```

### Rule 3: Rollback Procedure
```bash
# If regression occurs:
1. Stop broken service
2. Restore from protected directory:
   cp protected_working_code/PROTECTED_backend_fixed_v1.py backend_fixed.py
3. Restart service on original port
4. Verify data accuracy
```

## AI Tool Configuration

### Aider Configuration (.aider.conf.yml)
```yaml
# Prevent modification of protected files
read-only-files:
  - protected_working_code/*
  - PROTECTED_*

# Auto-commit with descriptive messages
auto-commits: true
commit-prefix: "[AIDER]"

# Require confirmation for critical files
confirm-edit:
  - backend_fixed.py
  - simple_working_dashboard.html
```

### Cursor IDE Rules (.cursor/rules)
```
DO NOT MODIFY:
- Files in protected_working_code/
- Files starting with PROTECTED_
- backend_fixed.py without verification
- simple_working_dashboard.html without testing

ALWAYS:
- Create new versions for testing
- Verify All Ordinaries shows -0.14%
- Use real Yahoo Finance data only
- Test on different ports first
```

## Verification Commands

### Quick Health Check
```bash
# Check if backend is running correctly
curl -s http://localhost:8002/api/indices | python3 -c "
import json, sys
data = json.load(sys.stdin)
aord = data['indices']['^AORD']
print(f\"All Ords: {aord['price']:.2f} ({aord['changePercent']:.2f}%)\")
assert abs(aord['changePercent'] - (-0.14)) < 0.01, 'Percentage mismatch!'
print('✓ Data verification passed')
"
```

### File Integrity Check
```bash
# Verify no synthetic data in code
grep -r "Math.random" *.py *.html *.js 2>/dev/null && echo "WARNING: Synthetic data found!" || echo "✓ No synthetic data"

# Check for history data usage
grep -n "hist\['Close'\].iloc\[-2\]" backend_fixed.py && echo "✓ Using history data" || echo "WARNING: Not using history data!"
```

## Recovery Checklist

When regression occurs:

1. [ ] Stop all modified services
2. [ ] Restore from protected_working_code/
3. [ ] Verify checksums match original
4. [ ] Restart services on original ports
5. [ ] Run verification commands
6. [ ] Document what caused regression
7. [ ] Update PROJECT_STATE.md with incident

## Critical Success Metrics

- All Ordinaries: Must show ~9,135 points, -0.14% change
- Data Source: Must be "Yahoo Finance (History-based)"
- No synthetic data: grep for Math.random must return empty
- Previous close: Must use hist['Close'].iloc[-2]

## Monitoring

Create a monitoring script that runs every 5 minutes:
```bash
#!/bin/bash
# monitor.sh - Continuous verification

while true; do
    echo "$(date): Checking data integrity..."
    
    # Check backend health
    curl -s http://localhost:8002/ | grep -q "Fixed Market Data API" || echo "WARNING: Backend issue!"
    
    # Verify data accuracy
    response=$(curl -s http://localhost:8002/api/indices)
    echo $response | grep -q "History-based" || echo "WARNING: Not using history data!"
    
    sleep 300
done
```