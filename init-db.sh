#!/bin/bash
set -e

# Создаем базу данных odoo_sportpit если она не существует
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
    SELECT 'CREATE DATABASE odoo_sportpit OWNER odoo'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'odoo_sportpit')\gexec
    
    GRANT ALL PRIVILEGES ON DATABASE odoo_sportpit TO odoo;
EOSQL

echo "Database initialization completed"
