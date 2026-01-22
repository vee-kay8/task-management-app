variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "backend_security_group_id" {
  description = "Security group ID for backend ECS tasks"
  type        = string
}

variable "backend_target_group_arn" {
  description = "ARN of the backend target group"
  type        = string
}

variable "frontend_target_group_arn" {
  description = "ARN of the frontend target group"
  type        = string
}

variable "execution_role_arn" {
  description = "ARN of the ECS task execution role"
  type        = string
}

variable "backend_image_url" {
  description = "URL of the backend container image"
  type        = string
}

variable "frontend_image_url" {
  description = "URL of the frontend container image"
  type        = string
}

variable "database_url" {
  description = "Database connection URL"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Flask secret key"
  type        = string
  sensitive   = true
}

variable "jwt_secret_key" {
  description = "JWT secret key"
  type        = string
  sensitive   = true
}

variable "api_url" {
  description = "API URL for frontend"
  type        = string
}
