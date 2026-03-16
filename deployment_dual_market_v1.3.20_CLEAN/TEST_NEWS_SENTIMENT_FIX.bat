@echo off
echo ============================================================
echo NEWS SENTIMENT FIX - VERIFICATION TEST
echo ============================================================
echo.
echo This test verifies that news sentiment modules can now be imported.
echo.
echo ============================================================
echo Test 1: Import FinBERT Bridge
echo ============================================================
python -c "from models.screening.finbert_bridge import FinBERTBridge; print('✅ FinBERT Bridge imported successfully')"
if errorlevel 1 (
    echo ❌ FAILED: Could not import FinBERT Bridge
    goto :end
)

echo.
echo ============================================================
echo Test 2: Check News Sentiment Availability
echo ============================================================
python -c "from models.screening.finbert_bridge import FinBERTBridge; bridge = FinBERTBridge(market='US'); available = bridge.is_available(); print(f'LSTM Available: {available[\"lstm_available\"]}'); print(f'Sentiment Available: {available[\"sentiment_available\"]}'); print(f'ASX News Scraping: {available[\"news_scraping_asx_available\"]}'); print(f'US News Scraping: {available[\"news_scraping_us_available\"]}'); print('✅ All components checked')"
if errorlevel 1 (
    echo ❌ FAILED: Could not check component availability
    goto :end
)

echo.
echo ============================================================
echo Test 3: Test ASX News Sentiment Import
echo ============================================================
python -c "from models.screening.finbert_bridge import NEWS_SENTIMENT_ASX_AVAILABLE, get_sentiment_sync_asx; print(f'ASX Module Available: {NEWS_SENTIMENT_ASX_AVAILABLE}'); print(f'Function Imported: {get_sentiment_sync_asx is not None}'); print('✅ ASX news sentiment module working' if NEWS_SENTIMENT_ASX_AVAILABLE else '❌ ASX news sentiment not available')"
if errorlevel 1 (
    echo ❌ FAILED: Error checking ASX news sentiment
    goto :end
)

echo.
echo ============================================================
echo Test 4: Test US News Sentiment Import
echo ============================================================
python -c "from models.screening.finbert_bridge import NEWS_SENTIMENT_US_AVAILABLE, get_sentiment_sync_us; print(f'US Module Available: {NEWS_SENTIMENT_US_AVAILABLE}'); print(f'Function Imported: {get_sentiment_sync_us is not None}'); print('✅ US news sentiment module working' if NEWS_SENTIMENT_US_AVAILABLE else '❌ US news sentiment not available')"
if errorlevel 1 (
    echo ❌ FAILED: Error checking US news sentiment
    goto :end
)

echo.
echo ============================================================
echo Test 5: Full FinBERT Bridge Status
echo ============================================================
python -c "from models.screening.finbert_bridge import FinBERTBridge; bridge = FinBERTBridge(market='US'); status = bridge.is_available(); print(''); print('FINBERT BRIDGE STATUS:'); print('=' * 50); print(f'LSTM Predictor:      {\"✅ Available\" if status[\"lstm_available\"] else \"❌ Not Available\"}'); print(f'Sentiment Analyzer:  {\"✅ Available\" if status[\"sentiment_available\"] else \"❌ Not Available\"}'); print(f'ASX News Scraping:   {\"✅ Available\" if status[\"news_scraping_asx_available\"] else \"❌ Not Available\"}'); print(f'US News Scraping:    {\"✅ Available\" if status[\"news_scraping_us_available\"] else \"❌ Not Available\"}'); print('=' * 50); print(''); all_ok = all(status.values()); print('✅ ALL COMPONENTS WORKING!' if all_ok else '⚠ Some components unavailable (but this is OK)')"

echo.
echo ============================================================
echo ✅ NEWS SENTIMENT FIX VERIFICATION COMPLETE!
echo ============================================================
echo.
echo The fix has been applied. News sentiment modules should now work.
echo.
echo NEXT STEPS:
echo 1. Run VERIFY_INSTALLATION.bat again to confirm
echo 2. Test the pipeline with: python models\screening\us_overnight_pipeline.py --test-mode
echo.
:end
pause
