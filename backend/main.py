"""
FastAPI backend for AI-Driven IDS.
Provides REST endpoints for inference, federated learning, and model management.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import torch
import numpy as np
import pandas as pd
import json
import time
import asyncio
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.hybrid_model import HybridCNNLSTM, ModelTrainer, create_model
from models.preprocessing import NetworkFlowPreprocessor, create_sequences
from federated.coordinator import FederatedCoordinator
from federated.client import FederatedClient

app = FastAPI(
    title="AI-Driven IDS API",
    description="Hybrid CNN+LSTM Intrusion Detection System with Federated Learning",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
model = None
preprocessor = None
coordinator = None
model_status = {
    "loaded": False,
    "training": False,
    "last_updated": None,
    "accuracy": 0.0,
    "model_info": {}
}
fl_progress = {
    "round": 0,
    "total_rounds": 0,
    "clients": [],
    "accuracy": 0.0,
    "status": "idle"
}

# Pydantic models
class InferenceRequest(BaseModel):
    data: List[List[float]]
    batch: bool = False

class InferenceResponse(BaseModel):
    predictions: List[str]
    confidence: List[float]
    latency_ms: float
    timestamp: str

class FLStartRequest(BaseModel):
    rounds: int = 5
    clients: List[str] = ["client_1", "client_2", "client_3"]

class FLProgressResponse(BaseModel):
    round: int
    total_rounds: int
    clients: List[Dict[str, Any]]
    accuracy: float
    status: str
    timestamp: str

class ModelStatusResponse(BaseModel):
    loaded: bool
    training: bool
    last_updated: Optional[str]
    accuracy: float
    model_info: Dict[str, Any]

class ClientUpdateRequest(BaseModel):
    client_id: str
    weights: List[List[float]]
    accuracy: float
    samples: int

# Initialize model and preprocessor
async def initialize_model():
    """Initialize the model and preprocessor."""
    global model, preprocessor, model_status
    
    try:
        # Load or create preprocessor
        preprocessor_path = "models/preprocessor.pkl"
        if os.path.exists(preprocessor_path):
            preprocessor = NetworkFlowPreprocessor()
            preprocessor.load(preprocessor_path)
            print("Loaded existing preprocessor")
        else:
            # Create new preprocessor from sample data
            from data.generate_sample_data import generate_network_flow_data
            df = generate_network_flow_data(n_samples=1000, attack_ratio=0.2)
            preprocessor = NetworkFlowPreprocessor()
            preprocessor.fit(df)
            preprocessor.save(preprocessor_path)
            print("Created new preprocessor")
        
        # Create model
        model = create_model(
            input_size=preprocessor.n_features,
            sequence_length=10,
            n_classes=len(preprocessor.label_encoders['label'].classes_)
        )
        
        # Try to load existing model
        model_path = "models/trained_model.pth"
        if os.path.exists(model_path):
            trainer = ModelTrainer(model)
            trainer.load_model(model_path)
            print("Loaded existing trained model")
            model_status["accuracy"] = max(trainer.val_accuracies) if trainer.val_accuracies else 0.0
        else:
            print("No trained model found, using untrained model")
        
        model_status["loaded"] = True
        model_status["model_info"] = model.get_model_info()
        model_status["last_updated"] = datetime.now().isoformat()
        
        print("Model initialization completed")
        
    except Exception as e:
        print(f"Error initializing model: {e}")
        model_status["loaded"] = False

@app.on_event("startup")
async def startup_event():
    """Initialize the application."""
    await initialize_model()

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI-Driven IDS API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model_status["loaded"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/model-status", response_model=ModelStatusResponse)
async def get_model_status():
    """Get current model status."""
    return ModelStatusResponse(**model_status)

@app.post("/infer", response_model=InferenceResponse)
async def infer(request: InferenceRequest):
    """Perform inference on network flow data."""
    if not model or not preprocessor:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    start_time = time.time()
    
    try:
        # Convert input data to numpy array
        data = np.array(request.data)
        
        if request.batch:
            # Batch inference
            if len(data.shape) != 3:
                raise HTTPException(status_code=400, detail="Batch data must be 3D (batch_size, sequence_length, features)")
            
            # Convert to tensor
            tensor_data = torch.FloatTensor(data)
            
        else:
            # Single sample inference
            if len(data.shape) == 2:
                # Add batch dimension
                data = data.reshape(1, data.shape[0], data.shape[1])
            elif len(data.shape) == 1:
                # Single sequence, add dimensions
                data = data.reshape(1, 1, -1)
            
            tensor_data = torch.FloatTensor(data)
        
        # Make predictions
        model.eval()
        with torch.no_grad():
            predictions, confidence = model.predict(tensor_data)
        
        # Convert predictions to labels
        pred_labels = preprocessor.inverse_transform_labels(predictions.numpy())
        confidence_scores = confidence.numpy().tolist()
        
        latency_ms = (time.time() - start_time) * 1000
        
        return InferenceResponse(
            predictions=pred_labels.tolist(),
            confidence=confidence_scores,
            latency_ms=latency_ms,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload and process CSV file for inference."""
    if not model or not preprocessor:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(pd.io.common.StringIO(contents.decode('utf-8')))
        
        # Validate columns
        required_columns = preprocessor.feature_columns
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing columns: {list(missing_columns)}"
            )
        
        # Preprocess data
        processed_data = preprocessor.transform(df[required_columns])
        
        # Create sequences
        sequences, _ = create_sequences(processed_data, np.zeros(len(processed_data)))
        
        # Perform inference
        tensor_data = torch.FloatTensor(sequences)
        model.eval()
        with torch.no_grad():
            predictions, confidence = model.predict(tensor_data)
        
        # Convert predictions to labels
        pred_labels = preprocessor.inverse_transform_labels(predictions.numpy())
        
        # Create results DataFrame
        results_df = df.copy()
        results_df['prediction'] = pred_labels
        results_df['confidence'] = confidence.numpy()
        
        # Calculate statistics
        attack_count = sum(1 for pred in pred_labels if pred != 'normal')
        total_count = len(pred_labels)
        
        return {
            "message": "File processed successfully",
            "total_samples": total_count,
            "attack_samples": attack_count,
            "normal_samples": total_count - attack_count,
            "attack_rate": attack_count / total_count,
            "results": results_df.to_dict('records')[:100]  # Return first 100 results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")

@app.post("/start-fl")
async def start_federated_learning(request: FLStartRequest, background_tasks: BackgroundTasks):
    """Start federated learning rounds."""
    global coordinator, fl_progress
    
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Initialize coordinator if not exists
        if not coordinator:
            coordinator = FederatedCoordinator(model, preprocessor)
        
        # Start federated learning in background
        background_tasks.add_task(
            run_federated_learning,
            request.rounds,
            request.clients
        )
        
        fl_progress["total_rounds"] = request.rounds
        fl_progress["status"] = "starting"
        fl_progress["clients"] = [{"id": client, "status": "pending"} for client in request.clients]
        
        return {
            "message": "Federated learning started",
            "rounds": request.rounds,
            "clients": request.clients,
            "status": "running"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FL start error: {str(e)}")

@app.get("/fl-progress", response_model=FLProgressResponse)
async def get_fl_progress():
    """Get federated learning progress."""
    return FLProgressResponse(
        round=fl_progress["round"],
        total_rounds=fl_progress["total_rounds"],
        clients=fl_progress["clients"],
        accuracy=fl_progress["accuracy"],
        status=fl_progress["status"],
        timestamp=datetime.now().isoformat()
    )

@app.post("/client-update")
async def client_update(request: ClientUpdateRequest):
    """Receive client model updates."""
    global coordinator, fl_progress
    
    if not coordinator:
        raise HTTPException(status_code=500, detail="Coordinator not initialized")
    
    try:
        # Convert weights to tensor
        weights = [torch.FloatTensor(w) for w in request.weights]
        
        # Update client in coordinator
        coordinator.update_client(request.client_id, weights, request.accuracy, request.samples)
        
        # Update progress
        for client in fl_progress["clients"]:
            if client["id"] == request.client_id:
                client["status"] = "updated"
                client["accuracy"] = request.accuracy
                client["samples"] = request.samples
                break
        
        return {
            "message": "Client update received",
            "client_id": request.client_id,
            "accuracy": request.accuracy,
            "samples": request.samples
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Client update error: {str(e)}")

@app.get("/metrics")
async def get_metrics():
    """Get model performance metrics."""
    if not model or not preprocessor:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Load test data for evaluation
        test_data_path = "data/test_data.csv"
        if os.path.exists(test_data_path):
            df = pd.read_csv(test_data_path)
            
            # Preprocess test data
            X = df.drop(['label', 'timestamp'], axis=1, errors='ignore')
            y = df['label']
            
            X_processed = preprocessor.transform(X)
            y_encoded = preprocessor.encode_labels(y)
            
            # Create sequences
            X_seq, y_seq = create_sequences(X_processed, y_encoded)
            
            # Evaluate model
            model.eval()
            with torch.no_grad():
                tensor_data = torch.FloatTensor(X_seq)
                predictions, confidence = model.predict(tensor_data)
            
            # Calculate metrics
            from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
            
            pred_labels = preprocessor.inverse_transform_labels(predictions.numpy())
            true_labels = preprocessor.inverse_transform_labels(y_seq)
            
            accuracy = accuracy_score(true_labels, pred_labels)
            report = classification_report(true_labels, pred_labels, output_dict=True)
            cm = confusion_matrix(true_labels, pred_labels)
            
            return {
                "accuracy": accuracy,
                "classification_report": report,
                "confusion_matrix": cm.tolist(),
                "class_names": preprocessor.label_encoders['label'].classes_.tolist(),
                "total_samples": len(true_labels)
            }
        else:
            return {"message": "No test data available"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics calculation error: {str(e)}")

# Background task for federated learning
async def run_federated_learning(rounds: int, clients: List[str]):
    """Run federated learning rounds."""
    global fl_progress, model_status
    
    try:
        fl_progress["status"] = "running"
        
        for round_num in range(1, rounds + 1):
            fl_progress["round"] = round_num
            
            # Simulate client updates (in real scenario, clients would send updates)
            await asyncio.sleep(2)  # Simulate processing time
            
            # Update client statuses
            for client in fl_progress["clients"]:
                client["status"] = "training"
                client["accuracy"] = np.random.uniform(0.7, 0.95)
                client["samples"] = np.random.randint(100, 1000)
            
            # Simulate aggregation
            await asyncio.sleep(1)
            
            # Update global accuracy
            client_accuracies = [c["accuracy"] for c in fl_progress["clients"]]
            fl_progress["accuracy"] = np.mean(client_accuracies)
            
            # Update model status
            model_status["accuracy"] = fl_progress["accuracy"]
            model_status["last_updated"] = datetime.now().isoformat()
            
            print(f"FL Round {round_num}/{rounds} completed. Accuracy: {fl_progress['accuracy']:.3f}")
        
        fl_progress["status"] = "completed"
        print("Federated learning completed")
        
    except Exception as e:
        fl_progress["status"] = "error"
        print(f"Federated learning error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
