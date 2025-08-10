#!/usr/bin/env python3
"""
Простой скрипт для открытия Odoo и помощи в создании БД
Автор: Claude AI Assistant
Дата: 09.08.2025
"""

import webbrowser
import time
import subprocess

# Конфигурация
ODOO_URL = "https://odoosportspitproject-production.up.railway.app"
MASTER_PASSWORD = "SportPit2024Master"
DB_NAME = "odoo_sportpit"
ADMIN_EMAIL = "danila@usafitandjoy.com"
ADMIN_PASSWORD = "admin_sportpit_2024"

def main():
    print("=" * 60)
    print("🚀 ПОМОЩНИК СОЗДАНИЯ БД ODOO")
    print("=" * 60)
    
    print("\n📋 Данные для создания БД:")
    print(f"  Master Password: {MASTER_PASSWORD}")
    print(f"  Database Name: {DB_NAME}")
    print(f"  Email: {ADMIN_EMAIL}")
    print(f"  Password: {ADMIN_PASSWORD}")
    print(f"  Language: Russian (Русский)")
    print(f"  Country: Russia")
    
    print("\n🌐 Открываю Odoo в браузере...")
    
    # Открываем страницу управления БД
    webbrowser.open(f"{ODOO_URL}/web/database/manager")
    
    print("\n📝 ИНСТРУКЦИИ:")
    print("1. Нажмите 'Create Database'")
    print("2. Введите данные выше в форму")
    print("3. Снимите галочку 'Load demonstration data'")
    print("4. Нажмите 'Create Database'")
    print("5. Подождите 1-2 минуты")
    
    print("\n⏳ Ожидание создания БД...")
    time.sleep(5)
    
    # Копируем данные в буфер обмена для удобства
    try:
        subprocess.run(['pbcopy'], input=ADMIN_EMAIL.encode(), check=True)
        print("\n📋 Email скопирован в буфер обмена!")
    except:
        pass
    
    print("\n✅ После создания БД:")
    print(f"  1. Войдите с email: {ADMIN_EMAIL}")
    print(f"  2. И паролем: {ADMIN_PASSWORD}")
    print(f"  3. Запустите install_odoo_modules.py для установки модулей")
    print(f"  4. Запустите create_products_and_bom.py для создания продуктов")

if __name__ == "__main__":
    main()
