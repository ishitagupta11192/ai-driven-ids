"""
Training script for the hybrid CNN+LSTM model.
Supports both centralized and federated learning modes.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import pandas as pd
import argparse
import os
import json
from datetime import datetime
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

from .hybrid_model import HybridCNNLSTM, ModelTrainer, create_model
from .preprocessing import prepare_data_for_training, load_and_preprocess_data

def train_centralized_model(data_path: str, 
                          model_save_path: str = "models/trained_model.pth",
                          preprocessor_save_path: str = "models/preprocessor.pkl",
                          epochs: int = 50,
                          batch_size: int = 32,
                          learning_rate: float = 0.001,
                          test_size: float = 0.2):
    """
    Train the model in centralized mode.
    
    Args:
        data_path: Path to training data CSV
        model_save_path: Path to save trained model
        preprocessor_save_path: Path to save preprocessor
        epochs: Number of training epochs
        batch_size: Batch size for training
        learning_rate: Learning rate
        test_size: Fraction of data for testing
    """
    print("Starting centralized training...")
    
    # Load and prepare data
    print(f"Loading data from {data_path}")
    data_dict = prepare_data_for_training(
        pd.read_csv(data_path),
        test_size=test_size,
        sequence_length=10
    )
    
    # Create model
    model = create_model(
        input_size=data_dict['n_features'],
        sequence_length=10,
        n_classes=data_dict['n_classes']
    )
    
    print(f"Model created with {sum(p.numel() for p in model.parameters())} parameters")
    print(f"Training on {len(data_dict['X_train'])} samples")
    print(f"Testing on {len(data_dict['X_test'])} samples")
    
    # Create data loaders
    train_dataset = TensorDataset(
        torch.FloatTensor(data_dict['X_train']),
        torch.LongTensor(data_dict['y_train'])
    )
    test_dataset = TensorDataset(
        torch.FloatTensor(data_dict['X_test']),
        torch.LongTensor(data_dict['y_test'])
    )
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    # Initialize trainer
    trainer = ModelTrainer(
        model=model,
        learning_rate=learning_rate
    )
    
    # Train model
    print("Starting training...")
    history = trainer.train(
        train_loader=train_loader,
        val_loader=test_loader,
        epochs=epochs,
        early_stopping_patience=10
    )
    
    # Evaluate model
    print("Evaluating model...")
    model.eval()
    all_predictions = []
    all_targets = []
    
    with torch.no_grad():
        for data, target in test_loader:
            output = model(data)
            predictions = torch.argmax(output, dim=1)
            all_predictions.extend(predictions.numpy())
            all_targets.extend(target.numpy())
    
    # Calculate metrics
    accuracy = accuracy_score(all_targets, all_predictions)
    report = classification_report(all_targets, all_predictions, 
                                 target_names=data_dict['class_names'], 
                                 output_dict=True)
    cm = confusion_matrix(all_targets, all_predictions)
    
    print(f"\nFinal Test Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(all_targets, all_predictions, 
                              target_names=data_dict['class_names']))
    
    # Save model and preprocessor
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    trainer.save_model(model_save_path)
    data_dict['preprocessor'].save(preprocessor_save_path)
    
    # Save training results
    results = {
        'accuracy': accuracy,
        'classification_report': report,
        'confusion_matrix': cm.tolist(),
        'class_names': data_dict['class_names'].tolist(),
        'training_history': history,
        'model_info': model.get_model_info(),
        'timestamp': datetime.now().isoformat()
    }
    
    results_path = model_save_path.replace('.pth', '_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Plot training history
    plot_training_history(history, model_save_path.replace('.pth', '_history.png'))
    
    # Plot confusion matrix
    plot_confusion_matrix(cm, data_dict['class_names'], 
                         model_save_path.replace('.pth', '_confusion_matrix.png'))
    
    print(f"Model saved to {model_save_path}")
    print(f"Preprocessor saved to {preprocessor_save_path}")
    print(f"Results saved to {results_path}")
    
    return results

def train_federated_model(data_dir: str = "data",
                         model_save_path: str = "models/federated_model.pth",
                         rounds: int = 10,
                         local_epochs: int = 5,
                         batch_size: int = 32,
                         learning_rate: float = 0.001):
    """
    Train the model using federated learning.
    
    Args:
        data_dir: Directory containing client data files
        model_save_path: Path to save trained model
        rounds: Number of federated learning rounds
        local_epochs: Number of local training epochs per round
        batch_size: Batch size for training
        learning_rate: Learning rate
    """
    print("Starting federated training...")
    
    from federated.coordinator import FederatedCoordinator
    from federated.client import create_federated_clients
    
    # Load first client's data to get model parameters
    client_1_data = pd.read_csv(os.path.join(data_dir, "client_1_data.csv"))
    data_dict = prepare_data_for_training(client_1_data, test_size=0.0)
    
    # Create global model
    global_model = create_model(
        input_size=data_dict['n_features'],
        sequence_length=10,
        n_classes=data_dict['n_classes']
    )
    
    # Create preprocessor
    preprocessor = data_dict['preprocessor']
    
    # Create coordinator
    coordinator = FederatedCoordinator(global_model, preprocessor)
    
    # Create clients
    clients = create_federated_clients(
        n_clients=3,
        data_dir=data_dir,
        model_template=global_model,
        preprocessor=preprocessor
    )
    
    print(f"Created {len(clients)} federated clients")
    print(f"Starting {rounds} federated learning rounds")
    
    # Federated learning rounds
    round_results = []
    
    for round_num in range(1, rounds + 1):
        print(f"\n=== Federated Round {round_num}/{rounds} ===")
        
        # Train clients locally
        client_updates = []
        for client in clients:
            print(f"Training {client.client_id}...")
            
            # Train local model
            local_result = client.train_local_model()
            
            if local_result['success']:
                # Get model weights
                weights = client.get_model_weights()
                client_updates.append({
                    'client_id': client.client_id,
                    'weights': weights,
                    'accuracy': local_result['accuracy'],
                    'samples': local_result['samples']
                })
                
                # Update coordinator
                coordinator.update_client(
                    client.client_id,
                    weights,
                    local_result['accuracy'],
                    local_result['samples']
                )
        
        # Aggregate and update global model
        if coordinator.can_aggregate():
            round_result = coordinator.run_federated_round()
            if round_result['success']:
                round_stats = round_result['round_stats']
                round_results.append(round_stats)
                
                # Update all clients with new global model
                global_weights = [param.clone().detach() for param in global_model.parameters()]
                for client in clients:
                    client.update_model_weights(global_weights)
                
                print(f"Round {round_num} completed. Global accuracy: {round_stats['avg_accuracy']:.3f}")
            else:
                print(f"Round {round_num} failed: {round_result['message']}")
        else:
            print(f"Round {round_num} skipped: Not enough client updates")
    
    # Save final model
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    coordinator.save_model(model_save_path)
    preprocessor.save(model_save_path.replace('.pth', '_preprocessor.pkl'))
    
    # Save federated learning results
    fl_results = {
        'round_results': round_results,
        'final_accuracy': round_results[-1]['avg_accuracy'] if round_results else 0.0,
        'total_rounds': rounds,
        'clients': len(clients),
        'timestamp': datetime.now().isoformat()
    }
    
    results_path = model_save_path.replace('.pth', '_fl_results.json')
    with open(results_path, 'w') as f:
        json.dump(fl_results, f, indent=2)
    
    # Plot federated learning progress
    plot_fl_progress(round_results, model_save_path.replace('.pth', '_fl_progress.png'))
    
    print(f"\nFederated training completed!")
    print(f"Final global accuracy: {fl_results['final_accuracy']:.3f}")
    print(f"Model saved to {model_save_path}")
    print(f"Results saved to {results_path}")
    
    return fl_results

def plot_training_history(history: dict, save_path: str):
    """Plot training history."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Loss plot
    ax1.plot(history['train_losses'], label='Training Loss')
    ax1.plot(history['val_losses'], label='Validation Loss')
    ax1.set_title('Training and Validation Loss')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.legend()
    ax1.grid(True)
    
    # Accuracy plot
    ax2.plot(history['train_accuracies'], label='Training Accuracy')
    ax2.plot(history['val_accuracies'], label='Validation Accuracy')
    ax2.set_title('Training and Validation Accuracy')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy (%)')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_confusion_matrix(cm: np.ndarray, class_names: list, save_path: str):
    """Plot confusion matrix."""
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_fl_progress(round_results: list, save_path: str):
    """Plot federated learning progress."""
    if not round_results:
        return
    
    rounds = [r['round'] for r in round_results]
    accuracies = [r['avg_accuracy'] for r in round_results]
    
    plt.figure(figsize=(10, 6))
    plt.plot(rounds, accuracies, marker='o', linewidth=2, markersize=6)
    plt.title('Federated Learning Progress')
    plt.xlabel('Round')
    plt.ylabel('Average Client Accuracy')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

def evaluate_model(model_path: str, test_data_path: str):
    """Evaluate a trained model."""
    print(f"Evaluating model from {model_path}")
    
    # Load model
    checkpoint = torch.load(model_path, map_location='cpu')
    model_info = checkpoint['model_info']
    
    # Create model
    model = create_model(
        input_size=model_info['input_size'],
        sequence_length=model_info['sequence_length'],
        n_classes=model_info['n_classes']
    )
    model.load_state_dict(checkpoint['model_state_dict'])
    
    # Load test data
    data_dict = load_and_preprocess_data(test_data_path)
    
    # Create test loader
    test_dataset = TensorDataset(
        torch.FloatTensor(data_dict['X_test']),
        torch.LongTensor(data_dict['y_test'])
    )
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # Evaluate
    model.eval()
    all_predictions = []
    all_targets = []
    
    with torch.no_grad():
        for data, target in test_loader:
            output = model(data)
            predictions = torch.argmax(output, dim=1)
            all_predictions.extend(predictions.numpy())
            all_targets.extend(target.numpy())
    
    # Calculate metrics
    accuracy = accuracy_score(all_targets, all_predictions)
    report = classification_report(all_targets, all_predictions, 
                                 target_names=data_dict['class_names'], 
                                 output_dict=True)
    cm = confusion_matrix(all_targets, all_predictions)
    
    print(f"Test Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(all_targets, all_predictions, 
                              target_names=data_dict['class_names']))
    
    return {
        'accuracy': accuracy,
        'classification_report': report,
        'confusion_matrix': cm,
        'class_names': data_dict['class_names']
    }

def main():
    parser = argparse.ArgumentParser(description='Train AI-Driven IDS Model')
    parser.add_argument('--mode', choices=['centralized', 'federated'], 
                       default='centralized', help='Training mode')
    parser.add_argument('--data-path', default='data/network_flows.csv',
                       help='Path to training data')
    parser.add_argument('--model-path', default='models/trained_model.pth',
                       help='Path to save trained model')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size')
    parser.add_argument('--learning-rate', type=float, default=0.001,
                       help='Learning rate')
    parser.add_argument('--rounds', type=int, default=10,
                       help='Number of federated learning rounds')
    parser.add_argument('--local-epochs', type=int, default=5,
                       help='Number of local epochs per federated round')
    
    args = parser.parse_args()
    
    if args.mode == 'centralized':
        train_centralized_model(
            data_path=args.data_path,
            model_save_path=args.model_path,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate
        )
    elif args.mode == 'federated':
        train_federated_model(
            model_save_path=args.model_path,
            rounds=args.rounds,
            local_epochs=args.local_epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate
        )

if __name__ == "__main__":
    main()
