# Olama-Forge

A framework for real-time monitoring, experiment tracking, and performance visualization of local LLMs on Ollama

## Starting

```bash
# Install dependencies
pip install -r requirements.txt

# Start Ollama
ollama serve

# Pull a model
ollama pull [model_name]

# Start the API server
uvicorn app:app --reload --port 8000

# Launch the dashboard
streamlit run streamlit_dashboard.py
```

Access the dashboard at `http://localhost:8501`

## API Endpoints

- `POST /generate` - Generate text with specified parameters
- `GET /metrics` - Retrieve current performance metrics
- `GET /experiments` - List all tracked experiments
- `GET /health` - Check system health status
