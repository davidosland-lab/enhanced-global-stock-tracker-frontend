// BROWSER CONSOLE FIX FOR BROKEN MODULE LINKS
// Instructions:
// 1. Open http://localhost:8000 in your browser
// 2. Press F12 to open Developer Tools
// 3. Click on "Console" tab
// 4. Copy and paste this entire code
// 5. Press Enter

console.log("🔧 Applying module link fixes...");

// Fix the modules object
window.modules = {
    'cba': 'modules/cba_enhanced.html',
    'indices': 'modules/indices_tracker.html',
    'tracker': 'modules/stock_tracker.html',
    'predictor': 'modules/prediction_centre_phase4.html',
    'documents': 'modules/document_uploader.html',
    'historical': 'modules/historical_data_manager_fixed.html',
    'performance': 'modules/prediction_performance_dashboard.html',
    'mltraining': 'modules/ml_training_centre.html',
    'technical': 'modules/technical_analysis_fixed.html'
};

// Override the loadModule function
window.loadModule = async function(module) {
    console.log(`Loading module: ${module}`);
    
    if (modules[module]) {
        // Hide main container
        document.querySelector('.container').style.display = 'none';
        
        // Show module in iframe
        const container = document.getElementById('moduleContainer');
        const frame = document.getElementById('moduleFrame');
        
        if (container && frame) {
            container.style.display = 'block';
            frame.src = modules[module];
            console.log(`✅ Loaded: ${modules[module]}`);
        } else {
            // If iframe doesn't exist, open in new tab
            console.log(`📂 Opening in new tab: ${modules[module]}`);
            window.open(modules[module], '_blank');
        }
    } else {
        console.error(`❌ Module not found: ${module}`);
    }
};

// Add direct click handlers to fix broken cards
document.addEventListener('DOMContentLoaded', function() {
    // Find all module cards
    const cards = document.querySelectorAll('.module-card');
    
    cards.forEach(card => {
        const title = card.querySelector('h2')?.textContent || '';
        
        if (title.includes('Phase 4 Predictor')) {
            card.onclick = () => loadModule('predictor');
            console.log("✅ Fixed: Phase 4 Predictor link");
        }
        else if (title.includes('Document Analyzer')) {
            card.onclick = () => loadModule('documents');
            console.log("✅ Fixed: Document Analyzer link");
        }
        else if (title.includes('Data Manager')) {
            card.onclick = () => loadModule('historical');
            console.log("✅ Fixed: Historical Data Manager link");
        }
    });
});

// If page is already loaded, fix it now
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    const cards = document.querySelectorAll('.module-card');
    
    cards.forEach(card => {
        const title = card.querySelector('h2')?.textContent || '';
        
        if (title.includes('Phase 4 Predictor')) {
            card.onclick = () => loadModule('predictor');
            console.log("✅ Fixed: Phase 4 Predictor link");
        }
        else if (title.includes('Document Analyzer')) {
            card.onclick = () => loadModule('documents');
            console.log("✅ Fixed: Document Analyzer link");
        }
        else if (title.includes('Data Manager')) {
            card.onclick = () => loadModule('historical');
            console.log("✅ Fixed: Historical Data Manager link");
        }
    });
}

// Test function to verify modules exist
window.testModules = function() {
    console.log("\n📋 Module Path Check:");
    console.log("====================");
    
    for (const [key, path] of Object.entries(modules)) {
        // Try to check if file exists
        fetch(path, { method: 'HEAD' })
            .then(response => {
                if (response.ok) {
                    console.log(`✅ ${key}: ${path} - EXISTS`);
                } else {
                    console.log(`❌ ${key}: ${path} - NOT FOUND (${response.status})`);
                }
            })
            .catch(error => {
                console.log(`❌ ${key}: ${path} - ERROR`);
            });
    }
    
    console.log("\n💡 If modules show NOT FOUND, the files may not exist in your installation.");
    console.log("Use the direct links page instead: http://localhost:8000/FIX_BROKEN_LINKS.html");
};

console.log("\n✅ Module fixes applied!");
console.log("📝 Instructions:");
console.log("1. Click on 'Phase 4 Predictor' - should now work");
console.log("2. Click on 'Document Analyzer' - should now work");
console.log("3. If still not working, type: testModules() and press Enter");
console.log("4. Or visit: http://localhost:8000/FIX_BROKEN_LINKS.html for direct links");

// Auto-test after 1 second
setTimeout(() => {
    console.log("\n🔍 Auto-testing modules...");
    testModules();
}, 1000);