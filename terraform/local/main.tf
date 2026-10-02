# Terraform SIN costo: crea la infraestructura como contenedores Docker locales.
# Sirve para aprender el ciclo init -> plan -> apply -> destroy, state, variables y outputs.
#
#   cd terraform/local
#   terraform init
#   terraform plan
#   terraform apply
#   curl http://localhost:8090/
#   terraform destroy
#
# Requiere haber construido antes la imagen:  docker compose build   (o make build)

terraform {
  required_version = ">= 1.6"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {
  host = var.docker_host
}

resource "docker_network" "lab" {
  name = "${var.prefix}-net"
}

resource "docker_volume" "pgdata" {
  name = "${var.prefix}-pgdata"
}

resource "docker_image" "postgres" {
  name         = "postgres:16-alpine"
  keep_locally = true
}

resource "docker_image" "redis" {
  name         = "redis:7-alpine"
  keep_locally = true
}

resource "docker_container" "db" {
  name  = "${var.prefix}-db"
  image = docker_image.postgres.image_id
  env = [
    "POSTGRES_USER=${var.db_user}",
    "POSTGRES_PASSWORD=${var.db_password}",
    "POSTGRES_DB=${var.db_name}",
  ]
  networks_advanced {
    name    = docker_network.lab.name
    aliases = ["db"]
  }
  volumes {
    volume_name    = docker_volume.pgdata.name
    container_path = "/var/lib/postgresql/data"
  }
  healthcheck {
    test     = ["CMD-SHELL", "pg_isready -U ${var.db_user}"]
    interval = "5s"
    retries  = 10
  }
  wait         = true # espera a que el healthcheck esté OK antes de seguir
  wait_timeout = 90
}

resource "docker_container" "redis" {
  name  = "${var.prefix}-redis"
  image = docker_image.redis.image_id
  networks_advanced {
    name    = docker_network.lab.name
    aliases = ["redis"]
  }
}

resource "docker_container" "api" {
  count = var.api_replicas
  name  = "${var.prefix}-api-${count.index}"
  image = var.api_image
  env = [
    "DATABASE_URL=postgresql+psycopg://${var.db_user}:${var.db_password}@db:5432/${var.db_name}",
    "REDIS_URL=redis://redis:6379/0",
    "APP_VERSION=terraform",
  ]
  networks_advanced {
    name = docker_network.lab.name
  }
  ports {
    internal = 8000
    external = var.api_base_port + count.index
  }
  restart    = "unless-stopped"
  depends_on = [docker_container.db, docker_container.redis]
}
