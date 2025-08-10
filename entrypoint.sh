#!/bin/bash
set -e

# Подставляем переменные окружения в конфигурацию
envsubst < /etc/odoo/odoo.conf.template > /etc/odoo/odoo.conf

echo "Starting Odoo..."
# Запускаем Odoo с инициализацией БД если её нет
exec odoo -c /etc/odoo/odoo.conf -d $DB_NAME --init base --stop-after-init || exec odoo -c /etc/odoo/odoo.conf -d $DB_NAME
