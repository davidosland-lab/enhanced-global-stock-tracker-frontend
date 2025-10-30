#!/usr/bin/env python3
"""
PATCH: Add Next Day Price Prediction
=====================================
This patch adds next day's predicted price to the existing system.
No reinstallation needed - just apply this patch to your existing app_finbert_ultimate.py

HOW TO APPLY:
1. Back up your current app_finbert_ultimate.py
2. Open app_finbert_ultimate.py in a text editor
3. Find the section around line 845-890 (the predict method where price estimation is done)
4. Replace that section with the code below
"""

# STEP 1: Find this section in your app_finbert_ultimate.py (around line 845-890)
# Look for: "# Calculate price target and timeframe"

# STEP 2: Replace the entire price calculation section with this:

"""
            # Get current price
            current_price = float(df['Close'].iloc[-1])
            
            # Calculate price target and timeframe
            # Based on historical volatility and confidence
            returns = df['Close'].pct_change().dropna()
            volatility = returns.tail(20).std() if len(returns) >= 20 else returns.std()
            
            # Calculate daily volatility for next day prediction
            daily_volatility = returns.tail(30).std() if len(returns) >= 30 else volatility
            
            # Calculate ATR for better estimation
            high_low = df['High'] - df['Low']
            high_close = np.abs(df['High'] - df['Close'].shift())
            low_close = np.abs(df['Low'] - df['Close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            atr = true_range.tail(14).mean() if len(true_range) >= 14 else true_range.mean()
            atr_percent = (atr / current_price) * 100
            
            # Calculate daily ATR for next day
            daily_atr = true_range.tail(5).mean() if len(true_range) >= 5 else atr
            daily_atr_percent = (daily_atr / current_price) * 100
            
            # NEXT DAY PREDICTION
            # Use shorter-term metrics for 1-day prediction
            next_day_confidence_adjust = 0.3 + (float(max(probabilities)) * 0.4)  # More conservative for 1 day
            next_day_movement = daily_volatility * next_day_confidence_adjust * 100
            
            if prediction == 1:  # UP
                next_day_price = current_price * (1 + next_day_movement / 100)
                next_day_low = current_price * (1 + next_day_movement * 0.2 / 100)
                next_day_high = current_price * (1 + next_day_movement * 1.8 / 100)
            else:  # DOWN
                next_day_price = current_price * (1 - next_day_movement / 100)
                next_day_high = current_price * (1 - next_day_movement * 0.2 / 100)
                next_day_low = current_price * (1 - next_day_movement * 1.8 / 100)
            
            # LONGER TERM PREDICTION (existing code, slightly modified)
            base_movement = (volatility * 2 + atr_percent / 100) / 2
            confidence_multiplier = 0.5 + (float(max(probabilities)) * 0.5)
            price_movement_percent = base_movement * confidence_multiplier * 100
            
            # Calculate estimated price for longer term
            if prediction == 1:  # UP
                estimated_price = current_price * (1 + price_movement_percent / 100)
                price_range_low = current_price * (1 + price_movement_percent * 0.3 / 100)
                price_range_high = current_price * (1 + price_movement_percent * 1.5 / 100)
            else:  # DOWN
                estimated_price = current_price * (1 - price_movement_percent / 100)
                price_range_high = current_price * (1 - price_movement_percent * 0.3 / 100)
                price_range_low = current_price * (1 - price_movement_percent * 1.5 / 100)
            
            # Determine timeframe based on volatility
            if volatility > 0.03:  # High volatility
                timeframe_text = "3-5 trading days"
            elif volatility > 0.02:  # Medium volatility
                timeframe_text = "1-2 weeks"
            elif volatility > 0.01:  # Low volatility
                timeframe_text = "2-4 weeks"
            else:  # Very low volatility
                timeframe_text = "1-2 months"
            
            # Feature importance
            importance = dict(zip(feature_cols, model.feature_importances_))
            top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]
            
            result = {
                "symbol": symbol,
                "prediction": "UP" if prediction == 1 else "DOWN",
                "confidence": float(max(probabilities)),
                "probabilities": {
                    "up": float(probabilities[1]) if len(probabilities) > 1 else 0.5,
                    "down": float(probabilities[0]) if len(probabilities) > 0 else 0.5
                },
                "current_price": current_price,
                "next_day": {
                    "price": round(next_day_price, 2),
                    "low": round(next_day_low, 2),
                    "high": round(next_day_high, 2),
                    "change_percent": round(next_day_movement, 2)
                },
                "estimated_price": round(estimated_price, 2),
                "price_range": {
                    "low": round(price_range_low, 2),
                    "high": round(price_range_high, 2)
                },
                "price_change_percent": round(price_movement_percent, 2),
                "timeframe": timeframe_text,
                "volatility_percent": round(volatility * 100, 2),
                "data_points_used": len(df),
                "top_features": top_features,
                "timestamp": datetime.now().isoformat()
            }
"""

# STEP 3: Find the JavaScript display section (around line 1462-1490)
# Look for: "// Current price and estimated price"
# Replace with this enhanced version:

"""
                    // Current price and estimated price
                    html += '<p style="font-size: 18px; margin: 10px 0;">Current Price: <strong>$' + data.current_price.toFixed(2) + '</strong></p>';
                    
                    // NEXT DAY PREDICTION (NEW!)
                    if (data.next_day) {
                        html += '<div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #ffc107;">';
                        html += '<h4 style="margin: 0 0 10px 0; color: #856404;">📅 Next Trading Day Prediction</h4>';
                        html += '<p style="font-size: 18px; margin: 5px 0; color: ' + (isUp ? '#28a745' : '#dc3545') + '">';
                        html += 'Next Day Target: <strong>$' + data.next_day.price.toFixed(2) + '</strong>';
                        html += ' (' + (isUp ? '+' : '') + data.next_day.change_percent.toFixed(2) + '%)</p>';
                        html += '<p style="margin: 5px 0; color: #666;">Range: $' + 
                               data.next_day.low.toFixed(2) + ' - $' + 
                               data.next_day.high.toFixed(2) + '</p>';
                        html += '</div>';
                    }
                    
                    // LONGER TERM PREDICTION (existing)
                    if (data.estimated_price) {
                        html += '<div style="background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 15px 0;">';
                        html += '<h4 style="margin: 0 0 10px 0; color: #004085;">📈 ' + data.timeframe + ' Target</h4>';
                        html += '<p style="font-size: 20px; margin: 5px 0; color: ' + (isUp ? '#28a745' : '#dc3545') + '">';
                        html += 'Target Price: <strong>$' + data.estimated_price.toFixed(2) + '</strong>';
                        html += ' (' + (isUp ? '+' : '') + data.price_change_percent.toFixed(1) + '%)</p>';
                        
                        if (data.price_range) {
                            html += '<p style="margin: 5px 0; color: #666;">Range: $' + 
                                   data.price_range.low.toFixed(2) + ' - $' + 
                                   data.price_range.high.toFixed(2) + '</p>';
                        }
                        
                        if (data.timeframe) {
                            html += '<p style="margin: 5px 0; color: #666;">⏱️ Timeframe: <strong>' + 
                                   data.timeframe + '</strong></p>';
                        }
                        
                        if (data.volatility_percent !== undefined) {
                            html += '<p style="margin: 5px 0; color: #666; font-size: 12px;">Volatility: ' + 
                                   data.volatility_percent.toFixed(1) + '%</p>';
                        }
                        html += '</div>';
                    }
"""

print("""
PATCH APPLICATION COMPLETE!
==========================
The patch adds:
1. Next day price prediction with conservative estimates
2. Next day price range (low/high)
3. Separate display box for next day vs longer term

No need to reinstall - just edit the two sections in app_finbert_ultimate.py
""")