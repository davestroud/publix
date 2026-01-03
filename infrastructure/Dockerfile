# Multi-stage build for Publix Expansion Predictor
FROM python:3.11-slim as builder

# Install Poetry
RUN pip install poetry==1.7.1

# Set working directory
WORKDIR /app

# Copy Poetry files
COPY backend/pyproject.toml backend/poetry.lock* ./

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY backend/ ./backend/

# Set environment variables
ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

