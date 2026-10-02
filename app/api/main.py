"""Tasks API: una app chica pero "de verdad" para practicar DevOps.

Endpoints:
  GET  /               info de la app (versión, hostname -> útil para ver el balanceo)
  GET  /health         liveness: el proceso está vivo
  GET  /ready          readiness: puede atender (DB y Redis OK)
  GET  /metrics        métricas en formato Prometheus
  CRUD /tasks          la "lógica de negocio"
  GET  /chaos/error    devuelve 500 (solo si CHAOS_ENABLED=true)
  GET  /chaos/slow     responde lento (solo si CHAOS_ENABLED=true)
"""

import json
import logging
import os
import socket
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from . import cache, models, schemas
from .database import Base, engine, get_db

APP_VERSION = os.getenv("APP_VERSION", "dev")
CHAOS_ENABLED = os.getenv("CHAOS_ENABLED", "false").lower() == "true"
CACHE_KEY = "tasks:all"


# ---------- Logging estructurado (JSON) ----------
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for extra in ("method", "path", "status", "duration_ms"):
            if hasattr(record, extra):
                payload[extra] = getattr(record, extra)
        return json.dumps(payload, ensure_ascii=False)


handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), handlers=[handler], force=True)
log = logging.getLogger("tasks-api")


# ---------- Métricas Prometheus ----------
REQUESTS = Counter("http_requests_total", "Total de requests HTTP", ["method", "path", "status"])
LATENCY = Histogram(
    "http_request_duration_seconds",
    "Duración de requests HTTP",
    ["method", "path"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Para practicar está bien crear tablas así. En un proyecto real se usan
    # migraciones (Alembic) -> es uno de los desafíos del roadmap.
    Base.metadata.create_all(bind=engine)
    log.info("app iniciada", extra={"path": "startup"})
    yield


app = FastAPI(title="Tasks API", version=APP_VERSION, lifespan=lifespan)


@app.middleware("http")
async def metrics_and_logs(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
        status = response.status_code
    except Exception:
        status = 500
        log.exception("error no manejado")
        response = JSONResponse({"detail": "internal error"}, status_code=500)
    duration = time.perf_counter() - start

    route = request.scope.get("route")
    path = getattr(route, "path", "unmatched")
    if path != "/metrics":
        REQUESTS.labels(request.method, path, str(status)).inc()
        LATENCY.labels(request.method, path).observe(duration)
        log.info(
            "request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": status,
                "duration_ms": round(duration * 1000, 2),
            },
        )
    return response


# ---------- Endpoints operativos ----------
@app.get("/")
def root():
    return {"app": "tasks-api", "version": APP_VERSION, "hostname": socket.gethostname()}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready(response: Response, db: Session = Depends(get_db)):
    checks = {}
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["database"] = f"error: {exc.__class__.__name__}"

    redis_ok = cache.ping()
    if redis_ok is not None:
        checks["redis"] = "ok" if redis_ok else "error"

    # Redis es opcional (degradación elegante): solo la DB define si estamos listos.
    if checks["database"] != "ok":
        response.status_code = 503
        return {"status": "not ready", "checks": checks}
    return {"status": "ready", "checks": checks}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ---------- CRUD de tareas ----------
@app.get("/tasks", response_model=list[schemas.TaskOut])
def list_tasks(response: Response, db: Session = Depends(get_db)):
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        response.headers["X-Cache"] = "HIT"
        return json.loads(cached)

    tasks = db.scalars(select(models.Task).order_by(models.Task.id)).all()
    data = [schemas.TaskOut.model_validate(t).model_dump(mode="json") for t in tasks]
    cache.set(CACHE_KEY, json.dumps(data))
    response.headers["X-Cache"] = "MISS"
    return data


@app.post("/tasks", response_model=schemas.TaskOut, status_code=201)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    task = models.Task(title=payload.title)
    db.add(task)
    db.commit()
    db.refresh(task)
    cache.delete(CACHE_KEY)
    return task


@app.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@app.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, payload: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    cache.delete(CACHE_KEY)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    db.delete(task)
    db.commit()
    cache.delete(CACHE_KEY)
    return Response(status_code=204)


# ---------- Caos controlado (para practicar alertas e incidentes) ----------
@app.get("/chaos/error")
def chaos_error():
    if not CHAOS_ENABLED:
        raise HTTPException(status_code=404, detail="chaos disabled")
    raise HTTPException(status_code=500, detail="error provocado a propósito")


@app.get("/chaos/slow")
def chaos_slow(seconds: float = 2.0):
    if not CHAOS_ENABLED:
        raise HTTPException(status_code=404, detail="chaos disabled")
    time.sleep(min(seconds, 10))
    return {"slept": min(seconds, 10)}
