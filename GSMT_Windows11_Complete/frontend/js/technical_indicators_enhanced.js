/**
 * Enhanced Technical Indicators Library
 * Based on open-source implementations from Stock.Indicators, indicator, and other repos
 * GSMT Ver 8.1.3
 */

class EnhancedTechnicalIndicators {
    
    /**
     * VWAP - Volume Weighted Average Price
     * Essential for intraday trading
     */
    static calculateVWAP(data) {
        let cumulativeTPV = 0;
        let cumulativeVolume = 0;
        const vwap = [];
        
        data.forEach((candle) => {
            const typicalPrice = (candle.high + candle.low + candle.close) / 3;
            cumulativeTPV += typicalPrice * candle.volume;
            cumulativeVolume += candle.volume;
            
            vwap.push({
                time: candle.time || candle.timestamp,
                value: cumulativeVolume > 0 ? cumulativeTPV / cumulativeVolume : typicalPrice
            });
        });
        
        return vwap;
    }
    
    /**
     * Ichimoku Cloud
     * Complete trend following system
     */
    static calculateIchimoku(data) {
        const conversionPeriod = 9;
        const basePeriod = 26;
        const spanPeriod = 52;
        const displacement = 26;
        
        const result = {
            tenkan: [],    // Conversion line
            kijun: [],     // Base line
            senkouA: [],   // Leading Span A
            senkouB: [],   // Leading Span B
            chikou: []     // Lagging Span
        };
        
        for (let i = 0; i < data.length; i++) {
            // Tenkan-sen (Conversion Line)
            if (i >= conversionPeriod - 1) {
                const period = data.slice(i - conversionPeriod + 1, i + 1);
                const high = Math.max(...period.map(d => d.high));
                const low = Math.min(...period.map(d => d.low));
                result.tenkan.push((high + low) / 2);
            } else {
                result.tenkan.push(null);
            }
            
            // Kijun-sen (Base Line)
            if (i >= basePeriod - 1) {
                const period = data.slice(i - basePeriod + 1, i + 1);
                const high = Math.max(...period.map(d => d.high));
                const low = Math.min(...period.map(d => d.low));
                result.kijun.push((high + low) / 2);
            } else {
                result.kijun.push(null);
            }
            
            // Senkou Span B (Leading Span B)
            if (i >= spanPeriod - 1) {
                const period = data.slice(i - spanPeriod + 1, i + 1);
                const high = Math.max(...period.map(d => d.high));
                const low = Math.min(...period.map(d => d.low));
                result.senkouB.push((high + low) / 2);
            } else {
                result.senkouB.push(null);
            }
        }
        
        // Senkou Span A (Leading Span A)
        for (let i = 0; i < data.length; i++) {
            if (result.tenkan[i] !== null && result.kijun[i] !== null) {
                result.senkouA.push((result.tenkan[i] + result.kijun[i]) / 2);
            } else {
                result.senkouA.push(null);
            }
        }
        
        // Chikou Span (Lagging Span) - close price displaced backwards
        result.chikou = data.map(d => d.close);
        
        return result;
    }
    
    /**
     * ADX - Average Directional Index
     * Measures trend strength
     */
    static calculateADX(data, period = 14) {
        const tr = [];  // True Range
        const plusDM = [];  // +DM
        const minusDM = [];  // -DM
        
        for (let i = 1; i < data.length; i++) {
            const high = data[i].high;
            const low = data[i].low;
            const prevClose = data[i-1].close;
            const prevHigh = data[i-1].high;
            const prevLow = data[i-1].low;
            
            // True Range
            const tr1 = high - low;
            const tr2 = Math.abs(high - prevClose);
            const tr3 = Math.abs(low - prevClose);
            tr.push(Math.max(tr1, tr2, tr3));
            
            // Directional Movement
            const upMove = high - prevHigh;
            const downMove = prevLow - low;
            
            if (upMove > downMove && upMove > 0) {
                plusDM.push(upMove);
            } else {
                plusDM.push(0);
            }
            
            if (downMove > upMove && downMove > 0) {
                minusDM.push(downMove);
            } else {
                minusDM.push(0);
            }
        }
        
        // Smooth the values
        const atr = this.calculateSMA(tr, period);
        const plusDI = this.calculateSMA(plusDM, period).map((v, i) => (v / atr[i]) * 100);
        const minusDI = this.calculateSMA(minusDM, period).map((v, i) => (v / atr[i]) * 100);
        
        // Calculate DX and ADX
        const dx = [];
        for (let i = 0; i < plusDI.length; i++) {
            const diff = Math.abs(plusDI[i] - minusDI[i]);
            const sum = plusDI[i] + minusDI[i];
            dx.push(sum === 0 ? 0 : (diff / sum) * 100);
        }
        
        const adx = this.calculateSMA(dx, period);
        
        return {
            adx: adx,
            plusDI: plusDI,
            minusDI: minusDI
        };
    }
    
    /**
     * Williams %R
     * Momentum indicator showing overbought/oversold
     */
    static calculateWilliamsR(data, period = 14) {
        const williamsR = [];
        
        for (let i = period - 1; i < data.length; i++) {
            const periodData = data.slice(i - period + 1, i + 1);
            const high = Math.max(...periodData.map(d => d.high));
            const low = Math.min(...periodData.map(d => d.low));
            const close = data[i].close;
            
            const wr = ((high - close) / (high - low)) * -100;
            williamsR.push(wr);
        }
        
        return williamsR;
    }
    
    /**
     * ATR - Average True Range
     * Volatility indicator for stop-loss placement
     */
    static calculateATR(data, period = 14) {
        const tr = [];
        
        for (let i = 1; i < data.length; i++) {
            const high = data[i].high;
            const low = data[i].low;
            const prevClose = data[i-1].close;
            
            const tr1 = high - low;
            const tr2 = Math.abs(high - prevClose);
            const tr3 = Math.abs(low - prevClose);
            
            tr.push(Math.max(tr1, tr2, tr3));
        }
        
        return this.calculateEMA(tr, period);
    }
    
    /**
     * Candlestick Pattern Recognition
     * Identifies common reversal and continuation patterns
     */
    static detectCandlePatterns(data) {
        const patterns = [];
        
        for (let i = 0; i < data.length; i++) {
            const candle = data[i];
            const o = candle.open;
            const h = candle.high;
            const l = candle.low;
            const c = candle.close;
            
            // Doji
            if (Math.abs(c - o) <= ((h - l) * 0.1)) {
                patterns.push({
                    index: i,
                    pattern: 'Doji',
                    type: 'reversal',
                    candle: candle
                });
            }
            
            // Hammer
            const body = Math.abs(c - o);
            const lowerShadow = Math.min(o, c) - l;
            const upperShadow = h - Math.max(o, c);
            
            if (lowerShadow > body * 2 && upperShadow < body * 0.5) {
                patterns.push({
                    index: i,
                    pattern: 'Hammer',
                    type: 'bullish_reversal',
                    candle: candle
                });
            }
            
            // Shooting Star
            if (upperShadow > body * 2 && lowerShadow < body * 0.5) {
                patterns.push({
                    index: i,
                    pattern: 'Shooting Star',
                    type: 'bearish_reversal',
                    candle: candle
                });
            }
            
            // Engulfing patterns
            if (i > 0) {
                const prev = data[i-1];
                
                // Bullish Engulfing
                if (prev.close < prev.open && c > o && 
                    o < prev.close && c > prev.open) {
                    patterns.push({
                        index: i,
                        pattern: 'Bullish Engulfing',
                        type: 'bullish_reversal',
                        candles: [prev, candle]
                    });
                }
                
                // Bearish Engulfing
                if (prev.close > prev.open && c < o &&
                    o > prev.close && c < prev.open) {
                    patterns.push({
                        index: i,
                        pattern: 'Bearish Engulfing',
                        type: 'bearish_reversal',
                        candles: [prev, candle]
                    });
                }
            }
            
            // Morning Star (3-candle pattern)
            if (i >= 2) {
                const first = data[i-2];
                const second = data[i-1];
                const third = candle;
                
                if (first.close < first.open && // Bearish candle
                    Math.abs(second.close - second.open) < (second.high - second.low) * 0.3 && // Small body
                    third.close > third.open && // Bullish candle
                    third.close > (first.open + first.close) / 2) { // Closes above midpoint
                    patterns.push({
                        index: i,
                        pattern: 'Morning Star',
                        type: 'bullish_reversal',
                        candles: [first, second, third]
                    });
                }
            }
        }
        
        return patterns;
    }
    
    /**
     * Anomaly Detection
     * Identifies unusual volume and price movements
     */
    static detectAnomalies(data, lookback = 20) {
        const anomalies = [];
        
        // Calculate average volume and standard deviation
        const volumes = data.map(d => d.volume);
        const avgVolume = volumes.reduce((sum, v) => sum + v, 0) / volumes.length;
        const stdDev = Math.sqrt(
            volumes.reduce((sum, v) => sum + Math.pow(v - avgVolume, 2), 0) / volumes.length
        );
        
        data.forEach((candle, i) => {
            // Volume anomaly (>2 standard deviations)
            const zScore = (candle.volume - avgVolume) / stdDev;
            if (Math.abs(zScore) > 2) {
                anomalies.push({
                    index: i,
                    type: 'volume_spike',
                    zScore: zScore,
                    candle: candle
                });
            }
            
            // Price breakout
            if (i >= lookback) {
                const recent = data.slice(i - lookback, i);
                const recentHighs = recent.map(r => r.high);
                const recentLows = recent.map(r => r.low);
                const high20 = Math.max(...recentHighs);
                const low20 = Math.min(...recentLows);
                
                if (candle.close > high20) {
                    anomalies.push({
                        index: i,
                        type: 'breakout_up',
                        level: high20,
                        candle: candle
                    });
                } else if (candle.close < low20) {
                    anomalies.push({
                        index: i,
                        type: 'breakout_down',
                        level: low20,
                        candle: candle
                    });
                }
            }
            
            // Gap detection
            if (i > 0) {
                const prevClose = data[i-1].close;
                const gapPercent = ((candle.open - prevClose) / prevClose) * 100;
                
                if (Math.abs(gapPercent) > 2) {
                    anomalies.push({
                        index: i,
                        type: gapPercent > 0 ? 'gap_up' : 'gap_down',
                        gapPercent: gapPercent,
                        candle: candle
                    });
                }
            }
        });
        
        return anomalies;
    }
    
    /**
     * Simple Backtesting Engine
     * Tests trading strategies on historical data
     */
    static backtest(data, strategy) {
        const trades = [];
        let position = null;
        let capitalStart = 10000;
        let capital = capitalStart;
        
        data.forEach((candle, i) => {
            const signal = strategy(candle, i, data);
            
            if (signal === 'BUY' && !position) {
                position = {
                    entryPrice: candle.close,
                    entryTime: candle.time || candle.timestamp,
                    shares: Math.floor(capital / candle.close)
                };
                capital -= position.shares * candle.close;
            } else if (signal === 'SELL' && position) {
                const exitPrice = candle.close;
                const profit = (exitPrice - position.entryPrice) * position.shares;
                const profitPercent = ((exitPrice - position.entryPrice) / position.entryPrice) * 100;
                
                capital += position.shares * exitPrice;
                
                trades.push({
                    entry: position.entryPrice,
                    exit: exitPrice,
                    shares: position.shares,
                    profit: profit,
                    profitPercent: profitPercent,
                    entryTime: position.entryTime,
                    exitTime: candle.time || candle.timestamp
                });
                
                position = null;
            }
        });
        
        // Close any open position at the end
        if (position) {
            const lastCandle = data[data.length - 1];
            capital += position.shares * lastCandle.close;
        }
        
        const winningTrades = trades.filter(t => t.profit > 0);
        const losingTrades = trades.filter(t => t.profit < 0);
        const totalProfit = trades.reduce((sum, t) => sum + t.profit, 0);
        
        return {
            trades: trades,
            totalTrades: trades.length,
            winningTrades: winningTrades.length,
            losingTrades: losingTrades.length,
            winRate: trades.length > 0 ? (winningTrades.length / trades.length * 100).toFixed(2) : 0,
            totalProfit: totalProfit,
            totalReturn: ((capital - capitalStart) / capitalStart * 100).toFixed(2),
            finalCapital: capital
        };
    }
    
    // Helper functions
    static calculateSMA(data, period) {
        const sma = [];
        for (let i = period - 1; i < data.length; i++) {
            const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
            sma.push(sum / period);
        }
        return sma;
    }
    
    static calculateEMA(data, period) {
        const ema = [];
        const multiplier = 2 / (period + 1);
        
        // Start with SMA for first value
        const firstSMA = data.slice(0, period).reduce((a, b) => a + b, 0) / period;
        ema.push(firstSMA);
        
        // Calculate EMA for rest
        for (let i = period; i < data.length; i++) {
            const value = (data[i] - ema[ema.length - 1]) * multiplier + ema[ema.length - 1];
            ema.push(value);
        }
        
        return ema;
    }
}

// Export for use in the main technical analysis module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedTechnicalIndicators;
}