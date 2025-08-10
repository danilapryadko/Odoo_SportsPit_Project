#!/bin/bash

# Скрипт запуска Odoo

echo "=== Starting Odoo ==="

# Ждём доступности PostgreSQL
until PGPASSWORD=odoo_sportpit_2024 psql -h postgresql-odoo.railway.internal -U odoo -d postgres -c '\q'; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

echo "PostgreSQL is ready!"

# Проверяем существование базы данных
DB_EXISTS=$(PGPASSWORD=odoo_sportpit_2024 psql -h postgresql-odoo.railway.internal -U odoo -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='odoo_sportpit'")

if [ "$DB_EXISTS" != "1" ]; then
    echo "Creating database odoo_sportpit..."
    PGPASSWORD=odoo_sportpit_2024 psql -h postgresql-odoo.railway.internal -U odoo -d postgres -c "CREATE DATABASE odoo_sportpit WITH OWNER odoo ENCODING 'UTF8';"
    echo "Database created! Will initialize on first run..."
fi

# Запускаем Odoo
echo "Starting Odoo server..."
exec odoo -c /etc/odoo/odoo.conf
