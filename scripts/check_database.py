#!/usr/bin/env python3
"""
Проверка статуса базы данных Odoo
"""

import requests
import json

ODOO_URL = "https://odoosportspitproject-production.up.railway.app"
DB_NAME = "odoo_sportpit"

def check_database():
    print("🔍 Проверка базы данных...")
    
    try:
        # Пробуем получить список БД
        url = f"{ODOO_URL}/web/database/list"
        headers = {'Content-Type': 'application/json'}
        data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {},
            "id": 1
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                databases = result.get("result", [])
                
                if databases:
                    print(f"✅ Найдены базы данных: {databases}")
                    
                    if DB_NAME in databases:
                        print(f"✅ База данных '{DB_NAME}' СОЗДАНА УСПЕШНО!")
                        return True
                    else:
                        print(f"❌ База данных '{DB_NAME}' не найдена")
                        return False
                else:
                    print("❌ Нет созданных баз данных")
                    return False
        
        print(f"⚠️ Не удалось получить список БД (HTTP {response.status_code})")
        return None
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    result = check_database()
    
    if result:
        print("\n✅ БАЗА ДАННЫХ СОЗДАНА!")
        print("\n📋 Данные для входа:")
        print(f"  URL: {ODOO_URL}/web/login")
        print(f"  Email: danila@usafitandjoy.com")
        print(f"  Пароль: admin_sportpit_2024")
        print("\n🎯 Следующий шаг:")
        print("  python3 scripts/install_odoo_modules.py")
    elif result is False:
        print("\n❌ База данных не создана")
        print("Попробуйте создать вручную на странице:")
        print(f"{ODOO_URL}/web/database/manager")
    else:
        print("\n⚠️ Не удалось проверить статус")
        print("Проверьте вручную на странице:")
        print(f"{ODOO_URL}/web/database/selector")
