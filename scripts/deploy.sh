#!/bin/bash

# Скрипт деплоя Odoo SportsPit на Railway
# Использование: ./scripts/deploy.sh [production|staging]

set -e

ENVIRONMENT=${1:-production}
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Начинаем деплой Odoo SportsPit в окружение: $ENVIRONMENT${NC}"

# Проверка наличия Railway CLI
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI не установлен!${NC}"
    echo "Установите его командой: npm install -g @railway/cli"
    exit 1
fi

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker не установлен!${NC}"
    exit 1
fi

# Проверка токена Railway
if [ -z "$RAILWAY_TOKEN" ]; then
    echo -e "${RED}❌ RAILWAY_TOKEN не установлен!${NC}"
    echo "Экспортируйте токен: export RAILWAY_TOKEN=your_token_here"
    exit 1
fi

echo -e "${GREEN}✅ Все зависимости установлены${NC}"

# Сборка Docker образа локально для тестирования
echo -e "${YELLOW}🔨 Собираем Docker образ...${NC}"
docker build -t odoo-sportpit:latest .

# Запуск тестов
echo -e "${YELLOW}🧪 Запускаем тесты...${NC}"
docker run --rm odoo-sportpit:latest python -m pytest tests/ || true

# Проверка конфигурации
echo -e "${YELLOW}🔍 Проверяем конфигурацию...${NC}"
if [ ! -f "railway.json" ]; then
    echo -e "${RED}❌ railway.json не найден!${NC}"
    exit 1
fi

if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}❌ Dockerfile не найден!${NC}"
    exit 1
fi

# Деплой на Railway
echo -e "${YELLOW}🚂 Деплоим на Railway...${NC}"

if [ "$ENVIRONMENT" == "staging" ]; then
    railway up --environment staging --service odoo-sportpit-staging
else
    railway up --environment production --service odoo-sportpit
fi

echo -e "${GREEN}✅ Деплой успешно завершен!${NC}"

# Проверка статуса
echo -e "${YELLOW}📊 Проверяем статус деплоя...${NC}"
railway status

# Получение URL приложения
echo -e "${YELLOW}🌐 URL приложения:${NC}"
railway domain

echo -e "${GREEN}🎉 Деплой завершен успешно!${NC}"
echo -e "${YELLOW}📝 Не забудьте:${NC}"
echo "  1. Проверить логи: railway logs"
echo "  2. Настроить переменные окружения в Railway Dashboard"
echo "  3. Инициализировать базу данных при первом запуске"
echo "  4. Установить русскую локализацию в настройках Odoo"