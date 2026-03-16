@app.route('/api/backtest/swing', methods=['POST'])
def run_swing_trading_backtest():
    """
    Run 5-day swing trading backtest with REAL sentiment + LSTM
    
    Request JSON:
    {
        "symbol": "AAPL",
        "start_date": "2023-01-01",
        "end_date": "2024-11-01",
        "initial_capital": 100000,
        "holding_period_days": 5,
        "stop_loss_percent": 3.0,
        "confidence_threshold": 0.65,
        "max_position_size": 0.25,
        "use_real_sentiment": true,
        "use_lstm": true,
        "sentiment_weight": 0.25,
        "lstm_weight": 0.25,
        "technical_weight": 0.25,
        "momentum_weight": 0.15,
        "volume_weight": 0.10
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['symbol', 'start_date', 'end_date']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({'error': f'Missing required fields: {missing}'}), 400
        
        symbol = data['symbol'].upper()
        start_date = data['start_date']
        end_date = data['end_date']
        
        # Extract parameters with defaults
        initial_capital = data.get('initial_capital', 100000.0)
        holding_period_days = data.get('holding_period_days', 5)
        stop_loss_percent = data.get('stop_loss_percent', 3.0)
        confidence_threshold = data.get('confidence_threshold', 0.65)
        max_position_size = data.get('max_position_size', 0.25)
        use_real_sentiment = data.get('use_real_sentiment', True)
        use_lstm = data.get('use_lstm', True)
        
        # Component weights
        sentiment_weight = data.get('sentiment_weight', 0.25)
        lstm_weight = data.get('lstm_weight', 0.25)
        technical_weight = data.get('technical_weight', 0.25)
        momentum_weight = data.get('momentum_weight', 0.15)
        volume_weight = data.get('volume_weight', 0.10)
        
        logger.info(f"Starting 5-day swing backtest for {symbol}: {start_date} to {end_date}")
        logger.info(f"Config: sentiment={use_real_sentiment}, LSTM={use_lstm}, threshold={confidence_threshold}")
        
        # Import swing trading module
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'models'))
        from backtesting.swing_trader_engine import SwingTraderEngine
        from backtesting.data_loader import HistoricalDataLoader
        from backtesting.news_sentiment_fetcher import NewsSentimentFetcher
        
        # Phase 1: Load price data
        data_loader = HistoricalDataLoader()
        price_data = data_loader.load_price_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval='1d'
        )
        
        if price_data is None or len(price_data) < 60:
            return jsonify({
                'error': f'Insufficient price data for {symbol}',
                'suggestion': 'Try a longer date range (need at least 60 trading days)'
            }), 400
        
        # Phase 2: Load news sentiment (if enabled)
        news_data = None
        if use_real_sentiment:
            try:
                logger.info(f"Fetching historical news sentiment for {symbol}...")
                sentiment_fetcher = NewsSentimentFetcher()
                news_data = sentiment_fetcher.fetch_historical_sentiment(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date
                )
                logger.info(f"Loaded {len(news_data) if news_data is not None else 0} news articles")
            except Exception as e:
                logger.warning(f"Could not load news sentiment: {e}. Continuing without sentiment.")
                news_data = None
        
        # Phase 3: Initialize swing trader
        engine = SwingTraderEngine(
            initial_capital=initial_capital,
            holding_period_days=holding_period_days,
            stop_loss_percent=stop_loss_percent,
            sentiment_weight=sentiment_weight,
            lstm_weight=lstm_weight,
            technical_weight=technical_weight,
            momentum_weight=momentum_weight,
            volume_weight=volume_weight,
            confidence_threshold=confidence_threshold,
            max_position_size=max_position_size,
            use_real_sentiment=use_real_sentiment and news_data is not None,
            use_lstm=use_lstm
        )
        
        # Phase 4: Run backtest
        results = engine.run_backtest(
            symbol=symbol,
            price_data=price_data,
            start_date=start_date,
            end_date=end_date,
            news_data=news_data
        )
        
        # Phase 5: Add metadata
        results['backtest_type'] = 'swing_trading'
        results['config'] = {
            'holding_period_days': holding_period_days,
            'stop_loss_percent': stop_loss_percent,
            'confidence_threshold': confidence_threshold,
            'max_position_size': max_position_size,
            'use_real_sentiment': use_real_sentiment,
            'use_lstm': use_lstm,
            'sentiment_weight': sentiment_weight,
            'lstm_weight': lstm_weight,
            'technical_weight': technical_weight,
            'momentum_weight': momentum_weight,
            'volume_weight': volume_weight,
            'news_articles_used': len(news_data) if news_data is not None else 0
        }
        
        logger.info(
            f"Swing backtest complete: {results.get('total_trades', 0)} trades, "
            f"{results.get('total_return_pct', 0):.2f}% return"
        )
        
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"Swing trading backtest error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
