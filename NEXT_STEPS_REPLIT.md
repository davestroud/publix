# Next Steps: Deploy to Replit

You've committed all the Replit deployment files. Now follow these steps to actually deploy your application.

## Step 1: Deploy Backend (10-15 minutes)

### 1.1 Create Backend Repl
1. Go to [Replit](https://replit.com) and sign in
2. Click **"Create Repl"** or **"+"** button
3. Select **"Python"** as the language
4. Name it: `publix-backend` (or your preferred name)
5. Click **"Create Repl"**

### 1.2 Upload Backend Files
**Option A: Using Git (Recommended)**
1. In your Repl, open the Shell (bottom panel)
2. Run:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git temp
   cp -r temp/backend temp/replit-backend/* .
   rm -rf temp
   ```

**Option B: Manual Upload**
1. Upload your entire `backend/` directory:
   - Click the **"Files"** icon (📁) in left sidebar
   - Click **"Upload file"** or drag and drop
   - Upload all files from `backend/` directory
2. Upload files from `replit-backend/`:
   - Upload `.replit` file
   - Upload `main.py`
   - Upload `requirements.txt`
   - Upload `run_migrations.py`

### 1.3 Install Dependencies
In the Replit Shell, run:
```bash
pip install -r requirements.txt
```

### 1.4 Set Secrets
1. Click the **lock icon** (🔒) in the left sidebar
2. Add these secrets (see `replit-backend/SECRETS_TEMPLATE.md` for details):

**Required Secrets:**
```
DATABASE_URL=postgresql://user:pass@publix-expansion-db.co1dd6f49wfo.us-east-1.rds.amazonaws.com:5432/public-expansion-db
OPENAI_API_KEY=sk-your-key-here
GOOGLE_PLACES_API_KEY=your-key-here
AWS_ACCESS_KEY_ID=your-key-here
AWS_SECRET_ACCESS_KEY=your-secret-here
AWS_REGION=us-east-1
S3_BUCKET_NAME=publix-expansion-data
S3_REGION=us-east-1
LOG_LEVEL=INFO
PYTHONPATH=/home/runner/publix-backend/backend
PYTHONUNBUFFERED=1
ALLOWED_ORIGINS=*
```

**Important:** Replace `publix-backend` in `PYTHONPATH` with your actual Repl name if different.

### 1.5 Run Database Migrations
In the Shell, run:
```bash
python run_migrations.py
```

### 1.6 Start Backend
1. Click the **"Run"** button (or press `Ctrl+Enter`)
2. Wait for server to start (check console output)
3. Copy your Repl URL from the address bar
   - Format: `https://publix-backend.yourusername.repl.co`
4. Test: Visit `https://<your-backend-url>/health`
   - Should return: `{"status":"healthy"}`

## Step 2: Deploy Frontend (10-15 minutes)

### 2.1 Create Frontend Repl
1. Create a **new Repl** in Replit
2. Select **"Node.js"** as the language
3. Name it: `publix-frontend` (or your preferred name)
4. Click **"Create Repl"**

### 2.2 Upload Frontend Files
**Option A: Using Git**
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git temp
cp -r temp/frontend temp/replit-frontend/* .
rm -rf temp
```

**Option B: Manual Upload**
1. Upload entire `frontend/` directory:
   - `frontend/src/`
   - `frontend/public/`
   - `frontend/package.json`
   - `frontend/vite.config.js`
   - `frontend/index.html`
2. Upload from `replit-frontend/`:
   - `.replit` file
   - `serve.js` (optional, for production)
   - `package.json` (if using serve.js)

### 2.3 Install Dependencies
In the Shell, run:
```bash
cd frontend
npm install
cd ..
```

### 2.4 Set Environment Variable
1. Click the **lock icon** (🔒)
2. Add secret:
   ```
   VITE_API_URL=https://<your-backend-repl-url>/api
   ```
   Replace `<your-backend-repl-url>` with your actual backend URL.

### 2.5 Start Frontend
1. Click the **"Run"** button
2. Wait for Vite dev server to start
3. Copy your frontend Repl URL
4. Visit the URL - frontend should load

## Step 3: Connect Frontend to Backend (2 minutes)

### 3.1 Update Backend CORS
1. Go back to your **Backend Repl**
2. Open **Secrets** tab
3. Update `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://publix-frontend.yourusername.repl.co
   ```
   Replace with your actual frontend URL
4. **Restart** the backend Repl (stop and run again)

### 3.2 Verify Frontend Configuration
1. In **Frontend Repl**, verify `VITE_API_URL` secret is set correctly
2. If you changed it, restart the frontend Repl

## Step 4: Test Everything (5 minutes)

### 4.1 Test Backend
- Visit: `https://<backend-url>/health`
- Should return: `{"status":"healthy"}`
- Visit: `https://<backend-url>/docs`
- Should show API documentation

### 4.2 Test Frontend
- Visit: `https://<frontend-url>`
- Frontend should load
- Open browser DevTools (F12)
- Check Console for errors
- Check Network tab - API calls should go to backend

### 4.3 Test API Connection
- Try interacting with the frontend
- Verify API calls are successful
- Check for CORS errors in console

## Troubleshooting

### Backend Won't Start
- Check `PYTHONPATH` matches your Repl name
- Verify all secrets are set correctly
- Check console for error messages
- Ensure `requirements.txt` dependencies installed

### Frontend Can't Connect
- Verify `VITE_API_URL` is set correctly
- Check backend is running
- Verify CORS is configured in backend
- Check browser console for errors

### Database Connection Failed
- Verify `DATABASE_URL` is correct
- Check RDS security group allows connections
- Ensure database is accessible from internet

### CORS Errors
- Update `ALLOWED_ORIGINS` in backend secrets
- Restart backend after changing secrets
- Check for trailing slashes in URLs

## Quick Reference

### Backend Repl Checklist
- [ ] Repl created (Python)
- [ ] Backend files uploaded
- [ ] Replit config files uploaded (.replit, main.py, etc.)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] All secrets set (see SECRETS_TEMPLATE.md)
- [ ] Migrations run (`python run_migrations.py`)
- [ ] Backend running and accessible
- [ ] Health check works (`/health` endpoint)

### Frontend Repl Checklist
- [ ] Repl created (Node.js)
- [ ] Frontend files uploaded
- [ ] Replit config files uploaded (.replit, serve.js)
- [ ] Dependencies installed (`npm install`)
- [ ] `VITE_API_URL` secret set
- [ ] Frontend running and accessible
- [ ] Can connect to backend API

### Connection Checklist
- [ ] Backend CORS updated with frontend URL
- [ ] Backend restarted after CORS change
- [ ] Frontend `VITE_API_URL` points to backend
- [ ] Both Repls running
- [ ] API calls working from frontend

## Need Help?

- See `REPLIT_DEPLOYMENT.md` for detailed guide
- See `REPLIT_QUICKSTART.md` for condensed steps
- Check Replit console logs for errors
- Verify all secrets match templates

## Success!

Once everything is working:
- Your app is live on Replit
- Both frontend and backend are accessible
- Database is connected
- API calls are working

You can share your frontend URL with others to use your application!

