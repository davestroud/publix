"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
from app.api import analytics_routes
from app.services.database import init_db
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging first (needed for logger)
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Configure LangSmith tracing BEFORE any LangChain imports
# This ensures all LangChain calls are automatically traced
# COMMENTED OUT: LangSmith causing 403 errors, disabling for now
# langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
# langsmith_project = os.getenv("LANGSMITH_PROJECT", "publix-expansion-predictor")
#
# if langsmith_api_key:
#     os.environ["LANGCHAIN_TRACING_V2"] = "true"
#     os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
#     os.environ["LANGCHAIN_PROJECT"] = langsmith_project
#     logger.info(f"LangSmith tracing enabled globally: project={langsmith_project}")
# else:
#     logger.warning("LANGSMITH_API_KEY not set - LangSmith tracing disabled")

logger.info("LangSmith tracing disabled (commented out due to 403 errors)")

# Initialize FastAPI app
app = FastAPI(
    title="Publix Expansion Predictor API",
    description="Multi-agent LLM system to predict Publix store expansion locations",
    version="0.1.0",
)

# Configure CORS
# Get allowed origins from environment variable, fallback to wildcard for development
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins_env == "*":
    allowed_origins = ["*"]
else:
    # Split comma-separated origins
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes.router, prefix="/api", tags=["api"])
app.include_router(analytics_routes.router, prefix="/api", tags=["analytics"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Publix Expansion Predictor API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """Health check endpoint - must respond quickly for App Runner"""
    # Always return healthy immediately - don't block on database
    # App Runner needs fast response for health checks
    # Return 200 status code explicitly
    from fastapi import Response

    return Response(
        content='{"status":"healthy"}', media_type="application/json", status_code=200
    )
