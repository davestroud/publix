# Publix Expansion Predictor

A multi-agent LLM-powered application that predicts where Publix grocery stores are likely to open by analyzing current locations, demographics, competitor data, and zoning/permitting information.

## Architecture

- **Backend**: Python FastAPI with multi-agent system using OpenAI
- **Frontend**: React with Vite
- **Database**: PostgreSQL (RDS)
- **Storage**: AWS S3
- **Deployment**: AWS App Runner
- **Monitoring**: LangSmith for LLM tracing

## Project Structure

```
publix/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── agents/       # Multi-agent system
│   │   ├── api/         # API routes and models
│   │   ├── models/      # Database models
│   │   └── services/    # Core services
│   └── alembic/         # Database migrations
├── frontend/            # React frontend
│   └── src/
│       └── components/  # React components
└── infrastructure/      # Deployment configs
    ├── Dockerfile
    └── apprunner.yaml
```

## Setup

### Prerequisites

- Python 3.11+
- Poetry
- Node.js 18+
- PostgreSQL
- AWS Account (for deployment)
- OpenAI API Key
- LangSmith API Key

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies with Poetry:
```bash
poetry install
```

3. Create `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

4. Update `.env` with your credentials:
- `OPENAI_API_KEY`
- `LANGSMITH_API_KEY`
- `DATABASE_URL`
- AWS credentials

5. Initialize database:
```bash
poetry run alembic upgrade head
```

6. Run the backend:
```bash
poetry run uvicorn app.main:app --reload
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Multi-Agent System

The application uses four specialized agents:

1. **Data Collector Agent**: Gathers store locations, competitor data, demographics, and zoning records
2. **Analyst Agent**: Analyzes patterns, calculates store density, and identifies expansion opportunities
3. **Site Evaluator Agent**: Evaluates specific parcels and cities for suitability
4. **Reporter Agent**: Generates insights and prediction reports

The **Orchestrator** coordinates the workflow between agents.

## API Endpoints

- `GET /api/stores` - List Publix stores
- `GET /api/predictions` - Get predictions
- `POST /api/analyze` - Trigger analysis for a region
- `POST /api/analyze/city` - Analyze a single city
- `GET /api/demographics/{city}` - Get demographic data
- `GET /api/zoning/{region}` - Get zoning records
- `GET /api/dashboard/stats` - Dashboard statistics

## Deployment

### Database Setup (RDS PostgreSQL)

Choose one of the following methods to set up your database:

1. **AWS CLI Script** (Quickest):
```bash
cd infrastructure
./rds-setup.sh
```

2. **Terraform** (Recommended for production):
```bash
cd infrastructure/rds-terraform
terraform init
terraform plan
terraform apply
```

3. **CloudFormation**:
```bash
aws cloudformation create-stack \
  --stack-name publix-rds \
  --template-body file://infrastructure/rds-cloudformation.yaml \
  --parameters ParameterKey=MasterUserPassword,ParameterValue=YourPassword123!
```

4. **AWS Console**: See `infrastructure/rds-setup.md` for detailed manual setup instructions.

After database creation, get the connection string and update your `.env` file:
```bash
DATABASE_URL=postgresql://username:password@endpoint:5432/publix_db
```

### AWS App Runner

1. Build Docker image:
```bash
docker build -t publix-expansion-predictor -f infrastructure/Dockerfile .
```

2. Push to ECR or use App Runner's build service

3. Configure App Runner service using `infrastructure/apprunner.yaml`

### Environment Variables

Set these in AWS Secrets Manager or App Runner environment:
- `OPENAI_API_KEY`
- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT`
- `DATABASE_URL` (RDS connection string)
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `S3_BUCKET_NAME`

## Development

### Running with Docker Compose

```bash
docker-compose -f infrastructure/docker-compose.yml up
```

### Database Migrations

Create a new migration:
```bash
poetry run alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
poetry run alembic upgrade head
```

## Features

- **Predictive Modeling**: Uses LLM to analyze expansion patterns
- **Interactive Map**: Visualize stores and predictions
- **Data Tables**: Sortable, filterable tables with CSV export
- **Dashboard**: Key metrics and visualizations
- **Reports**: LLM-generated insights and recommendations

## License

MIT

