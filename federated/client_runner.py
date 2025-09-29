"""
Client runner for federated learning.
Simulates client behavior in the federated learning setup.
"""

import argparse
import time
import requests
import torch
import numpy as np
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.hybrid_model import create_model
from models.preprocessing import NetworkFlowPreprocessor, create_sequences
from federated.client import FederatedClient, SimulatedClient

class FederatedClientRunner:
    """Runner for federated learning clients."""
    
    def __init__(self, client_id: str, data_path: str, coordinator_url: str = "http://localhost:8000"):
        self.client_id = client_id
        self.data_path = data_path
        self.coordinator_url = coordinator_url
        self.client = None
        self.running = False
        
    def initialize_client(self):
        """Initialize the federated client."""
        try:
            # Load data to get model parameters
            if os.path.exists(self.data_path):
                df = pd.read_csv(self.data_path)
                print(f"Client {self.client_id}: Loaded {len(df)} samples from {self.data_path}")
                
                # Create preprocessor
                preprocessor = NetworkFlowPreprocessor()
                preprocessor.fit(df)
                
                # Create model
                X = df.drop(['label', 'timestamp'], axis=1, errors='ignore')
                X_processed = preprocessor.fit_transform(X)
                
                model = create_model(
                    input_size=X_processed.shape[1],
                    sequence_length=10,
                    n_classes=len(preprocessor.label_encoders['label'].classes_)
                )
                
                # Create federated client
                self.client = FederatedClient(
                    client_id=self.client_id,
                    model=model,
                    preprocessor=preprocessor,
                    data_path=self.data_path
                )
                
                print(f"Client {self.client_id}: Initialized successfully")
                return True
            else:
                print(f"Client {self.client_id}: Data file not found at {self.data_path}")
                return False
                
        except Exception as e:
            print(f"Client {self.client_id}: Error initializing: {e}")
            return False
    
    def register_with_coordinator(self):
        """Register this client with the coordinator."""
        try:
            response = requests.post(
                f"{self.coordinator_url}/register-client",
                json={
                    "client_id": self.client_id,
                    "info": {
                        "data_path": self.data_path,
                        "samples": len(pd.read_csv(self.data_path)) if os.path.exists(self.data_path) else 0
                    }
                }
            )
            
            if response.status_code == 200:
                print(f"Client {self.client_id}: Registered with coordinator")
                return True
            else:
                print(f"Client {self.client_id}: Failed to register: {response.text}")
                return False
                
        except Exception as e:
            print(f"Client {self.client_id}: Error registering: {e}")
            return False
    
    def train_and_update(self):
        """Train locally and send update to coordinator."""
        if not self.client:
            print(f"Client {self.client_id}: Not initialized")
            return False
        
        try:
            # Train local model
            print(f"Client {self.client_id}: Starting local training...")
            result = self.client.train_local_model()
            
            if result['success']:
                # Get model weights
                weights = self.client.get_model_weights()
                
                # Convert weights to serializable format
                weights_serializable = [w.tolist() for w in weights]
                
                # Send update to coordinator
                update_data = {
                    "client_id": self.client_id,
                    "weights": weights_serializable,
                    "accuracy": result['accuracy'],
                    "samples": result['samples']
                }
                
                response = requests.post(
                    f"{self.coordinator_url}/client-update",
                    json=update_data
                )
                
                if response.status_code == 200:
                    print(f"Client {self.client_id}: Update sent successfully")
                    return True
                else:
                    print(f"Client {self.client_id}: Failed to send update: {response.text}")
                    return False
            else:
                print(f"Client {self.client_id}: Local training failed: {result['message']}")
                return False
                
        except Exception as e:
            print(f"Client {self.client_id}: Error in train_and_update: {e}")
            return False
    
    def get_global_model(self):
        """Get updated global model from coordinator."""
        try:
            response = requests.get(f"{self.coordinator_url}/global-model")
            
            if response.status_code == 200:
                global_weights = response.json()['weights']
                # Convert back to tensors
                weights_tensors = [torch.FloatTensor(w) for w in global_weights]
                
                if self.client:
                    self.client.update_model_weights(weights_tensors)
                    print(f"Client {self.client_id}: Updated with global model")
                    return True
            else:
                print(f"Client {self.client_id}: Failed to get global model: {response.text}")
                return False
                
        except Exception as e:
            print(f"Client {self.client_id}: Error getting global model: {e}")
            return False
    
    def run_simulation(self, rounds: int = 5, interval: int = 30):
        """Run client simulation for specified rounds."""
        print(f"Client {self.client_id}: Starting simulation for {rounds} rounds")
        self.running = True
        
        for round_num in range(1, rounds + 1):
            if not self.running:
                break
                
            print(f"\nClient {self.client_id}: Round {round_num}/{rounds}")
            
            # Train and send update
            if self.train_and_update():
                print(f"Client {self.client_id}: Round {round_num} completed")
            else:
                print(f"Client {self.client_id}: Round {round_num} failed")
            
            # Wait for next round
            if round_num < rounds:
                print(f"Client {self.client_id}: Waiting {interval} seconds for next round...")
                time.sleep(interval)
        
        print(f"Client {self.client_id}: Simulation completed")
    
    def stop(self):
        """Stop the client runner."""
        self.running = False
        print(f"Client {self.client_id}: Stopped")

def main():
    parser = argparse.ArgumentParser(description='Federated Learning Client Runner')
    parser.add_argument('--client-id', required=True, help='Client identifier')
    parser.add_argument('--data-path', required=True, help='Path to client data CSV')
    parser.add_argument('--coordinator-url', default='http://localhost:8000',
                       help='Coordinator URL')
    parser.add_argument('--rounds', type=int, default=5,
                       help='Number of training rounds')
    parser.add_argument('--interval', type=int, default=30,
                       help='Interval between rounds (seconds)')
    parser.add_argument('--mode', choices=['simulation', 'interactive'], 
                       default='simulation', help='Client mode')
    
    args = parser.parse_args()
    
    # Create client runner
    runner = FederatedClientRunner(
        client_id=args.client_id,
        data_path=args.data_path,
        coordinator_url=args.coordinator_url
    )
    
    # Initialize client
    if not runner.initialize_client():
        print(f"Failed to initialize client {args.client_id}")
        return
    
    # Register with coordinator
    if not runner.register_with_coordinator():
        print(f"Failed to register client {args.client_id}")
        return
    
    try:
        if args.mode == 'simulation':
            # Run simulation
            runner.run_simulation(rounds=args.rounds, interval=args.interval)
        else:
            # Interactive mode
            print(f"Client {args.client_id}: Running in interactive mode")
            print("Commands: train, stop, quit")
            
            while True:
                command = input(f"Client {args.client_id}> ").strip().lower()
                
                if command == 'train':
                    runner.train_and_update()
                elif command == 'stop':
                    runner.stop()
                    break
                elif command == 'quit':
                    break
                else:
                    print("Unknown command. Available: train, stop, quit")
    
    except KeyboardInterrupt:
        print(f"\nClient {args.client_id}: Interrupted by user")
        runner.stop()
    except Exception as e:
        print(f"Client {args.client_id}: Error: {e}")
        runner.stop()

if __name__ == "__main__":
    main()
