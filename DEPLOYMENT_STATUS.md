# EC2 Deployment Status

## ✅ Instance Launched Successfully

**Instance Details:**
- **Instance ID**: `i-0628cc02ecc0500c7`
- **Public IP**: `13.222.188.198`
- **Instance Type**: `t2.micro` (free tier eligible)
- **Region**: `us-east-1`
- **Status**: Running
- **Key Pair**: `publix-ec2-key` (saved to `~/.ssh/publix-ec2-key.pem`)

**Security Group**: `publix-app-sg` (sg-0cdb21381d81a5b2c)
- Port 22 (SSH) - Open
- Port 8000 (Backend) - Open
- Port 8080 (Frontend) - Open

## 🔗 Access URLs

Once deployed:
- **Backend API**: http://13.222.188.198:8000
- **Frontend App**: http://13.222.188.198:8080
- **Backend Health**: http://13.222.188.198:8000/health
- **Frontend Health**: http://13.222.188.198:8080/health

## 📋 Next Steps to Complete Deployment

### Step 1: SSH Into Instance

The SSH key has been created and saved to `~/.ssh/publix-ec2-key.pem`. Use it to connect:

```bash
ssh -i ~/.ssh/publix-ec2-key.pem ec2-user@<PUBLIC_IP>
```

(Replace `<PUBLIC_IP>` with the actual IP address shown above)

### Step 3: Install Docker and Docker Compose

Once connected, run:

```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install -y docker git
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and back in for group changes
exit
```

Then SSH back in.

### Step 4: Upload Application Files

From your **local machine**, upload the files:

```bash
# Replace <PUBLIC_IP> with your instance IP
PUBLIC_IP="<PUBLIC_IP>"

# Create directory on EC2
ssh -i ~/.ssh/publix-ec2-key.pem ec2-user@$PUBLIC_IP "mkdir -p /home/ec2-user/publix"

# Upload files
scp -i ~/.ssh/publix-ec2-key.pem \
  docker-compose.yml \
  ec2-user@$PUBLIC_IP:/home/ec2-user/publix/

scp -i ~/.ssh/publix-ec2-key.pem -r \
  infrastructure/ \
  backend/ \
  frontend/ \
  ec2-user@$PUBLIC_IP:/home/ec2-user/publix/
```

### Step 5: Create .env File

SSH into the instance and create the `.env` file:

```bash
ssh -i ~/.ssh/publix-ec2-key.pem ec2-user@<PUBLIC_IP>
cd /home/ec2-user/publix
nano .env
```

Add these environment variables (get values from AWS Secrets Manager):

```bash
DATABASE_URL=postgresql://publix_admin:Kk8pKDxT00jm%2BtMbusEXYG%2BoRqHZ2jZp@publix-expansion-db.co1dd6f49wfo.us-east-1.rds.amazonaws.com:5432/publix_db
OPENAI_API_KEY=your-openai-key
LANGSMITH_API_KEY=your-langsmith-key
GOOGLE_PLACES_API_KEY=your-google-places-key
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
VITE_API_URL=http://13.222.188.198:8000/api
```

**OR** load from AWS Secrets Manager:

```bash
cd /home/ec2-user/publix

# Get secrets (you'll need AWS CLI configured on EC2)
aws secretsmanager get-secret-value \
  --secret-id publix-backend/DATABASE_URL \
  --region us-east-1 \
  --query SecretString \
  --output text > .env

# Add other secrets...
echo "VITE_API_URL=http://13.222.188.198:8000/api" >> .env
```

### Step 6: Start the Application

```bash
cd /home/ec2-user/publix

# Build and start
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 7: Verify Deployment

```bash
# Check containers
docker-compose ps

# Test health endpoints
curl http://localhost:8000/health
curl http://localhost:8080/health

# View logs if issues
docker-compose logs backend
docker-compose logs frontend
```

## 🔧 Useful Commands

### View Logs
```bash
ssh -i ~/.ssh/publix-ec2-key.pem ec2-user@<PUBLIC_IP>
cd /home/ec2-user/publix
docker-compose logs -f
```

### Restart Services
```bash
cd /home/ec2-user/publix
docker-compose restart
```

### Stop Services
```bash
cd /home/ec2-user/publix
docker-compose stop
```

### Update Application
```bash
cd /home/ec2-user/publix
# Upload new files, then:
docker-compose up -d --build
```

## 🐛 Troubleshooting

### Can't SSH
- Verify key file permissions: `chmod 400 ~/.ssh/llm_setup.pem`
- Check security group allows SSH from your IP
- Verify instance is running: `aws ec2 describe-instances --instance-ids i-0628cc02ecc0500c7`

### Services won't start
- Check logs: `docker-compose logs`
- Verify .env file exists and has correct values
- Check Docker is running: `sudo systemctl status docker`

### Can't access from browser
- Verify security group allows ports 8000 and 8080
- Check containers are running: `docker-compose ps`
- Test locally on EC2: `curl http://localhost:8000/health`

## 💰 Cost

- **t2.micro**: Free tier (750 hours/month) or ~$7/month
- **Data transfer**: Minimal for non-production
- **Total**: ~$0-7/month

## 📖 Full Documentation

See `infrastructure/SIMPLE_DEPLOYMENT.md` for complete guide.


