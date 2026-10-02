# DevOps Lab 🛠️

Un proyecto para practicar **todo el ciclo DevOps** sobre una app real y chica, desde
`docker run` hasta Kubernetes, Terraform, CI/CD y monitoreo. La idea es que al terminarlo
tengas un repo en tu GitHub que puedas mostrar en entrevistas y que sepas explicar cada pieza.

> 👉 **Empezá por [`docs/ROADMAP.md`](docs/ROADMAP.md)**: son 12 módulos con ejercicios,
> desafíos (cosas que el repo NO trae resueltas, para que las hagas vos) y un checklist
> de "lo lograste si...".

## Qué hay adentro

```
devops-lab/
├── app/                    Tasks API (Python/FastAPI) + tests + Dockerfile multi-stage
├── docker-compose.yml      API + Postgres + Redis + Nginx (+ Prometheus/Grafana con perfil)
├── nginx/                  Reverse proxy
├── monitoring/             Prometheus (scrape + alertas) y Grafana (dashboard provisionado)
├── .github/workflows/      CI/CD: lint, tests, build, Trivy, integración, IaC, push a GHCR
├── k8s/                    Manifiestos Kubernetes con Kustomize (base + overlays dev/prod)
├── helm/tasks-api/         El mismo despliegue empaquetado como chart de Helm
├── terraform/local/        Terraform con provider Docker (gratis, para aprender)
├── terraform/aws/          Terraform en AWS: Security Group + EC2 (cuesta plata)
├── ansible/                Configura un Ubuntu desde cero y despliega la app
├── scripts/                smoke-test.sh y load-test.sh
└── Makefile                Atajos: make help
```

## La app

Una API de tareas (CRUD) pensada para tener las cosas que importan en operaciones:

| Endpoint | Para qué sirve en DevOps |
|---|---|
| `GET /` | Devuelve versión y **hostname** → ves el balanceo entre réplicas |
| `GET /health` | *Liveness probe*: el proceso vive |
| `GET /ready` | *Readiness probe*: chequea Postgres y Redis |
| `GET /metrics` | Métricas Prometheus (requests, latencia por ruta) |
| `/tasks` | CRUD con Postgres y cache en Redis (header `X-Cache: HIT/MISS`) |
| `GET /chaos/error`, `/chaos/slow` | Provoca errores/lentitud para practicar alertas e incidentes |

Logs en JSON a stdout, config 100% por variables de entorno (12-factor), corre como usuario
no-root, y si Redis se cae la app sigue andando (degradación elegante).

## Arranque rápido (5 minutos)

Requisitos: **Windows con WSL2 + Docker Desktop** (o Linux/Mac con Docker). Detalle en el módulo 0 del roadmap.

```bash
# desde WSL (Ubuntu), dentro de la carpeta del proyecto
cp .env.example .env
make up            # o: docker compose up -d --build --wait
make smoke         # o: bash scripts/smoke-test.sh

curl http://localhost:8080/
curl -X POST http://localhost:8080/tasks -H 'Content-Type: application/json' -d '{"title":"Aprender DevOps"}'
curl -i http://localhost:8080/tasks      # mirá el header X-Cache
```

Con monitoreo:

```bash
make monitoring                # Grafana: http://localhost:3000 (admin / la de tu .env)
make load MODE=errores         # genera tráfico con errores y mirá el dashboard
```

Sin Docker, solo la app (usa SQLite):

```bash
make venv && make test
cd app && .venv/bin/uvicorn api.main:app --reload   # http://localhost:8000/docs
```

## Puertos

| Servicio | URL |
|---|---|
| App vía Nginx (compose) | http://localhost:8080 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| App en Kubernetes (kind + ingress) | http://tasks.localhost:8081 |
| App vía Terraform local | http://localhost:8090, 8091 |

## Licencia

Usalo, rompelo, copialo. Es para aprender.
