"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api import routes
from app.api import analytics_routes
from app.services.database import init_db
import os
import logging
from pathlib import Path
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
    from fastapi import Response
    return Response(
        content='{"status":"healthy"}', media_type="application/json", status_code=200
    )

frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend for all non-API routes"""
        if full_path.startswith("api/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")
