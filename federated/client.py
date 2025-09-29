"""
Federated Learning Client for AI-Driven IDS.
Simulates client-side training and model updates.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
import json
import time
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.hybrid_model import HybridCNNLSTM, ModelTrainer
from models.preprocessing import NetworkFlowPreprocessor, create_sequences

class FederatedClient:
    """
    Federated learning client.
    Handles local training and model updates.
    """
    
    def __init__(self, 
                 client_id: str,
                 model: HybridCNNLSTM,
                 preprocessor: NetworkFlowPreprocessor,
                 data_path: str,
                 learning_rate: float = 0.001,
                 batch_size: int = 32,
                 local_epochs: int = 5):
        """
        Initialize the federated client.
        
        Args:
            client_id: Unique client identifier
            model: Local model instance
            preprocessor: Data preprocessor
            data_path: Path to client's local data
            learning_rate: Learning rate for local training
            batch_size: Batch size for training
            local_epochs: Number of local training epochs
        """
        self.client_id = client_id
        self.model = model
        self.preprocessor = preprocessor
        self.data_path = data_path
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.local_epochs = local_epochs
        
        # Training history
        self.training_history = []
        self.last_accuracy = 0.0
        self.last_update_time = None
        
        # Load local data
        self.local_data = self._load_local_data()
        
        # Initialize trainer
        self.trainer = ModelTrainer(
            model=self.model,
            learning_rate=learning_rate
        )
    
    def _load_local_data(self) -> Dict[str, Any]:
        """Load and preprocess local data."""
        try:
            if os.path.exists(self.data_path):
                df = pd.read_csv(self.data_path)
                print(f"Client {self.client_id}: Loaded {len(df)} samples")
                
                # Preprocess data
                X = df.drop(['label', 'timestamp'], axis=1, errors='ignore')
                y = df['label']
                
                X_processed = self.preprocessor.transform(X)
                y_encoded = self.preprocessor.encode_labels(y)
                
                # Create sequences
                X_seq, y_seq = create_sequences(X_processed, y_encoded)
                
                # Create data loaders
                dataset = torch.utils.data.TensorDataset(
                    torch.FloatTensor(X_seq),
                    torch.LongTensor(y_seq)
                )
                
                train_size = int(0.8 * len(dataset))
                val_size = len(dataset) - train_size
                train_dataset, val_dataset = torch.utils.data.random_split(
                    dataset, [train_size, val_size]
                )
                
                train_loader = torch.utils.data.DataLoader(
                    train_dataset, batch_size=self.batch_size, shuffle=True
                )
                val_loader = torch.utils.data.DataLoader(
                    val_dataset, batch_size=self.batch_size, shuffle=False
                )
                
                return {
                    "train_loader": train_loader,
                    "val_loader": val_loader,
                    "total_samples": len(df),
                    "train_samples": train_size,
                    "val_samples": val_size
                }
            else:
                print(f"Client {self.client_id}: No data file found at {self.data_path}")
                return None
                
        except Exception as e:
            print(f"Client {self.client_id}: Error loading data: {e}")
            return None
    
    def train_local_model(self) -> Dict[str, Any]:
        """
        Train the local model on client data.
        
        Returns:
            Training results dictionary
        """
        if not self.local_data:
            return {
                "success": False,
                "message": "No local data available",
                "accuracy": 0.0,
                "samples": 0
            }
        
        try:
            # Train for local epochs
            history = self.trainer.train(
                train_loader=self.local_data["train_loader"],
                val_loader=self.local_data["val_loader"],
                epochs=self.local_epochs,
                early_stopping_patience=3
            )
            
            # Get final accuracy
            final_accuracy = max(history["val_accuracies"]) if history["val_accuracies"] else 0.0
            self.last_accuracy = final_accuracy
            self.last_update_time = datetime.now().isoformat()
            
            # Store training history
            self.training_history.append({
                "timestamp": self.last_update_time,
                "accuracy": final_accuracy,
                "epochs": self.local_epochs,
                "samples": self.local_data["total_samples"]
            })
            
            print(f"Client {self.client_id}: Local training completed. Accuracy: {final_accuracy:.3f}")
            
            return {
                "success": True,
                "accuracy": final_accuracy,
                "samples": self.local_data["total_samples"],
                "epochs": self.local_epochs,
                "history": history
            }
            
        except Exception as e:
            print(f"Client {self.client_id}: Training error: {e}")
            return {
                "success": False,
                "message": str(e),
                "accuracy": 0.0,
                "samples": 0
            }
    
    def get_model_weights(self) -> List[torch.Tensor]:
        """Get current model weights."""
        return [param.clone().detach() for param in self.model.parameters()]
    
    def update_model_weights(self, global_weights: List[torch.Tensor]):
        """Update local model with global weights."""
        with torch.no_grad():
            for param, global_param in zip(self.model.parameters(), global_weights):
                param.copy_(global_param)
        
        print(f"Client {self.client_id}: Model weights updated from global model")
    
    def evaluate_model(self) -> Dict[str, Any]:
        """Evaluate the local model."""
        if not self.local_data:
            return {"accuracy": 0.0, "samples": 0}
        
        try:
            val_loss, val_accuracy = self.trainer.validate(self.local_data["val_loader"])
            
            return {
                "accuracy": val_accuracy,
                "loss": val_loss,
                "samples": self.local_data["val_samples"]
            }
            
        except Exception as e:
            print(f"Client {self.client_id}: Evaluation error: {e}")
            return {"accuracy": 0.0, "samples": 0}
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get client information and status."""
        return {
            "client_id": self.client_id,
            "data_path": self.data_path,
            "has_data": self.local_data is not None,
            "total_samples": self.local_data["total_samples"] if self.local_data else 0,
            "last_accuracy": self.last_accuracy,
            "last_update": self.last_update_time,
            "training_history": self.training_history[-5:],  # Last 5 training sessions
            "model_info": self.model.get_model_info()
        }
    
    def save_client_state(self, filepath: str):
        """Save client state to file."""
        state = {
            "client_id": self.client_id,
            "model_state_dict": self.model.state_dict(),
            "training_history": self.training_history,
            "last_accuracy": self.last_accuracy,
            "last_update_time": self.last_update_time,
            "model_info": self.model.get_model_info()
        }
        
        torch.save(state, filepath)
        print(f"Client {self.client_id}: State saved to {filepath}")
    
    def load_client_state(self, filepath: str):
        """Load client state from file."""
        if os.path.exists(filepath):
            state = torch.load(filepath, map_location='cpu')
            self.model.load_state_dict(state["model_state_dict"])
            self.training_history = state.get("training_history", [])
            self.last_accuracy = state.get("last_accuracy", 0.0)
            self.last_update_time = state.get("last_update_time")
            print(f"Client {self.client_id}: State loaded from {filepath}")
        else:
            print(f"Client {self.client_id}: No saved state found at {filepath}")

class SimulatedClient:
    """
    Simulated client for demonstration purposes.
    Generates synthetic updates without actual training.
    """
    
    def __init__(self, client_id: str, base_accuracy: float = 0.8):
        self.client_id = client_id
        self.base_accuracy = base_accuracy
        self.current_accuracy = base_accuracy
        self.update_count = 0
    
    def simulate_training(self) -> Dict[str, Any]:
        """Simulate local training."""
        # Simulate accuracy improvement with some randomness
        improvement = np.random.uniform(0.01, 0.05)
        noise = np.random.uniform(-0.02, 0.02)
        self.current_accuracy = min(0.99, self.current_accuracy + improvement + noise)
        
        # Simulate sample count
        samples = np.random.randint(100, 1000)
        
        self.update_count += 1
        
        return {
            "client_id": self.client_id,
            "accuracy": self.current_accuracy,
            "samples": samples,
            "update_count": self.update_count,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_weights(self, model: torch.nn.Module) -> List[torch.Tensor]:
        """Get simulated model weights with some noise."""
        weights = []
        for param in model.parameters():
            noise = torch.randn_like(param) * 0.01
            weights.append(param + noise)
        return weights

def create_federated_clients(n_clients: int = 3, 
                           data_dir: str = "data",
                           model_template: HybridCNNLSTM = None,
                           preprocessor: NetworkFlowPreprocessor = None) -> List[FederatedClient]:
    """
    Create multiple federated clients.
    
    Args:
        n_clients: Number of clients to create
        data_dir: Directory containing client data files
        model_template: Template model for clients
        preprocessor: Data preprocessor
        
    Returns:
        List of federated clients
    """
    clients = []
    
    for i in range(1, n_clients + 1):
        client_id = f"client_{i}"
        data_path = os.path.join(data_dir, f"{client_id}_data.csv")
        
        # Create a copy of the model for each client
        if model_template is not None:
            client_model = create_model(
                input_size=model_template.input_size,
                sequence_length=model_template.sequence_length,
                n_classes=model_template.n_classes
            )
            # Copy weights from template
            client_model.load_state_dict(model_template.state_dict())
        else:
            client_model = None
        
        client = FederatedClient(
            client_id=client_id,
            model=client_model,
            preprocessor=preprocessor,
            data_path=data_path
        )
        
        clients.append(client)
    
    return clients

if __name__ == "__main__":
    # Test the federated client
    print("Testing FederatedClient...")
    
    # Create a simple test
    client = SimulatedClient("test_client", base_accuracy=0.8)
    
    for i in range(5):
        result = client.simulate_training()
        print(f"Round {i+1}: {result}")
