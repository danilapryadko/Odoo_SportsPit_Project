#!/bin/bash

# Скрипт резервного копирования базы данных Odoo
# Использование: ./scripts/backup.sh

set -e

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Загрузка переменных окружения
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/odoo_sportpit_$TIMESTAMP.sql"

echo -e "${YELLOW}💾 Создание резервной копии базы данных Odoo SportsPit${NC}"

# Создание директории для бэкапов
mkdir -p $BACKUP_DIR

# Проверка переменных
if [ -z "$DATABASE_HOST" ]; then
    DATABASE_HOST="localhost"
fi

if [ -z "$DATABASE_NAME" ]; then
    DATABASE_NAME="odoo_sportpit"
fi

echo -e "${YELLOW}📝 Параметры:${NC}"
echo "  База данных: $DATABASE_NAME"
echo "  Файл бэкапа: $BACKUP_FILE"

# Создание бэкапа
echo -e "${YELLOW}🔨 Создаем резервную копию...${NC}"
PGPASSWORD=$DATABASE_PASSWORD pg_dump \
    -h $DATABASE_HOST \
    -p ${DATABASE_PORT:-5432} \
    -U $DATABASE_USER \
    -d $DATABASE_NAME \
    -f $BACKUP_FILE \
    --verbose \
    --no-owner \
    --no-privileges

# Сжатие бэкапа
echo -e "${YELLOW}🗜️ Сжимаем бэкап...${NC}"
gzip $BACKUP_FILE

echo -e "${GREEN}✅ Резервная копия создана: ${BACKUP_FILE}.gz${NC}"

# Копирование filestore
if [ -d "./filestore" ]; then
    echo -e "${YELLOW}📂 Копируем filestore...${NC}"
    tar -czf "$BACKUP_DIR/filestore_$TIMESTAMP.tar.gz" ./filestore
    echo -e "${GREEN}✅ Filestore скопирован${NC}"
fi

# Удаление старых бэкапов (старше 30 дней)
echo -e "${YELLOW}🗑️ Удаляем старые бэкапы...${NC}"
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

# Показываем размер бэкапа
BACKUP_SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
echo -e "${GREEN}📊 Размер бэкапа: $BACKUP_SIZE${NC}"

# Список всех бэкапов
echo -e "${YELLOW}📋 Все бэкапы:${NC}"
ls -lh $BACKUP_DIR/*.gz

echo -e "${GREEN}🎉 Резервное копирование завершено успешно!${NC}"