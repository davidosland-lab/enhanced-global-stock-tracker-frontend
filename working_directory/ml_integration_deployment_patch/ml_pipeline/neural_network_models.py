#!/usr/bin/env python3
"""
Neural Network Models for Enhanced Global Stock Market Tracker
Implements LSTM, GRU, Transformer, and hybrid models for market prediction

Features:
- LSTM (Long Short-Term Memory) for time series prediction
- GRU (Gated Recurrent Unit) for efficient sequence modeling
- Transformer architecture for attention-based predictions
- Hybrid models combining multiple architectures
- Ensemble methods for improved accuracy
- Real-time model updating and retraining
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit
import warnings
warnings.filterwarnings('ignore')

# Check for GPU availability
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for neural network models"""
    input_dim: int = 10
    hidden_dim: int = 128
    output_dim: int = 1
    num_layers: int = 2
    dropout: float = 0.2
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 100
    sequence_length: int = 30
    attention_heads: int = 8
    
class StockDataset(Dataset):
    """Custom dataset for stock market time series"""
    
    def __init__(self, data: np.ndarray, sequence_length: int = 30):
        self.data = torch.FloatTensor(data)
        self.sequence_length = sequence_length
        
    def __len__(self):
        return len(self.data) - self.sequence_length
        
    def __getitem__(self, idx):
        x = self.data[idx:idx + self.sequence_length]
        y = self.data[idx + self.sequence_length]
        return x, y

class LSTMModel(nn.Module):
    """LSTM model for stock price prediction"""
    
    def __init__(self, config: ModelConfig):
        super(LSTMModel, self).__init__()
        self.config = config
        
        self.lstm = nn.LSTM(
            input_size=config.input_dim,
            hidden_size=config.hidden_dim,
            num_layers=config.num_layers,
            batch_first=True,
            dropout=config.dropout if config.num_layers > 1 else 0
        )
        
        self.dropout = nn.Dropout(config.dropout)
        self.fc1 = nn.Linear(config.hidden_dim, config.hidden_dim // 2)
        self.fc2 = nn.Linear(config.hidden_dim // 2, config.output_dim)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        # LSTM forward pass
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Take the last output
        last_output = lstm_out[:, -1, :]
        
        # Fully connected layers
        x = self.dropout(last_output)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        
        return x

class GRUModel(nn.Module):
    """GRU model for stock price prediction"""
    
    def __init__(self, config: ModelConfig):
        super(GRUModel, self).__init__()
        self.config = config
        
        self.gru = nn.GRU(
            input_size=config.input_dim,
            hidden_size=config.hidden_dim,
            num_layers=config.num_layers,
            batch_first=True,
            dropout=config.dropout if config.num_layers > 1 else 0
        )
        
        self.dropout = nn.Dropout(config.dropout)
        self.fc1 = nn.Linear(config.hidden_dim, config.hidden_dim // 2)
        self.fc2 = nn.Linear(config.hidden_dim // 2, config.output_dim)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        # GRU forward pass
        gru_out, hidden = self.gru(x)
        
        # Take the last output
        last_output = gru_out[:, -1, :]
        
        # Fully connected layers
        x = self.dropout(last_output)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        
        return x

class TransformerModel(nn.Module):
    """Transformer model for stock price prediction"""
    
    def __init__(self, config: ModelConfig):
        super(TransformerModel, self).__init__()
        self.config = config
        
        # Positional encoding
        self.pos_encoder = PositionalEncoding(config.input_dim, config.dropout)
        
        # Transformer encoder
        encoder_layers = nn.TransformerEncoderLayer(
            d_model=config.input_dim,
            nhead=config.attention_heads,
            dim_feedforward=config.hidden_dim,
            dropout=config.dropout,
            batch_first=True
        )
        
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layers,
            num_layers=config.num_layers
        )
        
        self.fc1 = nn.Linear(config.input_dim, config.hidden_dim // 2)
        self.fc2 = nn.Linear(config.hidden_dim // 2, config.output_dim)
        self.dropout = nn.Dropout(config.dropout)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        # Add positional encoding
        x = self.pos_encoder(x)
        
        # Transformer encoding
        x = self.transformer_encoder(x)
        
        # Global average pooling
        x = torch.mean(x, dim=1)
        
        # Fully connected layers
        x = self.dropout(x)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        
        return x

class PositionalEncoding(nn.Module):
    """Positional encoding for transformer models"""
    
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)
        
    def forward(self, x):
        x = x + self.pe[:x.size(0)]
        return self.dropout(x)

class HybridLSTMGRU(nn.Module):
    """Hybrid model combining LSTM and GRU"""
    
    def __init__(self, config: ModelConfig):
        super(HybridLSTMGRU, self).__init__()
        self.config = config
        
        # LSTM branch
        self.lstm = nn.LSTM(
            input_size=config.input_dim,
            hidden_size=config.hidden_dim // 2,
            num_layers=config.num_layers,
            batch_first=True,
            dropout=config.dropout if config.num_layers > 1 else 0
        )
        
        # GRU branch
        self.gru = nn.GRU(
            input_size=config.input_dim,
            hidden_size=config.hidden_dim // 2,
            num_layers=config.num_layers,
            batch_first=True,
            dropout=config.dropout if config.num_layers > 1 else 0
        )
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(
            embed_dim=config.hidden_dim,
            num_heads=4,
            dropout=config.dropout,
            batch_first=True
        )
        
        # Final layers
        self.fc1 = nn.Linear(config.hidden_dim, config.hidden_dim // 2)
        self.fc2 = nn.Linear(config.hidden_dim // 2, config.output_dim)
        self.dropout = nn.Dropout(config.dropout)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        # LSTM branch
        lstm_out, _ = self.lstm(x)
        lstm_last = lstm_out[:, -1, :]
        
        # GRU branch
        gru_out, _ = self.gru(x)
        gru_last = gru_out[:, -1, :]
        
        # Concatenate outputs
        combined = torch.cat([lstm_last, gru_last], dim=1)
        
        # Self-attention
        combined = combined.unsqueeze(1)
        attn_out, _ = self.attention(combined, combined, combined)
        attn_out = attn_out.squeeze(1)
        
        # Final layers
        x = self.dropout(attn_out)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        
        return x

class NeuralNetworkPredictor:
    """Main class for neural network-based stock prediction"""
    
    def __init__(self, model_type: str = 'lstm', config: Optional[ModelConfig] = None):
        self.model_type = model_type
        self.config = config or ModelConfig()
        self.model = self._create_model()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.config.learning_rate)
        self.criterion = nn.MSELoss()
        self.scaler = StandardScaler()
        self.training_history = []
        
    def _create_model(self) -> nn.Module:
        """Create the specified model"""
        model_map = {
            'lstm': LSTMModel,
            'gru': GRUModel,
            'transformer': TransformerModel,
            'hybrid': HybridLSTMGRU
        }
        
        if self.model_type not in model_map:
            raise ValueError(f"Unknown model type: {self.model_type}")
            
        return model_map[self.model_type](self.config).to(device)
        
    def prepare_data(self, data: pd.DataFrame, feature_cols: List[str], 
                    target_col: str) -> Tuple[DataLoader, DataLoader]:
        """Prepare data for training"""
        # Extract features and target
        features = data[feature_cols].values
        target = data[target_col].values
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Create sequences
        X, y = [], []
        for i in range(len(features_scaled) - self.config.sequence_length):
            X.append(features_scaled[i:i + self.config.sequence_length])
            y.append(target[i + self.config.sequence_length])
            
        X = np.array(X)
        y = np.array(y).reshape(-1, 1)
        
        # Split data
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Create datasets
        train_dataset = torch.utils.data.TensorDataset(
            torch.FloatTensor(X_train),
            torch.FloatTensor(y_train)
        )
        val_dataset = torch.utils.data.TensorDataset(
            torch.FloatTensor(X_val),
            torch.FloatTensor(y_val)
        )
        
        # Create dataloaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.batch_size,
            shuffle=False
        )
        
        return train_loader, val_loader
        
    def train(self, train_loader: DataLoader, val_loader: DataLoader, 
             early_stopping: bool = True, patience: int = 10):
        """Train the model"""
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(self.config.epochs):
            # Training phase
            self.model.train()
            train_losses = []
            
            for batch_x, batch_y in train_loader:
                batch_x = batch_x.to(device)
                batch_y = batch_y.to(device)
                
                self.optimizer.zero_grad()
                outputs = self.model(batch_x)
                loss = self.criterion(outputs, batch_y)
                loss.backward()
                self.optimizer.step()
                
                train_losses.append(loss.item())
                
            # Validation phase
            self.model.eval()
            val_losses = []
            
            with torch.no_grad():
                for batch_x, batch_y in val_loader:
                    batch_x = batch_x.to(device)
                    batch_y = batch_y.to(device)
                    
                    outputs = self.model(batch_x)
                    loss = self.criterion(outputs, batch_y)
                    val_losses.append(loss.item())
                    
            avg_train_loss = np.mean(train_losses)
            avg_val_loss = np.mean(val_losses)
            
            self.training_history.append({
                'epoch': epoch,
                'train_loss': avg_train_loss,
                'val_loss': avg_val_loss
            })
            
            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}: Train Loss={avg_train_loss:.4f}, "
                          f"Val Loss={avg_val_loss:.4f}")
                
            # Early stopping
            if early_stopping:
                if avg_val_loss < best_val_loss:
                    best_val_loss = avg_val_loss
                    patience_counter = 0
                    # Save best model
                    self.save_model(f'best_{self.model_type}_model.pt')
                else:
                    patience_counter += 1
                    if patience_counter >= patience:
                        logger.info(f"Early stopping at epoch {epoch}")
                        break
                        
    def predict(self, data: np.ndarray) -> np.ndarray:
        """Make predictions"""
        self.model.eval()
        
        with torch.no_grad():
            # Scale input data
            data_scaled = self.scaler.transform(data)
            
            # Create sequences
            sequences = []
            for i in range(len(data_scaled) - self.config.sequence_length + 1):
                sequences.append(data_scaled[i:i + self.config.sequence_length])
                
            sequences = torch.FloatTensor(np.array(sequences)).to(device)
            
            # Make predictions
            predictions = self.model(sequences)
            
            return predictions.cpu().numpy()
            
    def save_model(self, filepath: str):
        """Save model state"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'config': self.config,
            'scaler': self.scaler,
            'training_history': self.training_history
        }, filepath)
        
    def load_model(self, filepath: str):
        """Load model state"""
        checkpoint = torch.load(filepath, map_location=device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.config = checkpoint['config']
        self.scaler = checkpoint['scaler']
        self.training_history = checkpoint['training_history']

class EnsembleNeuralPredictor:
    """Ensemble of multiple neural network models"""
    
    def __init__(self, model_types: List[str] = ['lstm', 'gru', 'transformer']):
        self.models = {}
        for model_type in model_types:
            self.models[model_type] = NeuralNetworkPredictor(model_type)
            
    def train_all(self, train_loader: DataLoader, val_loader: DataLoader):
        """Train all models in the ensemble"""
        for model_name, model in self.models.items():
            logger.info(f"Training {model_name} model...")
            model.train(train_loader, val_loader)
            
    def predict_ensemble(self, data: np.ndarray, method: str = 'mean') -> np.ndarray:
        """Make ensemble predictions"""
        predictions = []
        
        for model_name, model in self.models.items():
            pred = model.predict(data)
            predictions.append(pred)
            
        predictions = np.array(predictions)
        
        if method == 'mean':
            return np.mean(predictions, axis=0)
        elif method == 'median':
            return np.median(predictions, axis=0)
        elif method == 'weighted':
            # Weight by validation performance
            weights = self._get_model_weights()
            return np.average(predictions, axis=0, weights=weights)
        else:
            raise ValueError(f"Unknown ensemble method: {method}")
            
    def _get_model_weights(self) -> np.ndarray:
        """Get model weights based on validation performance"""
        val_losses = []
        
        for model_name, model in self.models.items():
            if model.training_history:
                # Get best validation loss
                best_val = min([h['val_loss'] for h in model.training_history])
                val_losses.append(best_val)
            else:
                val_losses.append(1.0)
                
        # Convert to weights (inverse of loss)
        weights = 1.0 / np.array(val_losses)
        weights = weights / weights.sum()
        
        return weights

class AttentionLSTM(nn.Module):
    """LSTM with attention mechanism"""
    
    def __init__(self, config: ModelConfig):
        super(AttentionLSTM, self).__init__()
        self.config = config
        
        self.lstm = nn.LSTM(
            input_size=config.input_dim,
            hidden_size=config.hidden_dim,
            num_layers=config.num_layers,
            batch_first=True,
            dropout=config.dropout if config.num_layers > 1 else 0
        )
        
        # Attention layers
        self.attention_weight = nn.Linear(config.hidden_dim, 1)
        self.softmax = nn.Softmax(dim=1)
        
        # Output layers
        self.fc1 = nn.Linear(config.hidden_dim, config.hidden_dim // 2)
        self.fc2 = nn.Linear(config.hidden_dim // 2, config.output_dim)
        self.dropout = nn.Dropout(config.dropout)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        # LSTM forward pass
        lstm_out, _ = self.lstm(x)
        
        # Attention mechanism
        attention_scores = self.attention_weight(lstm_out)
        attention_weights = self.softmax(attention_scores)
        
        # Weighted sum of LSTM outputs
        weighted_output = torch.sum(lstm_out * attention_weights, dim=1)
        
        # Output layers
        x = self.dropout(weighted_output)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        
        return x, attention_weights

# Export main classes and functions
__all__ = [
    'ModelConfig',
    'LSTMModel',
    'GRUModel',
    'TransformerModel',
    'HybridLSTMGRU',
    'AttentionLSTM',
    'NeuralNetworkPredictor',
    'EnsembleNeuralPredictor',
    'StockDataset'
]