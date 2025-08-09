#!/bin/bash

# Деплой в Railway проект athletic-emotion
# Использует сохраненный токен

set -e

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Railway Configuration
export RAILWAY_TOKEN=e2a89410-8aeb-419c-8020-741fba8f9bf9
PROJECT_NAME="athletic-emotion"

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}🚂 Деплой Odoo SportsPit в Railway${NC}"
echo -e "${GREEN}📦 Проект: ${PROJECT_NAME}${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# Проверка Railway CLI
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}📥 Установка Railway CLI...${NC}"
    npm install -g @railway/cli
fi

# Авторизация
echo -e "${YELLOW}🔐 Авторизация в Railway...${NC}"
railway login --browserless || {
    echo -e "${RED}❌ Ошибка авторизации${NC}"
    echo "Токен: ${RAILWAY_TOKEN:0:10}..."
    exit 1
}

echo -e "${GREEN}✅ Авторизация успешна${NC}"

# Связывание с проектом athletic-emotion
echo -e "${YELLOW}🔗 Связывание с проектом ${PROJECT_NAME}...${NC}"

# Попытка связаться с существующим проектом
railway link --environment production || {
    echo -e "${YELLOW}📦 Инициализация нового проекта...${NC}"
    railway init -n "${PROJECT_NAME}"
}

# Установка переменных окружения
echo -e "${YELLOW}⚙️ Настройка переменных окружения...${NC}"

# База данных PostgreSQL
railway variables set DATABASE_NAME="odoo_sportpit" --environment production
railway variables set DATABASE_USER="odoo" --environment production

# Odoo настройки
railway variables set ADMIN_PASSWORD="AthleticEmotion2025!" --environment production
railway variables set PORT="8069" --environment production
railway variables set WORKERS="2" --environment production

# Локализация
railway variables set LANG="ru_RU.UTF-8" --environment production
railway variables set TZ="Europe/Moscow" --environment production
railway variables set DEFAULT_LANG="ru_RU" --environment production

# Производительность
railway variables set LIMIT_MEMORY_HARD="2684354560" --environment production
railway variables set LIMIT_MEMORY_SOFT="2147483648" --environment production
railway variables set LIMIT_REQUEST="8192" --environment production
railway variables set LIMIT_TIME_CPU="60" --environment production
railway variables set LIMIT_TIME_REAL="120" --environment production

# Логирование
railway variables set LOG_LEVEL="info" --environment production

echo -e "${GREEN}✅ Переменные окружения установлены${NC}"

# Добавление PostgreSQL если еще не добавлен
echo -e "${YELLOW}🗄️ Проверка PostgreSQL...${NC}"
railway service create postgres --name "postgres" 2>/dev/null || echo "PostgreSQL уже существует"

# Деплой приложения
echo -e "${YELLOW}🚀 Запуск деплоя...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

railway up --environment production --detach

echo -e "${GREEN}✅ Деплой запущен!${NC}"

# Ожидание инициализации
echo -e "${YELLOW}⏳ Ожидание инициализации (30 сек)...${NC}"
sleep 30

# Получение домена
echo -e "${YELLOW}🌐 Настройка домена...${NC}"

# Генерация домена если его еще нет
DOMAIN=$(railway domain 2>/dev/null || echo "")
if [ -z "$DOMAIN" ]; then
    echo -e "${YELLOW}Генерация нового домена...${NC}"
    railway domain generate
    DOMAIN=$(railway domain)
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}📱 Информация о проекте:${NC}"
echo -e "  ${YELLOW}Название:${NC} ${PROJECT_NAME}"
echo -e "  ${YELLOW}URL:${NC} https://${DOMAIN}"
echo -e "  ${YELLOW}Admin:${NC} admin"
echo -e "  ${YELLOW}Password:${NC} AthleticEmotion2025!"
echo ""
echo -e "${GREEN}🔧 Полезные команды:${NC}"
echo -e "  ${YELLOW}Логи:${NC} railway logs -f"
echo -e "  ${YELLOW}Статус:${NC} railway status"
echo -e "  ${YELLOW}Переменные:${NC} railway variables"
echo -e "  ${YELLOW}Dashboard:${NC} railway open"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}⏱️ Время полной инициализации: 5-10 минут${NC}"
echo -e "${YELLOW}📊 Мониторинг: https://railway.app/dashboard${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# Открытие в браузере
echo ""
read -p "$(echo -e ${YELLOW}Открыть Railway Dashboard? [y/n]: ${NC})" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    railway open
fi

# Мониторинг логов
echo ""
read -p "$(echo -e ${YELLOW}Показать логи деплоя? [y/n]: ${NC})" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    railway logs -f
fi