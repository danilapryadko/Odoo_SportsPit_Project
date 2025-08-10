#!/usr/bin/env python3
"""
Создание рецептур (BOM) и рабочих центров - исправленная версия
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
        
        # СОЗДАНИЕ РАБОЧИХ ЦЕНТРОВ (упрощенная версия)
        print("\n🏭 СОЗДАНИЕ РАБОЧИХ ЦЕНТРОВ:")
        
        work_centers = [
            {'name': 'Участок взвешивания', 'code': 'WC-WEIGH', 'time_efficiency': 100, 'costs_hour': 500},
            {'name': 'Участок смешивания', 'code': 'WC-MIX', 'time_efficiency': 95, 'costs_hour': 800},
            {'name': 'Участок фасовки', 'code': 'WC-PACK', 'time_efficiency': 98, 'costs_hour': 600},
            {'name': 'Лаборатория контроля качества', 'code': 'WC-QC', 'time_efficiency': 100, 'costs_hour': 1000},
        ]
        
        wc_ids = {}
        for wc in work_centers:
            try:
                existing = models.execute_kw(
                    DB_NAME, uid, PASSWORD,
                    'mrp.workcenter', 'search',
                    [[('code', '=', wc['code'])]]
                )
                
                if not existing:
                    wc_id = models.execute_kw(
                        DB_NAME, uid, PASSWORD,
                        'mrp.workcenter', 'create', [{
                            'name': wc['name'],
                            'code': wc['code'],
                            'costs_hour': wc['costs_hour']
                        }]
                    )
                    wc_ids[wc['code']] = wc_id
                    print(f"  ✅ Создан: {wc['name']}")
                else:
                    wc_ids[wc['code']] = existing[0]
                    print(f"  ℹ️ Уже существует: {wc['name']}")
            except Exception as e:
                print(f"  ❌ Ошибка создания {wc['name']}: {str(e)[:50]}")
        
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
        
        # Функция для получения ID продукта по имени (если код не работает)
        def get_product_by_name(name):
            prod = models.execute_kw(
                DB_NAME, uid, PASSWORD,
                'product.product', 'search',
                [[('name', 'ilike', name)]]
            )
            return prod[0] if prod else None
        
        products = {}
        
        # Сырье
        raw_mapping = {
            'RAW-WHEY': 'Сывороточный протеин',
            'RAW-MALTO': 'Мальтодекстрин',
            'RAW-CREAT': 'Креатин',
            'RAW-BCAA': 'BCAA',
            'RAW-VANIL': 'Ароматизатор Ваниль'
        }
        
        for code, name in raw_mapping.items():
            prod_id = get_product_id(code) or get_product_by_name(name)
            if prod_id:
                products[code] = prod_id
                print(f"  ✅ Найден: {name}")
            else:
                print(f"  ❌ Не найден: {name}")
        
        # Готовая продукция
        finished_mapping = {
            'FIN-WHEY-2KG': 'Whey Protein Ваниль 2кг',
            'FIN-GAIN-3KG': 'Mass Gainer 3кг',
            'FIN-BCAA-300': 'BCAA 300г',
            'FIN-CREAT-500': 'Creatine 500г'
        }
        
        for code, name in finished_mapping.items():
            prod_id = get_product_id(code) or get_product_by_name(name)
            if prod_id:
                products[code] = prod_id
                print(f"  ✅ Найден: {name}")
            else:
                print(f"  ❌ Не найден: {name}")
        
        # СОЗДАНИЕ УПАКОВОЧНЫХ МАТЕРИАЛОВ
        print("\n📦 СОЗДАНИЕ УПАКОВКИ:")
        
        packaging = [
            {'name': 'Банка пластиковая 2кг', 'default_code': 'PACK-2KG', 'standard_price': 45},
            {'name': 'Банка пластиковая 3кг', 'default_code': 'PACK-3KG', 'standard_price': 55},
            {'name': 'Банка пластиковая 300г', 'default_code': 'PACK-300G', 'standard_price': 25},
            {'name': 'Банка пластиковая 500г', 'default_code': 'PACK-500G', 'standard_price': 30},
            {'name': 'Этикетка самоклеящаяся', 'default_code': 'PACK-LABEL', 'standard_price': 3},
            {'name': 'Мерная ложка 30мл', 'default_code': 'PACK-SCOOP', 'standard_price': 5},
        ]
        
        # Получаем категорию Сырье
        raw_cat_ids = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'product.category', 'search',
            [[('name', '=', 'Сырье')]]
        )
        
        if not raw_cat_ids:
            # Создаем категорию если не существует
            raw_cat_id = models.execute_kw(
                DB_NAME, uid, PASSWORD,
                'product.category', 'create',
                [{'name': 'Сырье'}]
            )
        else:
            raw_cat_id = raw_cat_ids[0]
        
        for pack in packaging:
            try:
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
                        'categ_id': raw_cat_id,
                        'uom_id': 1,  # штуки
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
            except Exception as e:
                print(f"  ❌ Ошибка создания {pack['name']}: {str(e)[:50]}")
        
        # СОЗДАНИЕ РЕЦЕПТУР (BOM)
        print("\n📋 СОЗДАНИЕ РЕЦЕПТУР (BOM):")
        
        boms = [
            {
                'name': 'Рецептура: Whey Protein Ваниль 2кг',
                'product_code': 'FIN-WHEY-2KG',
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
                'name': 'Рецептура: Mass Gainer 3кг',
                'product_code': 'FIN-GAIN-3KG',
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
                'name': 'Рецептура: BCAA 300г',
                'product_code': 'FIN-BCAA-300',
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
                'name': 'Рецептура: Creatine 500г',
                'product_code': 'FIN-CREAT-500',
                'product_qty': 1,
                'lines': [
                    ('RAW-CREAT', 0.5),      # Креатин
                    ('PACK-500G', 1),        # Банка
                    ('PACK-LABEL', 1),       # Этикетка
                    ('PACK-SCOOP', 1),       # Ложка
                ]
            }
        ]
        
        created_boms = 0
        for bom_data in boms:
            product_id = products.get(bom_data['product_code'])
            
            if not product_id:
                print(f"  ⚠️ Продукт не найден для {bom_data['name']}")
                continue
            
            try:
                # Проверяем существование BOM
                existing = models.execute_kw(
                    DB_NAME, uid, PASSWORD,
                    'mrp.bom', 'search',
                    [[('product_id', '=', product_id)]]
                )
                
                if existing:
                    print(f"  ℹ️ Уже существует: {bom_data['name']}")
                    continue
                
                # Получаем product_tmpl_id
                product = models.execute_kw(
                    DB_NAME, uid, PASSWORD,
                    'product.product', 'read',
                    [product_id, ['product_tmpl_id']]
                )
                
                # Подготавливаем линии BOM (только те компоненты, которые найдены)
                bom_lines = []
                missing_components = []
                
                for comp_code, qty in bom_data['lines']:
                    comp_id = products.get(comp_code)
                    if comp_id:
                        bom_lines.append((0, 0, {
                            'product_id': comp_id,
                            'product_qty': qty
                        }))
                    else:
                        missing_components.append(comp_code)
                
                if missing_components:
                    print(f"  ⚠️ Не найдены компоненты для {bom_data['name']}: {missing_components}")
                
                if bom_lines:  # Создаем BOM только если есть хотя бы один компонент
                    bom_id = models.execute_kw(
                        DB_NAME, uid, PASSWORD,
                        'mrp.bom', 'create',
                        [{
                            'product_tmpl_id': product[0]['product_tmpl_id'][0],
                            'product_id': product_id,
                            'product_qty': bom_data['product_qty'],
                            'type': 'normal',
                            'bom_line_ids': bom_lines
                        }]
                    )
                    print(f"  ✅ Создана: {bom_data['name']} ({len(bom_lines)} компонентов)")
                    created_boms += 1
                    
            except Exception as e:
                print(f"  ❌ Ошибка создания {bom_data['name']}: {str(e)[:100]}")
        
        # ИТОГОВАЯ ПРОВЕРКА
        print("\n" + "="*60)
        print("📊 ИТОГОВАЯ ПРОВЕРКА:")
        
        # Проверяем созданные рецептуры
        all_boms = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'mrp.bom', 'search_read',
            [[]],
            {'fields': ['display_name', 'product_id', 'bom_line_ids'], 'limit': 20}
        )
        
        print(f"\n✅ Всего рецептур в системе: {len(all_boms)}")
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
        
        # Проверяем все продукты
        all_products = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'product.product', 'search_read',
            [[('type', '=', 'product')]],
            {'fields': ['name', 'default_code'], 'limit': 50}
        )
        
        print(f"\n✅ Всего продуктов: {len(all_products)}")
        
        print("\n" + "="*60)
        print("✅ СИСТЕМА ПРОИЗВОДСТВА НАСТРОЕНА!")
        print("="*60)
        print("\n🎯 Теперь в Odoo можно:")
        print("1. Создать производственный заказ (Производство → Производственные заказы)")
        print("2. Запустить производство продукта")
        print("3. Отслеживать движение по складу")
        print("4. Контролировать себестоимость")
        
        return True
        
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("🏭 СОЗДАНИЕ РЕЦЕПТУР И НАСТРОЙКА ПРОИЗВОДСТВА")
    print("="*60)
    
    create_bom_and_workcenters()
