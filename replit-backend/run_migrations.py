"""
Run database migrations in Replit
Execute this script after setting up secrets to initialize/update the database
"""

import sys
import os

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
if os.path.exists(backend_path):
    sys.path.insert(0, backend_path)
else:
    sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
from alembic.config import Config
from alembic import command

# Load environment variables
load_dotenv()


def run_migrations():
    """Run Alembic migrations to head"""
    try:
        # Find alembic.ini - it should be in backend/alembic/ or backend/
        alembic_ini_paths = [
            os.path.join(backend_path, "alembic.ini"),
            "backend/alembic.ini",
            "alembic.ini",
        ]

        alembic_ini = None
        for path in alembic_ini_paths:
            if os.path.exists(path):
                alembic_ini = path
                break

        if not alembic_ini:
            print("ERROR: Could not find alembic.ini file")
            print("Please ensure alembic.ini exists in backend/ directory")
            return False

        print(f"Using Alembic config: {alembic_ini}")
        alembic_cfg = Config(alembic_ini)

        # Set the script location if not already set
        if not alembic_cfg.get_main_option("script_location"):
            script_location = os.path.join(os.path.dirname(alembic_ini), "alembic")
            if os.path.exists(script_location):
                alembic_cfg.set_main_option("script_location", script_location)

        print("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        print("✓ Migrations completed successfully!")
        return True

    except Exception as e:
        print(f"ERROR: Migration failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Publix Expansion Predictor - Database Migrations")
    print("=" * 50)

    # Check for DATABASE_URL
    if not os.getenv("DATABASE_URL"):
        print("ERROR: DATABASE_URL environment variable not set")
        print("Please set DATABASE_URL in Replit Secrets tab")
        sys.exit(1)

    success = run_migrations()
    sys.exit(0 if success else 1)
