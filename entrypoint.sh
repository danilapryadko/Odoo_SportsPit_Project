#!/bin/bash
set -e

echo "==================================="
echo "Starting Odoo Container"
echo "==================================="

# Проверяем переменные окружения
echo "Environment variables:"
echo "  DB_HOST=$DB_HOST"
echo "  DB_PORT=$DB_PORT"
echo "  DB_NAME=$DB_NAME"
echo "  DB_USER=$DB_USER"
echo "  PORT=$PORT"

# Тестируем подключение к БД
echo ""
echo "Testing database connection..."
/test-db.sh

# Подставляем переменные окружения в конфигурацию
echo ""
echo "Generating Odoo config..."
envsubst < /etc/odoo/odoo.conf.template > /etc/odoo/odoo.conf

# Показываем сгенерированный конфиг
echo ""
echo "Database config in odoo.conf:"
grep -E "db_" /etc/odoo/odoo.conf

echo ""
echo "Starting Odoo with network database connection..."
echo "==================================="

# Запускаем Odoo с явным указанием сетевых параметров БД
exec odoo \
    --db_host="$DB_HOST" \
    --db_port="$DB_PORT" \
    --db_user="$DB_USER" \
    --db_password="$DB_PASSWORD" \
    --http-port="$PORT" \
    -c /etc/odoo/odoo.conf
