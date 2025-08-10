#!/usr/bin/env python3
"""
Проверка установленных модулей и создание продуктов/рецептур
"""

import xmlrpc.client
import ssl

ODOO_URL = "https://odoosportspitproject-production.up.railway.app"
DB_NAME = "odoo_sportpit"

# Пробуем разные учетные данные
CREDENTIALS = [
    ("danila@usafitandjoy.com", "admin123"),
    ("test@test.com", "test123")
]

def check_and_create():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    for login, password in CREDENTIALS:
        try:
            common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common', context=ssl_context)
            uid = common.authenticate(DB_NAME, login, password, {})
            
            if uid:
                print(f"✅ Вошел как {login}")
                models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object', context=ssl_context)
                
                # ПРОВЕРКА МОДУЛЕЙ
                print("\n📦 УСТАНОВЛЕННЫЕ МОДУЛИ:")
                modules = models.execute_kw(
                    DB_NAME, uid, password,
                    'ir.module.module', 'search_read',
                    [[('state', '=', 'installed')]],
                    {'fields': ['name', 'display_name'], 'limit': 200}
                )
                
                important_modules = ['mrp', 'stock', 'sale', 'purchase', 'account', 'hr', 'project']
                installed = [m['name'] for m in modules]
                
                for mod in important_modules:
                    if mod in installed:
                        print(f"  ✅ {mod}")
                    else:
                        print(f"  ❌ {mod} - НЕ УСТАНОВЛЕН")
                
                # ПРОВЕРКА ПРОДУКТОВ
                print("\n📦 ПРОДУКТЫ:")
                products = models.execute_kw(
                    DB_NAME, uid, password,
                    'product.product', 'search_read',
                    [[]],
                    {'fields': ['name', 'default_code'], 'limit': 100}
                )
                print(f"  Найдено продуктов: {len(products)}")
                
                if len(products) < 5:
                    print("  ⚠️ Мало продуктов, создаю...")
                    
                    # СОЗДАНИЕ КАТЕГОРИЙ
                    print("\n📁 Создание категорий...")
                    categories = {
                        'Сырье': None,
                        'Готовая продукция': None
                    }
                    
                    for cat_name in categories:
                        cat_ids = models.execute_kw(
                            DB_NAME, uid, password,
                            'product.category', 'search',
                            [[('name', '=', cat_name)]]
                        )
                        
                        if not cat_ids:
                            cat_id = models.execute_kw(
                                DB_NAME, uid, password,
                                'product.category', 'create',
                                [{'name': cat_name}]
                            )
                            categories[cat_name] = cat_id
                            print(f"    ✅ Создана категория: {cat_name}")
                        else:
                            categories[cat_name] = cat_ids[0]
                    
                    # СОЗДАНИЕ ПРОДУКТОВ
                    print("\n📦 Создание продуктов...")
                    
                    # Сырье
                    raw_materials = [
                        {'name': 'Сывороточный протеин 80%', 'default_code': 'RAW-WHEY', 'standard_price': 350, 'categ_id': categories['Сырье']},
                        {'name': 'Мальтодекстрин', 'default_code': 'RAW-MALTO', 'standard_price': 80, 'categ_id': categories['Сырье']},
                        {'name': 'Креатин моногидрат', 'default_code': 'RAW-CREAT', 'standard_price': 550, 'categ_id': categories['Сырье']},
                        {'name': 'BCAA 2:1:1', 'default_code': 'RAW-BCAA', 'standard_price': 1200, 'categ_id': categories['Сырье']},
                        {'name': 'Ароматизатор Ваниль', 'default_code': 'RAW-VANIL', 'standard_price': 800, 'categ_id': categories['Сырье']},
                    ]
                    
                    for prod in raw_materials:
                        try:
                            prod['type'] = 'product'
                            prod['uom_id'] = 1  # kg
                            prod_id = models.execute_kw(
                                DB_NAME, uid, password,
                                'product.product', 'create', [prod]
                            )
                            print(f"    ✅ Создан: {prod['name']}")
                        except:
                            print(f"    ℹ️ Уже существует: {prod['name']}")
                    
                    # Готовая продукция
                    finished = [
                        {'name': 'Whey Protein Ваниль 2кг', 'default_code': 'FIN-WHEY-2KG', 'list_price': 2500, 'categ_id': categories['Готовая продукция']},
                        {'name': 'Mass Gainer 3кг', 'default_code': 'FIN-GAIN-3KG', 'list_price': 2200, 'categ_id': categories['Готовая продукция']},
                        {'name': 'BCAA 300г', 'default_code': 'FIN-BCAA-300', 'list_price': 1800, 'categ_id': categories['Готовая продукция']},
                        {'name': 'Creatine 500г', 'default_code': 'FIN-CREAT-500', 'list_price': 900, 'categ_id': categories['Готовая продукция']},
                    ]
                    
                    for prod in finished:
                        try:
                            prod['type'] = 'product'
                            prod['uom_id'] = 1
                            prod['sale_ok'] = True
                            prod['purchase_ok'] = False
                            prod_id = models.execute_kw(
                                DB_NAME, uid, password,
                                'product.product', 'create', [prod]
                            )
                            print(f"    ✅ Создан: {prod['name']}")
                        except:
                            print(f"    ℹ️ Уже существует: {prod['name']}")
                
                # ПРОВЕРКА СКЛАДОВ
                print("\n📦 СКЛАДЫ:")
                warehouses = models.execute_kw(
                    DB_NAME, uid, password,
                    'stock.warehouse', 'search_read',
                    [[]],
                    {'fields': ['name', 'code']}
                )
                
                if warehouses:
                    for wh in warehouses:
                        print(f"  ✅ {wh['name']} ({wh['code']})")
                else:
                    print("  ❌ Склады не найдены")
                    
                    # Создаем склад
                    wh_id = models.execute_kw(
                        DB_NAME, uid, password,
                        'stock.warehouse', 'create',
                        [{'name': 'Основной склад', 'code': 'MAIN'}]
                    )
                    print(f"  ✅ Создан основной склад")
                
                # ПРОВЕРКА BOM (рецептур)
                print("\n📋 РЕЦЕПТУРЫ (BOM):")
                boms = models.execute_kw(
                    DB_NAME, uid, password,
                    'mrp.bom', 'search_read',
                    [[]],
                    {'fields': ['display_name'], 'limit': 10}
                )
                
                if boms:
                    print(f"  Найдено рецептур: {len(boms)}")
                    for bom in boms[:3]:
                        print(f"    • {bom['display_name']}")
                else:
                    print("  ❌ Рецептуры не созданы")
                    print("  ℹ️ Для создания рецептур нужен модуль MRP")
                
                print("\n" + "="*60)
                print("📊 ИТОГО:")
                print(f"  Модулей установлено: {len([m for m in important_modules if m in installed])}/{len(important_modules)}")
                print(f"  Продуктов создано: {len(products)}")
                print(f"  Складов: {len(warehouses)}")
                print(f"  Рецептур: {len(boms)}")
                
                return True
                
        except Exception as e:
            print(f"❌ Ошибка с {login}: {str(e)[:100]}")
    
    return False

if __name__ == "__main__":
    print("="*60)
    print("🔍 ПРОВЕРКА И СОЗДАНИЕ ДАННЫХ В ODOO")
    print("="*60)
    
    check_and_create()
