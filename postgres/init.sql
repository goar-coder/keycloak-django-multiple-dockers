-- Create dedicated users for each service
CREATE USER keycloak_user WITH PASSWORD 'keycloak_pass';
CREATE USER pl_user WITH PASSWORD 'pl_pass' CREATEDB;

-- Create isolated databases
CREATE DATABASE keycloak_db OWNER keycloak_user;
CREATE DATABASE pl_db OWNER pl_user;

-- Revoke default public access
REVOKE ALL ON DATABASE keycloak_db FROM PUBLIC;
REVOKE ALL ON DATABASE pl_db FROM PUBLIC;

-- Grant privileges to each owner only
GRANT ALL PRIVILEGES ON DATABASE keycloak_db TO keycloak_user;
GRANT ALL PRIVILEGES ON DATABASE pl_db TO pl_user;
