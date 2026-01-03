"""Entry point for Replit backend deployment"""
import sys
import os

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if os.path.exists(backend_path):
    sys.path.insert(0, backend_path)
else:
    # If backend is in current directory, add current directory
    sys.path.insert(0, os.path.dirname(__file__))

from app.main import app
import uvicorn

if __name__ == "__main__":
    # Replit provides PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"Starting Publix Expansion Predictor Backend on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

