#!/bin/bash
set -e

# Подставляем переменные окружения в конфигурацию
envsubst < /etc/odoo/odoo.conf.template > /etc/odoo/odoo.conf

# Проверяем конфигурацию
echo "Database configuration:"
echo "  DB_HOST=$DB_HOST"
echo "  DB_PORT=$DB_PORT"
echo "  DB_NAME=$DB_NAME"
echo "  DB_USER=$DB_USER"

# Проверяем, что переменные подставились в конфиг
echo "Checking generated config:"
grep -E "db_host|db_port|db_name|db_user" /etc/odoo/odoo.conf

echo "Starting Odoo..."
# Запускаем Odoo БЕЗ указания конкретной БД, пусть использует конфиг
exec odoo -c /etc/odoo/odoo.conf
