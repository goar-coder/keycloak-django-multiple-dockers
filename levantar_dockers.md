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

# 3. D2 (necesita keycloak + postgres arriba)
cd ../django
docker compose up -d

Parar un servicio individual sin afectar a los demás:

docker compose down

(ejecutado dentro de la carpeta del servicio correspondiente: postgres/, keycloak/ o django/)

Por qué funciona la conexión entre proyectos
Todos los contenedores se unen a la misma red Docker sso-network (creada una vez, fuera de cualquier proyecto compose). Docker resuelve los nombres de servicio (postgres, keycloak) vía DNS interno dentro de esa red, sin importar en qué docker compose up se originó cada contenedor — por eso d2 sigue pudiendo conectarse a postgres:5432 y keycloak:8080 aunque vivan en proyectos distintos.

Nota: cada carpeta (postgres/, keycloak/, django/) tiene su propio docker-compose.yml y .env, con solo las variables que ese servicio necesita. No hay un docker-compose.yml raíz ni servicios d1/d3 — solo existe d2.
