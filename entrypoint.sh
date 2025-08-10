#!/bin/bash
set -e

# Подставляем переменные окружения в конфигурацию
envsubst < /etc/odoo/odoo.conf.template > /etc/odoo/odoo.conf

# Запускаем Odoo
exec odoo -c /etc/odoo/odoo.conf
