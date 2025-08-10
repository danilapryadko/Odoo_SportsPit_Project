#!/usr/bin/env python3
"""
Создание простого планировщика производства используя стандартные возможности
"""

import xmlrpc.client
import ssl
from datetime import datetime, timedelta

ODOO_URL = "https://odoosportspitproject-production.up.railway.app"
DB_NAME = "odoo_sportpit"
LOGIN = "danila@usafitandjoy.com"
PASSWORD = "admin123"

def create_production_schedule():
    """Создание расписания производства на неделю"""
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common', context=ssl_context)
        uid = common.authenticate(DB_NAME, LOGIN, PASSWORD, {})
        
        if not uid:
            print("❌ Не удалось войти")
            return False
            
        print(f"✅ Подключено")
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object', context=ssl_context)
        
        print("\n📅 СОЗДАНИЕ ПЛАНА ПРОИЗВОДСТВА НА НЕДЕЛЮ:")
        print("="*50)
        
        # Получаем продукты для производства
        products = models.execute_kw(
            DB_NAME, uid, PASSWORD,
            'product.product', 'search_read',
            [[('name', 'in', ['Whey Protein Ваниль 2кг', 'Mass Gainer 3кг', 'BCAA 300г', 'Creatine 500г'])]],
            {'fields': ['id', 'name']}
        )
        
        if not products:
            print("❌ Продукты не найдены")
            return False
        
        # План производства на неделю
        production_plan = [
            {'day': 'Понедельник', 'product': 'Whey Protein Ваниль 2кг', 'qty': 50},
            {'day': 'Вторник', 'product': 'Mass Gainer 3кг', 'qty': 30},
            {'day': 'Среда', 'product': 'BCAA 300г', 'qty': 100},
            {'day': 'Четверг', 'product': 'Creatine 500г', 'qty': 80},
            {'day': 'Пятница', 'product': 'Whey Protein Ваниль 2кг', 'qty': 50},
        ]
        
        # Создаем производственные заказы
        start_date = datetime.now()
        
        for i, plan in enumerate(production_plan):
            # Находим продукт
            product = next((p for p in products if plan['product'] in p['name']), None)
            
            if product:
                # Дата производства
                production_date = start_date + timedelta(days=i)
                
                # Создаем производственный заказ
                try:
                    mo_id = models.execute_kw(
                        DB_NAME, uid, PASSWORD,
                        'mrp.production', 'create',
                        [{
                            'product_id': product['id'],
                            'product_qty': plan['qty'],
                            'date_start': production_date.strftime('%Y-%m-%d 08:00:00'),
                            'date_finished': production_date.strftime('%Y-%m-%d 18:00:00'),
                            'name': f"MO/{plan['day'][:3]}/{product['name'][:10]}",
                        }]
                    )
                    
                    print(f"✅ {plan['day']:12} | {plan['product']:25} | {plan['qty']:3} шт")
                    
                except Exception as e:
                    print(f"⚠️ {plan['day']:12} | Ошибка: {str(e)[:40]}")
        
        print("\n" + "="*50)
        print("📊 ПЛАН СОЗДАН!")
        print("\nТеперь в Odoo:")
        print("1. Откройте Производство → Заказы на производство")
        print("2. Используйте вид 'Календарь' для просмотра расписания")
        print("3. Или экспортируйте в Excel для планирования")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def create_simple_kanban():
    """Создание простой Kanban доски для планирования"""
    print("\n📋 СОВЕТ: Используйте Kanban представление:")
    print("1. Производство → Заказы на производство")
    print("2. Переключитесь на вид Kanban (иконка в правом верхнем углу)")
    print("3. Группируйте по:")
    print("   - Статусу (Черновик → В процессе → Готово)")
    print("   - Продукту")
    print("   - Дате")
    print("\n✅ Это даст визуальное планирование без Enterprise!")

if __name__ == "__main__":
    print("="*60)
    print("🗓️ ПЛАНИРОВАНИЕ ПРОИЗВОДСТВА (Community Edition)")
    print("="*60)
    
    create_production_schedule()
    create_simple_kanban()
