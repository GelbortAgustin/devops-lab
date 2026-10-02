output "api_urls" {
  description = "URLs de cada réplica de la API"
  value       = [for c in docker_container.api : "http://localhost:${c.ports[0].external}"]
}

output "network" {
  value = docker_network.lab.name
}
