terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment and configure if using remote state
  # backend "s3" {
  #   bucket = "your-terraform-state-bucket"
  #   key    = "publix-expansion/rds/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region
}

# Data source to get default VPC
data "aws_vpc" "default" {
  default = true
}

# Data source to get subnets in default VPC
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Random password for database
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Store password in AWS Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name        = "publix-db-password"
  description = "Password for Publix Expansion Predictor RDS database"
  
  tags = {
    Name    = "publix-db-password"
    Project = "publix-expansion-predictor"
  }
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = random_password.db_password.result
}

# DB Subnet Group
resource "aws_db_subnet_group" "publix_db" {
  name       = "publix-db-subnet-group"
  subnet_ids = data.aws_subnets.default.ids

  tags = {
    Name    = "publix-db-subnet-group"
    Project = "publix-expansion-predictor"
  }
}

# Security Group for RDS
resource "aws_security_group" "rds" {
  name        = "publix-db-sg"
  description = "Security group for Publix Expansion Predictor RDS"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "PostgreSQL from VPC"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.default.cidr_block]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "publix-db-sg"
    Project = "publix-expansion-predictor"
  }
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "publix_db" {
  identifier = "publix-expansion-db"

  engine         = "postgres"
  engine_version = var.db_engine_version
  instance_class = var.db_instance_class

  db_name  = "publix_db"
  username = var.db_username
  password = random_password.db_password.result

  allocated_storage     = var.allocated_storage
  max_allocated_storage  = var.max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true

  db_subnet_group_name   = aws_db_subnet_group.publix_db.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"

  publicly_accessible = var.publicly_accessible
  multi_az            = var.multi_az

  skip_final_snapshot       = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : "publix-db-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  
  performance_insights_enabled = var.performance_insights_enabled
  performance_insights_retention_period = var.performance_insights_enabled ? 7 : null

  tags = {
    Name    = "publix-expansion-db"
    Project = "publix-expansion-predictor"
  }
}

# Outputs
output "db_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.publix_db.endpoint
}

output "db_port" {
  description = "RDS instance port"
  value       = aws_db_instance.publix_db.port
}

output "db_name" {
  description = "Database name"
  value       = aws_db_instance.publix_db.db_name
}

output "db_username" {
  description = "Database master username"
  value       = aws_db_instance.publix_db.username
}

output "db_password_secret_arn" {
  description = "ARN of the secret storing the database password"
  value       = aws_secretsmanager_secret.db_password.arn
}

output "connection_string" {
  description = "Database connection string (password stored in Secrets Manager)"
  value       = "postgresql://${aws_db_instance.publix_db.username}:<password-from-secrets-manager>@${aws_db_instance.publix_db.endpoint}:${aws_db_instance.publix_db.port}/${aws_db_instance.publix_db.db_name}"
  sensitive   = true
}

