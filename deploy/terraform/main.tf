provider "aws" {
  region = "eu-central-1"
}

variable "allowed_ingress_cidrs" {
  description = "Internal CIDR ranges (e.g. load balancer / VPC subnets) allowed to reach the Core API."
  type        = list(string)

  validation {
    condition     = length(var.allowed_ingress_cidrs) > 0 && alltrue([for c in var.allowed_ingress_cidrs : tonumber(split("/", c)[1]) >= 8])
    error_message = "allowed_ingress_cidrs must be non-empty internal ranges (prefix /8 or narrower); internet-wide rules are not allowed."
  }
}

resource "aws_security_group" "core_api" {
  name        = "aurora-core-api"
  description = "Aurora Core API"

  ingress {
    description = "Core API (uvicorn) from internal networks only"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = var.allowed_ingress_cidrs
  }
}

resource "aws_s3_bucket" "statements" {
  bucket = "aurora-customer-statements"
}

resource "aws_s3_bucket_public_access_block" "statements" {
  bucket = aws_s3_bucket.statements.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "statements" {
  bucket = aws_s3_bucket.statements.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "statements" {
  bucket = aws_s3_bucket.statements.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_db_instance" "core" {
  identifier        = "aurora-core-db"
  engine            = "postgres"
  instance_class    = "db.t3.medium"
  allocated_storage = 50
  username          = "aurora"

  # Master password is generated and rotated by RDS in AWS Secrets Manager;
  # no plaintext credential lives in code or state inputs.
  manage_master_user_password = true

  storage_encrypted   = true
  publicly_accessible = false
  skip_final_snapshot = true
}
