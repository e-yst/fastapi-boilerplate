#!/bin/bash
set -e

psql -v ON_ERROR_STOP=0 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER hydra WITH ENCRYPTED PASSWORD 'dbsecret';
	CREATE DATABASE hydra;
	GRANT ALL PRIVILEGES ON DATABASE hydra TO hydra;

	CREATE USER kratos WITH ENCRYPTED PASSWORD 'dbsecret';
	CREATE DATABASE kratos;
	GRANT ALL PRIVILEGES ON DATABASE kratos TO kratos;
EOSQL

psql -v ON_ERROR_STOP=0 --username "$POSTGRES_USER" --dbname "hydra" <<-EOSQL
	GRANT ALL ON SCHEMA public TO hydra;
EOSQL

psql -v ON_ERROR_STOP=0 --username "$POSTGRES_USER" --dbname "kratos" <<-EOSQL
	GRANT ALL ON SCHEMA public TO kratos;
EOSQL
