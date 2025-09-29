#!/usr/bin/env python3
"""
Simplified demo script for AI-Driven IDS.
This script demonstrates the basic functionality without complex training.
"""

import os
import sys
import time
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.generate_sample_data import save_datasets
from models.hybrid_model import create_model
from models.preprocessing import NetworkFlowPreprocessor

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_step(step, description):
    """Print a formatted step."""
    print(f"\n[Step {step}] {description}")
    print("-" * 40)

def test_model_creation():
    """Test model creation and basic functionality."""
    print_step(1, "Testing Model Creation")
    
    try:
        # Create a simple model
        model = create_model(
            input_size=41,  # Standard network flow features
            sequence_length=10,
            n_classes=5
        )
        
        print(f"✓ Model created successfully!")
        print(f"  Parameters: {sum(p.numel() for p in model.parameters()):,}")
        print(f"  Input size: 41 features")
        print(f"  Sequence length: 10")
        print(f"  Output classes: 5")
        
        # Test forward pass
        import torch
        sample_input = torch.randn(1, 10, 41)
        output = model(sample_input)
        
        print(f"✓ Forward pass successful!")
        print(f"  Input shape: {sample_input.shape}")
        print(f"  Output shape: {output.shape}")
        
        return True
        
    except Exception as e:
        print(f"✗ Model creation failed: {e}")
        return False

def test_data_generation():
    """Test data generation."""
    print_step(2, "Testing Data Generation")
    
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
    print_step(3, "Testing Data Preprocessing")
    
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
        
        return True
        
    except Exception as e:
        print(f"✗ Preprocessing failed: {e}")
        return False

def test_inference_simulation():
    """Test inference simulation."""
    print_step(4, "Testing Inference Simulation")
    
    try:
        import torch
        
        # Create model
        model = create_model(input_size=41, sequence_length=10, n_classes=5)
        
        # Create sample data
        sample_data = torch.randn(5, 10, 41)  # 5 samples, 10 timesteps, 41 features
        
        # Make predictions
        model.eval()
        with torch.no_grad():
            output = model(sample_data)
            predictions = torch.argmax(output, dim=1)
            confidence = torch.max(torch.softmax(output, dim=1), dim=1)[0]
        
        print(f"✓ Inference simulation successful!")
        print(f"  Sample predictions: {predictions.tolist()}")
        print(f"  Confidence scores: {[f'{c:.3f}' for c in confidence.tolist()]}")
        
        return True
        
    except Exception as e:
        print(f"✗ Inference simulation failed: {e}")
        return False

def test_backend_connection():
    """Test backend connection if available."""
    print_step(5, "Testing Backend Connection")
    
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

def run_simple_demo():
    """Run the simplified demo."""
    print_header("AI-Driven IDS Simple Demo")
    print("This demo tests the core components without complex training.")
    
    success = True
    success &= test_model_creation()
    success &= test_data_generation()
    success &= test_preprocessing()
    success &= test_inference_simulation()
    success &= test_backend_connection()
    
    return success

def main():
    """Main demo function."""
    print_header("AI-Driven IDS Simple Demo")
    print("Testing core functionality of the AI-Driven IDS system.")
    
    success = run_simple_demo()
    
    # Final summary
    print_header("Demo Summary")
    if success:
        print("🎉 All core components are working correctly!")
        print("\nNext steps:")
        print("1. Start the full system: docker-compose up")
        print("2. Access the web interface: http://localhost:3000")
        print("3. View API documentation: http://localhost:8000/docs")
        print("4. Run the full demo: python demo_script.py")
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
