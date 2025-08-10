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
    
    # Найти пользователей
    user_ids = models.execute_kw(db, uid, password, 'res.users', 'search', 
        [[('login', 'in', ['danila@usafitandjoy.com', 'svetlana@usafitandjoy.com'])]])
    
    if user_ids:
        # Сбросить пароли и отправить письма
        for user_id in user_ids:
            # Получаем информацию о пользователе
            user = models.execute_kw(db, uid, password, 'res.users', 'read', 
                [user_id, ['name', 'email']])
            
            # Устанавливаем временный пароль
            temp_password = 'SportPit2024!'
            models.execute_kw(db, uid, password, 'res.users', 'write', 
                [[user_id], {'password': temp_password}])
            
            print(f"✅ Пароль для {user[0]['name']} установлен: {temp_password}")
            
            # Отправляем письмо с приглашением
            try:
                models.execute_kw(db, uid, password, 'res.users', 'action_reset_password', [[user_id]])
                print(f"📧 Письмо отправлено на {user[0]['email']}")
            except:
                print(f"⚠️ Не удалось отправить письмо для {user[0]['name']}")
    
    print("\n✅ Готово! Временный пароль для всех: SportPit2024!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
