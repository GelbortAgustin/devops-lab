variable "region" {
  type    = string
  default = "us-east-1"
}

variable "instance_type" {
  description = "Elegí un tipo elegible para free tier en tu cuenta"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Nombre del key pair de EC2 ya creado en la región"
  type        = string
}

variable "my_ip_cidr" {
  description = "Tu IP pública con /32 (ej: 181.10.20.30/32). Averiguala con: curl ifconfig.me"
  type        = string
}
