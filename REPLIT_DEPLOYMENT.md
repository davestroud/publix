# Replit Deployment Guide

Complete guide for deploying Publix Expansion Predictor to Replit.

## Overview

This deployment uses two separate Repls:
- **Backend Repl**: FastAPI backend running on Python
- **Frontend Repl**: React frontend running on Node.js

Both connect to your existing AWS RDS PostgreSQL database.

## Prerequisites

- Replit account
- AWS RDS database endpoint and credentials
- API keys: OpenAI, Google Places, AWS credentials

## Step 1: Backend Repl Setup

### 1.1 Create Backend Repl

1. Go to [Replit](https://replit.com) and create a new Repl
2. Choose **Python** as the language
3. Name it `publix-backend` (or your preferred name)

### 1.2 Upload Backend Files

Upload the following files from `replit-backend/` directory:
- `.replit` - Replit configuration
- `main.py` - Entry point
- `requirements.txt` - Python dependencies
- `run_migrations.py` - Migration script
- `README.md` - Setup instructions

Then upload your entire `backend/` directory from your local project:
- `backend/app/` - Application code
- `backend/alembic/` - Database migrations
- `backend/pyproject.toml` - Poetry config (optional)
- All other backend files

### 1.3 Install Dependencies

In the Replit shell, run:
```bash
pip install -r requirements.txt
```

### 1.4 Configure Secrets

In Replit, go to **Secrets** tab (lock icon) and add:

| Secret Name | Value | Description |
|------------|-------|-------------|
| `DATABASE_URL` | `postgresql://user:pass@host:5432/dbname` | Your RDS connection string |
| `OPENAI_API_KEY` | `sk-...` | OpenAI API key |
| `GOOGLE_PLACES_API_KEY` | `...` | Google Places API key |
| `AWS_ACCESS_KEY_ID` | `...` | AWS access key ID |
| `AWS_SECRET_ACCESS_KEY` | `...` | AWS secret access key |
| `AWS_REGION` | `us-east-1` | AWS region |
| `S3_BUCKET_NAME` | `publix-expansion-data` | S3 bucket name |
| `S3_REGION` | `us-east-1` | S3 region |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ALLOWED_ORIGINS` | `*` | CORS origins (update after frontend deploy) |
| `PYTHONPATH` | `/home/runner/<repl-name>/backend` | Python path (adjust for your Repl) |
| `PYTHONUNBUFFERED` | `1` | Python output buffering |

**Important**: Replace `<repl-name>` in `PYTHONPATH` with your actual Repl name.

### 1.5 Run Database Migrations

In the Replit shell, run:
```bash
python run_migrations.py
```

This will initialize/update your database schema.

### 1.6 Start Backend

Click the **Run** button or the backend will start automatically.

### 1.7 Get Backend URL

Copy your Repl URL from the address bar. It will look like:
```
https://publix-backend.yourusername.repl.co
```

Save this URL - you'll need it for the frontend configuration.

### 1.8 Test Backend

Visit:
- Health check: `https://<backend-repl-url>/health`
- API docs: `https://<backend-repl-url>/docs`

## Step 2: Frontend Repl Setup

### 2.1 Create Frontend Repl

1. Create a new Repl in Replit
2. Choose **Node.js** as the language
3. Name it `publix-frontend` (or your preferred name)

### 2.2 Upload Frontend Files

Upload the following files from `replit-frontend/` directory:
- `.replit` - Replit configuration
- `serve.js` - Production server (optional)
- `README.md` - Setup instructions
- `.env.example` - Environment variable template

Then upload your entire `frontend/` directory from your local project:
- `frontend/src/` - React source code
- `frontend/public/` - Public assets
- `frontend/package.json` - NPM dependencies
- `frontend/vite.config.js` - Vite configuration
- `frontend/index.html` - HTML entry point
- All other frontend files

### 2.3 Install Dependencies

In the Replit shell, run:
```bash
npm install
```

### 2.4 Configure Environment Variables

**Option A: Using Replit Secrets** (Recommended)
1. Go to **Secrets** tab
2. Add: `VITE_API_URL` = `https://<backend-repl-url>/api`

**Option B: Using .env file**
1. Create `.env` file in frontend directory
2. Add: `VITE_API_URL=https://<backend-repl-url>/api`
3. Replace `<backend-repl-url>` with your actual backend Repl URL

### 2.5 Start Frontend

Click the **Run** button. The frontend will start in development mode using Vite.

### 2.6 Get Frontend URL

Copy your Repl URL from the address bar. It will look like:
```
https://publix-frontend.yourusername.repl.co
```

## Step 3: Connect Frontend to Backend

### 3.1 Update Backend CORS

1. Go back to your **Backend Repl**
2. Open **Secrets** tab
3. Update `ALLOWED_ORIGINS` with your frontend Repl URL:
   ```
   https://publix-frontend.yourusername.repl.co
   ```
4. Restart the backend Repl

### 3.2 Verify Frontend Configuration

Ensure `VITE_API_URL` in frontend Repl points to your backend URL:
```
https://<backend-repl-url>/api
```

If you changed it, restart the frontend Repl.

## Step 4: Test Deployment

### 4.1 Test Backend
- Visit: `https://<backend-repl-url>/health`
- Should return: `{"status":"healthy"}`

### 4.2 Test Frontend
- Visit: `https://<frontend-repl-url>`
- Frontend should load
- Check browser console for any API errors

### 4.3 Test API Connection
- Open browser DevTools (F12)
- Go to Network tab
- Interact with the frontend
- Verify API calls are going to backend URL

## Troubleshooting

### Backend Issues

**Database Connection Failed**
- Verify `DATABASE_URL` is correct in Secrets
- Check RDS security group allows connections from Replit IPs
- Ensure database is accessible from internet

**Module Not Found Errors**
- Run `pip install -r requirements.txt` again
- Check `PYTHONPATH` secret matches your Repl structure

**CORS Errors**
- Verify `ALLOWED_ORIGINS` includes frontend URL
- Check for trailing slashes in URLs
- Restart backend after changing secrets

### Frontend Issues

**API Calls Failing**
- Verify `VITE_API_URL` is set correctly
- Check backend is running and accessible
- Verify CORS is configured in backend

**Build Errors**
- Run `npm install` again
- Check Node.js version compatibility
- Review error messages in Replit console

**Environment Variables Not Working**
- For Vite, variables must start with `VITE_`
- Restart Repl after changing secrets
- Check `.env` file syntax if using file-based config

## Production Considerations

### Backend
- Consider using Replit's Always-On feature for production
- Monitor resource usage (CPU, memory)
- Set up proper logging and error tracking

### Frontend
- For production, use production build:
  1. Update `.replit` run command to: `npm run build && node serve.js`
  2. This builds static files and serves them with Express
- Consider using a CDN for static assets
- Enable caching headers for better performance

### Database
- Ensure RDS is configured for production workloads
- Set up database backups
- Monitor connection pool usage

## File Structure Reference

### Backend Repl Structure
```
publix-backend/
├── .replit
├── main.py
├── requirements.txt
├── run_migrations.py
├── README.md
└── backend/
    ├── app/
    ├── alembic/
    └── ...
```

### Frontend Repl Structure
```
publix-frontend/
├── .replit
├── serve.js
├── README.md
├── .env (or use Secrets)
└── frontend/
    ├── src/
    ├── public/
    ├── package.json
    └── ...
```

## Next Steps

1. **Custom Domains**: Replit supports custom domains for paid plans
2. **Monitoring**: Set up error tracking (e.g., Sentry)
3. **CI/CD**: Use Replit's GitHub integration for automatic deployments
4. **Scaling**: Consider Replit's scaling options for high traffic

## Support

If you encounter issues:
1. Check Replit console logs
2. Verify all secrets are set correctly
3. Test backend and frontend URLs independently
4. Review this guide for common issues

