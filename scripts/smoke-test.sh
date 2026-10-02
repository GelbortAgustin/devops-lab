#!/usr/bin/env bash
# Smoke test: verifica que la app desplegada responde bien.
# Uso: ./scripts/smoke-test.sh [URL_BASE]     (default: http://localhost:8080)
set -euo pipefail

BASE_URL="${1:-http://localhost:8080}"
FAILED=0

check() {
  local name="$1" expected="$2" method="$3" path="$4" data="${5:-}"
  local code
  if [[ -n "$data" ]]; then
    code=$(curl -s -o /dev/null -w '%{http_code}' -X "$method" \
      -H 'Content-Type: application/json' -d "$data" "$BASE_URL$path")
  else
    code=$(curl -s -o /dev/null -w '%{http_code}' -X "$method" "$BASE_URL$path")
  fi
  if [[ "$code" == "$expected" ]]; then
    echo "  OK   $name ($code)"
  else
    echo "  FAIL $name (esperaba $expected, obtuve $code)"
    FAILED=1
  fi
}

echo "Smoke test contra $BASE_URL"

# Esperar a que la app esté lista (máx ~60s)
for i in $(seq 1 30); do
  if curl -sf "$BASE_URL/health" > /dev/null; then break; fi
  echo "  esperando a la app... ($i)"
  sleep 2
done

check "health"       200 GET  /health
check "ready"        200 GET  /ready
check "listar tasks" 200 GET  /tasks
check "crear task"   201 POST /tasks '{"title":"smoke test"}'
check "404"          404 GET  /tasks/999999

if [[ "$FAILED" -ne 0 ]]; then
  echo "Smoke test FALLÓ"
  exit 1
fi
echo "Smoke test OK"
