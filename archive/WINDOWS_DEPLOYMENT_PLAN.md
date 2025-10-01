# Windows 11 Deployment Plan for GSMT

## Current Development Environment
- **Platform**: Linux Sandbox
- **Backend**: Python/FastAPI on port 8002
- **Frontend**: Pure HTML/JS (no build process needed)
- **Target**: Windows 11 local deployment

## Development Phases with Windows Testing

### Phase 1: Basic Modules (TODAY)
**Status**: In Progress
- [x] Module 1: Global Indices Tracker
- [ ] Module 2: Single Stock Tracker
- [ ] Module 3: CBA Analysis
- [ ] Module 4: Technical Analysis
- [ ] Module 5: ML Predictions
- [ ] Module 6: Document Center

**Windows Test 1**: After all basic modules complete
- Package as `GSMT_Basic_Windows.zip`
- Test startup scripts
- Verify Python dependencies

### Phase 2: Enhanced Features
**Timeline**: After Windows Test 1 passes
- [ ] Add Chart.js graphs
- [ ] Add candlestick charts
- [ ] Add technical indicators
- [ ] Add export functionality

**Windows Test 2**: After enhancements
- Test JavaScript libraries compatibility
- Verify performance on Windows
- Check memory usage

### Phase 3: Production Ready
**Timeline**: After Windows Test 2 passes
- [ ] Add Windows installer (.msi)
- [ ] Create auto-update mechanism
- [ ] Add Windows service option
- [ ] Create desktop shortcuts

## Windows Deployment Package Structure
```
GSMT_Windows/
├── backend/
│   ├── backend_fixed.py         # Protected working backend
│   ├── requirements.txt         # Python dependencies
│   └── config.yml               # Windows-specific config
├── frontend/
│   ├── index.html              # Main dashboard
│   └── modules/                # All 6 modules
│       ├── global_indices_tracker.html
│       ├── single_stock_tracker.html
│       ├── cba_analysis.html
│       ├── technical_analysis.html
│       ├── ml_predictions.html
│       └── document_center.html
├── START_GSMT.bat              # One-click start script
├── STOP_GSMT.bat               # Stop all services
├── INSTALL_DEPENDENCIES.bat    # First-time setup
└── README_WINDOWS.md           # Windows-specific instructions
```

## Windows-Specific Code Considerations

### 1. File Paths
```python
# Use os.path for Windows compatibility
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.yml')
```

### 2. Backend URLs in Frontend
```javascript
// Detect if running locally on Windows
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8002' 
    : window.location.protocol + '//' + window.location.hostname.replace('8080', '8002');
```

### 3. Batch Scripts
```batch
@echo off
REM START_GSMT.bat
echo Starting Global Stock Market Tracker...
cd /d %~dp0backend
start "GSMT Backend" python backend_fixed.py
timeout /t 3
cd /d %~dp0frontend
start http://localhost:8002/
echo GSMT is running. Use STOP_GSMT.bat to stop all services.
```

## Testing Requirements for Windows 11

### Functional Tests
- [ ] Backend starts without errors
- [ ] All modules load correctly
- [ ] Real-time data updates work
- [ ] Auto-refresh functions properly
- [ ] All links navigate correctly

### Compatibility Tests
- [ ] Python 3.8+ compatibility
- [ ] Works with Windows Defender enabled
- [ ] No firewall blocking issues
- [ ] Runs without admin rights
- [ ] Compatible with Edge/Chrome/Firefox

### Performance Tests
- [ ] CPU usage < 5% when idle
- [ ] Memory usage < 200MB
- [ ] Page load time < 2 seconds
- [ ] API response time < 500ms

## Current Status
- **Protected Backend**: `backend_fixed.py` working with -0.14% All Ordinaries
- **Basic Dashboard**: Working and connected
- **Module 1**: Global Indices Tracker complete
- **Modules 2-6**: In development (basic version)

## Next Steps
1. Complete basic modules 2-6
2. Create Windows package
3. Test on Windows 11
4. Fix any Windows-specific issues
5. Proceed to Phase 2 (enhancements)

## Risk Mitigation
- Keep features simple in Phase 1
- Test each module individually
- Maintain working backups
- Use vanilla JavaScript (no complex frameworks)
- Avoid platform-specific code