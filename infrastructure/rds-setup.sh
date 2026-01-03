#!/bin/bash
# Script to create RDS PostgreSQL database for Publix Expansion Predictor

set -e

# Configuration
DB_INSTANCE_IDENTIFIER="publix-expansion-db"
DB_NAME="publix_db"
DB_USERNAME="publix_admin"
# Generate random password (RDS allows: printable ASCII except '/', '@', '"', ' ')
DB_PASSWORD=$(openssl rand -base64 32 | tr -d '/@" ' | head -c 32)
DB_CLASS="db.t3.micro"  # Change to db.t3.small or larger for production
DB_ENGINE="postgres"
DB_ENGINE_VERSION="15.15"
ALLOCATED_STORAGE=20
MAX_ALLOCATED_STORAGE=100
VPC_ID=""  # Will be detected automatically if not set
SUBNET_GROUP_NAME="publix-db-subnet-group"
SECURITY_GROUP_NAME="publix-db-sg"
REGION="${AWS_REGION:-us-east-1}"

echo "Creating RDS PostgreSQL database..."
echo "Instance Identifier: $DB_INSTANCE_IDENTIFIER"
echo "Region: $REGION"

# Get default VPC if not specified
if [ -z "$VPC_ID" ]; then
    echo "Detecting default VPC..."
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text --region $REGION)
    echo "Using VPC: $VPC_ID"
fi

# Get subnet IDs from VPC
echo "Getting subnet IDs..."
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[*].SubnetId" --output text --region $REGION)
SUBNET_IDS_ARRAY=($SUBNET_IDS)

if [ ${#SUBNET_IDS_ARRAY[@]} -lt 2 ]; then
    echo "Error: Need at least 2 subnets for RDS subnet group"
    exit 1
fi

# Create DB Subnet Group
echo "Creating DB Subnet Group..."
aws rds create-db-subnet-group \
    --db-subnet-group-name $SUBNET_GROUP_NAME \
    --db-subnet-group-description "Subnet group for Publix Expansion Predictor database" \
    --subnet-ids ${SUBNET_IDS_ARRAY[@]} \
    --region $REGION \
    --tags Key=Name,Value=publix-db-subnet-group Key=Project,Value=publix-expansion-predictor \
    2>/dev/null || echo "Subnet group may already exist"

# Create Security Group
echo "Creating Security Group..."
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name $SECURITY_GROUP_NAME \
    --description "Security group for Publix Expansion Predictor RDS" \
    --vpc-id $VPC_ID \
    --region $REGION \
    --query 'GroupId' \
    --output text 2>/dev/null || \
    aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=$SECURITY_GROUP_NAME" "Name=vpc-id,Values=$VPC_ID" \
    --query "SecurityGroups[0].GroupId" \
    --output text \
    --region $REGION)

echo "Security Group ID: $SECURITY_GROUP_ID"

# Add inbound rule for PostgreSQL (port 5432) from App Runner/VPC
echo "Configuring security group rules..."
aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 5432 \
    --cidr $(aws ec2 describe-vpcs --vpc-ids $VPC_ID --query "Vpcs[0].CidrBlock" --output text --region $REGION) \
    --region $REGION \
    2>/dev/null || echo "Rule may already exist"

# Create RDS Instance
echo "Creating RDS PostgreSQL instance..."
echo "This may take 10-15 minutes..."

aws rds create-db-instance \
    --db-instance-identifier $DB_INSTANCE_IDENTIFIER \
    --db-instance-class $DB_CLASS \
    --engine $DB_ENGINE \
    --engine-version $DB_ENGINE_VERSION \
    --master-username $DB_USERNAME \
    --master-user-password $DB_PASSWORD \
    --allocated-storage $ALLOCATED_STORAGE \
    --max-allocated-storage $MAX_ALLOCATED_STORAGE \
    --db-name $DB_NAME \
    --db-subnet-group-name $SUBNET_GROUP_NAME \
    --vpc-security-group-ids $SECURITY_GROUP_ID \
    --backup-retention-period 7 \
    --storage-type gp3 \
    --storage-encrypted \
    --publicly-accessible \
    --no-multi-az \
    --tags Key=Name,Value=publix-expansion-db Key=Project,Value=publix-expansion-predictor \
    --region $REGION

echo ""
echo "=========================================="
echo "RDS Database Creation Initiated"
echo "=========================================="
echo "Instance Identifier: $DB_INSTANCE_IDENTIFIER"
echo "Database Name: $DB_NAME"
echo "Master Username: $DB_USERNAME"
echo "Master Password: $DB_PASSWORD"
echo ""
echo "IMPORTANT: Save the password above securely!"
echo ""
echo "Waiting for database to be available..."
echo "This will take approximately 10-15 minutes..."
echo ""

# Wait for DB to be available
aws rds wait db-instance-available \
    --db-instance-identifier $DB_INSTANCE_IDENTIFIER \
    --region $REGION

# Get endpoint
DB_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier $DB_INSTANCE_IDENTIFIER \
    --query "DBInstances[0].Endpoint.Address" \
    --output text \
    --region $REGION)

DB_PORT=$(aws rds describe-db-instances \
    --db-instance-identifier $DB_INSTANCE_IDENTIFIER \
    --query "DBInstances[0].Endpoint.Port" \
    --output text \
    --region $REGION)

echo ""
echo "=========================================="
echo "Database Created Successfully!"
echo "=========================================="
echo "Endpoint: $DB_ENDPOINT"
echo "Port: $DB_PORT"
echo "Database Name: $DB_NAME"
echo "Username: $DB_USERNAME"
echo ""
echo "Connection String:"
echo "postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_ENDPOINT:$DB_PORT/$DB_NAME"
echo ""
echo "Update your .env file with:"
echo "DATABASE_URL=postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_ENDPOINT:$DB_PORT/$DB_NAME"
echo ""
echo "For App Runner, store the password in AWS Secrets Manager:"
echo "aws secretsmanager create-secret --name publix-db-password --secret-string '$DB_PASSWORD' --region $REGION"
echo ""

