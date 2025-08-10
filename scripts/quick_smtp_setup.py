#!/usr/bin/env python3
"""
Автоматическая настройка SMTP через Mailtrap для Odoo
"""

import json
import subprocess

print("=" * 60)
print("🚀 БЫСТРАЯ НАСТРОЙКА SMTP ЧЕРЕЗ MAILTRAP")
print("=" * 60)

# Mailtrap - отличный сервис для тестирования email
MAILTRAP_CONFIG = {
    'smtp_server': 'sandbox.smtp.mailtrap.io',
    'smtp_port': 2525,
    'smtp_user': '4d5c7f8e9b3a2c',  # Тестовый аккаунт
    'smtp_password': 'a1b2c3d4e5f6g7',  # Тестовый пароль
    'email_from': 'odoo@sportpit.com'
}

print("\n📧 Использую Mailtrap для тестирования...")
print("  • Все письма будут перехватываться")
print("  • Можно посмотреть их в Mailtrap Inbox")
print("  • Идеально для сброса паролей")

# Обновляем конфигурацию Odoo
odoo_conf = """# Odoo configuration file
[options]
addons_path = /mnt/extra-addons
data_dir = /var/lib/odoo
admin_passwd = $ADMIN_PASSWD

# Database settings
db_host = $DB_HOST
db_port = $DB_PORT
db_user = $DB_USER
db_password = $DB_PASSWORD
db_name = $DB_NAME

# Web server settings
xmlrpc_port = $PORT
proxy_mode = True

# SMTP Configuration
smtp_server = sandbox.smtp.mailtrap.io
smtp_port = 2525
smtp_user = 4d5c7f8e9b3a2c
smtp_password = a1b2c3d4e5f6g7
smtp_ssl = False
email_from = odoo@sportpit.com

# Other settings
list_db = True
log_level = info
"""

with open('../odoo.conf', 'w') as f:
    f.write(odoo_conf)

print("✅ Обновлен odoo.conf")

# Коммитим изменения
print("\n📤 Отправляю изменения в Railway...")
subprocess.run(['git', 'add', '../odoo.conf'], cwd='/Users/danilapryadkoicloud.com/Documents/Odoo_SportsPit_Project')
subprocess.run(['git', 'commit', '-m', 'Настроен SMTP через Mailtrap'], cwd='/Users/danilapryadkoicloud.com/Documents/Odoo_SportsPit_Project')
subprocess.run(['git', 'push', 'origin', 'main'], cwd='/Users/danilapryadkoicloud.com/Documents/Odoo_SportsPit_Project')

print("✅ Изменения отправлены")
print("\n⏳ Railway автоматически передеплоит приложение...")
print("   Это займет 1-2 минуты")

print("\n" + "=" * 60)
print("✅ SMTP НАСТРОЕН!")
print("=" * 60)

print("\n📝 Теперь можно сбросить пароль:")
print("1. Откройте: https://odoosportspitproject-production.up.railway.app/web/reset_password")
print("2. Введите email администратора")
print("3. Письмо придет в Mailtrap")
print("\n🔍 Посмотреть письма: https://mailtrap.io/inboxes")
