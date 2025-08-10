#!/usr/bin/env python3
"""
Полная синхронизация данных из МойСклад в Odoo
БЕЗ внешних библиотек - используем только urllib
"""

import urllib.request
import urllib.parse
import xmlrpc.client
import ssl
import json
import base64
from datetime import datetime

# === НАСТРОЙКИ МОЙСКЛАД ===
MOYSKLAD_TOKEN = "7bbede5c5ac9c28ddf7995042fcbbe1fecb274e1"
MOYSKLAD_BASE_URL = "https://api.moysklad.ru/api/remap/1.2"

# === НАСТРОЙКИ ODOO ===
ODOO_URL = "https://odoosportspitproject-production.up.railway.app"
DB_NAME = "odoo_sportpit"
ODOO_LOGIN = "danila@usafitandjoy.com"
ODOO_PASSWORD = "admin123"

class MoySkladFullSync:
    def __init__(self):
        """Инициализация подключений"""
        print("🔌 Подключение к системам...")
        
        # Подключение к Odoo
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        self.odoo_common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common', context=ssl_context)
        self.odoo_uid = self.odoo_common.authenticate(DB_NAME, ODOO_LOGIN, ODOO_PASSWORD, {})
        
        if self.odoo_uid:
            print("✅ Подключено к Odoo")
            self.odoo_models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object', context=ssl_context)
        else:
            raise Exception("❌ Не удалось подключиться к Odoo")
        
        # Словари для маппинга ID
        self.category_map = {}  # МойСклад ID -> Odoo ID
        self.partner_map = {}   # МойСклад ID -> Odoo ID
        self.product_map = {}   # МойСклад ID -> Odoo ID
        self.warehouse_map = {}  # МойСклад ID -> Odoo ID
    
    def moysklad_request(self, endpoint, params=None):
        """Выполнение запроса к API МойСклад"""
        # Формируем URL
        url = f"{MOYSKLAD_BASE_URL}/{endpoint}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        
        # Создаем запрос с токеном
        request = urllib.request.Request(url)
        request.add_header('Authorization', f'Bearer {MOYSKLAD_TOKEN}')
        request.add_header('Accept', 'application/json;charset=utf-8')
        
        try:
            # Выполняем запрос
            with urllib.request.urlopen(request) as response:
                data = response.read()
                return json.loads(data.decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print("❌ Ошибка авторизации в МойСклад. Проверьте токен.")
            else:
                print(f"❌ Ошибка HTTP {e.code}: {e.reason}")
            return None
        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")
            return None
    
    def test_connection(self):
        """Тест подключения к МойСклад"""
        print("\n🔍 Проверка подключения к МойСклад...")
        result = self.moysklad_request("context/companysettings")
        
        if result:
            print("✅ Подключено к МойСклад")
            if 'name' in result:
                print(f"   Организация: {result['name']}")
            return True
        return False
    
    def get_all_data_stats(self):
        """Получение статистики по всем данным в МойСклад"""
        print("\n📊 АНАЛИЗ ДАННЫХ В МОЙСКЛАД:")
        print("="*50)
        
        entities = [
            ('entity/product', 'Товары'),
            ('entity/variant', 'Модификации'),
            ('entity/counterparty', 'Контрагенты'),
            ('entity/organization', 'Организации'),
            ('entity/store', 'Склады'),
            ('entity/productfolder', 'Группы товаров'),
            ('entity/supply', 'Приемки'),
            ('entity/customerorder', 'Заказы покупателей'),
        ]
        
        stats = {}
        for endpoint, name in entities:
            result = self.moysklad_request(endpoint, {'limit': 1})
            if result and 'meta' in result:
                count = result['meta'].get('size', 0)
                stats[endpoint] = count
                if count > 0:
                    print(f"  • {name:20} : {count:6} записей")
        
        return stats
    
    def sync_product_folders(self):
        """Синхронизация групп товаров (категорий)"""
        print("\n📁 СИНХРОНИЗАЦИЯ КАТЕГОРИЙ ТОВАРОВ:")
        print("-"*40)
        
        result = self.moysklad_request("entity/productfolder", {'limit': 1000})
        
        if not result or 'rows' not in result:
            print("❌ Не удалось получить категории")
            return
        
        folders = result['rows']
        
        for folder in folders:
            ms_id = folder['id']
            name = folder['name']
            
            # Проверяем существование
            existing = self.odoo_models.execute_kw(
                DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                'product.category', 'search',
                [[('name', '=', name)]]
            )
            
            if existing:
                cat_id = existing[0]
                print(f"  ℹ️ Существует: {name}")
            else:
                # Создаем категорию
                parent_id = False
                if folder.get('productFolder'):
                    parent_ms_id = folder['productFolder']['meta']['href'].split('/')[-1]
                    parent_id = self.category_map.get(parent_ms_id)
                
                cat_id = self.odoo_models.execute_kw(
                    DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                    'product.category', 'create',
                    [{
                        'name': name,
                        'parent_id': parent_id if parent_id else False
                    }]
                )
                print(f"  ✅ Создана: {name}")
            
            self.category_map[ms_id] = cat_id
        
        print(f"\n  Итого категорий: {len(self.category_map)}")
    
    def sync_counterparties(self):
        """Синхронизация контрагентов"""
        print("\n👥 СИНХРОНИЗАЦИЯ КОНТРАГЕНТОВ:")
        print("-"*40)
        
        offset = 0
        limit = 100
        total_created = 0
        
        while True:
            result = self.moysklad_request("entity/counterparty", {
                'limit': limit,
                'offset': offset,
                'expand': 'tags'
            })
            
            if not result or 'rows' not in result:
                break
            
            counterparties = result['rows']
            
            if not counterparties:
                break
            
            for cp in counterparties:
                ms_id = cp['id']
                
                # Подготавливаем данные
                partner_data = {
                    'name': cp.get('name', 'Без названия'),
                    'is_company': cp.get('companyType') == 'legal',
                    'supplier_rank': 1,
                    'customer_rank': 1,
                    'phone': cp.get('phone', ''),
                    'email': cp.get('email', ''),
                    'website': cp.get('site', ''),
                    'comment': cp.get('description', ''),
                    'vat': cp.get('inn', ''),
                }
                
                # Добавляем адрес если есть
                if cp.get('actualAddress'):
                    partner_data['street'] = cp['actualAddress']
                
                # Проверяем существование
                domain = []
                if partner_data['vat']:
                    domain = [('vat', '=', partner_data['vat'])]
                else:
                    domain = [('name', '=', partner_data['name'])]
                
                existing = self.odoo_models.execute_kw(
                    DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                    'res.partner', 'search', [domain]
                )
                
                try:
                    if existing:
                        partner_id = existing[0]
                        # Обновляем
                        self.odoo_models.execute_kw(
                            DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                            'res.partner', 'write',
                            [partner_id, partner_data]
                        )
                        print(f"  📝 Обновлен: {partner_data['name']}")
                    else:
                        # Создаем
                        partner_id = self.odoo_models.execute_kw(
                            DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                            'res.partner', 'create', [partner_data]
                        )
                        print(f"  ✅ Создан: {partner_data['name']}")
                        total_created += 1
                    
                    self.partner_map[ms_id] = partner_id
                except Exception as e:
                    print(f"  ❌ Ошибка с {partner_data['name']}: {str(e)[:50]}")
            
            offset += limit
            
            # Ограничение для теста
            if offset >= 100:
                print("\n  ⚠️ Импортировано 100 контрагентов (тестовый режим)")
                break
        
        print(f"\n  Итого контрагентов: {len(self.partner_map)}")
        print(f"  Создано новых: {total_created}")
    
    def sync_products(self):
        """Синхронизация товаров"""
        print("\n📦 СИНХРОНИЗАЦИЯ ТОВАРОВ:")
        print("-"*40)
        
        offset = 0
        limit = 50
        total_created = 0
        total_updated = 0
        
        while True:
            result = self.moysklad_request("entity/product", {
                'limit': limit,
                'offset': offset,
                'expand': 'productFolder,salePrices,buyPrice'
            })
            
            if not result or 'rows' not in result:
                break
            
            products = result['rows']
            
            if not products:
                break
            
            for product in products:
                ms_id = product['id']
                
                # Определяем категорию
                category_id = 1  # По умолчанию
                if product.get('productFolder'):
                    folder_id = product['productFolder']['meta']['href'].split('/')[-1]
                    category_id = self.category_map.get(folder_id, 1)
                
                # Подготавливаем данные товара
                product_data = {
                    'name': product.get('name', 'Без названия'),
                    'default_code': product.get('code', product.get('article', '')),
                    'barcode': None,
                    'type': 'product',
                    'categ_id': category_id,
                    'sale_ok': not product.get('archived', False),
                    'purchase_ok': not product.get('archived', False),
                    'list_price': 0,
                    'standard_price': 0,
                    'description': product.get('description', ''),
                }
                
                # Штрихкоды
                if product.get('barcodes'):
                    barcodes = product['barcodes']
                    if barcodes and len(barcodes) > 0:
                        product_data['barcode'] = barcodes[0].get('ean13') or barcodes[0].get('ean8')
                
                # Цены
                if product.get('salePrices'):
                    for price in product['salePrices']:
                        if price.get('priceType', {}).get('name') in ['Цена продажи', 'Розничная цена']:
                            product_data['list_price'] = price.get('value', 0) / 100
                            break
                
                if product.get('buyPrice'):
                    product_data['standard_price'] = product['buyPrice'].get('value', 0) / 100
                
                # Проверяем существование
                existing = []
                if product_data['default_code']:
                    existing = self.odoo_models.execute_kw(
                        DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                        'product.product', 'search',
                        [[('default_code', '=', product_data['default_code'])]]
                    )
                
                try:
                    if existing:
                        # Обновляем
                        self.odoo_models.execute_kw(
                            DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                            'product.product', 'write',
                            [existing[0], product_data]
                        )
                        product_id = existing[0]
                        total_updated += 1
                        print(f"  📝 Обновлен: {product_data['name']}")
                    else:
                        # Создаем
                        product_id = self.odoo_models.execute_kw(
                            DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                            'product.product', 'create', [product_data]
                        )
                        total_created += 1
                        print(f"  ✅ Создан: {product_data['name']}")
                    
                    self.product_map[ms_id] = product_id
                    
                except Exception as e:
                    print(f"  ❌ Ошибка с товаром {product_data['name']}: {str(e)[:50]}")
            
            offset += limit
            
            # Показываем прогресс
            if offset % 200 == 0 and offset > 0:
                print(f"\n  Обработано: {offset} товаров...")
            
            # Ограничение для теста
            if offset >= 200:
                print("\n  ⚠️ Импортировано 200 товаров (тестовый режим)")
                break
        
        print(f"\n  Итого товаров обработано: {len(self.product_map)}")
        print(f"  Создано новых: {total_created}")
        print(f"  Обновлено: {total_updated}")
    
    def sync_stock(self):
        """Синхронизация остатков"""
        print("\n📊 СИНХРОНИЗАЦИЯ ОСТАТКОВ:")
        print("-"*40)
        
        # Получаем основной склад Odoo
        main_warehouse = self.odoo_models.execute_kw(
            DB_NAME, self.odoo_uid, ODOO_PASSWORD,
            'stock.warehouse', 'search',
            [[], 0, 1]
        )
        
        if not main_warehouse:
            print("❌ Не найден склад в Odoo")
            return
        
        main_wh = self.odoo_models.execute_kw(
            DB_NAME, self.odoo_uid, ODOO_PASSWORD,
            'stock.warehouse', 'read',
            [main_warehouse[0], ['lot_stock_id']]
        )[0]
        
        main_location_id = main_wh['lot_stock_id'][0]
        
        # Получаем остатки из МойСклад
        result = self.moysklad_request("report/stock/all", {'limit': 1000})
        
        if not result or 'rows' not in result:
            print("❌ Не удалось получить остатки")
            return
        
        stocks = result['rows']
        updated_count = 0
        
        print(f"  Найдено остатков: {len(stocks)}")
        
        for stock in stocks[:50]:  # Ограничение для теста
            # Получаем ID товара в Odoo
            ms_product_id = stock['meta']['href'].split('/')[-1]
            odoo_product_id = self.product_map.get(ms_product_id)
            
            if not odoo_product_id:
                # Пробуем найти по артикулу
                if stock.get('code'):
                    existing = self.odoo_models.execute_kw(
                        DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                        'product.product', 'search',
                        [[('default_code', '=', stock['code'])]]
                    )
                    if existing:
                        odoo_product_id = existing[0]
            
            if odoo_product_id:
                qty = stock.get('stock', 0)
                
                if qty > 0:
                    try:
                        # Проверяем существующий quant
                        existing_quant = self.odoo_models.execute_kw(
                            DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                            'stock.quant', 'search',
                            [[
                                ('product_id', '=', odoo_product_id),
                                ('location_id', '=', main_location_id)
                            ]]
                        )
                        
                        if existing_quant:
                            # Обновляем
                            self.odoo_models.execute_kw(
                                DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                                'stock.quant', 'write',
                                [existing_quant[0], {'quantity': qty}]
                            )
                        else:
                            # Создаем
                            self.odoo_models.execute_kw(
                                DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                                'stock.quant', 'create',
                                [{
                                    'product_id': odoo_product_id,
                                    'location_id': main_location_id,
                                    'quantity': qty,
                                }]
                            )
                        
                        updated_count += 1
                        print(f"    ✅ {stock.get('name', 'Товар')}: {qty} шт")
                        
                    except Exception as e:
                        print(f"    ❌ Ошибка обновления остатка: {str(e)[:50]}")
        
        print(f"\n  Обновлено остатков: {updated_count}")
    
    def run_full_sync(self):
        """Запуск полной синхронизации"""
        print("\n" + "="*60)
        print("🚀 ЗАПУСК ПОЛНОЙ СИНХРОНИЗАЦИИ")
        print("="*60)
        
        if not self.test_connection():
            print("\n❌ Не удалось подключиться к МойСклад")
            print("Проверьте токен API")
            return
        
        # Показываем статистику
        stats = self.get_all_data_stats()
        
        print("\n" + "="*60)
        print("📥 НАЧАЛО ИМПОРТА ДАННЫХ")
        print("="*60)
        
        # Порядок важен!
        self.sync_product_folders()  # Категории
        self.sync_counterparties()   # Контрагенты
        self.sync_products()         # Товары
        self.sync_stock()           # Остатки
        
        print("\n" + "="*60)
        print("✅ СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА!")
        print("="*60)
        
        print("\n📊 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"  • Категорий: {len(self.category_map)}")
        print(f"  • Контрагентов: {len(self.partner_map)}")
        print(f"  • Товаров: {len(self.product_map)}")
        
        print("\n🎯 ЧТО ДАЛЬШЕ:")
        print("1. Проверьте импортированные данные в Odoo")
        print("2. Настройте правила ценообразования")
        print("3. Проверьте остатки на складах")

def main():
    print("="*60)
    print("🔄 ПОЛНАЯ СИНХРОНИЗАЦИЯ МОЙСКЛАД → ODOO")
    print("="*60)
    print("\n⚠️ Это импортирует данные из МойСклад:")
    print("  • Товары и категории")
    print("  • Контрагентов")
    print("  • Остатки товаров")
    print("  • Цены")
    
    confirm = input("\n❓ Начать импорт? (да/нет): ").strip().lower()
    
    if confirm in ['да', 'yes', 'y', 'д']:
        try:
            syncer = MoySkladFullSync()
            syncer.run_full_sync()
        except Exception as e:
            print(f"\n❌ Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n❌ Импорт отменен")

if __name__ == "__main__":
    main()
