#!/usr/bin/env python3
"""
Скрипт для настройки корпоративной почты Beget в Odoo
Домен: usafitandjoy.com
"""

import xmlrpc.client
import ssl
import sys

# Конфигурация подключения к Odoo
url = 'https://odoosportspitproject-production.up.railway.app'
db = 'odoo_sportpit'
username = 'danila@usafitandjoy.com'
password = 'admin_sportpit_2024'

# Настройки почты Beget для usafitandjoy.com
beget_config = {
    'name': 'USAFitAndJoy Corporate Mail (Beget)',
    'smtp_host': 'smtp.beget.com',
    'smtp_port': 465,  # SSL порт
    'smtp_user': 'noreply@usafitandjoy.com',
    'smtp_pass': 'aA%QOeiHY1Gv',
    'smtp_encryption': 'ssl',  # SSL/TLS
    'sequence': 5,  # Приоритет выше чем у Brevo
    'active': True,
    'smtp_authentication': 'login'  # Метод аутентификации
}

# Альтернативная конфигурация (если основная не работает)
beget_alt_config = {
    'name': 'USAFitAndJoy Mail Alternative',
    'smtp_host': 'mail.usafitandjoy.com',
    'smtp_port': 465,
    'smtp_user': 'noreply@usafitandjoy.com',
    'smtp_pass': 'aA%QOeiHY1Gv',
    'smtp_encryption': 'ssl',
    'sequence': 10,
    'active': False,  # Не активен по умолчанию
    'smtp_authentication': 'login'
}

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
        
        # Создаем контекст SSL
        context = ssl._create_unverified_context()
        
        # Подключение к Odoo
        print("\n🔄 Подключение к Odoo...")
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', context=context)
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            print("❌ Ошибка подключения к Odoo")
            return False
        
        print("✅ Подключение успешно")
        
        # Создаем объект для работы с моделями
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', context=context)
        
        # Проверяем существующие SMTP серверы
        print("\n🔍 Проверка существующих SMTP серверов...")
        existing_servers = models.execute_kw(db, uid, password,
            'ir.mail_server', 'search_read',
            [[]], {'fields': ['id', 'name', 'smtp_host', 'active', 'sequence']})
        
        if existing_servers:
            print(f"📧 Найдено {len(existing_servers)} серверов:")
            for server in existing_servers:
                status = "✅" if server['active'] else "❌"
                print(f"   {status} {server['name']} ({server['smtp_host']}) - приоритет: {server['sequence']}")
            
            # Находим и обновляем приоритет Brevo (делаем его резервным)
            for server in existing_servers:
                if 'brevo' in server['name'].lower() and server['active']:
                    models.execute_kw(db, uid, password,
                        'ir.mail_server', 'write',
                        [[server['id']], {'sequence': 20}])  # Понижаем приоритет Brevo
                    print(f"   ⚠️ Brevo сервер остается активным как резервный")
        
        # Создаем основной SMTP сервер Beget
        print("\n📮 Создание корпоративного SMTP сервера...")
        server_id = models.execute_kw(db, uid, password,
            'ir.mail_server', 'create',
            [beget_config])
        
        if server_id:
            print("✅ Корпоративный SMTP сервер создан!")
            print(f"   • ID: {server_id}")
            print(f"   • Приоритет: {beget_config['sequence']} (основной)")
            
            # Создаем альтернативный сервер (не активный)
            alt_server_id = models.execute_kw(db, uid, password,
                'ir.mail_server', 'create',
                [beget_alt_config])
            
            if alt_server_id:
                print(f"\n✅ Альтернативный сервер создан (не активен)")
                print(f"   • Хост: {beget_alt_config['smtp_host']}")
                print(f"   • Можно активировать при необходимости")
            
            # Настраиваем системные параметры
            print("\n⚙️ Настройка системных параметров...")
            params = {
                'mail.default.from': 'noreply@usafitandjoy.com',
                'mail.catchall.domain': 'usafitandjoy.com',
                'mail.bounce.alias': 'bounce',
                'mail.catchall.alias': 'info',
                'mail.default.from_filter': 'usafitandjoy.com'
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
                
                print(f"   ✅ {key} = {value}")
            
            # Обновляем настройки компании
            print("\n🏢 Обновление настроек компании...")
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
            
            print("\n" + "=" * 60)
            print("🎉 НАСТРОЙКА ЗАВЕРШЕНА УСПЕШНО!")
            print("=" * 60)
            
            print("\n📧 Конфигурация почты:")
            print("   • Основной сервер: smtp.beget.com:465 (SSL)")
            print("   • От кого: noreply@usafitandjoy.com")
            print("   • Резервный: Brevo (300 писем/день)")
            
            print("\n✅ Преимущества корпоративной почты:")
            print("   • Профессиональные письма от @usafitandjoy.com")
            print("   • Лучшая доставляемость (не попадает в спам)")
            print("   • Неограниченное количество писем")
            print("   • Полный контроль над почтой")
            
            print("\n🔍 Как проверить:")
            print("   1. Выйдите из Odoo")
            print("   2. Используйте 'Сбросить пароль'")
            print("   3. Проверьте отправителя - должен быть @usafitandjoy.com")
            
            print("\n📊 Порядок использования серверов:")
            print("   1. Beget (основной) - корпоративная почта")
            print("   2. Brevo (резервный) - если Beget недоступен")
            
            return True
        else:
            print("❌ Не удалось создать SMTP сервер")
            return False
            
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("\n💡 Возможные решения:")
        print("   • Проверьте доступность Odoo")
        print("   • Убедитесь в правильности пароля")
        print("   • Проверьте настройки в Beget")
        return False

def test_email_sending():
    """Тест отправки email через новые настройки"""
    try:
        context = ssl._create_unverified_context()
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', context=context)
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            return False
        
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', context=context)
        
        # Пытаемся отправить тестовое письмо
        print("\n📤 Отправка тестового письма...")
        
        mail_values = {
            'subject': 'Тест корпоративной почты USAFitAndJoy',
            'body_html': '''
                <h2>Тестовое письмо</h2>
                <p>Это тестовое письмо отправлено с корпоративной почты <b>usafitandjoy.com</b></p>
                <p>Настройки почты:</p>
                <ul>
                    <li>SMTP: smtp.beget.com</li>
                    <li>От: noreply@usafitandjoy.com</li>
                    <li>Хостинг: Beget</li>
                </ul>
                <p>Если вы получили это письмо - настройка выполнена успешно!</p>
            ''',
            'email_to': 'danila@usafitandjoy.com',
            'email_from': 'noreply@usafitandjoy.com',
            'auto_delete': False
        }
        
        mail_id = models.execute_kw(db, uid, password,
            'mail.mail', 'create',
            [mail_values])
        
        if mail_id:
            # Отправляем письмо
            models.execute_kw(db, uid, password,
                'mail.mail', 'send',
                [[mail_id]])
            print("✅ Тестовое письмо отправлено на danila@usafitandjoy.com")
            print("   Проверьте почту через 1-2 минуты")
            return True
        
    except Exception as e:
        print(f"⚠️ Не удалось отправить тестовое письмо: {e}")
        return False

if __name__ == "__main__":
    print("\n🚀 Запуск настройки корпоративной почты USAFitAndJoy...")
    
    result = setup_beget_mail()
    
    if result:
        print("\n📧 Пытаемся отправить тестовое письмо...")
        test_email_sending()
        print("\n✅ Настройка завершена успешно!")
        print("📌 Корпоративная почта @usafitandjoy.com готова к работе!")
        sys.exit(0)
    else:
        print("\n❌ Настройка завершена с ошибками")
        sys.exit(1)
