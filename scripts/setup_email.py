#!/usr/bin/env python3
"""
Скрипт для настройки SMTP сервера в Odoo
Использует Gmail SMTP для надежной доставки писем
"""

import xmlrpc.client
import ssl
import sys

# Конфигурация подключения к Odoo
url = 'https://odoosportspitproject-production.up.railway.app'
db = 'odoo_sportpit'
username = 'danila@usafitandjoy.com'
password = 'admin_sportpit_2024'

# ВАЖНО: Для использования Gmail SMTP нужно:
# 1. Включить двухфакторную аутентификацию в Google аккаунте
# 2. Создать пароль приложения: https://myaccount.google.com/apppasswords
# 3. Использовать этот пароль вместо обычного пароля Gmail

# Настройки SMTP (пример для Gmail)
smtp_config = {
    'name': 'Gmail SMTP Server',
    'smtp_host': 'smtp.gmail.com',
    'smtp_port': 587,
    'smtp_user': 'your_email@gmail.com',  # ЗАМЕНИТЕ на ваш Gmail
    'smtp_pass': 'your_app_password',     # ЗАМЕНИТЕ на пароль приложения Google
    'smtp_encryption': 'starttls',
    'sequence': 10,
    'active': True
}

# Альтернативные настройки для разных провайдеров:

# Yandex
yandex_config = {
    'name': 'Yandex SMTP Server',
    'smtp_host': 'smtp.yandex.ru',
    'smtp_port': 587,
    'smtp_user': 'your_email@yandex.ru',  # ЗАМЕНИТЕ
    'smtp_pass': 'your_password',         # ЗАМЕНИТЕ
    'smtp_encryption': 'starttls',
    'sequence': 10,
    'active': True
}

# Mail.ru
mailru_config = {
    'name': 'Mail.ru SMTP Server', 
    'smtp_host': 'smtp.mail.ru',
    'smtp_port': 465,
    'smtp_user': 'your_email@mail.ru',    # ЗАМЕНИТЕ
    'smtp_pass': 'your_password',         # ЗАМЕНИТЕ
    'smtp_encryption': 'ssl',
    'sequence': 10,
    'active': True
}

# SendGrid (рекомендуется для production)
sendgrid_config = {
    'name': 'SendGrid SMTP Server',
    'smtp_host': 'smtp.sendgrid.net',
    'smtp_port': 587,
    'smtp_user': 'apikey',                # Всегда 'apikey' для SendGrid
    'smtp_pass': 'your_sendgrid_api_key', # ЗАМЕНИТЕ на API ключ SendGrid
    'smtp_encryption': 'starttls',
    'sequence': 10,
    'active': True
}

def setup_smtp(config_to_use):
    """Настройка SMTP сервера в Odoo"""
    try:
        # Создаем контекст SSL
        context = ssl._create_unverified_context()
        
        # Подключение к Odoo
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', context=context)
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            print("❌ Ошибка аутентификации")
            return False
        
        print(f"✅ Успешная аутентификация. UID: {uid}")
        
        # Создаем объект для работы с моделями
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', context=context)
        
        # Проверяем существующие SMTP серверы
        existing_servers = models.execute_kw(db, uid, password,
            'ir.mail_server', 'search_read',
            [[]], {'fields': ['name', 'smtp_host', 'active']})
        
        if existing_servers:
            print("\n📧 Существующие SMTP серверы:")
            for server in existing_servers:
                status = "✅ Активен" if server['active'] else "❌ Неактивен"
                print(f"  - {server['name']} ({server['smtp_host']}) {status}")
            
            # Деактивируем старые серверы
            for server in existing_servers:
                models.execute_kw(db, uid, password,
                    'ir.mail_server', 'write',
                    [[server['id']], {'active': False}])
            print("  ⚠️ Старые серверы деактивированы")
        
        # Создаем новый SMTP сервер
        server_id = models.execute_kw(db, uid, password,
            'ir.mail_server', 'create',
            [config_to_use])
        
        if server_id:
            print(f"\n✅ SMTP сервер создан успешно!")
            print(f"   - Название: {config_to_use['name']}")
            print(f"   - Хост: {config_to_use['smtp_host']}")
            print(f"   - Порт: {config_to_use['smtp_port']}")
            print(f"   - Шифрование: {config_to_use['smtp_encryption']}")
            
            # Тестируем подключение
            print("\n🔍 Тестирование подключения...")
            try:
                test_result = models.execute_kw(db, uid, password,
                    'ir.mail_server', 'test_smtp_connection',
                    [server_id])
                print("✅ Тест подключения успешен!")
            except Exception as e:
                print(f"⚠️ Тест подключения не удался: {e}")
                print("   Проверьте логин/пароль и настройки безопасности вашего email провайдера")
            
            return True
        else:
            print("❌ Не удалось создать SMTP сервер")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def setup_email_templates():
    """Настройка email шаблонов для сброса пароля"""
    try:
        context = ssl._create_unverified_context()
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', context=context)
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            return False
        
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', context=context)
        
        # Настраиваем параметры системы для email
        params_to_set = {
            'mail.catchall.domain': 'usafitandjoy.com',  # Ваш домен
            'mail.default.from': 'noreply@usafitandjoy.com',  # Email отправителя
            'mail.bounce.alias': 'bounce',
            'mail.catchall.alias': 'catchall'
        }
        
        for key, value in params_to_set.items():
            # Ищем существующий параметр
            param_ids = models.execute_kw(db, uid, password,
                'ir.config_parameter', 'search',
                [[['key', '=', key]]])
            
            if param_ids:
                # Обновляем существующий
                models.execute_kw(db, uid, password,
                    'ir.config_parameter', 'write',
                    [param_ids, {'value': value}])
            else:
                # Создаем новый
                models.execute_kw(db, uid, password,
                    'ir.config_parameter', 'create',
                    [{'key': key, 'value': value}])
            
            print(f"✅ Параметр {key} = {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка настройки шаблонов: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("НАСТРОЙКА EMAIL В ODOO")
    print("=" * 60)
    
    print("\n⚠️ ВАЖНО: Перед запуском скрипта:")
    print("1. Замените email и пароль в конфигурации выше")
    print("2. Для Gmail: создайте пароль приложения")
    print("3. Для Yandex/Mail.ru: используйте обычный пароль")
    print("4. Для SendGrid: получите API ключ\n")
    
    print("Выберите провайдера email:")
    print("1. Gmail (рекомендуется)")
    print("2. Yandex")
    print("3. Mail.ru")
    print("4. SendGrid (для production)")
    print("5. Пропустить настройку")
    
    choice = input("\nВаш выбор (1-5): ")
    
    config = None
    if choice == '1':
        config = smtp_config
    elif choice == '2':
        config = yandex_config
    elif choice == '3':
        config = mailru_config
    elif choice == '4':
        config = sendgrid_config
    elif choice == '5':
        print("Настройка пропущена")
        sys.exit(0)
    else:
        print("Неверный выбор")
        sys.exit(1)
    
    # Запрашиваем данные у пользователя
    print(f"\nНастройка {config['name']}")
    config['smtp_user'] = input(f"Введите email ({config['smtp_user']}): ") or config['smtp_user']
    config['smtp_pass'] = input(f"Введите пароль/API ключ: ") or config['smtp_pass']
    
    if setup_smtp(config):
        print("\n📧 Настройка email шаблонов...")
        setup_email_templates()
        print("\n✅ Настройка завершена успешно!")
        print("\nТеперь вы можете:")
        print("1. Использовать функцию сброса пароля")
        print("2. Отправлять счета и документы по email")
        print("3. Получать уведомления системы")
    else:
        print("\n❌ Настройка не удалась")
        print("Проверьте данные и попробуйте снова")
