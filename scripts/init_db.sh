#!/bin/bash
# Скрипт инициализации чистой БД для Odoo 18

echo "=== Подготовка базы данных для Odoo 18 ==="

# Ждем доступности PostgreSQL
echo "Ожидание PostgreSQL..."
for i in {1..30}; do
    if pg_isready -h "$PGHOST" -p "$PGPORT" -U "$PGUSER"; then
        echo "PostgreSQL доступен!"
        break
    fi
    echo "Попытка $i/30..."
    sleep 2
done

# Установка пароля для psql
export PGPASSWORD="$PGPASSWORD"

echo "Очистка старой базы данных..."
# Сначала отключаем все активные соединения
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${PGDATABASE}' AND pid <> pg_backend_pid();" 2>/dev/null || true

# Удаляем существующую базу
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d postgres -c "DROP DATABASE IF EXISTS ${PGDATABASE};" 2>/dev/null || true

# Создаем новую чистую базу для Odoo 18
echo "Создание новой базы данных для Odoo 18..."
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d postgres -c "CREATE DATABASE ${PGDATABASE} WITH OWNER ${PGUSER} ENCODING 'UTF8' TEMPLATE template0;" || true

echo "✅ База данных готова для Odoo 18!"