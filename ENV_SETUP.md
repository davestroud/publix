# Environment Variables Setup Guide

This guide explains where to find each value needed for your `.env` file.

## Location of .env File

Create your `.env` file in the `backend/` directory:
```bash
cd backend
cp .env.example .env
# Then edit .env with your actual values
```

## Required Environment Variables

### 1. OpenAI API Key

**Variable**: `OPENAI_API_KEY`

**Where to get it**:
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to **API Keys** section: https://platform.openai.com/api-keys
4. Click **"Create new secret key"**
5. Copy the key (it starts with `sk-...`)
6. **Important**: Save it immediately - you won't be able to see it again!

**Example**:
```
OPENAI_API_KEY=sk-proj-abc123xyz789...
```

---

### 2. LangSmith API Key

**Variable**: `LANGSMITH_API_KEY`

**Where to get it**:
1. Go to https://smith.langchain.com/
2. Sign up or log in (can use GitHub/GitLab)
3. Navigate to **Settings** → **API Keys**
4. Click **"Create API Key"**
5. Copy the key

**Example**:
```
LANGSMITH_API_KEY=lsv2_pt_abc123...
```

**Variable**: `LANGSMITH_PROJECT`

**Value**: This is just a project name for organizing your traces. You can use:
```
LANGSMITH_PROJECT=publix-expansion-predictor
```

---

### 3. Database URL

**Variable**: `DATABASE_URL`

**Where to get it**: Depends on your setup:

#### Option A: Local PostgreSQL Database

If running PostgreSQL locally:
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/publix_db
```

**To set up locally**:
1. Install PostgreSQL: https://www.postgresql.org/download/
2. Create database:
   ```bash
   createdb publix_db
   # Or using psql:
   psql -U postgres -c "CREATE DATABASE publix_db;"
   ```
3. Use your PostgreSQL username and password

**Example**:
```
DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/publix_db
```

#### Option B: AWS RDS Database

After creating RDS database (see `infrastructure/rds-setup.md`):

1. **Get the endpoint** from AWS Console or CLI:
   ```bash
   aws rds describe-db-instances \
     --db-instance-identifier publix-expansion-db \
     --query "DBInstances[0].Endpoint.Address" \
     --output text
   ```

2. **Get the password** from Secrets Manager (if using Terraform/scripts):
   ```bash
   aws secretsmanager get-secret-value \
     --secret-id publix-db-password \
     --query SecretString \
     --output text
   ```

3. **Construct the connection string**:
   ```
   DATABASE_URL=postgresql://publix_admin:your_password@your-endpoint.region.rds.amazonaws.com:5432/publix_db
   ```

**Example**:
```
DATABASE_URL=postgresql://publix_admin:MySecurePass123@publix-expansion-db.abc123.us-east-1.rds.amazonaws.com:5432/publix_db
```

---

### 4. AWS Credentials

**Variables**: 
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`

**Where to get them**:

#### Option A: Using AWS CLI (if already configured)

If you've run `aws configure`, your credentials are stored in `~/.aws/credentials`. You can:

1. **Read from existing config**:
   ```bash
   cat ~/.aws/credentials
   ```

2. **Or use AWS CLI to get your current identity**:
   ```bash
   aws sts get-caller-identity
   ```

#### Option B: Create New IAM User

1. Go to AWS Console → **IAM** → **Users**
2. Click **"Add users"**
3. Username: `publix-app-user` (or your choice)
4. Select **"Programmatic access"**
5. Attach policies:
   - `AmazonS3FullAccess` (for S3 bucket access)
   - `AmazonRDSFullAccess` (if managing RDS)
   - Or create custom policy with minimal permissions
6. Click **"Create user"**
7. **Important**: Copy both:
   - **Access key ID** (starts with `AKIA...`)
   - **Secret access key** (you'll only see this once!)

**Example**:
```
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
```

**Note**: For App Runner deployment, you may not need these in `.env` if using IAM roles.

---

### 5. S3 Bucket Name

**Variable**: `S3_BUCKET_NAME`

**Where to get/create it**:

#### Option A: Use Existing Bucket

If you already have an S3 bucket:
```
S3_BUCKET_NAME=your-existing-bucket-name
```

#### Option B: Create New Bucket

1. Go to AWS Console → **S3**
2. Click **"Create bucket"**
3. Bucket name: `publix-expansion-data` (must be globally unique)
4. Region: Choose your region (e.g., `us-east-1`)
5. Click **"Create bucket"**

**Example**:
```
S3_BUCKET_NAME=publix-expansion-data
```

**Or create via CLI**:
```bash
aws s3 mb s3://publix-expansion-data --region us-east-1
```

---

### 6. Application Configuration

**Variables**: 
- `ENVIRONMENT`
- `LOG_LEVEL`

These are optional and have defaults:

```
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Options for LOG_LEVEL**:
- `DEBUG` - Most verbose
- `INFO` - Standard logging (recommended)
- `WARNING` - Only warnings and errors
- `ERROR` - Only errors

---

## Complete .env Example

Here's a complete example `.env` file:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-abc123xyz789def456ghi012jkl345mno678pqr901stu234vwx567yz

# LangSmith Configuration
LANGSMITH_API_KEY=lsv2_pt_abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
LANGSMITH_PROJECT=publix-expansion-predictor

# Database Configuration (Local)
DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/publix_db

# Database Configuration (AWS RDS) - Use this instead of local for production
# DATABASE_URL=postgresql://publix_admin:SecurePass123@publix-expansion-db.abc123.us-east-1.rds.amazonaws.com:5432/publix_db

# AWS Configuration
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
S3_BUCKET_NAME=publix-expansion-data

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## Quick Setup Checklist

- [ ] Get OpenAI API key from https://platform.openai.com/api-keys
- [ ] Get LangSmith API key from https://smith.langchain.com/
- [ ] Set up PostgreSQL database (local or RDS)
- [ ] Get database connection string
- [ ] Create AWS IAM user with S3 access
- [ ] Get AWS Access Key ID and Secret Access Key
- [ ] Create S3 bucket or use existing one
- [ ] Copy all values into `backend/.env` file
- [ ] **Never commit `.env` to git!** (it's in `.gitignore`)

---

## Security Best Practices

1. ✅ **Never commit `.env` to version control** (already in `.gitignore`)
2. ✅ **Use strong passwords** for database
3. ✅ **Rotate API keys regularly**
4. ✅ **Use IAM roles** instead of access keys when possible (for AWS deployments)
5. ✅ **Store secrets in AWS Secrets Manager** for production
6. ✅ **Limit IAM permissions** to only what's needed
7. ✅ **Use different credentials** for development vs production

---

## Troubleshooting

### "Invalid API Key" Error
- Check that you copied the entire key (no extra spaces)
- Verify the key is active in OpenAI/LangSmith dashboard
- Ensure you have credits/quota available

### "Database Connection Failed"
- Verify PostgreSQL is running: `pg_isready` or `psql -l`
- Check DATABASE_URL format is correct
- Verify username/password are correct
- For RDS: Check security group allows your IP/VPC

### "AWS Access Denied"
- Verify IAM user has correct permissions
- Check AWS_REGION matches your resources
- Verify access keys are correct
- Check IAM user policies

### "S3 Bucket Not Found"
- Verify bucket name is correct (case-sensitive)
- Check bucket exists in the specified region
- Verify IAM user has S3 permissions

---

## Next Steps

After setting up your `.env` file:

1. **Test database connection**:
   ```bash
   cd backend
   poetry run python -c "from app.services.database import engine; print('Connected!' if engine else 'Failed')"
   ```

2. **Run migrations**:
   ```bash
   poetry run alembic upgrade head
   ```

3. **Start the backend**:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

4. **Verify API is working**:
   - Visit http://localhost:8000/docs
   - Try the `/health` endpoint

