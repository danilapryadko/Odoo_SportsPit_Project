#!/bin/bash

# Скрипт настройки Railway MCP для Claude

set -e

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🚂 Настройка Railway MCP для Claude${NC}"

# Проверка токена
if [ ! -f ".env.railway" ]; then
    echo -e "${RED}❌ Файл .env.railway не найден!${NC}"
    exit 1
fi

source .env.railway

echo -e "${GREEN}✅ Railway Token: ${RAILWAY_TOKEN:0:10}...${NC}"

# Установка Railway MCP глобально
echo -e "${YELLOW}📦 Установка Railway MCP...${NC}"
npm install -g @railway/mcp

# Добавление в конфигурацию Claude
echo -e "${YELLOW}⚙️ Добавление Railway MCP в Claude...${NC}"

CLAUDE_CONFIG_PATH="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

if [ -f "$CLAUDE_CONFIG_PATH" ]; then
    echo -e "${YELLOW}Обновляем существующую конфигурацию Claude...${NC}"
    
    # Создаем резервную копию
    cp "$CLAUDE_CONFIG_PATH" "$CLAUDE_CONFIG_PATH.backup"
    
    # Добавляем Railway MCP в конфигурацию с помощью jq
    jq --arg token "$RAILWAY_TOKEN" '.mcpServers["railway-mcp"] = {
        "command": "npx",
        "args": ["-y", "@railway/mcp"],
        "env": {
            "RAILWAY_API_TOKEN": $token
        }
    }' "$CLAUDE_CONFIG_PATH" > "$CLAUDE_CONFIG_PATH.tmp" && mv "$CLAUDE_CONFIG_PATH.tmp" "$CLAUDE_CONFIG_PATH"
    
    echo -e "${GREEN}✅ Railway MCP добавлен в Claude${NC}"
else
    echo -e "${YELLOW}Создаем новую конфигурацию Claude...${NC}"
    
    mkdir -p "$HOME/Library/Application Support/Claude"
    
    cat > "$CLAUDE_CONFIG_PATH" << EOF
{
  "mcpServers": {
    "railway-mcp": {
      "command": "npx",
      "args": ["-y", "@railway/mcp"],
      "env": {
        "RAILWAY_API_TOKEN": "$RAILWAY_TOKEN"
      }
    }
  }
}
EOF
    
    echo -e "${GREEN}✅ Конфигурация Claude создана${NC}"
fi

# Тестирование Railway CLI
echo -e "${YELLOW}🧪 Тестирование Railway CLI...${NC}"
export RAILWAY_TOKEN=$RAILWAY_TOKEN

railway whoami || {
    echo -e "${RED}❌ Railway CLI не может авторизоваться с токеном${NC}"
    echo "Проверьте правильность токена"
    exit 1
}

echo -e "${GREEN}✅ Railway CLI работает корректно${NC}"

# Создание ярлыка для быстрого деплоя
echo -e "${YELLOW}🔗 Создание команды быстрого деплоя...${NC}"

cat > /usr/local/bin/odoo-deploy << 'EOF'
#!/bin/bash
cd /Users/danilapryadkoicloud.com/Documents/Odoo_SportsPit_Project
./scripts/railway-deploy.sh
EOF

chmod +x /usr/local/bin/odoo-deploy

echo -e "${GREEN}🎉 Настройка завершена!${NC}"
echo ""
echo -e "${YELLOW}📝 Инструкции:${NC}"
echo "  1. Перезапустите Claude Desktop"
echo "  2. Railway MCP будет доступен в Claude"
echo "  3. Для деплоя используйте: odoo-deploy"
echo ""
echo -e "${YELLOW}🔧 Доступные команды Railway MCP в Claude:${NC}"
echo "  - Создание проектов"
echo "  - Управление деплоями"
echo "  - Настройка переменных окружения"
echo "  - Мониторинг логов"
echo "  - Управление сервисами"
echo ""
echo -e "${GREEN}Token сохранен и настроен для автоматического использования${NC}"