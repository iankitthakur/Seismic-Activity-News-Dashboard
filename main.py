# ==============================================================================
# 2. Setup and Installation
# ==============================================================================
!pip install streamlit pyngrok pandas requests plotly google-genai -q
import os
import subprocess
import threading
import time
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from pyngrok import ngrok
from google import genai
from google.genai.errors import APIError
import plotly.graph_objects as go # Must keep this import here for the execution environment

# Create the mandatory /.kiro directory for submission
!mkdir .kiro

# ==============================================================================
# 3. Configuration (User Input)
# ==============================================================================
# --- REQUIRED: Replace these placeholders ---
NGROK_AUTH_TOKEN = "36hQryOC6fkZfCmSfMqropVyvRy_2x9ZdYRbG9AQQKzDHbWwY"
# Get your Gemini API Key from Google AI Studio (ai.google.dev)
# For secure storage in Colab, use the secrets manager (🔑 icon on the left panel).
# Name your secret 'GEMINI_API_KEY' if you wish to use the code below.
from google.colab import userdata

if 'GEMINI_API_KEY' not in os.environ:
    try:
        GEMINI_API_KEY = userdata.get('GEMINI_API_KEY')
    except userdata.SecretNotFoundError:
        print("Warning: GEMINI_API_KEY not found in Colab secrets. Please add it or set it manually.")
        GEMINI_API_KEY = "AIzaSyBLxpyVhF6OyOZ1GpdxfHiOvpmPFc8PWnw" # Fallback for execution
# ---------------------------------------------

# Set the environment variable for the Gemini client
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

# Initialize the Gemini Client
try:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
except ValueError:
    print("Warning: GEMINI_API_KEY is not set correctly. The sentiment analysis will fail.")
    gemini_client = None

# ==============================================================================
# 4. ngrok Setup and Execution
# ==============================================================================
import subprocess
import threading
import time
from pyngrok import ngrok

print("--- Starting ngrok and Streamlit ---")

# 1. Authenticate ngrok
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

# 2. Run Streamlit in the background
def run_streamlit():
    subprocess.Popen([
        "streamlit",
        "run",
        "app.py",
        "--server.port", "8501",
        "--server.headless", "true"
    ])

# Start Streamlit in a separate thread
threading.Thread(target=run_streamlit, daemon=True).start()
time.sleep(15) # Give Streamlit time to start

# 3. Create ngrok tunnel
try:
    public_url = ngrok.connect(8501)
    print("\n\n🎉 Your Streamlit Dashboard is Live! Access it here:\n")
    print(f"👉 PUBLIC URL: {public_url}\n")
    print("-----------------------------------------------------------\n")

    # Keep the Colab cell running until interrupted
    print("Dashboard running. To stop, interrupt this cell (■ button).")
    while True:
        time.sleep(1)
except Exception as e:
    print(f"\n[ERROR] ngrok failed to connect. Did you set the correct NGROK_AUTH_TOKEN? Error: {e}")
finally:
    # Cleanup on stop
    try:
        ngrok.kill()
    except:
        pass
    print("\n--- Streamlit and ngrok stopped. ---")