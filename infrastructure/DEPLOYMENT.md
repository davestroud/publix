# AWS App Runner Deployment Guide

This guide walks you through deploying the Publix Expansion Predictor application to AWS App Runner with two separate services: backend (FastAPI) and frontend (React).

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- GitHub repository (or AWS ECR) for source code
- RDS PostgreSQL database already set up
- S3 bucket already created
- All API keys ready (OpenAI, LangSmith, Google Places, etc.)

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│  Frontend       │────────▶│  Backend        │
│  App Runner     │  HTTP   │  App Runner     │
│  (React + Nginx)│         │  (FastAPI)      │
└─────────────────┘         └────────┬────────┘
                                     │
                                     ▼
                              ┌──────────────┐
                              │  RDS         │
                              │  PostgreSQL  │
                              └──────────────┘
```

## Step 1: Prepare AWS Secrets Manager

Before deploying, store sensitive environment variables in AWS Secrets Manager:

### Create Secrets

```bash
# Database URL
aws secretsmanager create-secret \
    --name publix-backend/DATABASE_URL \
    --secret-string "postgresql://user:password@rds-endpoint:5432/publix_db" \
    --region us-east-1

# OpenAI API Key
aws secretsmanager create-secret \
    --name publix-backend/OPENAI_API_KEY \
    --secret-string "sk-proj-YOUR_KEY" \
    --region us-east-1

# LangSmith API Key
aws secretsmanager create-secret \
    --name publix-backend/LANGSMITH_API_KEY \
    --secret-string "lsv2_pt_YOUR_KEY" \
    --region us-east-1

# Google Places API Key
aws secretsmanager create-secret \
    --name publix-backend/GOOGLE_PLACES_API_KEY \
    --secret-string "YOUR_KEY" \
    --region us-east-1

# AWS Credentials (or use IAM role instead)
aws secretsmanager create-secret \
    --name publix-backend/AWS_ACCESS_KEY_ID \
    --secret-string "YOUR_ACCESS_KEY" \
    --region us-east-1

aws secretsmanager create-secret \
    --name publix-backend/AWS_SECRET_ACCESS_KEY \
    --secret-string "YOUR_SECRET_KEY" \
    --region us-east-1

# Optional: Other API keys
aws secretsmanager create-secret \
    --name publix-backend/CENSUS_API_KEY \
    --secret-string "YOUR_KEY" \
    --region us-east-1
```

## Step 2: Deploy Backend Service

### Option A: Using AWS Console

1. **Navigate to AWS App Runner Console**
   - Go to: https://us-east-1.console.aws.amazon.com/apprunner/home?region=us-east-1
   - Click "Create service"

2. **Configure Source**
   - Choose "Source code repository" (GitHub) or "Container registry" (ECR)
   - If GitHub: Connect repository and select branch
   - If ECR: Select repository and image tag

3. **Configure Build**
   - Build type: Docker
   - Dockerfile path: `infrastructure/Dockerfile.backend`
   - Build command: Leave default or use from `apprunner-backend.yaml`

4. **Configure Service**
   - Service name: `publix-backend`
   - Port: `8000`
   - Start command: `./backend-start.sh`

5. **Configure Environment Variables**
   Add the following environment variables:
   ```
   LANGSMITH_PROJECT=publix-expansion-predictor
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=publix-expansion-data
   S3_REGION=us-east-1
   LOG_LEVEL=INFO
   PYTHONUNBUFFERED=1
   PYTHONPATH=/app/backend
   ALLOWED_ORIGINS=*
   ```

6. **Configure Secrets**
   Add secrets from AWS Secrets Manager:
   - `DATABASE_URL` → Reference `publix-backend/DATABASE_URL`
   - `OPENAI_API_KEY` → Reference `publix-backend/OPENAI_API_KEY`
   - `LANGSMITH_API_KEY` → Reference `publix-backend/LANGSMITH_API_KEY`
   - `GOOGLE_PLACES_API_KEY` → Reference `publix-backend/GOOGLE_PLACES_API_KEY`
   - `AWS_ACCESS_KEY_ID` → Reference `publix-backend/AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY` → Reference `publix-backend/AWS_SECRET_ACCESS_KEY`
   - Add other optional secrets as needed

7. **Configure Auto-Deploy**
   - Enable automatic deployments on code changes (recommended)

8. **Create Service**
   - Review configuration
   - Click "Create & deploy"
   - Wait for deployment (5-10 minutes)

9. **Get Service URL**
   - After deployment, note the service URL (e.g., `https://xxxxx.us-east-1.awsapprunner.com`)
   - This will be needed for frontend configuration

### Option B: Using AWS CLI

```bash
# Create App Runner service configuration file
cat > apprunner-backend-config.json << EOF
{
  "ServiceName": "publix-backend",
  "SourceConfiguration": {
    "CodeRepository": {
      "RepositoryUrl": "https://github.com/YOUR_USERNAME/YOUR_REPO",
      "SourceCodeVersion": {
        "Type": "BRANCH",
        "Value": "main"
      },
      "CodeConfiguration": {
        "ConfigurationSource": "API",
        "CodeConfigurationValues": {
          "Runtime": "DOCKER",
          "BuildCommand": "docker build -f infrastructure/Dockerfile.backend -t publix-backend .",
          "StartCommand": "./backend-start.sh",
          "RuntimeEnvironmentVariables": {
            "LANGSMITH_PROJECT": "publix-expansion-predictor",
            "AWS_REGION": "us-east-1",
            "S3_BUCKET_NAME": "publix-expansion-data",
            "S3_REGION": "us-east-1",
            "LOG_LEVEL": "INFO",
            "PYTHONUNBUFFERED": "1",
            "PYTHONPATH": "/app/backend",
            "ALLOWED_ORIGINS": "*"
          },
          "RuntimeEnvironmentSecrets": {
            "DATABASE_URL": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:publix-backend/DATABASE_URL",
            "OPENAI_API_KEY": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:publix-backend/OPENAI_API_KEY",
            "LANGSMITH_API_KEY": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:publix-backend/LANGSMITH_API_KEY",
            "GOOGLE_PLACES_API_KEY": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:publix-backend/GOOGLE_PLACES_API_KEY",
            "AWS_ACCESS_KEY_ID": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:publix-backend/AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:publix-backend/AWS_SECRET_ACCESS_KEY"
          }
        }
      }
    }
  },
  "InstanceConfiguration": {
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  },
  "AutoScalingConfigurationArn": "arn:aws:apprunner:us-east-1:ACCOUNT_ID:autoscalingconfiguration/default/1/00000000000000000000000000000001"
}
EOF

# Create the service
aws apprunner create-service \
    --cli-input-json file://apprunner-backend-config.json \
    --region us-east-1
```

## Step 3: Update Backend CORS Configuration

After backend is deployed, update the `ALLOWED_ORIGINS` environment variable:

1. Go to App Runner service → Configuration → Environment variables
2. Update `ALLOWED_ORIGINS` with frontend URL (will be set after frontend deployment)
3. Or update it to: `https://your-frontend-url.run.app` (after frontend deployment)

## Step 4: Deploy Frontend Service

### Option A: Using AWS Console

1. **Navigate to AWS App Runner Console**
   - Click "Create service"

2. **Configure Source**
   - Choose "Source code repository" (GitHub) or "Container registry" (ECR)
   - If GitHub: Connect repository and select branch
   - If ECR: Select repository and image tag

3. **Configure Build**
   - Build type: Docker
   - Dockerfile path: `infrastructure/Dockerfile.frontend`
   - Build command: `docker build -f infrastructure/Dockerfile.frontend --build-arg VITE_API_URL=https://YOUR_BACKEND_URL.run.app/api -t publix-frontend .`
   - Replace `YOUR_BACKEND_URL` with actual backend App Runner URL

4. **Configure Service**
   - Service name: `publix-frontend`
   - Port: `8080`
   - Start command: `nginx -g "daemon off;"`

5. **Configure Environment Variables**
   Add:
   ```
   VITE_API_URL=https://YOUR_BACKEND_URL.run.app/api
   ```
   Replace `YOUR_BACKEND_URL` with actual backend App Runner URL

6. **Create Service**
   - Review configuration
   - Click "Create & deploy"
   - Wait for deployment (5-10 minutes)

7. **Get Frontend Service URL**
   - Note the frontend service URL

### Option B: Using AWS CLI

```bash
# Get backend service URL first
BACKEND_URL=$(aws apprunner describe-service \
    --service-arn arn:aws:apprunner:us-east-1:ACCOUNT_ID:service/publix-backend/xxxxx \
    --region us-east-1 \
    --query 'Service.ServiceUrl' \
    --output text)

# Create frontend service configuration
cat > apprunner-frontend-config.json << EOF
{
  "ServiceName": "publix-frontend",
  "SourceConfiguration": {
    "CodeRepository": {
      "RepositoryUrl": "https://github.com/YOUR_USERNAME/YOUR_REPO",
      "SourceCodeVersion": {
        "Type": "BRANCH",
        "Value": "main"
      },
      "CodeConfiguration": {
        "ConfigurationSource": "API",
        "CodeConfigurationValues": {
          "Runtime": "DOCKER",
          "BuildCommand": "docker build -f infrastructure/Dockerfile.frontend --build-arg VITE_API_URL=${BACKEND_URL}/api -t publix-frontend .",
          "StartCommand": "nginx -g \"daemon off;\"",
          "RuntimeEnvironmentVariables": {
            "VITE_API_URL": "${BACKEND_URL}/api"
          }
        }
      }
    }
  },
  "InstanceConfiguration": {
    "Cpu": "0.5 vCPU",
    "Memory": "1 GB"
  }
}
EOF

# Create the service
aws apprunner create-service \
    --cli-input-json file://apprunner-frontend-config.json \
    --region us-east-1
```

## Step 5: Update Backend CORS with Frontend URL

After frontend is deployed:

1. Go to Backend App Runner service → Configuration → Environment variables
2. Update `ALLOWED_ORIGINS` to: `https://your-frontend-url.run.app`
3. Save and redeploy

## Step 6: Verify Deployment

### Test Backend

```bash
# Get backend URL
BACKEND_URL=$(aws apprunner describe-service \
    --service-arn arn:aws:apprunner:us-east-1:ACCOUNT_ID:service/publix-backend/xxxxx \
    --region us-east-1 \
    --query 'Service.ServiceUrl' \
    --output text)

# Test health endpoint
curl ${BACKEND_URL}/health

# Test API docs
curl ${BACKEND_URL}/docs
```

### Test Frontend

1. Open frontend App Runner URL in browser
2. Verify it loads correctly
3. Test API calls from frontend
4. Check browser console for errors

## Step 7: Configure Custom Domains (Optional)

### Backend Custom Domain

1. Go to App Runner service → Custom domains
2. Add domain: `api.yourdomain.com`
3. Follow DNS configuration instructions

### Frontend Custom Domain

1. Go to App Runner service → Custom domains
2. Add domain: `app.yourdomain.com` or `yourdomain.com`
3. Follow DNS configuration instructions

## Environment Variables Reference

### Backend Environment Variables

**Non-sensitive (set directly):**
- `LANGSMITH_PROJECT` - LangSmith project name
- `AWS_REGION` - AWS region (us-east-1)
- `S3_BUCKET_NAME` - S3 bucket name
- `S3_REGION` - S3 region
- `LOG_LEVEL` - Logging level (INFO, DEBUG, etc.)
- `ALLOWED_ORIGINS` - CORS allowed origins (comma-separated)
- `PYTHONUNBUFFERED` - Python output buffering
- `PYTHONPATH` - Python path

**Sensitive (from Secrets Manager):**
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key
- `LANGSMITH_API_KEY` - LangSmith API key
- `GOOGLE_PLACES_API_KEY` - Google Places API key
- `CENSUS_API_KEY` - US Census API key (optional)
- `SMARTY_AUTH_ID` - Smarty API auth ID (optional)
- `SMARTY_API_KEY` - Smarty API key (optional)
- `NEWS_API_KEY` - NewsAPI key (optional)
- `BLS_API_KEY` - Bureau of Labor Statistics API key (optional)
- `FRED_API_KEY` - FRED API key (optional)
- `AWS_ACCESS_KEY_ID` - AWS access key (or use IAM role)
- `AWS_SECRET_ACCESS_KEY` - AWS secret key (or use IAM role)

### Frontend Environment Variables

- `VITE_API_URL` - Backend API URL (e.g., `https://backend-url.run.app/api`)

## Troubleshooting

### Backend Issues

**Database Connection Failed**
- Verify RDS security group allows App Runner IP ranges
- Check DATABASE_URL secret is correct
- Verify database is accessible from App Runner VPC

**Migrations Failed**
- Check logs in App Runner service logs
- Verify Alembic configuration
- Ensure database user has CREATE TABLE permissions

**API Not Responding**
- Check health endpoint: `/health`
- Review App Runner service logs
- Verify PORT environment variable is set correctly

### Frontend Issues

**API Calls Failing**
- Verify VITE_API_URL is set correctly
- Check CORS configuration in backend
- Verify backend service is running
- Check browser console for CORS errors

**Build Failed**
- Check build logs in App Runner
- Verify Dockerfile.frontend is correct
- Ensure all dependencies are in package.json

**404 Errors on Routes**
- Verify nginx.conf is correct
- Check that try_files directive includes `/index.html`

### General Issues

**Service Won't Start**
- Check App Runner service logs
- Verify Dockerfile syntax
- Check environment variables are set correctly
- Verify secrets are accessible

**Slow Deployments**
- App Runner builds can take 5-10 minutes
- Check build logs for errors
- Verify source code repository is accessible

## Cost Optimization

- **Backend**: Start with 1 vCPU, 2 GB RAM (can scale up)
- **Frontend**: Start with 0.5 vCPU, 1 GB RAM (usually sufficient)
- **Auto-scaling**: Configure based on traffic patterns
- **Idle Timeout**: Set appropriate timeout to reduce costs

## Monitoring

- Use CloudWatch Logs for application logs
- Set up CloudWatch Alarms for service health
- Monitor App Runner service metrics (CPU, memory, requests)
- Set up alerts for deployment failures

## Updating Services

### Manual Update

1. Push code changes to GitHub
2. App Runner will auto-deploy if auto-deploy is enabled
3. Or manually trigger deployment from console

### Rollback

1. Go to App Runner service → Deployments
2. Select previous successful deployment
3. Click "Rollback"

## Security Best Practices

1. **Use IAM Roles**: Instead of AWS credentials, use IAM roles for App Runner
2. **Secrets Management**: Store all secrets in AWS Secrets Manager
3. **CORS**: Restrict ALLOWED_ORIGINS to specific frontend URL
4. **HTTPS**: App Runner provides HTTPS automatically
5. **Database**: Use RDS security groups to restrict access
6. **Environment Variables**: Don't commit secrets to repository

## Next Steps

After deployment:
1. Set up CloudWatch monitoring and alerts
2. Configure custom domains
3. Set up CI/CD pipeline for automatic deployments
4. Configure auto-scaling based on traffic
5. Set up backup strategy for database
6. Configure CloudFront CDN for frontend (optional)

## Support

For issues:
- Check AWS App Runner documentation: https://docs.aws.amazon.com/apprunner/
- Review CloudWatch logs
- Check service health in App Runner console

