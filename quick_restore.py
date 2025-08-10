#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xmlrpc.client
import ssl

# Игнорируем SSL
ssl._create_default_https_context = ssl._create_unverified_context

# Подключение
url = 'https://odoosportspitproject-production.up.railway.app'
db = 'odoo_sportpit'
username = 'admin'
password = 'admin'

# Аутентификация
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
print(f"Connected, UID: {uid}")

# Модели
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 1. НАСТРОЙКА SMTP
print("\n1. Настройка SMTP...")
smtp_data = {
    'name': 'Beget SMTP',
    'smtp_host': 'smtp.beget.com',
    'smtp_port': 465,
    'smtp_encryption': 'ssl',
    'smtp_user': 'danila@usafitandjoy.com',
    'smtp_pass': 'Vfdfcfthjpbr777',  # Замените на реальный
    'active': True,
    'sequence': 10,
}

try:
    smtp_id = models.execute_kw(db, uid, password, 'ir.mail_server', 'create', [smtp_data])
    print(f"✅ SMTP сервер создан (ID: {smtp_id})")
except Exception as e:
    print(f"❌ Ошибка SMTP: {e}")

# 2. СОЗДАНИЕ ПОЛЬЗОВАТЕЛЕЙ
print("\n2. Создание пользователей...")

users = [
    {
        'name': 'Данила Прядко',
        'login': 'danila@usafitandjoy.com',
        'email': 'danila@usafitandjoy.com',
        'phone': '+79779106671',
        'groups_id': [(6, 0, [3, 4, 44, 48])],  # Admin groups
    },
    {
        'name': 'Светлана',
        'login': 'svetlana@usafitandjoy.com', 
        'email': 'svetlana@usafitandjoy.com',
        'groups_id': [(6, 0, [4, 42, 46])],  # User groups
    }
]

for user in users:
    try:
        # Проверяем существование
        exists = models.execute_kw(db, uid, password, 'res.users', 'search', 
            [[('login', '=', user['login'])]])
        
        if not exists:
            user_id = models.execute_kw(db, uid, password, 'res.users', 'create', [user])
            print(f"✅ Создан: {user['name']} (ID: {user_id})")
        else:
            print(f"ℹ️ Уже существует: {user['name']}")
    except Exception as e:
        print(f"❌ Ошибка для {user['name']}: {e}")

# 3. ОБНОВЛЕНИЕ КОМПАНИИ
print("\n3. Настройка компании...")
try:
    company_data = {
        'name': 'SportsPit',
        'street': 'ул. Спортивная, 1',
        'city': 'Москва',
        'zip': '123456',
        'phone': '+7 (495) 123-45-67',
        'email': 'info@usafitandjoy.com',
        'website': 'https://usafitandjoy.com',
        'vat': '7712345678',
    }
    
    models.execute_kw(db, uid, password, 'res.company', 'write', [[1], company_data])
    print("✅ Компания настроена")
except Exception as e:
    print(f"❌ Ошибка компании: {e}")

# 4. УСТАНОВКА МОДУЛЕЙ
print("\n4. Установка модулей...")
modules = ['sale_management', 'purchase', 'stock', 'mrp', 'account', 'crm', 'hr', 'project']

for module_name in modules:
    try:
        # Ищем модуль
        module_ids = models.execute_kw(db, uid, password, 
            'ir.module.module', 'search', [[('name', '=', module_name)]])
        
        if module_ids:
            # Проверяем статус
            module = models.execute_kw(db, uid, password, 
                'ir.module.module', 'read', [module_ids, ['state']])
            
            if module[0]['state'] != 'installed':
                models.execute_kw(db, uid, password, 
                    'ir.module.module', 'button_immediate_install', [module_ids])
                print(f"✅ Установлен: {module_name}")
            else:
                print(f"ℹ️ Уже установлен: {module_name}")
    except Exception as e:
        print(f"❌ Ошибка {module_name}: {e}")

# 5. СОЗДАНИЕ ПРОДУКТОВ
print("\n5. Создание продуктов...")

# Создаём категорию
try:
    categ_id = models.execute_kw(db, uid, password, 'product.category', 'create', 
        [{'name': 'Спортивное питание'}])
    print(f"✅ Категория создана (ID: {categ_id})")
    
    products = [
        {
            'name': 'Протеин Whey Gold Standard',
            'type': 'product',
            'categ_id': categ_id,
            'list_price': 3500.00,
            'standard_price': 2800.00,
            'weight': 2.27,
            'barcode': '748927028881',
        },
        {
            'name': 'BCAA 2:1:1',
            'type': 'product', 
            'categ_id': categ_id,
            'list_price': 2200.00,
            'standard_price': 1800.00,
            'weight': 0.5,
            'barcode': '748927028882',
        },
        {
            'name': 'Креатин моногидрат',
            'type': 'product',
            'categ_id': categ_id,
            'list_price': 1500.00,
            'standard_price': 1200.00,
            'weight': 0.3,
            'barcode': '748927028883',
        }
    ]
    
    for product in products:
        prod_id = models.execute_kw(db, uid, password, 'product.product', 'create', [product])
        print(f"✅ Создан продукт: {product['name']} (ID: {prod_id})")
        
except Exception as e:
    print(f"❌ Ошибка продуктов: {e}")

print("\n✅ Восстановление завершено!")
