# Quick Start Guide

## ✅ Setup Complete!

You've successfully:
- ✅ Created RDS PostgreSQL database
- ✅ Created S3 bucket
- ✅ Configured environment variables
- ✅ Installed dependencies
- ✅ Run database migrations

## 🚀 Start the Application

### 1. Start the Backend Server

```bash
cd backend
poetry run uvicorn app.main:app --reload
```

The API will be available at:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Root**: http://localhost:8000/

### 2. Test the API

Open your browser and visit:
```
http://localhost:8000/docs
```

This will show you the interactive API documentation where you can:
- See all available endpoints
- Test API calls directly
- View request/response schemas

### 3. Try These Endpoints

**Get Dashboard Stats**:
```bash
curl http://localhost:8000/api/dashboard/stats
```

**Get Stores**:
```bash
curl http://localhost:8000/api/stores
```

**Get Predictions**:
```bash
curl http://localhost:8000/api/predictions
```

**Run Analysis** (requires valid API keys):
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"region": "KY"}'
```

## 📋 Optional: Start Frontend

If you want to use the React frontend:

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000/api" > .env
npm run dev
```

Frontend will be at: http://localhost:3000

## 🔍 Verify Everything Works

1. **Check Database Connection**:
   ```bash
   cd backend
   poetry run python -c "from app.services.database import engine; conn = engine.connect(); print('✅ Database connected!'); conn.close()"
   ```

2. **Check S3 Access**:
   ```bash
   aws s3 ls s3://publix-expansion-data/
   ```

3. **Check Backend Health**:
   ```bash
   curl http://localhost:8000/health
   ```

## 📚 Documentation

- **Full Setup Guide**: `SETUP.md`
- **Environment Variables**: `ENV_SETUP.md`
- **Next Steps**: `NEXT_STEPS.md`
- **Database Info**: `infrastructure/db-connection-info.txt`
- **S3 Info**: `infrastructure/s3-bucket-info.txt`

## 🎯 What's Next?

Once your backend is running:

1. **Test the multi-agent system** by running an analysis
2. **Add data** by scraping Publix store locations
3. **View predictions** in the API or frontend
4. **Deploy to AWS** using App Runner (see `SETUP.md`)

## 🆘 Troubleshooting

**Backend won't start?**
- Check `.env` file has all required keys
- Verify database connection
- Check logs for errors

**API returns errors?**
- Verify OpenAI and LangSmith API keys are valid
- Check database is accessible
- Review logs for specific error messages

**Need help?**
- Check `SETUP.md` for detailed instructions
- Review `ENV_SETUP.md` for environment variable help
- Check AWS Console for RDS and S3 status

---

**You're ready to go! Start the backend and explore the API! 🚀**

