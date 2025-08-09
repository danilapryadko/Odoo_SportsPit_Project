#!/usr/bin/env python3
"""
Скрипт для автоматической установки модулей Odoo
Автор: Claude AI Assistant
Дата: 09.08.2025
"""

import xmlrpc.client
import ssl
import sys

# Конфигурация
ODOO_URL = "https://odoosportspitproject-production.up.railway.app"
DB_NAME = "odoo_sportpit"
USERNAME = "danila@usafitandjoy.com"
PASSWORD = "admin_sportpit_2024"

# Список модулей для установки
MODULES_TO_INSTALL = [
    # Основные модули
    'mrp',                    # Manufacturing
    'stock',                  # Inventory
    'purchase',               # Purchase
    'sale_management',        # Sales with quotations
    'quality_control',        # Quality Control
    'account',               # Accounting
    'hr',                    # Employees
    'hr_attendance',         # Attendances
    'project',               # Project Management
    'product_expiry',        # Product Expiry Dates
    
    # Дополнительные полезные модули
    'mrp_workorder',         # Work Orders
    'stock_barcode',         # Barcode scanning
    'purchase_stock',        # Purchase-Stock integration
    'sale_stock',           # Sale-Stock integration
    'mrp_account',          # MRP-Accounting integration
    'quality_mrp',          # Quality in Manufacturing
    'stock_account',        # Stock valuation
    'mrp_subcontracting',   # Subcontracting
    'web_responsive',       # Responsive Web Interface (если доступен)
]

def connect_to_odoo():
    """Подключение к Odoo через XML-RPC"""
    print("🔌 Подключение к Odoo...")
    
    # Игнорируем SSL warnings для self-signed сертификатов
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        # Подключаемся к common endpoint для аутентификации
        common = xmlrpc.client.ServerProxy(
            f'{ODOO_URL}/xmlrpc/2/common',
            context=ssl_context
        )
        
        # Проверяем версию
        version = common.version()
        print(f"✅ Подключено к Odoo {version['server_version']}")
        
        # Аутентификация
        uid = common.authenticate(DB_NAME, USERNAME, PASSWORD, {})
        
        if uid:
            print(f"✅ Аутентификация успешна (UID: {uid})")
            
            # Подключаемся к object endpoint
            models = xmlrpc.client.ServerProxy(
                f'{ODOO_URL}/xmlrpc/2/object',
                context=ssl_context
            )
            
            return uid, models
        else:
            print("❌ Ошибка аутентификации")
            return None, None
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return None, None

def get_installed_modules(uid, models):
    """Получить список установленных модулей"""
    try:
        installed = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'ir.module.module', 'search_read',
            [[('state', '=', 'installed')]],
            {'fields': ['name', 'display_name']}
        )
        return {m['name']: m['display_name'] for m in installed}
    except Exception as e:
        print(f"❌ Ошибка получения списка модулей: {e}")
        return {}

def install_module(uid, models, module_name):
    """Установка одного модуля"""
    try:
        # Ищем модуль
        module_ids = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'ir.module.module', 'search',
            [[('name', '=', module_name)]]
        )
        
        if not module_ids:
            print(f"  ⚠️ Модуль '{module_name}' не найден")
            return False
        
        # Проверяем состояние модуля
        module = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'ir.module.module', 'read',
            [module_ids[0]],
            {'fields': ['state', 'display_name']}
        )
        
        if module[0]['state'] == 'installed':
            print(f"  ✅ '{module[0]['display_name']}' уже установлен")
            return True
        
        # Устанавливаем модуль
        print(f"  🔄 Установка '{module[0]['display_name']}'...")
        models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'ir.module.module', 'button_immediate_install',
            [module_ids]
        )
        
        print(f"  ✅ '{module[0]['display_name']}' установлен")
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка установки '{module_name}': {e}")
        return False

def configure_company(uid, models):
    """Базовая настройка компании"""
    print("\n🏢 Настройка компании...")
    
    try:
        # Получаем компанию
        company_ids = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'res.company', 'search',
            [[]]
        )
        
        if company_ids:
            # Обновляем данные компании
            models.execute_kw(
                DB_NAME, uid, PASSWORD,
                'res.company', 'write',
                [company_ids[0], {
                    'name': 'SportPit Company',
                    'street': 'ул. Спортивная, 1',
                    'city': 'Москва',
                    'zip': '123456',
                    'country_id': 188,  # Russia
                    'phone': '+7 (495) 123-45-67',
                    'email': 'info@sportpit.ru',
                    'website': 'https://sportpit.ru',
                    'vat': '7707123456',  # ИНН
                }]
            )
            print("  ✅ Данные компании обновлены")
            
        # Настройка валюты (RUB)
        rub_ids = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'res.currency', 'search',
            [[('name', '=', 'RUB')]]
        )
        
        if rub_ids:
            models.execute_kw(
                DB_NAME, uid, PASSWORD,
                'res.currency', 'write',
                [rub_ids[0], {'active': True}]
            )
            print("  ✅ Валюта RUB активирована")
            
    except Exception as e:
        print(f"  ❌ Ошибка настройки компании: {e}")

def create_warehouses(uid, models):
    """Создание структуры складов"""
    print("\n📦 Создание складов...")
    
    warehouses = [
        {
            'name': 'Склад сырья',
            'code': 'RAW',
            'reception_steps': 'two_steps',  # Приемка + Контроль качества
            'delivery_steps': 'pick_ship',   # Комплектация + Отгрузка
        },
        {
            'name': 'Склад готовой продукции',
            'code': 'FIN',
            'reception_steps': 'one_step',
            'delivery_steps': 'pick_pack_ship',  # Комплектация + Упаковка + Отгрузка
        }
    ]
    
    try:
        for wh_data in warehouses:
            # Проверяем, существует ли склад
            existing = models.execute_kw(
                DB_NAME, uid, PASSWORD,
                'stock.warehouse', 'search',
                [[('code', '=', wh_data['code'])]]
            )
            
            if not existing:
                wh_id = models.execute_kw(
                    DB_NAME, uid, PASSWORD,
                    'stock.warehouse', 'create',
                    [wh_data]
                )
                print(f"  ✅ Склад '{wh_data['name']}' создан")
            else:
                print(f"  ℹ️ Склад '{wh_data['name']}' уже существует")
                
    except Exception as e:
        print(f"  ❌ Ошибка создания складов: {e}")

def create_product_categories(uid, models):
    """Создание категорий продуктов"""
    print("\n📁 Создание категорий продуктов...")
    
    categories = [
        {'name': 'Сырье', 'parent': None},
        {'name': 'Белки', 'parent': 'Сырье'},
        {'name': 'Углеводы', 'parent': 'Сырье'},
        {'name': 'Добавки', 'parent': 'Сырье'},
        {'name': 'Ароматизаторы', 'parent': 'Сырье'},
        {'name': 'Готовая продукция', 'parent': None},
        {'name': 'Протеины', 'parent': 'Готовая продукция'},
        {'name': 'Гейнеры', 'parent': 'Готовая продукция'},
        {'name': 'BCAA', 'parent': 'Готовая продукция'},
        {'name': 'Креатин', 'parent': 'Готовая продукция'},
        {'name': 'Предтреники', 'parent': 'Готовая продукция'},
    ]
    
    try:
        created_categories = {}
        
        for cat_data in categories:
            # Определяем parent_id
            parent_id = False
            if cat_data['parent']:
                if cat_data['parent'] in created_categories:
                    parent_id = created_categories[cat_data['parent']]
            
            # Проверяем существование категории
            existing = models.execute_kw(
                DB_NAME, uid, PASSWORD,
                'product.category', 'search',
                [[('name', '=', cat_data['name']), 
                  ('parent_id', '=', parent_id)]]
            )
            
            if not existing:
                cat_id = models.execute_kw(
                    DB_NAME, uid, PASSWORD,
                    'product.category', 'create',
                    [{
                        'name': cat_data['name'],
                        'parent_id': parent_id
                    }]
                )
                created_categories[cat_data['name']] = cat_id
                print(f"  ✅ Категория '{cat_data['name']}' создана")
            else:
                created_categories[cat_data['name']] = existing[0]
                print(f"  ℹ️ Категория '{cat_data['name']}' уже существует")
                
    except Exception as e:
        print(f"  ❌ Ошибка создания категорий: {e}")

def main():
    """Основная функция"""
    print("=" * 60)
    print("🚀 УСТАНОВКА И НАСТРОЙКА МОДУЛЕЙ ODOO")
    print("=" * 60)
    
    # Подключаемся к Odoo
    uid, models = connect_to_odoo()
    
    if not uid:
        print("\n❌ Не удалось подключиться к Odoo")
        print("Убедитесь, что:")
        print("1. База данных создана")
        print("2. Учетные данные корректны")
        print("3. Odoo доступен по указанному URL")
        sys.exit(1)
    
    # Получаем список установленных модулей
    print("\n📋 Проверка установленных модулей...")
    installed = get_installed_modules(uid, models)
    print(f"  Установлено модулей: {len(installed)}")
    
    # Устанавливаем необходимые модули
    print("\n📦 Установка модулей...")
    success_count = 0
    for module_name in MODULES_TO_INSTALL:
        if install_module(uid, models, module_name):
            success_count += 1
    
    print(f"\n✅ Установлено {success_count} из {len(MODULES_TO_INSTALL)} модулей")
    
    # Настраиваем компанию
    configure_company(uid, models)
    
    # Создаем склады
    create_warehouses(uid, models)
    
    # Создаем категории продуктов
    create_product_categories(uid, models)
    
    print("\n" + "=" * 60)
    print("✅ НАСТРОЙКА ЗАВЕРШЕНА!")
    print("=" * 60)
    print("\n📋 Следующие шаги:")
    print("1. Войдите в Odoo и проверьте установленные модули")
    print("2. Настройте рабочие центры для производства")
    print("3. Создайте первые продукты и рецептуры")
    print("4. Настройте пользователей и права доступа")

if __name__ == "__main__":
    main()
