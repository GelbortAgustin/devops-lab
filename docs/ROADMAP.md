# Roadmap DevOps Lab

12 módulos, de cero a "puedo trabajar de esto". Cada uno tiene:

- **Ejercicios**: guiados, usando lo que ya trae el repo.
- **Desafíos**: cosas que el repo NO trae resueltas. Acá es donde realmente aprendés. Hacelos en una rama y abrí un Pull Request.
- **Lo lograste si...**: checklist para saber si podés pasar al siguiente.
- **Preguntas de entrevista**: si podés responderlas en voz alta sin leer, estás bien.

Ritmo sugerido: **8–10 horas por semana → ~14 semanas**. No saltees módulos: cada uno usa lo anterior.

| # | Módulo | Semanas |
|---|---|---|
| 0 | Preparar el entorno | 0,5 |
| 1 | Linux y Bash | 1,5 |
| 2 | Git y GitHub | 0,5 |
| 3 | Docker | 1,5 |
| 4 | Docker Compose, redes y proxies | 1 |
| 5 | CI/CD con GitHub Actions | 1,5 |
| 6 | Kubernetes | 2,5 |
| 7 | Helm | 0,5 |
| 8 | Terraform | 1,5 |
| 9 | Ansible | 1 |
| 10 | Observabilidad | 1 |
| 11 | Seguridad (DevSecOps) | 0,5 |
| 12 | Cloud real + proyecto final | 1+ |

---

## Módulo 0 — Preparar el entorno (Windows)

El mundo DevOps vive en Linux. En Windows vas a trabajar **dentro de WSL2 (Ubuntu)**.

1. PowerShell como administrador: `wsl --install -d Ubuntu-24.04` → reiniciá y creá tu usuario.
2. Instalá **Docker Desktop** → Settings → Resources → WSL Integration → activá Ubuntu.
3. Instalá **VS Code** + extensión **WSL**. Desde Ubuntu: `code .` abre VS Code conectado a Linux.
4. Dentro de Ubuntu:

```bash
sudo apt update && sudo apt install -y make git curl unzip python3-venv python3-pip pipx jq
pipx install ansible-core && pipx ensurepath

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/ && rm kubectl
# kind
curl -Lo kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64 && sudo install kind /usr/local/bin/ && rm kind
# helm
curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
# terraform: seguí https://developer.hashicorp.com/terraform/install (pestaña Linux / Ubuntu)
```

5. **Copiá el proyecto al filesystem de Linux** (trabajar sobre `/mnt/d/...` es lento y trae problemas de permisos y finales de línea):

```bash
cp -r /mnt/d/Devops ~/devops-lab && cd ~/devops-lab
git init && git add . && git commit -m "chore: proyecto inicial"
```

6. Creá un repo **público** en GitHub llamado `devops-lab` y subilo (`git remote add origin ...`, `git push -u origin main`). Configurá una clave SSH para GitHub.

**Lo lograste si...**
- [ ] `docker run hello-world` funciona desde Ubuntu.
- [ ] `kubectl version --client`, `kind version`, `helm version`, `terraform version`, `ansible --version` responden.
- [ ] El repo está en tu GitHub.

---

## Módulo 1 — Linux y Bash

Es la base de todo. En entrevistas preguntan mucho de esto.

**Ejercicios**
1. Leé `scripts/smoke-test.sh` línea por línea. Explicá qué hace `set -euo pipefail`.
2. Levantá el stack (`make up`) y practicá diagnóstico:
   - `docker compose exec api sh` → `ps aux`, `env`, `cat /etc/os-release`, `whoami` (¿por qué no sos root?).
   - Desde Ubuntu: `ss -tlnp`, `curl -v http://localhost:8080/`, `dig`/`nslookup`.
   - `docker compose logs api | jq .` → filtrá solo los requests con `status` 404 usando `jq`.
3. Practicá: permisos (`chmod`, `chown`), procesos (`top`, `kill`, señales), `systemctl`, `journalctl`, `grep`, `awk`, `sed`, pipes, redirecciones.

**Desafíos**
- [ ] Escribí `scripts/backup-db.sh` que haga `pg_dump` del Postgres del compose a `backups/tasks-YYYYMMDD-HHMM.sql.gz` y borre backups de más de 7 días.
- [ ] Escribí `scripts/restore-db.sh` que restaure un backup. Probalo: borrá tareas, restaurá, verificá.
- [ ] Hacé que el backup corra cada hora con `cron` en WSL.

**Lo lograste si...**
- [ ] Podés explicar la diferencia entre proceso y servicio, y qué es un file descriptor.
- [ ] Sabés ver qué proceso escucha en un puerto y por qué un puerto puede estar "ocupado".

**Preguntas de entrevista**: ¿Qué pasa cuando escribís una URL en el navegador (DNS, TCP, TLS, HTTP)? ¿Diferencia entre `kill -15` y `kill -9`? ¿Cómo ves el uso de disco y qué carpeta lo ocupa (`df`, `du`)? ¿Qué es un inode? ¿Qué es la *load average*?

---

## Módulo 2 — Git y GitHub

**Ejercicios**
1. En GitHub → Settings → Branches: protegé `main` (requiere PR + que pase el CI).
2. Desde ahora, **todo cambio va en una rama + Pull Request**, aunque trabajes solo.
3. Usá *conventional commits*: `feat:`, `fix:`, `chore:`, `docs:`, `ci:`.

**Desafíos**
- [ ] Provocá un conflicto de merge a propósito (dos ramas tocando la misma línea) y resolvelo.
- [ ] Practicá `git rebase -i` para limpiar commits antes de un PR, y `git revert` de un commit ya mergeado.
- [ ] Agregá un `CODEOWNERS` y una plantilla de PR (`.github/pull_request_template.md`).

**Preguntas de entrevista**: ¿merge vs rebase? ¿Qué es trunk-based development vs GitFlow? ¿Cómo deshacés un commit que ya está en `main`?

---

## Módulo 3 — Docker

**Ejercicios**
1. Leé `app/Dockerfile`. Explicá cada línea, en especial: multi-stage, `USER appuser`, `HEALTHCHECK`, `ARG` vs `ENV`.
2. `docker build -t tasks-api:local app` y después `docker images tasks-api` → anotá el tamaño.
3. `docker history tasks-api:local` → ¿qué capa pesa más?
4. Corré la app sola con SQLite: `docker run --rm -p 8000:8000 tasks-api:local` y entrá a http://localhost:8000/docs.
5. Cambiá una línea de `main.py`, rebuildeá y mirá qué capas usan cache y cuáles no. ¿Por qué se copia `requirements.txt` antes que el código?

**Desafíos**
- [ ] Hacé una versión del Dockerfile con base `python:3.12-alpine` o *distroless* y compará tamaño y vulnerabilidades (`docker scout cves` o Trivy).
- [ ] Hacé que la imagen tenga labels OCI (`org.opencontainers.image.source`, `version`, `revision`).
- [ ] Corré el contenedor con `--read-only --cap-drop ALL` y verificá que sigue funcionando.

**Lo lograste si...**
- [ ] Entendés la diferencia entre imagen y contenedor, capa, registry, tag y digest.
- [ ] Sabés por qué no se corre como root y por qué no se meten secretos en la imagen.

**Preguntas de entrevista**: ¿`CMD` vs `ENTRYPOINT`? ¿`COPY` vs `ADD`? ¿Cómo achicás una imagen? ¿Qué es un namespace y un cgroup? ¿Contenedor vs máquina virtual?

---

## Módulo 4 — Docker Compose, redes y proxies

**Ejercicios**
1. `make up` y `docker compose ps`. Leé `docker-compose.yml`: `depends_on` con `condition: service_healthy`, volúmenes, redes `backend`/`frontend`.
2. **Escalado**: `docker compose up -d --scale api=3` → llamá `curl localhost:8080/` varias veces y mirá cómo cambia el `hostname`.
3. **Persistencia**: creá tareas, `docker compose down` (sin `-v`), `make up` → ¿siguen? Ahora con `down -v` → ¿y ahora?
4. **Resiliencia**: `docker compose stop redis` → la app sigue andando (mirá `/ready` y el header `X-Cache`). `docker compose stop db` → ¿qué devuelve `/ready`?
5. `docker network inspect devops-lab_backend` → ¿qué IPs tienen? ¿Cómo resuelve `db` como nombre?

**Desafíos**
- [ ] Agregá HTTPS a Nginx con un certificado autofirmado (`openssl`) y redirección 80 → 443.
- [ ] Agregá *rate limiting* en Nginx (`limit_req`) y probalo con `scripts/load-test.sh`.
- [ ] Agregá un servicio `pgadmin` o `adminer` solo para un perfil `tools`.

**Preguntas de entrevista**: ¿reverse proxy vs load balancer? ¿Qué es un healthcheck y para qué sirve? ¿Cómo se comunican contenedores entre sí?

---

## Módulo 5 — CI/CD con GitHub Actions

**Ejercicios**
1. Leé `.github/workflows/ci.yml`. Dibujá en papel el grafo de jobs (`needs`).
2. Hacé un PR con un cambio chico y mirá correr el pipeline en la pestaña *Actions*.
3. **Rompé cosas a propósito** (en ramas distintas) y mirá qué job falla:
   - un test que falle,
   - código mal formateado,
   - un endpoint que devuelva 500 en `/health` (¿falla el smoke test?).
4. Mergeá a `main` → mirá la imagen publicada en tu perfil de GitHub → *Packages*.
5. Creá un tag `git tag v0.1.0 && git push --tags` → ¿qué tags tiene ahora la imagen?

**Desafíos**
- [ ] Agregá **migraciones con Alembic** en lugar de `create_all()`, y un paso de CI que verifique que las migraciones aplican sobre un Postgres de servicio (`services:` en el job).
- [ ] Agregá **Dependabot** (`.github/dependabot.yml`) para pip, Docker y GitHub Actions.
- [ ] Agregá un job de **deploy** que, al crear un tag, haga `helm upgrade` contra un cluster (usá `environment: production` con aprobación manual).
- [ ] Hacé un workflow reutilizable (`workflow_call`) o una *composite action*.

**Preguntas de entrevista**: ¿Continuous Delivery vs Continuous Deployment? ¿Cómo manejás secretos en un pipeline? ¿Qué estrategia de versionado usás para imágenes y por qué no conviene usar solo `latest`? ¿Cómo harías un rollback?

---

## Módulo 6 — Kubernetes

El módulo más largo y el más pedido en ofertas laborales.

**Ejercicios**
1. `make kind-up` (cluster de 3 nodos + ingress + metrics-server) y `make k8s-dev`.
2. `make k8s-status` → identificá Deployment, ReplicaSet, Pods, Services, StatefulSet, PVC, Ingress, HPA.
3. Entrá a http://tasks.localhost:8081/ (si no resuelve, agregá `127.0.0.1 tasks.localhost` al archivo hosts).
4. Diferencias entre overlays: `kubectl kustomize k8s/overlays/dev` vs `.../prod`.
5. **Self-healing**: `kubectl -n tasks delete pod -l app=tasks-api` → ¿qué pasa?
6. **Rolling update sin downtime**: mientras corrés `while true; do curl -s tasks.localhost:8081/ ; echo; sleep 0.3; done`, en otra terminal hacé `kubectl -n tasks set env deploy/tasks-api APP_VERSION=v2` (dispara un rollout). ¿Hubo errores? Después: `kubectl -n tasks rollout undo deploy/tasks-api`.
7. **Probes**: borrá el pod de Postgres → los pods de la API quedan *NotReady* (no reciben tráfico) pero no se reinician. ¿Por qué? (pista: readiness vs liveness).
8. **Autoescalado**: `kubectl -n tasks get hpa -w` y generá carga. ¿Escala?
9. Debug: `kubectl describe`, `kubectl logs -f`, `kubectl get events --sort-by=.lastTimestamp`, `kubectl exec`, `kubectl port-forward`.

**Desafíos**
- [ ] Rompé el deployment a propósito de 3 formas y diagnosticá cada una: imagen inexistente (`ImagePullBackOff`), límite de memoria muy bajo (`OOMKilled`), `DATABASE_URL` mal (`CrashLoopBackOff`).
- [ ] Agregá un **PodDisruptionBudget** y una **NetworkPolicy** que solo deje a la API hablar con Postgres y Redis.
- [ ] Agregá un **CronJob** que haga el backup de Postgres del módulo 1.
- [ ] El proyecto ingress-nginx fue retirado por la comunidad de Kubernetes (sigue funcionando para practicar). Migrá el Ingress a la **Gateway API** con una implementación como Envoy Gateway o Traefik.
- [ ] Instalá **Argo CD** en el cluster y hacé que despliegue `k8s/overlays/dev` desde tu repo (GitOps).

**Lo lograste si...**
- [ ] Podés explicar el camino de un request: Ingress → Service → Endpoints → Pod.
- [ ] Sabés diagnosticar un pod que no arranca sin googlear los comandos.

**Preguntas de entrevista**: ¿Deployment vs StatefulSet vs DaemonSet? ¿Tipos de Service? ¿Requests vs limits? ¿Qué hace el scheduler? ¿ConfigMap vs Secret (y por qué un Secret no está "cifrado")? ¿Qué componentes tiene el control plane?

---

## Módulo 7 — Helm

**Ejercicios**
1. Leé `helm/tasks-api/`. Compará `templates/deployment.yaml` con `k8s/base/api-deployment.yaml`.
2. `helm template demo helm/tasks-api` → mirá el YAML renderizado.
3. `make helm-install` → `helm list -n tasks`, `helm history demo -n tasks`.
4. `helm upgrade demo helm/tasks-api -n tasks --set replicaCount=3` y después `helm rollback demo 1 -n tasks`.

**Desafíos**
- [ ] Creá `values-prod.yaml` con autoscaling e ingress activados.
- [ ] Hacé que el chart incluya Postgres y Redis como **dependencias** (charts de Bitnami u otros) opcionales.
- [ ] Publicá el chart como artefacto OCI en GHCR desde el CI.

**Preguntas de entrevista**: ¿Helm vs Kustomize, cuándo usarías cada uno? ¿Qué es un release?

---

## Módulo 8 — Terraform (Infraestructura como Código)

**Ejercicios (gratis, con Docker)**
1. `cd terraform/local && terraform init && terraform plan` → leé el plan entero.
2. `terraform apply` → `curl localhost:8090/` y `curl localhost:8091/`.
3. Cambiá `api_replicas` a 3 (`terraform apply -var api_replicas=3`) → mirá el plan: ¿qué crea, qué modifica?
4. Borrá un contenedor a mano (`docker rm -f tf-lab-api-0`) y corré `terraform plan` → eso es **drift**.
5. Abrí `terraform.tfstate`: ¿por qué la contraseña de la base está ahí en texto plano? ¿Qué implica?
6. `terraform destroy`.

**Ejercicios (AWS — cuesta plata)**
1. Creá cuenta de AWS, activá MFA en root, creá un usuario IAM y **configurá un Budget con alerta de 5 USD**.
2. `cd terraform/aws`, copiá `terraform.tfvars.example` a `terraform.tfvars`, completalo y `apply`.
3. Conectate por SSH con el output `ssh_command`. **Al terminar: `terraform destroy`.**

**Desafíos**
- [ ] Mové el state a un **backend remoto S3** con lock (está comentado en `main.tf`).
- [ ] Convertí la creación de la EC2 en un **módulo** reutilizable y usalo para crear `dev` y `prod`.
- [ ] En lugar de la VPC default, creá tu propia VPC con subredes públicas y privadas.
- [ ] Agregá `tflint` y `checkov` (o `trivy config`) al CI.

**Preguntas de entrevista**: ¿Qué es el state y por qué es delicado? ¿Qué es el drift? ¿`count` vs `for_each`? ¿Cómo trabajan varias personas sobre la misma infraestructura? ¿Terraform vs Ansible?

---

## Módulo 9 — Ansible (gestión de configuración)

Necesitás un servidor Ubuntu: la EC2 del módulo 8 o una VM local con [Multipass](https://multipass.run/) (`multipass launch -n lab 24.04`).

**Ejercicios**
1. `cd ansible && ansible-galaxy collection install -r requirements.yml`.
2. Copiá `inventory.ini.example` a `inventory.ini` con tu servidor. `ansible all -m ping`.
3. Editá `group_vars/all.yml` con tu imagen de GHCR (hacé el package **público** en GitHub o configurá login).
4. `ansible-playbook site.yml --check --diff` y después `ansible-playbook site.yml`.
5. Corrélo **otra vez**: debería decir `changed=0` (idempotencia). Si algo cambia siempre, investigá por qué.
6. Abrí `http://IP_DEL_SERVIDOR/`.

**Desafíos**
- [ ] Cifrá `db_password` con **ansible-vault**.
- [ ] Investigá por qué Docker se "saltea" las reglas de UFW cuando publica puertos y cómo se mitiga.
- [ ] Agregá un rol que instale **node_exporter** para que Prometheus mida CPU/RAM/disco del servidor.
- [ ] Hacé que el CI corra `ansible-lint`.

**Preguntas de entrevista**: ¿Qué es idempotencia? ¿Ansible es *push* o *pull*? ¿Qué es un handler?

---

## Módulo 10 — Observabilidad

**Ejercicios**
1. `make monitoring` → Grafana en http://localhost:3000 → carpeta *DevOps Lab* → dashboard *Tasks API*.
2. Prometheus http://localhost:9090 → *Status → Targets* (¿ves las réplicas?) y *Alerts*.
3. Escribí queries PromQL a mano: requests por segundo, % de errores, p95 de latencia.
4. **Simulacro de incidente**: `make load MODE=errores` durante 5 minutos → la alerta `TasksApiHighErrorRate` debería pasar a *Firing*. Repetí con `MODE=lento`.
5. Escribí un **postmortem** (en `docs/postmortems/`): qué pasó, impacto, cómo se detectó, causa raíz, acciones.

**Desafíos**
- [ ] Agregá **Alertmanager** y mandá las alertas a un canal de Slack/Discord/Telegram.
- [ ] Agregá **Loki + Promtail** (o Grafana Alloy) para ver los logs JSON en Grafana.
- [ ] Definí un **SLO** (ej: 99,5% de requests sin 5xx en 30 días) y un panel de *error budget*.
- [ ] Instalá **kube-prometheus-stack** con Helm en el cluster kind y hacé que scrapee la API.

**Preguntas de entrevista**: ¿Métricas vs logs vs traces? ¿SLI, SLO, SLA? ¿Qué son las *golden signals*? ¿Por qué se usa p95/p99 y no el promedio?

---

## Módulo 11 — Seguridad (DevSecOps)

**Ejercicios**
1. Mirá el job `build-and-scan` del CI: Trivy escanea la imagen.
2. Corrélo local: `docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image tasks-api:local`.
3. Repasá lo que ya trae el proyecto: usuario no-root, `readOnlyRootFilesystem`, `capabilities drop ALL`, `.env` fuera de git, `/metrics` bloqueado en Nginx, SSH solo desde tu IP en AWS, IMDSv2.

**Desafíos**
- [ ] Agregá **gitleaks** (detección de secretos) como *pre-commit hook* y en el CI.
- [ ] Firmá la imagen con **cosign** en el CI y generá un SBOM (`syft` o Trivy).
- [ ] Reemplazá el Secret de Kubernetes por **Sealed Secrets** o **External Secrets**.
- [ ] Usá **OIDC** de GitHub Actions para autenticarte en AWS sin access keys.

**Preguntas de entrevista**: ¿Qué es el principio de mínimo privilegio? ¿Cómo gestionás secretos? ¿Qué es *shift-left*?

---

## Módulo 12 — Cloud real + proyecto final

Elegí **una** nube y profundizá (AWS es la más pedida en LATAM, después Azure y GCP).

**Proyecto final** (lo que mostrás en entrevistas):
- [ ] Infraestructura 100% en Terraform con state remoto: VPC, cluster gestionado (EKS/AKS/GKE) **o** EC2 + ALB, base gestionada (RDS).
- [ ] CI/CD que, al mergear a `main`, testea, escanea, publica y despliega solo (GitOps con Argo CD es un plus).
- [ ] Monitoreo con alertas que llegan a un canal.
- [ ] Un diagrama de arquitectura en el README (draw.io o Excalidraw).
- [ ] Un postmortem de un incidente simulado.
- [ ] **Todo destruible con un comando** (para no pagar de más).

---

## Cómo convertir esto en trabajo

**Tu repo es tu CV técnico.** Pinealo en tu perfil de GitHub y cuidá el README: diagrama, cómo levantarlo, decisiones tomadas y por qué.

**Cómo contarlo en el CV** (con lo que realmente hiciste):
- "Diseñé un pipeline de CI/CD en GitHub Actions con tests, escaneo de vulnerabilidades e integración con Docker Compose, publicando imágenes versionadas en GHCR."
- "Desplegué una aplicación en Kubernetes con Kustomize y Helm, con probes, autoescalado y rolling updates sin downtime."
- "Aprovisioné infraestructura en AWS con Terraform (state remoto) y la configuré con Ansible."
- "Implementé monitoreo con Prometheus y Grafana, alertas sobre tasa de errores y latencia p95."

**Certificaciones** (en orden sugerido, no son obligatorias pero ayudan a pasar filtros):
1. AWS Certified Cloud Practitioner → AWS Solutions Architect Associate
2. HashiCorp Terraform Associate
3. CKA (Certified Kubernetes Administrator) — la más valorada, y es práctica, no de opción múltiple.

**Roles a buscar**: DevOps Jr / Trainee, SRE Jr, Platform Engineer Jr, Cloud Engineer Jr, y también Soporte/Infra/Sysadmin con foco en Linux y cloud (es una puerta de entrada muy común).

**Tip**: en la entrevista técnica casi siempre te piden diagnosticar algo ("el pod no levanta", "la web está lenta"). Los ejercicios de "rompé cosas a propósito" de este roadmap son justamente eso: practicalos hasta que te salgan de memoria.
