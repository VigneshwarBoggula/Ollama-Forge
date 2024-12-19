import json
import os
from datetime import datetime
from typing import Dict, Any, List
import uuid

class ExperimentTracker:
    def __init__(self, storage_path: str = "experiments.json"):
        self.storage_path = storage_path
        self.experiments = self._load_experiments()
    
    def _load_experiments(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_experiments(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.experiments, f, indent=2)
    
    def create_experiment(self, model_name: str, parameters: Dict[str, Any]):
        experiment_id = str(uuid.uuid4())
        
        self.experiments[experiment_id] = {
            "id": experiment_id,
            "model_name": model_name,
            "parameters": parameters,
            "created_at": datetime.now().isoformat(),
            "metrics": {},
            "status": "running"
        }
        
        self._save_experiments()
        return experiment_id
    
    def log_metrics(self, experiment_id: str, metrics: Dict[str, Any]):
        if experiment_id in self.experiments:
            self.experiments[experiment_id]["metrics"].update(metrics)
            self.experiments[experiment_id]["updated_at"] = datetime.now().isoformat()
            
            # Update status based on success metric
            if "success" in metrics:
                self.experiments[experiment_id]["status"] = "completed" if metrics["success"] else "failed"
            
            self._save_experiments()
    
    def get_experiment(self, experiment_id: str):
        return self.experiments.get(experiment_id, {})
    
    def get_all_experiments(self) -> List[Dict[str, Any]]:

        return list(self.experiments.values())
    
    def get_best_experiment(self, metric: str = "latency", minimize: bool = True):
        completed_experiments = [
            exp for exp in self.experiments.values() 
            if exp.get("status") == "completed" and metric in exp.get("metrics", {})
        ]
        
        if not completed_experiments:
            return {}
        
        return min(completed_experiments, 
                  key=lambda x: x["metrics"][metric]) if minimize else max(
                  completed_experiments, 
                  key=lambda x: x["metrics"][metric])