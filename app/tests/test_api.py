def test_root_devuelve_version(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["app"] == "tasks-api"
    assert "hostname" in r.json()


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_ready_con_db_ok(client):
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json()["checks"]["database"] == "ok"


def test_crud_completo(client):
    r = client.post("/tasks", json={"title": "Aprender Docker"})
    assert r.status_code == 201
    task = r.json()
    assert task["done"] is False

    r = client.patch(f"/tasks/{task['id']}", json={"done": True})
    assert r.status_code == 200
    assert r.json()["done"] is True

    ids = [t["id"] for t in client.get("/tasks").json()]
    assert task["id"] in ids

    assert client.delete(f"/tasks/{task['id']}").status_code == 204
    assert client.get(f"/tasks/{task['id']}").status_code == 404


def test_validacion_titulo_vacio(client):
    assert client.post("/tasks", json={"title": ""}).status_code == 422


def test_metrics_expone_contadores(client):
    client.get("/health")
    body = client.get("/metrics").text
    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body


def test_chaos_error(client):
    assert client.get("/chaos/error").status_code == 500
