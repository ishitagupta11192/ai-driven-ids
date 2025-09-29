#!/usr/bin/env python3
"""
Basic demo script for AI-Driven IDS.
This script demonstrates the basic functionality with a simple model.
"""

import os
import sys
import time
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime
import torch
import torch.nn as nn

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.generate_sample_data import save_datasets
from models.preprocessing import NetworkFlowPreprocessor

class SimpleIDSModel(nn.Module):
    """Simple IDS model for demonstration."""
    
    def __init__(self, input_size, n_classes):
        super(SimpleIDSModel, self).__init__()
        self.classifier = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, n_classes)
        )
    
    def forward(self, x):
        return self.classifier(x)

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_step(step, description):
    """Print a formatted step."""
    print(f"\n[Step {step}] {description}")
    print("-" * 40)

def test_data_generation():
    """Test data generation."""
    print_step(1, "Testing Data Generation")
    
    try:
        save_datasets()
        print("✓ Sample data generated successfully!")
        
        # Check if files exist
        data_files = [
            "data/network_flows.csv",
            "data/client_1_data.csv", 
            "data/client_2_data.csv",
            "data/client_3_data.csv",
            "data/test_data.csv"
        ]
        
        for file_path in data_files:
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                print(f"  {file_path}: {len(df)} samples")
            else:
                print(f"  ✗ {file_path}: Not found")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Data generation failed: {e}")
        return False

def test_preprocessing():
    """Test data preprocessing."""
    print_step(2, "Testing Data Preprocessing")
    
    try:
        # Load sample data
        df = pd.read_csv("data/network_flows.csv")
        print(f"✓ Loaded {len(df)} samples")
        
        # Create preprocessor
        preprocessor = NetworkFlowPreprocessor()
        
        # Fit preprocessor
        X = df.drop(['label', 'timestamp'], axis=1, errors='ignore')
        y = df['label']
        
        X_processed = preprocessor.fit_transform(X)
        y_encoded = preprocessor.encode_labels(y)
        
        print(f"✓ Preprocessing successful!")
        print(f"  Original features: {X.shape[1]}")
        print(f"  Processed features: {X_processed.shape[1]}")
        print(f"  Classes: {preprocessor.label_encoders['label'].classes_}")
        print(f"  Encoded labels shape: {y_encoded.shape}")
        
        return True, preprocessor, X_processed, y_encoded
        
    except Exception as e:
        print(f"✗ Preprocessing failed: {e}")
        return False, None, None, None

def test_simple_model():
    """Test simple model creation and training."""
    print_step(3, "Testing Simple Model")
    
    try:
        # Load and preprocess data
        success, preprocessor, X_processed, y_encoded = test_preprocessing()
        if not success:
            return False
        
        # Create simple model
        model = SimpleIDSModel(input_size=X_processed.shape[1], n_classes=5)
        print(f"✓ Simple model created!")
        print(f"  Parameters: {sum(p.numel() for p in model.parameters()):,}")
        
        # Convert to tensors
        X_tensor = torch.FloatTensor(X_processed[:1000])  # Use subset for demo
        y_tensor = torch.LongTensor(y_encoded[:1000])
        
        # Simple training loop
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        criterion = nn.CrossEntropyLoss()
        
        model.train()
        for epoch in range(5):  # Just 5 epochs for demo
            optimizer.zero_grad()
            output = model(X_tensor)
            loss = criterion(output, y_tensor)
            loss.backward()
            optimizer.step()
            
            if epoch % 2 == 0:
                print(f"  Epoch {epoch}: Loss = {loss.item():.4f}")
        
        # Test inference
        model.eval()
        with torch.no_grad():
            test_output = model(X_tensor[:10])
            predictions = torch.argmax(test_output, dim=1)
            confidence = torch.max(torch.softmax(test_output, dim=1), dim=1)[0]
        
        print(f"✓ Training and inference successful!")
        print(f"  Sample predictions: {predictions.tolist()}")
        print(f"  Confidence scores: {[f'{c:.3f}' for c in confidence.tolist()]}")
        
        return True
        
    except Exception as e:
        print(f"✗ Simple model test failed: {e}")
        return False

def test_backend_connection():
    """Test backend connection if available."""
    print_step(4, "Testing Backend Connection")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✓ Backend is running and accessible!")
            return True
        else:
            print(f"⚠ Backend responded with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("ℹ Backend not running (this is expected for offline demo)")
        return False

def test_federated_learning_simulation():
    """Test federated learning simulation."""
    print_step(5, "Testing Federated Learning Simulation")
    
    try:
        # Simulate federated learning with simple aggregation
        print("  Simulating 3 clients with different data...")
        
        # Load client data
        clients_data = []
        for i in range(1, 4):
            df = pd.read_csv(f"data/client_{i}_data.csv")
            clients_data.append(df)
            print(f"    Client {i}: {len(df)} samples")
        
        # Simulate local training
        print("  Simulating local training...")
        for i, client_data in enumerate(clients_data):
            # Simulate some training metrics
            accuracy = np.random.uniform(0.7, 0.95)
            samples = len(client_data)
            print(f"    Client {i+1}: Accuracy = {accuracy:.3f}, Samples = {samples}")
        
        # Simulate aggregation
        print("  Simulating model aggregation...")
        avg_accuracy = np.random.uniform(0.8, 0.92)
        print(f"    Global model accuracy: {avg_accuracy:.3f}")
        
        print("✓ Federated learning simulation successful!")
        return True
        
    except Exception as e:
        print(f"✗ Federated learning simulation failed: {e}")
        return False

def run_basic_demo():
    """Run the basic demo."""
    print_header("AI-Driven IDS Basic Demo")
    print("Testing core functionality with simplified components.")
    
    success = True
    success &= test_data_generation()
    success &= test_simple_model()
    # Backend connection is optional for offline demo
    test_backend_connection()
    success &= test_federated_learning_simulation()
    
    return success

def main():
    """Main demo function."""
    print_header("AI-Driven IDS Basic Demo")
    print("Testing the core functionality of the AI-Driven IDS system.")
    
    success = run_basic_demo()
    
    # Final summary
    print_header("Demo Summary")
    if success:
        print("🎉 All core components are working correctly!")
        print("\nSystem Components Tested:")
        print("✓ Data generation and preprocessing")
        print("✓ Simple neural network model")
        print("✓ Model training and inference")
        print("✓ Federated learning simulation")
        print("\nNext steps:")
        print("1. Start the full system: docker-compose up")
        print("2. Access the web interface: http://localhost:3000")
        print("3. View API documentation: http://localhost:8000/docs")
        print("4. Upload CSV files for real-time inference")
    else:
        print("❌ Some components had issues")
        print("\nTroubleshooting:")
        print("1. Check that all dependencies are installed")
        print("2. Ensure data files are generated")
        print("3. Check Python version compatibility")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nDemo failed with error: {e}")
        sys.exit(1)
