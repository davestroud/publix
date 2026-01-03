# Backend Replit Secrets Configuration

Copy these secrets to your Replit Secrets tab. Replace placeholder values with your actual credentials.

## Required Secrets

### Database
```
DATABASE_URL=postgresql://username:password@publix-expansion-db.co1dd6f49wfo.us-east-1.rds.amazonaws.com:5432/public-expansion-db
```

### API Keys
```
OPENAI_API_KEY=sk-your-openai-api-key-here
GOOGLE_PLACES_API_KEY=your-google-places-api-key-here
```

### AWS Credentials
```
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=publix-expansion-data
S3_REGION=us-east-1
```

### Application Settings
```
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
PYTHONPATH=/home/runner/publix-backend/backend
```

### CORS Configuration
```
ALLOWED_ORIGINS=*
```
**Note**: Update this with your frontend Repl URL after deploying frontend:
```
ALLOWED_ORIGINS=https://publix-frontend.yourusername.repl.co
```

## How to Set Secrets in Replit

1. Click the **lock icon** (🔒) in the left sidebar
2. Click **"New secret"**
3. Enter the secret name (e.g., `DATABASE_URL`)
4. Enter the secret value
5. Click **"Add secret"**
6. Repeat for all secrets above

## Important Notes

- Never commit secrets to version control
- Secrets are encrypted and only accessible to your Repl
- Changes to secrets require a Repl restart to take effect
- Use `*` for `ALLOWED_ORIGINS` initially, then restrict to frontend URL after deployment

