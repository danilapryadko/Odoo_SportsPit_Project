#!/usr/bin/env python3
"""
Скрипт для создания базовых продуктов и рецептур в Odoo
Автор: Claude AI Assistant
Дата: 09.08.2025
"""

import xmlrpc.client
import ssl
import sys
from datetime import datetime, timedelta

# Конфигурация
ODOO_URL = "https://odoosportspitproject-production.up.railway.app"
DB_NAME = "odoo_sportpit"
USERNAME = "danila@usafitandjoy.com"
PASSWORD = "admin_sportpit_2024"

def connect_to_odoo():
    """Подключение к Odoo через XML-RPC"""
    print("🔌 Подключение к Odoo...")
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        common = xmlrpc.client.ServerProxy(
            f'{ODOO_URL}/xmlrpc/2/common',
            context=ssl_context
        )
        
        uid = common.authenticate(DB_NAME, USERNAME, PASSWORD, {})
        
        if uid:
            print(f"✅ Аутентификация успешна")
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

def get_product_id(uid, models, default_code):
    """Получить ID продукта по коду"""
    try:
        product_ids = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'product.product', 'search',
            [[('default_code', '=', default_code)]]
        )
        return product_ids[0] if product_ids else False
    except:
        return False

def create_bom(uid, models, materials, packaging, products):
    """Создание рецептур (Bill of Materials)"""
    print("\n📋 Создание рецептур (BoM)...")
    
    boms = [
        {
            'name': 'Whey Protein Ваниль 2кг',
            'product_code': 'FIN-WHEY-VAN-2KG',
            'components': [
                ('RAW-WHEY-80', 1.95),      # Сывороточный протеин
                ('RAW-FLAV-VAN', 0.03),     # Ароматизатор ваниль
                ('RAW-SUCRALOSE', 0.02),    # Подсластитель
                ('PACK-JAR-2KG', 1),        # Банка 2кг
                ('PACK-LABEL', 1),          # Этикетка
                ('PACK-SCOOP', 1),          # Мерная ложка
            ]
        },
        {
            'name': 'Whey Protein Шоколад 2кг',
            'product_code': 'FIN-WHEY-CHOC-2KG',
            'components': [
                ('RAW-WHEY-80', 1.95),
                ('RAW-FLAV-CHOC', 0.03),
                ('RAW-SUCRALOSE', 0.02),
                ('PACK-JAR-2KG', 1),
                ('PACK-LABEL', 1),
                ('PACK-SCOOP', 1),
            ]
        },
        {
            'name': 'Mass Gainer Ваниль 3кг',
            'product_code': 'FIN-GAINER-VAN-3KG',
            'components': [
                ('RAW-WHEY-80', 0.9),       # 30% белка
                ('RAW-MALTO', 1.5),         # 50% углеводов
                ('RAW-DEXTROSE', 0.55),     # Дополнительные углеводы
                ('RAW-VITAMIN', 0.005),     # Витамины
                ('RAW-FLAV-VAN', 0.04),
                ('RAW-SUCRALOSE', 0.005),
                ('PACK-JAR-3KG', 1),
                ('PACK-LABEL', 1),
                ('PACK-SCOOP', 1),
            ]
        },
        {
            'name': 'BCAA Powder 300г',
            'product_code': 'FIN-BCAA-300G',
            'components': [
                ('RAW-BCAA', 0.295),
                ('RAW-FLAV-VAN', 0.003),
                ('RAW-SUCRALOSE', 0.002),
                ('PACK-JAR-300G', 1),
                ('PACK-LABEL', 1),
                ('PACK-SCOOP', 1),
            ]
        },
        {
            'name': 'Creatine Monohydrate 500г',
            'product_code': 'FIN-CREATINE-500G',
            'components': [
                ('RAW-CREATINE', 0.5),
                ('PACK-JAR-500G', 1),
                ('PACK-LABEL', 1),
                ('PACK-SCOOP', 1),
            ]
        },
    ]
    
    for bom_data in boms:
        try:
            # Получаем ID продукта
            product_id = get_product_id(uid, models, bom_data['product_code'])
            
            if not product_id:
                print(f"  ⚠️ Продукт {bom_data['product_code']} не найден")
                continue
            
            # Проверяем существование BoM
            existing = models.execute_kw(
                DB_NAME, uid, PASSWORD,
                'mrp.bom', 'search',
                [[('product_id', '=', product_id)]]
            )
            
            if existing:
                print(f"  ℹ️ Рецептура для {bom_data['name']} уже существует")
                continue
            
            # Подготавливаем компоненты
            bom_lines = []
            for comp_code, qty in bom_data['components']:
                comp_id = get_product_id(uid, models, comp_code)
                if comp_id:
                    bom_lines.append((0, 0, {
                        'product_id': comp_id,
                        'product_qty': qty
                    }))
            
            # Создаем BoM
            bom_id = models.execute_kw(
                DB_NAME, uid, PASSWORD,
                'mrp.bom', 'create',
                [{
                    'product_tmpl_id': models.execute_kw(
                        DB_NAME, uid, PASSWORD,
                        'product.product', 'read',
                        [product_id, ['product_tmpl_id']]
                    )[0]['product_tmpl_id'][0],
                    'product_id': product_id,
                    'product_qty': 1,
                    'type': 'normal',
                    'bom_line_ids': bom_lines
                }]
            )
            
            print(f"  ✅ Создана рецептура: {bom_data['name']}")
            
        except Exception as e:
            print(f"  ❌ Ошибка создания рецептуры {bom_data['name']}: {e}")

def create_work_centers(uid, models):
    """Создание рабочих центров"""
    print("\n🏭 Создание рабочих центров...")
    
    work_centers = [
        {
            'name': 'Участок взвешивания',
            'code': 'WC-WEIGH',
            'capacity': 2,
            'time_efficiency': 100,
            'costs_hour': 500,
        },
        {
            'name': 'Участок смешивания',
            'code': 'WC-MIX',
            'capacity': 1,
            'time_efficiency': 95,
            'costs_hour': 800,
        },
        {
            'name': 'Участок фасовки',
            'code': 'WC-PACK',
            'capacity': 3,
            'time_efficiency': 98,
            'costs_hour': 600,
        },
        {
            'name': 'Участок упаковки',
            'code': 'WC-LABEL',
            'capacity': 2,
            'time_efficiency': 99,
            'costs_hour': 400,
        },
        {
            'name': 'Лаборатория контроля качества',
            'code': 'WC-QC',
            'capacity': 1,
            'time_efficiency': 100,
            'costs_hour': 1000,
        },
    ]
    
    for wc_data in work_centers:
        try:
            # Проверяем существование
            existing = models.execute_kw(
                DB_NAME, uid, PASSWORD,
                'mrp.workcenter', 'search',
                [[('code', '=', wc_data['code'])]]
            )
            
            if not existing:
                wc_id = models.execute_kw(
                    DB_NAME, uid, PASSWORD,
                    'mrp.workcenter', 'create',
                    [wc_data]
                )
                print(f"  ✅ Создан рабочий центр: {wc_data['name']}")
            else:
                print(f"  ℹ️ Рабочий центр уже существует: {wc_data['name']}")
                
        except Exception as e:
            print(f"  ❌ Ошибка создания {wc_data['name']}: {e}")

def main():
    """Основная функция"""
    print("=" * 60)
    print("🚀 СОЗДАНИЕ ПРОДУКТОВ И РЕЦЕПТУР")
    print("=" * 60)
    
    # Подключаемся к Odoo
    uid, models = connect_to_odoo()
    
    if not uid:
        print("\n❌ Не удалось подключиться к Odoo")
        sys.exit(1)
    
    # Создаем рабочие центры
    create_work_centers(uid, models)
    
    # Создаем продукты
    materials = create_raw_materials(uid, models)
    packaging = create_packaging_materials(uid, models)
    products = create_finished_products(uid, models)
    
    # Создаем рецептуры
    create_bom(uid, models, materials, packaging, products)
    
    print("\n" + "=" * 60)
    print("✅ СОЗДАНИЕ ЗАВЕРШЕНО!")
    print("=" * 60)
    print("\n📋 Результаты:")
    print(f"  • Создано сырьевых материалов: {len(materials)}")
    print(f"  • Создано упаковочных материалов: {len(packaging)}")
    print(f"  • Создано готовых продуктов: {len(products)}")
    print("\n📋 Следующие шаги:")
    print("1. Проверьте созданные продукты в Odoo")
    print("2. Настройте маршруты производства")
    print("3. Создайте первый производственный заказ")
    print("4. Настройте точки контроля качества")

if __name__ == "__main__":
    main()
