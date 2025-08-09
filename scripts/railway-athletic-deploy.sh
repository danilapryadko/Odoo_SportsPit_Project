#!/bin/bash

# Deploy to Railway project athletic-emotion
# Project ID: daa4ac63-d597-4ba7-b10e-1baf84cbacad

set -e

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ID="daa4ac63-d597-4ba7-b10e-1baf84cbacad"
TOKEN="e2a89410-8aeb-419c-8020-741fba8f9bf9"

echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        ${YELLOW}🚂 Railway Deploy - Athletic Emotion${BLUE}         ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📦 Project ID:${NC} ${PROJECT_ID}"
echo -e "${GREEN}🔑 Token:${NC} ${TOKEN:0:10}..."
echo ""

# Инструкции для ручного деплоя
echo -e "${YELLOW}📋 Инструкции для деплоя:${NC}"
echo ""
echo -e "${BLUE}1. Авторизация в Railway:${NC}"
echo "   railway login"
echo ""
echo -e "${BLUE}2. Связывание с проектом:${NC}"
echo "   railway link -p ${PROJECT_ID}"
echo ""
echo -e "${BLUE}3. Установка переменных окружения:${NC}"
cat << 'EOF'
   railway variables set PORT=8069
   railway variables set ADMIN_PASSWORD="SportsPit2025!"
   railway variables set WORKERS=2
   railway variables set LANG="ru_RU.UTF-8"
   railway variables set TZ="Europe/Moscow"
   railway variables set LOG_LEVEL="info"
   railway variables set LIMIT_MEMORY_HARD=2684354560
   railway variables set LIMIT_MEMORY_SOFT=2147483648
EOF
echo ""
echo -e "${BLUE}4. Деплой проекта:${NC}"
echo "   railway up"
echo ""
echo -e "${BLUE}5. Получение URL:${NC}"
echo "   railway domain"
echo ""

# Альтернативный метод через GitHub
echo -e "${YELLOW}🔄 Альтернативный метод (через GitHub):${NC}"
echo ""
echo -e "${BLUE}1. Откройте Railway Dashboard:${NC}"
echo "   https://railway.app/project/${PROJECT_ID}"
echo ""
echo -e "${BLUE}2. В настройках проекта:${NC}"
echo "   - Settings → Service → Connect GitHub"
echo "   - Выберите репозиторий: danilapryadko/Odoo_SportsPit_Project"
echo "   - Branch: main"
echo ""
echo -e "${BLUE}3. Railway автоматически обнаружит:${NC}"
echo "   - Dockerfile"
echo "   - railway.json"
echo "   - railway.toml"
echo ""
echo -e "${BLUE}4. Добавьте PostgreSQL:${NC}"
echo "   - New Service → Database → PostgreSQL"
echo ""

echo -e "${GREEN}✅ Конфигурация готова!${NC}"
echo ""
echo -e "${YELLOW}🌐 Dashboard проекта:${NC}"
echo "   https://railway.app/project/${PROJECT_ID}"
echo ""
echo -e "${YELLOW}📝 GitHub репозиторий:${NC}"
echo "   https://github.com/danilapryadko/Odoo_SportsPit_Project"
echo ""

# Создание команды для быстрого доступа
echo -e "${YELLOW}💡 Совет: Сохраните команду для быстрого доступа:${NC}"
echo "   alias odoo-deploy='cd $(pwd) && railway up'"
echo ""

# Открытие в браузере
echo -e "${YELLOW}Открыть Railway Dashboard? [y/n]:${NC}"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    open "https://railway.app/project/${PROJECT_ID}"
fi