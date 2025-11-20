@echo off
REM Event Risk Guard - Pipeline Runner
REM Run the overnight screening pipeline with all phases

echo ================================================================================
echo EVENT RISK GUARD - OVERNIGHT SCREENING PIPELINE
echo ================================================================================
echo.
echo This will run the complete overnight screening pipeline:
echo   - Phase 1: SPI Futures Monitoring
echo   - Phase 2: Stock Data Collection (86 stocks)
echo   - Phase 3: FinBERT Sentiment Analysis
echo   - Phase 4: Technical and Event Scoring
echo   - Phase 4.5: LSTM Model Training
echo   - Phase 5: Report Generation
echo   - Phase 6-9: Web Server and Monitoring
echo.
echo Expected runtime: 70-110 minutes (first run)
echo                   40-60 minutes (subsequent runs)
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo Starting pipeline...
echo.

python run_pipeline.py

echo.
echo ================================================================================
echo PIPELINE COMPLETE
echo ================================================================================
echo.
echo Check the following directories for results:
echo   - models\         : Trained LSTM models (*.keras files)
echo   - reports\        : HTML opportunity reports
echo   - logs\screening\ : Detailed execution logs
echo.
echo To view results in the web UI:
echo   1. Run: python web_ui.py
echo   2. Open browser to: http://localhost:5000
echo.
pause
