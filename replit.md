# Publix Expansion Predictor

## Overview
A multi-agent LLM system to predict Publix grocery store expansion locations. The application features a React frontend with an interactive dashboard, map view, data tables, and AI-powered chat assistant, backed by a FastAPI Python backend with PostgreSQL database.

## Project Architecture

### Frontend (React + Vite)
- **Location**: `frontend/`
- **Port**: 5000 (development)
- **Framework**: React 18 with Vite
- **Key Libraries**: react-leaflet (maps), recharts (charts), axios (API calls)
- **Entry**: `frontend/src/main.jsx`

### Backend (FastAPI + Python)
- **Location**: `backend/`
- **Port**: 8000 (development)
- **Framework**: FastAPI with uvicorn
- **Database**: PostgreSQL (via SQLAlchemy)
- **AI**: LangChain + OpenAI integration
- **Entry**: `backend/app/main.py`

### Database
- PostgreSQL with SQLAlchemy ORM
- Alembic migrations in `backend/alembic/`
- Models defined in `backend/app/models/schemas.py`

## Key Features
- Dashboard with store/prediction statistics
- Interactive map view with Leaflet
- Data tables for stores, predictions, competitors
- Property search functionality
- AI chat assistant (requires OPENAI_API_KEY)
- Advanced analytics and reporting

## Environment Variables

### Required for Full Functionality
- `DATABASE_URL` - PostgreSQL connection string (auto-configured by Replit)
- `OPENAI_API_KEY` - OpenAI API key for AI features (optional, app runs without it)

### Optional
- `ALLOWED_ORIGINS` - CORS origins (defaults to `*`)
- `LOG_LEVEL` - Logging level (defaults to INFO)

## Running the Application
The app is configured to run via a single workflow that starts both frontend and backend:
- Frontend: `cd frontend && npm run dev` (port 5000)
- Backend: `cd backend && uvicorn app.main:app --host localhost --port 8000`

## API Endpoints
- `GET /` - API info
- `GET /health` - Health check
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/stores` - List stores
- `GET /api/predictions` - List predictions
- `GET /api/competitors` - List competitors
- `POST /api/chat` - AI chat endpoint (requires OpenAI)
- And more (see `backend/app/api/routes.py`)

## Recent Changes
- 2026-01-03: Configured for Replit environment
  - Updated Vite to use port 5000 with allowedHosts enabled
  - Made OpenAI client initialization lazy to allow app to run without API key
  - Fixed langchain import paths for newer versions
  - Set up PostgreSQL database connection

## User Preferences
- None recorded yet

## Development Notes
- The AI features (chat, analysis) require an OPENAI_API_KEY to be set
- Frontend proxies `/api` requests to backend on port 8000
- Database tables are auto-created on startup
