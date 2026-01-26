# RDS Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${local.name_prefix}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "${local.name_prefix}-db-subnet-group"
  }
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "main" {
  identifier = "${local.name_prefix}-pg"

  engine         = "postgres"
  engine_version = "16"
  instance_class = var.db_instance_class
  allocated_storage = 20

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  publicly_accessible     = false
  multi_az                = false
  storage_encrypted       = true
  deletion_protection     = false
  skip_final_snapshot     = true
  backup_retention_period = 0

  tags = {
    Name = "${local.name_prefix}-postgres"
  }
}
