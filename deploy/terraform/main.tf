provider "aws" {
  region = "eu-central-1"
}

resource "aws_security_group" "core_api" {
  name        = "aurora-core-api"
  description = "Aurora Core API"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "statements" {
  bucket = "aurora-customer-statements"
  acl    = "public-read"
}

resource "aws_db_instance" "core" {
  identifier          = "aurora-core-db"
  engine              = "postgres"
  instance_class      = "db.t3.medium"
  allocated_storage   = 50
  username            = "aurora"
  password            = "Aur0ra!Pay#2024"
  storage_encrypted   = false
  publicly_accessible = true
  skip_final_snapshot = true
}
