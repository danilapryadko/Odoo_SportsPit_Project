#!/usr/bin/env python3
"""
Перенос товаров из МойСклад в Odoo
"""

import requests
import xmlrpc.client
import ssl
import json
from datetime import datetime

# === НАСТРОЙКИ МОЙСКЛАД ===
# Вам нужно будет указать свои данные
MOYSKLAD_LOGIN = "admin@company"  # Ваш логин в МойСклад
MOYSKLAD_PASSWORD = "password"     # Ваш пароль в МойСклад
MOYSKLAD_BASE_URL = "https://api.moysklad.ru/api/remap/1.2"

# === НАСТРОЙКИ ODOO ===
ODOO_URL = "https://odoosportspitproject-production.up.railway.app"
DB_NAME = "odoo_sportpit"
ODOO_LOGIN = "danila@usafitandjoy.com"
ODOO_PASSWORD = "admin123"

class MoySkladToOdoo:
    def __init__(self):
        """Инициализация подключений"""
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
        
        # Сессия для МойСклад
        self.moysklad_session = requests.Session()
        self.moysklad_session.auth = (MOYSKLAD_LOGIN, MOYSKLAD_PASSWORD)
        
    def test_moysklad_connection(self):
        """Тест подключения к МойСклад"""
        try:
            response = self.moysklad_session.get(f"{MOYSKLAD_BASE_URL}/entity/product")
            if response.status_code == 200:
                print("✅ Подключено к МойСклад")
                return True
            else:
                print(f"❌ Ошибка МойСклад: {response.status_code}")
                print(f"Ответ: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Не удалось подключиться к МойСклад: {e}")
            return False
    
    def get_moysklad_products(self):
        """Получение товаров из МойСклад"""
        print("\n📦 Получение товаров из МойСклад...")
        
        products = []
        offset = 0
        limit = 100
        
        while True:
            response = self.moysklad_session.get(
                f"{MOYSKLAD_BASE_URL}/entity/product",
                params={'limit': limit, 'offset': offset}
            )
            
            if response.status_code != 200:
                print(f"❌ Ошибка получения товаров: {response.status_code}")
                break
            
            data = response.json()
            rows = data.get('rows', [])
            
            if not rows:
                break
                
            products.extend(rows)
            
            # Проверяем, есть ли еще товары
            if len(rows) < limit:
                break
                
            offset += limit
        
        print(f"✅ Найдено товаров в МойСклад: {len(products)}")
        return products
    
    def get_moysklad_variants(self):
        """Получение модификаций товаров из МойСклад"""
        print("\n📦 Получение модификаций из МойСклад...")
        
        variants = []
        offset = 0
        limit = 100
        
        while True:
            response = self.moysklad_session.get(
                f"{MOYSKLAD_BASE_URL}/entity/variant",
                params={'limit': limit, 'offset': offset}
            )
            
            if response.status_code != 200:
                break
            
            data = response.json()
            rows = data.get('rows', [])
            
            if not rows:
                break
                
            variants.extend(rows)
            
            if len(rows) < limit:
                break
                
            offset += limit
        
        print(f"✅ Найдено модификаций: {len(variants)}")
        return variants
    
    def get_moysklad_stock(self):
        """Получение остатков из МойСклад"""
        print("\n📊 Получение остатков...")
        
        response = self.moysklad_session.get(
            f"{MOYSKLAD_BASE_URL}/report/stock/all"
        )
        
        if response.status_code == 200:
            data = response.json()
            stocks = data.get('rows', [])
            print(f"✅ Получено остатков: {len(stocks)}")
            return stocks
        else:
            print(f"❌ Ошибка получения остатков: {response.status_code}")
            return []
    
    def create_odoo_category(self, name):
        """Создание категории в Odoo"""
        # Проверяем существование
        existing = self.odoo_models.execute_kw(
            DB_NAME, self.odoo_uid, ODOO_PASSWORD,
            'product.category', 'search',
            [[('name', '=', name)]]
        )
        
        if existing:
            return existing[0]
        
        # Создаем новую
        cat_id = self.odoo_models.execute_kw(
            DB_NAME, self.odoo_uid, ODOO_PASSWORD,
            'product.category', 'create',
            [{'name': name}]
        )
        return cat_id
    
    def create_odoo_product(self, moysklad_product):
        """Создание товара в Odoo на основе данных МойСклад"""
        
        # Определяем категорию
        category_name = "Импорт из МойСклад"
        if moysklad_product.get('productFolder'):
            # Получаем папку товара
            folder_url = moysklad_product['productFolder']['meta']['href']
            folder_response = self.moysklad_session.get(folder_url)
            if folder_response.status_code == 200:
                folder_data = folder_response.json()
                category_name = folder_data.get('name', category_name)
        
        category_id = self.create_odoo_category(category_name)
        
        # Подготавливаем данные товара
        product_data = {
            'name': moysklad_product.get('name', 'Без названия'),
            'default_code': moysklad_product.get('code', moysklad_product.get('article', '')),
            'barcode': moysklad_product.get('barcodes', [{}])[0].get('ean13') if moysklad_product.get('barcodes') else None,
            'type': 'product',
            'categ_id': category_id,
            'sale_ok': True,
            'purchase_ok': True,
            'list_price': 0,  # Цену получим отдельно
            'standard_price': 0,  # Себестоимость получим отдельно
            'description': moysklad_product.get('description', ''),
            'uom_id': 1,  # Единица измерения (штуки по умолчанию)
        }
        
        # Получаем цены
        if moysklad_product.get('salePrices'):
            for price in moysklad_product['salePrices']:
                if price.get('priceType', {}).get('name') == 'Цена продажи':
                    product_data['list_price'] = price.get('value', 0) / 100  # МойСклад хранит в копейках
                    break
        
        if moysklad_product.get('buyPrice'):
            product_data['standard_price'] = moysklad_product['buyPrice'].get('value', 0) / 100
        
        # Проверяем существование товара по артикулу
        if product_data['default_code']:
            existing = self.odoo_models.execute_kw(
                DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                'product.product', 'search',
                [[('default_code', '=', product_data['default_code'])]]
            )
            
            if existing:
                # Обновляем существующий
                self.odoo_models.execute_kw(
                    DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                    'product.product', 'write',
                    [existing[0], product_data]
                )
                return existing[0]
        
        # Создаем новый товар
        try:
            product_id = self.odoo_models.execute_kw(
                DB_NAME, self.odoo_uid, ODOO_PASSWORD,
                'product.product', 'create',
                [product_data]
            )
            return product_id
        except Exception as e:
            print(f"  ❌ Ошибка создания товара {product_data['name']}: {str(e)[:50]}")
            return None
    
    def sync_products(self):
        """Основная функция синхронизации"""
        print("\n" + "="*60)
        print("🔄 СИНХРОНИЗАЦИЯ ТОВАРОВ")
        print("="*60)
        
        # Получаем товары из МойСклад
        moysklad_products = self.get_moysklad_products()
        moysklad_variants = self.get_moysklad_variants()
        
        # Обрабатываем товары
        created_count = 0
        updated_count = 0
        
        print("\n📝 Перенос товаров в Odoo...")
        
        # Переносим основные товары
        for product in moysklad_products:
            result = self.create_odoo_product(product)
            if result:
                created_count += 1
                print(f"  ✅ {product.get('name', 'Без названия')}")
            
            # Ограничение для теста (уберите для полного импорта)
            if created_count >= 10:
                print("\n⚠️ Импортировано 10 товаров для теста")
                print("Уберите ограничение в коде для полного импорта")
                break
        
        # Переносим модификации
        for variant in moysklad_variants[:10]:  # Ограничение для теста
            result = self.create_odoo_product(variant)
            if result:
                created_count += 1
                print(f"  ✅ {variant.get('name', 'Без названия')}")
        
        print("\n" + "="*60)
        print(f"✅ СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА")
        print(f"  Создано/обновлено товаров: {created_count}")
        print("="*60)
        
        # Получаем и показываем остатки
        stocks = self.get_moysklad_stock()
        if stocks:
            print("\n📊 Остатки товаров (первые 5):")
            for stock in stocks[:5]:
                print(f"  • {stock.get('name', 'Без названия')}: {stock.get('stock', 0)} шт")

def main():
    print("="*60)
    print("🔄 ИНТЕГРАЦИЯ МОЙСКЛАД → ODOO")
    print("="*60)
    
    print("\n⚠️ ВАЖНО: Укажите ваши данные МойСклад в скрипте:")
    print("  - MOYSKLAD_LOGIN = 'ваш_логин'")
    print("  - MOYSKLAD_PASSWORD = 'ваш_пароль'")
    
    # Запрашиваем данные у пользователя
    print("\nВведите данные МойСклад:")
    login = input("Логин (email): ").strip()
    password = input("Пароль: ").strip()
    
    if not login or not password:
        print("❌ Необходимо указать логин и пароль")
        return
    
    # Обновляем глобальные переменные
    global MOYSKLAD_LOGIN, MOYSKLAD_PASSWORD
    MOYSKLAD_LOGIN = login
    MOYSKLAD_PASSWORD = password
    
    try:
        # Создаем экземпляр и синхронизируем
        syncer = MoySkladToOdoo()
        
        if syncer.test_moysklad_connection():
            syncer.sync_products()
        else:
            print("\n❌ Не удалось подключиться к МойСклад")
            print("Проверьте логин и пароль")
            
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
