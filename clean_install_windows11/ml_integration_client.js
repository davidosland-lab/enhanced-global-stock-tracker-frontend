/**
 * ML Integration Client Library
 * Optional library for modules to integrate with ML learning
 * Does NOT break existing functionality if bridge is unavailable
 */

class MLIntegrationClient {
    constructor(moduleName, options = {}) {
        this.moduleName = moduleName;
        this.bridgeUrl = options.bridgeUrl || 'http://localhost:8004';
        this.enabled = options.enabled !== false;
        this.fallbackMode = false;
        this.cache = new Map();
        this.cacheTimeout = options.cacheTimeout || 300000; // 5 minutes
        
        // Check bridge availability on init
        this.checkBridgeStatus();
    }
    
    /**
     * Check if bridge is available
     */
    async checkBridgeStatus() {
        if (!this.enabled) return false;
        
        try {
            const response = await fetch(`${this.bridgeUrl}/api/bridge/health`, {
                method: 'GET',
                mode: 'cors',
                signal: AbortSignal.timeout(2000)
            });
            
            if (response.ok) {
                this.fallbackMode = false;
                console.log('ML Integration Bridge connected');
                return true;
            }
        } catch (error) {
            console.log('ML Integration Bridge not available - using fallback mode');
        }
        
        this.fallbackMode = true;
        return false;
    }
    
    /**
     * Send document sentiment to ML (Document Analyzer)
     */
    async sendDocumentSentiment(data) {
        if (!this.enabled || this.fallbackMode) {
            return this.getFallbackResponse('document_sentiment', data);
        }
        
        try {
            const response = await fetch(`${this.bridgeUrl}/api/bridge/document-sentiment`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source: this.moduleName,
                    symbol: data.symbol,
                    sentiment_score: data.sentimentScore,
                    confidence: data.confidence || 0.7,
                    key_phrases: data.keyPhrases || [],
                    document_type: data.documentType || 'text',
                    analysis_text: data.text || ''
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                this.cacheResult('sentiment', data.symbol, result);
                return result;
            }
        } catch (error) {
            console.warn('Failed to send sentiment to ML:', error.message);
        }
        
        return this.getFallbackResponse('document_sentiment', data);
    }
    
    /**
     * Send historical pattern to ML (Historical Data Analysis)
     */
    async sendHistoricalPattern(data) {
        if (!this.enabled || this.fallbackMode) {
            return this.getFallbackResponse('historical_pattern', data);
        }
        
        try {
            const response = await fetch(`${this.bridgeUrl}/api/bridge/historical-pattern`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source: this.moduleName,
                    symbol: data.symbol,
                    pattern_type: data.patternType,
                    pattern_data: data.patternData || {},
                    time_period: data.timePeriod || '1Y',
                    confidence: data.confidence || 0.6
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                this.cacheResult('pattern', data.symbol, result);
                return result;
            }
        } catch (error) {
            console.warn('Failed to send pattern to ML:', error.message);
        }
        
        return this.getFallbackResponse('historical_pattern', data);
    }
    
    /**
     * Send market movement to ML (Market Movers)
     */
    async sendMarketMovement(data) {
        if (!this.enabled || this.fallbackMode) {
            return this.getFallbackResponse('market_movement', data);
        }
        
        try {
            const response = await fetch(`${this.bridgeUrl}/api/bridge/market-movement`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source: this.moduleName,
                    symbol: data.symbol,
                    movement_type: data.changePercent > 0 ? 'gainer' : 'loser',
                    change_percent: data.changePercent,
                    volume_spike: data.volumeSpike || 1.0,
                    sector: data.sector
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                this.cacheResult('movement', data.symbol, result);
                return result;
            }
        } catch (error) {
            console.warn('Failed to send market movement to ML:', error.message);
        }
        
        return this.getFallbackResponse('market_movement', data);
    }
    
    /**
     * Send technical indicators to ML (Technical Analysis)
     */
    async sendTechnicalIndicators(data) {
        if (!this.enabled || this.fallbackMode) {
            return this.getFallbackResponse('technical_indicators', data);
        }
        
        try {
            const response = await fetch(`${this.bridgeUrl}/api/bridge/technical-indicators`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source: this.moduleName,
                    symbol: data.symbol,
                    indicators: data.indicators || {},
                    signals: data.signals || [],
                    trend: data.trend || 'neutral'
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                this.cacheResult('technical', data.symbol, result);
                return result;
            }
        } catch (error) {
            console.warn('Failed to send indicators to ML:', error.message);
        }
        
        return this.getFallbackResponse('technical_indicators', data);
    }
    
    /**
     * Get ML knowledge for a symbol
     */
    async getMLKnowledge(symbol) {
        // Check cache first
        const cached = this.getCachedResult('knowledge', symbol);
        if (cached) return cached;
        
        if (!this.enabled || this.fallbackMode) {
            return this.getFallbackKnowledge(symbol);
        }
        
        try {
            const response = await fetch(
                `${this.bridgeUrl}/api/bridge/ml-knowledge/${symbol}?module=${this.moduleName}`,
                {
                    method: 'GET',
                    mode: 'cors'
                }
            );
            
            if (response.ok) {
                const result = await response.json();
                this.cacheResult('knowledge', symbol, result);
                return result;
            }
        } catch (error) {
            console.warn('Failed to get ML knowledge:', error.message);
        }
        
        return this.getFallbackKnowledge(symbol);
    }
    
    /**
     * Get integration status
     */
    async getIntegrationStatus() {
        if (!this.enabled || this.fallbackMode) {
            return {
                bridge_active: false,
                fallback_mode: true,
                module: this.moduleName
            };
        }
        
        try {
            const response = await fetch(`${this.bridgeUrl}/api/bridge/status`, {
                method: 'GET',
                mode: 'cors',
                signal: AbortSignal.timeout(2000)
            });
            
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.warn('Failed to get integration status:', error.message);
        }
        
        return {
            bridge_active: false,
            fallback_mode: true,
            module: this.moduleName
        };
    }
    
    /**
     * Enhance existing module data with ML insights
     */
    async enhanceWithML(data) {
        const ml = await this.getMLKnowledge(data.symbol);
        
        if (ml && ml.current_prediction) {
            data.ml_enhanced = true;
            data.ml_prediction = ml.current_prediction;
            data.ml_confidence = ml.current_prediction.confidence || 0;
            data.ml_patterns = ml.learned_patterns || [];
            
            // Add visual indicators if elements exist
            this.addMLIndicators(data);
        }
        
        return data;
    }
    
    /**
     * Add ML indicator badges to UI
     */
    addMLIndicators(data) {
        // Add ML badge to existing elements without breaking layout
        const elements = document.querySelectorAll(`[data-symbol="${data.symbol}"]`);
        elements.forEach(el => {
            if (!el.querySelector('.ml-indicator')) {
                const badge = document.createElement('span');
                badge.className = 'ml-indicator';
                badge.style.cssText = `
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-size: 10px;
                    margin-left: 5px;
                    font-weight: 600;
                `;
                badge.textContent = `ML: ${(data.ml_confidence * 100).toFixed(0)}%`;
                badge.title = 'ML Enhanced';
                el.appendChild(badge);
            }
        });
    }
    
    /**
     * Cache management
     */
    cacheResult(type, key, data) {
        const cacheKey = `${type}_${key}`;
        this.cache.set(cacheKey, {
            data,
            timestamp: Date.now()
        });
    }
    
    getCachedResult(type, key) {
        const cacheKey = `${type}_${key}`;
        const cached = this.cache.get(cacheKey);
        
        if (cached && (Date.now() - cached.timestamp) < this.cacheTimeout) {
            return cached.data;
        }
        
        return null;
    }
    
    /**
     * Fallback responses when bridge is unavailable
     */
    getFallbackResponse(type, data) {
        // Return safe default response that won't break module functionality
        return {
            status: 'fallback',
            ml_insights: null,
            recommendation: {
                action: 'monitor',
                confidence: 0.5,
                reasoning: ['ML integration unavailable - using standard analysis']
            }
        };
    }
    
    getFallbackKnowledge(symbol) {
        return {
            symbol,
            learned_patterns: [],
            ml_feedback: [],
            current_prediction: null,
            integration_active: false
        };
    }
    
    /**
     * Enable/disable integration dynamically
     */
    setEnabled(enabled) {
        this.enabled = enabled;
        if (enabled) {
            this.checkBridgeStatus();
        }
    }
    
    /**
     * Utility function to safely integrate with existing code
     */
    static createOptional(moduleName, options = {}) {
        try {
            return new MLIntegrationClient(moduleName, options);
        } catch (error) {
            console.log('ML Integration Client not available');
            // Return a no-op client that won't break existing code
            return {
                sendDocumentSentiment: async () => ({ status: 'disabled' }),
                sendHistoricalPattern: async () => ({ status: 'disabled' }),
                sendMarketMovement: async () => ({ status: 'disabled' }),
                sendTechnicalIndicators: async () => ({ status: 'disabled' }),
                getMLKnowledge: async () => ({ integration_active: false }),
                enhanceWithML: async (data) => data,
                setEnabled: () => {},
                enabled: false
            };
        }
    }
}

// Auto-initialize for modules that include this script
if (typeof window !== 'undefined') {
    window.MLIntegrationClient = MLIntegrationClient;
    
    // Set up global instance if module name is available
    document.addEventListener('DOMContentLoaded', () => {
        const moduleName = document.querySelector('meta[name="module-name"]')?.content || 'unknown';
        window.mlIntegration = MLIntegrationClient.createOptional(moduleName, {
            enabled: true,
            bridgeUrl: 'http://localhost:8004'
        });
        
        console.log(`ML Integration Client initialized for module: ${moduleName}`);
    });
}