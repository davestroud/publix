# Setup Guide

## Prerequisites

1. **Python 3.11+** - Install from [python.org](https://www.python.org/downloads/)
2. **Poetry** - Install from [python-poetry.org](https://python-poetry.org/docs/#installation)
3. **Node.js 18+** - Install from [nodejs.org](https://nodejs.org/)
4. **PostgreSQL** - Install from [postgresql.org](https://www.postgresql.org/download/)
5. **AWS Account** - For deployment (optional for local development)
6. **OpenAI API Key** - Get from [platform.openai.com](https://platform.openai.com/api-keys)
7. **LangSmith API Key** - Get from [smith.langchain.com](https://smith.langchain.com/)

## Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create `.env` file:
```bash
cat > .env << EOF
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# LangSmith Configuration
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=publix-expansion-predictor

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/publix_db

# AWS Configuration (optional for local dev)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=publix-expansion-data

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
EOF
```

3. Install dependencies:
```bash
# For Python 3.13 users, set this environment variable first:
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

poetry install --no-root
```

4. Set up PostgreSQL database:
```bash
createdb publix_db
# Or using psql:
# psql -U postgres -c "CREATE DATABASE publix_db;"
```

5. Update DATABASE_URL in `.env` with your PostgreSQL credentials

6. Run database migrations:
```bash
poetry run alembic upgrade head
```

7. Start the backend server:
```bash
poetry run uvicorn app.main:app --reload
# Or use the startup script:
# ./run.sh
```

The API will be available at `http://localhost:8000`
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file (optional, defaults to localhost:8000):
```bash
echo "VITE_API_URL=http://localhost:8000/api" > .env
```

4. Start development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Docker Setup (Alternative)

1. Update environment variables in `infrastructure/docker-compose.yml`

2. Start services:
```bash
docker-compose -f infrastructure/docker-compose.yml up
```

This will start:
- PostgreSQL database on port 5432
- Backend API on port 8000

## AWS Deployment

### Prerequisites
- AWS CLI configured
- Docker installed
- ECR repository created (or use App Runner build service)

### Steps

1. **Create RDS PostgreSQL Instance**:
   - Use AWS Console or CLI
   - Note the endpoint URL
   - Update `DATABASE_URL` in App Runner config

2. **Create S3 Bucket**:
   ```bash
   aws s3 mb s3://publix-expansion-data
   ```

3. **Store Secrets in AWS Secrets Manager**:
   ```bash
   aws secretsmanager create-secret \
     --name publix-expansion-secrets \
     --secret-string '{"OPENAI_API_KEY":"your_key","LANGSMITH_API_KEY":"your_key"}'
   ```

4. **Build and Push Docker Image** (if using ECR):
   ```bash
   docker build -t publix-expansion-predictor -f infrastructure/Dockerfile .
   docker tag publix-expansion-predictor:latest <account>.dkr.ecr.<region>.amazonaws.com/publix-expansion-predictor:latest
   docker push <account>.dkr.ecr.<region>.amazonaws.com/publix-expansion-predictor:latest
   ```

5. **Create App Runner Service**:
   - Use AWS Console or CLI
   - Reference `infrastructure/apprunner.yaml` for configuration
   - Set environment variables from Secrets Manager

## Testing the Application

1. **Start Backend**: `cd backend && poetry run uvicorn app.main:app --reload`

2. **Start Frontend**: `cd frontend && npm run dev`

3. **Test API**:
   - Visit http://localhost:8000/docs
   - Try `GET /api/dashboard/stats`
   - Try `POST /api/analyze` with `{"region": "KY"}`

4. **Test Frontend**:
   - Visit http://localhost:3000
   - Navigate through Dashboard, Map, Data Table, and Reports tabs
   - Try running an analysis from the Reports tab

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running: `pg_isready`
- Check DATABASE_URL format: `postgresql://user:password@host:port/dbname`
- Ensure database exists: `psql -l | grep publix_db`

### Poetry Issues
- Update Poetry: `curl -sSL https://install.python-poetry.org | python3 -`
- Clear cache: `poetry cache clear pypi --all`

### Frontend API Connection Issues
- Check backend is running on port 8000
- Verify CORS is enabled in backend
- Check browser console for errors

### LLM API Issues
- Verify OPENAI_API_KEY is set correctly
- Check API key has sufficient credits
- Review LangSmith dashboard for traces

## Next Steps

1. Implement actual web scraping logic in `backend/app/services/scraper.py`
2. Add more data sources (Census API, etc.)
3. Enhance LLM prompts for better predictions
4. Add authentication/authorization
5. Set up CI/CD pipeline
6. Add comprehensive tests

