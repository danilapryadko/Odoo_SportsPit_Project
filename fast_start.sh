#!/bin/bash

echo "=== Fast Odoo Startup ==="

# Проверяем доступность PostgreSQL
for i in {1..10}; do
  if PGPASSWORD=odoo_sportpit_2024 psql -h postgresql-odoo.railway.internal -U odoo -d postgres -c '\q' 2>/dev/null; then
    echo "PostgreSQL is ready!"
    break
  fi
  echo "Waiting for PostgreSQL... ($i/10)"
  sleep 2
done

# Проверяем существует ли БД
DB_EXISTS=$(PGPASSWORD=odoo_sportpit_2024 psql -h postgresql-odoo.railway.internal -U odoo -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='odoo_sportpit'")

if [ "$DB_EXISTS" != "1" ]; then
    echo "Database doesn't exist, creating..."
    PGPASSWORD=odoo_sportpit_2024 createdb -h postgresql-odoo.railway.internal -U odoo odoo_sportpit
fi

# Запускаем Odoo БЕЗ инициализации модулей
echo "Starting Odoo (no init mode)..."
exec odoo \
  --db_host=postgresql-odoo.railway.internal \
  --db_port=5432 \
  --db_user=odoo \
  --db_password=odoo_sportpit_2024 \
  --database=odoo_sportpit \
  --db-filter='^odoo_sportpit$' \
  --no-database-list \
  --without-demo=all \
  --load= \
  --init= \
  --update=
