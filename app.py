from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import requests
import json
import time
from model_monitor import ModelMonitor
from experiment_tracker import ExperimentTracker

app = FastAPI()
monitor = ModelMonitor()
tracker = ExperimentTracker()

class QueryRequest(BaseModel):
    prompt: str
    model: str = "llama3.2"
    temperature: float = 0.7
    max_tokens: int = 100

class QueryResponse(BaseModel):
    response: str
    model: str
    latency: float
    timestamp: str
    experiment_id: str

@app.post("/generate", response_model=QueryResponse)
async def generate_text(request: QueryRequest):
    """Generate text using Ollama and track metrics"""
    start_time = time.time()
    
    # Create experiment
    experiment_id = tracker.create_experiment(
        model_name=request.model,
        parameters={
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }
    )
    
    try:
        # Call Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": request.model,
                "prompt": request.prompt,
                "stream": False,
                "options": {
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens
                }
            }
        )
        response.raise_for_status()
        
        result = response.json()
        generated_text = result.get("response", "")
        
        # Calculate metrics
        latency = time.time() - start_time
        
        # Update monitoring metrics
        monitor.record_request(
            model=request.model,
            latency=latency,
            input_length=len(request.prompt),
            output_length=len(generated_text)
        )
        
        # Log to experiment tracker
        tracker.log_metrics(experiment_id, {
            "latency": latency,
            "input_tokens": len(request.prompt.split()),
            "output_tokens": len(generated_text.split()),
            "success": True
        })
        
        return QueryResponse(
            response=generated_text,
            model=request.model,
            latency=latency,
            timestamp=datetime.now().isoformat(),
            experiment_id=experiment_id
        )
        
    except Exception as e:
        monitor.record_error(request.model)
        tracker.log_metrics(experiment_id, {"success": False, "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    return monitor.get_metrics()

@app.get("/experiments")
async def get_experiments():
    return tracker.get_all_experiments()

@app.get("/health")
async def health_check():
    try:
        # Check if Ollama is running
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()
        return {"status": "healthy", "ollama": "connected"}
    except:
        return {"status": "unhealthy", "ollama": "disconnected"}