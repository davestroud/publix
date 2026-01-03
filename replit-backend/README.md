# Publix Expansion Predictor - Backend Repl

This is the backend Repl for the Publix Expansion Predictor application.

## Setup Instructions

1. **Upload Files**: Upload the entire `backend/` directory from your local project to this Repl

2. **Install Dependencies**: Run `pip install -r requirements.txt` in the Replit shell

3. **Configure Secrets**: In Replit Secrets tab, add:
   - `DATABASE_URL` - Your RDS PostgreSQL connection string
   - `OPENAI_API_KEY` - OpenAI API key
   - `GOOGLE_PLACES_API_KEY` - Google Places API key
   - `AWS_ACCESS_KEY_ID` - AWS access key ID
   - `AWS_SECRET_ACCESS_KEY` - AWS secret access key
   - `AWS_REGION` - `us-east-1`
   - `S3_BUCKET_NAME` - `publix-expansion-data`
   - `S3_REGION` - `us-east-1`
   - `LOG_LEVEL` - `INFO`
   - `ALLOWED_ORIGINS` - Frontend Repl URL (set after frontend is deployed)
   - `PYTHONPATH` - `/home/runner/<repl-name>/backend` (adjust for your Repl name)
   - `PYTHONUNBUFFERED` - `1`

4. **Run Migrations**: After setting up secrets, run database migrations:
   ```python
   from alembic.config import Config
   from alembic import command
   import os
   import sys
   sys.path.insert(0, 'backend')
   
   alembic_cfg = Config("backend/alembic.ini")
   command.upgrade(alembic_cfg, "head")
   ```

5. **Start Server**: Click the "Run" button or the server will start automatically

6. **Get URL**: Copy your Repl URL and share it with the frontend Repl configuration

## File Structure

```
replit-backend/
├── .replit              # Replit configuration
├── main.py              # Entry point
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── backend/             # Upload your backend directory here
    ├── app/
    ├── alembic/
    ├── pyproject.toml
    └── ...
```

## Notes

- The backend will run on the port provided by Replit (check PORT environment variable)
- Health check endpoint: `/health`
- API documentation: `/docs`
- Make sure your RDS security group allows connections from Replit IPs

