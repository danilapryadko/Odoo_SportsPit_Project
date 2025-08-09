#!/bin/bash

# Скрипт восстановления базы данных Odoo из резервной копии
# Использование: ./scripts/restore.sh backup_file.sql.gz

set -e

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Укажите файл резервной копии!${NC}"
    echo "Использование: ./scripts/restore.sh backups/odoo_sportpit_YYYYMMDD_HHMMSS.sql.gz"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Файл $BACKUP_FILE не найден!${NC}"
    exit 1
fi

echo -e "${YELLOW}♻️ Восстановление базы данных Odoo SportsPit${NC}"

# Загрузка переменных окружения
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Проверка переменных
if [ -z "$DATABASE_HOST" ]; then
    DATABASE_HOST="localhost"
fi

if [ -z "$DATABASE_NAME" ]; then
    DATABASE_NAME="odoo_sportpit"
fi

echo -e "${YELLOW}⚠️ ВНИМАНИЕ: Все данные в базе $DATABASE_NAME будут перезаписаны!${NC}"
read -p "Продолжить? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Отменено пользователем${NC}"
    exit 1
fi

# Остановка Odoo
echo -e "${YELLOW}🛑 Останавливаем Odoo...${NC}"
docker-compose stop odoo || true

# Удаление существующей базы данных
echo -e "${YELLOW}🗑️ Удаляем существующую базу данных...${NC}"
PGPASSWORD=$DATABASE_PASSWORD psql \
    -h $DATABASE_HOST \
    -p ${DATABASE_PORT:-5432} \
    -U $DATABASE_USER \
    -c "DROP DATABASE IF EXISTS $DATABASE_NAME;"

# Создание новой базы данных
echo -e "${YELLOW}🔨 Создаем новую базу данных...${NC}"
PGPASSWORD=$DATABASE_PASSWORD psql \
    -h $DATABASE_HOST \
    -p ${DATABASE_PORT:-5432} \
    -U $DATABASE_USER \
    -c "CREATE DATABASE $DATABASE_NAME WITH ENCODING 'UTF8' LC_COLLATE='ru_RU.UTF-8' LC_CTYPE='ru_RU.UTF-8' TEMPLATE=template0;"

# Распаковка и восстановление
echo -e "${YELLOW}📦 Восстанавливаем данные...${NC}"
gunzip -c $BACKUP_FILE | PGPASSWORD=$DATABASE_PASSWORD psql \
    -h $DATABASE_HOST \
    -p ${DATABASE_PORT:-5432} \
    -U $DATABASE_USER \
    -d $DATABASE_NAME

echo -e "${GREEN}✅ База данных восстановлена${NC}"

# Восстановление filestore если есть
FILESTORE_BACKUP=$(echo $BACKUP_FILE | sed 's/odoo_sportpit/filestore/g' | sed 's/.sql.gz/.tar.gz/g')
if [ -f "$FILESTORE_BACKUP" ]; then
    echo -e "${YELLOW}📂 Восстанавливаем filestore...${NC}"
    tar -xzf $FILESTORE_BACKUP
    echo -e "${GREEN}✅ Filestore восстановлен${NC}"
fi

# Запуск Odoo
echo -e "${YELLOW}🚀 Запускаем Odoo...${NC}"
docker-compose start odoo

echo -e "${GREEN}🎉 Восстановление завершено успешно!${NC}"
echo -e "${YELLOW}📝 Проверьте работу системы:${NC}"
echo "  1. Откройте браузер: http://localhost:8069"
echo "  2. Проверьте доступность всех модулей"
echo "  3. Проверьте целостность данных"