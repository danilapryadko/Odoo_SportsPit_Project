#!/bin/bash

# Быстрый деплой через Railway CLI
# Использует сохраненный токен

set -e

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Установка токена
export RAILWAY_TOKEN=e2a89410-8aeb-419c-8020-741fba8f9bf9

echo -e "${YELLOW}🚂 Railway Quick Deploy${NC}"
echo -e "${GREEN}Token установлен: ${RAILWAY_TOKEN:0:10}...${NC}"

# Проверка авторизации
echo -e "${YELLOW}🔐 Проверка авторизации...${NC}"
railway whoami || {
    echo -e "${RED}❌ Ошибка авторизации!${NC}"
    echo "Проверьте токен Railway"
    exit 1
}

# Инициализация проекта (если еще не инициализирован)
if [ ! -f ".railway/config.json" ]; then
    echo -e "${YELLOW}📦 Инициализация Railway проекта...${NC}"
    railway init -n "odoo-sportpit"
fi

# Связывание с существующим проектом или создание нового
echo -e "${YELLOW}🔗 Связывание с проектом...${NC}"
railway link || railway init -n "odoo-sportpit"

# Установка переменных окружения
echo -e "${YELLOW}⚙️ Установка переменных окружения...${NC}"

# Основные переменные для Odoo
railway variables set PORT=8069
railway variables set WORKERS=2
railway variables set ADMIN_PASSWORD="SportsPit2025Admin!"
railway variables set LANG="ru_RU.UTF-8"
railway variables set TZ="Europe/Moscow"
railway variables set LOG_LEVEL="info"

# Лимиты памяти
railway variables set LIMIT_MEMORY_HARD=2684354560
railway variables set LIMIT_MEMORY_SOFT=2147483648

echo -e "${GREEN}✅ Переменные установлены${NC}"

# Деплой
echo -e "${YELLOW}🚀 Запуск деплоя...${NC}"
railway up --detach

echo -e "${GREEN}✅ Деплой запущен!${NC}"

# Получение URL
echo -e "${YELLOW}🌐 Получение URL проекта...${NC}"
sleep 3

# Попытка получить домен
DOMAIN=$(railway domain 2>/dev/null || echo "")

if [ -n "$DOMAIN" ]; then
    echo -e "${GREEN}✅ Проект будет доступен по адресу:${NC}"
    echo -e "${GREEN}   https://$DOMAIN${NC}"
else
    echo -e "${YELLOW}⏳ Генерация домена...${NC}"
    railway domain generate
    DOMAIN=$(railway domain)
    echo -e "${GREEN}✅ Проект будет доступен по адресу:${NC}"
    echo -e "${GREEN}   https://$DOMAIN${NC}"
fi

# Мониторинг логов
echo ""
echo -e "${YELLOW}📋 Просмотр логов деплоя:${NC}"
echo -e "${YELLOW}   railway logs -f${NC}"
echo ""
echo -e "${YELLOW}📊 Статус проекта:${NC}"
echo -e "${YELLOW}   railway status${NC}"
echo ""
echo -e "${GREEN}🎉 Деплой запущен успешно!${NC}"
echo ""
echo -e "${YELLOW}⏱️ Ожидаемое время сборки: 5-10 минут${NC}"
echo -e "${YELLOW}📱 Откройте Railway Dashboard для мониторинга:${NC}"
echo -e "${YELLOW}   https://railway.app/dashboard${NC}"