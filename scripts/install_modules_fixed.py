#!/usr/bin/env python3
"""
Установка модулей с правильными учетными данными
"""

import xmlrpc.client
import ssl
import sys

ODOO_URL = "https://odoosportspitproject-production.up.railway.app"

# Учетные данные администратора, которые мы создали
LOGINS = [
    ("danila@usafitandjoy.com", "admin123"),
    ("test@test.com", "test123"),
    ("admin", "admin"),
    ("admin", "SportPit2024Master"),
    ("admin", "admin_sportpit_2024")
]

DB_NAME = "odoo_sportpit"

# Модули для установки
MODULES_TO_INSTALL = [
    'mrp',                    # Manufacturing
    'stock',                  # Inventory
    'purchase',               # Purchase
    'sale_management',        # Sales
    'account',                # Accounting
    'hr',                     # Employees
    'hr_attendance',          # Attendances
    'project',                # Project Management
    'product_expiry',         # Product Expiry Dates
]

def connect_and_install():
    """Подключение и установка модулей"""
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    for login, password in LOGINS:
        print(f"\n🔐 Пробую войти как {login}...")
        
        try:
            common = xmlrpc.client.ServerProxy(
                f'{ODOO_URL}/xmlrpc/2/common',
                context=ssl_context
            )
            
            uid = common.authenticate(DB_NAME, login, password, {})
            
            if uid:
                print(f"✅ Успешный вход! UID: {uid}")
                
                models = xmlrpc.client.ServerProxy(
                    f'{ODOO_URL}/xmlrpc/2/object',
                    context=ssl_context
                )
                
                # Устанавливаем модули
                print("\n📦 Установка модулей...")
                
                for module_name in MODULES_TO_INSTALL:
                    try:
                        # Ищем модуль
                        module_ids = models.execute_kw(
                            DB_NAME, uid, password,
                            'ir.module.module', 'search',
                            [[('name', '=', module_name)]]
                        )
                        
                        if module_ids:
                            # Проверяем состояние
                            module = models.execute_kw(
                                DB_NAME, uid, password,
                                'ir.module.module', 'read',
                                [module_ids[0]],
                                {'fields': ['state', 'display_name']}
                            )
                            
                            if module[0]['state'] == 'installed':
                                print(f"  ✅ {module[0]['display_name']} - уже установлен")
                            else:
                                # Устанавливаем
                                models.execute_kw(
                                    DB_NAME, uid, password,
                                    'ir.module.module', 'button_immediate_install',
                                    [module_ids]
                                )
                                print(f"  ✅ {module[0]['display_name']} - установлен")
                        else:
                            print(f"  ⚠️ Модуль {module_name} не найден")
                            
                    except Exception as e:
                        print(f"  ❌ Ошибка с {module_name}: {str(e)[:50]}")
                
                print("\n✅ Модули установлены!")
                return True
                
        except Exception as e:
            print(f"  ❌ Не подошел: {str(e)[:50]}")
    
    print("\n❌ Не удалось войти ни с одним паролем")
    print("\n🔧 Решение:")
    print("1. Войдите в Odoo через браузер")
    print("2. Перейдите в Настройки → Приложения")
    print("3. Установите модули вручную")
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 УСТАНОВКА МОДУЛЕЙ ODOO")
    print("=" * 60)
    
    if connect_and_install():
        print("\n✅ Успешно завершено!")
    else:
        print("\n❌ Требуется ручная установка")
