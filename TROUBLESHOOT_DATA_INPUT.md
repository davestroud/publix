# Troubleshooting: Site Not Accepting Data

## Quick Diagnosis

### 1. Check Backend Status

**Is backend running?**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

**If backend is NOT running:**
```bash
# Activate virtual environment
source venv/bin/activate

# Start backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Check Frontend-Backend Connection

**Open browser DevTools (F12) and check:**
- Console tab: Look for API errors
- Network tab: Check if API calls are failing
- Check the API URL being used

**Common issues:**
- Frontend trying to connect to wrong URL
- CORS errors blocking requests
- Backend not running

### 3. Check Database Connection

**Is database accessible?**
```bash
# Test database connection (if you have psql)
psql $DATABASE_URL -c "SELECT 1;"

# Or check backend logs for database errors
```

## Common Issues & Solutions

### Issue 1: Backend Not Running

**Symptoms:**
- Frontend loads but API calls fail
- Network errors in browser console
- "Connection refused" errors

**Solution:**
```bash
# Start backend
source venv/bin/activate
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Issue 2: CORS Errors

**Symptoms:**
- Browser console shows CORS errors
- "Access-Control-Allow-Origin" errors
- API calls blocked by browser

**Solution:**
1. Check `backend/app/main.py` CORS configuration
2. Ensure `ALLOWED_ORIGINS` includes frontend URL
3. For local dev, use `ALLOWED_ORIGINS=*` temporarily

### Issue 3: Wrong API URL

**Symptoms:**
- Frontend making requests to wrong URL
- 404 errors on API calls
- Network tab shows incorrect endpoints

**Solution:**
1. Check `frontend/src/services/api.js`
2. Verify `VITE_API_URL` environment variable
3. For local dev, should be `http://localhost:8000/api`
4. Check browser console for actual API calls

### Issue 4: Database Connection Failed

**Symptoms:**
- Backend starts but requests fail
- Database errors in backend logs
- "Could not connect to database" errors

**Solution:**
1. Check `.env` file has correct `DATABASE_URL`
2. Verify database is accessible
3. Check RDS security group allows connections
4. Test connection: `psql $DATABASE_URL`

### Issue 5: Form Submissions Not Working

**Symptoms:**
- Forms submit but nothing happens
- No error messages
- Data not appearing in database

**Solution:**
1. Check browser console for JavaScript errors
2. Verify API endpoint exists in backend
3. Check request payload format matches backend expectations
4. Look at Network tab to see actual request/response

## Step-by-Step Debugging

### Step 1: Verify Backend is Running
```bash
# Terminal 1: Start backend
source venv/bin/activate
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Test backend
curl http://localhost:8000/health
curl http://localhost:8000/api/stores
```

### Step 2: Verify Frontend Can Connect
1. Open frontend in browser (usually http://localhost:3000)
2. Open DevTools (F12)
3. Go to Network tab
4. Try an action that should call API
5. Check if requests appear and their status

### Step 3: Check API Endpoints
```bash
# Test specific endpoints
curl http://localhost:8000/api/stores
curl http://localhost:8000/api/dashboard/stats
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

### Step 4: Check Database
```bash
# If using PostgreSQL
psql $DATABASE_URL -c "SELECT COUNT(*) FROM publix_stores;"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM predictions;"
```

## Quick Fixes

### Fix 1: Restart Everything
```bash
# Kill existing processes
pkill -f uvicorn
pkill -f vite

# Start backend
source venv/bin/activate
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Start frontend (in another terminal)
cd frontend
npm run dev
```

### Fix 2: Check Environment Variables
```bash
# Verify .env file exists and has correct values
cat .env | grep DATABASE_URL
cat .env | grep OPENAI_API_KEY

# For frontend
cd frontend
cat .env  # Should have VITE_API_URL=http://localhost:8000/api
```

### Fix 3: Clear Browser Cache
- Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
- Clear cache in browser settings
- Try incognito/private mode

## Testing Data Input

### Test Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How many stores are in Florida?",
    "conversation_history": []
  }'
```

### Test Analysis Endpoint
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "region": "Florida",
    "cities": ["Miami", "Tampa"]
  }'
```

### Test City Analysis
```bash
curl -X POST http://localhost:8000/api/analyze/city \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Miami",
    "state": "FL"
  }'
```

## Still Not Working?

1. **Check Backend Logs**: Look at terminal where backend is running
2. **Check Browser Console**: Look for JavaScript errors
3. **Check Network Tab**: See actual HTTP requests/responses
4. **Verify Database**: Ensure data actually exists in database
5. **Check API Documentation**: Visit http://localhost:8000/docs

## Need More Help?

Provide:
1. Backend logs (from terminal)
2. Browser console errors (F12 → Console)
3. Network tab details (F12 → Network → failed requests)
4. What action you're trying (form submission, chat, etc.)

