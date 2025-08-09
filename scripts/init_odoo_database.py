#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных Odoo
Автор: Claude AI Assistant
Дата: 09.08.2025
"""

import requests
import sys
import time
import json
from urllib.parse import urljoin

# Конфигурация
ODOO_URL = "https://odoosportspitproject-production.up.railway.app"
MASTER_PASSWORD = "SportPit2024Master"
DB_NAME = "odoo_sportpit"
ADMIN_EMAIL = "danila@usafitandjoy.com"
ADMIN_PASSWORD = "admin_sportpit_2024"
LANG = "ru_RU"
COUNTRY_CODE = "ru"

def check_odoo_status():
    """Проверка доступности Odoo"""
    try:
        response = requests.get(urljoin(ODOO_URL, "/web/database/selector"))
        if response.status_code == 200:
            print("✅ Odoo доступен")
            return True
        else:
            print(f"❌ Odoo недоступен: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к Odoo: {e}")
        return False

def list_databases():
    """Получить список существующих баз данных"""
    try:
        url = urljoin(ODOO_URL, "/web/database/list")
        data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {},
            "id": 1
        }
        response = requests.post(url, json=data)
        result = response.json()
        
        if "result" in result:
            databases = result["result"]
            if databases:
                print(f"📊 Существующие базы данных: {', '.join(databases)}")
            else:
                print("📊 Нет существующих баз данных")
            return databases
        return []
    except Exception as e:
        print(f"⚠️ Не удалось получить список баз данных: {e}")
        return []

def create_database():
    """Создание новой базы данных Odoo"""
    print("\n🔄 Создание базы данных Odoo...")
    
    # Проверяем, существует ли уже база
    existing_dbs = list_databases()
    if DB_NAME in existing_dbs:
        print(f"✅ База данных '{DB_NAME}' уже существует")
        return True
    
    try:
        url = urljoin(ODOO_URL, "/web/database/create")
        data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "master_pwd": MASTER_PASSWORD,
                "name": DB_NAME,
                "login": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD,
                "lang": LANG,
                "country_code": COUNTRY_CODE,
                "phone": "",
                "demo": False
            },
            "id": 1
        }
        
        print(f"📝 Параметры создания:")
        print(f"   - База данных: {DB_NAME}")
        print(f"   - Email администратора: {ADMIN_EMAIL}")
        print(f"   - Язык: {LANG}")
        print(f"   - Страна: {COUNTRY_CODE}")
        print(f"   - Демо-данные: Нет")
        
        response = requests.post(url, json=data, timeout=120)
        result = response.json()
        
        if "error" in result:
            print(f"❌ Ошибка создания БД: {result['error']}")
            return False
        
        print("✅ База данных успешно создана!")
        print("⏳ Ожидание инициализации базы данных...")
        time.sleep(10)
        
        return True
        
    except requests.Timeout:
        print("⏱️ Создание БД занимает время... Проверьте статус через несколько минут")
        return False
    except Exception as e:
        print(f"❌ Ошибка при создании БД: {e}")
        return False

def test_login():
    """Тестирование входа в систему"""
    print("\n🔐 Проверка входа в систему...")
    
    try:
        session = requests.Session()
        
        # Получаем CSRF токен
        login_page = session.get(urljoin(ODOO_URL, "/web/login"))
        
        # Попытка входа
        url = urljoin(ODOO_URL, "/web/login")
        data = {
            "login": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "db": DB_NAME,
            "redirect": "/web"
        }
        
        response = session.post(url, data=data, allow_redirects=False)
        
        if response.status_code in [302, 303]:
            print("✅ Вход в систему успешен!")
            print(f"🌐 URL для входа: {ODOO_URL}/web/login")
            print(f"📧 Email: {ADMIN_EMAIL}")
            print(f"🔑 Пароль: {ADMIN_PASSWORD}")
            return True
        else:
            print("⚠️ Не удалось войти в систему")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании входа: {e}")
        return False

def main():
    """Основная функция"""
    print("=" * 60)
    print("🚀 ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ODOO SPORTPIT")
    print("=" * 60)
    
    # Проверяем доступность Odoo
    if not check_odoo_status():
        print("\n⚠️ Odoo недоступен. Проверьте статус деплоя на Railway.")
        sys.exit(1)
    
    # Создаем базу данных
    if create_database():
        # Тестируем вход
        test_login()
        
        print("\n" + "=" * 60)
        print("✅ ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 60)
        print("\n📋 Следующие шаги:")
        print("1. Войдите в Odoo по адресу: " + ODOO_URL)
        print("2. Установите необходимые модули (MRP, Inventory, Purchase, Sales)")
        print("3. Настройте компанию и реквизиты")
        print("4. Создайте структуру складов и продуктов")
        
        # Обновляем статус проекта
        print("\n📝 Обновление PROJECT_STATUS.md...")
        update_project_status()
    else:
        print("\n❌ Инициализация не завершена. См. ошибки выше.")
        sys.exit(1)

def update_project_status():
    """Обновление файла статуса проекта"""
    # Здесь будет логика обновления PROJECT_STATUS.md
    print("✅ Статус проекта будет обновлен вручную")

if __name__ == "__main__":
    main()
