#!/usr/bin/env bash
# Genera tráfico para ver algo en Grafana y disparar alertas.
# Uso: ./scripts/load-test.sh [URL_BASE] [SEGUNDOS] [modo]
#   modo: normal | errores | lento
set -euo pipefail

BASE_URL="${1:-http://localhost:8080}"
DURATION="${2:-60}"
MODE="${3:-normal}"
END=$((SECONDS + DURATION))

echo "Generando tráfico '$MODE' contra $BASE_URL durante ${DURATION}s (Ctrl+C para cortar)"
while (( SECONDS < END )); do
  curl -s -o /dev/null "$BASE_URL/tasks" &
  curl -s -o /dev/null "$BASE_URL/" &
  case "$MODE" in
    errores) curl -s -o /dev/null "$BASE_URL/chaos/error" & ;;
    lento)   curl -s -o /dev/null "$BASE_URL/chaos/slow?seconds=2" & ;;
  esac
  sleep 0.2
done
wait
echo "Listo."
