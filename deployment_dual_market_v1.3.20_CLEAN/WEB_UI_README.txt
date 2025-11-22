================================================================================
EVENT RISK GUARD - DUAL MARKET WEB UI
================================================================================

OVERVIEW
--------
The Web UI provides a browser-based dashboard for monitoring and managing 
both ASX and US market screening pipelines.

FEATURES
--------
✓ Real-time system status for both markets
✓ View latest screening reports (ASX + US)
✓ Monitor pipeline logs for both markets
✓ Check market regime status (crash risk, volatility)
✓ Browse trained LSTM models
✓ View sector configurations
✓ Email notification status

QUICK START
-----------

1. Windows:
   Double-click: START_WEB_UI.bat

2. Linux/Mac:
   ./START_WEB_UI.sh

3. Access Dashboard:
   Open browser: http://localhost:5000

REQUIREMENTS
------------
✓ Python 3.8+
✓ Flask and flask-cors (installed during INSTALL)
✓ Port 5000 available

WHAT YOU'LL SEE
---------------

📊 DASHBOARD SECTIONS:

1. Status Cards (Top)
   - System Status: Overall health
   - Email Notifications: Enabled/Disabled
   - LSTM Training: Active/Inactive
   - SPI Monitoring: Active/Inactive

2. Market Regime Analysis
   - Current regime state (Low/Medium/High volatility)
   - Crash risk score and classification
   - Daily and annual volatility metrics
   - Regime probabilities (3-state HMM)

3. Recent Reports
   - Latest HTML morning reports
   - Separate sections for ASX and US markets
   - Clickable to view full reports
   - Shows generation timestamp

4. Pipeline Logs
   - Real-time log viewing
   - Separate tabs for ASX and US markets
   - Last 200 lines displayed
   - Auto-refresh available

5. Trained Models
   - List of all LSTM models
   - Model metadata and file sizes
   - Last trained timestamps

API ENDPOINTS
-------------

Dashboard:
  GET  /                        - Main dashboard page

Status:
  GET  /api/status              - System status (both markets)
  GET  /api/markets             - Available markets info

Reports:
  GET  /api/reports             - All reports
  GET  /api/reports?market=asx  - ASX reports only
  GET  /api/reports?market=us   - US reports only
  GET  /api/reports/<filename>  - Specific report

Logs:
  GET  /api/logs                - All logs
  GET  /api/logs?market=asx     - ASX logs only
  GET  /api/logs?market=us      - US logs only

Configuration:
  GET  /api/config              - Current configuration
  POST /api/config              - Update configuration
  GET  /api/sectors             - All sectors
  GET  /api/sectors?market=asx  - ASX sectors only
  GET  /api/sectors?market=us   - US sectors only

Market Analysis:
  GET  /api/regime              - Market regime data

Models:
  GET  /api/models              - List trained LSTM models

DASHBOARD FEATURES
------------------

🔄 REFRESH BUTTON
  - Updates all dashboard sections
  - Fetches latest data from both markets
  - Recommended: Refresh after pipeline runs

⚙️ SETTINGS BUTTON
  - View/edit configuration
  - Enable/disable features
  - Update email settings

DIRECTORY STRUCTURE
-------------------

The Web UI monitors these locations:

ASX Market:
  reports/html/              - HTML reports
  reports/morning_reports/   - Morning reports
  reports/pipeline_state/    - Pipeline state files
  logs/screening/            - Pipeline logs

US Market:
  reports/us/                - US reports
  reports/html/us/           - US HTML reports
  reports/morning_reports/us/- US morning reports
  reports/pipeline_state/us/ - US pipeline state
  logs/screening/us/         - US pipeline logs

TROUBLESHOOTING
---------------

Problem: Web UI won't start
Solution:
  1. Check Python installed: python --version
  2. Install requirements: pip install -r requirements.txt
  3. Check port 5000 not in use: netstat -an | findstr 5000

Problem: "No reports found"
Solution:
  1. Run pipeline first: RUN_QUICK_TEST.bat
  2. Check reports/ directory has files
  3. Wait 3-5 minutes for pipeline to complete

Problem: "Scanner not available" in status
Solution:
  1. Verify installation: VERIFY.py
  2. Check models/screening/ has all files
  3. Run INSTALL.bat again if needed

Problem: Logs not showing
Solution:
  1. Run pipeline to generate logs
  2. Check logs/screening/ directory
  3. For US logs, check logs/screening/us/

Problem: Market regime not displaying
Solution:
  1. Run full pipeline (not quick test)
  2. Pipeline must complete event risk analysis
  3. Check reports/pipeline_state/ has JSON files

CONFIGURATION
-------------

The Web UI reads configuration from:
  models/config/screening_config.json

You can edit settings through the web interface or directly in the file.

Key settings:
  - email_notifications: Enable/disable emails
  - lstm_training: Auto-train models
  - spi_monitoring: Track market indices

ACCESSING FROM NETWORK
-----------------------

By default, Web UI binds to 0.0.0.0:5000, making it accessible from:
  - Localhost: http://localhost:5000
  - Local IP: http://192.168.x.x:5000 (check your IP)

Security Note: Only use on trusted networks. No authentication is enabled.

STOPPING THE WEB UI
-------------------

Press: Ctrl+C in the terminal window

The server will shutdown gracefully.

INTEGRATION
-----------

The Web UI integrates with:
  ✓ run_screening.py - Main pipeline launcher
  ✓ RUN_QUICK_TEST.bat - Quick test scripts
  ✓ RUN_US_MARKET.bat - US market scripts
  ✓ RUN_BOTH_MARKETS.bat - Dual market scripts
  ✓ All report generators
  ✓ All log files

BEST PRACTICES
--------------

1. Start Web UI before running pipelines
   - Keep dashboard open during runs
   - Monitor logs in real-time

2. Refresh after pipeline completion
   - Click 🔄 Refresh button
   - Check both ASX and US sections

3. Review reports regularly
   - Check morning reports daily
   - Compare ASX vs US opportunities

4. Monitor market regime
   - High crash risk = Reduce exposure
   - Low volatility = More opportunities

5. Track model performance
   - Review LSTM models section
   - Retrain if accuracy drops

SUPPORT
-------

For issues with Web UI:
  1. Check TROUBLESHOOTING_WEB_UI.md
  2. Review Flask logs in terminal
  3. Verify requirements.txt installed
  4. Check firewall allows port 5000

================================================================================
