#!/usr/bin/env bash
# Automatiza "parar y recargar los dockers.md": baja d2/keycloak, limpia el
# volumen de postgres, levanta todo de nuevo (Keycloak reimporta
# keycloak/realm-export.json) y recrea los usuarios de prueba.
#
# Uso: ./reload_dockers.sh
set -euo pipefail

ROOT="$HOME/projects/keycloak/new2/keycloak-django-multiple-dockers"

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

log "1. Bajando d2 y keycloak"
(cd "$ROOT/django" && docker compose down)
(cd "$ROOT/keycloak" && docker compose down)

log "2. Limpiando postgres (borra el volumen con el realm viejo)"
(cd "$ROOT/postgres" && docker compose down -v)

log "3. Levantando postgres limpio"
docker rm -f sso-postgres-postgres-1 >/dev/null 2>&1 || true
(cd "$ROOT/postgres" && docker compose up -d)
wait_healthy sso-postgres-postgres-1 30

log "4. Levantando keycloak (importa el realm-export.json nuevo)"
docker rm -f sso-keycloak-keycloak-1 >/dev/null 2>&1 || true
(cd "$ROOT/keycloak" && docker compose up -d)
wait_healthy sso-keycloak-keycloak-1 90

log "5. Levantando d2"
docker rm -f sso-d2-d2-1 >/dev/null 2>&1 || true
(cd "$ROOT/django" && docker compose up -d)
wait_healthy sso-d2-d2-1 60

log "6. Creando usuarios (ya incluyen los roles de d2)"
docker exec sso-d2-d2-1 python3 scripts/create_users.py

log "Listo"
