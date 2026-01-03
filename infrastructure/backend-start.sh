#!/bin/bash
# Don't use set -e - we want to start even if migrations fail
set +e

echo "🚀 Starting Publix Expansion Predictor Backend..."

# Get port from environment variable (App Runner sets PORT)
PORT=${PORT:-8000}

# Run database migrations (non-blocking - don't fail if DB is unavailable)
echo "📊 Running database migrations..."
cd /app/backend
python -m alembic upgrade head || {
    echo "⚠️  Migration failed, but continuing to start server..."
}

# Start the FastAPI server immediately
echo "🌐 Starting FastAPI server on port $PORT..."
# Use exec to replace shell process
# Add --log-level info for better visibility
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --log-level info

