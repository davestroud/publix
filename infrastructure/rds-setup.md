# RDS Database Setup Guide

This guide provides multiple options for setting up the PostgreSQL database on AWS RDS.

## Option 1: AWS CLI Script (Quickest)

The `rds-setup.sh` script automates the entire RDS setup process.

### Prerequisites
- AWS CLI installed and configured
- Appropriate IAM permissions
- `openssl` installed (for password generation)

### Usage

```bash
cd infrastructure
chmod +x rds-setup.sh
./rds-setup.sh
```

The script will:
1. Detect your default VPC
2. Create a DB subnet group
3. Create a security group
4. Create the RDS PostgreSQL instance
5. Wait for it to be available
6. Output connection details

### Customization

Edit the variables at the top of `rds-setup.sh`:
- `DB_INSTANCE_IDENTIFIER`: Name of your RDS instance
- `DB_CLASS`: Instance size (db.t3.micro, db.t3.small, etc.)
- `REGION`: AWS region
- `ALLOCATED_STORAGE`: Initial storage size

## Option 2: Terraform (Recommended for Production)

Use Terraform for infrastructure as code and better state management.

### Prerequisites
- Terraform >= 1.0 installed
- AWS CLI configured

### Usage

```bash
cd infrastructure/rds-terraform
terraform init
terraform plan
terraform apply
```

See `rds-terraform/README.md` for detailed instructions.

## Option 3: AWS Console (Manual)

1. **Navigate to RDS Console**
   - Go to https://console.aws.amazon.com/rds/
   - Click "Create database"

2. **Choose Engine**
   - Select "PostgreSQL"
   - Choose version 15.4 or later

3. **Template**
   - Select "Free tier" for development or "Production" for production

4. **Settings**
   - DB instance identifier: `publix-expansion-db`
   - Master username: `publix_admin`
   - Master password: Generate a strong password

5. **Instance Configuration**
   - Instance class: `db.t3.micro` (dev) or `db.t3.small` (prod)
   - Storage: 20 GB (auto-scaling enabled)

6. **Connectivity**
   - VPC: Select your default VPC
   - Subnet group: Create new or use default
   - Public access: Yes (for App Runner access)
   - VPC security group: Create new
   - Availability Zone: No preference

7. **Database Authentication**
   - Password authentication

8. **Additional Configuration**
   - Initial database name: `publix_db`
   - Backup retention: 7 days
   - Enable encryption: Yes
   - Performance Insights: Optional

9. **Create Database**
   - Click "Create database"
   - Wait 10-15 minutes for creation

## Post-Creation Setup

### 1. Get Connection Details

From AWS Console:
- Go to RDS → Databases → Your instance
- Note the endpoint and port

From AWS CLI:
```bash
aws rds describe-db-instances \
  --db-instance-identifier publix-expansion-db \
  --query "DBInstances[0].Endpoint"
```

### 2. Update Security Group

Allow access from App Runner or your IP:

```bash
# Get your security group ID
SG_ID=$(aws rds describe-db-instances \
  --db-instance-identifier publix-expansion-db \
  --query "DBInstances[0].VpcSecurityGroups[0].VpcSecurityGroupId" \
  --output text)

# Add rule for VPC access (if using App Runner)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 5432 \
  --cidr <your-vpc-cidr>
```

### 3. Store Password in Secrets Manager

```bash
aws secretsmanager create-secret \
  --name publix-db-password \
  --secret-string "your-database-password-here" \
  --region us-east-1
```

### 4. Update Environment Variables

For local development, update `backend/.env`:
```bash
DATABASE_URL=postgresql://publix_admin:password@endpoint:5432/publix_db
```

For App Runner, add environment variable:
```
DATABASE_URL=postgresql://publix_admin:[password-from-secrets-manager]@[endpoint]:5432/publix_db
```

### 5. Run Database Migrations

```bash
cd backend
export DATABASE_URL="postgresql://publix_admin:password@endpoint:5432/publix_db"
poetry run alembic upgrade head
```

## Connection Testing

Test the connection:

```bash
psql "postgresql://publix_admin:password@endpoint:5432/publix_db"
```

Or using Python:
```python
from sqlalchemy import create_engine
engine = create_engine("postgresql://publix_admin:password@endpoint:5432/publix_db")
with engine.connect() as conn:
    result = conn.execute("SELECT version();")
    print(result.fetchone())
```

## App Runner Integration

To use with AWS App Runner:

1. **Store credentials in Secrets Manager**:
```bash
aws secretsmanager create-secret \
  --name publix-db-credentials \
  --secret-string '{"username":"publix_admin","password":"your-password","endpoint":"your-endpoint","port":"5432","database":"publix_db"}' \
  --region us-east-1
```

2. **Update App Runner configuration** (`infrastructure/apprunner.yaml`):
```yaml
env:
  - name: DATABASE_URL
    value: "postgresql://publix_admin:[password-from-secrets-manager]@[endpoint]:5432/publix_db"
```

Or reference Secrets Manager directly in App Runner console.

## Cost Estimation

- **db.t3.micro**: ~$15/month (free tier eligible for first year)
- **db.t3.small**: ~$30/month
- **Storage**: $0.115/GB/month
- **Backups**: Included for 7 days
- **Data Transfer**: First 100 GB/month free

## Security Best Practices

1. ✅ Use strong passwords (auto-generated by scripts)
2. ✅ Enable encryption at rest
3. ✅ Store passwords in Secrets Manager
4. ✅ Use security groups to restrict access
5. ✅ Enable automated backups
6. ✅ Use Multi-AZ for production (high availability)
7. ✅ Enable Performance Insights for monitoring
8. ✅ Regularly rotate passwords
9. ✅ Use SSL/TLS for connections
10. ✅ Enable CloudWatch logging

## Troubleshooting

### Connection Timeout
- Check security group allows traffic on port 5432
- Verify database is in "available" state
- Check VPC routing tables

### Authentication Failed
- Verify username and password
- Check password hasn't expired
- Ensure user has proper permissions

### Database Not Found
- Verify database name matches (`publix_db`)
- Check initial database name was set correctly

### Performance Issues
- Upgrade instance class
- Enable Performance Insights
- Check CloudWatch metrics
- Review slow query logs

## Next Steps

After database setup:
1. Run migrations: `alembic upgrade head`
2. Seed initial data (if needed)
3. Configure App Runner to use the database
4. Set up monitoring and alerts
5. Configure automated backups schedule

