# AWS Lightsail Containers Deployment Guide

This guide provides instructions for deploying the Publix Expansion Predictor application to AWS Lightsail Containers.

## Why Lightsail Containers?

- **Simpler**: No complex health check configurations like App Runner
- **Reliable**: Less prone to deployment failures
- **Cost-effective**: Predictable pricing (~$14/month for both services)
- **Easy management**: Simple web console and CLI
- **Works with ECR**: Can use existing Docker images

## Prerequisites

- AWS Account
- AWS CLI configured
- Docker images in ECR (or build new ones)
- RDS PostgreSQL database
- S3 bucket
- Secrets in AWS Secrets Manager

## Architecture

```
┌─────────────────────────┐
│  Lightsail Containers   │
│  - Backend Service       │
│  - Frontend Service      │
└──────────┬───────────────┘
           │
           ▼
┌─────────────────────────┐
│  Existing Resources     │
│  - RDS PostgreSQL       │
│  - S3 Bucket            │
│  - Secrets Manager      │
└─────────────────────────┘
```

## Step 1: Prepare Docker Images

Build and push Docker images to ECR:

```bash
# Authenticate with ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 022398263250.dkr.ecr.us-east-1.amazonaws.com

# Build backend
docker build -f infrastructure/Dockerfile.backend -t publix-backend:latest .
docker tag publix-backend:latest 022398263250.dkr.ecr.us-east-1.amazonaws.com/publix-backend:latest
docker push 022398263250.dkr.ecr.us-east-1.amazonaws.com/publix-backend:latest

# Build frontend (after backend URL is known)
docker build -f infrastructure/Dockerfile.frontend --build-arg VITE_API_URL=https://BACKEND_URL/api -t publix-frontend:latest .
docker tag publix-frontend:latest 022398263250.dkr.ecr.us-east-1.amazonaws.com/publix-frontend:latest
docker push 022398263250.dkr.ecr.us-east-1.amazonaws.com/publix-frontend:latest
```

## Step 2: Create Backend Lightsail Container Service

### Using AWS CLI

```bash
# Create the service
aws lightsail create-container-service \
  --service-name publix-backend \
  --power nano \
  --scale 1 \
  --region us-east-1

# Enable ECR access
aws lightsail update-container-service \
  --service-name publix-backend \
  --private-registry-access ecrImagePullerRole={isActive=true} \
  --region us-east-1

# Deploy container (use the JSON files created in infrastructure/)
aws lightsail create-container-service-deployment \
  --service-name publix-backend \
  --containers file://infrastructure/lightsail-backend-containers.json \
  --public-endpoint file://infrastructure/lightsail-backend-endpoint.json \
  --region us-east-1
```

### Using AWS Console

1. Go to AWS Lightsail Console
2. Click "Containers" → "Create container service"
3. Configure:
   - Service name: `publix-backend`
   - Power: `nano` (0.25 vCPU, 0.5 GB RAM)
   - Scale: `1`
4. Click "Create"
5. After service is created, go to "Deployments" tab
6. Click "Create deployment"
7. Configure:
   - Container name: `backend`
   - Image: `022398263250.dkr.ecr.us-east-1.amazonaws.com/publix-backend:latest`
   - Port: `8000` → `HTTP`
   - Environment variables: Add all from Secrets Manager
   - Public endpoint: Enable
   - Health check: Path `/health`, Interval 30s, Timeout 5s
8. Click "Deploy"

## Step 3: Create Frontend Lightsail Container Service

After backend is deployed and URL is available:

```bash
# Create the service
aws lightsail create-container-service \
  --service-name publix-frontend \
  --power nano \
  --scale 1 \
  --region us-east-1

# Enable ECR access
aws lightsail update-container-service \
  --service-name publix-frontend \
  --private-registry-access ecrImagePullerRole={isActive=true} \
  --region us-east-1

# Deploy container
aws lightsail create-container-service-deployment \
  --service-name publix-frontend \
  --containers file://infrastructure/lightsail-frontend-containers.json \
  --public-endpoint file://infrastructure/lightsail-frontend-endpoint.json \
  --region us-east-1
```

## Step 4: Update Backend CORS

After frontend is deployed, update backend CORS:

```bash
# Update backend deployment with frontend URL in ALLOWED_ORIGINS
aws lightsail create-container-service-deployment \
  --service-name publix-backend \
  --containers file://infrastructure/lightsail-backend-containers-updated.json \
  --public-endpoint file://infrastructure/lightsail-backend-endpoint.json \
  --region us-east-1
```

## Step 5: Verify Deployment

```bash
# Check service status
aws lightsail get-container-services --region us-east-1

# Test health endpoints
BACKEND_URL=$(aws lightsail get-container-services --service-name publix-backend --region us-east-1 --query 'containerServices[0].url' --output text)
FRONTEND_URL=$(aws lightsail get-container-services --service-name publix-frontend --region us-east-1 --query 'containerServices[0].url' --output text)

curl $BACKEND_URL/health
curl $FRONTEND_URL/health
```

## Configuration Files

The following files are created in `infrastructure/`:

- `lightsail-backend.json` - Backend service configuration
- `lightsail-frontend.json` - Frontend service configuration
- `lightsail-backend-containers.json` - Backend container deployment
- `lightsail-frontend-containers.json` - Frontend container deployment
- `lightsail-backend-endpoint.json` - Backend public endpoint config
- `lightsail-frontend-endpoint.json` - Frontend public endpoint config

## Environment Variables

### Backend
- `LANGSMITH_PROJECT=publix-expansion-predictor`
- `AWS_REGION=us-east-1`
- `S3_BUCKET_NAME=publix-expansion-data`
- `S3_REGION=us-east-1`
- `LOG_LEVEL=INFO`
- `PYTHONUNBUFFERED=1`
- `PYTHONPATH=/app/backend`
- `ALLOWED_ORIGINS=https://<frontend-url>`
- Plus secrets from Secrets Manager

### Frontend
- `VITE_API_URL=https://<backend-url>/api`

## Health Checks

Both services use simple HTTP health checks:
- Path: `/health`
- Interval: 30 seconds
- Timeout: 5 seconds
- Healthy threshold: 2
- Unhealthy threshold: 2
- Success codes: 200

## Cost Estimate

- Backend: ~$7/month (nano power, 1 container)
- Frontend: ~$7/month (nano power, 1 container)
- **Total: ~$14/month**

## Troubleshooting

### Services show "No Such Service" (404)
- Containers haven't been deployed yet
- Wait for deployment to complete
- Check deployment status in console

### Services show "503 Service Temporarily Unavailable"
- Containers are starting up
- Wait a few minutes for containers to initialize
- Check container logs in Lightsail console

### ECR Image Pull Failures
- Ensure ECR access is enabled: `ecrImagePullerRole={isActive=true}`
- Verify image exists in ECR
- Check IAM permissions

### Health Check Failures
- Verify health endpoint responds: `curl https://<service-url>/health`
- Check container logs
- Ensure ports are correctly configured

## Monitoring

```bash
# Check service status
aws lightsail get-container-services --region us-east-1

# View logs (in AWS Console)
# Go to Lightsail → Container Services → Service → Logs tab
```

## Advantages Over App Runner

1. **Simpler Health Checks**: No complex timing requirements
2. **More Reliable**: Fewer deployment failures
3. **Easier Management**: Intuitive console interface
4. **Better Logs**: Easier to view and debug
5. **Predictable Pricing**: Simple cost model

