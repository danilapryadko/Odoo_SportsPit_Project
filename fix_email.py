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
    # Аутентификация
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    print(f"✅ Подключено (UID: {uid})")
    
    # Модели
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # Обновляем email администратора
    models.execute_kw(db, uid, password, 'res.users', 'write', [[uid], {
        'email': 'noreply@usafitandjoy.com',
        'notification_type': 'email',
    }])
    print("✅ Email администратора обновлён")
    
    # Обновляем настройки компании
    models.execute_kw(db, uid, password, 'res.company', 'write', [[1], {
        'email': 'noreply@usafitandjoy.com',
        'catchall_email': 'noreply@usafitandjoy.com',
    }])
    print("✅ Email компании обновлён")
    
    # Обновляем SMTP сервер - добавляем from_filter
    smtp_servers = models.execute_kw(db, uid, password, 
        'ir.mail_server', 'search', [[('name', '=', 'Beget SMTP')]])
    
    if smtp_servers:
        models.execute_kw(db, uid, password, 'ir.mail_server', 'write', 
            [smtp_servers, {
                'from_filter': 'noreply@usafitandjoy.com',
            }])
        print("✅ SMTP сервер обновлён с фильтром FROM")
    
    # Устанавливаем системный параметр
    param_id = models.execute_kw(db, uid, password, 
        'ir.config_parameter', 'search', [[('key', '=', 'mail.default.from')]])
    
    if param_id:
        models.execute_kw(db, uid, password, 'ir.config_parameter', 'write',
            [param_id, {'value': 'noreply@usafitandjoy.com'}])
    else:
        models.execute_kw(db, uid, password, 'ir.config_parameter', 'create',
            [{'key': 'mail.default.from', 'value': 'noreply@usafitandjoy.com'}])
    print("✅ Системный параметр mail.default.from установлен")
    
    print("\n✅ Все настройки email успешно обновлены!")
    print("Теперь все письма будут отправляться от noreply@usafitandjoy.com")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
