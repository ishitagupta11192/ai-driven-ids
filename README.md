# AI-Driven IDS

This project is a Hybrid CNN+LSTM Intrusion Detection System (IDS) with Federated Learning capabilities. It includes a FastAPI backend, a React frontend, and sample data for demonstration and testing.

## Features

- Network flow data preprocessing and encoding
- Hybrid CNN+LSTM model for intrusion detection
- Federated learning simulation with multiple clients
- REST API for inference, metrics, and model management
- Web interface for uploading CSV files and viewing results

## Project Structure

```
basic_demo.py
backend/
  main.py
  requirements.txt
  Dockerfile
  ...
data/
  network_flows.csv
  client_1_data.csv
  ...
federated/
  coordinator.py
  client.py
frontend/
  src/
    App.js
    pages/
      Inference.js
      ...
models/
  hybrid_model.py
  preprocessing.py
  ...
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js (for frontend)
- Docker (optional)

### Backend Setup

1. Install Python dependencies:
   ```bash
   cd backend
   python3 -m pip install -r requirements.txt
   ```
2. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

### Frontend Setup

1. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Start the frontend server:
   ```bash
   npm start
   ```
   The web interface will be available at `http://localhost:3000`.

### Docker Setup

1. Build and run the backend container:
   ```bash
   cd backend
   docker build -t ai-ids-backend .
   docker run -p 8000:8000 ai-ids-backend
   ```

## Usage

- Upload CSV files containing network flow data via the web interface.
- View predictions, confidence scores, and metrics.
- Simulate federated learning rounds.

## API Endpoints

- `/upload-csv` : Upload and process CSV files for inference
- `/infer` : Perform inference via JSON payload
- `/metrics` : Get model performance metrics
- `/model-status` : Get model status
- `/start-fl` : Start federated learning
- `/fl-progress` : Get federated learning progress

## Troubleshooting

- Ensure all dependencies are installed
- Check backend logs for detailed error messages
- Make sure your CSV files match the required format (see `network_flows.csv` for reference)

## License

MIT
