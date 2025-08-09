#!/bin/bash

# Railway MCP Deployment Script
# Использует Railway API для автоматического деплоя

set -e

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Загрузка Railway токена
if [ -f ".env.railway" ]; then
    export $(cat .env.railway | grep -v '^#' | xargs)
fi

if [ -z "$RAILWAY_TOKEN" ]; then
    echo -e "${RED}❌ RAILWAY_TOKEN не найден!${NC}"
    echo "Проверьте файл .env.railway"
    exit 1
fi

echo -e "${YELLOW}🚂 Railway MCP Deployment${NC}"
echo -e "${GREEN}Token: ${RAILWAY_TOKEN:0:10}...${NC}"

# Функция для проверки статуса проекта
check_project_status() {
    echo -e "${YELLOW}📊 Проверка статуса проекта...${NC}"
    
    curl -s -X GET \
        -H "Authorization: Bearer $RAILWAY_TOKEN" \
        -H "Content-Type: application/json" \
        "https://backboard.railway.app/graphql/v2" \
        -d '{"query":"query { me { projects { edges { node { id name } } } } }"}' \
        | jq -r '.data.me.projects.edges[].node | select(.name=="odoo-sportpit") | .id'
}

# Функция для создания проекта если не существует
create_project() {
    echo -e "${YELLOW}🔨 Создание проекта odoo-sportpit...${NC}"
    
    RESPONSE=$(curl -s -X POST \
        -H "Authorization: Bearer $RAILWAY_TOKEN" \
        -H "Content-Type: application/json" \
        "https://backboard.railway.app/graphql/v2" \
        -d '{
            "query": "mutation CreateProject($name: String!) { projectCreate(name: $name) { id name } }",
            "variables": {
                "name": "odoo-sportpit"
            }
        }')
    
    PROJECT_ID=$(echo $RESPONSE | jq -r '.data.projectCreate.id')
    echo -e "${GREEN}✅ Проект создан: $PROJECT_ID${NC}"
    echo $PROJECT_ID
}

# Функция для деплоя
deploy_project() {
    local PROJECT_ID=$1
    
    echo -e "${YELLOW}🚀 Деплой проекта...${NC}"
    
    # Создание нового деплоя
    RESPONSE=$(curl -s -X POST \
        -H "Authorization: Bearer $RAILWAY_TOKEN" \
        -H "Content-Type: application/json" \
        "https://backboard.railway.app/graphql/v2" \
        -d "{
            \"query\": \"mutation Deploy(\$projectId: String!, \$environment: String!) { 
                deploymentCreate(
                    projectId: \$projectId,
                    environment: \$environment,
                    source: {
                        git: {
                            repo: \\\"https://github.com/danilapryadko/Odoo_SportsPit_Project.git\\\",
                            branch: \\\"main\\\"
                        }
                    }
                ) { 
                    id 
                    status 
                } 
            }\",
            \"variables\": {
                \"projectId\": \"$PROJECT_ID\",
                \"environment\": \"production\"
            }
        }")
    
    DEPLOYMENT_ID=$(echo $RESPONSE | jq -r '.data.deploymentCreate.id')
    
    if [ "$DEPLOYMENT_ID" != "null" ] && [ -n "$DEPLOYMENT_ID" ]; then
        echo -e "${GREEN}✅ Деплой запущен: $DEPLOYMENT_ID${NC}"
        return 0
    else
        echo -e "${RED}❌ Ошибка деплоя${NC}"
        echo $RESPONSE | jq .
        return 1
    fi
}

# Функция для установки переменных окружения
set_environment_variables() {
    local PROJECT_ID=$1
    
    echo -e "${YELLOW}⚙️ Установка переменных окружения...${NC}"
    
    # Читаем переменные из .env.example
    while IFS='=' read -r key value; do
        # Пропускаем комментарии и пустые строки
        if [[ ! "$key" =~ ^# ]] && [ -n "$key" ]; then
            # Удаляем кавычки из значения
            value="${value%\"}"
            value="${value#\"}"
            
            echo "  Устанавливаем $key"
            
            curl -s -X POST \
                -H "Authorization: Bearer $RAILWAY_TOKEN" \
                -H "Content-Type: application/json" \
                "https://backboard.railway.app/graphql/v2" \
                -d "{
                    \"query\": \"mutation SetEnvVar(\$projectId: String!, \$key: String!, \$value: String!) {
                        variableSet(projectId: \$projectId, environment: \\\"production\\\", key: \$key, value: \$value)
                    }\",
                    \"variables\": {
                        \"projectId\": \"$PROJECT_ID\",
                        \"key\": \"$key\",
                        \"value\": \"$value\"
                    }
                }" > /dev/null
        fi
    done < .env.example
    
    echo -e "${GREEN}✅ Переменные окружения установлены${NC}"
}

# Основной процесс
echo -e "${YELLOW}🔍 Проверка существующего проекта...${NC}"
PROJECT_ID=$(check_project_status)

if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}Проект не найден, создаем новый...${NC}"
    PROJECT_ID=$(create_project)
fi

echo -e "${GREEN}📝 ID проекта: $PROJECT_ID${NC}"

# Установка переменных окружения
set_environment_variables "$PROJECT_ID"

# Деплой проекта
deploy_project "$PROJECT_ID"

# Получение URL
echo -e "${YELLOW}🌐 Получение URL проекта...${NC}"
sleep 5

DOMAIN=$(curl -s -X GET \
    -H "Authorization: Bearer $RAILWAY_TOKEN" \
    -H "Content-Type: application/json" \
    "https://backboard.railway.app/graphql/v2" \
    -d "{
        \"query\": \"query GetDomain(\$projectId: String!) { 
            project(id: \$projectId) { 
                deployments { 
                    edges { 
                        node { 
                            staticUrl 
                        } 
                    } 
                } 
            } 
        }\",
        \"variables\": {
            \"projectId\": \"$PROJECT_ID\"
        }
    }" | jq -r '.data.project.deployments.edges[0].node.staticUrl')

if [ "$DOMAIN" != "null" ] && [ -n "$DOMAIN" ]; then
    echo -e "${GREEN}✅ Проект доступен по адресу: https://$DOMAIN${NC}"
else
    echo -e "${YELLOW}⏳ Домен еще не назначен. Проверьте через несколько минут в Railway Dashboard${NC}"
fi

echo -e "${GREEN}🎉 Деплой завершен!${NC}"
echo -e "${YELLOW}📝 Следующие шаги:${NC}"
echo "  1. Откройте Railway Dashboard: https://railway.app/dashboard"
echo "  2. Проверьте логи деплоя"
echo "  3. Дождитесь завершения сборки (5-10 минут)"
echo "  4. Откройте приложение по предоставленному URL"