// Configuration for the frontend application
window.CONFIG = {
    // Backend API URL - Railway production deployment
    // Note: If Railway backend fails, use local backend URL
    BACKEND_URL: 'https://enhanced-global-stock-tracker-frontend-production.up.railway.app',
    
    // Alternative backend for testing (when Railway is down)
    // LOCAL_BACKEND_URL: 'https://8000-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev',
    
    // Refresh interval in milliseconds (5 minutes)
    REFRESH_INTERVAL: 300000,
    
    // Enable debug logging
    DEBUG: true,  // Set to true to see error details
    
    // Frontend URL
    FRONTEND_URL: 'https://egsmtver110.netlify.app'
};