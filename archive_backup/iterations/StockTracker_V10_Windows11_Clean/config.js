// Configuration for Stock Tracker
// Update these URLs based on your deployment environment

// For local Windows deployment:
const LOCAL_CONFIG = {
    MAIN_API: 'http://localhost:8000',
    HISTORICAL_API: 'http://localhost:8001',
    ML_API: 'http://localhost:8002',
    FINBERT_API: 'http://localhost:8003',
    BACKTESTING_API: 'http://localhost:8005',
    WEBSCRAPER_API: 'http://localhost:8006'
};

// For sandbox/cloud deployment:
const SANDBOX_CONFIG = {
    MAIN_API: 'https://8000-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev',
    HISTORICAL_API: 'https://8001-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev',
    ML_API: 'https://8002-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev',
    FINBERT_API: 'https://8003-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev',
    BACKTESTING_API: 'https://8005-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev',
    WEBSCRAPER_API: 'https://8006-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev'
};

// Auto-detect environment
const isSandbox = window.location.hostname.includes('e2b.dev') || 
                  window.location.hostname.includes('sandbox') ||
                  !window.location.hostname.includes('localhost');

// Use appropriate configuration
const API_CONFIG = isSandbox ? SANDBOX_CONFIG : LOCAL_CONFIG;

// Export for use in HTML files
window.API_CONFIG = API_CONFIG;