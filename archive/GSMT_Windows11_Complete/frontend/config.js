// Local configuration for GSMT Windows 11 deployment
// All modules point to local backend server

window.CONFIG = {
    // Backend API URL - Local deployment
    BACKEND_URL: 'http://localhost:8000',
    
    // Refresh interval in milliseconds (5 minutes)
    REFRESH_INTERVAL: 300000,
    
    // Enable debug logging
    DEBUG: false,
    
    // Frontend URL (local)
    FRONTEND_URL: 'file://',
    
    // Environment
    ENVIRONMENT: 'local',
    
    // Version
    VERSION: '8.1.3'
};

// Additional configuration for backward compatibility
window.BACKEND_URL = window.CONFIG.BACKEND_URL;

// Log configuration loaded
console.log('GSMT Local Config loaded at:', new Date().toISOString());
console.log('Backend URL:', window.CONFIG.BACKEND_URL);
console.log('Environment:', window.CONFIG.ENVIRONMENT);