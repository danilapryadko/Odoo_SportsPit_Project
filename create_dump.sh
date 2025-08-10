#!/bin/bash

# Скрипт создания дампа БД для быстрого восстановления

echo "Creating PostgreSQL dump..."

# Подключаемся к БД и создаём дамп
PGPASSWORD=odoo_sportpit_2024 pg_dump \
  -h postgresql-odoo.railway.internal \
  -U odoo \
  -d odoo_sportpit \
  --no-owner \
  --no-acl \
  --if-exists \
  --clean \
  > /tmp/odoo_sportpit_dump.sql

echo "Dump created at /tmp/odoo_sportpit_dump.sql"

# Копируем в папку проекта
cp /tmp/odoo_sportpit_dump.sql /mnt/extra-addons/odoo_sportpit_dump.sql

echo "Dump saved to project directory"
