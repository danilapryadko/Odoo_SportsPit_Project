#!/usr/bin/env python3
"""
Скрипт для изменения имени администратора в Odoo
"""

import xmlrpc.client
import ssl
import sys

# Конфигурация подключения
url = 'https://odoosportspitproject-production.up.railway.app'
db = 'odoo_sportpit'
username = 'danila@usafitandjoy.com'
password = 'admin_sportpit_2024'

# Новое имя администратора
new_name = 'Прядко Данила Игоревич'

try:
    # Создаем контекст SSL для игнорирования проверки сертификата (для Railway)
    context = ssl._create_unverified_context()
    
    # Подключение к Odoo
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', context=context)
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        print("❌ Ошибка аутентификации. Проверьте логин и пароль.")
        sys.exit(1)
    
    print(f"✅ Успешная аутентификация. UID: {uid}")
    
    # Создаем объект для работы с моделями
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', context=context)
    
    # Ищем пользователя администратора
    admin_ids = models.execute_kw(db, uid, password,
        'res.users', 'search',
        [[['login', '=', username]]])
    
    if not admin_ids:
        print("❌ Пользователь не найден")
        sys.exit(1)
    
    admin_id = admin_ids[0]
    print(f"✅ Найден пользователь с ID: {admin_id}")
    
    # Получаем текущее имя
    current_user = models.execute_kw(db, uid, password,
        'res.users', 'read',
        [admin_id], {'fields': ['name', 'login']})
    
    if current_user:
        print(f"📝 Текущее имя: {current_user[0]['name']}")
    
    # Обновляем имя пользователя
    result = models.execute_kw(db, uid, password,
        'res.users', 'write',
        [[admin_id], {'name': new_name}])
    
    if result:
        print(f"✅ Имя успешно изменено на: {new_name}")
        
        # Проверяем изменение
        updated_user = models.execute_kw(db, uid, password,
            'res.users', 'read',
            [admin_id], {'fields': ['name']})
        
        if updated_user:
            print(f"✅ Проверка: новое имя в системе - {updated_user[0]['name']}")
    else:
        print("❌ Не удалось изменить имя")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")
    sys.exit(1)
