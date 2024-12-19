from prometheus_client import Counter, Histogram, Gauge, generate_latest
from datetime import datetime
import json
from typing import Dict, Any

class ModelMonitor:
    def __init__(self):
        # Prometheus metrics
        self.request_count = Counter(
            'model_requests_total', 
            'Total number of model requests',
            ['model']
        )
        
        self.request_latency = Histogram(
            'model_request_latency_seconds',
            'Model request latency',
            ['model']
        )
        
        self.error_count = Counter(
            'model_errors_total',
            'Total number of model errors',
            ['model']
        )
        
        self.input_length = Histogram(
            'model_input_length',
            'Input text length in characters',
            ['model']
        )
        
        self.output_length = Histogram(
            'model_output_length',
            'Output text length in characters',
            ['model']
        )
        
        # Local metrics storage
        self.metrics_history = []
        
    def record_request(self, model: str, latency: float, 
                      input_length: int, output_length: int):
        # Update Prometheus metrics
        self.request_count.labels(model=model).inc()
        self.request_latency.labels(model=model).observe(latency)
        self.input_length.labels(model=model).observe(input_length)
        self.output_length.labels(model=model).observe(output_length)
        
        # Store in history
        self.metrics_history.append({
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "latency": latency,
            "input_length": input_length,
            "output_length": output_length,
            "success": True
        })
        
        # Keep only last 1000 entries
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
    
    def record_error(self, model: str):
        self.error_count.labels(model=model).inc()
        self.metrics_history.append({
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "success": False
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        if not self.metrics_history:
            return {"message": "No metrics recorded yet"}
        
        # Calculate summary statistics
        successful_requests = [m for m in self.metrics_history if m.get("success", False)]
        
        if successful_requests:
            latencies = [m["latency"] for m in successful_requests]
            avg_latency = sum(latencies) / len(latencies)
            
            return {
                "total_requests": len(self.metrics_history),
                "successful_requests": len(successful_requests),
                "failed_requests": len(self.metrics_history) - len(successful_requests),
                "average_latency": avg_latency,
                "last_request": self.metrics_history[-1]
            }
        
        return {
            "total_requests": len(self.metrics_history),
            "successful_requests": 0,
            "failed_requests": len(self.metrics_history)
        }
    
    def get_prometheus_metrics(self):
        """Get metrics in Prometheus format"""
        return generate_latest()