#!/bin/bash
# Тестовый скрипт для проверки подключения к БД

echo "Testing database connection..."
echo "DB_HOST: $DB_HOST"
echo "DB_PORT: $DB_PORT"
echo "DB_NAME: $DB_NAME"
echo "DB_USER: $DB_USER"

# Пытаемся подключиться через psql
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "SELECT version();" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Connection successful!"
    
    # Проверяем, существует ли наша БД
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -tc "SELECT datname FROM pg_database WHERE datname = '$DB_NAME';" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Database $DB_NAME exists!"
    else
        echo "❌ Database $DB_NAME not found, creating..."
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>&1
    fi
else
    echo "❌ Connection failed!"
fi
