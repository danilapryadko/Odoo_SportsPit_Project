#!/usr/bin/env python3
"""
Скрипт для настройки Brevo SMTP в Odoo с вашими данными
"""

import xmlrpc.client
import ssl
import sys

# Конфигурация подключения к Odoo
url = 'https://odoosportspitproject-production.up.railway.app'
db = 'odoo_sportpit'
username = 'danila@usafitandjoy.com'
password = 'admin_sportpit_2024'

# Ваши настройки Brevo SMTP
brevo_config = {
    'name': 'Brevo SMTP Server',
    'smtp_host': 'smtp-relay.brevo.com',
    'smtp_port': 587,
    'smtp_user': '9462a2001@smtp-brevo.com',
    'smtp_pass': 'G0MAdWJHScU8DQBv',
    'smtp_encryption': 'starttls',
    'sequence': 10,
    'active': True
}

def setup_brevo():
    """Настройка Brevo SMTP в Odoo"""
    try:
        print("=" * 60)
        print("НАСТРОЙКА BREVO SMTP В ODOO")
        print("=" * 60)
        
        # Создаем контекст SSL
        context = ssl._create_unverified_context()
        
        # Подключение к Odoo
        print("\n🔄 Подключение к Odoo...")
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', context=context)
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            print("❌ Ошибка подключения к Odoo. Проверьте доступность сервера.")
            return False
        
        print("✅ Подключение к Odoo успешно установлено")
        
        # Создаем объект для работы с моделями
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', context=context)
        
        # Проверяем и деактивируем существующие SMTP серверы
        print("\n🔍 Проверка существующих SMTP серверов...")
        existing_servers = models.execute_kw(db, uid, password,
            'ir.mail_server', 'search_read',
            [[]], {'fields': ['id', 'name', 'smtp_host', 'active']})
        
        if existing_servers:
            print(f"📧 Найдено {len(existing_servers)} существующих серверов:")
            for server in existing_servers:
                status = "✅" if server['active'] else "❌"
                print(f"   {status} {server['name']} ({server['smtp_host']})")
            
            # Деактивируем все существующие серверы
            for server in existing_servers:
                if server['active']:
                    models.execute_kw(db, uid, password,
                        'ir.mail_server', 'write',
                        [[server['id']], {'active': False}])
            print("   ⚠️ Все старые серверы деактивированы")
        
        # Создаем новый SMTP сервер Brevo
        print("\n📮 Создание нового Brevo SMTP сервера...")
        server_id = models.execute_kw(db, uid, password,
            'ir.mail_server', 'create',
            [brevo_config])
        
        if server_id:
            print("✅ Brevo SMTP сервер успешно создан!")
            print(f"   • ID сервера: {server_id}")
            print(f"   • Хост: {brevo_config['smtp_host']}")
            print(f"   • Порт: {brevo_config['smtp_port']}")
            print(f"   • Логин: {brevo_config['smtp_user']}")
            
            # Настраиваем системные параметры для email
            print("\n⚙️ Настройка системных параметров email...")
            params = {
                'mail.default.from': 'noreply@usafitandjoy.com',
                'mail.catchall.domain': 'usafitandjoy.com',
                'mail.bounce.alias': 'bounce',
                'mail.catchall.alias': 'catchall'
            }
            
            for key, value in params.items():
                # Ищем существующий параметр
                param_ids = models.execute_kw(db, uid, password,
                    'ir.config_parameter', 'search',
                    [[['key', '=', key]]])
                
                if param_ids:
                    # Обновляем существующий параметр
                    models.execute_kw(db, uid, password,
                        'ir.config_parameter', 'write',
                        [param_ids, {'value': value}])
                else:
                    # Создаем новый параметр
                    models.execute_kw(db, uid, password,
                        'ir.config_parameter', 'create',
                        [{'key': key, 'value': value}])
                
                print(f"   ✅ {key} = {value}")
            
            print("\n" + "=" * 60)
            print("🎉 НАСТРОЙКА ЗАВЕРШЕНА УСПЕШНО!")
            print("=" * 60)
            print("\n✅ Что теперь работает:")
            print("   • Сброс пароля через email")
            print("   • Отправка счетов и документов")
            print("   • Email уведомления системы")
            print("   • Приглашения пользователей")
            print("\n📊 Лимиты Brevo:")
            print("   • 300 писем в день (бесплатно)")
            print("   • Высокая доставляемость")
            print("   • Статистика в личном кабинете Brevo")
            print("\n🔍 Как проверить:")
            print("   1. Выйдите из Odoo")
            print("   2. На странице входа нажмите 'Сбросить пароль'")
            print("   3. Введите email: danila@usafitandjoy.com")
            print("   4. Проверьте почту (включая папку Спам)")
            
            return True
        else:
            print("❌ Не удалось создать SMTP сервер")
            return False
            
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        print("\n💡 Возможные причины:")
        print("   • Odoo сервер недоступен")
        print("   • Неверные учетные данные")
        print("   • Проблемы с сетью")
        return False

if __name__ == "__main__":
    print("\n🚀 Запуск настройки Brevo SMTP для Odoo SportsPit...")
    print("   Сервер: https://odoosportspitproject-production.up.railway.app")
    print("   База данных: odoo_sportpit")
    
    result = setup_brevo()
    
    if result:
        print("\n✅ Скрипт выполнен успешно!")
        sys.exit(0)
    else:
        print("\n❌ Скрипт завершен с ошибкой")
        print("📞 Обратитесь за помощью если проблема повторяется")
        sys.exit(1)
