#!/usr/bin/env python3
"""
Получение списка всех пользователей в БД через XML-RPC
"""

import xmlrpc.client
import ssl

ODOO_URL = "https://odoosportspitproject-production.up.railway.app"

def get_all_users():
    print("🔍 Получаю список всех пользователей в БД...")
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        # Подключаемся с тестовым пользователем
        common = xmlrpc.client.ServerProxy(
            f'{ODOO_URL}/xmlrpc/2/common',
            context=ssl_context
        )
        
        # Входим как test пользователь (который мы создали)
        uid = common.authenticate('odoo_sportpit', 'test@test.com', 'test123', {})
        
        if uid:
            print("✅ Подключился к БД\n")
            
            models = xmlrpc.client.ServerProxy(
                f'{ODOO_URL}/xmlrpc/2/object',
                context=ssl_context
            )
            
            # Получаем всех пользователей
            users = models.execute_kw(
                'odoo_sportpit', uid, 'test123',
                'res.users', 'search_read',
                [[]],
                {'fields': ['id', 'login', 'name', 'email', 'active']}
            )
            
            print("=" * 60)
            print("📋 ПОЛЬЗОВАТЕЛИ В БАЗЕ ДАННЫХ:")
            print("=" * 60)
            
            admin_found = False
            for user in users:
                is_admin = user['id'] in [1, 2]  # ID 1 и 2 обычно админы
                marker = "👑" if is_admin else "👤"
                
                print(f"\n{marker} ID: {user['id']}")
                print(f"   Login: {user['login']}")
                print(f"   Name: {user['name']}")
                print(f"   Email: {user.get('email', 'Не указан')}")
                print(f"   Активен: {'Да' if user['active'] else 'Нет'}")
                
                if is_admin and user['login']:
                    admin_found = user['login']
            
            print("\n" + "=" * 60)
            
            if admin_found:
                print(f"\n✅ АДМИНСКИЙ ЛОГИН: {admin_found}")
                print(f"\n📝 Используйте его для сброса пароля:")
                print(f"   1. Введите в поле: {admin_found}")
                print(f"   2. Нажмите 'Сбросить пароль'")
            
            return users
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []

if __name__ == "__main__":
    get_all_users()
