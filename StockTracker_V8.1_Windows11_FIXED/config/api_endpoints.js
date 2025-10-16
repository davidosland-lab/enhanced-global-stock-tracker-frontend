// API Endpoint Configuration
// Update these URLs based on your deployment environment

const API_CONFIG = {
    // For local Windows deployment (after running START_TRACKER.bat)
    local: {
        mainAPI: 'http://localhost:8002',
        mlAPI: 'http://localhost:8003',
        sentimentAPI: 'http://localhost:8004'
    },
    
    // For sandbox/cloud deployment
    sandbox: {
        mainAPI: 'https://8002-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev',
        mlAPI: 'https://8003-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev',
        sentimentAPI: 'https://8004-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev'
    },
    
    // Auto-detect environment
    getEndpoints: function() {
        // If accessing from sandbox URL, use sandbox endpoints
        if (window.location.hostname.includes('e2b.dev')) {
            return this.sandbox;
        }
        // Otherwise use local endpoints
        return this.local;
    }
};

// Export for use in other scripts
const API_ENDPOINTS = API_CONFIG.getEndpoints();