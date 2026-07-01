docker exec sso-d2-d2-1 python3 scripts/create_users.py


https://mailtrap.io/sandboxes/4722658/settings


# 1. Bajar d2 y keycloak
cd ~/projects/keycloak/new3/django && docker compose down
cd ~/projects/keycloak/new3/keycloak && docker compose down

# 2. Limpiar postgres (borra el volumen con el realm viejo)
cd ~/projects/keycloak/new3/postgres && docker compose down -v

# 3. Levantar postgres limpio
docker rm -f sso-postgres-postgres-1 2>/dev/null; docker compose up -d
# esperar "healthy" (~10s): docker compose ps

# 4. Levantar keycloak (importa el realm-export.json nuevo)
cd ~/projects/keycloak/new3/keycloak && docker rm -f sso-keycloak-keycloak-1 2>/dev/null; docker compose up -d
# esperar "healthy" (~30s): docker compose ps

# 5. Levantar d2
cd ~/projects/keycloak/new3/django && docker rm -f sso-d2-d2-1 2>/dev/null; docker compose up -d

# 6. Crear usuarios (ya incluyen los roles de d2)
docker exec sso-d2-d2-1 python3 scripts/create_users.py
El docker rm -f en cada paso evita el error de bind mount stale que te apareció antes.