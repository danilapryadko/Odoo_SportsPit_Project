#!/bin/bash

# Простой запуск Odoo

echo "=== Starting Odoo ==="

# Ждём PostgreSQL
until PGPASSWORD=odoo_sportpit_2024 psql -h postgresql-odoo.railway.internal -U odoo -d postgres -c '\q'; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

echo "PostgreSQL is ready!"

# Запускаем Odoo БЕЗ флага инициализации
echo "Starting Odoo server..."
exec odoo -c /etc/odoo/odoo.conf -d odoo_sportpit
