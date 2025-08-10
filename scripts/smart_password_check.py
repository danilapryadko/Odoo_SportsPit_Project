#!/usr/bin/env python3
"""
Умный подбор пароля с анализом ответов
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import time

ODOO_URL = "https://odoosportspitproject-production.up.railway.app"
EMAIL = "danila@usafitandjoy.com"

# Расширенный список паролей
PASSWORDS = [
    # Оригинальные из документации
    "admin_sportpit_2024",
    "SportPit2024Master", 
    "dbny-777k-4ggc",
    
    # Вариации SportPit
    "SportPit2024",
    "sportpit2024",
    "SportPit",
    "sportpit",
    "SPORTPIT2024",
    "Sportpit2024",
    
    # Вариации admin
    "admin",
    "Admin",
    "ADMIN",
    "admin123",
    "Admin123",
    "admin2024",
    "Admin2024",
    "administrator",
    
    # Вариации odoo
    "odoo",
    "Odoo",
    "ODOO", 
    "odoo2024",
    "Odoo2024",
    "odoo_sportpit",
    "OdooSportPit",
    "odoo_sportpit_2024",
    
    # Простые пароли
    "password",
    "Password",
    "password123",
    "Password123",
    "123456",
    "12345678",
    "1234567890",
    "qwerty",
    "qwerty123",
    
    # Связанные с проектом
    "danila",
    "Danila",
    "usafitandjoy",
    "railway",
    "Railway",
    
    # Дефолтные
    "demo",
    "test",
    "root",
    "pass",
    "1234",
    "0000",
    "1111"
]

def create_session():
    """Создание сессии с retry логикой"""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def check_via_jsonrpc(email, password):
    """Проверка через JSON-RPC API"""
    session = create_session()
    
    try:
        # Пробуем аутентификацию через JSON-RPC
        url = f"{ODOO_URL}/jsonrpc"
        headers = {'Content-Type': 'application/json'}
        
        data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "common",
                "method": "authenticate",
                "args": ["odoo_sportpit", email, password, {}]
            },
            "id": 1
        }
        
        response = session.post(url, json=data, headers=headers, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('result'):
                return True
                
    except:
        pass
    
    return False

def check_via_web(email, password):
    """Проверка через веб-форму"""
    session = create_session()
    
    try:
        # Получаем CSRF токен
        login_page = session.get(f"{ODOO_URL}/web/login", timeout=5)
        
        # Извлекаем CSRF если есть
        csrf_token = None
        if 'csrf_token' in login_page.text:
            import re
            match = re.search(r'csrf_token["\s:]+["\'](.*?)["\']', login_page.text)
            if match:
                csrf_token = match.group(1)
        
        # Подготавливаем данные
        login_data = {
            'login': email,
            'password': password,
            'db': 'odoo_sportpit'
        }
        
        if csrf_token:
            login_data['csrf_token'] = csrf_token
        
        # Отправляем
        response = session.post(
            f"{ODOO_URL}/web/login",
            data=login_data,
            allow_redirects=False,
            timeout=5
        )
        
        # Анализируем ответ
        if response.status_code in [302, 303]:
            location = response.headers.get('location', '')
            if '/web' in location and 'login' not in location:
                return True
                
        # Проверяем куки
        if 'session_id' in session.cookies:
            # Проверяем валидность сессии
            check = session.get(f"{ODOO_URL}/web", timeout=5)
            if check.status_code == 200 and 'login' not in check.url:
                return True
                
    except:
        pass
    
    return False

def main():
    print("=" * 60)
    print("🔐 УМНЫЙ ПОДБОР ПАРОЛЯ ДЛЯ ODOO")
    print("=" * 60)
    print(f"\n📧 Email: {EMAIL}")
    print(f"🔍 Паролей для проверки: {len(PASSWORDS)}")
    print("🔄 Использую 2 метода проверки\n")
    
    found = False
    
    for i, password in enumerate(PASSWORDS, 1):
        print(f"[{i:2d}/{len(PASSWORDS)}] {password:25s} ", end="")
        
        # Метод 1: JSON-RPC
        if check_via_jsonrpc(EMAIL, password):
            print("✅ (JSON-RPC)")
            found = password
            break
            
        # Метод 2: Web форма
        if check_via_web(EMAIL, password):
            print("✅ (Web)")
            found = password
            break
            
        print("❌")
        time.sleep(0.3)  # Антибрут защита
    
    if found:
        print("\n" + "="*60)
        print("🎉 ПАРОЛЬ НАЙДЕН! 🎉")
        print("="*60)
        print(f"\n✅ Email: {EMAIL}")
        print(f"✅ Пароль: {found}")
        print(f"\n🌐 Войдите здесь: {ODOO_URL}/web/login")
        
        # Сохраняем найденный пароль
        with open("FOUND_PASSWORD.txt", "w") as f:
            f.write(f"Email: {EMAIL}\n")
            f.write(f"Password: {found}\n")
            f.write(f"URL: {ODOO_URL}\n")
        
        print("\n📄 Пароль сохранен в FOUND_PASSWORD.txt")
    else:
        print("\n❌ Пароль не найден")
        print("\n🔧 Возможные решения:")
        print("1. База создана с другим email")
        print("2. Нужно удалить БД и создать заново")
        print("3. Попробуйте вспомнить пароль, который вводили")

if __name__ == "__main__":
    main()
