// ================================================
// FORCE FIX - PASTE THIS IN PHASE 4 CONSOLE
// ================================================

console.log('🔨 APPLYING FORCE FIX...');

// Store original functions if they exist
const originalFunctions = {
    generatePrediction: window.generatePrediction,
    runRealBacktest: window.runRealBacktest,
    trainModels: window.trainModels
};

// 1. COMPLETELY OVERRIDE PREDICTION
window.generatePrediction = async function() {
    console.log('🎯 FORCE FIX: Generating prediction...');
    
    const symbol = (document.getElementById('stockSymbol') || 
                   document.querySelector('input[type="text"]'))?.value || 'CBA.AX';
    
    // Find ALL possible display elements
    const displays = [
        ...document.querySelectorAll('.prediction-value'),
        ...document.querySelectorAll('.stat-value'),
        ...document.querySelectorAll('[class*="price"]'),
        ...document.querySelectorAll('div:not([class])'),
    ].filter(el => el.textContent.includes('$'));
    
    console.log('Found', displays.length, 'display elements');
    
    try {
        const response = await fetch('http://localhost:8002/api/predict', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                symbol: symbol,
                period: '1mo',
                model_type: 'simple'
            })
        });
        
        const data = await response.json();
        console.log('✅ Prediction data:', data);
        
        // Force update displays
        let updated = 0;
        displays.forEach((el, i) => {
            if (el.textContent === '$--' || el.textContent.includes('--')) {
                if (updated === 0 && data.current_price) {
                    el.textContent = '$' + data.current_price.toFixed(2);
                    updated++;
                } else if (updated === 1 && data.predictions?.[0]) {
                    el.textContent = '$' + data.predictions[0].predicted_price.toFixed(2);
                    updated++;
                } else if (updated === 2 && data.predictions?.[0]) {
                    el.textContent = (data.predictions[0].confidence * 100).toFixed(1) + '%';
                    updated++;
                }
            }
        });
        
        // Show alert with results
        if (data.predictions && data.predictions[0]) {
            alert(`✅ Prediction Generated!\n\nSymbol: ${symbol}\nCurrent: $${data.current_price.toFixed(2)}\nPredicted: $${data.predictions[0].predicted_price.toFixed(2)}\nChange: ${data.predictions[0].change_percent.toFixed(2)}%\nConfidence: ${(data.predictions[0].confidence * 100).toFixed(1)}%`);
        }
        
        return data;
        
    } catch (error) {
        console.error('❌ Prediction error:', error);
        alert('Error: ' + error.message);
    }
};

// 2. COMPLETELY OVERRIDE BACKTEST
window.runRealBacktest = window.runBacktest = async function() {
    console.log('📊 FORCE FIX: Running backtest...');
    
    const symbol = (document.getElementById('stockSymbol') || 
                   document.querySelector('input[type="text"]'))?.value || 'CBA.AX';
    
    try {
        // Show loading
        const btn = event?.target || document.querySelector('button:contains("Backtest")');
        if (btn) btn.textContent = 'Running...';
        
        const response = await fetch('http://localhost:8002/api/phase4/backtest', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                symbol: symbol,
                start_date: '2024-01-01',
                end_date: '2024-10-01',
                initial_capital: 10000,
                strategy: 'momentum'
            })
        });
        
        const data = await response.json();
        console.log('✅ Backtest data:', data);
        
        // Display results
        alert(`✅ Backtest Complete!\n\nSymbol: ${data.symbol}\nPeriod: ${data.start_date} to ${data.end_date}\n\nResults:\n• Total Return: ${data.performance.total_return.toFixed(2)}%\n• Strategy Return: ${data.performance.strategy_return.toFixed(2)}%\n• Win Rate: ${data.performance.win_rate.toFixed(2)}%\n• Number of Trades: ${data.performance.number_of_trades}`);
        
        // Reset button
        if (btn) btn.textContent = 'Run Backtest';
        
        return data;
        
    } catch (error) {
        console.error('❌ Backtest error:', error);
        alert('Backtest error: ' + error.message);
    }
};

// 3. OVERRIDE TRAIN (redirect to prediction)
window.trainModels = async function() {
    console.log('🎓 FORCE FIX: Training redirected to prediction...');
    alert('Training endpoint not available.\nGenerating prediction instead...');
    return await window.generatePrediction();
};

// 4. FORCE OVERRIDE ALL BUTTONS AND ONCLICK
const fixButtons = () => {
    // Fix all buttons
    document.querySelectorAll('button').forEach(btn => {
        const text = btn.textContent.toLowerCase();
        if (text.includes('predict')) {
            btn.onclick = (e) => { e.preventDefault(); window.generatePrediction(); };
            console.log('Fixed button:', btn.textContent);
        } else if (text.includes('backtest')) {
            btn.onclick = (e) => { e.preventDefault(); window.runBacktest(); };
            console.log('Fixed button:', btn.textContent);
        } else if (text.includes('train')) {
            btn.onclick = (e) => { e.preventDefault(); window.trainModels(); };
            console.log('Fixed button:', btn.textContent);
        }
    });
    
    // Fix all onclick attributes
    document.querySelectorAll('[onclick]').forEach(el => {
        const onclick = el.getAttribute('onclick');
        if (onclick.includes('generatePrediction')) {
            el.setAttribute('onclick', 'event.preventDefault(); window.generatePrediction();');
        } else if (onclick.includes('Backtest')) {
            el.setAttribute('onclick', 'event.preventDefault(); window.runBacktest();');
        } else if (onclick.includes('train')) {
            el.setAttribute('onclick', 'event.preventDefault(); window.trainModels();');
        }
    });
};

// Apply fixes immediately
fixButtons();

// Re-apply fixes after a delay (in case of dynamic content)
setTimeout(fixButtons, 1000);
setTimeout(fixButtons, 2000);

// Also intercept any new button creation
const observer = new MutationObserver(fixButtons);
observer.observe(document.body, { childList: true, subtree: true });

console.log('=' .repeat(50));
console.log('✅ FORCE FIX APPLIED SUCCESSFULLY!');
console.log('=' .repeat(50));
console.log('Available functions:');
console.log('  • window.generatePrediction() - Generate predictions');
console.log('  • window.runBacktest() - Run backtest analysis');
console.log('  • window.trainModels() - Training (redirects to prediction)');
console.log('=' .repeat(50));
console.log('Try clicking the buttons now!');

// Auto-test prediction
setTimeout(() => {
    console.log('🔄 Auto-testing prediction in 2 seconds...');
    window.generatePrediction();
}, 2000);