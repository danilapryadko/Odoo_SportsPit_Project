#!/bin/bash

# Очистка всех баз данных кроме postgres
echo "Cleaning all Odoo databases..."

# Подключаемся к PostgreSQL и удаляем все базы кроме системных
PGPASSWORD=odoo_sportpit_2024 psql -h postgresql-odoo.railway.internal -p 5432 -U odoo -d postgres << EOF
-- Завершаем все активные подключения
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname NOT IN ('postgres', 'template0', 'template1') 
AND pid <> pg_backend_pid();

-- Удаляем все базы данных Odoo
DROP DATABASE IF EXISTS odoo_sportpit;
DROP DATABASE IF EXISTS odoo_sportpit_new;
DROP DATABASE IF EXISTS production;
DROP DATABASE IF EXISTS sportpit_main;

-- Создаём чистую базу данных odoo_sportpit
CREATE DATABASE odoo_sportpit WITH OWNER odoo ENCODING 'UTF8';
EOF

echo "Database cleanup completed!"
