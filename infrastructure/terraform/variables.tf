variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability Zones to use (avoid DescribeAvailabilityZones in restricted accounts)"
  type        = list(string)
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_backup_retention_period" {
  description = "Number of days to retain automated RDS backups (0 to disable)"
  type        = number
  default     = 7
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "shelter_db"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "shelter_admin"
  sensitive   = true
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

variable "backend_cpu" {
  description = "CPU units for backend container (1024 = 1 vCPU)"
  type        = number
  default     = 256
}

variable "backend_memory" {
  description = "Memory for backend container in MB"
  type        = number
  default     = 512
}

variable "frontend_cpu" {
  description = "CPU units for frontend container"
  type        = number
  default     = 256
}

variable "frontend_memory" {
  description = "Memory for frontend container in MB"
  type        = number
  default     = 512
}

variable "backend_desired_count" {
  description = "Desired number of backend tasks"
  type        = number
  default     = 1
}

variable "frontend_desired_count" {
  description = "Desired number of frontend tasks"
  type        = number
  default     = 1
}

variable "django_secret_key" {
  description = "Django secret key"
  type        = string
  sensitive   = true
}

variable "allowed_hosts" {
  description = "Comma-separated ALLOWED_HOSTS for Django"
  type        = string
  default     = "*"
}

variable "oauth_client_id" {
  description = "OAuth client ID for frontend"
  type        = string
  default     = "shelter-frontend"
}

variable "ecs_task_role_name" {
  description = "Existing IAM role name for ECS tasks (Learner Lab uses LabRole)"
  type        = string
  default     = "LabRole"
}

variable "secure_ssl_redirect" {
  description = "Enable Django SECURE_SSL_REDIRECT"
  type        = bool
  default     = false
}

variable "session_cookie_secure" {
  description = "Enable Django SESSION_COOKIE_SECURE"
  type        = bool
  default     = false
}

variable "csrf_cookie_secure" {
  description = "Enable Django CSRF_COOKIE_SECURE"
  type        = bool
  default     = false
}
