#!/usr/bin/env python3
"""
Создание рецептур (BOM) и рабочих центров для производства
"""

import xmlrpc.client
import ssl

ODOO_URL = "https://odoosportspitproject-production.up.railway.app"
DB_NAME = "odoo_sportpit"
LOGIN = "danila@usafitandjoy.com"
PASSWORD = "admin123"

def create_bom_and_workcenters():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common', context=ssl_context)
        uid = common.authenticate(DB_NAME, LOGIN, PASSWORD, {})
        
        if not uid:
            print("❌ Не удалось войти")
            return False
            
        print(f"✅ Вошел как {LOGIN}")
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object', context=ssl_context)
        
        # СОЗДАНИЕ РАБОЧИХ ЦЕНТРОВ
        print("\n🏭 СОЗДАНИЕ РАБОЧИХ ЦЕНТРОВ:")
        
        work_centers = [
            {'name': 'Участок взвешивания', 'code': 'WC-WEIGH', 'capacity': 2, 'time_efficiency': 100, 'costs_hour': 500},
            {'name': 'Участок смешивания', 'code': 'WC-MIX', 'capacity': 1, 'time_efficiency': 95, 'costs_hour': 800},
            {'name': 'Участок фасовки', 'code': 'WC-PACK', 'capacity': 3, 'time_efficiency': 98, 'costs_hour': 600},
            {'name': 'Лаборатория QC', 'code': 'WC-QC', 'capacity': 1, 'time_efficiency': 100, 'costs_hour': 1000},
        ]
        
        wc_ids = {}
        for wc in work_centers:
            existing = models.execute_kw(
                DB_NAME, uid, PASSWORD,
                'mrp.workcenter', 'search',
                [[('code', '=', wc['code'])]]
            )
            
            if not existing:
                wc_id = models.execute_kw(
                    DB_NAME, uid, PASSWORD,
                    'mrp.workcenter', 'create', [wc]
                )
                wc_ids[wc['code']] = wc_id
                print(f"  ✅ Создан: {wc['name']}")
            else:
                wc_ids[wc['code']] = existing[0]
                print(f"  ℹ️ Уже существует: {wc['name']}")
        
        # ПОЛУЧЕНИЕ ID ПРОДУКТОВ
        print("\n📦 ПОЛУЧЕНИЕ ПРОДУКТОВ:")
        
        # Функция для получения ID продукта по коду
        def get_product_id(code):
            prod = models.execute_kw(
                DB_NAME, uid, PASSWORD,
                'product.product', 'search',
                [[('default_code', '=', code)]]
            )
            return prod[0] if prod else None
        
        products = {}
        codes = ['RAW-WHEY', 'RAW-MALTO', 'RAW-CREAT', 'RAW-BCAA', 'RAW-VANIL',
                 'FIN-WHEY-2KG', 'FIN-GAIN-3KG', 'FIN-BCAA-300', 'FIN-CREAT-500']
        
        for code in codes:
            prod_id = get_product_id(code)
            if prod_id:
                products[code] = prod_id
                print(f"  ✅ Найден: {code}")
        
        # СОЗДАНИЕ УПАКОВОЧНЫХ МАТЕРИАЛОВ
        print("\n📦 СОЗДАНИЕ УПАКОВКИ:")
        
        packaging = [
            {'name': 'Банка 2кг', 'default_code': 'PACK-2KG', 'standard_price': 45},
            {'name': 'Банка 3кг', 'default_code': 'PACK-3KG', 'standard_price': 55},
            {'name': 'Банка 300г', 'default_code': 'PACK-300G', 'standard_price': 25},
            {'name': 'Банка 500г', 'default_code': 'PACK-500G', 'standard_price': 30},
            {'name': 'Этикетка', 'default_code': 'PACK-LABEL', 'standard_price': 3},
            {'name': 'Мерная ложка', 'default_code': 'PACK-SCOOP', 'standard_price': 5},
        ]
        
        # Получаем категорию Сырье
        raw_cat = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'product.category', 'search',
            [[('name', '=', 'Сырье')]]
        )[0]
        
        for pack in packaging:
            existing = models.execute_kw(
                DB_NAME, uid, PASSWORD,
                'product.product', 'search',
                [[('default_code', '=', pack['default_code'])]]
            )
            
            if not existing:
                pack_data = {
                    'name': pack['name'],
                    'default_code': pack['default_code'],
                    'standard_price': pack['standard_price'],
                    'type': 'product',
                    'categ_id': raw_cat,
                    'uom_id': 1,
                    'purchase_ok': True,
                    'sale_ok': False
                }
                
                pack_id = models.execute_kw(
                    DB_NAME, uid, PASSWORD,
                    'product.product', 'create', [pack_data]
                )
                products[pack['default_code']] = pack_id
                print(f"  ✅ Создана: {pack['name']}")
            else:
                products[pack['default_code']] = existing[0]
                print(f"  ℹ️ Уже существует: {pack['name']}")
        
        # СОЗДАНИЕ РЕЦЕПТУР (BOM)
        print("\n📋 СОЗДАНИЕ РЕЦЕПТУР (BOM):")
        
        boms = [
            {
                'name': 'Whey Protein Ваниль 2кг',
                'product_id': products.get('FIN-WHEY-2KG'),
                'product_qty': 1,
                'lines': [
                    ('RAW-WHEY', 1.95),      # Сывороточный протеин
                    ('RAW-VANIL', 0.03),     # Ароматизатор
                    ('PACK-2KG', 1),         # Банка
                    ('PACK-LABEL', 1),       # Этикетка
                    ('PACK-SCOOP', 1),       # Ложка
                ]
            },
            {
                'name': 'Mass Gainer 3кг',
                'product_id': products.get('FIN-GAIN-3KG'),
                'product_qty': 1,
                'lines': [
                    ('RAW-WHEY', 0.9),       # Протеин
                    ('RAW-MALTO', 2.0),      # Углеводы
                    ('RAW-VANIL', 0.05),     # Ароматизатор
                    ('PACK-3KG', 1),         # Банка
                    ('PACK-LABEL', 1),       # Этикетка
                    ('PACK-SCOOP', 1),       # Ложка
                ]
            },
            {
                'name': 'BCAA 300г',
                'product_id': products.get('FIN-BCAA-300'),
                'product_qty': 1,
                'lines': [
                    ('RAW-BCAA', 0.295),     # BCAA
                    ('RAW-VANIL', 0.005),    # Ароматизатор
                    ('PACK-300G', 1),        # Банка
                    ('PACK-LABEL', 1),       # Этикетка
                    ('PACK-SCOOP', 1),       # Ложка
                ]
            },
            {
                'name': 'Creatine 500г',
                'product_id': products.get('FIN-CREAT-500'),
                'product_qty': 1,
                'lines': [
                    ('RAW-CREAT', 0.5),      # Креатин
                    ('PACK-500G', 1),        # Банка
                    ('PACK-LABEL', 1),       # Этикетка
                    ('PACK-SCOOP', 1),       # Ложка
                ]
            }
        ]
        
        for bom_data in boms:
            if not bom_data['product_id']:
                print(f"  ⚠️ Продукт не найден для {bom_data['name']}")
                continue
            
            # Проверяем существование BOM
            existing = models.execute_kw(
                DB_NAME, uid, PASSWORD,
                'mrp.bom', 'search',
                [[('product_id', '=', bom_data['product_id'])]]
            )
            
            if existing:
                print(f"  ℹ️ Рецептура уже существует: {bom_data['name']}")
                continue
            
            # Получаем product_tmpl_id
            product = models.execute_kw(
                DB_NAME, uid, PASSWORD,
                'product.product', 'read',
                [bom_data['product_id'], ['product_tmpl_id']]
            )
            
            # Подготавливаем линии BOM
            bom_lines = []
            for comp_code, qty in bom_data['lines']:
                comp_id = products.get(comp_code)
                if comp_id:
                    bom_lines.append((0, 0, {
                        'product_id': comp_id,
                        'product_qty': qty
                    }))
            
            # Создаем BOM
            try:
                bom_id = models.execute_kw(
                    DB_NAME, uid, PASSWORD,
                    'mrp.bom', 'create',
                    [{
                        'product_tmpl_id': product[0]['product_tmpl_id'][0],
                        'product_id': bom_data['product_id'],
                        'product_qty': bom_data['product_qty'],
                        'type': 'normal',
                        'bom_line_ids': bom_lines
                    }]
                )
                print(f"  ✅ Создана рецептура: {bom_data['name']}")
            except Exception as e:
                print(f"  ❌ Ошибка создания {bom_data['name']}: {str(e)[:50]}")
        
        # ИТОГОВАЯ ПРОВЕРКА
        print("\n" + "="*60)
        print("📊 ИТОГОВАЯ ПРОВЕРКА:")
        
        # Проверяем созданные рецептуры
        all_boms = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'mrp.bom', 'search_read',
            [[]],
            {'fields': ['display_name', 'product_id', 'bom_line_ids']}
        )
        
        print(f"\n✅ Создано рецептур: {len(all_boms)}")
        for bom in all_boms:
            line_count = len(bom['bom_line_ids']) if bom['bom_line_ids'] else 0
            print(f"  • {bom['display_name']} ({line_count} компонентов)")
        
        # Проверяем рабочие центры
        all_wc = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'mrp.workcenter', 'search_read',
            [[]],
            {'fields': ['name', 'code']}
        )
        
        print(f"\n✅ Рабочих центров: {len(all_wc)}")
        for wc in all_wc:
            print(f"  • {wc['name']} ({wc['code']})")
        
        print("\n" + "="*60)
        print("✅ СИСТЕМА ГОТОВА К РАБОТЕ!")
        print("="*60)
        print("\n🎯 Теперь можно:")
        print("1. Создать производственный заказ")
        print("2. Запустить производство")
        print("3. Отслеживать склад")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🏭 СОЗДАНИЕ РЕЦЕПТУР И НАСТРОЙКА ПРОИЗВОДСТВА")
    print("="*60)
    
    create_bom_and_workcenters()
