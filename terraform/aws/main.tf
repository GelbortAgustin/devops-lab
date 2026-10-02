# Terraform en AWS (CUESTA PLATA si te olvidás recursos prendidos).
# Crea: un Security Group + una instancia EC2 Ubuntu "pelada".
# Docker y la app se instalan después con Ansible (carpeta ansible/).
#
# Antes de empezar:
#   - Cuenta de AWS con alertas de presupuesto (Billing -> Budgets) configuradas.
#   - aws configure  (credenciales de un usuario IAM, NO de root)
#   - Un key pair creado en la región (EC2 -> Key Pairs) -> variable key_name
#
#   terraform init && terraform plan && terraform apply
#   ...practicar...
#   terraform destroy      <- ¡SIEMPRE al terminar!

terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Desafío del roadmap: mover el state a un backend remoto.
  # backend "s3" {
  #   bucket         = "TU-BUCKET-DE-STATE"
  #   key            = "devops-lab/terraform.tfstate"
  #   region         = "us-east-1"
  #   use_lockfile   = true
  # }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Project   = "devops-lab"
      ManagedBy = "terraform"
    }
  }
}

data "aws_vpc" "default" {
  default = true
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
}

resource "aws_security_group" "app" {
  name        = "devops-lab-app"
  description = "SSH desde tu IP y HTTP publico"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH solo desde tu IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip_cidr]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.app.id]

  root_block_device {
    volume_size = 20
    encrypted   = true
  }

  metadata_options {
    http_tokens = "required" # IMDSv2
  }

  tags = {
    Name = "devops-lab-app"
  }
}
