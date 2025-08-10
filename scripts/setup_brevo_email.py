#!/usr/bin/env python3
"""
Скрипт для быстрой настройки SMTP через Brevo (бесплатный сервис)
Brevo предоставляет 300 бесплатных писем в день
"""

import xmlrpc.client
import ssl
import sys

# Конфигурация подключения к Odoo
url = 'https://odoosportspitproject-production.up.railway.app'
db = 'odoo_sportpit'
username = 'danila@usafitandjoy.com'
password = 'admin_sportpit_2024'

def setup_brevo_smtp():
    """
    Настройка Brevo SMTP
    
    Для получения SMTP ключа:
    1. Зарегистрируйтесь на https://www.brevo.com (бесплатно)
    2. Перейдите в Settings -> SMTP & API
    3. Создайте SMTP ключ
    4. Используйте его в этом скрипте
    """
    
    print("=" * 60)
    print("НАСТРОЙКА BREVO SMTP (БЕСПЛАТНО)")
    print("=" * 60)
    print("\n📧 Brevo предоставляет:")
    print("  • 300 бесплатных писем в день")
    print("  • Надежная доставка")
    print("  • Статистика отправок")
    print("\n🔗 Регистрация: https://www.brevo.com")
    print("\nПосле регистрации:")
    print("1. Перейдите в Settings -> SMTP & API")
    print("2. Создайте SMTP ключ")
    print("3. Введите его ниже\n")
    
    smtp_login = input("Введите ваш email в Brevo: ")
    smtp_password = input("Введите SMTP ключ из Brevo: ")
    
    if not smtp_login or not smtp_password:
        print("❌ Email и SMTP ключ обязательны!")
        return False
    
    # Конфигурация Brevo SMTP
    brevo_config = {
        'name': 'Brevo SMTP Server',
        'smtp_host': 'smtp-relay.brevo.com',
        'smtp_port': 587,
        'smtp_user': smtp_login,
        'smtp_pass': smtp_password,
        'smtp_encryption': 'starttls',
        'sequence': 10,
        'active': True
    }
    
    try:
        # Создаем контекст SSL
        context = ssl._create_unverified_context()
        
        # Подключение к Odoo
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', context=context)
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            print("❌ Ошибка подключения к Odoo")
            return False
        
        print("✅ Подключение к Odoo успешно")
        
        # Создаем объект для работы с моделями
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', context=context)
        
        # Деактивируем существующие SMTP серверы
        existing_servers = models.execute_kw(db, uid, password,
            'ir.mail_server', 'search',
            [[]])
        
        if existing_servers:
            models.execute_kw(db, uid, password,
                'ir.mail_server', 'write',
                [existing_servers, {'active': False}])
            print("⚠️ Существующие SMTP серверы деактивированы")
        
        # Создаем новый SMTP сервер
        server_id = models.execute_kw(db, uid, password,
            'ir.mail_server', 'create',
            [brevo_config])
        
        if server_id:
            print(f"\n✅ Brevo SMTP сервер создан!")
            
            # Настраиваем параметры системы
            params = {
                'mail.default.from': f'noreply@{smtp_login.split("@")[1]}',
                'mail.catchall.domain': smtp_login.split("@")[1],
                'mail.bounce.alias': 'bounce',
                'mail.catchall.alias': 'catchall'
            }
            
            for key, value in params.items():
                param_ids = models.execute_kw(db, uid, password,
                    'ir.config_parameter', 'search',
                    [[['key', '=', key]]])
                
                if param_ids:
                    models.execute_kw(db, uid, password,
                        'ir.config_parameter', 'write',
                        [param_ids, {'value': value}])
                else:
                    models.execute_kw(db, uid, password,
                        'ir.config_parameter', 'create',
                        [{'key': key, 'value': value}])
            
            print("\n✅ Параметры email настроены")
            print("\n🎉 НАСТРОЙКА ЗАВЕРШЕНА!")
            print("\nТеперь функция сброса пароля будет работать!")
            print("Также вы сможете:")
            print("  • Отправлять счета по email")
            print("  • Получать уведомления")
            print("  • Использовать email маркетинг")
            
            return True
        else:
            print("❌ Не удалось создать SMTP сервер")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    setup_brevo_smtp()
