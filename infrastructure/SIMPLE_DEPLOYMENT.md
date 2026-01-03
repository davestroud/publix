# Simple EC2 Deployment Guide

This is the simplest deployment option for non-production use. Run everything on a single EC2 instance using Docker Compose.

## Why This Approach?

- ✅ **Simplest**: Just one EC2 instance
- ✅ **Fast**: Deploy in minutes
- ✅ **Cheap**: Use t2.micro (free tier) or t3.micro (~$7/month)
- ✅ **No Complex Config**: Standard Docker Compose
- ✅ **Easy Debugging**: SSH in and check logs
- ✅ **Works Everywhere**: Can run locally too

## Architecture

```
┌─────────────────────────┐
│   Single EC2 Instance   │
│                         │
│  ┌───────────────────┐ │
│  │  Docker Compose   │ │
│  │  - Backend :8000  │ │
│  │  - Frontend :8080 │ │
│  └───────────────────┘ │
│                         │
│  Ports exposed:         │
│  - 8000 (Backend)       │
│  - 8080 (Frontend)      │
└─────────────────────────┘
```

## Step 1: Launch EC2 Instance

### Using AWS Console:

1. Go to EC2 Console → Launch Instance
2. Choose:
   - **AMI**: Amazon Linux 2023 (free tier eligible)
   - **Instance Type**: t2.micro or t3.micro
   - **Key Pair**: Create or select existing
   - **Security Group**: 
     - Allow SSH (22) from your IP
     - Allow HTTP (8000) from anywhere (0.0.0.0/0)
     - Allow HTTP (8080) from anywhere (0.0.0.0/0)
3. Launch instance

### Using AWS CLI:

```bash
# Create security group
aws ec2 create-security-group \
  --group-name publix-app-sg \
  --description "Security group for Publix app" \
  --region us-east-1

# Allow SSH
aws ec2 authorize-security-group-ingress \
  --group-name publix-app-sg \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0 \
  --region us-east-1

# Allow Backend
aws ec2 authorize-security-group-ingress \
  --group-name publix-app-sg \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0 \
  --region us-east-1

# Allow Frontend
aws ec2 authorize-security-group-ingress \
  --group-name publix-app-sg \
  --protocol tcp \
  --port 8080 \
  --cidr 0.0.0.0/0 \
  --region us-east-1

# Launch instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --key-name your-key-name \
  --security-groups publix-app-sg \
  --region us-east-1
```

## Step 2: Setup EC2 Instance

SSH into your instance:

```bash
ssh -i your-key.pem ec2-user@<instance-ip>
```

Run the setup script:

```bash
# Download and run setup script
curl -o- https://raw.githubusercontent.com/your-repo/publix/main/infrastructure/ec2-setup.sh | bash

# OR copy the script to the instance and run it
# scp infrastructure/ec2-setup.sh ec2-user@<instance-ip>:~
# ssh ec2-user@<instance-ip>
# chmod +x ec2-setup.sh
# ./ec2-setup.sh
```

**Important**: Log out and back in after running setup script (for Docker group changes).

## Step 3: Deploy Application

### Option A: Clone from Git

```bash
cd /home/ec2-user/publix
git clone <your-repo-url> .
```

### Option B: Upload Files

```bash
# From your local machine
scp -r . ec2-user@<instance-ip>:~/publix/
```

## Step 4: Configure Environment Variables

Create `.env` file:

```bash
cd /home/ec2-user/publix
nano .env
```

Add your environment variables (see `.env.example`):

```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
OPENAI_API_KEY=your-key
LANGSMITH_API_KEY=your-key
GOOGLE_PLACES_API_KEY=your-key
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-key
```

**OR** load from AWS Secrets Manager:

```bash
# Get secrets from Secrets Manager
aws secretsmanager get-secret-value \
  --secret-id publix-backend/DATABASE_URL \
  --region us-east-1 \
  --query SecretString \
  --output text > .env

# Add other secrets...
```

## Step 5: Update Frontend Backend URL

Edit `docker-compose.yml` and update `VITE_API_URL`:

```yaml
frontend:
  build:
    args:
      - VITE_API_URL=http://<your-ec2-public-ip>:8000/api
```

Or use environment variable:

```bash
export VITE_API_URL=http://<your-ec2-public-ip>:8000/api
docker-compose build frontend
```

## Step 6: Start Services

```bash
cd /home/ec2-user/publix

# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

## Step 7: Access Application

- **Backend**: `http://<ec2-public-ip>:8000`
- **Frontend**: `http://<ec2-public-ip>:8080`
- **Backend Health**: `http://<ec2-public-ip>:8000/health`
- **Frontend Health**: `http://<ec2-public-ip>:8080/health`

## Useful Commands

```bash
# View logs
docker-compose logs -f
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart

# Stop services
docker-compose stop

# Start services
docker-compose start

# Rebuild and restart
docker-compose up -d --build

# Check status
docker-compose ps

# Execute commands in container
docker-compose exec backend bash
docker-compose exec frontend sh
```

## Updating Application

```bash
cd /home/ec2-user/publix

# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build
```

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Check Docker
sudo systemctl status docker

# Check if ports are in use
sudo netstat -tulpn | grep -E '8000|8080'
```

### Can't access from browser
- Check security group allows ports 8000 and 8080
- Check EC2 instance is running
- Verify services are running: `docker-compose ps`

### Database connection issues
- Verify DATABASE_URL is correct
- Check security group allows database access
- Test connection: `docker-compose exec backend python -c "import psycopg2; print('OK')"`

## Cost Estimate

- **t2.micro**: Free tier (750 hours/month) or ~$7/month
- **t3.micro**: ~$7/month
- **Data transfer**: Minimal for non-production
- **Total**: ~$0-7/month

## Security Notes

For production, consider:
- Use HTTPS (add nginx reverse proxy with Let's Encrypt)
- Restrict security group to specific IPs
- Use AWS Systems Manager Parameter Store for secrets
- Enable CloudWatch logging
- Set up automated backups

## Local Development

This same `docker-compose.yml` works locally too:

```bash
# Copy .env.example to .env and fill in values
cp .env.example .env

# Start services
docker-compose up
```

Access at:
- Backend: http://localhost:8000
- Frontend: http://localhost:8080

