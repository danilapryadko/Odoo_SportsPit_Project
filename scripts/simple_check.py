#!/usr/bin/env python3
"""
Простая проверка - пытаемся войти в Odoo
"""

import requests

ODOO_URL = "https://odoosportspitproject-production.up.railway.app"
EMAIL = "danila@usafitandjoy.com"
PASSWORD = "admin_sportpit_2024"

print("=" * 60)
print("🔍 ПРОВЕРКА БАЗЫ ДАННЫХ ODOO")
print("=" * 60)

# Проверяем доступность страницы входа
try:
    response = requests.get(f"{ODOO_URL}/web/login", timeout=10)
    
    if response.status_code == 200:
        print("\n✅ Страница входа доступна")
        
        # Если в HTML есть selector базы данных, значит БД не выбрана
        if "database/selector" in response.text:
            print("⚠️ Требуется выбор базы данных")
            print("🔍 Проверяю список баз данных...")
            
            # Пробуем получить список БД
            list_response = requests.post(
                f"{ODOO_URL}/web/database/list",
                json={"jsonrpc": "2.0", "method": "call", "params": {}, "id": 1}
            )
            
            if list_response.status_code == 200:
                data = list_response.json()
                databases = data.get("result", [])
                
                if databases:
                    print(f"\n✅ НАЙДЕНЫ БАЗЫ ДАННЫХ: {databases}")
                    
                    if "odoo_sportpit" in databases:
                        print("\n🎉 БАЗА ДАННЫХ 'odoo_sportpit' СОЗДАНА УСПЕШНО!")
                    else:
                        print("\n❌ База 'odoo_sportpit' не найдена в списке")
                else:
                    print("\n❌ Список баз данных пуст")
        else:
            print("✅ База данных уже выбрана или создана")
            
        print("\n📋 Попробуйте войти:")
        print(f"  1. Откройте: {ODOO_URL}/web/login")
        print(f"  2. Email: {EMAIL}")
        print(f"  3. Пароль: {PASSWORD}")
        
    else:
        print(f"❌ Страница недоступна (HTTP {response.status_code})")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n" + "=" * 60)
