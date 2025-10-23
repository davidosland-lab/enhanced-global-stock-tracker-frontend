// Fix for Phase 4 Prediction Centre
// Add this to your prediction_centre_phase4.html or run in console

async function generatePrediction() {
    const symbol = document.getElementById('stockSymbol').value.trim() || 'CBA.AX';
    const modelType = document.getElementById('modelType').value || 'ensemble';
    const timeframe = document.getElementById('timeframe').value || '5 Days';
    
    console.log('Generating prediction for:', symbol, modelType, timeframe);
    
    // Update UI to show loading
    const priceElements = document.querySelectorAll('.prediction-value');
    if (priceElements.length > 0) {
        priceElements[0].textContent = 'Loading...';
    }
    
    try {
        // Map timeframe to period
        const periodMap = {
            '5 Days': '5d',
            '1 Month': '1mo',
            '3 Months': '3mo',
            '6 Months': '6mo'
        };
        
        const period = periodMap[timeframe] || '1mo';
        
        // Call the correct endpoint
        const response = await fetch('http://localhost:8002/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                symbol: symbol,
                period: period,
                model_type: modelType.toLowerCase()
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Prediction response:', data);
        
        // Update current price
        const currentPriceElem = document.querySelector('.prediction-value');
        if (currentPriceElem) {
            currentPriceElem.textContent = `$${data.current_price.toFixed(2)}`;
        }
        
        // Update predicted price (using 5-day prediction)
        const predictedPriceElems = document.querySelectorAll('.prediction-value');
        if (predictedPriceElems.length > 1 && data.predictions && data.predictions.length > 0) {
            // Find the appropriate prediction based on timeframe
            let prediction;
            if (timeframe === '5 Days') {
                prediction = data.predictions[0]; // 1 day prediction
            } else if (timeframe === '1 Month') {
                prediction = data.predictions[2] || data.predictions[1]; // 1 month or 1 week
            } else {
                prediction = data.predictions[1]; // 1 week as default
            }
            
            if (prediction) {
                predictedPriceElems[1].textContent = `$${prediction.predicted_price.toFixed(2)}`;
                
                // Update confidence if exists
                const confidenceElem = document.querySelectorAll('.prediction-value')[2];
                if (confidenceElem) {
                    confidenceElem.textContent = `${(prediction.confidence * 100).toFixed(1)}%`;
                }
                
                // Update chart if exists
                if (window.updatePredictionChart) {
                    updatePredictionChart(data);
                }
            }
        }
        
        // Show success message
        console.log('✅ Prediction generated successfully');
        
    } catch (error) {
        console.error('Error generating prediction:', error);
        alert('Error generating prediction: ' + error.message);
        
        // Reset display on error
        const priceElements = document.querySelectorAll('.prediction-value');
        if (priceElements.length > 1) {
            priceElements[1].textContent = '$--';
        }
    }
}

// Also fix the backtest function
async function runBacktest() {
    const symbol = document.getElementById('stockSymbol').value.trim() || 'CBA.AX';
    
    console.log('Running backtest for:', symbol);
    
    try {
        const response = await fetch('http://localhost:8002/api/phase4/backtest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                symbol: symbol,
                start_date: '2024-01-01',
                end_date: '2024-10-01',
                initial_capital: 10000,
                strategy: 'momentum'
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Backtest results:', data);
        
        // Display results
        alert(`Backtest Results:\n
Symbol: ${data.symbol}
Total Return: ${data.performance.total_return}%
Strategy Return: ${data.performance.strategy_return}%
Number of Trades: ${data.performance.number_of_trades}
Win Rate: ${data.performance.win_rate}%`);
        
    } catch (error) {
        console.error('Error running backtest:', error);
        alert('Error running backtest: ' + error.message);
    }
}

// Auto-fix on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('Prediction Centre fix loaded');
        // Replace the existing generatePrediction function
        window.generatePrediction = generatePrediction;
        window.runBacktest = runBacktest;
    });
} else {
    console.log('Prediction Centre fix loaded (immediate)');
    window.generatePrediction = generatePrediction;
    window.runBacktest = runBacktest;
}

console.log('✅ Prediction Centre fixes applied. Try clicking "Generate Prediction" now.');