"""
Hybrid CNN+LSTM model for network intrusion detection.
Combines convolutional layers for spatial feature extraction
with LSTM layers for temporal pattern recognition.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple, Dict, List
import json

class HybridCNNLSTM(nn.Module):
    """
    Hybrid CNN+LSTM model for network intrusion detection.
    
    Architecture:
    1. CNN layers for spatial feature extraction
    2. LSTM layers for temporal pattern recognition
    3. Dense layers for final classification
    """
    
    def __init__(self, 
                 input_size: int,
                 sequence_length: int = 10,
                 n_classes: int = 5,
                 cnn_filters: List[int] = [64, 128, 256],
                 lstm_hidden: int = 128,
                 lstm_layers: int = 2,
                 dropout_rate: float = 0.3):
        """
        Initialize the hybrid model.
        
        Args:
            input_size: Number of input features
            sequence_length: Length of input sequences
            n_classes: Number of output classes
            cnn_filters: List of CNN filter sizes
            lstm_hidden: LSTM hidden size
            lstm_layers: Number of LSTM layers
            dropout_rate: Dropout rate
        """
        super(HybridCNNLSTM, self).__init__()
        
        self.input_size = input_size
        self.sequence_length = sequence_length
        self.n_classes = n_classes
        self.cnn_filters = cnn_filters
        self.lstm_hidden = lstm_hidden
        self.lstm_layers = lstm_layers
        
        # CNN layers for spatial feature extraction
        self.conv_layers = nn.ModuleList()
        prev_filters = 1  # Input is treated as single channel
        
        for i, filters in enumerate(cnn_filters):
            self.conv_layers.append(
                nn.Conv1d(
                    in_channels=prev_filters,
                    out_channels=filters,
                    kernel_size=3,
                    padding=1
                )
            )
            prev_filters = filters
        
        # Batch normalization and dropout
        self.batch_norms = nn.ModuleList([
            nn.BatchNorm1d(filters) for filters in cnn_filters
        ])
        
        # LSTM layers for temporal pattern recognition
        # We'll set the input size dynamically based on CNN output
        self.lstm = None  # Will be initialized in forward pass
        self.lstm_hidden = lstm_hidden
        self.lstm_layers = lstm_layers
        self.dropout_rate = dropout_rate
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(
            embed_dim=lstm_hidden * 2,  # *2 for bidirectional
            num_heads=8,
            dropout=dropout_rate,
            batch_first=True
        )
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(lstm_hidden * 2, 256),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(128, n_classes)
        )
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize model weights."""
        for m in self.modules():
            if isinstance(m, nn.Conv1d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.LSTM):
                for name, param in m.named_parameters():
                    if 'weight' in name:
                        nn.init.xavier_normal_(param)
                    elif 'bias' in name:
                        nn.init.constant_(param, 0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the model.
        
        Args:
            x: Input tensor of shape (batch_size, sequence_length, input_size)
            
        Returns:
            Output tensor of shape (batch_size, n_classes)
        """
        batch_size, seq_len, input_size = x.size()
        
        # Apply CNN layers to each timestep independently
        # Reshape to (batch_size * seq_len, 1, input_size)
        x_reshaped = x.view(batch_size * seq_len, 1, input_size)
        
        # Apply CNN layers
        for conv, bn in zip(self.conv_layers, self.batch_norms):
            x_reshaped = F.relu(bn(conv(x_reshaped)))
            x_reshaped = F.max_pool1d(x_reshaped, kernel_size=2, stride=1, padding=1)
        
        # Reshape back to (batch_size, seq_len, cnn_output_size)
        cnn_output_size = x_reshaped.size(-1)
        x_lstm = x_reshaped.view(batch_size, seq_len, cnn_output_size)
        
        # Initialize LSTM if not done yet
        if self.lstm is None:
            self.lstm = nn.LSTM(
                input_size=cnn_output_size,
                hidden_size=self.lstm_hidden,
                num_layers=self.lstm_layers,
                batch_first=True,
                dropout=self.dropout_rate if self.lstm_layers > 1 else 0,
                bidirectional=True
            ).to(x.device)
        
        # Apply LSTM
        lstm_out, (hidden, cell) = self.lstm(x_lstm)
        
        # Apply attention mechanism
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        
        # Global average pooling
        pooled = torch.mean(attn_out, dim=1)
        
        # Classification
        output = self.classifier(pooled)
        
        return output
    
    def predict(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Make predictions with confidence scores.
        
        Args:
            x: Input tensor
            
        Returns:
            Tuple of (predictions, confidence_scores)
        """
        self.eval()
        with torch.no_grad():
            logits = self.forward(x)
            probabilities = F.softmax(logits, dim=1)
            predictions = torch.argmax(probabilities, dim=1)
            confidence = torch.max(probabilities, dim=1)[0]
        
        return predictions, confidence
    
    def get_model_info(self) -> Dict:
        """Get model information."""
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        
        return {
            'input_size': self.input_size,
            'sequence_length': self.sequence_length,
            'n_classes': self.n_classes,
            'cnn_filters': self.cnn_filters,
            'lstm_hidden': self.lstm_hidden,
            'lstm_layers': self.lstm_layers,
            'total_parameters': total_params,
            'trainable_parameters': trainable_params
        }

class ModelTrainer:
    """Trainer class for the hybrid model."""
    
    def __init__(self, 
                 model: HybridCNNLSTM,
                 device: str = 'cpu',
                 learning_rate: float = 0.001,
                 weight_decay: float = 1e-5):
        """
        Initialize trainer.
        
        Args:
            model: The hybrid model
            device: Device to use for training
            learning_rate: Learning rate
            weight_decay: Weight decay for regularization
        """
        self.model = model.to(device)
        self.device = device
        self.optimizer = torch.optim.Adam(
            model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        self.criterion = nn.CrossEntropyLoss()
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', patience=5, factor=0.5
        )
        
        # Training history
        self.train_losses = []
        self.train_accuracies = []
        self.val_losses = []
        self.val_accuracies = []
    
    def train_epoch(self, train_loader) -> Tuple[float, float]:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(self.device), target.to(self.device)
            
            self.optimizer.zero_grad()
            output = self.model(data)
            loss = self.criterion(output, target)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)
        
        avg_loss = total_loss / len(train_loader)
        accuracy = 100. * correct / total
        
        return avg_loss, accuracy
    
    def validate(self, val_loader) -> Tuple[float, float]:
        """Validate the model."""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                loss = self.criterion(output, target)
                
                total_loss += loss.item()
                pred = output.argmax(dim=1, keepdim=True)
                correct += pred.eq(target.view_as(pred)).sum().item()
                total += target.size(0)
        
        avg_loss = total_loss / len(val_loader)
        accuracy = 100. * correct / total
        
        return avg_loss, accuracy
    
    def train(self, 
              train_loader, 
              val_loader, 
              epochs: int = 50,
              early_stopping_patience: int = 10) -> Dict:
        """
        Train the model.
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            epochs: Number of epochs
            early_stopping_patience: Early stopping patience
            
        Returns:
            Training history dictionary
        """
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(epochs):
            # Train
            train_loss, train_acc = self.train_epoch(train_loader)
            
            # Validate
            val_loss, val_acc = self.validate(val_loader)
            
            # Update learning rate
            self.scheduler.step(val_loss)
            
            # Store history
            self.train_losses.append(train_loss)
            self.train_accuracies.append(train_acc)
            self.val_losses.append(val_loss)
            self.val_accuracies.append(val_acc)
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
            else:
                patience_counter += 1
            
            if patience_counter >= early_stopping_patience:
                print(f"Early stopping at epoch {epoch+1}")
                break
            
            if (epoch + 1) % 10 == 0:
                print(f'Epoch {epoch+1}/{epochs}: '
                      f'Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%, '
                      f'Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%')
        
        return {
            'train_losses': self.train_losses,
            'train_accuracies': self.train_accuracies,
            'val_losses': self.val_losses,
            'val_accuracies': self.val_accuracies
        }
    
    def save_model(self, filepath: str):
        """Save the trained model."""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'model_info': self.model.get_model_info(),
            'train_history': {
                'train_losses': self.train_losses,
                'train_accuracies': self.train_accuracies,
                'val_losses': self.val_losses,
                'val_accuracies': self.val_accuracies
            }
        }, filepath)
    
    def load_model(self, filepath: str):
        """Load a trained model."""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        
        if 'train_history' in checkpoint:
            history = checkpoint['train_history']
            self.train_losses = history['train_losses']
            self.train_accuracies = history['train_accuracies']
            self.val_losses = history['val_losses']
            self.val_accuracies = history['val_accuracies']

def create_model(input_size: int, 
                sequence_length: int = 10,
                n_classes: int = 5,
                **kwargs) -> HybridCNNLSTM:
    """
    Create a hybrid CNN+LSTM model.
    
    Args:
        input_size: Number of input features
        sequence_length: Length of input sequences
        n_classes: Number of output classes
        **kwargs: Additional model parameters
        
    Returns:
        Initialized hybrid model
    """
    return HybridCNNLSTM(
        input_size=input_size,
        sequence_length=sequence_length,
        n_classes=n_classes,
        **kwargs
    )

if __name__ == "__main__":
    # Test the model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create model
    model = create_model(
        input_size=41,  # KDD99-like features
        sequence_length=10,
        n_classes=5
    )
    
    print(f"Model created with {sum(p.numel() for p in model.parameters())} parameters")
    
    # Test forward pass
    batch_size = 32
    x = torch.randn(batch_size, 10, 41)
    output = model(x)
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {output.shape}")
    
    # Test prediction
    predictions, confidence = model.predict(x)
    print(f"Predictions shape: {predictions.shape}")
    print(f"Confidence shape: {confidence.shape}")
