#!/bin/bash
set -e

# Ждем пока PostgreSQL станет доступен
echo "Waiting for PostgreSQL..."
while ! nc -z ${DB_HOST} ${DB_PORT:-5432}; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Проверяем, существует ли база данных
export PGPASSWORD=${DB_PASSWORD}
if psql -h ${DB_HOST} -p ${DB_PORT:-5432} -U ${DB_USER} -lqt | cut -d \| -f 1 | grep -qw ${DB_NAME}; then
    echo "Database ${DB_NAME} already exists"
else
    echo "Creating database ${DB_NAME}..."
    createdb -h ${DB_HOST} -p ${DB_PORT:-5432} -U ${DB_USER} ${DB_NAME}
    echo "Database created!"
fi

# Запускаем Odoo
exec odoo \
    --http-port=${PORT:-8069} \
    --db_host=${DB_HOST} \
    --db_port=${DB_PORT:-5432} \
    --db_user=${DB_USER} \
    --db_password=${DB_PASSWORD} \
    --database=${DB_NAME} \
    --db-filter=.* \
    --list-db \
    "$@"
