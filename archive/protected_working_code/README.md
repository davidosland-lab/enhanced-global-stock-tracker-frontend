# PROTECTED WORKING CODE - DO NOT MODIFY

## Critical Files - VERIFIED WORKING

### 1. PROTECTED_backend_fixed_v1.py
- **Status**: WORKING - Verified correct percentage calculations
- **Port**: 8002
- **Key Feature**: Uses history data for accurate previous close
- **Verification**: All Ordinaries shows 9,135 points, -0.14% change (CORRECT)
- **Date Protected**: 2025-09-30

### 2. PROTECTED_dashboard_v1.html
- **Status**: WORKING - Shows real data from fixed backend
- **Connected to**: Port 8002 (fixed backend)
- **Key Feature**: NO synthetic data, pure Yahoo Finance
- **Date Protected**: 2025-09-30

## Protection Rules

1. **NEVER MODIFY THESE FILES DIRECTLY**
2. **ALWAYS CREATE NEW VERSIONS** if changes needed
3. **TEST NEW VERSIONS SEPARATELY** before replacing
4. **KEEP THESE AS ROLLBACK POINTS**

## How to Use Protected Files

### To restore backend:
```bash
cp protected_working_code/PROTECTED_backend_fixed_v1.py backend_fixed.py
python backend_fixed.py
```

### To restore dashboard:
```bash
cp protected_working_code/PROTECTED_dashboard_v1.html simple_working_dashboard.html
```

## Version History

- **v1**: Initial protected version with correct percentage calculations
  - All Ordinaries: -0.14% (VERIFIED CORRECT)
  - Using history data for previous close
  - No synthetic data generation