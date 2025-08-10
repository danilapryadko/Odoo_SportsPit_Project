#!/usr/bin/env python3
"""
Подбор пароля для Odoo
"""

import requests
import time

ODOO_URL = "https://odoosportspitproject-production.up.railway.app"
EMAIL = "danila@usafitandjoy.com"

# Список паролей для перебора
PASSWORDS = [
    "admin_sportpit_2024",
    "admin123",
    "admin",
    "SportPit2024Master",
    "SportPit2024",
    "sportpit2024",
    "odoo_sportpit_2024",
    "odoo",
    "password",
    "123456",
    "12345678",
    "dbny-777k-4ggc",
    "Odoo2024",
    "odoo2024",
    "Admin2024",
    "admin2024",
    "SportPit",
    "sportpit",
    "danila",
    "usafitandjoy",
    "Password1",
    "Password123",
    "Qwerty123",
    "qwerty123",
    "Admin123",
    "odoo_sportpit",
    "OdooSportPit2024",
    "odoosportpit",
    "railway",
    "Railway2024",
    "test",
    "demo",
    "1234",
    "0000",
    "1111",
    "admin_password",
    "administrator",
    "root",
    "toor",
    "pass",
    "Password",
    "password123"
]

def try_login(email, password):
    """Попытка входа с заданными учетными данными"""
    session = requests.Session()
    
    try:
        # Получаем страницу входа для CSRF токена
        login_page = session.get(f"{ODOO_URL}/web/login", timeout=5)
        
        # Пытаемся войти
        login_data = {
            'login': email,
            'password': password,
            'db': 'odoo_sportpit',
            'redirect': '/web'
        }
        
        response = session.post(
            f"{ODOO_URL}/web/login",
            data=login_data,
            allow_redirects=False,
            timeout=5
        )
        
        # Проверяем успешность входа
        if response.status_code in [302, 303]:
            # Проверяем, куда редиректит
            if 'location' in response.headers:
                location = response.headers['location']
                if '/web' in location and 'login' not in location:
                    return True
        
        # Проверяем по содержимому ответа
        if response.status_code == 200:
            text = response.text.lower()
            if 'invalid' not in text and 'error' not in text and 'неверный' not in text:
                # Дополнительная проверка
                check = session.get(f"{ODOO_URL}/web", timeout=5)
                if 'login' not in check.url:
                    return True
                    
    except:
        pass
    
    return False

def main():
    print("=" * 60)
    print("🔐 ПОДБОР ПАРОЛЯ ДЛЯ ODOO")
    print("=" * 60)
    print(f"\n📧 Email: {EMAIL}")
    print(f"🔍 Паролей для проверки: {len(PASSWORDS)}\n")
    
    found = False
    
    for i, password in enumerate(PASSWORDS, 1):
        print(f"[{i}/{len(PASSWORDS)}] Пробую: {password:<25}", end=" ")
        
        if try_login(EMAIL, password):
            print("✅ ПОДОШЕЛ!")
            print("\n" + "🎉" * 30)
            print(f"\n✅ ПАРОЛЬ НАЙДЕН: {password}")
            print(f"\n📋 Данные для входа:")
            print(f"  URL: {ODOO_URL}")
            print(f"  Email: {EMAIL}")
            print(f"  Пароль: {password}")
            print("\n" + "🎉" * 30)
            found = True
            break
        else:
            print("❌")
            time.sleep(0.5)  # Небольшая задержка между попытками
    
    if not found:
        print("\n❌ Пароль не найден в списке")
        print("\n🔧 Что делать дальше:")
        print("1. Попробуйте вспомнить, какой пароль вы вводили при создании БД")
        print("2. Удалите БД и создайте заново:")
        print(f"   - Откройте {ODOO_URL}/web/database/manager")
        print("   - Удалите базу odoo_sportpit")
        print("   - Создайте новую с известным паролем")

if __name__ == "__main__":
    main()
