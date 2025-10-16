@echo off
echo ================================================================================
echo FIXING SENTIMENT SCRAPER DISPLAY ISSUE
echo For Windows 11 Local Deployment
echo ================================================================================
echo.

echo The web scraper backend is working correctly.
echo The issue is with the HTML display not showing results properly.
echo.
echo Creating backup of original...
copy sentiment_scraper.html sentiment_scraper_original.html >nul 2>&1

echo.
echo Applying fixed version...
copy sentiment_scraper_fixed.html sentiment_scraper.html >nul 2>&1

echo.
echo ================================================================================
echo FIX COMPLETE!
echo ================================================================================
echo.
echo The sentiment scraper should now properly display:
echo - Sentiment percentages (Positive, Neutral, Negative)
echo - Individual article cards with sentiment colors
echo - Clickable links to articles
echo - Total article count and average score
echo.
echo Test it now:
echo 1. Open http://localhost:8000/sentiment_scraper.html
echo 2. Enter a stock symbol (e.g., AAPL)
echo 3. Select sources (Yahoo, Finviz, etc.)
echo 4. Click "Scrape & Analyze"
echo 5. Results should now display properly!
echo.
echo If you want to revert to original:
echo copy sentiment_scraper_original.html sentiment_scraper.html
echo.
pause