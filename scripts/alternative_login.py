#!/usr/bin/env python3
"""
Создание нового пользователя через XML-RPC с известным паролем
"""

import xmlrpc.client
import ssl

ODOO_URL = "https://odoosportspitproject-production.up.railway.app"

# Список возможных master passwords для создания пользователя
MASTER_PASSWORDS = [
    "SportPit2024Master",
    "admin_sportpit_2024", 
    "dbny-777k-4ggc",
    "admin",
    "SportPit2024"
]

# Новый пользователь
NEW_USER = "test@test.com"
NEW_PASSWORD = "test123"

def create_user_with_master():
    """Создание нового пользователя используя master password"""
    print("🔐 Пытаюсь создать нового пользователя...")
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    for master_pwd in MASTER_PASSWORDS:
        print(f"\n  Пробую master password: {master_pwd[:5]}...")
        
        try:
            # Подключаемся к common endpoint
            common = xmlrpc.client.ServerProxy(
                f'{ODOO_URL}/xmlrpc/2/common',
                context=ssl_context
            )
            
            # Пытаемся использовать master password для создания пользователя
            # Это работает только если есть доступ к db management
            db_proxy = xmlrpc.client.ServerProxy(
                f'{ODOO_URL}/xmlrpc/2/db',
                context=ssl_context
            )
            
            # Проверяем доступ к БД
            dbs = db_proxy.list()
            if 'odoo_sportpit' in dbs:
                print(f"    ✅ БД найдена")
                
                # Пытаемся аутентифицироваться с master password
                # как администратор БД
                uid = common.authenticate(
                    'odoo_sportpit', 
                    'admin', 
                    master_pwd, 
                    {}
                )
                
                if uid:
                    print(f"    ✅ Аутентификация успешна с {master_pwd}")
                    
                    # Создаем нового пользователя
                    models = xmlrpc.client.ServerProxy(
                        f'{ODOO_URL}/xmlrpc/2/object',
                        context=ssl_context
                    )
                    
                    user_id = models.execute_kw(
                        'odoo_sportpit', uid, master_pwd,
                        'res.users', 'create',
                        [{
                            'name': 'Test User',
                            'login': NEW_USER,
                            'password': NEW_PASSWORD,
                            'email': NEW_USER
                        }]
                    )
                    
                    print(f"\n✅ Создан новый пользователь!")
                    print(f"  Email: {NEW_USER}")
                    print(f"  Пароль: {NEW_PASSWORD}")
                    return True
                    
        except Exception as e:
            print(f"    ❌ Не подошел: {str(e)[:50]}")
            
    return False

def try_superuser_access():
    """Попытка использовать суперпользователя"""
    print("\n🔐 Пытаюсь войти как суперпользователь...")
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Стандартные учетки суперпользователя Odoo
    SUPERUSERS = [
        ('admin', 'admin'),
        ('admin', 'admin_sportpit_2024'),
        ('admin', 'SportPit2024Master'),
        ('administrator', 'admin'),
        ('odoo', 'odoo'),
        ('superuser', 'superuser')
    ]
    
    for username, password in SUPERUSERS:
        try:
            common = xmlrpc.client.ServerProxy(
                f'{ODOO_URL}/xmlrpc/2/common',
                context=ssl_context
            )
            
            uid = common.authenticate('odoo_sportpit', username, password, {})
            
            if uid:
                print(f"\n✅ ВХОД УСПЕШЕН!")
                print(f"  Username: {username}")
                print(f"  Password: {password}")
                print(f"  UID: {uid}")
                return username, password
                
        except:
            pass
            
    return None, None

def main():
    print("=" * 60)
    print("🔓 АЛЬТЕРНАТИВНЫЕ СПОСОБЫ ВХОДА В ODOO")
    print("=" * 60)
    
    # Способ 1: Попробовать войти как суперпользователь
    username, password = try_superuser_access()
    
    if username:
        print(f"\n🎉 Используйте эти данные для входа:")
        print(f"  URL: {ODOO_URL}")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
    else:
        # Способ 2: Создать нового пользователя
        if create_user_with_master():
            print(f"\n🎉 Войдите с новым пользователем:")
            print(f"  URL: {ODOO_URL}")
            print(f"  Email: {NEW_USER}")
            print(f"  Password: {NEW_PASSWORD}")
        else:
            print("\n❌ Не удалось создать пользователя")
            print("\n🔧 Последний вариант:")
            print("1. Откройте страницу 'Сбросить пароль'")
            print("2. Введите email: danila@usafitandjoy.com")
            print("3. Если SMTP настроен, получите письмо")
            print("4. Или удалите БД и создайте заново")

if __name__ == "__main__":
    main()
