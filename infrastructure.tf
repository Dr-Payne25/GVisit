# GVisit Infrastructure Configuration
# This file provisions AWS resources for the GVisit application

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Variables
variable "project_name" {
  description = "Project name for resource naming"
  default     = "gvisit"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  default     = "production"
}

# Local variables for consistent naming
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Repository  = "github.com/yourusername/gvisit"
  }
  
  bucket_name = "${var.project_name}-journal-backups-${var.environment}"
  table_name  = "${var.project_name}-journal-entries-${var.environment}"
}

# S3 Bucket for Journal Backups
resource "aws_s3_bucket" "journal_backups" {
  bucket = local.bucket_name
  tags   = local.common_tags
}

# Enable versioning for backup safety
resource "aws_s3_bucket_versioning" "journal_backups" {
  bucket = aws_s3_bucket.journal_backups.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "journal_backups" {
  bucket = aws_s3_bucket.journal_backups.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Lifecycle policy to reduce storage costs
resource "aws_s3_bucket_lifecycle_configuration" "journal_backups" {
  bucket = aws_s3_bucket.journal_backups.id

  rule {
    id     = "archive-old-backups"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }
    
    expiration {
      days = 365  # Delete backups older than 1 year
    }
  }
}

# DynamoDB Table for Journal Entries
resource "aws_dynamodb_table" "journal_entries" {
  name         = local.table_name
  billing_mode = "PAY_PER_REQUEST"  # Auto-scaling, pay per request
  hash_key     = "id"

  attribute {
    name = "id"
    type = "N"
  }

  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }

  # Enable server-side encryption
  server_side_encryption {
    enabled = true
  }
  
  tags = local.common_tags
}

# IAM Role for EC2/ECS instances running the application
resource "aws_iam_role" "app_role" {
  name = "${var.project_name}-app-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = ["ec2.amazonaws.com", "ecs-tasks.amazonaws.com"]
        }
      }
    ]
  })
  
  tags = local.common_tags
}

# IAM Policy for application permissions
resource "aws_iam_role_policy" "app_policy" {
  name = "${var.project_name}-app-policy-${var.environment}"
  role = aws_iam_role.app_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.journal_backups.arn,
          "${aws_s3_bucket.journal_backups.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:Scan",
          "dynamodb:Query"
        ]
        Resource = aws_dynamodb_table.journal_entries.arn
      }
    ]
  })
}

# Outputs for application configuration
output "s3_bucket_name" {
  value       = aws_s3_bucket.journal_backups.id
  description = "S3 bucket name for journal backups"
}

output "dynamodb_table_name" {
  value       = aws_dynamodb_table.journal_entries.name
  description = "DynamoDB table name for journal entries"
}

output "iam_role_arn" {
  value       = aws_iam_role.app_role.arn
  description = "IAM role ARN for the application"
} 