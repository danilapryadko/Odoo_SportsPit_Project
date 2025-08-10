#!/bin/bash
set -e

# Ждем, пока PostgreSQL запустится
echo "Waiting for PostgreSQL to start..."
sleep 10

# Подставляем переменные окружения в конфигурацию
envsubst < /etc/odoo/odoo.conf.template > /etc/odoo/odoo.conf

# Проверяем подключение к БД
echo "Checking database connection..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "SELECT 1;" || {
    echo "Warning: Cannot connect to database, but continuing..."
}

# Проверяем, существует ли база данных
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || {
    echo "Creating database $DB_NAME..."
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
}

echo "Starting Odoo..."
# Запускаем Odoo с указанием конкретной БД
exec odoo -c /etc/odoo/odoo.conf -d $DB_NAME --db-filter="^${DB_NAME}$"
