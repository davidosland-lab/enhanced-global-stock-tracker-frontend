# Trained LSTM Models Storage

This directory stores trained LSTM models and scalers.

## Structure:
- {SYMBOL}_lstm_model.keras - Trained Keras 3 model for each stock
- {SYMBOL}_scaler.pkl - MinMaxScaler for each stock's features

## Example:
- AAPL_lstm_model.keras (Apple's trained model)
- AAPL_scaler.pkl (Apple's feature scaler)
- MSFT_lstm_model.keras (Microsoft's trained model)
- MSFT_scaler.pkl (Microsoft's feature scaler)

## Purpose:
Models are persisted here to avoid retraining on every pipeline run.
Training takes ~2-5 minutes per stock. Loading takes <1 second.

## Training:
python finbert_v4.4.4/models/train_lstm.py --symbol AAPL

## Size Estimates:
- Each .keras model: ~2-5 MB
- Each .pkl scaler: ~5-10 KB
- 212 US stocks: ~500 MB - 1 GB total
- 240 UK stocks: ~600 MB - 1.2 GB total
