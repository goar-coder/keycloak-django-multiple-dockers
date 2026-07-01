1. Crear la red compartida una sola vez (todos los compose la referencian como external: true):

docker network create sso-network

2. Levantar en orden (porque depends_on con condition: service_healthy no funciona entre proyectos distintos — cada docker compose up es un proyecto independiente, así que hay que esperar manualmente):

# 1. Postgres
cd postgres
docker compose up -d
docker compose ps   # esperar "healthy"

# 2. Keycloak (necesita postgres arriba)
cd ../keycloak
docker compose up -d
docker compose ps   # esperar "healthy" (~30-60s)

# 3. pl (Django; necesita keycloak + postgres arriba)
cd ../django
docker compose up -d
docker compose ps   # esperar "healthy"

# 4. Crear usuarios de prueba (el realm se importa sin usuarios)
docker exec sso-pl-pl-1 python3 scripts/create_users.py


