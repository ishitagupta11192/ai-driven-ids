"""
Federated Learning Coordinator for AI-Driven IDS.
Manages the federated learning process and aggregates client updates.
"""

import torch
import numpy as np
from typing import Dict, List, Any, Optional
import json
import time
from datetime import datetime
import copy

class FederatedCoordinator:
    """
    Coordinator for federated learning.
    Manages client updates and performs model aggregation.
    """
    
    def __init__(self, 
                 global_model: torch.nn.Module,
                 preprocessor: Any,
                 aggregation_method: str = "fedavg"):
        """
        Initialize the coordinator.
        
        Args:
            global_model: The global model to be trained
            preprocessor: Data preprocessor
            aggregation_method: Method for aggregating client updates
        """
        self.global_model = global_model
        self.preprocessor = preprocessor
        self.aggregation_method = aggregation_method
        
        # Client management
        self.clients = {}
        self.client_updates = {}
        self.round_history = []
        
        # Training configuration
        self.current_round = 0
        self.total_rounds = 0
        self.min_clients = 2
        self.max_clients = 10
        
    def add_client(self, client_id: str, client_info: Dict[str, Any]):
        """Add a new client to the federation."""
        self.clients[client_id] = {
            "id": client_id,
            "info": client_info,
            "last_update": None,
            "accuracy": 0.0,
            "samples": 0,
            "active": True
        }
        print(f"Added client: {client_id}")
    
    def remove_client(self, client_id: str):
        """Remove a client from the federation."""
        if client_id in self.clients:
            del self.clients[client_id]
            if client_id in self.client_updates:
                del self.client_updates[client_id]
            print(f"Removed client: {client_id}")
    
    def update_client(self, 
                     client_id: str, 
                     weights: List[torch.Tensor],
                     accuracy: float,
                     samples: int):
        """
        Receive client model update.
        
        Args:
            client_id: Client identifier
            weights: Updated model weights
            accuracy: Client model accuracy
            samples: Number of training samples used
        """
        if client_id not in self.clients:
            self.add_client(client_id, {})
        
        # Store client update
        self.client_updates[client_id] = {
            "weights": weights,
            "accuracy": accuracy,
            "samples": samples,
            "timestamp": datetime.now().isoformat()
        }
        
        # Update client info
        self.clients[client_id]["last_update"] = datetime.now().isoformat()
        self.clients[client_id]["accuracy"] = accuracy
        self.clients[client_id]["samples"] = samples
        
        print(f"Received update from client {client_id}: accuracy={accuracy:.3f}, samples={samples}")
    
    def can_aggregate(self) -> bool:
        """Check if enough clients have provided updates for aggregation."""
        active_clients = [c for c in self.clients.values() if c["active"]]
        updates_received = len(self.client_updates)
        
        return (len(active_clients) >= self.min_clients and 
                updates_received >= self.min_clients)
    
    def aggregate_weights(self) -> Dict[str, torch.Tensor]:
        """
        Aggregate client weights using the specified method.
        
        Returns:
            Dictionary of aggregated weights
        """
        if not self.can_aggregate():
            raise ValueError("Not enough client updates for aggregation")
        
        if self.aggregation_method == "fedavg":
            return self._fedavg_aggregation()
        elif self.aggregation_method == "weighted_avg":
            return self._weighted_avg_aggregation()
        else:
            raise ValueError(f"Unknown aggregation method: {self.aggregation_method}")
    
    def _fedavg_aggregation(self) -> Dict[str, torch.Tensor]:
        """Federated Averaging aggregation."""
        # Get global model state dict
        global_state = self.global_model.state_dict()
        aggregated_state = copy.deepcopy(global_state)
        
        # Initialize aggregated weights
        for key in aggregated_state.keys():
            aggregated_state[key] = torch.zeros_like(aggregated_state[key])
        
        # Calculate total samples
        total_samples = sum(update["samples"] for update in self.client_updates.values())
        
        # Weighted average of client updates
        for client_id, update in self.client_updates.items():
            client_weights = update["weights"]
            client_samples = update["samples"]
            weight = client_samples / total_samples
            
            # Convert client weights to state dict format
            client_state = self._weights_to_state_dict(client_weights)
            
            # Add weighted client weights
            for key in aggregated_state.keys():
                if key in client_state:
                    aggregated_state[key] += weight * client_state[key]
        
        return aggregated_state
    
    def _weighted_avg_aggregation(self) -> Dict[str, torch.Tensor]:
        """Accuracy-weighted aggregation."""
        # Get global model state dict
        global_state = self.global_model.state_dict()
        aggregated_state = copy.deepcopy(global_state)
        
        # Initialize aggregated weights
        for key in aggregated_state.keys():
            aggregated_state[key] = torch.zeros_like(aggregated_state[key])
        
        # Calculate total accuracy weight
        total_accuracy_weight = sum(update["accuracy"] for update in self.client_updates.values())
        
        # Accuracy-weighted average
        for client_id, update in self.client_updates.items():
            client_weights = update["weights"]
            client_accuracy = update["accuracy"]
            weight = client_accuracy / total_accuracy_weight
            
            # Convert client weights to state dict format
            client_state = self._weights_to_state_dict(client_weights)
            
            # Add weighted client weights
            for key in aggregated_state.keys():
                if key in client_state:
                    aggregated_state[key] += weight * client_state[key]
        
        return aggregated_state
    
    def _weights_to_state_dict(self, weights: List[torch.Tensor]) -> Dict[str, torch.Tensor]:
        """Convert list of weights to state dict format."""
        state_dict = {}
        param_idx = 0
        
        for name, param in self.global_model.named_parameters():
            if param_idx < len(weights):
                state_dict[name] = weights[param_idx]
                param_idx += 1
        
        return state_dict
    
    def update_global_model(self, aggregated_weights: Dict[str, torch.Tensor]):
        """Update the global model with aggregated weights."""
        self.global_model.load_state_dict(aggregated_weights)
        print("Global model updated with aggregated weights")
    
    def run_federated_round(self) -> Dict[str, Any]:
        """
        Run one federated learning round.
        
        Returns:
            Round results dictionary
        """
        if not self.can_aggregate():
            return {
                "success": False,
                "message": "Not enough client updates for aggregation",
                "clients_updated": len(self.client_updates),
                "min_clients": self.min_clients
            }
        
        # Aggregate weights
        aggregated_weights = self.aggregate_weights()
        
        # Update global model
        self.update_global_model(aggregated_weights)
        
        # Calculate round statistics
        client_accuracies = [update["accuracy"] for update in self.client_updates.values()]
        client_samples = [update["samples"] for update in self.client_updates.values()]
        
        round_stats = {
            "round": self.current_round,
            "timestamp": datetime.now().isoformat(),
            "clients_participated": len(self.client_updates),
            "avg_accuracy": np.mean(client_accuracies),
            "max_accuracy": np.max(client_accuracies),
            "min_accuracy": np.min(client_accuracies),
            "total_samples": sum(client_samples),
            "client_details": {
                client_id: {
                    "accuracy": update["accuracy"],
                    "samples": update["samples"]
                }
                for client_id, update in self.client_updates.items()
            }
        }
        
        # Store round history
        self.round_history.append(round_stats)
        
        # Clear client updates for next round
        self.client_updates.clear()
        
        # Increment round
        self.current_round += 1
        
        print(f"Federated round {self.current_round - 1} completed")
        print(f"Average client accuracy: {round_stats['avg_accuracy']:.3f}")
        
        return {
            "success": True,
            "round_stats": round_stats
        }
    
    def get_round_history(self) -> List[Dict[str, Any]]:
        """Get the history of federated learning rounds."""
        return self.round_history
    
    def get_client_status(self) -> Dict[str, Any]:
        """Get current status of all clients."""
        return {
            "total_clients": len(self.clients),
            "active_clients": len([c for c in self.clients.values() if c["active"]]),
            "clients_with_updates": len(self.client_updates),
            "current_round": self.current_round,
            "clients": self.clients
        }
    
    def save_model(self, filepath: str):
        """Save the current global model."""
        torch.save({
            "model_state_dict": self.global_model.state_dict(),
            "round_history": self.round_history,
            "current_round": self.current_round,
            "clients": self.clients
        }, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a previously saved global model."""
        checkpoint = torch.load(filepath, map_location='cpu')
        self.global_model.load_state_dict(checkpoint["model_state_dict"])
        self.round_history = checkpoint.get("round_history", [])
        self.current_round = checkpoint.get("current_round", 0)
        self.clients = checkpoint.get("clients", {})
        print(f"Model loaded from {filepath}")
    
    def get_aggregation_metrics(self) -> Dict[str, Any]:
        """Get metrics about the aggregation process."""
        if not self.client_updates:
            return {"message": "No client updates available"}
        
        accuracies = [update["accuracy"] for update in self.client_updates.values()]
        samples = [update["samples"] for update in self.client_updates.values()]
        
        return {
            "num_clients": len(self.client_updates),
            "accuracy_stats": {
                "mean": np.mean(accuracies),
                "std": np.std(accuracies),
                "min": np.min(accuracies),
                "max": np.max(accuracies)
            },
            "sample_stats": {
                "total": sum(samples),
                "mean": np.mean(samples),
                "std": np.std(samples),
                "min": np.min(samples),
                "max": np.max(samples)
            },
            "aggregation_method": self.aggregation_method
        }

class SimpleAggregator:
    """
    Simplified aggregator for demonstration purposes.
    Simulates federated learning without actual client communication.
    """
    
    def __init__(self, model: torch.nn.Module, n_clients: int = 3):
        self.model = model
        self.n_clients = n_clients
        self.round_history = []
        self.current_round = 0
    
    def simulate_round(self) -> Dict[str, Any]:
        """Simulate one federated learning round."""
        # Simulate client updates
        client_updates = []
        for i in range(self.n_clients):
            # Simulate client training with some noise
            client_weights = []
            for param in self.model.parameters():
                noise = torch.randn_like(param) * 0.01
                client_weights.append(param + noise)
            
            client_accuracy = np.random.uniform(0.7, 0.95)
            client_samples = np.random.randint(100, 1000)
            
            client_updates.append({
                "weights": client_weights,
                "accuracy": client_accuracy,
                "samples": client_samples
            })
        
        # Simple averaging
        aggregated_weights = []
        for i, param in enumerate(self.model.parameters()):
            avg_weight = torch.zeros_like(param)
            for update in client_updates:
                avg_weight += update["weights"][i]
            avg_weight /= len(client_updates)
            aggregated_weights.append(avg_weight)
        
        # Update model
        with torch.no_grad():
            for param, new_weight in zip(self.model.parameters(), aggregated_weights):
                param.copy_(new_weight)
        
        # Calculate statistics
        avg_accuracy = np.mean([u["accuracy"] for u in client_updates])
        total_samples = sum([u["samples"] for u in client_updates])
        
        round_stats = {
            "round": self.current_round,
            "avg_accuracy": avg_accuracy,
            "total_samples": total_samples,
            "clients": len(client_updates)
        }
        
        self.round_history.append(round_stats)
        self.current_round += 1
        
        return round_stats
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get simulation history."""
        return self.round_history
