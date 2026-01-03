#!/bin/bash
# Startup script for backend

# Check if .env exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Please create one from .env.example"
fi

# Install dependencies if needed
if [ ! -d ".venv" ]; then
    echo "Installing dependencies..."
    poetry install
fi

# Run database migrations
echo "Running database migrations..."
poetry run alembic upgrade head

# Start the server
echo "Starting FastAPI server..."
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

