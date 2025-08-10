#!/bin/bash

# Скрипт запуска Odoo с очисткой лишних БД

echo "=== Starting Odoo ==="

# Ждём доступности PostgreSQL
until PGPASSWORD=odoo_sportpit_2024 psql -h postgresql-odoo.railway.internal -U odoo -d postgres -c '\q'; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

echo "PostgreSQL is ready!"

# Удаляем все БД кроме odoo_sportpit
echo "Cleaning up extra databases..."
PGPASSWORD=odoo_sportpit_2024 psql -h postgresql-odoo.railway.internal -U odoo -d postgres << EOF
-- Получаем список БД для удаления
DO \$\$
DECLARE
    db_name TEXT;
BEGIN
    FOR db_name IN 
        SELECT datname FROM pg_database 
        WHERE datname NOT IN ('postgres', 'template0', 'template1', 'odoo_sportpit')
        AND datistemplate = false
    LOOP
        -- Завершаем соединения
        EXECUTE format('SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %L', db_name);
        -- Удаляем БД
        EXECUTE format('DROP DATABASE IF EXISTS %I', db_name);
        RAISE NOTICE 'Dropped database: %', db_name;
    END LOOP;
END \$\$;
EOF

echo "Database cleanup complete"

# Проверяем существование основной БД
DB_EXISTS=$(PGPASSWORD=odoo_sportpit_2024 psql -h postgresql-odoo.railway.internal -U odoo -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='odoo_sportpit'")

if [ "$DB_EXISTS" != "1" ]; then
    echo "Creating database odoo_sportpit..."
    PGPASSWORD=odoo_sportpit_2024 psql -h postgresql-odoo.railway.internal -U odoo -d postgres -c "CREATE DATABASE odoo_sportpit WITH OWNER odoo ENCODING 'UTF8';"
fi

# Запускаем Odoo
echo "Starting Odoo server..."
exec odoo -c /etc/odoo/odoo.conf -d odoo_sportpit
