#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт восстановления настроек Odoo SportsPit
Восстанавливает состояние системы на 10.08.2025 15:24 МСК
"""

import xmlrpc.client
import ssl
import sys

# Конфигурация подключения
URL = 'https://odoosportspitproject-production.up.railway.app'
DB = 'odoo_sportpit'
USERNAME = 'admin'
PASSWORD = 'admin'

# Игнорируем SSL предупреждения для Railway
ssl._create_default_https_context = ssl._create_unverified_context

def connect_odoo():
    """Подключение к Odoo через XML-RPC"""
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    
    if not uid:
        print("❌ Ошибка аутентификации!")
        sys.exit(1)
    
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    print(f"✅ Подключено к Odoo (UID: {uid})")
    return models, uid

def setup_company(models, uid):
    """Настройка компании"""
    print("\n📦 Настройка компании SportsPit...")
    
    # Обновляем данные компании
    company_id = 1  # Основная компания
    models.execute_kw(DB, uid, PASSWORD, 'res.company', 'write', 
        [[company_id], {
            'name': 'SportsPit',
            'street': 'ул. Спортивная, 1',
            'city': 'Москва',
            'zip': '123456',
            'country_id': 188,  # Russia
            'phone': '+7 (495) 123-45-67',
            'email': 'info@usafitandjoy.com',
            'website': 'https://usafitandjoy.com',
            'vat': '7712345678',
        }])
    
    print("✅ Компания SportsPit настроена")

def setup_smtp(models, uid):
    """Настройка SMTP для отправки почты"""
    print("\n📧 Настройка почтового сервера...")
    
    # Проверяем существующие серверы
    existing = models.execute_kw(DB, uid, PASSWORD, 
        'ir.mail_server', 'search', [[('name', '=', 'Beget SMTP')]])
    
    smtp_data = {
        'name': 'Beget SMTP',
        'smtp_host': 'smtp.beget.com',
        'smtp_port': 465,
        'smtp_encryption': 'ssl',
        'smtp_user': 'danila@usafitandjoy.com',
        'smtp_pass': 'Vfdfcfthjpbr777',  # Замените на реальный пароль
        'sequence': 10,
        'active': True,
    }
    
    if existing:
        models.execute_kw(DB, uid, PASSWORD, 
            'ir.mail_server', 'write', [existing, smtp_data])
        print("✅ SMTP сервер обновлён")
    else:
        models.execute_kw(DB, uid, PASSWORD, 
            'ir.mail_server', 'create', [smtp_data])
        print("✅ SMTP сервер создан")

def create_users(models, uid):
    """Создание пользователей системы"""
    print("\n👥 Создание пользователей...")
    
    users = [
        {
            'name': 'Данила Прядко',
            'login': 'danila@usafitandjoy.com',
            'email': 'danila@usafitandjoy.com',
            'groups_id': [(6, 0, [
                3,  # Settings
                4,  # Employee
                44, # Sales Manager
                48, # Inventory Manager
            ])],
        },
        {
            'name': 'Светлана',
            'login': 'svetlana@usafitandjoy.com',
            'email': 'svetlana@usafitandjoy.com',
            'groups_id': [(6, 0, [
                4,  # Employee
                42, # Sales User
                46, # Inventory User
            ])],
        },
    ]
    
    for user_data in users:
        # Проверяем, существует ли пользователь
        existing = models.execute_kw(DB, uid, PASSWORD, 
            'res.users', 'search', [[('login', '=', user_data['login'])]])
        
        if not existing:
            try:
                user_id = models.execute_kw(DB, uid, PASSWORD, 
                    'res.users', 'create', [user_data])
                print(f"✅ Создан пользователь: {user_data['name']}")
                
                # Отправляем приглашение
                models.execute_kw(DB, uid, PASSWORD, 
                    'res.users', 'action_reset_password', [[user_id]])
                print(f"📧 Отправлено приглашение: {user_data['email']}")
            except Exception as e:
                print(f"⚠️ Ошибка при создании {user_data['name']}: {e}")
        else:
            print(f"ℹ️ Пользователь {user_data['name']} уже существует")

def install_modules(models, uid):
    """Установка необходимых модулей"""
    print("\n📦 Установка модулей...")
    
    modules_to_install = [
        'sale_management',     # Продажи
        'purchase',            # Закупки
        'stock',              # Склад
        'mrp',                # Производство
        'account',            # Бухгалтерия
        'hr',                 # Персонал
        'project',            # Проекты
        'crm',                # CRM
        'website',            # Веб-сайт
        'mass_mailing',       # Email маркетинг
    ]
    
    for module_name in modules_to_install:
        # Ищем модуль
        module_ids = models.execute_kw(DB, uid, PASSWORD, 
            'ir.module.module', 'search', [[('name', '=', module_name)]])
        
        if module_ids:
            # Проверяем статус
            module = models.execute_kw(DB, uid, PASSWORD, 
                'ir.module.module', 'read', [module_ids, ['state']])
            
            if module[0]['state'] != 'installed':
                try:
                    # Устанавливаем модуль
                    models.execute_kw(DB, uid, PASSWORD, 
                        'ir.module.module', 'button_immediate_install', [module_ids])
                    print(f"✅ Установлен модуль: {module_name}")
                except Exception as e:
                    print(f"⚠️ Ошибка установки {module_name}: {e}")
            else:
                print(f"ℹ️ Модуль {module_name} уже установлен")
        else:
            print(f"❌ Модуль {module_name} не найден")

def setup_products(models, uid):
    """Создание базовых продуктов"""
    print("\n🏷️ Создание продуктов...")
    
    # Создаём категорию
    category_id = models.execute_kw(DB, uid, PASSWORD, 
        'product.category', 'create', [{
            'name': 'Спортивное питание',
        }])
    
    products = [
        {
            'name': 'Протеин Whey Gold Standard',
            'type': 'product',
            'categ_id': category_id,
            'list_price': 3500.00,
            'standard_price': 2800.00,
            'weight': 2.27,
            'description': 'Сывороточный протеин премиум класса',
        },
        {
            'name': 'BCAA 2:1:1',
            'type': 'product',
            'categ_id': category_id,
            'list_price': 2200.00,
            'standard_price': 1800.00,
            'weight': 0.5,
            'description': 'Аминокислоты с разветвленной цепью',
        },
        {
            'name': 'Креатин моногидрат',
            'type': 'product',
            'categ_id': category_id,
            'list_price': 1500.00,
            'standard_price': 1200.00,
            'weight': 0.3,
            'description': 'Чистый креатин моногидрат',
        },
    ]
    
    for product_data in products:
        try:
            product_id = models.execute_kw(DB, uid, PASSWORD, 
                'product.product', 'create', [product_data])
            print(f"✅ Создан продукт: {product_data['name']}")
        except Exception as e:
            print(f"⚠️ Ошибка создания продукта {product_data['name']}: {e}")

def setup_warehouse(models, uid):
    """Настройка склада"""
    print("\n🏭 Настройка склада...")
    
    # Получаем основной склад
    warehouse_ids = models.execute_kw(DB, uid, PASSWORD, 
        'stock.warehouse', 'search', [[('company_id', '=', 1)]], {'limit': 1})
    
    if warehouse_ids:
        models.execute_kw(DB, uid, PASSWORD, 
            'stock.warehouse', 'write', [warehouse_ids, {
                'name': 'Основной склад SportsPit',
                'code': 'SP01',
            }])
        print("✅ Склад настроен")

def main():
    """Основная функция"""
    print("=" * 50)
    print("🚀 Восстановление настроек Odoo SportsPit")
    print("📅 Состояние на 10.08.2025 15:24 МСК")
    print("=" * 50)
    
    try:
        models, uid = connect_odoo()
        
        # Выполняем настройки
        setup_company(models, uid)
        setup_smtp(models, uid)
        create_users(models, uid)
        install_modules(models, uid)
        setup_products(models, uid)
        setup_warehouse(models, uid)
        
        print("\n" + "=" * 50)
        print("✅ Все настройки успешно восстановлены!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
