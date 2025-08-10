#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Очистка БД - удаляем все кроме odoo_sportpit
"""

import psycopg2
import sys

print("="*50)
print("🧹 УДАЛЕНИЕ ЛИШНИХ БАЗ ДАННЫХ")
print("="*50)

try:
    # Подключаемся к PostgreSQL
    conn = psycopg2.connect(
        host="postgresql-odoo.railway.internal",
        port=5432,
        user="odoo",
        password="odoo_sportpit_2024",
        database="postgres"
    )
    cur = conn.cursor()
    
    print("\n📋 Проверяем существующие базы данных...")
    
    # Получаем список всех БД
    cur.execute("""
        SELECT datname FROM pg_database 
        WHERE datname NOT IN ('postgres', 'template0', 'template1', 'odoo_sportpit')
        AND datistemplate = false
    """)
    dbs_to_delete = cur.fetchall()
    
    if not dbs_to_delete:
        print("✅ Лишних БД нет, только odoo_sportpit")
    else:
        print(f"\n🗑️ Найдено БД для удаления: {len(dbs_to_delete)}")
        
        for db in dbs_to_delete:
            db_name = db[0]
            print(f"\n   Удаляем БД: {db_name}")
            
            # Завершаем все активные соединения к этой БД
            cur.execute(f"""
                SELECT pg_terminate_backend(pid) 
                FROM pg_stat_activity 
                WHERE datname = '{db_name}' 
                AND pid <> pg_backend_pid()
            """)
            conn.commit()
            print(f"   - Соединения закрыты")
            
            # Удаляем БД
            conn.autocommit = True
            cur.execute(f"DROP DATABASE IF EXISTS \"{db_name}\"")
            print(f"   ✅ БД {db_name} удалена")
    
    # Проверяем что осталась только odoo_sportpit
    cur.execute("""
        SELECT datname FROM pg_database 
        WHERE datname NOT IN ('postgres', 'template0', 'template1')
        AND datistemplate = false
    """)
    remaining_dbs = cur.fetchall()
    
    print("\n📊 Итоговый список БД:")
    for db in remaining_dbs:
        print(f"   - {db[0]}")
    
    cur.close()
    conn.close()
    
    print("\n✅ Готово! Осталась только БД odoo_sportpit")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    sys.exit(1)
