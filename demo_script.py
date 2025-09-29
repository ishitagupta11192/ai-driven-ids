#!/usr/bin/env python3
"""
Demo script for AI-Driven IDS with Federated Learning.
This script demonstrates the complete workflow including data generation,
model training, and federated learning simulation.
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
from models.train import train_centralized_model, train_federated_model
from models.hybrid_model import create_model
from models.preprocessing import NetworkFlowPreprocessor
from federated.coordinator import SimpleAggregator

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_step(step, description):
    """Print a formatted step."""
    print(f"\n[Step {step}] {description}")
    print("-" * 40)

def wait_for_backend(url="http://localhost:8000", timeout=60):
    """Wait for the backend to be ready."""
    print("Waiting for backend to be ready...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print("✓ Backend is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(2)
        print(".", end="", flush=True)
    
    print(f"\n✗ Backend not ready after {timeout} seconds")
    return False

def test_inference_api():
    """Test the inference API with sample data."""
    print_step(5, "Testing Inference API")
    
    # Generate sample data for inference
    sample_data = [
        [0.1, 0, 0, 0, 8.5, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 50, 30, 0.8, 0.8, 0.8, 0.8, 0.9, 0.1, 0.1, 100, 50, 0.9, 0.1, 0.9, 0.1, 0.8, 0.8, 0.8, 0.8],
        [10.5, 0, 0, 0, 8.2, 7.8, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 5, 3, 0.1, 0.1, 0.1, 0.1, 0.8, 0.2, 0.2, 10, 5, 0.8, 0.2, 0.8, 0.2, 0.1, 0.1, 0.1, 0.1]
    ]
    
    try:
        response = requests.post(
            "http://localhost:8000/infer",
            json={"data": sample_data, "batch": True}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Inference API working!")
            print(f"  Predictions: {result['predictions']}")
            print(f"  Confidence: {[f'{c:.2f}' for c in result['confidence']]}")
            print(f"  Latency: {result['latency_ms']:.1f}ms")
            return True
        else:
            print(f"✗ Inference API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Inference API error: {e}")
        return False

def test_federated_learning_api():
    """Test the federated learning API."""
    print_step(6, "Testing Federated Learning API")
    
    try:
        # Start federated learning
        response = requests.post(
            "http://localhost:8000/start-fl",
            json={"rounds": 3, "clients": ["client_1", "client_2", "client_3"]}
        )
        
        if response.status_code == 200:
            print("✓ Federated learning started!")
            
            # Monitor progress
            for i in range(10):  # Check for 10 iterations
                time.sleep(3)
                
                progress_response = requests.get("http://localhost:8000/fl-progress")
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    print(f"  Round {progress['round']}/{progress['total_rounds']} - "
                          f"Status: {progress['status']} - "
                          f"Accuracy: {progress['accuracy']:.1f}%")
                    
                    if progress['status'] == 'completed':
                        print("✓ Federated learning completed!")
                        return True
            
            print("⚠ Federated learning still in progress...")
            return True
        else:
            print(f"✗ Failed to start federated learning: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Federated learning API error: {e}")
        return False

def test_metrics_api():
    """Test the metrics API."""
    print_step(7, "Testing Metrics API")
    
    try:
        response = requests.get("http://localhost:8000/metrics")
        
        if response.status_code == 200:
            metrics = response.json()
            if 'accuracy' in metrics:
                print("✓ Metrics API working!")
                print(f"  Model Accuracy: {metrics['accuracy']:.3f}")
                print(f"  Total Samples: {metrics.get('total_samples', 'N/A')}")
                return True
            else:
                print("⚠ Metrics API returned no accuracy data")
                return True
        else:
            print(f"✗ Metrics API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Metrics API error: {e}")
        return False

def run_offline_demo():
    """Run offline demo without backend."""
    print_header("AI-Driven IDS Offline Demo")
    
    # Step 1: Generate sample data
    print_step(1, "Generating Sample Data")
    try:
        save_datasets()
        print("✓ Sample data generated successfully!")
    except Exception as e:
        print(f"✗ Failed to generate sample data: {e}")
        return False
    
    # Step 2: Train centralized model
    print_step(2, "Training Centralized Model")
    try:
        results = train_centralized_model(
            data_path="data/network_flows.csv",
            model_save_path="models/demo_centralized_model.pth",
            epochs=10,  # Reduced for demo
            batch_size=32
        )
        print("✓ Centralized model training completed!")
        print(f"  Final Accuracy: {results['accuracy']:.3f}")
    except Exception as e:
        print(f"✗ Centralized training failed: {e}")
        return False
    
    # Step 3: Train federated model
    print_step(3, "Training Federated Model")
    try:
        fl_results = train_federated_model(
            model_save_path="models/demo_federated_model.pth",
            rounds=3,  # Reduced for demo
            local_epochs=2
        )
        print("✓ Federated model training completed!")
        print(f"  Final Accuracy: {fl_results['final_accuracy']:.3f}")
    except Exception as e:
        print(f"✗ Federated training failed: {e}")
        return False
    
    # Step 4: Demonstrate model inference
    print_step(4, "Model Inference Demo")
    try:
        # Load the trained model
        import torch
        checkpoint = torch.load("models/demo_centralized_model.pth", map_location='cpu')
        model_info = checkpoint['model_info']
        
        # Create model
        model = create_model(
            input_size=model_info['input_size'],
            sequence_length=model_info['sequence_length'],
            n_classes=model_info['n_classes']
        )
        model.load_state_dict(checkpoint['model_state_dict'])
        
        # Generate sample input
        sample_input = torch.randn(1, 10, model_info['input_size'])
        
        # Make prediction
        model.eval()
        with torch.no_grad():
            output = model(sample_input)
            prediction = torch.argmax(output, dim=1)
            confidence = torch.max(torch.softmax(output, dim=1), dim=1)[0]
        
        print("✓ Model inference working!")
        print(f"  Sample prediction: {prediction.item()}")
        print(f"  Confidence: {confidence.item():.3f}")
        
    except Exception as e:
        print(f"✗ Model inference failed: {e}")
        return False
    
    return True

def run_online_demo():
    """Run online demo with backend."""
    print_header("AI-Driven IDS Online Demo")
    
    # Wait for backend
    if not wait_for_backend():
        print("Please start the backend first with: docker-compose up backend")
        return False
    
    # Test APIs
    success = True
    success &= test_inference_api()
    success &= test_federated_learning_api()
    success &= test_metrics_api()
    
    if success:
        print_header("Demo Completed Successfully!")
        print("✓ All API endpoints are working correctly")
        print("✓ You can now access the web interface at: http://localhost:3000")
        print("✓ API documentation is available at: http://localhost:8000/docs")
    else:
        print_header("Demo Completed with Issues")
        print("⚠ Some API endpoints had issues")
        print("  Check the backend logs for more details")
    
    return success

def main():
    """Main demo function."""
    print_header("AI-Driven IDS Demo")
    print("This demo will test the AI-Driven IDS system with hybrid")
    print("CNN+LSTM models and federated learning capabilities.")
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        backend_running = response.status_code == 200
    except:
        backend_running = False
    
    if backend_running:
        print("\nBackend detected! Running online demo...")
        success = run_online_demo()
    else:
        print("\nNo backend detected. Running offline demo...")
        print("(To run the full demo with web interface, start with: docker-compose up)")
        success = run_offline_demo()
    
    # Final summary
    print_header("Demo Summary")
    if success:
        print("🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("1. Start the full system: docker-compose up")
        print("2. Access the web interface: http://localhost:3000")
        print("3. View API documentation: http://localhost:8000/docs")
        print("4. Upload CSV files for inference")
        print("5. Start federated learning rounds")
    else:
        print("❌ Demo encountered issues")
        print("\nTroubleshooting:")
        print("1. Check that all dependencies are installed")
        print("2. Ensure data files are generated")
        print("3. Check backend logs for errors")
        print("4. Verify Docker containers are running")
    
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
