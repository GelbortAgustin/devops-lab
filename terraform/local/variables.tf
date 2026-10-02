variable "docker_host" {
  description = "Socket de Docker. En WSL/Linux/Mac: unix:///var/run/docker.sock. En PowerShell con Docker Desktop: npipe:////./pipe/docker_engine"
  type        = string
  default     = "unix:///var/run/docker.sock"
}

variable "prefix" {
  description = "Prefijo para nombrar los recursos"
  type        = string
  default     = "tf-lab"
}

variable "api_image" {
  description = "Imagen de la API (construila antes con docker compose build)"
  type        = string
  default     = "tasks-api:local"
}

variable "api_replicas" {
  description = "Cantidad de contenedores de la API"
  type        = number
  default     = 2

  validation {
    condition     = var.api_replicas >= 1 && var.api_replicas <= 5
    error_message = "api_replicas tiene que estar entre 1 y 5."
  }
}

variable "api_base_port" {
  description = "Primer puerto expuesto en el host (8090, 8091, ...)"
  type        = number
  default     = 8090
}

variable "db_user" {
  type    = string
  default = "tasks"
}

variable "db_password" {
  type      = string
  default   = "tf-dev-password"
  sensitive = true
}

variable "db_name" {
  type    = string
  default = "tasks"
}
