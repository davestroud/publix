# Fix: Site Not Accepting Data

## Problem Identified

Your backend is returning HTML instead of JSON, which means:
- Backend might be serving frontend files
- Or there's a routing/proxy issue
- API endpoints aren't working correctly

## Solution: Restart Backend Properly

### Step 1: Stop Current Backend
```bash
# Find and kill backend processes
pkill -f uvicorn
pkill -f "python.*main"

# Verify they're stopped
lsof -ti:8000
# Should return nothing
```

### Step 2: Start Backend Correctly
```bash
# Activate virtual environment
source venv/bin/activate

# Navigate to backend directory
cd backend

# Start backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Verify Backend is Working
In a **new terminal**, test:
```bash
# Health check should return JSON
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# API endpoint should return JSON
curl http://localhost:8000/api/stores
# Expected: [] or array of stores

# API docs should work
open http://localhost:8000/docs
```

### Step 4: Check Frontend Connection
1. Open frontend in browser (http://localhost:3000)
2. Open DevTools (F12)
3. Go to **Console** tab
4. Look for errors
5. Go to **Network** tab
6. Try an action (like chat or search)
7. Check if API calls are being made

## Common Issues

### Issue: Backend Serving Frontend
**Symptom**: Backend returns HTML instead of JSON

**Fix**: Make sure backend is started from `backend/` directory, not root:
```bash
cd backend  # Important!
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Issue: Frontend Can't Connect
**Symptom**: Browser console shows connection errors

**Fix**: 
1. Check `frontend/src/services/api.js` - should use `http://localhost:8000/api`
2. For local dev, ensure no `VITE_API_URL` is set (or set to `http://localhost:8000/api`)
3. Check CORS in backend - should allow `http://localhost:3000`

### Issue: CORS Errors
**Symptom**: Browser blocks API requests

**Fix**: Update `backend/app/main.py`:
```python
allowed_origins = ["http://localhost:3000", "http://localhost:5173", "*"]
```

### Issue: Database Connection
**Symptom**: Backend starts but API calls fail with DB errors

**Fix**:
1. Check `.env` file has `DATABASE_URL`
2. Verify database is accessible
3. Check backend logs for connection errors

## Quick Test Script

Run this to test everything:
```bash
#!/bin/bash
echo "Testing Backend..."
echo "1. Health check:"
curl -s http://localhost:8000/health | python3 -m json.tool

echo ""
echo "2. API stores:"
curl -s http://localhost:8000/api/stores | python3 -m json.tool | head -10

echo ""
echo "3. API dashboard:"
curl -s http://localhost:8000/api/dashboard/stats | python3 -m json.tool

echo ""
echo "4. Test chat endpoint:"
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "conversation_history": []}' \
  | python3 -m json.tool
```

## Next Steps

1. **Restart backend** using steps above
2. **Test API endpoints** with curl commands
3. **Check browser console** for errors
4. **Verify frontend can connect** to backend
5. **Test data input** through the UI

## Still Having Issues?

Check:
- Backend terminal logs for errors
- Browser console (F12) for JavaScript errors  
- Network tab (F12) for failed API calls
- Database connection (verify DATABASE_URL)

