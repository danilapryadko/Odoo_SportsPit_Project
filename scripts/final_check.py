#!/usr/bin/env python3
"""
ФИНАЛЬНАЯ ПРОВЕРКА: Какой же пароль у БД?
"""

import requests
import json

ODOO_URL = "https://odoosportspitproject-production.up.railway.app"

# ВСЕ возможные комбинации email и паролей
EMAILS = [
    "danila@usafitandjoy.com",
    "admin@admin.com",
    "admin",
    "administrator"
]

PASSWORDS = [
    "admin",
    "Admin", 
    "admin123",
    "Admin123",
    "password",
    "123456",
    "admin_sportpit_2024",
    "SportPit2024Master",
    "SportPit2024",
    "odoo",
    "demo"
]

print("=" * 60)
print("🔍 ФИНАЛЬНАЯ ПРОВЕРКА ВСЕХ КОМБИНАЦИЙ")
print("=" * 60)

session = requests.Session()
found = False

for email in EMAILS:
    for password in PASSWORDS:
        try:
            print(f"Пробую: {email:30s} / {password:20s} ", end="")
            
            # Получаем страницу для CSRF
            session.get(f"{ODOO_URL}/web/login")
            
            # Пробуем войти
            response = session.post(
                f"{ODOO_URL}/web/login",
                data={
                    'login': email,
                    'password': password,
                    'db': 'odoo_sportpit'
                },
                allow_redirects=False
            )
            
            if response.status_code in [302, 303]:
                location = response.headers.get('location', '')
                if '/web' in location and 'login' not in location:
                    print("✅ НАШЕЛ!")
                    print("\n" + "🎉"*30)
                    print(f"\n✅ РАБОЧИЕ ДАННЫЕ:")
                    print(f"  Email: {email}")
                    print(f"  Password: {password}")
                    print("\n" + "🎉"*30)
                    found = True
                    break
            
            print("❌")
            
        except Exception as e:
            print(f"❌ Ошибка")
    
    if found:
        break

if not found:
    print("\n❌ НИ ОДИН ПАРОЛЬ НЕ ПОДОШЕЛ!")
    print("\n🔨 ЕДИНСТВЕННОЕ РЕШЕНИЕ:")
    print("1. Откройте: https://odoosportspitproject-production.up.railway.app/web/database/manager")
    print("2. Удалите базу odoo_sportpit")
    print("3. Создайте новую с паролем: admin")
    print("\nИли скажите мне, какой пароль вы вводили при создании БД!")
