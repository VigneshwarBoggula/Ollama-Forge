import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

st.set_page_config(page_title="Ollama Dashboard", layout="wide")

st.title("Ollama Dashboard")

# Sidebar for configuration
st.sidebar.header("Configuration")
api_url = st.sidebar.text_input("API URL", "http://localhost:8000")
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 1, 10, 5)

# Main layout
col1, col2, col3 = st.columns(3)

# Health Check
with col1:
    st.subheader("Health Status")
    try:
        health_response = requests.get(f"{api_url}/health")
        health_data = health_response.json()
        if health_data["status"] == "healthy":
            st.success(f"API: {health_data['status']}")
            st.success(f"Ollama: {health_data['ollama']}")
        else:
            st.error(f"API: {health_data['status']}")
            st.error(f"Ollama: {health_data['ollama']}")
    except:
        st.error("Cannot connect to API")

# Metrics
with col2:
    st.subheader("Current Metrics")
    try:
        metrics_response = requests.get(f"{api_url}/metrics")
        metrics = metrics_response.json()
        
        if "total_requests" in metrics:
            st.metric("Total Requests", metrics["total_requests"])
            st.metric("Success Rate", 
                     f"{(metrics['successful_requests'] / metrics['total_requests'] * 100):.1f}%")
            st.metric("Avg Latency", f"{metrics.get('average_latency', 0):.2f}s")
    except:
        st.info("No metrics available yet")

# Model Testing
with col3:
    st.subheader("Test Model")
    test_prompt = st.text_area("Enter prompt:", "What is machine learning?")
    test_model = st.selectbox("Model:", ["llama3.2"])
    test_temp = st.slider("Temperature:", 0.0, 1.0, 0.7)
    
    if st.button("Generate"):
        with st.spinner("Generating..."):
            try:
                response = requests.post(
                    f"{api_url}/generate",
                    json={
                        "prompt": test_prompt,
                        "model": test_model,
                        "temperature": test_temp,
                        "max_tokens": 100
                    }
                )
                result = response.json()
                st.success(f"Generated in {result['latency']:.2f}s")
                st.text_area("Response:", result['response'], height=150)
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Experiments Section
st.header("Experiments")

try:
    experiments_response = requests.get(f"{api_url}/experiments")
    experiments = experiments_response.json()
    
    if experiments:
        # Convert to DataFrame
        df = pd.DataFrame(experiments)
        
        # Filter successful experiments
        successful_df = df[df['status'] == 'completed'].copy()
        
        if not successful_df.empty:
            # Latency over time
            fig_latency = px.line(
                successful_df.sort_values('created_at'),
                x='created_at',
                y=[exp.get('latency', 0) for exp in successful_df['metrics']],
                title='Latency Over Time'
            )
            st.plotly_chart(fig_latency, use_container_width=True)
            
            # Experiments table
            st.subheader("Recent Experiments")
            display_df = df[['id', 'model_name', 'status', 'created_at']].tail(10)
            st.dataframe(display_df)
        else:
            st.info("No completed experiments yet")
    else:
        st.info("No experiments recorded yet")
except:
    st.error("Could not load experiments")

# Auto-refresh
time.sleep(refresh_rate)
st.rerun()