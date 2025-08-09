#!/usr/bin/env python3
"""
Тестовый скрипт для проверки подключения к PostgreSQL
"""
import os
import psycopg2
from psycopg2 import sql

# Получаем параметры из переменных окружения
DB_HOST = os.getenv('DB_HOST', 'postgresql-odoo.railway.internal')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'odoo')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'odoo_sportpit_2024')
DB_NAME = os.getenv('DB_NAME', 'odoo_sportpit')

def test_connection():
    """Тестирует подключение к PostgreSQL"""
    try:
        # Подключаемся к PostgreSQL
        print(f"Подключение к PostgreSQL...")
        print(f"Host: {DB_HOST}")
        print(f"Port: {DB_PORT}")
        print(f"User: {DB_USER}")
        print(f"Database: {DB_NAME}")
        
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database='postgres'  # Подключаемся к системной БД
        )
        
        print("✅ Подключение успешно!")
        
        # Проверяем, существует ли база данных
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_NAME,)
        )
        
        if cur.fetchone():
            print(f"✅ База данных '{DB_NAME}' существует")
        else:
            print(f"❌ База данных '{DB_NAME}' не найдена")
            print(f"Создаем базу данных...")
            
            # Создаем базу данных
            conn.autocommit = True
            cur.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(DB_NAME)
                )
            )
            print(f"✅ База данных '{DB_NAME}' создана")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_connection()
