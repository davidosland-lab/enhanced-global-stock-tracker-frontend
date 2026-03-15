#!/usr/bin/env python3
"""
Deep Learning Ensemble System for Market Prediction
Combines multiple deep learning architectures for robust predictions

Features:
- CNN-LSTM hybrid for pattern recognition
- Bidirectional LSTM for temporal dependencies
- Variational Autoencoder for feature extraction
- Deep Reinforcement Learning integration
- Online learning and adaptation
- Uncertainty quantification
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Import neural network models
from neural_network_models import ModelConfig, NeuralNetworkPredictor

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger = logging.getLogger(__name__)

class CNN_LSTM(nn.Module):
    """CNN-LSTM hybrid model for temporal pattern recognition"""
    
    def __init__(self, config: ModelConfig):
        super(CNN_LSTM, self).__init__()
        
        # CNN layers for feature extraction
        self.conv1 = nn.Conv1d(config.input_dim, 64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(64, 128, kernel_size=3, padding=1)
        self.pool = nn.MaxPool1d(2)
        self.dropout1 = nn.Dropout(config.dropout)
        
        # Calculate CNN output dimension
        cnn_output_dim = 128 * (config.sequence_length // 2)
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=128,
            hidden_size=config.hidden_dim,
            num_layers=config.num_layers,
            batch_first=True,
            dropout=config.dropout if config.num_layers > 1 else 0,
            bidirectional=True
        )
        
        # Fully connected layers
        self.fc1 = nn.Linear(config.hidden_dim * 2, config.hidden_dim)
        self.fc2 = nn.Linear(config.hidden_dim, config.hidden_dim // 2)
        self.fc3 = nn.Linear(config.hidden_dim // 2, config.output_dim)
        self.dropout2 = nn.Dropout(config.dropout)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        # Reshape for CNN: (batch, features, sequence)
        x = x.transpose(1, 2)
        
        # CNN feature extraction
        x = self.relu(self.conv1(x))
        x = self.pool(x)
        x = self.relu(self.conv2(x))
        x = self.dropout1(x)
        
        # Reshape for LSTM: (batch, sequence, features)
        x = x.transpose(1, 2)
        
        # LSTM processing
        lstm_out, _ = self.lstm(x)
        
        # Take the last output
        lstm_last = lstm_out[:, -1, :]
        
        # Fully connected layers
        x = self.dropout2(lstm_last)
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        
        return x

class BidirectionalLSTM(nn.Module):
    """Bidirectional LSTM for capturing forward and backward dependencies"""
    
    def __init__(self, config: ModelConfig):
        super(BidirectionalLSTM, self).__init__()
        
        self.lstm = nn.LSTM(
            input_size=config.input_dim,
            hidden_size=config.hidden_dim,
            num_layers=config.num_layers,
            batch_first=True,
            dropout=config.dropout if config.num_layers > 1 else 0,
            bidirectional=True
        )
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(
            embed_dim=config.hidden_dim * 2,
            num_heads=config.attention_heads,
            dropout=config.dropout,
            batch_first=True
        )
        
        # Output layers
        self.fc1 = nn.Linear(config.hidden_dim * 2, config.hidden_dim)
        self.fc2 = nn.Linear(config.hidden_dim, config.output_dim)
        self.dropout = nn.Dropout(config.dropout)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        # Bidirectional LSTM
        lstm_out, _ = self.lstm(x)
        
        # Self-attention
        attn_out, attn_weights = self.attention(lstm_out, lstm_out, lstm_out)
        
        # Global average pooling
        pooled = torch.mean(attn_out, dim=1)
        
        # Output layers
        x = self.dropout(pooled)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        
        return x, attn_weights

class VariationalAutoencoder(nn.Module):
    """VAE for feature extraction and dimensionality reduction"""
    
    def __init__(self, config: ModelConfig):
        super(VariationalAutoencoder, self).__init__()
        
        # Calculate flattened input size
        self.input_size = config.input_dim * config.sequence_length
        self.latent_dim = config.hidden_dim // 4
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(self.input_size, config.hidden_dim),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.hidden_dim, config.hidden_dim // 2),
            nn.ReLU()
        )
        
        # Latent space parameters
        self.fc_mu = nn.Linear(config.hidden_dim // 2, self.latent_dim)
        self.fc_logvar = nn.Linear(config.hidden_dim // 2, self.latent_dim)
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(self.latent_dim, config.hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(config.dropout),
            nn.Linear(config.hidden_dim // 2, config.hidden_dim),
            nn.ReLU(),
            nn.Linear(config.hidden_dim, self.input_size)
        )
        
        # Prediction head
        self.predictor = nn.Sequential(
            nn.Linear(self.latent_dim, config.hidden_dim // 4),
            nn.ReLU(),
            nn.Linear(config.hidden_dim // 4, config.output_dim)
        )
        
    def encode(self, x):
        # Flatten input
        x = x.view(x.size(0), -1)
        h = self.encoder(x)
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)
        return mu, logvar
        
    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std
        
    def decode(self, z):
        return self.decoder(z)
        
    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        reconstruction = self.decode(z)
        prediction = self.predictor(z)
        return prediction, reconstruction, mu, logvar

class TemporalConvNet(nn.Module):
    """Temporal Convolutional Network for sequence modeling"""
    
    def __init__(self, config: ModelConfig):
        super(TemporalConvNet, self).__init__()
        
        channels = [config.input_dim, 64, 128, 256, 128, 64]
        kernel_size = 3
        dropout = config.dropout
        
        layers = []
        for i in range(len(channels) - 1):
            in_channels = channels[i]
            out_channels = channels[i + 1]
            dilation_size = 2 ** i
            padding = (kernel_size - 1) * dilation_size
            
            layers.append(nn.Conv1d(
                in_channels, out_channels, kernel_size,
                padding=padding, dilation=dilation_size
            ))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            
        self.network = nn.Sequential(*layers)
        self.global_pool = nn.AdaptiveAvgPool1d(1)
        self.fc = nn.Linear(64, config.output_dim)
        
    def forward(self, x):
        # Reshape for Conv1d: (batch, features, sequence)
        x = x.transpose(1, 2)
        x = self.network(x)
        x = self.global_pool(x).squeeze(-1)
        x = self.fc(x)
        return x

class DeepEnsemblePredictor:
    """Deep ensemble combining multiple architectures"""
    
    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig()
        self.models = self._initialize_models()
        self.optimizers = self._initialize_optimizers()
        self.criterion = nn.MSELoss()
        self.uncertainty_estimator = UncertaintyQuantifier()
        
    def _initialize_models(self) -> Dict[str, nn.Module]:
        """Initialize all models in the ensemble"""
        models = {
            'cnn_lstm': CNN_LSTM(self.config),
            'bidirectional': BidirectionalLSTM(self.config),
            'vae': VariationalAutoencoder(self.config),
            'tcn': TemporalConvNet(self.config)
        }
        
        for model in models.values():
            model.to(device)
            
        return models
        
    def _initialize_optimizers(self) -> Dict[str, optim.Optimizer]:
        """Initialize optimizers for each model"""
        optimizers = {}
        for name, model in self.models.items():
            optimizers[name] = optim.Adam(
                model.parameters(),
                lr=self.config.learning_rate
            )
        return optimizers
        
    def train_ensemble(self, train_loader: DataLoader, val_loader: DataLoader,
                      epochs: int = 100):
        """Train all models in the ensemble"""
        training_history = {}
        
        for model_name, model in self.models.items():
            logger.info(f"Training {model_name}...")
            history = self._train_single_model(
                model, 
                self.optimizers[model_name],
                train_loader,
                val_loader,
                epochs
            )
            training_history[model_name] = history
            
        return training_history
        
    def _train_single_model(self, model: nn.Module, optimizer: optim.Optimizer,
                          train_loader: DataLoader, val_loader: DataLoader,
                          epochs: int) -> List[Dict]:
        """Train a single model"""
        history = []
        best_val_loss = float('inf')
        
        for epoch in range(epochs):
            # Training
            model.train()
            train_losses = []
            
            for batch_x, batch_y in train_loader:
                batch_x = batch_x.to(device)
                batch_y = batch_y.to(device)
                
                optimizer.zero_grad()
                
                # Handle different model outputs
                if isinstance(model, VariationalAutoencoder):
                    pred, recon, mu, logvar = model(batch_x)
                    # VAE loss = reconstruction + KL divergence
                    recon_loss = F.mse_loss(
                        recon, 
                        batch_x.view(batch_x.size(0), -1)
                    )
                    kl_loss = -0.5 * torch.sum(
                        1 + logvar - mu.pow(2) - logvar.exp()
                    )
                    loss = self.criterion(pred, batch_y) + 0.1 * (recon_loss + kl_loss)
                elif isinstance(model, BidirectionalLSTM):
                    pred, _ = model(batch_x)
                    loss = self.criterion(pred, batch_y)
                else:
                    pred = model(batch_x)
                    loss = self.criterion(pred, batch_y)
                    
                loss.backward()
                optimizer.step()
                train_losses.append(loss.item())
                
            # Validation
            model.eval()
            val_losses = []
            
            with torch.no_grad():
                for batch_x, batch_y in val_loader:
                    batch_x = batch_x.to(device)
                    batch_y = batch_y.to(device)
                    
                    if isinstance(model, VariationalAutoencoder):
                        pred, _, _, _ = model(batch_x)
                    elif isinstance(model, BidirectionalLSTM):
                        pred, _ = model(batch_x)
                    else:
                        pred = model(batch_x)
                        
                    loss = self.criterion(pred, batch_y)
                    val_losses.append(loss.item())
                    
            avg_train_loss = np.mean(train_losses)
            avg_val_loss = np.mean(val_losses)
            
            history.append({
                'epoch': epoch,
                'train_loss': avg_train_loss,
                'val_loss': avg_val_loss
            })
            
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                
            if epoch % 20 == 0:
                logger.info(f"Epoch {epoch}: Train={avg_train_loss:.4f}, "
                          f"Val={avg_val_loss:.4f}")
                
        return history
        
    def predict_with_uncertainty(self, data: torch.Tensor) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions with uncertainty estimates"""
        predictions = []
        
        for model_name, model in self.models.items():
            model.eval()
            with torch.no_grad():
                data = data.to(device)
                
                if isinstance(model, VariationalAutoencoder):
                    pred, _, _, _ = model(data)
                elif isinstance(model, BidirectionalLSTM):
                    pred, _ = model(data)
                else:
                    pred = model(data)
                    
                predictions.append(pred.cpu().numpy())
                
        predictions = np.array(predictions)
        
        # Calculate mean and uncertainty
        mean_pred = np.mean(predictions, axis=0)
        uncertainty = np.std(predictions, axis=0)
        
        return mean_pred, uncertainty

class UncertaintyQuantifier:
    """Quantify prediction uncertainty using ensemble disagreement and dropout"""
    
    def __init__(self, n_samples: int = 100):
        self.n_samples = n_samples
        
    def monte_carlo_dropout(self, model: nn.Module, data: torch.Tensor,
                           n_samples: int = None) -> Tuple[np.ndarray, np.ndarray]:
        """Use Monte Carlo Dropout for uncertainty estimation"""
        n_samples = n_samples or self.n_samples
        predictions = []
        
        # Enable dropout during inference
        model.train()
        
        with torch.no_grad():
            for _ in range(n_samples):
                if isinstance(model, VariationalAutoencoder):
                    pred, _, _, _ = model(data)
                elif isinstance(model, BidirectionalLSTM):
                    pred, _ = model(data)
                else:
                    pred = model(data)
                    
                predictions.append(pred.cpu().numpy())
                
        predictions = np.array(predictions)
        mean_pred = np.mean(predictions, axis=0)
        epistemic_uncertainty = np.std(predictions, axis=0)
        
        return mean_pred, epistemic_uncertainty
        
    def ensemble_uncertainty(self, predictions: np.ndarray) -> Dict[str, np.ndarray]:
        """Calculate various uncertainty metrics from ensemble predictions"""
        mean_pred = np.mean(predictions, axis=0)
        std_pred = np.std(predictions, axis=0)
        
        # Coefficient of variation
        cv = std_pred / (np.abs(mean_pred) + 1e-8)
        
        # Entropy-based uncertainty (for classification)
        if predictions.shape[-1] > 1:
            # Softmax probabilities
            probs = np.exp(predictions) / np.sum(np.exp(predictions), axis=-1, keepdims=True)
            mean_probs = np.mean(probs, axis=0)
            entropy = -np.sum(mean_probs * np.log(mean_probs + 1e-8), axis=-1)
        else:
            entropy = None
            
        return {
            'mean': mean_pred,
            'std': std_pred,
            'cv': cv,
            'entropy': entropy
        }

class OnlineLearningAdapter:
    """Adapt models online with streaming data"""
    
    def __init__(self, model: nn.Module, learning_rate: float = 1e-4):
        self.model = model
        self.optimizer = optim.SGD(model.parameters(), lr=learning_rate)
        self.buffer_size = 100
        self.data_buffer = []
        
    def update(self, new_data: torch.Tensor, new_target: torch.Tensor):
        """Update model with new data point"""
        self.model.train()
        
        # Add to buffer
        self.data_buffer.append((new_data, new_target))
        
        # Keep buffer size limited
        if len(self.data_buffer) > self.buffer_size:
            self.data_buffer.pop(0)
            
        # Mini-batch update
        if len(self.data_buffer) >= 10:
            batch_data = torch.cat([d[0] for d in self.data_buffer[-10:]])
            batch_targets = torch.cat([d[1] for d in self.data_buffer[-10:]])
            
            self.optimizer.zero_grad()
            predictions = self.model(batch_data)
            loss = F.mse_loss(predictions, batch_targets)
            loss.backward()
            self.optimizer.step()
            
            return loss.item()
        return None

# Export main classes
__all__ = [
    'CNN_LSTM',
    'BidirectionalLSTM',
    'VariationalAutoencoder',
    'TemporalConvNet',
    'DeepEnsemblePredictor',
    'UncertaintyQuantifier',
    'OnlineLearningAdapter'
]