#!/bin/bash

# Скрипт инициализации базы данных Odoo
# Использование: ./scripts/init_db.sh

set -e

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🗄️ Инициализация базы данных Odoo SportsPit${NC}"

# Загрузка переменных окружения
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Проверка переменных
if [ -z "$DATABASE_HOST" ]; then
    DATABASE_HOST="localhost"
fi

if [ -z "$DATABASE_PORT" ]; then
    DATABASE_PORT="5432"
fi

if [ -z "$DATABASE_USER" ]; then
    DATABASE_USER="odoo"
fi

if [ -z "$DATABASE_NAME" ]; then
    DATABASE_NAME="odoo_sportpit"
fi

echo -e "${YELLOW}📝 Параметры подключения:${NC}"
echo "  Host: $DATABASE_HOST"
echo "  Port: $DATABASE_PORT"
echo "  User: $DATABASE_USER"
echo "  Database: $DATABASE_NAME"

# Создание базы данных
echo -e "${YELLOW}🔨 Создаем базу данных...${NC}"
PGPASSWORD=$DATABASE_PASSWORD psql -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER -c "CREATE DATABASE $DATABASE_NAME WITH ENCODING 'UTF8' LC_COLLATE='ru_RU.UTF-8' LC_CTYPE='ru_RU.UTF-8' TEMPLATE=template0;" 2>/dev/null || echo "База данных уже существует"

# Инициализация Odoo
echo -e "${YELLOW}🚀 Инициализируем Odoo...${NC}"
docker run --rm \
    -e DATABASE_HOST=$DATABASE_HOST \
    -e DATABASE_PORT=$DATABASE_PORT \
    -e DATABASE_USER=$DATABASE_USER \
    -e DATABASE_PASSWORD=$DATABASE_PASSWORD \
    -e DATABASE_NAME=$DATABASE_NAME \
    -e ADMIN_PASSWORD=$ADMIN_PASSWORD \
    --network host \
    odoo-sportpit:latest \
    odoo -c /etc/odoo/odoo.conf \
    -d $DATABASE_NAME \
    -i base,l10n_ru,mrp,stock,purchase,sale,quality_control,hr,hr_attendance,project,timesheet,product_expiry \
    --load-language=ru_RU \
    --stop-after-init

echo -e "${GREEN}✅ База данных инициализирована${NC}"

# Установка часового пояса
echo -e "${YELLOW}⏰ Устанавливаем часовой пояс...${NC}"
PGPASSWORD=$DATABASE_PASSWORD psql -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER -d $DATABASE_NAME <<EOF
UPDATE res_users SET tz='Europe/Moscow' WHERE tz IS NULL OR tz = '';
UPDATE res_company SET tz='Europe/Moscow';
UPDATE res_partner SET tz='Europe/Moscow' WHERE tz IS NULL OR tz = '';
EOF

echo -e "${GREEN}✅ Часовой пояс установлен${NC}"

# Установка русского языка по умолчанию
echo -e "${YELLOW}🌐 Устанавливаем русский язык...${NC}"
PGPASSWORD=$DATABASE_PASSWORD psql -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_USER -d $DATABASE_NAME <<EOF
UPDATE res_lang SET active = true WHERE code = 'ru_RU';
UPDATE res_users SET lang = 'ru_RU';
UPDATE res_company SET lang = 'ru_RU';
UPDATE res_partner SET lang = 'ru_RU' WHERE lang IS NULL OR lang = 'en_US';
EOF

echo -e "${GREEN}✅ Русский язык установлен${NC}"

echo -e "${GREEN}🎉 Инициализация завершена успешно!${NC}"
echo -e "${YELLOW}📝 Следующие шаги:${NC}"
echo "  1. Запустите Odoo: docker-compose up -d"
echo "  2. Откройте браузер: http://localhost:8069"
echo "  3. Войдите с паролем администратора из .env"
echo "  4. Активируйте необходимые модули в настройках"