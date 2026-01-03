output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.publix_db.endpoint
}

output "database_port" {
  description = "RDS instance port"
  value       = aws_db_instance.publix_db.port
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.publix_db.db_name
}

output "database_username" {
  description = "Database master username"
  value       = aws_db_instance.publix_db.username
}

output "database_password_secret_arn" {
  description = "ARN of the secret storing the database password"
  value       = aws_secretsmanager_secret.db_password.arn
}

output "database_connection_string_template" {
  description = "Template for database connection string"
  value       = "postgresql://${aws_db_instance.publix_db.username}:[PASSWORD]@${aws_db_instance.publix_db.endpoint}:${aws_db_instance.publix_db.port}/${aws_db_instance.publix_db.db_name}"
  sensitive   = false
}

