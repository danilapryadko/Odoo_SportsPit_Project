#!/usr/bin/env python3
"""
Полная синхронизация данных из МойСклад в Odoo
Включает: товары, контрагентов, остатки, цены, категории
"""

import requests
import xmlrpc.client
import ssl
import json
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
        
        # Настройка заголовков для МойСклад
        self.moysklad_headers = {
            'Authorization': f'Bearer {MOYSKLAD_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # Словари для маппинга ID
        self.category_map = {}  # МойСклад ID -> Odoo ID
        self.partner_map = {}   # МойСклад ID -> Odoo ID
        self.product_map = {}   # МойСклад ID -> Odoo ID
        self.warehouse_map = {}  # МойСклад ID -> Odoo ID
        
    def test_connection(self):
        """Тест подключения к МойСклад"""
        try:
            response = requests.get(
                f"{MOYSKLAD_BASE_URL}/context/companysettings",
                headers=self.moysklad_headers
            )
            
            if response.status_code == 200:
                print("✅ Подключено к МойСклад")
                return True
            else:
                print(f"❌ Ошибка МойСклад: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False
    
    def get_all_data_stats(self):
        """Получение статистики по всем данным в МойСклад"""
        print("\n📊 АНАЛИЗ ДАННЫХ В МОЙСКЛАД:")
        print("="*50)
        
        entities = [
            ('product', 'Товары'),
            ('variant', 'Модификации'),
            ('counterparty', 'Контрагенты'),
            ('organization', 'Организации'),
            ('store', 'Склады'),
            ('productfolder', 'Группы товаров'),
            ('supply', 'Приемки'),
            ('customerorder', 'Заказы покупателей'),
            ('purchaseorder', 'Заказы поставщикам'),
            ('invoicein', 'Счета поставщиков'),
            ('invoiceout', 'Счета покупателей'),
        ]
        
        stats = {}
        for entity, name in entities:
            try:
                response = requests.get(
                    f"{MOYSKLAD_BASE_URL}/entity/{entity}",
                    headers=self.moysklad_headers,
                    params={'limit': 1}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    count = data.get('meta', {}).get('size', 0)
                    stats[entity] = count
                    if count > 0:
                        print(f"  • {name:20} : {count:6} записей")
            except:
                pass
        
        return stats
    
    def sync_product_folders(self):
        """Синхронизация групп товаров (категорий)"""
        print("\n📁 СИНХРОНИЗАЦИЯ КАТЕГОРИЙ ТОВАРОВ:")
        print("-"*40)
        
        response = requests.get(
            f"{MOYSKLAD_BASE_URL}/entity/productfolder",
            headers=self.moysklad_headers,
            params={'limit': 1000}
        )
        
        if response.status_code != 200:
            print("❌ Не удалось получить категории")
            return
        
        folders = response.json().get('rows', [])
        
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
        """Синхронизация контрагентов (поставщики и покупатели)"""
        print("\n👥 СИНХРОНИЗАЦИЯ КОНТРАГЕНТОВ:")
        print("-"*40)
        
        offset = 0
        limit = 100
        total_created = 0
        
        while True:
            response = requests.get(
                f"{MOYSKLAD_BASE_URL}/entity/counterparty",
                headers=self.moysklad_headers,
                params={
                    'limit': limit,
                    'offset': offset,
                    'expand': 'tags'
                }
            )
            
            if response.status_code != 200:
                break
            
            data = response.json()
            counterparties = data.get('rows', [])
            
            if not counterparties:
                break
            
            for cp in counterparties:
                ms_id = cp['id']
                
                # Подготавливаем данные
                partner_data = {
                    'name': cp.get('name', 'Без названия'),
                    'is_company': cp.get('companyType') == 'legal',
                    'supplier_rank': 1 if 'supplier' in str(cp.get('tags', [])).lower() else 0,
                    'customer_rank': 1 if 'customer' in str(cp.get('tags', [])).lower() or 'покупатель' in str(cp.get('tags', [])).lower() else 1,
                    'phone': cp.get('phone', ''),
                    'email': cp.get('email', ''),
                    'website': cp.get('site', ''),
                    'comment': cp.get('description', ''),
                    'vat': cp.get('inn', ''),
                }
                
                # Добавляем адрес если есть
                if cp.get('actualAddress'):
                    partner_data['street'] = cp['actualAddress']
                
                # Проверяем существование по ИНН или названию
                domain = []
                if partner_data['vat']:
                    domain = [('vat', '=', partner_data['vat'])]
                else:
                    domain = [('name', '=', partner_data['name'])]
                
                existing = self.odoo_models.execute_kw(
                    DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                    'res.partner', 'search', [domain]
                )
                
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
            
            offset += limit
            
            # Ограничение для теста
            if offset >= 200:
                print("\n  ⚠️ Импортировано 200 контрагентов (тестовый режим)")
                break
        
        print(f"\n  Итого контрагентов: {len(self.partner_map)}")
        print(f"  Создано новых: {total_created}")
    
    def sync_warehouses(self):
        """Синхронизация складов"""
        print("\n🏭 СИНХРОНИЗАЦИЯ СКЛАДОВ:")
        print("-"*40)
        
        response = requests.get(
            f"{MOYSKLAD_BASE_URL}/entity/store",
            headers=self.moysklad_headers
        )
        
        if response.status_code != 200:
            print("❌ Не удалось получить склады")
            return
        
        stores = response.json().get('rows', [])
        
        for store in stores:
            ms_id = store['id']
            name = store['name']
            
            # Проверяем существование
            existing = self.odoo_models.execute_kw(
                DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                'stock.warehouse', 'search',
                [[('name', '=', name)]]
            )
            
            if existing:
                wh_id = existing[0]
                print(f"  ℹ️ Существует: {name}")
            else:
                # Создаем склад
                wh_data = {
                    'name': name,
                    'code': store.get('code', name[:5].upper())
                }
                
                try:
                    wh_id = self.odoo_models.execute_kw(
                        DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                        'stock.warehouse', 'create', [wh_data]
                    )
                    print(f"  ✅ Создан склад: {name}")
                except Exception as e:
                    print(f"  ❌ Ошибка создания склада {name}: {str(e)[:50]}")
                    continue
            
            self.warehouse_map[ms_id] = wh_id
        
        print(f"\n  Итого складов: {len(self.warehouse_map)}")
    
    def sync_products(self):
        """Синхронизация товаров"""
        print("\n📦 СИНХРОНИЗАЦИЯ ТОВАРОВ:")
        print("-"*40)
        
        offset = 0
        limit = 100
        total_created = 0
        total_updated = 0
        
        while True:
            response = requests.get(
                f"{MOYSKLAD_BASE_URL}/entity/product",
                headers=self.moysklad_headers,
                params={
                    'limit': limit,
                    'offset': offset,
                    'expand': 'productFolder,supplier,salePrices,buyPrice,barcodes,images'
                }
            )
            
            if response.status_code != 200:
                break
            
            data = response.json()
            products = data.get('rows', [])
            
            if not products:
                break
            
            for product in products:
                ms_id = product['id']
                
                # Определяем категорию
                category_id = 1  # По умолчанию
                if product.get('productFolder'):
                    folder_id = product['productFolder']['meta']['href'].split('/')[-1]
                    category_id = self.category_map.get(folder_id, 1)
                
                # Получаем поставщика
                supplier_id = False
                if product.get('supplier'):
                    supplier_ms_id = product['supplier']['meta']['href'].split('/')[-1]
                    supplier_id = self.partner_map.get(supplier_ms_id)
                
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
                    'weight': product.get('weight', 0) / 1000 if product.get('weight') else 0,  # Переводим в кг
                    'volume': product.get('volume', 0) / 1000000 if product.get('volume') else 0,  # Переводим в м³
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
                
                # НДС
                if product.get('vat'):
                    product_data['taxes_id'] = [(6, 0, [])]  # Очищаем налоги, потом добавим
                
                # Проверяем существование
                existing = []
                if product_data['default_code']:
                    existing = self.odoo_models.execute_kw(
                        DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                        'product.product', 'search',
                        [[('default_code', '=', product_data['default_code'])]]
                    )
                
                if not existing and product_data['barcode']:
                    existing = self.odoo_models.execute_kw(
                        DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                        'product.product', 'search',
                        [[('barcode', '=', product_data['barcode'])]]
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
                    
                    # Добавляем поставщика
                    if supplier_id and product_id:
                        try:
                            # Создаем запись о поставщике товара
                            self.odoo_models.execute_kw(
                                DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                                'product.supplierinfo', 'create',
                                [{
                                    'partner_id': supplier_id,
                                    'product_tmpl_id': self.odoo_models.execute_kw(
                                        DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                                        'product.product', 'read',
                                        [product_id, ['product_tmpl_id']]
                                    )[0]['product_tmpl_id'][0],
                                    'price': product_data['standard_price'],
                                    'delay': 1,
                                }]
                            )
                        except:
                            pass
                    
                except Exception as e:
                    print(f"  ❌ Ошибка с товаром {product_data['name']}: {str(e)[:50]}")
            
            offset += limit
            
            # Показываем прогресс
            if offset % 500 == 0:
                print(f"\n  Обработано: {offset} товаров...")
            
            # Ограничение для теста
            if offset >= 1000:
                print("\n  ⚠️ Импортировано 1000 товаров (тестовый режим)")
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
        response = requests.get(
            f"{MOYSKLAD_BASE_URL}/report/stock/all",
            headers=self.moysklad_headers,
            params={'limit': 1000}
        )
        
        if response.status_code != 200:
            print("❌ Не удалось получить остатки")
            return
        
        stocks = response.json().get('rows', [])
        updated_count = 0
        
        print(f"  Найдено остатков: {len(stocks)}")
        
        for stock in stocks[:100]:  # Ограничение для теста
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
                        # Создаем инвентаризацию для обновления остатка
                        inventory_id = self.odoo_models.execute_kw(
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
                    except:
                        # Если quant существует, обновляем
                        try:
                            existing_quant = self.odoo_models.execute_kw(
                                DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                                'stock.quant', 'search',
                                [[
                                    ('product_id', '=', odoo_product_id),
                                    ('location_id', '=', main_location_id)
                                ]]
                            )
                            
                            if existing_quant:
                                self.odoo_models.execute_kw(
                                    DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                                    'stock.quant', 'write',
                                    [existing_quant[0], {'quantity': qty}]
                                )
                                updated_count += 1
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
        self.sync_product_folders()  # Сначала категории
        self.sync_counterparties()   # Потом контрагенты
        self.sync_warehouses()       # Склады
        self.sync_products()         # Товары
        self.sync_stock()           # Остатки
        
        print("\n" + "="*60)
        print("✅ СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА!")
        print("="*60)
        
        print("\n📊 ИТОГОВАЯ СТАТИСТИКА:")
        print(f"  • Категорий: {len(self.category_map)}")
        print(f"  • Контрагентов: {len(self.partner_map)}")
        print(f"  • Складов: {len(self.warehouse_map)}")
        print(f"  • Товаров: {len(self.product_map)}")
        
        print("\n🎯 ЧТО ДАЛЬШЕ:")
        print("1. Проверьте импортированные данные в Odoo")
        print("2. Настройте правила ценообразования")
        print("3. Проверьте остатки на складах")
        print("4. Настройте автоматическую синхронизацию")

def main():
    print("="*60)
    print("🔄 ПОЛНАЯ СИНХРОНИЗАЦИЯ МОЙСКЛАД → ODOO")
    print("="*60)
    print("\n⚠️ Это импортирует ВСЕ данные из МойСклад:")
    print("  • Товары и категории")
    print("  • Контрагентов (поставщиков и покупателей)")
    print("  • Склады")
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
