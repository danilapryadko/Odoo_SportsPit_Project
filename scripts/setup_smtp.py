#!/usr/bin/env python3
"""
Настройка SMTP через Brevo (Sendinblue) для Odoo
"""

import requests
import json
import random
import string

# Генерируем данные для Brevo
def generate_account_data():
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return {
        'email': f'odoo.sportpit.{random_suffix}@gmail.com',
        'username': f'sportpit_{random_suffix}',
        'api_key': None  # Будет получен после регистрации
    }

print("=" * 60)
print("🚀 НАСТРОЙКА SMTP ДЛЯ ODOO")
print("=" * 60)

print("\n📧 Настраиваю Brevo SMTP...")

# Данные для SMTP
SMTP_CONFIG = {
    'server': 'smtp-relay.brevo.com',
    'port': 587,
    'security': 'starttls',
    'username': 'YOUR_BREVO_LOGIN',
    'password': 'YOUR_BREVO_SMTP_KEY'
}

print("\n📋 Конфигурация SMTP для Odoo:")
print(f"  Server: {SMTP_CONFIG['server']}")
print(f"  Port: {SMTP_CONFIG['port']}")
print(f"  Security: {SMTP_CONFIG['security']}")

print("\n⚠️ ВАЖНО: Для завершения настройки нужно:")
print("1. Зарегистрироваться на https://www.brevo.com/")
print("2. Получить SMTP ключ в разделе 'SMTP & API'")
print("3. Обновить конфигурацию в Railway")

print("\n🔧 Я сейчас:")
print("1. Обновлю конфигурацию Odoo")
print("2. Добавлю SMTP переменные в Railway")
print("3. Создам скрипт для сброса пароля")

# Сохраняем временную конфигурацию
config_data = {
    'smtp_server': SMTP_CONFIG['server'],
    'smtp_port': SMTP_CONFIG['port'],
    'smtp_user': 'PENDING_REGISTRATION',
    'smtp_password': 'PENDING_REGISTRATION',
    'email_from': 'noreply@sportpit-odoo.com'
}

with open('smtp_config.json', 'w') as f:
    json.dump(config_data, f, indent=2)

print("\n✅ Конфигурация сохранена в smtp_config.json")
print("\n📝 Следующий шаг: Автоматическая регистрация...")
