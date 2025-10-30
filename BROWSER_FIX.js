// COPY AND PASTE THIS INTO YOUR BROWSER CONSOLE
// This will replace the broken function with a working one

console.log('Installing ML Predictions Fix...');

// Create a completely new working function
window.MLPredict = async function(symbol) {
    if (!symbol) {
        symbol = document.getElementById('symbol')?.value || 'AAPL';
    }
    
    console.log(`Fetching ML predictions for ${symbol}...`);
    
    // Use XMLHttpRequest instead of fetch to avoid any issues
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', `/api/predict/${symbol}`, true);
        
        xhr.onload = function() {
            console.log('Response status:', xhr.status);
            
            if (xhr.status === 200) {
                try {
                    const data = JSON.parse(xhr.responseText);
                    console.log('ML Data received:', data);
                    
                    if (data.available && data.predictions) {
                        // Display in alert for immediate feedback
                        let msg = `ML Predictions for ${symbol}:\n\n`;
                        msg += `Current Price: $${data.current_price.toFixed(2)}\n\n`;
                        
                        data.predictions.forEach(p => {
                            msg += `${p.days} Day: $${p.price.toFixed(2)} (${p.return >= 0 ? '+' : ''}${p.return.toFixed(2)}%)\n`;
                        });
                        
                        alert(msg);
                        
                        // Also update the page if elements exist
                        const contentDiv = document.getElementById('predictions-content');
                        if (contentDiv) {
                            let html = '<h3>ML Predictions Working!</h3>';
                            html += `<p>Current Price: $${data.current_price.toFixed(2)}</p>`;
                            html += '<ul>';
                            data.predictions.forEach(p => {
                                html += `<li>${p.days} Day: $${p.price.toFixed(2)} (${p.return >= 0 ? '+' : ''}${p.return.toFixed(2)}%)</li>`;
                            });
                            html += '</ul>';
                            contentDiv.innerHTML = html;
                        }
                        
                        resolve(data);
                    } else {
                        alert('ML not available: ' + (data.error || 'Unknown error'));
                        reject(new Error(data.error));
                    }
                } catch (e) {
                    console.error('Parse error:', e);
                    alert('Failed to parse response');
                    reject(e);
                }
            } else {
                console.error('Server error:', xhr.status, xhr.responseText);
                alert(`Server error ${xhr.status}. Check console for details.`);
                console.log('Full error response:', xhr.responseText);
                reject(new Error(`Server error: ${xhr.status}`));
            }
        };
        
        xhr.onerror = function() {
            console.error('Network error');
            alert('Network error - check console');
            reject(new Error('Network error'));
        };
        
        xhr.send();
    });
};

// Also create a button to test it
const testBtn = document.createElement('button');
testBtn.textContent = 'Test ML (Fixed)';
testBtn.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 10000; padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;';
testBtn.onclick = () => MLPredict();
document.body.appendChild(testBtn);

console.log('✅ Fix installed!');
console.log('You can now:');
console.log('1. Click the green "Test ML (Fixed)" button at bottom-right');
console.log('2. Or run: MLPredict("AAPL") in console');
console.log('3. Or run: MLPredict() to use current symbol in input');