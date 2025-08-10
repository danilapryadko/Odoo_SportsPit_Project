#!/bin/bash

# Скрипт запуска Odoo с очисткой лишних баз

echo "=== Starting Odoo with DB cleanup ==="

# Ждём доступности PostgreSQL
until PGPASSWORD=odoo_sportpit_2024 psql -h postgresql-odoo.railway.internal -U odoo -d postgres -c '\q'; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

echo "PostgreSQL is ready!"

# Удаляем лишние базы данных
echo "Removing extra databases..."
PGPASSWORD=odoo_sportpit_2024 psql -h postgresql-odoo.railway.internal -U odoo -d postgres << EOF
-- Завершаем активные подключения к лишним БД
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname IN ('odoo_sportpit_new', 'production') 
AND pid <> pg_backend_pid();

-- Удаляем лишние базы
DROP DATABASE IF EXISTS odoo_sportpit_new;
DROP DATABASE IF EXISTS production;
EOF

echo "Extra databases removed"

# Проверяем существование основной базы данных
DB_EXISTS=$(PGPASSWORD=odoo_sportpit_2024 psql -h postgresql-odoo.railway.internal -U odoo -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='odoo_sportpit'")

if [ "$DB_EXISTS" != "1" ]; then
    echo "Creating database odoo_sportpit..."
    PGPASSWORD=odoo_sportpit_2024 psql -h postgresql-odoo.railway.internal -U odoo -d postgres -c "CREATE DATABASE odoo_sportpit WITH OWNER odoo ENCODING 'UTF8';"
    echo "Database created!"
fi

# Запускаем Odoo
echo "Starting Odoo server..."
exec odoo -c /etc/odoo/odoo.conf -d odoo_sportpit
