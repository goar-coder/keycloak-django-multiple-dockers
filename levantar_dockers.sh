#!/usr/bin/env bash
# Automatiza "levantar_dockers.md": primer arranque en una máquina nueva
# (clon del repo). Crea la red compartida, levanta postgres -> keycloak -> pl
# en orden esperando cada healthcheck, e importa los usuarios de prueba.
#
# Uso: ./levantar_dockers.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() { echo -e "\n== $* =="; }

wait_healthy() {
    local container="$1"
    local timeout="${2:-60}"
    local waited=0

    echo "  esperando a que '$container' esté healthy (timeout ${timeout}s)..."
    while true; do
        local status
        status="$(docker inspect -f '{{.State.Health.Status}}' "$container" 2>/dev/null || echo "starting")"
        [ "$status" = "healthy" ] && break

        if [ "$waited" -ge "$timeout" ]; then
            echo "  [ERROR] '$container' no llegó a 'healthy' tras ${timeout}s (estado: $status)" >&2
            docker logs --tail=50 "$container" || true
            exit 1
        fi
        sleep 2
        waited=$((waited + 2))
    done
    echo "  '$container' healthy (${waited}s)"
}

log "1. Red compartida"
if docker network inspect sso-network >/dev/null 2>&1; then
    echo "  'sso-network' ya existe"
else
    docker network create sso-network
    echo "  'sso-network' creada"
fi

log "2. Levantando postgres"
(cd "$ROOT/postgres" && docker compose up -d)
wait_healthy sso-postgres-postgres-1 30

log "3. Levantando keycloak (importa keycloak/realm-export.json)"
(cd "$ROOT/keycloak" && docker compose up -d)
wait_healthy sso-keycloak-keycloak-1 90

log "4. Levantando pl (Django)"
(cd "$ROOT/django" && docker compose up -d)
wait_healthy sso-pl-pl-1 60

log "5. Creando usuarios de prueba (el realm se importa sin usuarios)"
docker exec sso-pl-pl-1 python3 scripts/create_users.py

log "Listo"
