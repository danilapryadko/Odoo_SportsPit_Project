#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xmlrpc.client
import ssl

# Игнорируем SSL
ssl._create_default_https_context = ssl._create_unverified_context

# Подключение
url = 'https://odoosportspitproject-production.up.railway.app'
db = 'odoo_sportpit'
username = 'admin'
password = 'admin'

try:
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    print("✅ Подключено к Odoo")
    
    # Находим модуль website
    website_ids = models.execute_kw(db, uid, password, 
        'ir.module.module', 'search', [[('name', '=', 'website')]])
    
    if website_ids:
        # Проверяем статус
        module = models.execute_kw(db, uid, password, 
            'ir.module.module', 'read', [website_ids, ['state']])
        
        if module[0]['state'] == 'installed':
            print("🔄 Удаляем модуль website...")
            # Деинсталлируем модуль
            models.execute_kw(db, uid, password, 
                'ir.module.module', 'button_immediate_uninstall', [website_ids])
            print("✅ Модуль website удалён!")
        else:
            print("ℹ️ Модуль website не установлен")
    
    # Проверяем другие website модули
    website_modules = ['website_sale', 'website_blog', 'website_event', 'website_form']
    for mod_name in website_modules:
        mod_ids = models.execute_kw(db, uid, password, 
            'ir.module.module', 'search', [[('name', '=', mod_name)]])
        if mod_ids:
            module = models.execute_kw(db, uid, password, 
                'ir.module.module', 'read', [mod_ids, ['state']])
            if module[0]['state'] == 'installed':
                print(f"🔄 Удаляем {mod_name}...")
                models.execute_kw(db, uid, password, 
                    'ir.module.module', 'button_immediate_uninstall', [mod_ids])
                print(f"✅ {mod_name} удалён")
    
    print("\n✅ Готово! Теперь Odoo должен работать без website модуля")
    print("📌 Используйте URL: https://odoosportspitproject-production.up.railway.app/web")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
