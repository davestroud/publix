# RDS Database Setup with Terraform

This directory contains Terraform configuration to provision an RDS PostgreSQL database for the Publix Expansion Predictor application.

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **Terraform** installed (>= 1.0)
3. **AWS Account** with permissions to create:
   - RDS instances
   - VPC resources (subnets, security groups)
   - Secrets Manager secrets

## Quick Start

1. **Initialize Terraform**:
```bash
cd infrastructure/rds-terraform
terraform init
```

2. **Review the plan**:
```bash
terraform plan
```

3. **Apply the configuration**:
```bash
terraform apply
```

4. **Get the connection details**:
```bash
terraform output
```

## Configuration

Edit `variables.tf` or create `terraform.tfvars` to customize:

```hcl
aws_region              = "us-east-1"
db_instance_class        = "db.t3.small"  # For production, use larger instance
db_engine_version        = "15.4"
db_username              = "publix_admin"
allocated_storage        = 50
max_allocated_storage    = 200
publicly_accessible      = true
multi_az                 = false  # Set to true for production
skip_final_snapshot      = false  # Set to false for production
performance_insights_enabled = true  # Enable for production
```

## Getting the Password

The database password is stored in AWS Secrets Manager. Retrieve it:

```bash
aws secretsmanager get-secret-value \
  --secret-id publix-db-password \
  --query SecretString \
  --output text
```

Or use the ARN from Terraform output:
```bash
SECRET_ARN=$(terraform output -raw database_password_secret_arn)
aws secretsmanager get-secret-value \
  --secret-id $SECRET_ARN \
  --query SecretString \
  --output text
```

## Connection String

After deployment, construct the connection string:

```bash
DB_ENDPOINT=$(terraform output -raw database_endpoint)
DB_PORT=$(terraform output -raw database_port)
DB_NAME=$(terraform output -raw database_name)
DB_USER=$(terraform output -raw database_username)
DB_PASSWORD=$(aws secretsmanager get-secret-value --secret-id publix-db-password --query SecretString --output text)

echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_ENDPOINT:$DB_PORT/$DB_NAME"
```

## Running Migrations

After the database is created, run Alembic migrations:

```bash
cd backend
export DATABASE_URL="postgresql://[username]:[password]@[endpoint]:[port]/publix_db"
poetry run alembic upgrade head
```

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will delete the database and all data. Make sure you have backups if needed.

## Security Notes

1. **Password**: The password is automatically generated and stored in AWS Secrets Manager
2. **Network**: The security group allows access from within the VPC
3. **Encryption**: Storage encryption is enabled by default
4. **Public Access**: Set `publicly_accessible = false` for production if you don't need public access

## Troubleshooting

### Connection Issues

1. Check security group rules allow traffic from your IP/VPC
2. Verify the database is in "available" state:
   ```bash
   aws rds describe-db-instances --db-instance-identifier publix-expansion-db
   ```

### Permission Issues

Ensure your AWS credentials have these permissions:
- `rds:*`
- `ec2:DescribeVpcs`
- `ec2:DescribeSubnets`
- `ec2:CreateSecurityGroup`
- `ec2:AuthorizeSecurityGroupIngress`
- `secretsmanager:*`

## Cost Optimization

- Use `db.t3.micro` for development/testing
- Use `db.t3.small` or larger for production
- Enable `multi_az` only for production (doubles cost)
- Set appropriate `max_allocated_storage` based on expected growth
- Consider using RDS Proxy for connection pooling in production

