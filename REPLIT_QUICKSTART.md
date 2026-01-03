# Replit Deployment - Quick Start Guide

This is a condensed guide for quickly deploying to Replit. For detailed instructions, see [REPLIT_DEPLOYMENT.md](REPLIT_DEPLOYMENT.md).

## Quick Steps

### Backend (5 minutes)

1. **Create Repl**: New Python Repl named `publix-backend`

2. **Upload Files**:
   - Upload entire `backend/` directory
   - Upload files from `replit-backend/`:
     - `.replit`
     - `main.py`
     - `requirements.txt`
     - `run_migrations.py`

3. **Install**: `pip install -r requirements.txt`

4. **Set Secrets** (see `replit-backend/SECRETS_TEMPLATE.md`):
   - `DATABASE_URL`
   - `OPENAI_API_KEY`
   - `GOOGLE_PLACES_API_KEY`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION=us-east-1`
   - `S3_BUCKET_NAME=publix-expansion-data`
   - `S3_REGION=us-east-1`
   - `LOG_LEVEL=INFO`
   - `ALLOWED_ORIGINS=*` (update after frontend deploy)
   - `PYTHONPATH=/home/runner/publix-backend/backend`
   - `PYTHONUNBUFFERED=1`

5. **Migrate**: `python run_migrations.py`

6. **Run**: Click Run button

7. **Copy URL**: Save backend Repl URL

### Frontend (5 minutes)

1. **Create Repl**: New Node.js Repl named `publix-frontend`

2. **Upload Files**:
   - Upload entire `frontend/` directory
   - Upload files from `replit-frontend/`:
     - `.replit`
     - `serve.js` (optional, for production)
     - `package.json` (for serve.js)

3. **Install**: `npm install` (in frontend directory)

4. **Set Secret**: `VITE_API_URL=https://<backend-repl-url>/api`

5. **Run**: Click Run button

6. **Copy URL**: Save frontend Repl URL

### Connect (2 minutes)

1. **Update Backend CORS**:
   - Backend Repl → Secrets
   - Update `ALLOWED_ORIGINS` with frontend URL
   - Restart backend

2. **Test**:
   - Backend: `https://<backend-url>/health`
   - Frontend: Visit frontend URL

## File Checklist

### Backend Repl Needs:
- [ ] `backend/` directory (all files)
- [ ] `.replit` (from `replit-backend/`)
- [ ] `main.py` (from `replit-backend/`)
- [ ] `requirements.txt` (from `replit-backend/`)
- [ ] `run_migrations.py` (from `replit-backend/`)

### Frontend Repl Needs:
- [ ] `frontend/` directory (all files)
- [ ] `.replit` (from `replit-frontend/`)
- [ ] `serve.js` (from `replit-frontend/`, optional)
- [ ] `package.json` (from `replit-frontend/`, if using serve.js)

## Common Issues

**Backend won't start**: Check `PYTHONPATH` matches your Repl name

**Frontend can't connect**: Verify `VITE_API_URL` is set correctly

**CORS errors**: Update `ALLOWED_ORIGINS` in backend secrets

**Database errors**: Check `DATABASE_URL` and RDS security group

## Next Steps

- See [REPLIT_DEPLOYMENT.md](REPLIT_DEPLOYMENT.md) for detailed guide
- See `replit-backend/SECRETS_TEMPLATE.md` for all secrets
- See `replit-frontend/SECRETS_TEMPLATE.md` for frontend config

