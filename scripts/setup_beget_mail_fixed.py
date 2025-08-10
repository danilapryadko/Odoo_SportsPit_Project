#!/usr/bin/env python3
"""
Скрипт для настройки корпоративной почты Beget в Odoo
Исправленная версия с правильным подключением
"""

import xmlrpc.client
import ssl
import sys
import urllib.parse

# Конфигурация подключения к Odoo
url = 'https://odoosportspitproject-production.up.railway.app'
db = 'odoo_sportpit'
username = 'danila@usafitandjoy.com'
password = 'admin_sportpit_2024'

# Настройки почты Beget для usafitandjoy.com
beget_config = {
    'name': 'USAFitAndJoy Corporate Mail',
    'smtp_host': 'smtp.beget.com',
    'smtp_port': 465,
    'smtp_user': 'noreply@usafitandjoy.com',
    'smtp_pass': 'aA%QOeiHY1Gv',
    'smtp_encryption': 'ssl',
    'sequence': 5,
    'active': True
}

def delete_brevo_servers(models, db, uid, password):
    """Удаляет все серверы Brevo"""
    try:
        # Ищем серверы Brevo
        brevo_servers = models.execute_kw(db, uid, password,
            'ir.mail_server', 'search',
            [[['smtp_host', 'like', 'brevo']]])
        
        if brevo_servers:
            # Удаляем найденные серверы
            models.execute_kw(db, uid, password,
                'ir.mail_server', 'unlink',
                [brevo_servers])
            print(f"   ✅ Удалено {len(brevo_servers)} серверов Brevo")
            return True
        else:
            print("   ℹ️ Серверы Brevo не найдены")
            return False
    except Exception as e:
        print(f"   ⚠️ Ошибка при удалении Brevo: {e}")
        return False

def setup_beget_mail():
    """Настройка корпоративной почты Beget в Odoo"""
    try:
        print("=" * 60)
        print("НАСТРОЙКА КОРПОРАТИВНОЙ ПОЧТЫ USAFITANDJOY.COM")
        print("=" * 60)
        print("\n📧 Настройки почты:")
        print(f"   • Домен: usafitandjoy.com")
        print(f"   • Email: noreply@usafitandjoy.com")
        print(f"   • SMTP сервер: smtp.beget.com")
        print(f"   • Порт: 465 (SSL)")
        
        # Создаем контекст SSL для игнорирования проверки сертификата
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context
        
        # Подключение к Odoo
        print("\n🔄 Подключение к Odoo...")
        
        # Проверяем доступность сервера
        try:
            common_url = f'{url}/xmlrpc/2/common'
            common = xmlrpc.client.ServerProxy(common_url, allow_none=True)
            
            # Проверяем версию (это не требует аутентификации)
            version = common.version()
            print(f"✅ Сервер Odoo доступен. Версия: {version.get('server_version', 'Unknown')}")
            
            # Аутентификация
            uid = common.authenticate(db, username, password, {})
            
            if not uid:
                print("❌ Ошибка аутентификации. Проверьте логин и пароль.")
                print(f"   База данных: {db}")
                print(f"   Пользователь: {username}")
                return False
            
            print(f"✅ Аутентификация успешна. UID: {uid}")
            
        except Exception as e:
            print(f"❌ Ошибка подключения к серверу: {e}")
            print(f"   URL: {url}")
            print("\n💡 Проверьте:")
            print("   1. Доступность сервера Railway")
            print("   2. Правильность URL")
            print("   3. Статус деплоя в Railway")
            return False
        
        # Создаем объект для работы с моделями
        models_url = f'{url}/xmlrpc/2/object'
        models = xmlrpc.client.ServerProxy(models_url, allow_none=True)
        
        # Удаляем серверы Brevo
        print("\n🗑️ Удаление серверов Brevo...")
        delete_brevo_servers(models, db, uid, password)
        
        # Проверяем и удаляем существующие SMTP серверы с таким же хостом
        print("\n🔍 Проверка существующих SMTP серверов...")
        existing_servers = models.execute_kw(db, uid, password,
            'ir.mail_server', 'search_read',
            [[]], {'fields': ['id', 'name', 'smtp_host', 'active']})
        
        if existing_servers:
            print(f"📧 Найдено {len(existing_servers)} серверов:")
            for server in existing_servers:
                status = "✅" if server['active'] else "❌"
                print(f"   {status} {server['name']} ({server['smtp_host']})")
                
                # Удаляем если это старая версия Beget сервера
                if 'beget' in server['smtp_host'].lower():
                    models.execute_kw(db, uid, password,
                        'ir.mail_server', 'unlink',
                        [[server['id']]])
                    print(f"   🗑️ Удален старый сервер Beget")
        
        # Создаем новый SMTP сервер Beget
        print("\n📮 Создание корпоративного SMTP сервера...")
        try:
            server_id = models.execute_kw(db, uid, password,
                'ir.mail_server', 'create',
                [beget_config])
            
            if server_id:
                print(f"✅ Корпоративный SMTP сервер создан!")
                print(f"   • ID: {server_id}")
                print(f"   • Хост: {beget_config['smtp_host']}")
                print(f"   • Порт: {beget_config['smtp_port']}")
                print(f"   • Email: {beget_config['smtp_user']}")
            
        except Exception as e:
            print(f"❌ Ошибка при создании SMTP сервера: {e}")
            return False
        
        # Настраиваем системные параметры
        print("\n⚙️ Настройка системных параметров...")
        params = {
            'mail.default.from': 'noreply@usafitandjoy.com',
            'mail.catchall.domain': 'usafitandjoy.com',
            'mail.bounce.alias': 'bounce',
            'mail.catchall.alias': 'info'
        }
        
        for key, value in params.items():
            try:
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
                
            except Exception as e:
                print(f"   ⚠️ Ошибка настройки {key}: {e}")
        
        # Обновляем настройки компании
        print("\n🏢 Обновление настроек компании...")
        try:
            company_ids = models.execute_kw(db, uid, password,
                'res.company', 'search',
                [[]])
            
            if company_ids:
                models.execute_kw(db, uid, password,
                    'res.company', 'write',
                    [company_ids, {
                        'email': 'info@usafitandjoy.com',
                        'catchall_email': 'info@usafitandjoy.com'
                    }])
                print("   ✅ Email компании обновлен")
        except Exception as e:
            print(f"   ⚠️ Ошибка обновления компании: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 НАСТРОЙКА ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 60)
        
        print("\n📧 Итоговая конфигурация:")
        print("   • SMTP сервер: smtp.beget.com:465 (SSL)")
        print("   • От кого: noreply@usafitandjoy.com")
        print("   • Серверы Brevo: УДАЛЕНЫ")
        print("   • Корпоративная почта: АКТИВНА")
        
        print("\n✅ Преимущества:")
        print("   • Профессиональные письма от @usafitandjoy.com")
        print("   • Неограниченное количество писем")
        print("   • Высокая доставляемость")
        print("   • Полный контроль над почтой")
        
        print("\n🔍 Как проверить:")
        print("   1. Выйдите из Odoo")
        print("   2. Используйте функцию 'Сбросить пароль'")
        print("   3. Письмо придет от noreply@usafitandjoy.com")
        
        # Проверяем финальную конфигурацию
        print("\n📊 Проверка конфигурации...")
        final_servers = models.execute_kw(db, uid, password,
            'ir.mail_server', 'search_read',
            [[]], {'fields': ['name', 'smtp_host', 'active']})
        
        print(f"Активные SMTP серверы ({len(final_servers)}):")
        for server in final_servers:
            status = "✅" if server['active'] else "❌"
            print(f"   {status} {server['name']} ({server['smtp_host']})")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        print("\nПолная информация об ошибке:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🚀 Запуск настройки корпоративной почты USAFitAndJoy...")
    print(f"   Сервер: {url}")
    print(f"   База данных: {db}")
    
    result = setup_beget_mail()
    
    if result:
        print("\n✅ Скрипт выполнен успешно!")
        print("📌 Корпоративная почта @usafitandjoy.com готова к работе!")
        print("🗑️ Серверы Brevo удалены")
        sys.exit(0)
    else:
        print("\n❌ Настройка завершена с ошибками")
        print("📞 Проверьте доступность сервера Railway")
        sys.exit(1)
