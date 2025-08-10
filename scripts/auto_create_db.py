#!/usr/bin/env python3
"""
Автоматическое создание БД Odoo через браузер
Использует AppleScript для управления Chrome
"""

import subprocess
import time
import sys

# Конфигурация
ODOO_URL = "https://odoosportspitproject-production.up.railway.app"
MASTER_PASSWORD = "SportPit2024Master"
DB_NAME = "odoo_sportpit"
ADMIN_EMAIL = "danila@usafitandjoy.com"
ADMIN_PASSWORD = "admin_sportpit_2024"

def run_applescript(script):
    """Выполнить AppleScript"""
    process = subprocess.Popen(['osascript', '-e', script], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    out, err = process.communicate()
    return out.decode('utf-8').strip()

def create_database():
    print("=" * 60)
    print("🚀 АВТОМАТИЧЕСКОЕ СОЗДАНИЕ БД ODOO")
    print("=" * 60)
    
    # Открываем Chrome с нужной страницей
    print("\n🌐 Открываю страницу управления БД...")
    script = f'''
    tell application "Google Chrome"
        activate
        open location "{ODOO_URL}/web/database/manager"
        delay 3
    end tell
    '''
    run_applescript(script)
    time.sleep(3)
    
    # Нажимаем кнопку Create Database
    print("📝 Нажимаю 'Create Database'...")
    script = '''
    tell application "Google Chrome"
        tell active tab of window 1
            execute javascript "document.querySelector('a.btn-primary, button.btn-primary').click();"
        end tell
    end tell
    '''
    run_applescript(script)
    time.sleep(2)
    
    # Заполняем форму
    print("✍️ Заполняю форму...")
    
    js_code = f'''
    // Заполнение формы
    document.querySelector('input[name="master_pwd"]').value = "{MASTER_PASSWORD}";
    document.querySelector('input[name="name"]').value = "{DB_NAME}";
    document.querySelector('input[name="login"]').value = "{ADMIN_EMAIL}";
    document.querySelector('input[name="password"]').value = "{ADMIN_PASSWORD}";
    document.querySelector('input[name="confirm_password"]').value = "{ADMIN_PASSWORD}";
    
    // Выбираем язык
    var langSelect = document.querySelector('select[name="lang"]');
    if (langSelect) {{
        langSelect.value = "ru_RU";
    }}
    
    // Выбираем страну
    var countrySelect = document.querySelector('select[name="country_code"]');
    if (countrySelect) {{
        countrySelect.value = "ru";
    }}
    
    // Снимаем галочку демо-данных
    var demoCheckbox = document.querySelector('input[name="demo"]');
    if (demoCheckbox && demoCheckbox.checked) {{
        demoCheckbox.click();
    }}
    
    "Форма заполнена";
    '''
    
    script = f'''
    tell application "Google Chrome"
        tell active tab of window 1
            execute javascript "{js_code.replace('"', '\\"').replace('\n', ' ')}"
        end tell
    end tell
    '''
    run_applescript(script)
    
    print("✅ Форма заполнена!")
    
    # Отправляем форму
    print("\n⏳ Создаю базу данных (это займет 1-2 минуты)...")
    script = '''
    tell application "Google Chrome"
        tell active tab of window 1
            execute javascript "document.querySelector('button[type=submit]').click();"
        end tell
    end tell
    '''
    run_applescript(script)
    
    print("⏳ Ожидание создания БД...")
    time.sleep(60)
    
    print("\n✅ База данных должна быть создана!")
    print("\n📋 Данные для входа:")
    print(f"  URL: {ODOO_URL}")
    print(f"  Email: {ADMIN_EMAIL}")
    print(f"  Пароль: {ADMIN_PASSWORD}")
    
    # Переходим на страницу входа
    print("\n🔐 Перехожу на страницу входа...")
    script = f'''
    tell application "Google Chrome"
        tell active tab of window 1
            set URL to "{ODOO_URL}/web/login"
        end tell
    end tell
    '''
    run_applescript(script)
    
    time.sleep(3)
    
    # Заполняем форму входа
    print("✍️ Заполняю форму входа...")
    js_login = f'''
    document.getElementById('login').value = "{ADMIN_EMAIL}";
    document.getElementById('password').value = "{ADMIN_PASSWORD}";
    document.querySelector('button[type=submit]').click();
    '''
    
    script = f'''
    tell application "Google Chrome"
        tell active tab of window 1
            execute javascript "{js_login.replace('"', '\\"').replace('\n', ' ')}"
        end tell
    end tell
    '''
    run_applescript(script)
    
    print("\n✅ ГОТОВО!")
    print("=" * 60)
    print("\n📋 Следующие шаги:")
    print("1. Проверьте, что вы вошли в Odoo")
    print("2. Запустите: python3 scripts/install_odoo_modules.py")
    print("3. Запустите: python3 scripts/create_products_and_bom.py")

if __name__ == "__main__":
    create_database()
