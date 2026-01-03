variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
  
  validation {
    condition = can(regex("^db\\.", var.db_instance_class))
    error_message = "Instance class must start with 'db.'"
  }
}

variable "db_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.15"
}

variable "db_username" {
  description = "Master username for the database"
  type        = string
  default     = "publix_admin"
  
  validation {
    condition     = length(var.db_username) >= 1 && length(var.db_username) <= 16
    error_message = "Username must be between 1 and 16 characters."
  }
}

variable "allocated_storage" {
  description = "Initial allocated storage in GB"
  type        = number
  default     = 20
  
  validation {
    condition     = var.allocated_storage >= 20 && var.allocated_storage <= 65536
    error_message = "Allocated storage must be between 20 and 65536 GB."
  }
}

variable "max_allocated_storage" {
  description = "Maximum allocated storage for autoscaling in GB"
  type        = number
  default     = 100
  
  validation {
    condition     = var.max_allocated_storage >= var.allocated_storage
    error_message = "Max allocated storage must be >= allocated storage."
  }
}

variable "publicly_accessible" {
  description = "Whether the database should be publicly accessible"
  type        = bool
  default     = true
}

variable "multi_az" {
  description = "Enable Multi-AZ deployment for high availability"
  type        = bool
  default     = false
}

variable "skip_final_snapshot" {
  description = "Skip final snapshot when destroying (set to false for production)"
  type        = bool
  default     = true
}

variable "performance_insights_enabled" {
  description = "Enable Performance Insights"
  type        = bool
  default     = false
}

