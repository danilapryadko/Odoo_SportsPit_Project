#!/usr/bin/env python3
"""
Создание/обновление администратора с email danila@usafitandjoy.com
"""

import xmlrpc.client
import ssl

ODOO_URL = "https://odoosportspitproject-production.up.railway.app"
ADMIN_EMAIL = "danila@usafitandjoy.com"
ADMIN_PASSWORD = "admin123"  # Временный пароль

def create_or_update_admin():
    print("=" * 60)
    print("🔧 СОЗДАНИЕ АДМИНИСТРАТОРА")
    print("=" * 60)
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        common = xmlrpc.client.ServerProxy(
            f'{ODOO_URL}/xmlrpc/2/common',
            context=ssl_context
        )
        
        # Входим как test пользователь
        uid = common.authenticate('odoo_sportpit', 'test@test.com', 'test123', {})
        
        if not uid:
            print("❌ Не могу войти как test пользователь")
            
            # Пробуем войти с master password как admin
            for pwd in ['admin', 'SportPit2024Master', 'admin_sportpit_2024']:
                uid = common.authenticate('odoo_sportpit', 'admin', pwd, {})
                if uid:
                    print(f"✅ Вошел как admin с паролем: {pwd}")
                    break
        else:
            print("✅ Вошел как test@test.com")
        
        if uid:
            models = xmlrpc.client.ServerProxy(
                f'{ODOO_URL}/xmlrpc/2/object',
                context=ssl_context
            )
            
            # Проверяем, есть ли пользователь с таким email
            existing = models.execute_kw(
                'odoo_sportpit', uid, 'test123',
                'res.users', 'search',
                [[('login', '=', ADMIN_EMAIL)]]
            )
            
            if existing:
                print(f"\n📝 Обновляю существующего пользователя...")
                # Обновляем пароль и права
                models.execute_kw(
                    'odoo_sportpit', uid, 'test123',
                    'res.users', 'write',
                    [existing, {
                        'password': ADMIN_PASSWORD,
                        'email': ADMIN_EMAIL,
                        'active': True
                    }]
                )
                print(f"✅ Пользователь обновлен!")
            else:
                print(f"\n➕ Создаю нового администратора...")
                
                # Получаем группу администраторов
                admin_group = models.execute_kw(
                    'odoo_sportpit', uid, 'test123',
                    'res.groups', 'search',
                    [[('name', '=', 'Settings')]]
                )
                
                # Создаем нового пользователя
                new_user = models.execute_kw(
                    'odoo_sportpit', uid, 'test123',
                    'res.users', 'create',
                    [{
                        'name': 'Danila Administrator',
                        'login': ADMIN_EMAIL,
                        'email': ADMIN_EMAIL,
                        'password': ADMIN_PASSWORD,
                        'active': True,
                        'groups_id': [(6, 0, admin_group)] if admin_group else []
                    }]
                )
                
                if new_user:
                    print(f"✅ Администратор создан! ID: {new_user}")
                    
                    # Даем права администратора
                    try:
                        # Получаем все административные группы
                        admin_groups = models.execute_kw(
                            'odoo_sportpit', uid, 'test123',
                            'res.groups', 'search',
                            [[('category_id.name', 'in', ['Administration', 'Technical', 'Settings'])]]
                        )
                        
                        if admin_groups:
                            models.execute_kw(
                                'odoo_sportpit', uid, 'test123',
                                'res.users', 'write',
                                [[new_user], {
                                    'groups_id': [(6, 0, admin_groups)]
                                }]
                            )
                            print("✅ Административные права назначены!")
                    except:
                        print("⚠️ Базовые права назначены")
            
            print("\n" + "=" * 60)
            print("✅ ГОТОВО!")
            print("=" * 60)
            print(f"\n📧 Email: {ADMIN_EMAIL}")
            print(f"🔑 Пароль: {ADMIN_PASSWORD}")
            print(f"\n🌐 Войдите: {ODOO_URL}/web/login")
            
            print("\n📝 Теперь можно:")
            print("1. Войти с этими данными")
            print("2. Или сбросить пароль через форму сброса")
            
            return True
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        
        # Если не получается, пробуем создать через admin
        print("\n🔄 Пробую альтернативный способ...")
        
        try:
            # Список возможных паролей для admin
            admin_passwords = ['admin', 'SportPit2024Master', 'admin_sportpit_2024']
            
            for admin_pwd in admin_passwords:
                uid = common.authenticate('odoo_sportpit', 'admin', admin_pwd, {})
                if uid:
                    print(f"✅ Вошел как admin/{admin_pwd}")
                    
                    models = xmlrpc.client.ServerProxy(
                        f'{ODOO_URL}/xmlrpc/2/object',
                        context=ssl_context
                    )
                    
                    # Обновляем админа
                    models.execute_kw(
                        'odoo_sportpit', uid, admin_pwd,
                        'res.users', 'write',
                        [[uid], {
                            'login': ADMIN_EMAIL,
                            'email': ADMIN_EMAIL,
                            'password': ADMIN_PASSWORD
                        }]
                    )
                    
                    print(f"\n✅ Администратор обновлен!")
                    print(f"📧 Email: {ADMIN_EMAIL}")
                    print(f"🔑 Пароль: {ADMIN_PASSWORD}")
                    return True
                    
        except Exception as e2:
            print(f"❌ Альтернативный способ тоже не сработал: {e2}")
        
        return False

if __name__ == "__main__":
    create_or_update_admin()
