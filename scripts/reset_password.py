#!/usr/bin/env python3
"""
Сброс пароля администратора Odoo
"""

import psycopg2
import hashlib
from passlib.context import CryptContext

# Конфигурация подключения к БД
DB_HOST = "postgresql-odoo.railway.internal"
DB_PORT = 5432
DB_NAME = "odoo_sportpit"
DB_USER = "odoo"
DB_PASSWORD = "odoo_sportpit_2024"

# Новый пароль
NEW_PASSWORD = "admin123"  # Простой пароль для теста
ADMIN_EMAIL = "danila@usafitandjoy.com"

def reset_password():
    print("🔐 Сброс пароля администратора Odoo...")
    
    try:
        # Подключаемся к БД
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        cursor = conn.cursor()
        
        # Генерируем хэш пароля
        pwd_context = CryptContext(schemes=['pbkdf2_sha512', 'plaintext'], deprecated='auto')
        password_hash = pwd_context.hash(NEW_PASSWORD)
        
        # Обновляем пароль
        cursor.execute("""
            UPDATE res_users 
            SET password = %s 
            WHERE login = %s
        """, (password_hash, ADMIN_EMAIL))
        
        conn.commit()
        
        print(f"✅ Пароль успешно изменен!")
        print(f"📧 Email: {ADMIN_EMAIL}")
        print(f"🔑 Новый пароль: {NEW_PASSWORD}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\nПопробуйте другой способ...")

if __name__ == "__main__":
    reset_password()
